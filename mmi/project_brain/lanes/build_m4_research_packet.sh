#!/usr/bin/env bash
# Build targeted M4 research ZIP for ChatGPT/Gemini upload.
# Run from WSL: bash mmi/project_brain/lanes/build_m4_research_packet.sh

set -euo pipefail

REPO="/mnt/c/Architectapp_clean"
OUT="/tmp/m4_research_packet_targeted"
ZIP="/tmp/m4_research_packet_targeted_2026-07-03.zip"
DATE_TAG="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

rm -rf "$OUT"
mkdir -p "$OUT"

copy() {
  local src="$1"
  if [[ -f "$REPO/$src" ]]; then
    mkdir -p "$OUT/$(dirname "$src")"
    cp "$REPO/$src" "$OUT/$src"
  fi
}

# Curated core (always include)
CORE=(
  "AGENTS.md"
  "mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md"
  "mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_RELAY_PORTABLE_2026-07-03.md"
  "mmi/project_brain/chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md"
  "mmi/project_brain/architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md"
  "mmi/project_brain/architecture/MMI_AGI_EVOLUTION_PATHWAY.md"
  "mmi/project_brain/architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md"
  "mmi/project_brain/architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md"
  "mmi/project_brain/architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md"
  "mmi/project_brain/architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md"
  "mmi/project_brain/status/MMI_PIPE_STAGING.json"
  "mmi/project_brain/status/MMI_MACRO_BUILD_DECISION_2026-07-03.md"
  "mmi/project_brain/status/MMI_GENOMIC_REALIGNMENT_LOOP_STEP5_CLOSEOUT_2026-07-03.md"
  "mmi/project_brain/status/MMI_CLIENT_EMAIL_LANES_V1_CLOSEOUT_2026-07-03.md"
  "mmi/project_brain/status/MMI_PHASE1_STABILITY_PASS_2026-07-02.md"
  "mmi/project_brain/status/MMI_GENOMIC_COMPLETION_GATE_2026-07-03.json"
  "mmi/project_brain/status/MMI_CLIENT_EMAIL_LANES_COMPLETION_GATE_2026-07-03.json"
  "mmi/project_brain/lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md"
  "mmi/project_brain/chaos/MMI_CHAOS_LAB_PROVISIONER_SPEC_2026-07.md"
  "mmi/project_brain/lanes/CODEX_HANDOFF_CLIENT_EMAIL_LANES_DIFF_REVIEW_2026-07-03.md"
)

for f in "${CORE[@]}"; do
  copy "$f"
done

# Optional root docs (include if present)
for f in PROJECT_HANDSHAKE.md MASTER_INDEX.md PROJECT_ACTIVITY_LOG.md; do
  copy "$f"
done

# Grep-expanded matches under mmi/ only (exclude heavy dirs)
if command -v rg >/dev/null 2>&1; then
  RG=rg
elif command -v grep >/dev/null 2>&1; then
  RG=""
else
  RG=""
fi

PATTERN='Evolution Matrix|Weapon Matrix|M4|PERFECT|host boundary|canary|genomic v2|email lanes|AGI §5|evolution gate|48h|AFE|Gate C'

if [[ -n "$RG" ]]; then
  while IFS= read -r f; do
    [[ "$f" == mmi/* ]] || continue
    copy "$f"
  done < <(cd "$REPO" && rg -l "$PATTERN" mmi --glob '*.md' --glob '*.json' 2>/dev/null || true)
else
  while IFS= read -r f; do
    [[ "$f" == ./mmi/* ]] || continue
    copy "${f#./}"
  done < <(cd "$REPO" && grep -RIl "$PATTERN" mmi --include='*.md' --include='*.json' 2>/dev/null || true)
fi

# Manifest
FILE_COUNT="$(find "$OUT" -type f | wc -l | tr -d ' ')"
cat > "$OUT/M4_RESEARCH_PACKET_MANIFEST.md" <<EOF
# M4 Research Packet Manifest

**Built:** $DATE_TAG  
**Authority repo:** C:\\Architectapp_clean (WSL: /mnt/c/Architectapp_clean)  
**NOT northstar:** /home/socialarchitect/northstar is a different/legacy path  
**Purpose:** ChatGPT/Gemini research lane — \`mmi-m4-evolution-gate-research\`  
**Deliver back:** \`RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md\`

## File count

$FILE_COUNT files

## Task

Read \`mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md\` first.  
Produce findings with 8 sections (see relay portable doc).  
Do NOT claim PERFECT closed or authorize build.

## Lane routing (MMI)

| Lane | Owner | Role |
|------|-------|------|
| Research | ChatGPT + Gemini | This packet |
| Spec | Claude | Architecture contract after findings |
| Plan/diff review | Codex | BUILDABLE / CLEAN |
| Implement | Cursor | Matt \`authorize build\` only |
| GATED | Matt | Final closeout |
EOF

rm -f "$ZIP"
(cd /tmp && zip -rq "$(basename "$ZIP")" "$(basename "$OUT")")

echo "PACKET=$ZIP"
echo "FILES=$FILE_COUNT"
echo "MANIFEST=$OUT/M4_RESEARCH_PACKET_MANIFEST.md"
