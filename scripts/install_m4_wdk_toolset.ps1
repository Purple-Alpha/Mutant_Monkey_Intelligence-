# Register WDK toolset with Visual Studio 2022 (Phase 4D-b).
# Run as Administrator if copy-to-Program-Files is required.

param(
    [switch]$SkipVsix
)

$ErrorActionPreference = "Stop"

function Test-Admin {
    $current = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    return $current.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-Vs2022ToolsetDir {
    $vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
    if (-not (Test-Path $vswhere)) {
        return $null
    }
    $installPath = & $vswhere -latest -version "[17.0,18.0)" -products * -property installationPath 2>$null
    if (-not $installPath) {
        return $null
    }
    return Join-Path $installPath "MSBuild\Microsoft\VC\v170\Platforms\x64\PlatformToolsets\WindowsKernelModeDriver10.0"
}

function Install-WdkVsix {
    $vsix = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\Vsix" -Recurse -Filter "WDK.vsix" -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if (-not $vsix) {
        Write-Host "WDK.vsix not found under Windows Kits\10\Vsix (standalone WDK may not have bundled VSIX)."
        return $false
    }

    $vsixInstaller = Get-ChildItem "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer" -Recurse -Filter "VSIXInstaller.exe" -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not $vsixInstaller) {
        Write-Warning "VSIXInstaller.exe not found."
        return $false
    }

    Write-Host "Installing $($vsix.FullName) via $($vsixInstaller.FullName)"
    & $vsixInstaller.FullName /quiet $vsix.FullName
    Start-Sleep -Seconds 3
    return $true
}

function Install-ToolsetShim {
    param([string]$DestDir)

    $repoRoot = Split-Path -Parent $PSScriptRoot
    $srcDir = Join-Path $repoRoot "host_boundary\mmi_minifilter\msbuild\toolset\Platforms\x64\PlatformToolsets\WindowsKernelModeDriver10.0"
    if (-not (Test-Path $srcDir)) {
        throw "Missing toolset shim source: $srcDir"
    }

    New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
    Copy-Item (Join-Path $srcDir "Toolset.props") (Join-Path $DestDir "Toolset.props") -Force
    Copy-Item (Join-Path $srcDir "Toolset.targets") (Join-Path $DestDir "Toolset.targets") -Force
    $importAfterSrc = Join-Path $srcDir "ImportAfter"
    if (Test-Path $importAfterSrc) {
        $importAfterDest = Join-Path $DestDir "ImportAfter"
        New-Item -ItemType Directory -Path $importAfterDest -Force | Out-Null
        Copy-Item (Join-Path $importAfterSrc "*") $importAfterDest -Force
    }
    Write-Host "Copied toolset shim to $DestDir"
}

$toolsetDir = Get-Vs2022ToolsetDir
if (-not $toolsetDir) {
    throw "Visual Studio 2022 installation not found."
}

$toolsetProps = Join-Path $toolsetDir "Toolset.props"
if (Test-Path $toolsetProps) {
    Write-Host "Refreshing WDK toolset shim at $toolsetDir"
} else {
    Write-Host "Installing WDK toolset shim at $toolsetDir"
}

if (-not $SkipVsix) {
    Install-WdkVsix | Out-Null
}

$toolsetTargets = Join-Path $toolsetDir "Toolset.targets"
$needsShim = -not (Test-Path $toolsetProps)
if (Test-Path $toolsetTargets) {
    $targetsText = Get-Content $toolsetTargets -Raw
    if ($targetsText -notmatch "Microsoft\.CppCommon\.targets") {
        $needsShim = $true
    }
}

if (-not $needsShim) {
    Write-Host "OK: WDK toolset already registered at $toolsetDir"
    exit 0
}

if (-not (Test-Admin)) {
    throw "WDK toolset incomplete. Re-run as Administrator: .\scripts\install_m4_wdk_toolset.ps1 -SkipVsix"
}

Install-ToolsetShim -DestDir $toolsetDir
if (-not (Test-Path $toolsetProps)) {
    throw "Toolset install failed: $toolsetProps still missing."
}

Write-Host "OK: WDK toolset registered at $toolsetDir"
