# Install/load MMI boundary minifilter (Phase 4D-b) — Administrator + test signing.
param(
    [string]$AuthorityRoot = "C:\MMI",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

function Test-Admin {
    $current = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    return $current.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    throw "Run as Administrator (test signing + driver install)."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$projectDir = Join-Path $repoRoot "host_boundary\mmi_minifilter"
$inf = Join-Path $projectDir "mmi_minifilter.inf"

if (-not $SkipBuild) {
    & (Join-Path $repoRoot "scripts\build_m4_minifilter.ps1") -TestSign
}

$staging = Join-Path $projectDir "x64\Release"
$sys = Join-Path $staging "mmi_minifilter.sys"
if (-not (Test-Path $sys)) {
    throw "Missing built driver: $sys"
}

# inf2cat emits stamped INF + signed CAT beside SYS under x64\Release\mmi_minifilter\.
$builtPackageDir = Join-Path $staging "mmi_minifilter"
$packageSourceDir = if (Test-Path (Join-Path $builtPackageDir "mmi_minifilter.cat")) {
    $builtPackageDir
} else {
    $staging
}

$packageInfSource = Join-Path $packageSourceDir "mmi_minifilter.inf"
if (-not (Test-Path $packageInfSource)) {
    $packageInfSource = $inf
}
$packageSysSource = if (Test-Path (Join-Path $packageSourceDir "mmi_minifilter.sys")) {
    Join-Path $packageSourceDir "mmi_minifilter.sys"
} else {
    $sys
}
$packageCatSource = Join-Path $packageSourceDir "mmi_minifilter.cat"
if (-not (Test-Path $packageCatSource)) {
    $cat = Get-ChildItem $staging -Filter "*.cat" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cat) {
        $packageCatSource = $cat.FullName
    }
}

# Volume-relative NTFS path for minifilter registry (e.g. \MMI).
$full = (Resolve-Path $AuthorityRoot).Path
if ($full.Length -lt 3 -or $full[1] -ne ':') {
    throw "AuthorityRoot must be a drive path like C:\MMI"
}
function Get-MinifilterInstanceCount {
    param(
        [Parameter(Mandatory = $true)][string]$FilterName
    )

    $output = & fltmc.exe filters 2>&1 | Out-String
    foreach ($line in ($output -split "`r?`n")) {
        if ($line -notmatch [regex]::Escape($FilterName)) {
            continue
        }
        $tail = $line.Substring($line.IndexOf($FilterName, [System.StringComparison]::OrdinalIgnoreCase) + $FilterName.Length).Trim()
        $count = ($tail -split '\s+', 2)[0]
        if ($count -match '^\d+$') {
            return [int]$count
        }
    }
    return 0
}

function Ensure-MinifilterAttached {
    param(
        [Parameter(Mandatory = $true)][string]$FilterName,
        [Parameter(Mandatory = $true)][string]$DriveLetter
    )

    $instances = Get-MinifilterInstanceCount -FilterName $FilterName
    if ($instances -gt 0) {
        Write-Host "$FilterName already attached ($instances instance(s))"
        return
    }

    Write-Host "Attaching $FilterName to $DriveLetter (automatic attach had 0 instances)..."
    & fltmc.exe attach $FilterName $DriveLetter 2>&1 | Write-Host
    if ($LASTEXITCODE -ne 0) {
        throw "fltmc attach $FilterName $DriveLetter failed with exit code $LASTEXITCODE"
    }

    $instances = Get-MinifilterInstanceCount -FilterName $FilterName
    if ($instances -le 0) {
        throw "$FilterName still has 0 instances after fltmc attach."
    }
    Write-Host "$FilterName attached ($instances instance(s))"
}

$volumeRelative = "\" + $full.Substring(3).Replace('/', '\')
$authorityDrive = $full.Substring(0, 2)
Write-Host "AuthorityRoot registry value: $volumeRelative"
Write-Host "Authority drive: $authorityDrive"

Write-Host "Stopping mmi_boundary before driver package update..."
& sc.exe stop mmi_boundary 2>$null | Out-Null
Start-Sleep -Seconds 2

# Copy INF + SYS to a single staging folder for pnputil.
$packageDir = Join-Path $projectDir "package"
if (Test-Path $packageDir) {
    Remove-Item -Recurse -Force $packageDir
}
New-Item -ItemType Directory -Path $packageDir | Out-Null
Copy-Item $packageSysSource (Join-Path $packageDir "mmi_minifilter.sys")
Copy-Item $packageInfSource (Join-Path $packageDir "mmi_minifilter.inf")
if (-not (Test-Path $packageCatSource)) {
    throw "Missing signed catalog (mmi_minifilter.cat). Rebuild with -TestSign; inf2cat output should be under x64\Release\mmi_minifilter\."
}
Copy-Item $packageCatSource (Join-Path $packageDir "mmi_minifilter.cat")
Write-Host "Package staged: INF + SYS + CAT from $packageSourceDir"

$testSigningLine = bcdedit /enum "{current}" 2>$null | Select-String -Pattern "testsigning" -SimpleMatch
if ($testSigningLine -notmatch "Yes") {
    throw "Test signing is not active (bcdedit testsigning != Yes). Run: bcdedit /set testsigning on  then reboot before pnputil install."
}

$packageInf = Join-Path $packageDir "mmi_minifilter.inf"
Write-Host "Installing driver package from $packageInf"
& pnputil.exe /add-driver $packageInf /install
if ($LASTEXITCODE -ne 0) {
    throw "pnputil failed with exit code $LASTEXITCODE"
}

$serviceKey = "HKLM:\SYSTEM\CurrentControlSet\Services\mmi_boundary\Parameters"
if (-not (Test-Path $serviceKey)) {
    New-Item -Path $serviceKey -Force | Out-Null
}
Set-ItemProperty -Path $serviceKey -Name AuthorityRoot -Value $volumeRelative -Type String

Write-Host "Starting filter service mmi_boundary"
& sc.exe start mmi_boundary
if ($LASTEXITCODE -ne 0) {
    Write-Warning "sc start returned $LASTEXITCODE (may already be running)."
}

Ensure-MinifilterAttached -FilterName "mmi_boundary" -DriveLetter $authorityDrive

Write-Host "`nFilter state:"
& fltmc.exe filters

Write-Host "`nNext (still in Admin session after test signing reboot if needed):"
Write-Host "  cd $repoRoot"
Write-Host "  python scripts/m4_minifilter_suite.py --live --json"
