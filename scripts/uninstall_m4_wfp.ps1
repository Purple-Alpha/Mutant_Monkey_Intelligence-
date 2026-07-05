# Remove MMI WFP engine (Phase 4E) — Administrator required.
param(
    [string]$EvidenceRoot = "C:\mmi_m4_evidence\boundary"
)

$ErrorActionPreference = "Stop"

function Test-Admin {
    $current = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    return $current.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    throw "Run as Administrator."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$scratchRoot = "C:\mmi_boundary_scratch\mmi_wfp_build"
$helperExe = Join-Path $scratchRoot "x64\Release\mmi_wfp_helper.exe"
$configPath = Join-Path $EvidenceRoot "wfp_install_config.json"

if (Test-Path $helperExe) {
    if (Test-Path $configPath) {
        & $helperExe uninstall --config $configPath
    } else {
        & $helperExe uninstall
    }
}

$statePath = Join-Path $EvidenceRoot "wfp_engine_state.json"
if (Test-Path $statePath) {
    Remove-Item $statePath -Force
}

Write-Host "WFP engine removed."
