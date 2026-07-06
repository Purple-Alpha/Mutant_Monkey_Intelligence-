# Install/load MMI WFP default-deny engine (Phase 4E) — Administrator required.
param(
    [string]$AuthorityRoot = "C:\MMI",
    [string]$EvidenceRoot = "C:\mmi_m4_evidence\boundary",
    [string]$ProbeAccount = "MmiWfpProbe",
    [string]$ProbePassword = $env:MMI_WFP_PROBE_PASSWORD,
    [switch]$SkipBuild
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
$policyManifest = Join-Path $EvidenceRoot "policy_manifest.json"

if (-not $SkipBuild) {
    & (Join-Path $repoRoot "scripts\build_m4_wfp.ps1")
}

if (-not (Test-Path $helperExe)) {
    throw "Missing built helper: $helperExe"
}

if (-not $ProbePassword) {
    $ProbePassword = "Mmi-Wfp-Probe-Dev-2026!"
    Write-Host "Using dev probe password (set MMI_WFP_PROBE_PASSWORD to override)."
}

function Test-LocalProbeAccount {
    param([Parameter(Mandatory = $true)][string]$Name)
    try {
        $null = (New-Object System.Security.Principal.NTAccount($Name)).Translate(
            [System.Security.Principal.SecurityIdentifier]
        )
        return $true
    } catch {
        return $false
    }
}

function Ensure-LocalProbeAccount {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Password
    )
    if (Test-LocalProbeAccount -Name $Name) {
        return
    }
    Write-Host "Creating local probe account $Name ..."
    if (Get-Command New-LocalUser -ErrorAction SilentlyContinue) {
        $secure = ConvertTo-SecureString $Password -AsPlainText -Force
        New-LocalUser -Name $Name -Password $secure -PasswordNeverExpires -UserMayNotChangePassword | Out-Null
        return
    }
    $addOut = net user $Name $Password /add /y 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create probe account ${Name}: $addOut"
    }
    net user $Name /expires:never 2>&1 | Out-Null
    net user $Name /passwordchg:no 2>&1 | Out-Null
}

Ensure-LocalProbeAccount -Name $ProbeAccount -Password $ProbePassword

$probeSid = (New-Object System.Security.Principal.NTAccount("$env:COMPUTERNAME\$ProbeAccount")).Translate(
    [System.Security.Principal.SecurityIdentifier]
).Value
Write-Host "Signed WFP clone target SID: $probeSid"

Write-Host "Re-sealing policy_manifest with signed clone_sid + probe_account_name ..."
& python (Join-Path $repoRoot "scripts\m4_authority_seal.py") `
    --authority $AuthorityRoot `
    --evidence $EvidenceRoot `
    --store `
    --clone-sid $probeSid `
    --probe-account $ProbeAccount `
    --json | Out-Null

$manifest = Get-Content $policyManifest -Raw | ConvertFrom-Json
$manifestSid = $manifest.wfp_policy.clone_sid
if ($manifestSid -ne $probeSid) {
    throw "policy_manifest wfp_policy.clone_sid mismatch after re-seal (expected $probeSid got $manifestSid)"
}

New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null

$config = @{
    engine_name = "mmi_wfp"
    target_clone_sid = $manifestSid
    probe_account_name = $ProbeAccount
    probe_account_password = $ProbePassword
    host = "127.0.0.1"
    port = 9443
    evidence_dir = $EvidenceRoot
} | ConvertTo-Json -Depth 4

$configPath = Join-Path $EvidenceRoot "wfp_install_config.json"
Set-Content -Path $configPath -Value $config -Encoding UTF8

& $helperExe install --config $configPath
if ($LASTEXITCODE -ne 0) {
    $hex = ('0x{0:X8}' -f ($LASTEXITCODE -band 0xFFFFFFFF))
    throw "mmi_wfp_helper install failed with exit code $LASTEXITCODE ($hex)."
}

$status = & $helperExe status --json | ConvertFrom-Json
Write-Host ($status | ConvertTo-Json -Compress)
if (-not $status.loaded -or [int]$status.filter_count -lt 4) {
    throw "WFP engine not fully loaded after install (need 4 filters on V4/V6 ALE_AUTH_CONNECT layers)."
}

Write-Host "WFP engine installed for signed clone SID. Live probes run via helper impersonation."
Write-Host "Run: python scripts/m4_wfp_suite.py --live --json"
