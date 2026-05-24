# NorthStar Inbox Shield — Fraud Detection Product Sheet

**Status:** Customer-facing v1 draft, created for Month 6 Phase 2.1.
**Audience:** SMB owners, office managers, finance leads, MSP partners, and non-technical leadership.
**Current runtime scope:** Analysis, scoring, reporting, recommendations, and evidence support. NorthStar Inbox Shield does **not** currently block, quarantine, delete, or remediate emails.

## Plain-English Offer

NorthStar Inbox Shield helps small businesses spot email fraud before it becomes a payment mistake, account compromise, or business interruption.

It reviews inbound email risk, highlights suspicious financial and impersonation patterns, and turns the findings into plain-English reporting that owners, finance teams, and MSP partners can act on.

## What It Helps Detect

- Vendor invoice fraud.
- New or unusual banking instructions.
- Wire-transfer pressure.
- Executive impersonation.
- Lookalike sender domains.
- Invoice authenticity anomalies.
- Suspicious attachments and links that may be early ransomware precursors.
- Behavioral changes in tone, urgency, sender identity, or payment request pattern.

## What Inbox Shield Does Today

NorthStar Inbox Shield currently:

- Analyzes email content and metadata supplied to the runtime.
- Scores fraud, wire-transfer, invoice-authenticity, impersonation, attachment, URL, and precursor signals.
- Produces structured risk analysis using the locked `EmailAnalysisPayload` schema.
- Generates recommended business actions such as `safe`, `needs_review`, or `block` as an advisory label.
- Supports monthly leadership reporting, daily digest generation, operator notes, and evidence-package workflows.
- Uses sandbox evaluation and signed policy updates to improve defensive sensitivity without allowing uncontrolled production mutation.

## What Inbox Shield Does Not Do Yet

NorthStar Inbox Shield does **not** currently:

- Block or quarantine emails directly.
- Delete messages from mailboxes.
- Change Microsoft 365, Google Workspace, or mail-gateway settings.
- Fetch URLs, execute attachments, or interact with live infrastructure.
- Replace human approval for payments, vendor changes, wire transfers, or incident response.
- Provide a customer self-serve secure portal in the MVP runtime.

The product is designed as a decision-support and reporting layer first. Direct email action capabilities are future enhancements.

## Proof Points

The current fraud detection baseline has already passed an internal live LLM evaluation gate on `grok-4`:

| Proof Point | Result |
|---|---:|
| Fraud eval cases | 40 total |
| Final passing cases | 36 / 40 |
| Fraud precision | 100% |
| Legit false-positive rate | 0% |
| Fraud subcategory recall floor | Met across all required categories |
| Durable report | `eval_report_2026_05_21_final_recovery_grok4.md` |

The runtime also has a closed defensive-improvement loop:

1. Sandbox Red profiles generate synthetic fraud and ransomware-precursor cases.
2. Blue scoring evaluates the cases with the production scoring path.
3. Weakness reports identify concrete failure patterns.
4. The mutation engine proposes typed sensitivity changes.
5. Signed policy updates pass through the promotion pipeline and Guardrail 11 gate.
6. Production scoring reads the approved parameters on the next cycle.

This is verified by the Month 5 close-the-loop gate test: `test_close_the_loop_red_battery_to_next_cycle_effect`.

## Buyer Message

Fraud starts in the inbox. Ransomware often starts with a click. NorthStar Inbox Shield gives SMBs and MSPs a practical way to see those risks early, explain them clearly, and document what was found.

## MSP Positioning

For MSPs, Inbox Shield is a lightweight human-layer security add-on:

- Easy to explain to non-technical clients.
- Useful for monthly business reviews.
- Supports cyber-insurance and leadership reporting.
- Creates recurring value without requiring a full SOC.
- Pairs naturally with Microsoft 365, Google Workspace, endpoint security, backup, and awareness training services.

## Recommended First Package

**NorthStar Inbox Shield — Fraud Monitoring Add-On**

Includes:

- Monthly inbox-risk summary.
- Fraud-category breakdown.
- Top risk signals.
- Recommended business actions.
- Leadership-ready summary.
- Evidence-package support.
- MSP/operator notes for follow-up.

## SMB Tier Matrix — Essentials / Plus / Enterprise

Three packaged tiers map the current runtime, the planned trend / anomaly / drift cluster, and the autonomy and governance surfaces onto buyer-readable capability sets. Tier names match the runtime tier vocabulary used across `Autonomous_Orchestration/agent-enablement-map-per-tier.md` and `trigger-routing-table-per-tier.md`.

### Tier intent

- **Essentials** — Stable, low-noise, **report-first** fraud monitoring for very small businesses or MSPs with one or two clients. No anomaly, drift, or forecasting. Designed to be safe to leave on with minimal review.
- **Plus** — Main product tier for SMBs and MSPs with a real fraud surface. Adds anomaly detection, drift detection, forecasting, and per-tenant sensitivity tuning with audit. Operator-facing CLI and effective-parameter report included.
- **Enterprise** — Multi-tenant MSP fleets, mid-market clients with finance-heavy operations, and regulated industries. Adds tenant-fleet aggregation, campaign clustering, full autonomy guardrails, integrity checks, and longer focus windows.

### Capability matrix

| Capability | Essentials | Plus | Enterprise |
|---|:---:|:---:|:---:|
| Fraud scoring (vendor / invoice / impersonation / lookalike / wire pressure / behavior) | Yes | Yes | Yes |
| Ransomware-precursor overlay (attachment / URL / body) | Yes | Yes | Yes |
| Monthly leadership summary | Yes | Yes | Yes |
| Daily digest | Optional | Yes | Yes |
| Recommended action label (`safe` / `needs_review` / `block`) | Yes | Yes | Yes |
| Evidence-package support | Basic | Full | Full + chain export |
| Sandbox training pit (Red battery + weakness reports) | No | Yes | Yes |
| Mutation engine specialisation (sandbox-only) | No | Yes | Yes |
| Signed-policy promotion pipeline | Read-only | Read-only | Read-only |
| Per-tenant sensitivity overrides (Phase 1.4 lift keys) | No | Yes | Yes |
| Operator override CLI (create / pause / revoke / effective / audit) | No | Yes | Yes |
| Effective-parameter report (Markdown / JSON) | No | Yes | Yes + Blackboard append |
| Anomaly detection | No | Yes | Yes |
| Drift detection | No | Yes | Yes |
| ARIMA forecasting | No | Yes | Yes |
| Campaign clustering | No | No | Yes |
| Tenant-fleet risk aggregation | No | No | Yes |
| Trend orchestration agent | No | No | Yes |
| Source-classifier + integrity-check agents | No | No | Yes |
| Quality-score + baseline-model agents | No | No | Yes |
| Drift-guardrail agent | No | No | Yes |
| RBAC enforcer agent (human-role RBAC) | No | No | Yes |
| Kill switch (operator-controlled) | Yes | Yes | Yes |
| Cross-tenant rejection (governance) | Yes | Yes | Yes |
| One-hour defensive training loop on trigger | No | Yes (gated) | Yes (gated) |

### Tier inclusion rules

- **No tier** may block, quarantine, delete, remediate, fetch URLs, execute attachments, or apply production policy without operator approval. These boundaries are runtime guardrails (Guardrail 11, kill switch, signed promotion pipeline), not pricing levers.
- **No tier** removes audit trail or kill-switch capability. Audit and kill-switch are floor capabilities for all tiers.
- **No tier** alters the eligible per-tenant override keys. Only `fraud_risk_floor_lift`, `attachment_risk_floor_lift`, and `url_obfuscation_floor_lift` are exposed.

### Tier scoping suggestions (operator guidance)

| Buyer profile | Suggested tier |
|---|---|
| SMB owner-operator, light email volume, basic awareness training in place | Essentials |
| SMB with active finance team, wire / vendor risk, MSP managed | Plus |
| Multi-client MSP, finance-heavy SMB fleet, regulated industries, insurance reporting need | Enterprise |

### Recommended discovery alignment per tier

- **Essentials buyers** typically need monthly visibility, not real-time tuning. Position around the leadership summary and recommended-action labels.
- **Plus buyers** typically want a fraud-trend story per quarter plus operator-tunable sensitivity per client. Position around the effective-parameter report, per-tenant override CLI, and the closed sandbox-to-production training loop.
- **Enterprise buyers** typically need tenant-fleet aggregation, campaign clustering, and full autonomy-guardrail agents. Position around the Trend_Orchestrator + RBAC_Enforcer + Drift_Guardrail layer and the multi-tenant isolation hardening already implemented.

### Operator note

Tier matrix is **GTM / packaging** language. Internal RBAC and agent enablement live in `Autonomous_Orchestration/agent-enablement-map-per-tier.md` (master matrix) and `Autonomous_Orchestration/trigger-routing-table-per-tier.md` (trigger routing). This product-sheet section is the buyer-facing view; the runtime view stays under `Autonomous_Orchestration/` to avoid two places of truth.

## Suggested Discovery Questions

- Who approves vendor banking changes today?
- What happens when an invoice arrives from a new sender?
- Do wire transfers require a second person to approve?
- Has the team seen fake invoices, lookalike domains, or executive impersonation attempts?
- Do you need better documentation for cyber-insurance renewal?

## Safe Claim Boundary

Use:

- "NorthStar identifies and reports suspicious email-fraud patterns."
- "NorthStar helps teams review high-risk payment and impersonation emails."
- "NorthStar provides evidence-friendly reporting for leadership and operators."

Avoid:

- "NorthStar stops all phishing."
- "NorthStar guarantees fraud prevention."
- "NorthStar quarantines malicious email."
- "NorthStar replaces finance approval controls."

## Next Product Step

Pair this product sheet with the Month 6 per-tenant override surface and the effective-parameter report so MSPs can safely tune sensitivity by client profile, evidence the tuning in monthly reviews, and keep the global governance model intact.

## Last Updated

2026-05-22 — added Essentials / Plus / Enterprise tier matrix aligned to runtime tier vocabulary.

