# Remove MMI boundary minifilter (Phase 4D-b rollback).

$ErrorActionPreference = "Stop"

function Test-Admin {
    $current = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    return $current.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    throw "Run as Administrator."
}

Write-Host "Stopping mmi_boundary if loaded..."
& sc.exe stop mmi_boundary 2>$null | Out-Null
& fltmc.exe unload mmi_boundary 2>$null | Out-Null

$infName = "mmi_minifilter.inf"
Write-Host "Removing driver packages matching $infName ..."
& pnputil.exe /enum-drivers | Out-String | ForEach-Object {
    if ($_ -match "Published Name\s*:\s*(oem\d+\.inf)") {
        $published = $Matches[1]
        $detail = & pnputil.exe /enum-drivers /class ActivityMonitor 2>$null
        $block = & pnputil.exe /delete-driver $published /uninstall /force 2>&1
        Write-Host $block
    }
}

Write-Host "Done. Verify with: fltmc filters"
