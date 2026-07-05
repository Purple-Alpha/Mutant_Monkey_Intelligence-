# MMI Evidence–Summary Binding

**Status:** HARD CONTROL — documentation only  
**Date:** 2026-07-04  
**Related:** RR-M4-008, INV-5, §11 evidence chain

**Forbidden claims:** "the summary is sufficient," "the report is enough."

---

## Rule

Every human-readable claim must cite **raw artifact lineage**. A summary that cannot be traced to raw evidence is **not acceptable** (invalidation rule I-07).

---

## Required trace chain

```text
claim ID
  → raw artifact path
  → artifact hash (SHA-256)
  → run ID / RUN_NONCE
  → time window (UTC)
  → evidence excerpt or pointer
  → summary statement
  → reviewer identity
  → residual-risk link (RR-* or R-*)
```

---

## Mandatory fields per gate output

| Field | Required for |
| ----- | ------------ |
| `evidence_dir` | Harness outputs (e.g. `C:/mmi_m4_evidence/fuzz/`) |
| `seed`, `iters` | Fuzz reproducibility |
| `completed_at` | Run context |
| `fuzz_summary.json` hash | Summary binding |
| Command replay string | Independent verification |

---

## Failure mode prevented

```text
Raw evidence:  narrow Phase 2 fuzz PASS
Bad summary:   "containment proven" / "M4 safer"
```

Binding rules reject promotion language that exceeds artifact scope.

---

## EVIDENCE_ROOT discipline

- Evidence writes **outside** `AUTHORITY_ROOT` (§2, §13, H-EVID-001).
- Default host path: `C:/mmi_m4_evidence/` or `$MMI_EVIDENCE_ROOT`.
- Harness must fail-closed if evidence path is under authority (`mmi/m4/evidence_paths.py`).
