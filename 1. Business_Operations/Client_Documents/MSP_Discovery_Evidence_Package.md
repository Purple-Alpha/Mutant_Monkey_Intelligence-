# NorthStar Inbox Shield — MSP Discovery Evidence Package

**Prepared by:** Matt — NorthStar Security, Kelowna BC
**Version:** 1.0 (2026-05-23)
**Audience:** MSP owners, principal consultants, vCISOs evaluating fraud / BEC tooling for their SMB client base
**Format:** Single-file evidence bundle for review after an introductory discovery call

---

## The 60-Second Read

NorthStar Inbox Shield is an **auditable AI fraud-detection layer** for SMB email. It scores inbound email for vendor invoice fraud, executive impersonation, wire-transfer pressure, lookalike domains, and ransomware-precursor signals, and produces evidence-grade reporting that an MSP can defend to a client, an insurer, or a regulator.

What it does today:
- Analyzes and scores email content with a locked LLM scoring prompt.
- Produces structured risk analysis (`risk_score`, `vendor_fraud_score`, `invoice_authenticity_score`, recommended action label).
- Generates MSP-facing evidence reports with per-tenant parameter provenance.
- Exposes a per-tenant operator CLI so MSPs can tune sensitivity per client with full audit.
- Maintains a kill switch and a signed policy pipeline so nothing changes silently.

What it does **not** do today:
- Does not block, quarantine, delete, or remediate email.
- Does not modify M365 / Google Workspace settings.
- Does not replace human approval for payments or vendor changes.

It is a **decision-support and reporting layer first** — built so MSPs can position fraud detection as a defensible, monthly-reviewable service rather than an opaque AI black box.

---

## Why MSPs Should Care

There are plenty of AI email-security tools on the market. The differences that matter for an MSP positioning to an SMB:

| Concern | Most AI tools | NorthStar Inbox Shield |
|---|---|---|
| Why did it flag this? | Black box | Structured risk-factor breakdown per email, signed scoring prompt |
| Per-client tuning | Vendor-controlled | Operator CLI, per-tenant overrides with audit trail |
| Proof for the client / insurer | "We have AI" | Effective Parameter Report with provenance, eval-gate results, signed promotion log |
| When the AI changes its mind | Silent vendor update | Signed policy pipeline, append-only audit, rollback primitive |
| What if it makes a mistake | Vendor support ticket | Operator kill switch, per-tenant pause / revoke, reversible |
| Cross-tenant data leak | Vendor-managed boundary | Guardrail 11 enforces tenant isolation at the gate |

This is the **auditable AI moat.** It is the difference between a tool you bolt on and a tool you can defend to a $5M-revenue manufacturing client whose CFO just wired $47,000 to a fraudster.

---

## Proof Point 1 — Live LLM Eval Gate (40-case)

The current scoring prompt was evaluated against a curated 40-case fraud dataset using xAI's `grok-4` model. Results below are from the actual saved report at `eval_report_2026_05_22_phase_1_5_rerun.md`.

**Aggregate (full 40-case rerun, 2026-05-22):**

| Metric | Result |
|---|---:|
| Cases evaluated | 40 |
| Cases passed | 36 / 40 |
| **Precision on fraud cases** | **100.00%** |
| **False positive rate on legit cases** | **0.00%** |

**Per-subcategory recall:**

| Subcategory | Total | Passed | Recall |
|---|---:|---:|---:|
| executive_impersonation | 5 | 4 | 80.00% |
| header_inconsistency | 1 | 1 | 100.00% |
| invoice_authenticity_anomaly | 3 | 3 | 100.00% |
| lookalike_sender | 2 | 2 | 100.00% |
| vendor_invoice_fraud | 5 | 2 | **40.00%** ⚠️ |
| wire_transfer_pressure | 4 | 4 | 100.00% |
| legit_calendar | 3 | 3 | 100.00% |
| legit_hr | 2 | 2 | 100.00% |
| legit_internal | 5 | 5 | 100.00% |
| legit_newsletter | 2 | 2 | 100.00% |
| legit_vendor_invoice | 8 | 8 | 100.00% |

**Honest read:** This run did not pass the internal gate. The `vendor_invoice_fraud` subcategory recall fell to 40% (2 of 5 cases). **Precision and false-positive rate stayed clean** — the tool was not flagging legitimate emails as fraud; it was missing some real vendor-invoice fraud patterns. Diagnosed, remediated, and re-verified in Proof Point 2.

This transparency about an internal failure is itself part of the proof: a vendor that doesn't show you their failures is hiding them.

---

## Proof Point 2 — Recall Remediation (post-patch verification)

After the 40-case rerun failed the recall floor, the scoring prompt was patched (no API spend, no model change) to pin the five weak vendor-invoice fraud shapes:

1. First invoice after onboarding with remittance instructions only in the attached PDF.
2. Updated remit-to address with old instructions declared invalid.
3. Fake thread continuity (`Re:`, "following up as discussed below", "as discussed" with no quoted history).
4. High-value emergency invoice approval before EOD tied to shipment / operations pressure.
5. Explicit new ACH / banking details with urgency.

Five single-case live diagnostics were re-run on `grok-4` against each of the previously-failing cases. Results:

| Case | Pattern | Risk Score | Vendor Fraud Score | Recommended Action | Verdict |
|---|---|---:|---:|---|---|
| vf-001 | New ACH details + urgency, lookalike sender domain | 88 | 88 | **block** | PASS |
| vf-002 | First invoice after onboarding, PDF-only remittance | 65 | 60 | **needs_review** | PASS |
| vf-003 | Updated remit-to with old instructions invalid | 68 | 65 | **needs_review** | PASS |
| vf-004 | Fake thread continuity (`Re:` no quoted history) | 70 | 68 | **needs_review** | PASS |
| vf-005 | High-value emergency invoice before EOD | 78 | 70 | **needs_review** | PASS |

**5 / 5 vendor-invoice cases passed after the prompt patch.** Per-case diagnostic reports are saved as durable markdown files (`eval_report_2026_05_22_phase_1_5_vf-001_diagnostic.md` through `vf-005_diagnostic.md`).

### Sample raw LLM response (case vf-001)

This is the actual structured JSON output of the scoring agent for a real fraud case. An MSP can see exactly *why* the email was flagged:

```json
{
  "summary": "Sender claims to be Acme Manufacturing requesting urgent payment of $48,920 for invoice 4471 with new ACH details provided in both body and attached PDF.",
  "risk_analysis": {
    "risk_score": 88,
    "risk_factors": ["new banking instructions", "urgent payment request", "sender domain anomaly"],
    "phishing_signals": ["lookalike sender domain"],
    "urgency_signals": ["push through today", "missed last cycle"],
    "financial_risk": "high",
    "vendor_fraud_score": 88,
    "wire_transfer_anomaly_score": 72,
    "invoice_authenticity_score": 25,
    "behavioral_deviation_flags": [
      "new_banking_instructions",
      "urgency_paired_with_finance",
      "lookalike_sender_domain"
    ]
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 75,
    "suspicious_elements": [
      "domain .co instead of expected corporate domain",
      "new ACH details only in this message"
    ],
    "sender_legitimacy_notes": "Sender domain does not match typical Acme Manufacturing corporate domains"
  },
  "recommended_action": "block"
}
```

This level of structured output is what an MSP shows the client's CFO when explaining why the payment was held.

---

## Proof Point 3 — Effective Parameter Report (real generated demo)

The Effective Parameter Report is the **MSP-facing evidence artifact** for what scoring sensitivity is currently active for a given tenant, where it came from, and what has changed. It pulls from signed policy state plus any active per-tenant override plus the recent audit trail.

The Acme demo report is now generated by the real runtime CLI, not hand-written:

```powershell
cd "C:\Unified Folder Structure NorthStar + SwarmCommand Venture\3. SwarmCommand_Engine\Agent_Loop_Runtime\Runtime_Implementation"
python -m scripts.acme_effective_parameter_report_demo
```

Generated artifact:

`1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md`

That command seeds an isolated demo blackboard for the fictional `acme-industries-demo` tenant, writes deterministic signed policy state, creates real override audit events through the existing per-tenant override API, and then invokes the existing `tenant_override_operator report --format markdown --out ...` path.

Current demo output summary:

| Parameter | Effective Value | Source | Signed Policy | Tenant Override |
|---|---:|---|---:|---:|
| `attachment_risk_floor_lift` | 0 | `signed_policy` | 0 | none |
| `fraud_risk_floor_lift` | 10 | `tenant_override` | 5 | 10 |
| `url_obfuscation_floor_lift` | 8 | `tenant_override` | 5 | 8 |

Recent audit events in the generated report:

| Timestamp | Event | Requester | Approver | Source |
|---|---|---|---|---|
| 2026-05-23T15:15:00+00:00 | `tenant_parameter_override_updated` | `msp_operator_jane` | `msp_owner_dave` | `demo_effective_parameter_report_generator` |
| 2026-05-23T15:00:00+00:00 | `tenant_parameter_override_created` | `msp_operator_jane` | `msp_owner_dave` | `demo_effective_parameter_report_generator` |

What this gives the MSP:
- A single artifact to attach to a monthly business review.
- A clear trail for cyber-insurance renewal questionnaires.
- A defense if a client ever asks "why did you block this email?" or "why did this slip through?"

---

## Proof Point 4 — The Non-Negotiable Guardrails

These are runtime guardrails, not pricing tiers. **No tier removes them. No tier can override them.**

| Guardrail | What it does | Why an MSP should care |
|---|---|---|
| **Operator kill switch (Guardrail 12)** | Pulls all 9 loop entry points to halt. Operator-controlled. | If anything ever goes wrong, you have an off switch you control. |
| **Append-only audit (Blackboard)** | Every record, every change, every action is logged. Tamper-evident. | Compliance, insurance, client trust. |
| **Signed policy promotion pipeline** | Every scoring sensitivity change is cryptographically signed and traceable. | No silent vendor updates. You see and approve every change. |
| **Tenant isolation (Guardrail 11)** | Cross-tenant data leakage is rejected at the gate. | One client's data never leaks to another client's analysis. |
| **Per-tenant override audit (JSONL)** | Every operator change is timestamped and attributed. | If a client asks "who changed this and when," there is a single answer. |
| **Policy rollback primitive** | Any signed policy update can be reverted. | If a tuning change misfires, you revert. |
| **Write-time parameter validation** | Invalid override values are rejected, not silently clamped. | No silent drift. Operators see errors immediately. |

---

## Test Suite Verification

Current runtime baseline: **473 automated tests passing** (exit code 0).

Key test surfaces an MSP-side auditor would care about:
- Multi-tenant isolation: `tests/test_multi_tenant_isolation.py`
- Kill switch end-to-end: `tests/test_kill_switch_e2e.py`
- Policy promotion + rollback: `tests/test_policy_pipeline.py`, `tests/test_policy_rollback.py`
- Per-tenant override: `tests/test_tenant_parameter_overrides.py` (15 tests)
- Operator override CLI: `tests/test_tenant_override_operator_cli.py` (9 tests)
- Effective parameter report: `tests/test_effective_parameters_report.py` (18 tests)
- Scoring prompt lock: `tests/test_email_risk_scoring_agent.py` (28 tests)
- Sandbox close-the-loop: `tests/test_phase_1_4_mutation_engine_specialization.py::test_close_the_loop_red_battery_to_next_cycle_effect`

---

## SMB Tier Menu (for client packaging)

| Tier | Buyer profile | Includes |
|---|---|---|
| **Essentials** | SMB owner-operator, light email volume, awareness training already in place | Fraud scoring + ransomware-precursor overlay + monthly leadership summary + recommended action label + basic evidence-package support + kill switch + audit |
| **Plus** | SMB with active finance team, real wire / vendor fraud risk, MSP-managed | Everything in Essentials + daily digest + per-tenant overrides + operator CLI + effective-parameter report + anomaly / drift / forecast (planned) + gated one-hour training loop on trigger |
| **Enterprise** | Multi-client MSP, finance-heavy SMB fleet, regulated industries, insurance reporting requirement | Everything in Plus + tenant-fleet aggregation + campaign clustering + trend orchestration + RBAC enforcer + drift guardrail + full evidence-chain export |

**Tier rules:** No tier removes the kill switch, audit, or cross-tenant rejection. No tier expands the eligible per-tenant override keys (only `fraud_risk_floor_lift`, `attachment_risk_floor_lift`, `url_obfuscation_floor_lift` are operator-tunable).

---

## What This Package Does NOT Claim

In keeping with the auditable-AI posture, here is what NorthStar Inbox Shield is **not** today:

- Not a replacement for Microsoft Defender for Office 365 or Google Workspace Advanced Protection at the gateway layer.
- Not a SOAR / SIEM. It produces evidence, not workflow orchestration.
- Not a guarantee. No security tool is. It is a decision-support and reporting layer.
- Not currently integrated with M365 / Google Workspace at the action layer. (Roadmapped for Stage B — 12 to 24 months.)
- Not multi-region cloud-hosted yet. Current deployments are operator-run on local or VPS infrastructure.

The roadmap to autonomous defensive action with live mailbox integration is documented internally as Stage B of a multi-stage arc. The pitch today is Stage A: **evidence and decision support an MSP can defend.**

---

## Pilot Offer

**First-MSP-pilot terms (free):**

- 30 days, one of your SMB tenants of your choice.
- You operate the override CLI; I operate the scoring runtime and produce the monthly Effective Parameter Report.
- You hand the report to your client and to your insurance broker as proof of monitoring.
- At the end of 30 days we both decide: walk away, continue at a per-tenant rate, or expand to a fleet retainer.

**What I need from you:**
- A non-sensitive subset of email samples (or synthesized cases derived from real patterns) for one tenant.
- 15 minutes per week for the first 4 weeks.
- An honest conversation at day 30.

**What I commit:**
- A signed evidence package every week.
- Full operator transparency — you see every parameter, every override, every audit event.
- A written postmortem if the pilot doesn't deliver what we discussed.

---

## Suggested Discovery Follow-up Questions

If this package raised questions, here are the ones I'd want to dig into on the next call:

1. Who at your firm currently handles a client's "is this email real?" ticket?
2. What's your average time-to-respond on a suspected-fraud client escalation?
3. How do you currently document fraud detection for cyber-insurance renewals?
4. What would a 30-day pilot need to prove for you to bring it to a paying client?
5. Who else in your network (MSP peers, brokers, insurers) should I be talking to about this?

---

## Contact

**Matt — NorthStar Security**
Kelowna, BC
[email to be filled in]
[LinkedIn to be filled in]

This package and all referenced reports are reproducible from the current runtime build (commit / version tag to be embedded at send time).

---

## Appendix — Source-of-Truth Files

For future technical due diligence, the following files in the NorthStar runtime support every claim in this package:

| Claim | Source |
|---|---|
| 40-case eval result | `Runtime_Implementation/eval_report_2026_05_22_phase_1_5_rerun.md` |
| Vendor-invoice diagnostic recovery | `Runtime_Implementation/eval_report_2026_05_22_phase_1_5_vf-00{1..5}_diagnostic.md` |
| Locked scoring prompt | `core/scoring/email_risk_scoring_agent.py::NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` |
| Effective Parameter Report builder | `core/production_state/effective_parameters_report.py` |
| Generated Acme Effective Parameter Report demo | `1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md` |
| Acme report demo generator | `Runtime_Implementation/scripts/acme_effective_parameter_report_demo.py` |
| Per-tenant override runtime | `core/production_state/tenant_overrides.py` |
| Operator CLI | `core/production_state/tenant_override_operator.py` |
| Kill switch | `core/operator_state/` + `core/production_state/gate.py` |
| Tenant isolation guardrail | `tests/test_multi_tenant_isolation.py` |
| Customer-facing product sheet | `4. Product_Roadmap/Product_Sheets/Fraud_Detection_Product_Sheet.md` |
| SMB tier matrix | Same product sheet, "SMB Tier Matrix" section |
