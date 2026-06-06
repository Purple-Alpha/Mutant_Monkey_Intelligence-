# Blue-Team Swarm Architecture Map — SPARK

**Status:** SPARK / vision capture. Pre-spec, unsigned, NOT §11, authority-free. Authored 2026-06-05 by Cursor capturing Matt Nichol's operator vision verbatim (preserved in §D below) plus an agent-added cross-map and boundary layer. **This file builds nothing, authorizes nothing, and expands no signed scope.** It does not override `AGENTS.md`, the seven `VISION.md` non-negotiables, or any signed spec. It is a map to draw milestones from, not a build order.

**Operator adoption (2026-06-05):** Matt adopted this as the original Stage B/C architecture inventory/backlog map (per `DECISION_PROTOCOL.md` §4). **Superseded as the canonical design source on 2026-06-06** by `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`, after Matt confirmed the cleaner 6-layer "agentic evidence swarm" fit. This file remains preserved as the 70-agent inventory/cross-map. **Adoption is not build authorization** — every agent here still runs the normal Next-Action Rubric -> spec-first -> gate -> operator sign-off path one at a time. Lives in the `agent_concepts/` design-dump folder.

**Brand note:** buyer-facing surfaces use **Mutant Monkey**; "NorthStar" / "SwarmCommand" remain internal codenames per the rebrand Option B decision. The operator vision below uses "NorthStar" as the internal codename; no rename is implied.

---

## §A What this is

A 70-agent blue-team swarm architecture for email fraud, phishing, ransomware precursors, vendor-payment deception, and cyber-insurance evidence. It is the detailed articulation of `VISION.md` Stage B (auto-defend obvious / escalate ambiguous) and Stage C (self-evolving defense swarm). It is captured here so it is not lost and so daily milestones can be drawn from it one at a time.

**Operating loop (operator):** Observe -> Detect -> Compare -> Verify -> Escalate -> Document -> Explain -> Test -> Learn.
**Product loop:** Detection -> Verification -> Evidence -> Outcome -> Retest.
**Trust promise:** NorthStar does not just flag risk; it builds the evidence record behind the decision.
**Central principle:** No trust decision without evidence. No high-risk action without verification. No failure without a learning record.

---

## §B Butterfly / boundary flags (agent-added, honest)

1. **This is a butterfly / path-setting artifact.** Promoting any agent here into an actual build is a Stage B/C scope + architecture decision. Each promotion runs the normal path: Next-Action Decision Rubric to pick it as a milestone, spec-first deep-dive, `complete_gate.py`, operator sign-off. The Consequence Matrix is available for any promotion that sets architecture, autonomy, revenue, or insurance posture.
2. **Stage discipline holds.** `VISION.md` Stage A is analyze + recommend only. Several agents here (Containment #38, Dual-Approval #19, any auto-action) describe Stage B/C autonomy that the seven non-negotiables gate: kill switch wins, every autonomous action audited + reversible, operator approval for client-facing actions. No agent here authorizes autonomous action; that remains gated.
3. **Insurance-named agents stay inside the carve-outs.** #54-#60 (Cyber Insurance Evidence, Control Mapping, Renewal Readiness, Underwriter Summary, Claim Support, Exception Tracking, Evidence Freshness) must obey `Compliance_and_Trend_Watch_Process.md` §5: no "compliant," "certified," "insurer-approved," or guaranteed-outcome claims. The vision already encodes this discipline (Decision Integrity #5, Safe Language #53) — keep it.
4. **Synthetic-only until controls clear.** Any agent that would touch real customer data inherits the §11-signed Real-Customer-Data Controls contract (local-AI audit, no external egress, separate production store, §13/IQ3 revision precondition). No agent here is a backdoor around that.
5. **Scope-vs-reality.** Current execution reality is Stage A, email-fraud / inbox-layer, synthetic-only. This is a multi-year map. "Build it" means feed it in one milestone at a time, not all 70 at once.

---

## §C Cross-map: what already exists vs net-new

Tags: [EXISTS] real code in the runtime; [SPECCED] signed or drafted spec, not all built; [GOVERNANCE] covered by VISION/AGENTS/gate; [NET-NEW] no current surface.

**Team 1 — Swarm command layer**
- #1 Swarm Commander [NET-NEW] (the orchestration heart; Stage B/C)
- #2 Mission Context [NET-NEW]
- #3 Risk Triage [EXISTS] email_risk_scoring + Tiered Detection Intensity (signed)
- #4 Human-in-the-Loop [GOVERNANCE] VISION non-negotiables 6/7
- #5 Decision Integrity [GOVERNANCE/SPECCED] AGENTS authority model + Client-Facing 5-Axis Rubric contradiction guard

**Team 2 — Email identity / sender**
- #6 Header Analysis [EXISTS] header_divergence_detector
- #7 Sender Identity [EXISTS/partial] scoring agent
- #8 Reply-To Mismatch [EXISTS/partial]
- #9 Domain Reputation [NET-NEW]
- #10 Lookalike Domain [SPECCED/partial] discussed in think_sheet
- #11 Known-Good Contact [EXISTS] Vendor Baseline Store (signed)
- #12 Compromised Mailbox Suspicion [NET-NEW]

**Team 3 — Vendor-payment / BEC**
- #13 Vendor Relationship Intelligence [EXISTS] Vendor Baseline Store
- #14 Payment Change Detection [EXISTS] Financial State Ledger / Delta Tripwire (signed)
- #15 Invoice Fraud [SPECCED/partial]
- #16 Bank Detail Drift [EXISTS] Financial State Ledger + Vendor Baseline
- #17 Vendor Master Record [EXISTS] Vendor Baseline Store
- #18 Callback Verification [EXISTS/partial] Callback Phishing/TOAD (signed) + Vendor Payment Verification Workflow (draft)
- #19 Dual-Approval [SPECCED/partial] Vendor Payment Verification Workflow (draft)
- #20 Financial Exposure [EXISTS/partial] Financial State Ledger
- #21 Executive Impersonation [NET-NEW/partial]
- #22 Payroll Diversion [NET-NEW]

**Team 4 — Phishing / credential**
- #23 Credential Phishing [NET-NEW/partial]
- #24 MFA Manipulation [NET-NEW]
- #25 Session Theft [NET-NEW/partial] prompt_injection_detector adjacent
- #26 QR Phishing [NET-NEW] (flagged in Frontier Intake)
- #27 Link Inspection [NET-NEW/partial]
- #28 Brand Impersonation [NET-NEW]
- #29 Form Abuse [NET-NEW]

**Team 5 — Attachment / ransomware precursor**
- #30 Attachment Risk [EXISTS/partial] attachment scoring
- #31 PDF Fingerprint [SPECCED] document metadata fingerprinting (think_sheet promote)
- #32 Macro/Script Risk [NET-NEW]
- #33 Payload Delivery [NET-NEW]
- #34 Remote Access Abuse [NET-NEW]
- #35 Inbox Rule Abuse [NET-NEW]
- #36 Account Takeover [NET-NEW]
- #37 Ransomware Precursor [NET-NEW] (overlay exists conceptually in VISION)
- #38 Containment Recommendation [NET-NEW] (Stage B; non-negotiable-gated)

**Team 6 — Language / behavior / deception**
- #39 Language Pressure [EXISTS] Callback Phishing/TOAD detector
- #40 Tone Drift [NET-NEW]
- #41 Behavioral Baseline [NET-NEW/partial]
- #42 Timing Anomaly [NET-NEW]
- #43 Geo-Context [SPECCED] Sender Provenance / Geo-Velocity proof protocol
- #44 Social Engineering [EXISTS/partial] TOAD vocabulary
- #45 Process Bypass [NET-NEW]

**Team 7 — Evidence / audit**
- #46 Evidence Package [EXISTS] Cyber Insurance Evidence Package generator
- #47 Case Timeline [EXISTS/partial] Reaction Timing Log + audit_trail
- #48 Verification Outcome [SPECCED] Vendor Payment Verification Workflow (draft)
- #49 Audit Trail [EXISTS] Blackboard + package audit_trail
- #50 Evidence Strength [SPECCED/partial] Email Security Testing framework
- #51 Assumption Control [GOVERNANCE/partial]
- #52 Plain-English Explanation [EXISTS] Client-Facing 5-Axis Rubric (signed)
- #53 Safe Language [GOVERNANCE] Compliance_and_Trend_Watch_Process (signed)

**Team 8 — Cyber insurance**
- #54 Cyber Insurance Evidence [EXISTS] Cyber Insurance Evidence Package (signed)
- #55 Control Mapping [SPECCED/partial]
- #56 Renewal Readiness [SPECCED/partial]
- #57 Underwriter Summary [SPECCED/partial]
- #58 Claim Support [NET-NEW]
- #59 Exception Tracking [NET-NEW]
- #60 Evidence Freshness [SPECCED] freshness policy in Cyber Insurance spec §6.1

**Team 9 — Learning / testing**
- #61 Test Case Generator [SPECCED] Email Security Testing framework (draft)
- #62 Regression Test [EXISTS] pytest suite + cadence gate
- #63 Adversarial Test [EXISTS/partial] break-it tests
- #64 Failure Classification [SPECCED] Email Security Testing failure cards
- #65 Correction Evidence [GOVERNANCE] CURRENT_STATE_MAP FP/FN correction loop
- #66 Drift Watch [GOVERNANCE] Compliance and Trend Watch Process (signed)
- #67 Rule Improvement [NET-NEW]
- #68 Swarm Memory [NET-NEW]

**Team 10 — Review / decision integrity**
- #69 Swarm Health [NET-NEW]
- #70 Final Review [GOVERNANCE/partial] complete_gate.py + package auditor

**Rough tally:** a meaningful share (~30-40 of 70) already have an EXISTS / SPECCED / GOVERNANCE surface; the clear NET-NEW cluster is the orchestration layer (#1, #2, #68, #69) and several Stage-B detectors (phishing/credential team, ransomware-precursor team).

---

## §D Operator vision (verbatim — Matt Nichol, 2026-06-05)

> NorthStar is an evolving blue-team AI swarm for email fraud, phishing, ransomware precursors, vendor-payment deception, and cyber-insurance evidence. The swarm watches for the "perfect storm": a real-looking email from a trusted person/vendor/executive where technical signals look clean but the request, behavior, timing, payment detail, attachment, or verification path has changed. NorthStar's job is not just "safe" or "dangerous" — it is: detect the drift, verify the facts, escalate the risk, document the evidence, create an audit-ready outcome, learn from every case.

The full ten-team / 70-agent breakdown as authored by the operator:

1. **Swarm command layer:** (1) Swarm Commander — controls workflow, assigns specialists, prevents duplicate work, builds final case, routes to humans. (2) Mission Context — determines case type and required evidence. (3) Risk Triage — first risk classification + danger signals. (4) Human-in-the-Loop — decides when human review is required; prevents silent automation. (5) Decision Integrity — prevents overclaim, separates facts from assumptions, forces cautious wording.
2. **Email identity / sender:** (6) Header Analysis (SPF/DKIM/DMARC/return-path/reply-to). (7) Sender Identity (display-name deception, mismatch). (8) Reply-To Mismatch (hidden redirection). (9) Domain Reputation (new/suspicious domains). (10) Lookalike Domain (typosquat/homoglyph). (11) Known-Good Contact (vendor master/CRM/historical for out-of-band). (12) Compromised Mailbox Suspicion (real but compromised sender).
3. **Vendor-payment / BEC:** (13) Vendor Relationship Intelligence (normal-behavior pattern + drift). (14) Payment Change Detection (new bank/routing/wire/portal). (15) Invoice Fraud (format/amount/timing/numbering). (16) Bank Detail Drift (vs historical). (17) Vendor Master Record (unauthorized changes; require known-good confirm). (18) Callback Verification (known-good channel; block in-email numbers/links; record call). (19) Dual-Approval (second-person approval). (20) Financial Exposure (estimate amount; prioritize). (21) Executive Impersonation (CEO/CFO urgency/secrecy). (22) Payroll Diversion (direct-deposit change scams).
4. **Phishing / credential:** (23) Credential Phishing (fake login/reset; M365/Google/DocuSign/Dropbox/bank/payroll). (24) MFA Manipulation (approve-prompt/share-code/fatigue). (25) Session Theft (token/OAuth abuse). (26) QR Phishing. (27) Link Inspection (redirects/shorteners/mismatch). (28) Brand Impersonation. (29) Form Abuse.
5. **Attachment / ransomware precursor:** (30) Attachment Risk. (31) PDF Fingerprint (producer metadata). (32) Macro/Script Risk. (33) Payload Delivery. (34) Remote Access Abuse. (35) Inbox Rule Abuse (forwarding/hidden rules). (36) Account Takeover. (37) Ransomware Precursor (connects signals into one risk view). (38) Containment Recommendation (hold payment, verify, reset, isolate, escalate, preserve evidence).
6. **Language / behavior / deception:** (39) Language Pressure (urgency/secrecy/fear/authority). (40) Tone Drift (vs known-good). (41) Behavioral Baseline. (42) Timing Anomaly (after-hours/holiday/region). (43) Geo-Context (impossible travel/location drift). (44) Social Engineering. (45) Process Bypass (skip approval/callback/ticketing).
7. **Evidence / audit:** (46) Evidence Package. (47) Case Timeline. (48) Verification Outcome (confirmed legit/fraud/not-verified/follow-up/override/exception). (49) Audit Trail. (50) Evidence Strength. (51) Assumption Control (facts vs assumptions vs memories). (52) Plain-English Explanation (no chain-of-thought). (53) Safe Language (no "prevented fraud/guaranteed/compliant/insurer-approved/certified" unless proven).
8. **Cyber insurance:** (54) Cyber Insurance Evidence (proof of operation). (55) Control Mapping (MFA/vendor-verify/dual-approval/training/IR/backup/endpoint/access). (56) Renewal Readiness. (57) Underwriter Summary (cautious, evidence-backed). (58) Claim Support (incident timelines/verification/containment/decision history). (59) Exception Tracking (gaps/partial controls/overrides visible). (60) Evidence Freshness (current vs historical).
9. **Learning / testing:** (61) Test Case Generator. (62) Regression Test. (63) Adversarial Test (no real malware). (64) Failure Classification. (65) Correction Evidence (link to failed tests; retest before complete). (66) Drift Watch (new attacker behavior). (67) Rule Improvement (scoped/testable). (68) Swarm Memory (prior cases/trusted relationships/exceptions; separate from verified facts). (69) Swarm Health (agent consistency/conflict). (70) Final Review (verdict+evidence+explanation+action match; final decision record).

Ten defensive teams: command layer; email identity/sender; vendor-payment/BEC; phishing/credential; attachment/ransomware precursor; language/behavior/deception; evidence/audit; cyber-insurance documentation; testing/improvement; final review/decision integrity.

---

## §E How this feeds milestones (the on-track mechanism)

This map is a **backlog source**, per `DECISION_PROTOCOL.md` §4. Daily milestone-setting draws candidate agents from §C, preferring: (a) [SPECCED] items already close to buildable, (b) agents that produce buyer/audit evidence (the moat), (c) low net-new-surface items that strengthen Stage A before Stage B autonomy. Each promotion is its own spec-first, gated, signed slice. No agent is "in the build" until it goes through that path.
