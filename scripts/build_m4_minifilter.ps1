# Build MMI boundary minifilter (Phase 4D-b).
# Requires Visual Studio 2022 + WDK toolset (run install_m4_wdk_toolset.ps1 as Admin once).

param(
    [switch]$TestSign
)

$ErrorActionPreference = "Stop"

function Find-Vs2022MsBuild {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        $installPath = & $vswhere -latest -version "[17.0,18.0)" -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
        if ($installPath) {
            $candidate = Join-Path $installPath "MSBuild\Current\Bin\amd64\MSBuild.exe"
            if (Test-Path $candidate) {
                return $candidate
            }
        }
    }

    $candidates = @(
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\amd64\MSBuild.exe",
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\amd64\MSBuild.exe",
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\amd64\MSBuild.exe"
    )
    foreach ($path in $candidates) {
        if (Test-Path $path) {
            return $path
        }
    }
    return $null
}

function Get-Vs2022InstallPath {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        return (& $vswhere -latest -version "[17.0,18.0)" -products * -property installationPath 2>$null)
    }
    return $null
}

function Get-LatestVcToolsVersion {
    param([Parameter(Mandatory = $true)][string]$VsInstallPath)

    $msvcRoot = Join-Path $VsInstallPath "VC\Tools\MSVC"
    if (-not (Test-Path $msvcRoot)) {
        return $null
    }

    $latest = Get-ChildItem $msvcRoot -Directory |
        Sort-Object { [version]$_.Name } -Descending |
        Select-Object -First 1

    if (-not $latest) {
        return $null
    }
    return $latest.Name
}

function Get-WdkToolsetProps {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        $installPath = & $vswhere -latest -version "[17.0,18.0)" -products * -property installationPath 2>$null
        if ($installPath) {
            $candidate = Join-Path $installPath "MSBuild\Microsoft\VC\v170\Platforms\x64\PlatformToolsets\WindowsKernelModeDriver10.0\Toolset.props"
            if (Test-Path $candidate) {
                return $candidate
            }
        }
    }
    return $null
}

function Get-WdkContentRoot {
    $candidate = "C:\Program Files (x86)\Windows Kits\10\"
    if (Test-Path (Join-Path $candidate "Include\wdf")) {
        return $candidate
    }
    return $null
}

function Write-MmiBuildEnvProps {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$VsInstallDir,
        [Parameter(Mandatory = $true)][string]$VcToolsVersion,
        [Parameter(Mandatory = $true)][string]$VcToolsInstallDir,
        [Parameter(Mandatory = $true)][string]$WdkRoot
    )

    $xml = @(
        '<?xml version="1.0" encoding="utf-8"?>',
        '<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">',
        '  <PropertyGroup>',
        "    <VSInstallDir>$VsInstallDir</VSInstallDir>",
        "    <VCToolsVersion>$VcToolsVersion</VCToolsVersion>",
        "    <VCToolsInstallDir>$VcToolsInstallDir</VCToolsInstallDir>",
        "    <WDKContentRoot>$WdkRoot</WDKContentRoot>",
        "    <WdkContentRoot>$WdkRoot</WdkContentRoot>",
        '    <VisualStudioVersion>17.0</VisualStudioVersion>',
        '  </PropertyGroup>',
        '</Project>'
    ) -join "`r`n"

    Set-Content -Path $Path -Value $xml -Encoding UTF8
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$projectDir = Join-Path $repoRoot "host_boundary\mmi_minifilter"
$project = Join-Path $projectDir "mmi_minifilter.vcxproj"

$msbuild = Find-Vs2022MsBuild
if (-not $msbuild) {
    throw "Visual Studio 2022 MSBuild not found."
}

if ($msbuild -match "\\Microsoft Visual Studio\\18\\") {
    throw "Refusing Build Tools 18 MSBuild: $msbuild"
}

$vsInstallPath = Get-Vs2022InstallPath
if (-not $vsInstallPath) {
    throw "Visual Studio 2022 installation not found via vswhere."
}

$vcToolsVersion = Get-LatestVcToolsVersion -VsInstallPath $vsInstallPath
if (-not $vcToolsVersion) {
    throw "No MSVC toolset found under $vsInstallPath\VC\Tools\MSVC. Install/repair VS 2022 'Desktop development with C++'."
}

$vcToolsInstallDir = Join-Path $vsInstallPath "VC\Tools\MSVC\$vcToolsVersion\"
$clExe = Join-Path $vcToolsInstallDir "bin\Hostx64\x64\cl.exe"
if (-not (Test-Path $clExe)) {
    $vcvarsAll = Join-Path $vsInstallPath "VC\Auxiliary\Build\vcvarsall.bat"
    if (-not (Test-Path $vcvarsAll)) {
        throw "CL.exe not found and vcvarsall.bat is missing. Repair VS 2022 'Desktop development with C++'. Expected CL: $clExe"
    }
    throw "CL.exe not found at $clExe. Repair VS 2022 'Desktop development with C++'."
}

$wdkContentRoot = Get-WdkContentRoot
if (-not $wdkContentRoot) {
    throw "WDK not found. Install Windows Driver Kit 10.0.26100.x matching SDK 10.0.26100.x."
}

$driverKitTasks = Join-Path $wdkContentRoot "build\10.0.26100.0\bin\Microsoft.DriverKit.Build.Tasks.17.0.dll"
if (-not (Test-Path $driverKitTasks)) {
    throw "WDK DriverKit tasks missing: $driverKitTasks. Repair WDK 10.0.26100.x (VS 2022 / toolset 17.0)."
}

if ($env:VisualStudioVersion -and $env:VisualStudioVersion -ne "17.0") {
    Write-Warning "Ignoring env VisualStudioVersion=$($env:VisualStudioVersion); WDK 26100 requires 17.0 (VS 2022)."
}

$toolsetProps = Get-WdkToolsetProps
if (-not $toolsetProps) {
    Write-Host "WDK toolset missing - run install helper (Admin if prompted)..."
    & (Join-Path $repoRoot "scripts\install_m4_wdk_toolset.ps1") -SkipVsix
    $toolsetProps = Get-WdkToolsetProps
}
if (-not $toolsetProps) {
    throw "WDK toolset still missing. Run as Administrator: .\scripts\install_m4_wdk_toolset.ps1 -SkipVsix"
}

Write-Host "WDK toolset: $toolsetProps"
Write-Host "Using MSBuild: $msbuild"
Write-Host "VS install: $vsInstallPath"
Write-Host "VCToolsVersion: $vcToolsVersion"
Write-Host "WDKContentRoot: $wdkContentRoot"
Write-Host "VisualStudioVersion: 17.0 (pinned for WDK 26100 DriverKit tasks)"
Write-Host "Building $project"

$signMode = if ($TestSign) { "TestSign" } else { "Off" }
Write-Host "SignMode: $signMode"

$vsDir = $vsInstallPath.TrimEnd('\') + '\'
$vcToolsDir = $vcToolsInstallDir.TrimEnd('\') + '\'
$wdkRoot = $wdkContentRoot.TrimEnd('\') + '\'
$buildEnvProps = Join-Path $projectDir "mmi_build_env.props"

Write-MmiBuildEnvProps `
    -Path $buildEnvProps `
    -VsInstallDir $vsDir `
    -VcToolsVersion $vcToolsVersion `
    -VcToolsInstallDir $vcToolsDir `
    -WdkRoot $wdkRoot

Write-Host "Wrote $buildEnvProps"

# Path properties live in mmi_build_env.props (imported by mmi_wdk_paths.props).
# Do not pass /p:VSInstallDir=... on the command line — trailing backslashes break MSBuild parsing (MSB1008).
& $msbuild $project `
    '/p:Configuration=Release' `
    '/p:Platform=x64' `
    '/p:VisualStudioVersion=17.0' `
    '/p:ClearDevCommandPromptEnvVars=false' `
    ("/p:SignMode={0}" -f $signMode) `
    '/restore' `
    '/v:m'
if ($LASTEXITCODE -ne 0) {
    throw "MSBuild failed. If CL.exe or WDK headers are missing, repair VS 2022 C++ workload and WDK 10.0.26100.x."
}

$sys = Join-Path $projectDir "x64\Release\mmi_minifilter.sys"
if (-not (Test-Path $sys)) {
    throw "Expected output not found: $sys"
}

Write-Host "OK: $sys"
