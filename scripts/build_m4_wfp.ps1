# Build MMI WFP user-mode helper (Phase 4E).
# Toolchain props + output go to scratch — authority tree is minifilter write-deny.
param(
    [switch]$TestSign,
    [string]$ScratchRoot = "C:\mmi_boundary_scratch\mmi_wfp_build"
)

$ErrorActionPreference = "Stop"

function Find-Vs2022MsBuild {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        $installPath = & $vswhere -latest -version "[17.0,18.0)" -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
        if ($installPath) {
            $candidate = Join-Path $installPath "MSBuild\Current\Bin\amd64\MSBuild.exe"
            if (Test-Path $candidate) { return $candidate }
        }
    }
    return $null
}

function Get-Vs2022InstallPath {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        return (& $vswhere -latest -version "[17.0,18.0)" -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null)
    }
    return $null
}

function Get-LatestVcToolsVersion {
    param([Parameter(Mandatory = $true)][string]$VsInstallPath)

    $msvcRoot = Join-Path $VsInstallPath "VC\Tools\MSVC"
    if (-not (Test-Path $msvcRoot)) { return $null }

    $latest = Get-ChildItem $msvcRoot -Directory |
        Sort-Object { [version]$_.Name } -Descending |
        Select-Object -First 1
    if (-not $latest) { return $null }
    return $latest.Name
}

function Get-WindowsSdkRoot {
    $candidate = Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10"
    if (Test-Path $candidate) { return $candidate }
    return $null
}

function Get-LatestWindowsSdkVersion {
    param([Parameter(Mandatory = $true)][string]$SdkRoot)

    $includeRoot = Join-Path $SdkRoot "Include"
    if (-not (Test-Path $includeRoot)) { return "10.0" }
    $latest = Get-ChildItem $includeRoot -Directory |
        Where-Object { $_.Name -match '^\d' } |
        Sort-Object { [version]$_.Name } -Descending |
        Select-Object -First 1
    if (-not $latest) { return "10.0" }
    return $latest.Name
}

function Write-WfpBuildEnvProps {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$VsInstallDir,
        [Parameter(Mandatory = $true)][string]$VcToolsVersion,
        [Parameter(Mandatory = $true)][string]$VcToolsInstallDir,
        [Parameter(Mandatory = $true)][string]$WindowsSdkDir,
        [Parameter(Mandatory = $true)][string]$WindowsSdkVersion
    )

    $xml = @(
        '<?xml version="1.0" encoding="utf-8"?>',
        '<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">',
        '  <PropertyGroup>',
        "    <VSInstallDir>$VsInstallDir</VSInstallDir>",
        "    <VCToolsVersion>$VcToolsVersion</VCToolsVersion>",
        "    <VCToolsInstallDir>$VcToolsInstallDir</VCToolsInstallDir>",
        "    <WindowsSdkDir>$WindowsSdkDir</WindowsSdkDir>",
        "    <WindowsSDKVersion>$WindowsSdkVersion</WindowsSDKVersion>",
        '    <VisualStudioVersion>17.0</VisualStudioVersion>',
        '  </PropertyGroup>',
        '</Project>'
    ) -join "`r`n"

    Set-Content -Path $Path -Value $xml -Encoding UTF8
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$project = Join-Path $repoRoot "host_boundary\mmi_wfp\mmi_wfp_helper.vcxproj"

$msbuild = Find-Vs2022MsBuild
if (-not $msbuild) {
    throw "Visual Studio 2022 MSBuild not found."
}

$vsInstallPath = Get-Vs2022InstallPath
if (-not $vsInstallPath) {
    throw "Visual Studio 2022 installation not found via vswhere."
}

$vcToolsVersion = Get-LatestVcToolsVersion -VsInstallPath $vsInstallPath
if (-not $vcToolsVersion) {
    throw "No MSVC toolset found. Repair VS 2022 'Desktop development with C++' workload."
}

$vcToolsInstallDir = Join-Path $vsInstallPath "VC\Tools\MSVC\$vcToolsVersion\"
$clExe = Join-Path $vcToolsInstallDir "bin\Hostx64\x64\cl.exe"
if (-not (Test-Path $clExe)) {
    throw "CL.exe not found at $clExe. Repair VS 2022 'Desktop development with C++'."
}

$windowsSdkRoot = Get-WindowsSdkRoot
if (-not $windowsSdkRoot) {
    throw "Windows 10 SDK not found under Program Files (x86)\Windows Kits\10."
}
$windowsSdkVersion = Get-LatestWindowsSdkVersion -SdkRoot $windowsSdkRoot

$outDir = Join-Path $ScratchRoot "x64\Release\"
$intDir = Join-Path $ScratchRoot "x64\Release\obj\"
New-Item -ItemType Directory -Force -Path $outDir, $intDir | Out-Null

$propsPath = Join-Path $ScratchRoot "mmi_wfp_build_env.props"
Write-WfpBuildEnvProps `
    -Path $propsPath `
    -VsInstallDir ($vsInstallPath.TrimEnd('\') + '\') `
    -VcToolsVersion $vcToolsVersion `
    -VcToolsInstallDir ($vcToolsInstallDir.TrimEnd('\') + '\') `
    -WindowsSdkDir ($windowsSdkRoot.TrimEnd('\') + '\') `
    -WindowsSdkVersion $windowsSdkVersion

Write-Host "Using MSBuild: $msbuild"
Write-Host "VS install: $vsInstallPath"
Write-Host "VCToolsVersion: $vcToolsVersion"
Write-Host "WindowsSDKVersion: $windowsSdkVersion"
Write-Host "Wrote $propsPath"
Write-Host "Building $project"
Write-Host "OutDir=$outDir"
Write-Host "IntDir=$intDir"

& $msbuild $project `
    '/p:Configuration=Release' `
    '/p:Platform=x64' `
    '/p:VisualStudioVersion=17.0' `
    "/p:OutDir=$outDir" `
    "/p:IntDir=$intDir" `
    '/restore' `
    '/v:m'
if ($LASTEXITCODE -ne 0) {
    throw "MSBuild failed for mmi_wfp_helper."
}

$exe = Join-Path $outDir "mmi_wfp_helper.exe"
if (-not (Test-Path $exe)) {
    throw "Expected output not found: $exe"
}

$marker = Join-Path $ScratchRoot "helper_path.txt"
Set-Content -Path $marker -Value $exe -Encoding ASCII
Write-Host "OK: $exe"
