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
> Then continue from **Build List item 1** unless the operator overrides. Do not pre-decide §10 / §12 open questions on any spec without operator direction.

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

1. **Update `Frontier_Intake_Log.md` intake protocol.**
   Replace the "5-axis rubric sniff test" language with the new authority model:
   - Matt decides.
   - Intake classifies signals; it does not gate them.
   - `think_sheet.md` is a staging artifact, not authority.
   - No candidate auto-promotes from intake.
   Pre-authorized by `Compliance_and_Trend_Watch_Process.md` §1.1 (§11 signed 2026-05-26).

2. **Close `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` to signable v1.**
   Resolve its §12 minimum decisions:
   - cadence / stale threshold
   - delivery mechanism
   - per-carrier stance (variants vs. carrier-agnostic)
   - v1 artifact set
   - cheaper-proof go bar
   Other §12 questions may stay open past §11 if they aren't blocking the sign-off contract.

3. **Run cheaper-proof MSP discovery.**
   Use the Cyber Insurance Evidence Package framing to test whether MSPs actually want this evidence package before any implementation. The "cheaper-proof go bar" set by Build item 2 is the decision criterion.

4. **Only after cheaper-proof go: draft implementation spec.**
   Not code yet. Define generation workflow, artifact schema, redaction gates, and output surfaces. Spec-first discipline. §11 again.

5. **14-day Operating Doctrine Trial.**
   Spec drafted at `4. Product_Roadmap/Operating_Doctrine_14_Day_Trial.md` (DRAFT pre-§11). Operator signs §11 to activate. Trial runs **in parallel** with items 1–4, not after them — it evaluates whether the doctrine governing how items 1–4 are executed (queue-driven defaults, gate-enforced completion, rubric demotion, no AI-authored authority, TVL role) reduces micromanagement and drift over a fixed 14-day window. Retrospective at trial end produces one of four decisions: D1 keep / D2 tighten / D3 loosen / D4 rollback. The trial does not block any other queue item; it only governs the operating mode while the other items run.

**Operator focus call (not queue-ordered):** Matt selects the active spec lane when two items compete for attention — currently **Cyber Insurance §12 close-out** (Build item 2) vs **Callback Phishing / TOAD §10 stress-test** (pre-§11, not yet on this queue). Queue order still governs what is *authorized* to start; operator instruction governs what runs *now*.

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

3. **Before any implementation.**
   Audit must verify:
   - cheaper-proof gate was satisfied or explicitly overridden by Matt with a recorded reason
   - the relevant spec is §11-signed
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

**Build List item 1.** Update `Frontier_Intake_Log.md` intake protocol to replace the "5-axis rubric sniff test" language with the post-D6 authority model (Matt decides; intake classifies, does not gate; `think_sheet.md` is a staging artifact, not authority; no candidate auto-promotes from intake). Pre-authorized by `Compliance_and_Trend_Watch_Process.md` §1.1 (§11 signed 2026-05-26).

**Parallel operator focus (Matt's call, not queue-gated):** Cyber Insurance Evidence Package §12 close-out **or** Callback Phishing / TOAD §10 stress-test — see Build List operator-focus note.

Nothing in Build items 2–4 starts until item 1 closes unless Matt explicitly overrides.

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
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` — DRAFT pre-§11. Build List item 2 closes this.
- `4. Product_Roadmap/Operating_Doctrine_14_Day_Trial.md` — DRAFT pre-§11. Build List item 5 activates this. Audit List item 4 follows the trial.
- `Frontier_Intake_Log.md` — Build List item 1 targets the intake-protocol step in this file.
- `audit_tools/complete_gate.py` — enforces Audit List item 1 automatically when invoked at commit / ship / sign-off boundaries; also self-audits on any future change inside `audit_tools/` (v1.1 scope contract). Comment / source-of-truth alignment to `Compliance_and_Trend_Watch_Process.md` §5.1 / §5.5 was authored in the original 2026-05-26 sign-off commit (`470714d`); no separate reference-sync edit is outstanding.
- `MASTER_INDEX.md` — navigation. This file is indexed there under "Project Control Files."

---

**End of operational queue. No item below is authorized to start outside its listed order without an operator decision.**
