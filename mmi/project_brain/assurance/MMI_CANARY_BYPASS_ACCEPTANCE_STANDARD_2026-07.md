# MMI Canary Bypass Acceptance Standard

**Status:** HARD CONTROL — documentation only  
**Date:** 2026-07-04  
**Related:** RR-M4-003, §9 canary taxonomy, CANARY-026

**Forbidden claims:** canary coverage without bypass tests, "canaries prove detection."

---

## Rule

**A canary without a bypass test is not a canary.** It is an optimism sensor.

No canary ID is accepted in the M4 engine until this row is complete.

---

## Mandatory fields per canary ID

| Field | Meaning |
| ----- | ------- |
| Canary ID | e.g. M4-CANARY-011 |
| Expected trigger | Signal/condition that must trip |
| Telemetry dependency | What sensor/log must be live |
| Known bypass path | Documented way alert could be missed |
| Negative bypass test | Fixture proving bypass is detected or fail-closed |
| False-negative mode | What happens if canary fails to fire |
| False-positive cost | Operational impact of trip |
| Fail-closed action | HALT / SUSPEND / INDETERMINATE |
| Evidence artifact | Log/chain record on trip |
| Residual-risk entry | RR-* if bypass unproven |

---

## Acceptance gate

| Missing field | Verdict |
| ------------- | ------- |
| Known bypass path | REJECT or DOWNGRADE |
| Negative bypass test | REJECT |
| Fail-closed action undefined | REJECT |
| No residual-risk entry | REJECT (invalidation I-03) |

---

## §9 blind-spot table

M4 spec §9 blind-spot table is the seed list. This standard requires each ID to graduate from **defined** to **accepted** only when bypass tests exist.

**Current status:** Canaries not built (Phase 6). All canary acceptance rows **NOT_STARTED**.

**Not claimed:** canary coverage proven, runtime detection guaranteed.
