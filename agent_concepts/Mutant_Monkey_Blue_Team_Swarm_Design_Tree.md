# Mutant Monkey Blue-Team Swarm — Design Tree (v2, governed)

**Status:** ADOPTED CANONICAL DESIGN MAP (2026-06-06 operator decision). Pre-spec, unsigned, NOT §11, authority-free. Captured 2026-06-05 by Cursor from Matt Nichol's operator design (preserved verbatim in §A below), then promoted on 2026-06-06 when Matt confirmed the cleaner 6-layer articulation "fits" and "everyone agrees with this fit." **Builds nothing, authorizes nothing, expands no signed scope.** Does not override `AGENTS.md`, the seven `VISION.md` non-negotiables, or any signed spec.

**Relationship to v1:** this supersedes `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` as the canonical agent-design map and milestone-shaping source. The v1 70-agent map remains preserved as the original operator-adopted inventory/backlog cross-map; this file is now the governing design articulation for how agents should be shaped before promotion: command structure, Rules of Engagement, authority levels, reputation, two-pass decision model, client-safe decision evidence record, conflict resolution, and the V1 starting swarm.

**Brand / claim note:** "Mutant Monkey" is the buyer brand. The agent names, positioning lines (#13), and slogans below are **internal design labels, not approved buyer-facing copy or claims**. Any buyer-heard wording (especially anything touching cyber-insurance) must still pass the claim boundary in `Compliance_and_Trend_Watch_Process.md` §5 before use — no "compliant / certified / insurer-approved / guaranteed / proof-of-coverage" claims in buyer voice.

**Promotion path:** nothing here is in the build until it goes Next-Action Rubric -> spec-first deep-dive -> `complete_gate.py` -> operator sign-off, one agent/slice at a time (the V1 14-agent list in §A.10 is the natural draw order).

---

## §0 Canonical fit decision (operator-confirmed 2026-06-06)

Matt confirmed this cleaned articulation as the right fit for Mutant Monkey Security:

> **Mutant Monkey Security is not just an email scanner. It is a governed defensive swarm. Each agent has a role, a boundary, evidence requirements, failure modes, promotion conditions, demotion conditions, and a signed record of why it was trusted.**

Canonical internal positioning:

> **Mutant Monkey Security is an agentic evidence swarm that detects trusted-relationship drift, verifies suspicious payment or access events, and produces audit-ready evidence for operator review before money moves or risk escalates.**

Buyer-facing wording must still pass `Compliance_and_Trend_Watch_Process.md` §5 before use; "before money moves" is an internal design target, not a guaranteed buyer claim.

### Canonical six-layer swarm map

```text
Mutant Monkey Security Swarm
|
|-- 1. Command Layer
|   |-- Swarm Commander Agent
|   |-- Mission Context Agent
|   |-- Risk Triage Agent
|   |-- Human-in-the-Loop Agent
|   `-- Decision Integrity Agent
|
|-- 2. Detection Layer
|   |-- Header Analysis Agent
|   |-- Sender Provenance Agent
|   |-- Vendor Relationship Agent
|   |-- Payment Change Agent
|   |-- Executive Impersonation Agent
|   |-- Language Pressure Agent
|   |-- Attachment Risk Agent
|   `-- Link Inspection Agent
|
|-- 3. Verification Layer
|   |-- Known-Good Callback Agent
|   |-- Geo/Origin Check Agent
|   |-- Two-Step Verification Agent
|   |-- Vendor Baseline Agent
|   `-- Human Approval Agent
|
|-- 4. Evidence Layer
|   |-- Evidence Package Agent
|   |-- Case Timeline Agent
|   |-- Verification Outcome Ledger Agent
|   |-- Control Mapping Agent
|   `-- Underwriter Summary Agent
|
|-- 5. Challenge / Red-Team Layer
|   |-- Adversarial Test Agent
|   |-- Regression Test Agent
|   |-- Failure Classification Agent
|   |-- Retest Evidence Agent
|   `-- Drift Watch Agent
|
`-- 6. Learning / Governance Layer
    |-- Promotion Agent
    |-- Demotion Agent
    |-- Signed Policy Agent
    |-- Rollback Agent
    |-- Independent Decision Auditor
    `-- Swarm Memory / Agent Bible Agent
```

### Governing rules

```text
No trust decision without evidence.
No high-risk action without verification.
No failure without a learning record.
The detector is not the decision.
The detector is the trigger for verification.
```

### Stage path

```text
Stage A -- Analyze and recommend only.
Stage B -- Auto-defend obvious cases, escalate ambiguous cases.
Stage C -- Self-evolving defense swarm with signed promotions, demotions, tests, rollback, and audit trails.
```

### Design consequence

Every future promoted agent should declare its layer, role, authority level, boundary, evidence requirements, failure modes, promotion conditions, demotion conditions, two-pass role, and decision-evidence-record contribution before build authorization. Existing promoted detectors (#10 Lookalike Domain and #21 Executive Impersonation) should receive a later light retrofit to add those fields without changing their signed detection contracts.

---

## §A Operator design (verbatim — Matt Nichol, 2026-06-05)

# Mutant Monkey Security — Evolving Blue-Team Swarm Design Tree

## Core identity

**Mutant Monkey Security** is an evolving blue-team AI swarm for email fraud, phishing, ransomware precursor detection, vendor-payment deception, and cyber-insurance evidence.

The system is not just a collection of AI agents. It is a governed defensive decision system where agents detect risk, challenge each other, produce evidence, and improve over time.

## Core promise

**Mutant Monkey Security does not just flag risk. It builds the evidence record behind the decision.**

## Core operating loop

**Observe -> Compare -> Classify -> Verify -> Document -> Learn**

## Product loop

**Detection -> Verification -> Evidence -> Outcome -> Retest**

## Trust rule

**Agents do not earn trust by sounding confident. Agents earn trust by producing accurate, evidence-backed, retestable decisions.**

---

# 1. Mutant Monkey Swarm Command

This is the management layer for the swarm.

## 1.1 Swarm Commander Agent

Role: Controls the full case workflow.

Responsibilities:

* Receives suspicious email events.
* Determines which teams should review the case.
* Assigns specialist agents.
* Prevents duplicate work.
* Routes cases to human review when needed.
* Prepares the final case package.

Output:

* Case status.
* Assigned agents.
* Review path.
* Final decision package.

## 1.2 Mission Context Agent

Role: Identifies what kind of case this is.

Responsibilities:

* Classifies the case as phishing, vendor-payment fraud, ransomware precursor, executive impersonation, payroll diversion, invoice fraud, business email compromise, or cyber-insurance evidence.
* Determines the required review depth.
* Selects the required evidence list.

Output:

* Case type.
* Review scope.
* Required evidence.

## 1.3 Severity Commander Agent

Role: Determines how serious the case is.

Responsibilities:

* Checks whether money is at risk.
* Checks whether credentials are at risk.
* Checks whether ransomware exposure is possible.
* Checks whether business continuity could be affected.
* Checks whether human review is required.

Output:

* Severity level.
* Business exposure.
* Escalation recommendation.

## 1.4 Human-in-the-Loop Agent

Role: Decides when humans must be involved.

Responsibilities:

* Requires human review for high-risk events.
* Requires finance, owner, MSP, or security review where appropriate.
* Prevents silent automation on serious events.
* Tracks whether a human decision happened.

Output:

* Human review required: yes/no.
* Required reviewer.
* Review reason.

## 1.5 Final Review Agent

Role: Reviews the complete case before final output.

Responsibilities:

* Confirms that verdict, evidence, explanation, and recommendation match.
* Checks that no unsupported claims are made.
* Confirms the case is ready for client-facing or internal output.

Output:

* Final verdict.
* Final recommendation.
* Final evidence package.

---

# 2. Mutant Monkey Rules of Engagement

Rules of Engagement define what the swarm is allowed to do, when it must escalate, and when it must stop.

## Core rules

* If money movement is involved, never approve automatically.
* If payment instructions changed, require known-good verification.
* If sender authentication passes but behavior is abnormal, treat it as possible compromised mailbox activity.
* If evidence is incomplete, use **needs review** instead of **confirmed fraud**.
* If the action could disrupt business, require human approval.
* If ransomware precursor signals are present, escalate to MSP or security lead.
* If the system cannot prove a claim, it must not say it as fact.
* If agents disagree on a high-risk case, escalate or require challenge review.
* If a case fails testing, record the failure and require retest evidence.

## Purpose

Mutant Monkey agents are not free to improvise without boundaries. They operate inside a defensive command structure with evidence rules, escalation rules, and safety limits.

---

# 3. Mutant Monkey Agent Authority Levels

Not every agent has the same authority. Agents earn influence based on performance, evidence quality, and case-type reliability.

## Level 1 — Observer Agent

Can:

* Detect and report signals.
* Flag suspicious details.
* Provide observations.

Cannot:

* Make final decisions.
* Recommend business action alone.

## Level 2 — Analyst Agent

Can:

* Classify risk.
* Suggest severity.
* Recommend additional review.

Cannot:

* Finalize high-risk cases alone.

## Level 3 — Specialist Agent

Can:

* Produce domain-specific evidence.
* Review specialized risks such as vendor-payment changes, phishing links, ransomware precursors, or cyber-insurance gaps.

Cannot:

* Override command rules.

## Level 4 — Commander Agent

Can:

* Assign agents.
* Route cases.
* Set review paths.
* Escalate cases.

Cannot:

* Ignore evidence rules.

## Level 5 — Challenge Agent

Can:

* Challenge weak decisions.
* Block unsupported verdicts.
* Force human review.
* Flag assumptions and missing evidence.

Cannot:

* Approve risky actions without required evidence.

## Level 6 — Final Review Agent

Can:

* Approve the final decision package.
* Confirm the evidence record is complete.
* Release the final explanation or recommendation.

Cannot:

* Overclaim beyond the evidence.

---

# 4. Mutant Monkey Agent Reputation System

This is the promotion and demotion system inside the swarm.

Agents do not get promoted emotionally. They earn more or less decision weight based on evidence-backed performance.

## Reputation scoring categories

### Accuracy

Did the agent identify the correct risk?

### Evidence quality

Did the agent provide useful proof instead of vague claims?

### False positive rate

Did the agent overreact too often?

### False negative rate

Did the agent miss serious threats?

### Consistency

Did the agent behave reliably across similar cases?

### Correction history

When the agent was wrong, was the correction recorded and retested?

### Case-type strength

Is the agent strong in this specific domain?

Example:

* Vendor-payment fraud
* Phishing
* Ransomware precursor detection
* Cyber-insurance evidence
* Executive impersonation
* Payroll diversion

## Domain-specific reputation

Agents should not have one universal score. They should have case-specific reputation.

Example:

```text
Payment Change Agent
Vendor payment fraud: 94/100
Payroll diversion: 71/100
Ransomware precursor: not authorized
Cyber-insurance evidence: 82/100
```

## Promotion rule

An agent earns more influence when it is consistently accurate, evidence-backed, and retest-proven in a specific case type.

## Demotion rule

An agent loses influence when it overclaims, misses key evidence, produces unsupported recommendations, or fails retesting.

---

# 5. Mutant Monkey Two-Pass Decision Model

This replaces exposed chain-of-thought.

The system should not show clients every internal reasoning step. Instead, it should show the evidence-backed decision record.

## Pass 1 — Detection Pass

Purpose:

* Detect the risk.
* Classify the case.
* Identify suspicious signals.
* Assign initial severity.
* Decide which specialist agents are needed.

Example output:

```text
Initial finding:
This appears to be a vendor-payment-change event with high-risk indicators.
```

## Pass 2 — Challenge and Verification Pass

Purpose:

* Challenge the first finding.
* Check for weak evidence.
* Separate facts from assumptions.
* Verify whether the verdict is supported.
* Decide whether human review is required.
* Produce the final recommendation.

Example output:

```text
Challenge finding:
The initial risk is supported by bank-detail drift and callback-pressure language. Sender authentication passed, so this may be compromised trusted mailbox activity rather than simple spoofing. Payment should be held until verified through a known-good contact.
```

## Clean product language

**First pass detects. Second pass challenges. Final output documents.**

---

# 6. Mutant Monkey Decision Evidence Record

This is the client-safe replacement for chain-of-thought.

Instead of showing hidden reasoning, Mutant Monkey Security shows a structured evidence record.

## Evidence record structure

### Observed facts

What the system directly observed.

Examples:

* Email came from a known vendor domain.
* Banking instructions changed.
* Email requested same-day payment.
* Callback number was provided inside the email.
* Link points to a domain that does not match the visible sender.

### Interpretations

What the observations may mean.

Examples:

* Possible vendor-payment-change fraud.
* Possible compromised trusted mailbox.
* Possible credential phishing attempt.
* Possible ransomware precursor event.

### Assumptions

What is not yet proven.

Examples:

* Sender may not be the true vendor representative.
* Payment change may be unauthorized.
* Link may be credential-harvesting.
* Attachment may require sandbox review.

### Missing evidence

What the system still needs.

Examples:

* No known-good callback confirmation yet.
* No second-person approval recorded yet.
* No vendor master record match yet.
* No MSP review recorded yet.

### Recommended verification

What should happen next.

Examples:

* Hold payment.
* Verify through known-good contact.
* Require second-person approval.
* Reset credentials.
* Review inbox rules.
* Escalate to MSP or security lead.

### Final outcome

What happened after review.

Examples:

* Confirmed legitimate.
* Confirmed fraudulent.
* Needs review.
* Follow-up needed.
* Owner override.
* Known exception.
* Payment held.
* Credentials reset.
* Evidence packet created.

---

# 7. Mutant Monkey Decision Conflict Resolution

Agents will disagree. The swarm needs a formal disagreement process.

## Purpose

The system should not average agent opinions blindly. It should resolve disagreement based on evidence, authority, and case type.

## Conflict questions

When agents disagree, the system asks:

* Which agent has stronger evidence?
* Which agent has more authority for this case type?
* Is the disagreement about facts, interpretation, or severity?
* Is money, access, or business continuity at risk?
* Does the disagreement require human review?
* Should uncertainty upgrade the case to needs review or high risk?

## Example conflict

```text
Technical authentication appears normal.
Vendor-payment behavior changed.
Because financial exposure is present and verification is incomplete, final status remains hold/review recommended.
```

## Product value

This makes Mutant Monkey Security more trustworthy because it does not hide uncertainty. It documents why the safer decision was chosen.

---

# 8. Mutant Monkey Specialist Teams

The 60–70 agent swarm should be managed as teams, not as 70 separate loose agents.

## 8.1 Email Identity and Sender Analysis Team

Purpose:
Determine whether the sender identity can be trusted.

Agents:

* Header Analysis Agent
* Sender Identity Agent
* Reply-To Mismatch Agent
* Domain Reputation Agent
* Lookalike Domain Agent
* Known-Good Contact Agent
* Compromised Mailbox Suspicion Agent

Tasks:

* Review SPF, DKIM, DMARC, return path, reply-to, sender path, and forwarding details.
* Detect spoofing or routing anomalies.
* Compare sender identity against known contacts.
* Detect display-name deception.
* Detect mismatched email addresses.
* Flag newly registered or suspicious domains.
* Detect typosquatting and homoglyph tricks.
* Identify possible compromised trusted mailboxes.

## 8.2 Vendor-Payment and Business Email Compromise Team

Purpose:
Detect trusted-relationship fraud before money moves.

Agents:

* Vendor Relationship Intelligence Agent
* Payment Change Detection Agent
* Invoice Fraud Agent
* Bank Detail Drift Agent
* Vendor Master Record Agent
* Callback Verification Agent
* Dual-Approval Agent
* Financial Exposure Agent
* Executive Impersonation Agent
* Payroll Diversion Agent

Tasks:

* Detect new bank account instructions.
* Detect routing-number drift.
* Detect wire-transfer changes.
* Detect new payment portals.
* Compare invoice format to prior invoices.
* Review payment cadence and vendor history.
* Require known-good callback verification.
* Require second-person approval for larger payment changes.
* Estimate financial exposure.
* Detect CEO, CFO, owner, vendor, or payroll impersonation.

## 8.3 Phishing and Credential-Theft Team

Purpose:
Detect phishing, account takeover, and credential theft.

Agents:

* Credential Phishing Agent
* MFA Manipulation Agent
* Session Theft Agent
* QR Phishing Agent
* Link Inspection Agent
* Brand Impersonation Agent
* Form Abuse Agent

Tasks:

* Detect fake login pages.
* Detect password reset traps.
* Detect Microsoft 365, Google, DocuSign, Dropbox, bank, payroll, courier, and tax impersonation.
* Detect requests to approve MFA prompts or share codes.
* Detect suspicious OAuth or session-token theft flows.
* Detect QR-code phishing.
* Review links, redirects, shorteners, and suspicious landing pages.
* Detect fake forms requesting credentials, payment data, tax records, or vendor data.

## 8.4 Attachment and Ransomware Precursor Team

Purpose:
Detect early signs of malware delivery or ransomware exposure.

Agents:

* Attachment Risk Agent
* PDF Fingerprint Agent
* Macro and Script Risk Agent
* Payload Delivery Agent
* Remote Access Abuse Agent
* Inbox Rule Abuse Agent
* Account Takeover Agent
* Ransomware Precursor Agent
* Containment Recommendation Agent

Tasks:

* Review suspicious attachments.
* Flag risky PDFs, Office files, archives, scripts, macros, and executables.
* Compare PDF producer metadata.
* Detect suspicious invoice document changes.
* Detect links or attachments that may deliver malware.
* Detect remote access tool abuse.
* Review suspicious inbox rules.
* Detect account takeover indicators.
* Recommend containment steps such as hold payment, reset credentials, review inbox rules, isolate device, block sender, or escalate to MSP.

## 8.5 Language, Behavior, and Deception Team

Purpose:
Detect manipulation, behavioral drift, and process bypass.

Agents:

* Language Pressure Agent
* Tone Drift Agent
* Behavioral Baseline Agent
* Timing Anomaly Agent
* Geo-Context Agent
* Social Engineering Agent
* Process Bypass Agent

Tasks:

* Detect urgency, secrecy, fear, shame, authority pressure, and time pressure.
* Detect "do not call," "I'm unavailable," "handle this now," or "keep this confidential" language.
* Compare tone against prior known-good communication.
* Flag unusual formality, spelling, phrasing, or behavior.
* Detect unusual send times.
* Review location signals where available.
* Detect attempts to skip approval, callback, ticketing, payment, or vendor-update procedures.

## 8.6 Evidence and Audit Team

Purpose:
Turn detection into reviewable evidence.

Agents:

* Evidence Package Agent
* Case Timeline Agent
* Verification Outcome Agent
* Audit Trail Agent
* Evidence Strength Agent
* Assumption Control Agent
* Plain-English Explanation Agent
* Safe Language Agent

Tasks:

* Build evidence packets.
* Create case timelines.
* Record verification outcomes.
* Preserve decision history.
* Score evidence quality.
* Separate facts, observations, interpretations, assumptions, and missing evidence.
* Create client-readable explanations.
* Remove risky overclaims.

## 8.7 Cyber Insurance Evidence Team

Purpose:
Turn security activity into cyber-insurance-useful documentation.

Agents:

* Cyber Insurance Evidence Agent
* Control Mapping Agent
* Renewal Readiness Agent
* Underwriter Summary Agent
* Claim Support Agent
* Exception Tracking Agent
* Evidence Freshness Agent

Tasks:

* Convert security activity into underwriting or renewal evidence.
* Show proof of operation, not just policy claims.
* Map cases to controls such as MFA, vendor verification, dual approval, phishing training, incident response, backup review, endpoint protection, and access control.
* Prepare concise underwriter summaries.
* Preserve incident timelines and containment evidence.
* Track partial controls, known gaps, unresolved issues, owner overrides, and stale evidence.

## 8.8 Challenge and Decision Integrity Team

Purpose:
Prevent overconfidence, unsupported decisions, and weak evidence.

Agents:

* Decision Challenge Agent
* Assumption Control Agent
* Overclaim Prevention Agent
* False Positive Review Agent
* False Negative Review Agent
* Conflict Resolution Agent
* Final Decision Integrity Agent

Tasks:

* Challenge weak decisions.
* Check whether evidence supports the verdict.
* Separate facts from assumptions.
* Flag missing evidence.
* Identify possible false positives and false negatives.
* Resolve agent disagreement.
* Force human review where needed.
* Prevent unsupported claims.

## 8.9 Learning, Testing, and Improvement Team

Purpose:
Make the swarm evolve safely over time.

Agents:

* Test Case Generator Agent
* Regression Test Agent
* Adversarial Test Agent
* Failure Classification Agent
* Correction Evidence Agent
* Drift Watch Agent
* Rule Improvement Agent
* Swarm Memory Agent
* Swarm Health Agent
* Agent Reputation Agent

Tasks:

* Create test cases for phishing, vendor fraud, invoice fraud, payroll diversion, executive impersonation, ransomware precursor events, and cyber-insurance evidence.
* Run regression tests after detector, scoring, schema, rendering, orchestration, or evidence changes.
* Create hard cases that try to fool the system safely.
* Classify failures.
* Record corrections.
* Require retest evidence before calling a fix complete.
* Watch attacker behavior drift.
* Suggest rule and threshold improvements.
* Store prior cases, trusted relationships, known exceptions, and verification outcomes.
* Detect broken workflows or agent inconsistency.
* Update agent reputation scores.

---

# 9. Mutant Monkey Blue-Team Command Tree

```text
Mutant Monkey Swarm Command
│
├── 1. Command Layer
│   ├── Swarm Commander Agent
│   ├── Mission Context Agent
│   ├── Severity Commander Agent
│   ├── Human-in-the-Loop Agent
│   └── Final Review Agent
│
├── 2. Rules of Engagement
│   ├── Money Movement Rule
│   ├── Payment Change Verification Rule
│   ├── Compromised Mailbox Rule
│   ├── Incomplete Evidence Rule
│   ├── Business Disruption Rule
│   ├── Ransomware Escalation Rule
│   ├── No Overclaim Rule
│   ├── Agent Disagreement Rule
│   └── Failed Test Retest Rule
│
├── 3. Agent Authority System
│   ├── Level 1 — Observer Agent
│   ├── Level 2 — Analyst Agent
│   ├── Level 3 — Specialist Agent
│   ├── Level 4 — Commander Agent
│   ├── Level 5 — Challenge Agent
│   └── Level 6 — Final Review Agent
│
├── 4. Agent Reputation System
│   ├── Accuracy Score
│   ├── Evidence Quality Score
│   ├── False Positive Rate
│   ├── False Negative Rate
│   ├── Consistency Score
│   ├── Correction History
│   └── Case-Type Strength
│
├── 5. Two-Pass Decision Model
│   ├── Pass 1 — Detection Pass
│   ├── Pass 2 — Challenge and Verification Pass
│   └── Final Output — Decision Evidence Record
│
├── 6. Decision Evidence Record
│   ├── Observed Facts
│   ├── Interpretations
│   ├── Assumptions
│   ├── Missing Evidence
│   ├── Recommended Verification
│   └── Final Outcome
│
├── 7. Decision Conflict Resolution
│   ├── Evidence Strength Review
│   ├── Authority Review
│   ├── Case-Type Review
│   ├── Uncertainty Review
│   └── Human Escalation Review
│
├── 8. Specialist Teams
│   ├── Email Identity and Sender Analysis Team
│   ├── Vendor-Payment and BEC Team
│   ├── Phishing and Credential-Theft Team
│   ├── Attachment and Ransomware Precursor Team
│   ├── Language, Behavior, and Deception Team
│   ├── Evidence and Audit Team
│   ├── Cyber Insurance Evidence Team
│   ├── Challenge and Decision Integrity Team
│   └── Learning, Testing, and Improvement Team
│
└── 9. Final Product Output
    ├── Risk Verdict
    ├── Severity Level
    ├── Evidence Summary
    ├── Verification Requirement
    ├── Recommended Action
    ├── Human Review Status
    ├── Case Timeline
    ├── Insurance Evidence Summary
    └── Retest / Learning Record
```

---

# 10. V1 Starting Swarm

Mutant Monkey Security does not need all 60–70 agents on day one. The first version should prove the command structure.

## Recommended V1 agents

1. Swarm Commander Agent
2. Mission Context Agent
3. Severity Commander Agent
4. Sender Identity Agent
5. Vendor Relationship Intelligence Agent
6. Payment Change Detection Agent
7. Link Inspection Agent
8. Language Pressure Agent
9. Callback Verification Agent
10. Evidence Package Agent
11. Decision Challenge Agent
12. Safe Language Agent
13. Final Review Agent
14. Agent Reputation Agent

## V1 purpose

The first version should prove that Mutant Monkey Security can:

* Detect a suspicious vendor-payment or phishing event.
* Classify seriousness.
* Assign the right review path.
* Require verification when money or credentials are at risk.
* Produce a clean evidence record.
* Challenge unsupported conclusions.
* Avoid overclaiming.
* Record the final outcome.
* Learn from failed or corrected cases.

---

# 11. Future 60–70 Agent Swarm

Once V1 is proven, Mutant Monkey Security can expand into the full swarm.

## Expansion areas

* More vendor-fraud agents.
* More phishing agents.
* More ransomware precursor agents.
* More cyber-insurance evidence agents.
* More control-mapping agents.
* More testing agents.
* More behavioral drift agents.
* More agent reputation and governance agents.

## Long-term vision

Mutant Monkey Security becomes an evolving defensive AI swarm that improves through evidence, testing, correction, and retesting.

It does not rely on blind confidence.

It relies on:

* Signals
* Verification
* Evidence
* Challenge
* Human review
* Outcome records
* Retest history
* Agent reputation

---

# 12. One-paragraph summary

**Mutant Monkey Security is an evolving blue-team swarm where specialized agents detect, verify, challenge, and document email-borne risk. The swarm uses a command structure to assign agents based on case type and severity. Each agent produces evidence, not just opinions. A two-pass decision model allows the system to detect risk first, then challenge and verify the decision before final output. Over time, agents earn or lose decision authority based on accuracy, evidence quality, correction history, and retest results. The result is a defensive AI system that becomes more trustworthy because every decision can be reviewed, scored, corrected, and proven.**

---

# 13. Best positioning line

**Mutant Monkey Security is an evolving blue-team evidence swarm for email fraud, phishing, ransomware precursors, and cyber-insurance proof.**

# 14. Best internal slogan

**First pass detects. Second pass challenges. Final output documents.**

# 15. Best trust slogan

**No trust decision without evidence. No high-risk action without verification. No failure without a learning record.**
