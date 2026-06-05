# NorthStar — Project Build and Audit Queue

**Status:** Operational queue artifact. Not a signed spec. Operator-maintained.
**Authority:** Matt is the operator. This file lists what comes next; it does not authorize anything by itself. Spec-first discipline still applies — items below that say "draft" or "sign" are gated by the relevant deep-dive's §11.
**Out of scope for this file:** scoring, implementation guidance, progress markers, completion claims. This file lives forward of the line; it does not record what shipped.

> **Default operating rule.**
> 1. Matt's current instruction overrides everything.
> 2. If no override, follow this queue in order.
> 3. Every "ready / done / sign / ship" claim requires audit evidence.

> **For the next assistant (handoff reading list).**
> Before doing work on this project, read in this order:
> 1. `PROJECT_BUILD_AND_AUDIT_QUEUE.md` (this file) — for ordering, default rule, and named next action.
> 2. `PROJECT_HANDSHAKE.md` — for current single active focus and runtime-build state.
> 3. `VISION.md` — for the seven non-negotiables that override all queue items.
> 4. `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` — §11 SIGNED 2026-05-26; canonical compliance-claim boundary (§5).
> 5. `audit_tools/complete_gate.py` — the gate that enforces the audit-evidence rule above.
>
> Then continue from **Build List item 1** unless the operator overrides. Do not pre-decide open questions on any spec without operator direction.

---

## §1 Purpose

One page. One source of truth for "what's the next move?" Two ordered lists:

1. **Build List** — what Cursor should build or draft next, in order.
2. **Audit List** — what Grok or `audit_tools/complete_gate.py` must audit before anything can be called ready / done / signed.

This file replaces the implicit recommendation pattern (suggestions buried in chat turns) with an explicit operator-readable queue. The next-action section names the single thing that should happen *now*.

This file is not a contract. The contracts are the signed §11 specs. This file is a workflow aid.

---

## §2 Build List

In execution order. Each item runs only when its predecessors are complete or explicitly skipped by the operator.

1. **Continue Cyber Insurance / Vendor Payment Integrity evidence-package build shaping after operator removal of the call-sheet blocker.**
   Operator override recorded 2026-06-02: the `Cyber_Insurance_Vendor_Payment_Integrity_Discovery_Call_Sheet.md` path is no longer the active build blocker and has been removed from the working tree. The project has enough research / Reddit / Todd / live-run / testing-footing signal to keep building the pre-spec evidence-package footing instead of cycling on the call sheet. This does **not** claim D10 is satisfied, does **not** authorize §13 sign-off, and does **not** edit the signed / pre-sign Cyber Insurance Evidence Package spec. It only changes the forward queue so the active build path is no longer stalled on that call-sheet workflow.

2. **Later: explicit operator decision on Cyber Insurance §13 readiness path.**
   Because the call-sheet/D10 path has been removed as the active blocker but D10 is not being claimed complete, any move toward §13 sign-off requires a separate operator decision and a fresh audit packet that states the basis clearly. Do not draft signature wording for Matt.

3. **Only after §13 is signed: draft implementation spec.**
   Not code yet. Define generation workflow, artifact schema, redaction gates, and output surfaces. Spec-first discipline. §11 again.

4. **14-day Operating Doctrine Trial.**
   Spec drafted at `4. Product_Roadmap/Operating_Doctrine_14_Day_Trial.md` (DRAFT pre-§11). Operator signs §11 to activate. Trial runs **in parallel** with items 1–3, not after them — it evaluates whether the doctrine governing how items 1–3 are executed (queue-driven defaults, gate-enforced completion, rubric demotion, no AI-authored authority, TVL role) reduces micromanagement and drift over a fixed 14-day window. Retrospective at trial end produces one of four decisions: D1 keep / D2 tighten / D3 loosen / D4 rollback. The trial does not block any other queue item; it only governs the operating mode while the other items run.

**Operator focus call (not queue-ordered):** Matt selects the active lane when items compete for attention. Current operator-selected focus is Cyber Insurance / Vendor Payment Integrity evidence-package build shaping after removal of the call-sheet blocker. Callback Phishing / TOAD pass 1 and pass 2 are already implemented and committed (`014a163`, `9bcb3d5`); TOAD pass 2 tracker baseline is committed at `c2ff29f`. Queue order still governs what is *authorized* to start; operator instruction governs what runs *now*.

---

## §3 Audit List

What must run cleanly before anything in §2 can be called done. Every "ready / done / signed" wording is gated by the relevant Audit item.

1. **Before signing the Cyber Insurance spec.**
   Grok audit packet should include:
   - `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md`
   - `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md`
   - `VISION.md`
   - source artifact map (the §4 evidence-source list in the cyber-insurance spec)
   - touched / read file manifest

2. **Before any tracker update that says "done."**
   Audit must verify:
   - fresh Grok output exists for the work being marked done
   - packet hash matches current touched files (no stale audit reuse)
   - no blocking deviations open
   - operator wording is Matt-authored (not AI-paraphrased completion claims)
   The `complete_gate.py` gate handles item 1 automatically when invoked; this item is operator-side discipline. Any change inside `audit_tools/` also fires a `complete_gate.py` self-audit (the v1.1 contract — `audit_tools/` is in gate scope from v1.1 onward, so editing the gate itself triggers an audit run).

3. **Before any Cyber Insurance implementation spec or implementation.**
   Audit must verify:
   - cheaper-proof gate was satisfied or explicitly overridden by Matt with a recorded reason
   - the Cyber Insurance Evidence Package spec is §13-signed
   - implementation scope matches the signed spec — no scope creep, no quiet additions
   - no claims surfaced anywhere in the implementation that fall outside the email-fraud / inbox-layer MDR boundary

4. **After the 14-day Operating Doctrine Trial.**
   Review (operator-led; Grok audit optional per the trial spec §10):
   - Queue accuracy — did `PROJECT_BUILD_AND_AUDIT_QUEUE.md` match what actually happened during the trial window
   - Whether gates helped or slowed — count gate firings, blocking findings, operator overrides, and any unjustified blocks
   - Whether Grok caught drift — list specific findings that altered work vs. findings ignored as noise
   - Whether Matt had to micromanage less — operator self-report against the prior comparable period
   - Whether build moved closer to revenue or signed specs — count §11 signatures landed, MSP discovery conversations logged, revenue-lane progress
   The trial spec §10 governs the audit packet and prompt for the optional retrospective Grok audit. Output of this audit informs (but does not decide) the §7 D1/D2/D3/D4 decision; the operator decides.

---

## §4 Next Action

**Current state 2026-06-03:** Cyber Insurance Evidence Package §13 is signed and committed (`85f2069`). The implementation spec is §11 signed and committed (`4308b22`). The §14 runner-first milestone passed live `grok-4` and tracker/intake commits landed (`908cb9b`, `e5a5caf`). Package-generator Pass 1 is now built locally: `core/evidence_package/` + `scripts/cyber_insurance_package_generate.py` produce a deterministic Markdown bundle from the §14 artifacts with all nine local §7 gates passing.

**Boundary:** D10 remains overridden, not met. Pass 1 is internal only: no PDF, no live Grok package audit, no done declaration, no operator package signature, no buyer-facing release, no pricing, no push.

**Committed 2026-06-04:** gate library `db32cd5` (fresh Grok gate clean), generator + CLI `ff0f41e` (via `complete_gate.py --operator-override`; Matt explicitly authorized generator Pass-1 start-build, internal scope; the §11-signed implementation spec is a no-code document, so the override path is the designed mechanism and a warning-level drift incident is recorded). Focused tests 16 passed. Doctrine/log/tracker docs committed alongside.

**Committed 2026-06-04 (later session):** generator stages 8 (audit-packet assembly, `ec91074`), 10 (done-declaration, `d75c3e7`), and 9 (Grok package audit — separate explicit injectable step, `264a340`) are built, gate-clean, and pushed off-site (github `7d4b3c1`+). An end-to-end pipeline integration test (`ab9846a`) proves stages 8->9->10 chain on a synthetic package. Criterion 14's operator package-signature mechanism is built (`a65babf`): it records Matt-authored wording as a `signed_by_operator` evidence record, but the actual signing remains operator authority. Rebrand decided via Consequence Matrix (Option B — external brand "Mutant Monkey Security" + domain now; internal codenames stay; deep rename deferred). Private test-data store spec drafted (pre-§11, `7cf4361`). Baseline 1122 passing, 1 skipped.

**Committed 2026-06-04 (PDF render surface):** IQ2 supply-chain decision resolved with the operator — concrete PDF engine pinned to **ReportLab 4.2.5** (pure-Python, no system binaries; smallest cross-platform supply-chain surface, the dimension IQ2 flagged). New `core/evidence_package/pdf_renderer.py` renders a deterministic (reportlab invariant) internal PDF per package with the boundary statement verbatim (HC8) and a `rendered/pdf_render.json` sidecar carrying the pinned engine identity+version (HC6) and pdf_sha256. It is a separate explicit step (not auto-wired into generation), synthetic/internal-only, **no buyer delivery**. Gate clean 0/0 (`cyber_insurance_pdf_render_surface_20260604T193751Z.md`). Baseline 1128 passing, 1 skipped.

**Committed 2026-06-05 (buyer-brand boundary revision):** The §2 package boundary statement and MSP retainer summary now use the external/commercial brand **Mutant Monkey Inbox Shield** / **Mutant Monkey Security** on buyer-facing package surfaces. The §13 deep-dive revision was re-signed with Matt's exact wording: "Approved by Matt Nichol, Sovereign Operator." Internal `NorthStar Inbox Shield` codename remains in place per rebrand Option B; no blanket rename. Full suite 1128 passing, 1 skipped; gate clean 0/0 (`cyber_insurance_buyer_brand_boundary_20260605T005903Z.md`); synthetic sample package re-rendered and visually inspected.

**Next concrete actions, in order:**
1. **Real-customer-data controls decision: DECIDED 2026-06-05 (Option B).** The Consequence Matrix ran (`_Real_Customer_Data_Controls_Consequence_Matrix.md`); operator chose **Option B** — real customer packages audited by operator-controlled local AI on a locked machine; Grok stays synthetic/test only until sunset; Private Test-Data Store stays test/lab forever. Next build action under B: draft the production / real-customer-data controls spec (pre-§11) so it can be gated and operator-signed. The decision does NOT by itself change §13/IQ3, authorize real-data handling, or open buyer delivery — those still need spec edit -> gate -> operator sign-off.
2. **Buyer PDF delivery (gated).** The renderer exists for internal/synthetic packages only. Actual buyer-facing PDF delivery is excluded by the standing Pass-1 authorization and stays an explicit operator decision (ties to item 1).
3. **Actual package-level operator signature (when a concrete package is ready).** The mechanism exists; Matt must review the rendered package and supply his own wording. No AI-authored sign-off text.
4. **Push remains an explicit operator instruction.** Pushing is never inferred; operator authorized today's pushes specifically.

---

## §5 Maintenance Rules

- **Owner.** Matt. Edits land via operator instruction or Cursor revision pass; no autonomous edits.
- **Canonical roles.** Queue is canonical for ordering. `PROJECT_HANDSHAKE.md` is canonical for current active focus. Matt's current instruction overrides both.
- **When to update.** Whenever (a) a Build or Audit item completes, (b) operator reorders or removes an item, (c) a new item is added by operator direction, or (d) a §11 signature changes what's blocking or unblocked. Updates are *removals and additions of queue items*, not historical log entries.
- **No history layer.** This file does not record what shipped. `PROJECT_ACTIVITY_LOG.md` and `PROGRESS.md` carry historical state. This file is forward-only.
- **No scoring.** Items are ordered by operator decision, not by rubric.
- **No progress marker.** Marking an item complete is done by removing it from the list, not by checkbox or status tag. A removed item is a completed-or-skipped item; the audit log records which.
- **Drift signal.** If this file goes stale (no edit in 14+ days while project work continues), that's an operator-discipline signal, not a tracker failure. The file is only useful if it's kept current.

---

## §6 Cross-references

- `PROJECT_HANDSHAKE.md` — current active build target (one item) and resume point. This file is the multi-item queue; `PROJECT_HANDSHAKE.md` is the single active focus.
- `PROGRESS.md` — historical task-tracker. This file is forward-only.
- `VISION.md` — seven non-negotiables that govern every item below.
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` — §11 SIGNED 2026-05-26. Canonical compliance-claim boundary (§5).
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` — DRAFT pre-§11. Build List item 1 closes this.
- `4. Product_Roadmap/Operating_Doctrine_14_Day_Trial.md` — DRAFT pre-§11. Build List item 4 activates this. Audit List item 4 follows the trial.
- `Frontier_Intake_Log.md` — intake protocol already carries the post-D6 authority model from `Compliance_and_Trend_Watch_Process.md` §1.1; the queue no longer carries a separate Frontier update item.
- `audit_tools/complete_gate.py` — enforces Audit List item 1 automatically when invoked at commit / ship / sign-off boundaries; also self-audits on any future change inside `audit_tools/` (v1.1 scope contract). Comment / source-of-truth alignment to `Compliance_and_Trend_Watch_Process.md` §5.1 / §5.5 was authored in the original 2026-05-26 sign-off commit (`470714d`); no separate reference-sync edit is outstanding.
- `MASTER_INDEX.md` — navigation. This file is indexed there under "Project Control Files."

---

**End of operational queue. No item below is authorized to start outside its listed order without an operator decision.**
