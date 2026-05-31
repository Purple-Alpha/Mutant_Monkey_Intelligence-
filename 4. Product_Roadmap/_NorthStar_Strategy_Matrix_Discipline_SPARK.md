# NorthStar Strategy Matrix Discipline — SPARK Capture

**Status:** SPARK ONLY. Pre-spec. Unsigned. Not §11. Not pricing approval. Not client-facing copy. Not a product sheet. Not a build authorization. Not a new required gate.
**Captured:** 2026-05-31 (immediately after the late-night chat run that produced a Pain Matrix, Revenue Matrix, Fear Matrix, Wedge Matrix, Competitive Moat Matrix, and a proposed Quarterly Trend Review).
**Architect:** Matt. The structure, scope, and direction of any future matrix discipline are Matt's to design.
**Purpose:** Preserve the *discipline conclusion* about which lightweight decision aids are worth adopting now and which are SPARK-only, without converting every chat-surfaced matrix into a permanent dashboard, scorecard, or build gate.

---

## What this SPARK is preserving

A bounded conclusion from the matrix-heavy chat exploration: most of the matrices were useful as *thinking tools* in the conversation but should not become permanent project artifacts. Only three lightweight decision aids are worth keeping live; the rest stay parked.

### Adopt now (lightweight)

1. **Pain Matrix.** Rank candidate features by *how much the customer cares*. Protects against feature creep. Used at the start of a candidate's evaluation, not as a decision authority.
2. **Revenue Matrix.** Rank candidate features by *ability to charge for it*. Protects against building unpaid "cool" features. Used alongside the Pain Matrix, not in place of it.
3. **Strategic Relevance Score.** Four-question 0-10 check (see §"Strategic Relevance Score" below) that protects the authenticated-deception mission from drift. Used after Pain + Revenue, before queue placement.

### Park as SPARK (do not adopt now)

- **Fear Matrix.** The customer-fear ranking from the chat is informative narrative; it is not a permanent project artifact in v1. Reason: fear-ranking duplicates the Pain Matrix at the buyer level without adding decision-useful information. Promote only if a discovery conversation surfaces a fear pattern the Pain Matrix misses.
- **Competitive Moat Matrix.** Useful for positioning conversations but not for build prioritization. Building a permanent moat scoreboard creates fake progress (re-scoring moats does not change the build). Promote only if a competitive event (e.g., Microsoft / Abnormal ships something that directly overlaps NorthStar's wedge) demands a fresh assessment.
- **Trust Layer Matrix.** The trust-layer thinking is already covered by `VISION.md` non-negotiables + existing signed specs. A separate matrix would duplicate that surface. Promote only if a specific decision needs a trust-layer scoring lens that the existing specs do not provide.

### Schedule, do not overbuild

- **Quarterly Trend Review.** Addresses the obsolescence risk that the chat surfaced (the threat / vendor / framework landscape moves faster than NorthStar ships) **without** daily pivoting. The existing `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` (§11 SIGNED 2026-05-26) already specifies a monthly Frontier Intake Review with a quarterly deep-review every third month. The Quarterly Trend Review noted in this SPARK is **not a new process** — it is a reminder that the existing quarterly deep-review under `Compliance_and_Trend_Watch_Process.md` §3 is the right home for this discipline. If a need arises later to widen the quarterly deep-review's scope beyond Frontier Intake (e.g., to include a wedge-vs-incumbent positioning check), that is a spec-amendment to `Compliance_and_Trend_Watch_Process.md`, not a separate new process.

---

## Why each adoption protects something specific

Plain explanations so the discipline conclusion survives even if the matrix labels later change:

- **Pain Matrix protects against feature creep.** Without a customer-pain check, the build queue fills with technically interesting features that no buyer cares about. The Pain Matrix is the first filter.
- **Revenue Matrix protects against unpaid "cool" features.** Even high-pain features can be hard to monetize. The Revenue Matrix is the second filter and prevents building things customers want but won't pay for.
- **Strategic Relevance Score protects the authenticated-deception mission.** Without a mission-fit check, NorthStar drifts into adjacent surfaces (VPN, endpoint, password manager, generic compliance) where it has no moat. The Strategic Relevance Score keeps the build inside the wedge.
- **Quarterly Trend Review addresses obsolescence risk without daily pivoting.** The existing Frontier Intake + quarterly deep-review cadence catches landscape shifts; daily re-scoring would just create noise.
- **Too many matrices create fake progress and slow the build.** Each matrix added is one more thing to maintain, one more place to drift, and one more surface that the operator might mistake for a decision authority. Three lightweight matrices is the upper bound for this stage; more is worse, not better.

---

## Strategic Relevance Score

Four 0-10 questions, scored independently. No weighted sum, no decision threshold. The scoreboard surfaces the shape of a candidate's fit; the operator decides what to do with it.

1. **Supports authenticated deception mission?** Does this feature help NorthStar detect, evidence, or explain a deception inside a relationship that the customer otherwise trusts (vendor, internal sender, signed authority)? 0 = no, 10 = directly central.
2. **Helps MSP sell value?** Is the feature something an MSP can show, demo, or invoice for, or is it invisible infrastructure that does not move the buying conversation? 0 = invisible, 10 = the headline of the next MSP sales call.
3. **Improves evidence quality?** Does the feature add to NorthStar's audit-trail / evidence-bundle / decision-transparency surface in a way an analyst, MSP, or third-party reviewer can consume? 0 = no evidence surface change, 10 = first-class evidence improvement.
4. **Improves trust / provability?** Does the feature make NorthStar easier to defend to a client, an insurance reviewer, or a regulator? 0 = no, 10 = directly removes a current "we can't prove that" gap.

### Worked examples (illustrative, not endorsements)

- **Vendor relationship baselines (already on the build path).** Mission = 10. MSP sell = 9. Evidence = 9. Trust = 9. → Keep. High strategic-relevance shape across all four axes; matches the wedge.
- **TOAD body-language detection (§11 SIGNED).** Mission = 9. MSP sell = 8. Evidence = 8. Trust = 8. → Keep. Already locked; relevance score consistent with the existing signed posture.
- **Evidence trail / monthly evidence digest.** Mission = 8. MSP sell = 10. Evidence = 10. Trust = 10. → Keep. Highest single concentration of MSP-facing differentiation.
- **VPN.** Mission = 1. MSP sell = 4. Evidence = 1. Trust = 2. → Parking lot. Low across the board; outside the wedge.
- **Generic malware detection.** Mission = 2. MSP sell = 4. Evidence = 2. Trust = 2. → Parking lot. Crowded competitor space; not differentiating.
- **Endpoint protection / password manager.** Mission = 1-2. MSP sell = 3-4. Evidence = 1-2. Trust = 1-2. → Parking lot. Adjacent-surface drift; not NorthStar's lane.

These illustrative numbers are **operator-discretionary**; they are not signed and not binding on any future build decision.

---

## Boundary

These matrices and the Strategic Relevance Score:

- **Do not decide.** They surface shape; Matt selects what runs.
- **Do not replace Matt's authority.** Per `AGENTS.md` §2, every promotion, commit, sign-off, and direction change is the operator's call.
- **Do not replace the Next-Action Decision Rubric.** `4. Product_Roadmap/Next_Action_Decision_Rubric_Deep_Dive.md` (pre-§11) is the tactical session-layer ranker. The matrices in this SPARK operate at the strategic / feature-candidate level, not at the session-action level. Two different lanes; they do not collide.
- **Do not create a new gate.** `audit_tools/complete_gate.py` and `audit_tools/pre_ship_audit.py` remain the only enforced gates. The matrices do not add a third.
- **Are advisory tools for business focus only.** Their output is a shape, not an authorization.
- **If a matrix conflicts with a signed spec, the signed spec wins.** No matrix score can supersede `VISION.md`, a §11-signed spec, or any of the seven non-negotiables.
- **If a matrix creates build friction, simplify or remove it.** Friction without decision value is drift. Discipline conclusion: prefer one fewer matrix to one more.

---

## What this SPARK is NOT

- **Not a product strategy.** Strategic intent at the product / brand level lives in `VISION.md` and the signed deep-dives, not in a matrix scoreboard.
- **Not pricing approval.** Pricing belongs in `REVENUE_MAP.md` / `THIRTY_DAY_PLAN.md` after real proof, not in a matrix.
- **Not client-facing copy.** No phrase in this SPARK is approved for landing pages, sales decks, or MSP pitch materials. Forbidden-language scope inherits from `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md`.
- **Not a permanent matrix specification.** The matrices named here are *adopted lightweight*. They may evolve, be simplified, or be retired without a spec-revision cycle, because they are advisory tools, not signed contracts. Promoting any of them to a signed §11 spec is a separate operator decision.
- **Not a competitive-moat declaration.** The Competitive Moat Matrix from the chat is parked here. The conclusion about NorthStar's moat shape (`Vendor Relationship Intelligence + Evidence Engine + Information Integrity`) is preserved in the companion SPARK at `4. Product_Roadmap/_NorthStar_Business_Positioning_SPARK.md` (when / if Matt authorizes that capture); it is not asserted as fact here.
- **Not a re-scoring of existing signed specs.** The Strategic Relevance Score's illustrative examples for TOAD / vendor baselines are *consistency checks*, not re-evaluations. A signed spec is locked; the score is a sanity probe, not a re-authorization.

---

## Failure modes this SPARK is parking

These are recorded so the next time the matrix-discipline conversation surfaces, the discussion does not need to re-discover them:

- **Matrix proliferation.** Every new matrix is a new surface to maintain, drift on, and confuse with a decision. The cap of three lightweight matrices is the discipline; more is the failure mode.
- **Decision laundering through matrix scores.** A high-scoring candidate is not an authorization; a low-scoring one is not a rejection. AGENTS.md §11 names this failure mode explicitly: rubrics rank, humans decide.
- **Fake progress through re-scoring.** Re-scoring the same matrix monthly without acting on the output produces the *feeling* of work without movement. The Quarterly Trend Review under `Compliance_and_Trend_Watch_Process.md` is the only scheduled scoring cadence; the three lightweight matrices are used ad-hoc when a real candidate appears.
- **Calibration drift.** Silently changing axis definitions or 0-10 anchors over time without an operator-signed amendment is the same failure mode as the rubric calibration drift named in `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`. If the Strategic Relevance Score's four questions change, the change is recorded — even though the SPARK itself is unsigned.
- **Adjacent-surface drift.** A high-pain feature outside the wedge (e.g., a VPN that scores 10 on a hypothetical "everyone wants one" pain axis) is still parking-lot. The Strategic Relevance Score's mission-fit axis is the brake.
- **Free-work perception.** A matrix that ranks a parked feature highly does not commit NorthStar to building it. AGENTS.md §11 names this. No matrix output is a commitment.
- **Sycophancy / praise-stacking around matrix conclusions.** A matrix output that flatters the existing build queue ("everything we are doing is high-scoring") is more likely a sign that the matrix is being applied with confirmation bias than a sign that the queue is right. The matrices are most useful when they surface something uncomfortable.

---

## Trigger conditions for un-deferring the parked matrices

The three parked matrices (Fear Matrix, Competitive Moat Matrix, Trust Layer Matrix) stay parked unless **at least one** of the following is true for that specific matrix:

1. **Fear Matrix.** A real MSP / SMB discovery conversation surfaces a customer fear that the Pain Matrix did not flag, AND the gap is not closeable by adding a new Pain Matrix candidate. Un-deferring would then add the Fear Matrix as a second-layer filter, not as a replacement.
2. **Competitive Moat Matrix.** An incumbent (Microsoft, Abnormal, Mimecast, Proofpoint, KnowBe4, Barracuda) ships a feature that directly overlaps NorthStar's wedge (vendor relationship intelligence, evidence-package generation, authenticated deception detection), AND that ship event materially changes positioning. Promoting the matrix at that point would be a one-shot competitive response, not a permanent scoreboard.
3. **Trust Layer Matrix.** A specific decision arises that needs a trust-layer scoring lens which the existing `VISION.md` non-negotiables + signed specs do not provide. The matrix would then be drafted scoped to that decision only.

None of these triggers auto-promotes any matrix. The trigger only authorizes an operator-led drafting pass.

---

## What this SPARK deliberately does NOT include

(Mirroring the `_Cross_Channel_Fraud_Shield_Concept_Capture.md` and `_SPARK_Bibles_Concept_Capture.md` pattern.)

- No fully-populated example of any matrix. The three lightweight matrices are *defined* here, not *filled in*. Filling them in for the current build queue is operator work, not SPARK content.
- No dashboard / UI / portal mockup. The matrices are paper-and-judgment tools, not surfaces with a frontend.
- No commitment to apply the Strategic Relevance Score retroactively to already-signed specs. Existing signed specs are locked by their §11 signature; the score is for *future candidates*, not for re-litigating closed decisions.
- No spec-version policy for the matrices. Because the matrices are advisory, not signed, they do not carry an Dn-decision list, a §11 placeholder, or a revision cycle. If they outgrow that posture they convert into a real deep-dive with the normal pre-§11 template.
- No automation hook. The matrices do not feed `audit_tools/complete_gate.py`, `audit_tools/pre_ship_audit.py`, `audit_tools/decision_audit_runner.py`, or any other runtime / audit surface. They are operator-side judgment aids only.
- No buyer-segment / pricing matrix. Buyer segmentation and pricing belong in `REVENUE_MAP.md` / `THIRTY_DAY_PLAN.md` after real proof; they are not a matrix this SPARK adopts.

---

## Why this file exists at all

A long late-night chat run produced six different matrices in rapid succession (Pain, Revenue, Strategic Relevance, Fear, Competitive Moat, Trust Layer) plus a proposed Quarterly Trend Review. The operator's discipline conclusion — adopt three lightweight aids, park three as SPARK, do not invent a new process where `Compliance_and_Trend_Watch_Process.md` already covers the cadence — needs to survive past the chat session. This SPARK is that survival layer.

It is intentionally **not** a matrix-specification deep-dive. Writing a full §11-signed "Strategic Matrix Discipline" spec would itself be the failure mode this SPARK is warning against: it would convert a *judgment aid* into a *signed contract*, and then the matrices would have to be maintained, audited, and gated like any other locked surface. That is exactly the "too many matrices create fake progress" failure mode named above.

If the lightweight matrices outgrow their advisory posture — for example, if the operator finds them so useful that they want gate-enforced application before any new feature enters the build queue — then a real deep-dive is the right next step, with the normal pre-§11 / §11 / gated-implementation lifecycle. Until that growth happens, this SPARK is the holding pattern.

---

## Cross-references (raw material, not endorsements)

- `AGENTS.md` — §2 authority model (Matt decides; rubrics rank), §11 named failure modes (authority drift, decision laundering, calibration drift, free-work perception).
- `VISION.md` — seven non-negotiables; the strategic frame any matrix must live inside.
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` — §11 SIGNED 2026-05-26. The existing home of the quarterly deep-review cadence referenced above. Any widening of that cadence belongs here, not in a new process.
- `4. Product_Roadmap/Next_Action_Decision_Rubric_Deep_Dive.md` — pre-§11. Tactical / session-layer ranker; distinct lane from the strategic / feature-candidate matrices in this SPARK.
- `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` — §11 SIGNED 2026-05-25 + §11.1 + §11.2 amendments. The buyer-facing 5-axis rubric; the naming-collision reason the matrices in this SPARK deliberately do not use the "5-axis" label.
- `4. Product_Roadmap/Consequence_Matrix_Process.md` — pre-§11. Operator-triggered process for path-setting decisions; the right tool to run *before* deciding to promote any parked matrix.
- `4. Product_Roadmap/_SPARK_Bibles_Concept_Capture.md` and `4. Product_Roadmap/_Cross_Channel_Fraud_Shield_Concept_Capture.md` — the precedent SPARK files for "park a big idea without pretending it is a product."
- `REVENUE_MAP.md` / `THIRTY_DAY_PLAN.md` — where pricing / revenue lanes live, not here.
- `PROJECT_BUILD_AND_AUDIT_QUEUE.md` — current operational queue. Matrices in this SPARK do not edit the queue; the queue is operator-maintained.

---

## Tomorrow's actual first move (Matt's call to accept or reject)

The tomorrow path remains whatever is at the top of `PROJECT_HANDSHAKE.md` / `PROGRESS.md` / `PROJECT_BUILD_AND_AUDIT_QUEUE.md`. This SPARK does not move the queue, does not authorize a new gate, does not promote any feature, and does not retroactively re-score any signed spec. It only ensures the matrix-discipline conclusion (adopt three lightweight aids; park three; lean on the existing trend-watch process for cadence) survives the chat session so the next time matrices come up, this file is the holding pattern.
