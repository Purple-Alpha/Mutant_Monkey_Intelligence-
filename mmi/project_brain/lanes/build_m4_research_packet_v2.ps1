# Build M4 research packet v2 — attach actual ZIP to ChatGPT (not terminal listing).
$ErrorActionPreference = "Stop"
$repo = "C:\Architectapp_clean"
$out = Join-Path $env:TEMP "m4_research_packet_v2"
$zip = Join-Path $env:TEMP "m4_research_packet_v2_2026-07-03.zip"
$zipRepo = Join-Path $repo "mmi\project_brain\lanes\m4_research_packet_v2_2026-07-03.zip"

$excludePattern = '\\(\.git|venv|\.venv|\.venv_kinetic|node_modules|\.pytest_cache|__pycache__|\.tmp\.driveupload)(\\|$)'

if (Test-Path $out) { Remove-Item -Recurse -Force $out }

function Copy-Rel([string]$rel) {
    $src = Join-Path $repo $rel
    if (-not (Test-Path $src)) { return $false }
    if ($src -match $excludePattern) { return $false }
    if (Test-Path $src -PathType Container) {
        Get-ChildItem $src -Recurse -File | ForEach-Object {
            $r = $_.FullName.Substring($repo.Length + 1)
            if ($r -match $excludePattern) { return }
            $dest = Join-Path $out $r
            New-Item -ItemType Directory -Force -Path (Split-Path $dest -Parent) | Out-Null
            Copy-Item $_.FullName $dest -Force
        }
    } else {
        $dest = Join-Path $out $rel
        New-Item -ItemType Directory -Force -Path (Split-Path $dest -Parent) | Out-Null
        Copy-Item $src $dest -Force
    }
    return $true
}

# Mandatory scope
Copy-Rel "tasks.json" | Out-Null
Copy-Rel "AGENTS.md" | Out-Null
Copy-Rel "mmi\project_brain\status" | Out-Null
Copy-Rel "mmi\project_brain\lanes\RESEARCH_M4_EVOLUTION_GATE_2026-07.md" | Out-Null
Copy-Rel "mmi\project_brain\lanes\RESEARCH_M4_EVOLUTION_GATE_RELAY_PORTABLE_2026-07-03.md" | Out-Null
Copy-Rel "mmi\project_brain\lanes\RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md" | Out-Null
Copy-Rel "mmi\project_brain\lanes\CHATGPT_MMI_LANE_INTEGRATION_2026-07-03.md" | Out-Null
Copy-Rel "mmi\project_brain\architecture\MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md" | Out-Null
Copy-Rel "mmi\project_brain\chaos\MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md" | Out-Null
Copy-Rel "mmi\project_brain\architecture\MMI_AGI_EVOLUTION_PATHWAY.md" | Out-Null
Copy-Rel "mmi\project_brain\lanes\RESEARCH_host_boundary_wsl_windows_2026-06.md" | Out-Null

# Harness + core implementation
$code = @(
    "scripts\genomic_realignment_loop_harness.py",
    "scripts\control_envelope_harness.py",
    "scripts\email_lanes_harness.py",
    "scripts\console_server_harness.py",
    "scripts\proof_gate_harness.py",
    "scripts\phase1_stability_harness.py",
    "scripts\chaos_lab_provisioner.py",
    "ops\genomic_realignment_loop.py",
    "tests\test_genomic_realignment_loop.py",
    "tests\test_genomic_constraint_validator.py",
    "tests\test_metadata_ingress_gate.py",
    "tests\test_control_envelope.py",
    "tests\test_console_server.py",
    "mmi\project_brain\chaos\mmi_control_envelope.py",
    "mmi\project_brain\chaos\console_evidence_gate.py",
    "mmi\project_brain\chaos\canary_metadata_layer.py",
    "mmi\project_brain\chaos\metadata_ingress_gate.py",
    "mmi\project_brain\chaos\mirror_dimension_router.py",
    "mmi\project_brain\chaos\weapon_battlefield_scoring.py",
    "mmi\project_brain\chaos\purple_evasion_suite.py",
    "mmi\project_brain\chaos\genomic_constraint_validator.py",
    "mmi\project_brain\chaos\genomic_constraint_synth.py"
)
foreach ($rel in $code) { Copy-Rel $rel | Out-Null }

# Topic grep under mmi/ + selected roots
$pattern = "M4|PERFECT|host boundary|host-boundary|canary|48h|genomic|evolution gate|Gate C|AFE|evolution_gate|destructive evolution"
$grepRoots = @(
    (Join-Path $repo "mmi"),
    (Join-Path $repo "scripts"),
    (Join-Path $repo "tests"),
    (Join-Path $repo "ops")
)
foreach ($root in $grepRoots) {
    if (-not (Test-Path $root)) { continue }
    Get-ChildItem $root -Recurse -Include *.md, *.json, *.py -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch $excludePattern } |
        ForEach-Object {
            try {
                $content = Get-Content $_.FullName -Raw -ErrorAction Stop
                if ($content -match $pattern) {
                    $rel = $_.FullName.Substring($repo.Length + 1)
                    Copy-Rel $rel | Out-Null
                }
            } catch {}
        }
}

$fileCount = (Get-ChildItem $out -Recurse -File).Count
$manifest = @(
    "# M4 Research Packet v2 Manifest",
    "",
    "**Built:** $(Get-Date -Format o)",
    "**Authority repo:** C:\Architectapp_clean",
    "**Task:** mmi-m4-evolution-gate-research-v2",
    "**Authorization:** RESEARCH PACKET V2 ONLY — no spec, no build, no gate closure",
    "",
    "## Upload instructions (ChatGPT)",
    "",
    "Attach this ZIP file directly in chat. Do NOT paste terminal zip output.",
    "",
    "## Deliverable",
    "",
    "Revise: mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md",
    "",
    "Read directly from ZIP:",
    "- mmi/project_brain/status/ (full)",
    "- tasks.json",
    "- Evolution Matrix M4 + Weapon Matrix section 6",
    "- RESEARCH_M4_EVOLUTION_GATE_2026-07.md",
    "",
    "Remove [UNVERIFIED] where source text was read. Do NOT claim PERFECT or authorize build.",
    "",
    "## File count",
    "",
    "$fileCount files"
)
Set-Content -Path (Join-Path $out "M4_RESEARCH_PACKET_V2_MANIFEST.md") -Value $manifest -Encoding UTF8

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $out -DestinationPath $zip -Force
Copy-Item $zip $zipRepo -Force

Write-Output "ZIP=$zip"
Write-Output "ZIP_REPO=$zipRepo"
Write-Output "FILES=$fileCount"
