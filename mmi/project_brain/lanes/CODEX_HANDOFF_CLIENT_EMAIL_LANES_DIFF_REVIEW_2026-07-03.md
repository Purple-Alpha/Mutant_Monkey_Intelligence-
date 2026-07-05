# CODEX HANDOFF — Client Email Lanes Diff Review (v1)

**Date:** 2026-07-03  
**Lane:** Codex post-build diff review (mandatory hard stop before GATED)  
**Matt authorization:** `authorize build client email lanes v1`  
**Spec:** `architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md` (r2 PASS)  
**Plan review:** BUILDABLE (`lanes/CODEX_HANDOFF_CLIENT_EMAIL_LANES_PLAN_REVIEW_R2_2026-07-03.md`)

---

## R1 diff review — NOT CLEAN (fixed in R2)

**Blocker:** `verify_confirmation_chain()` promoted VERIFIED on hash-chain match alone without Ed25519/domain/normalizer/method/role/event_id checks (spec §4.6:276).

**R2 fix:** shared `_validate_confirmation_event_record()` + operator pubkey + attestation covers `prev_event_hash`; unsigned matching-record falsifier added.

## R2 diff review — NOT CLEAN (fixed in R3)

**Blocker:** R2 still skipped cryptographic validation for non-matching log lines. An unsigned/forged ConfirmationEvent for a *different* `fact_key` (or any invalid line) left `chain_ok: true` and allowed `tier: VERIFIED` from an earlier valid record — violating spec §4.6 “intact chain” + fail-closed on any break.

**Falsifier:** valid signed `banking.iban` append → append unsigned `other.fact` line with correct `prev_event_hash` → R2 returned `{"tier":"VERIFIED","chain_ok":true}`.

**R3 fix:**
- `verify_confirmation_chain()` validates **every** JSONL record (full attestation/schema/event_id), not only matching tenant/fact rows.
- Required-field + `prior_tier == OBSERVED` checks added.
- `append_confirmation_event()` uses atomic read-modify-write append.
- Harness falsifier expanded: unsigned matching **and** unsigned other-fact injection after valid append.
- Pytest updated for other-fact injection case.

---

## Build summary

| Artifact | Path |
|---|---|
| Policy Engine + orchestrator | `ops/client_email_lanes/` (17 modules) |
| Harness (T1–T7, T3a, T7b + H-rules) | `scripts/email_lanes_harness.py` |
| Pytest | `tests/test_client_email_lanes.py` |

**v1 defaults:** Drafting ON, Response OFF, `AUTONOMOUS_SEND=DISABLED`. Lane state under `LANE_ROOT` (default `/tmp/mmi_email_lanes/`).

---

## Verification (Cursor lane — R3)

```text
python -m pytest tests/test_client_email_lanes.py -q
# 13 passed (incl. other-fact unsigned injection falsifier)

python scripts/email_lanes_harness.py --authority C:/Architectapp_clean
# overall_gate_status: CLEAN
# CONFIRMATION_CHAIN includes matching-forgery + other-fact-forgery rejects
```

---

## Codex diff review request (R3 re-run)

Please re-review R3 fix against spec §4.6. Verdict: **CLEAN** or **NOT CLEAN** with blockers.

**Focus:** any invalid JSONL line (any fact_key/tenant) breaks `chain_ok`; valid chain still promotes VERIFIED for queried fact; falsifiers in harness + pytest.

**Pipe staging:** `client_email_lanes_gated=GATED`, `client_email_lanes_diff_review=CODEX_CLEAN`, `client_email_lanes_completion_gate=CLEAN`.

**CLOSED:** GATED 2026-07-03 — Codex R3 CLEAN. Closeout: `status/MMI_CLIENT_EMAIL_LANES_V1_CLOSEOUT_2026-07-03.md`.

---

## Copy-paste for Matt → Codex

> Client email lanes v1 R3 fix: `verify_confirmation_chain()` now cryptographically validates every ConfirmationEvent log line (not just matching tenant/fact), closing the unsigned other-fact injection falsifier that still returned VERIFIED under R2. Atomic append + expanded harness/pytest falsifiers. Harness CLEAN. Handoff: `lanes/CODEX_HANDOFF_CLIENT_EMAIL_LANES_DIFF_REVIEW_2026-07-03.md`. Verdict CLEAN or NOT CLEAN only.
