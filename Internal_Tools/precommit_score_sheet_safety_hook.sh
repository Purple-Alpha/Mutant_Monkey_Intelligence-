#!/usr/bin/env bash
# Wave 3.1 score-sheet safety hook.
# Scans staged score-sheet evidence/review surfaces for secrets, raw financial
# identifiers, raw payload leakage, and chain-of-thought labels.

set -euo pipefail

mapfile -d '' STAGED_FILES < <(
  git diff --cached --name-only -z --diff-filter=ACM -- \
    '4. Product_Roadmap/Research_Inputs/Testing_Score_Sheet_Schema.md' \
    'PROJECT_ACTIVITY_LOG.md' \
    'audit_outputs/score_sheet_candidates/**/*.candidate.jsonl' \
    '4. Product_Roadmap/Score_Sheet_Candidate_Review_Promotion_Deep_Dive.md' \
    '4. Product_Roadmap/Score_Sheet_Review_Ledger_Wave3_1_Deep_Dive.md'
)

if [ "${#STAGED_FILES[@]}" -eq 0 ]; then
  exit 0
fi

python3 audit_tools/score_sheet_review_scanner.py "${STAGED_FILES[@]}"
