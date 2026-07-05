$ErrorActionPreference = "Stop"
$repo = "C:\Architectapp_clean"
$out = Join-Path $env:TEMP "m4_research_packet_targeted"
$zip = Join-Path $env:TEMP "m4_research_packet_targeted_2026-07-03.zip"

if (Test-Path $out) { Remove-Item -Recurse -Force $out }

$core = @(
    "AGENTS.md",
    "mmi\project_brain\lanes\RESEARCH_M4_EVOLUTION_GATE_2026-07.md",
    "mmi\project_brain\lanes\RESEARCH_M4_EVOLUTION_GATE_RELAY_PORTABLE_2026-07-03.md",
    "mmi\project_brain\chaos\MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md",
    "mmi\project_brain\architecture\MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md",
    "mmi\project_brain\architecture\MMI_AGI_EVOLUTION_PATHWAY.md",
    "mmi\project_brain\architecture\MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md",
    "mmi\project_brain\architecture\MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md",
    "mmi\project_brain\architecture\MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md",
    "mmi\project_brain\architecture\MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md",
    "mmi\project_brain\status\MMI_PIPE_STAGING.json",
    "mmi\project_brain\status\MMI_MACRO_BUILD_DECISION_2026-07-03.md",
    "mmi\project_brain\status\MMI_GENOMIC_REALIGNMENT_LOOP_STEP5_CLOSEOUT_2026-07-03.md",
    "mmi\project_brain\status\MMI_CLIENT_EMAIL_LANES_V1_CLOSEOUT_2026-07-03.md",
    "mmi\project_brain\status\MMI_PHASE1_STABILITY_PASS_2026-07-02.md",
    "mmi\project_brain\status\MMI_GENOMIC_COMPLETION_GATE_2026-07-03.json",
    "mmi\project_brain\status\MMI_CLIENT_EMAIL_LANES_COMPLETION_GATE_2026-07-03.json",
    "mmi\project_brain\lanes\RESEARCH_host_boundary_wsl_windows_2026-06.md",
    "mmi\project_brain\chaos\MMI_CHAOS_LAB_PROVISIONER_SPEC_2026-07.md"
)

function Copy-Rel($rel) {
    $src = Join-Path $repo $rel
    if (-not (Test-Path $src)) { return }
    $dest = Join-Path $out $rel
    $destDir = Split-Path $dest -Parent
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    Copy-Item $src $dest -Force
}

foreach ($rel in $core) { Copy-Rel $rel }

$pattern = "Evolution Matrix|Weapon Matrix|M4|PERFECT|host boundary|canary|genomic v2|email lanes|evolution gate|48h|AFE|Gate C"
Get-ChildItem -Path (Join-Path $repo "mmi") -Recurse -Include *.md, *.json -File |
    Where-Object { $_.FullName -notmatch "\\\.venv|\\node_modules" } |
    ForEach-Object {
        try {
            $content = Get-Content $_.FullName -Raw -ErrorAction Stop
            if ($content -match $pattern) {
                $rel = $_.FullName.Substring($repo.Length + 1)
                Copy-Rel $rel
            }
        } catch {}
    }

$fileCount = (Get-ChildItem $out -Recurse -File).Count
$manifest = @(
    "# M4 Research Packet Manifest",
    "",
    "**Authority repo:** C:\Architectapp_clean",
    "**NOT:** /home/socialarchitect/northstar",
    "**Task:** mmi-m4-evolution-gate-research",
    "**Deliver back:** RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md",
    "",
    "File count: $fileCount"
)
Set-Content -Path (Join-Path $out "M4_RESEARCH_PACKET_MANIFEST.md") -Value $manifest -Encoding UTF8

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $out -DestinationPath $zip -Force

Write-Output "ZIP=$zip"
Write-Output "FILES=$fileCount"
