# MMI Closeout Evidence Contract — P8

Status: ACTIVE
Owner: Codex implementation, Matt authorization
Scope: `scripts/complete_task.py` completed-task records

## Purpose

Completed tasks must be explainable and recoverable under pressure. A closeout is
not just prose; it must carry enough machine-readable evidence to answer:

- What changed?
- Which outputs were claimed?
- Which gates ran?
- What evidence artifact, if any, supports the closeout?
- Who accepted the caveats?

## Required Completed-Task Fields

`complete_task.py` records these fields on every successful closeout:

| Field | Meaning |
| --- | --- |
| `output_files` | Claimed outputs; H1 verifies each path exists. |
| `verification_commands` | Structured list of verification steps represented as command records with exit codes. |
| `verification_artifact` | Optional JSON evidence artifact path; if supplied, it must exist and parse before closeout. |
| `report_card` | Required independent report-card path; grade math is validated before closeout. |
| `result_summary` | Human summary prefixed with `PASS`, `PASS WITH REVISIONS`, or `FAIL`. |
| `sign_off` | Closeout enum: `PASS`, `PASS WITH REVISIONS`, or `FAIL`. |
| `sign_off_tier` | Person/lane accepting revision caveats; defaults to `--by`. |
| `closeout_verification` | H1/H2/verify-json/artifact/report-card gate results. |
| `closeout_evidence_contract` | Contract marker and recovery instructions. |

## Operator Use

Default closeout still works:

```bash
python scripts/complete_task.py TASK_ID \
  --by Codex \
  --summary "Implemented scoped fix." \
  --output path/to/output \
  --report-card path/to/report_card.md
```

For closeouts with a separate evidence JSON:

```bash
python scripts/complete_task.py TASK_ID \
  --by Codex \
  --summary "PASS WITH REVISIONS - Display corrected; conflict blocking deferred." \
  --sign-off "PASS WITH REVISIONS" \
  --sign-off-tier Matt \
  --output path/to/output \
  --report-card path/to/report_card.md \
  --verification-artifact mmi/project_brain/status/verify/TASK_ID.json
```

If `--verification-artifact` is supplied and the file is missing, not JSON, or not
a JSON object, closeout blocks before `tasks.json` is written.

## Hard Boundary

P8 does not weaken H1, H2, OPSEC, backup, or task-specific gates. It only records
the evidence contract in a consistent shape after existing gates pass.
