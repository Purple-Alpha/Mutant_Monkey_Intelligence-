# NorthStar + SwarmCommand — Current State Map

**Purpose:** Operator-authored compressed snapshot of doctrines and open gaps that already exist as designed concepts across multiple specs but are not captured anywhere as a single one-line reference. Prevents future sessions from re-litigating settled design or rediscovering known gaps by re-assembling them from five scattered specs.

**Status:** Pre-spec, unsigned, not §11. Floor reference, not floor doctrine. Adds entries over time; never replaces the underlying specs. If an entry here ever conflicts with a §11-SIGNED spec, the signed spec wins.

**Edit rule:** Each entry is operator-authored prose, captured verbatim. Cross-references point to the actual anchor artifacts. Entries do not introduce new D-decisions, new requirements, or new gates.

**Authored 2026-05-31 by Matt Nichol.**

---

## Alert-fatigue doctrine

> **Alert-fatigue doctrine:** NorthStar reduces operator fatigue by batching risk into daily digests, tiering detection intensity by tenant plan/posture, escalating only on conservative high-signal triggers, explaining findings through action-first evidence, and allowing per-tenant tuning. Stage A is decision-support and evidence, not a per-email alert stream.

**Anchor artifacts (the five surfaces this doctrine lives across):**

- **Batch** — `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/drafting/daily_digest_agent.py` + `DAILY_DIGEST_SYSTEM_PROMPT`; one ranked summary per `(tenant_id, digest_date)`, idempotent; Plus tier and above per `1. Business_Operations/Client_Documents/MSP_Discovery_Evidence_Package.md` §tier matrix.
- **Tier** — `4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md`; Low / Medium / High mapped to Essentials / Plus / Enterprise; lift-only invariant pinned by gate tests #9 / #15 / #24.
- **Escalate rarely** — Tiered Detection Intensity §risks table (forced-escalation thresholds: LLM ≥ 80, header divergence ≥ 80, ghost thread > 0, manual; deliberately conservative; tunable only by re-spec). Plus `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` and the Vendor Baseline Store: "recommend review, not block" pattern so legitimate vendor changes don't fire blocking alarms.
- **Explain clearly** — `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` §11.1 / §11.2; `recommended_action` most prominent (D16), `Rubric: <axis_total>/10`, all five axes with `why_this_score` and the fixed-order disclaimer. Plus the per-tenant evidence package and the `Inbox_Shield_Daily_Digest_Demo.md` sample.
- **Tune per tenant** — per-tenant override CLI + effective-parameter report + per-tenant `production_state/{tenant_id}/vendor_baseline.sqlite`. Operator-tunable keys restricted to `fraud_risk_floor_lift` / `attachment_risk_floor_lift` / `url_obfuscation_floor_lift` per the MSP package tier rules.

**Stage A framing:** `VISION.md` lines 36-44 — Stage A is analyze-only; ships daily decision-support + evidence package, not a per-event alert stream.

---

## Open gap — verification workflow ergonomics for vendor-payment changes

> **Still open:** verification workflow ergonomics for vendor-payment changes: verified / unresolved / false-positive / follow-up-needed, with evidence and retest linkage.

Closest existing surfaces this would touch when the operator chooses to spec it:

- `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` — the detector that surfaces vendor-payment changes for review.
- `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` §7.3 verdict-match + §9.4 failure-card schema — retest-linkage pattern.
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` §14 Stage A test plan — operator-side workflow ergonomics already framed for the cyber-insurance evidence surface; would extend naturally.
- `REACTION_TIMING_TEST_LOG.md` — closed verdict enum (`pass` / `partial` / `fail` / `blocked`) which the new four-value verification enum (`verified` / `unresolved` / `false-positive` / `follow-up-needed`) would echo in spirit, not replicate verbatim.

This is operator-acknowledged open work; not on any current build queue.

---

**End of current state map. New entries appended only on explicit operator capture; never auto-promoted from the assistant.**
