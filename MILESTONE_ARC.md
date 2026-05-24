# NorthStar + SwarmCommand — Milestone Arc

**Purpose:** Multi-year milestone tracker. Distinguishes weekly tasks (`PROGRESS.md`) from quarterly engineering (`PROJECT_HANDSHAKE.md`) from **multi-year stage milestones** that the product is actually walking toward.

**Update rule:** When a milestone closes, mark it ✅ with date and proof link. When a new milestone is added, attach a clear "done when" criterion. Do not let aspirational items sit without one.

**See also:** `VISION.md` (the thesis), `THIRTY_DAY_PLAN.md` (current 30-day revenue push), `REVENUE_MAP.md` (funding plan).

**Last reviewed:** 2026-05-23

---

## Stage A — Analyze + Recommend (Now → 12 months)

The product analyzes threats and produces evidence MSPs can defend to a client. No autonomous defensive action yet.

### Engineering milestones

| # | Milestone | Done when | Status |
|---|---|---|---|
| A1 | Inbox Shield scoring runtime | Locked prompt, schema, scoring path, ≥400 tests green | ✅ DONE (472 tests, 2026-05-22) |
| A2 | Eval harness with pass gate | 40-case fraud-eval gate runs, full report emitted | ✅ DONE (Phase 1.1 gate, 2026-05-21) |
| A3 | Ransomware precursor overlay | Attachment + URL + body-language detectors merged into scoring | ✅ DONE (Month 3, 27 tests) |
| A4 | Sandbox training pit | 4 Red profiles, ≥100 cases/profile, byte-deterministic | ✅ DONE (Month 4, 38 tests) |
| A5 | Mutation engine + signed promotion pipeline | Close-the-loop test green, 3 fraud-specialized MutationKind values | ✅ DONE (Month 5, 22 tests) |
| A6 | Per-tenant override surface | Local JSON + audit JSONL + operator CLI + effective-parameter report | ✅ DONE (Month 6, 15+9+18 tests) |
| A7 | Autonomous trigger scanner v1 | Read-only drift detection, emits trigger packets with full forbidden-action list | ✅ DONE (2026-05-22, 10 tests) |
| A8 | Vendor-invoice recall floor | Full 40-case `grok-4` gate PASS verdict | ⚠️ PARTIAL (per-case 5/5 PASS post-patch; full rerun deferred for budget) |
| A9 | First MSP-facing pilot deliverable | One MSP receives Effective Parameter Report + signed evidence package for one tenant | ⚠️ ARTIFACT READY 2026-05-23 — `1. Business_Operations/Client_Documents/MSP_Discovery_Evidence_Package.md` is the send-ready bundle and `1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md` is the real generated report proof; closes fully when first MSP actually receives it |
| A10 | First paid client (any form) | $300+ invoice issued for AI engineering or eval work | ⏳ PER `THIRTY_DAY_PLAN.md` |
| A11 | First MSP retainer | Monthly recurring agreement with an MSP for Inbox Shield-derived service | ⏳ Q3 2026 target |

### Revenue milestones

| # | Milestone | Done when | Status |
|---|---|---|---|
| AR1 | First $1 earned | Any external payment received | ⏳ |
| AR2 | First $300 delivered | Per THIRTY_DAY_PLAN.md "real win" | ⏳ |
| AR3 | First $1k month | Single calendar month with $1k+ received | ⏳ |
| AR4 | First MSP discovery call landed | 30-min conversation with an MSP owner about fraud risk | ⏳ |
| AR5 | 10 MSP discovery calls completed | Per REVENUE_MAP.md Lane 3 discovery program | ⏳ |
| AR6 | First pilot MSP signed | Free or paid pilot, signed authorization | ⏳ |
| AR7 | Survival income secured | Local employment + wage subsidy covers monthly burn | ⏳ |

### Documentation milestones

| # | Milestone | Done when | Status |
|---|---|---|---|
| AD1 | Customer-facing product sheet with SMB tiers | Essentials / Plus / Enterprise matrix landed | ✅ DONE 2026-05-22 |
| AD2 | Operator runbooks | Tenant override + effective report runbooks complete | ✅ DONE 2026-05-22 |
| AD3 | LLM governance framework | Policy + system prompt template + traceability matrix | ✅ DONE 2026-05-20 |
| AD4 | Stage A → B → C vision doc | `VISION.md` lands | ✅ DONE 2026-05-23 |
| AD5 | MSP-facing one-page pitch | One-page PDF or markdown explaining Inbox Shield to an MSP owner | ⏳ NEXT |
| AD6 | Discovery-call script | Script for cold/warm MSP discovery conversations | ⏳ PER REVENUE_MAP |

---

## Stage B — Auto-Defend Obvious, Escalate Ambiguous (12–24 months)

The product begins to take autonomous defensive action on high-confidence threats while escalating ambiguous cases to a human. First real recurring revenue.

### Engineering milestones

| # | Milestone | Done when |
|---|---|---|
| B1 | Action authorization tiering spec | Each defensive action classified: auto, escalate, operator-required |
| B2 | First live connector | Working integration with Microsoft 365 OR Google Workspace |
| B3 | Auto-quarantine path | High-confidence threats auto-quarantined with full audit |
| B4 | Auto-rollback path | Any autonomous action reversible by operator with one CLI call |
| B5 | Adversarial robustness layer v1 | Mutation engine refuses suspicious training signals |
| B6 | Production-side continuous learning loop | New attack pattern Monday → defended Friday, fully audited, signed |
| B7 | Cross-tenant signature sharing protocol | Spec for sharing patterns across tenants without sharing customer data |
| B8 | First Stage-B pilot deployment | One MSP deployed with auto-quarantine enabled for one tenant |

### Revenue milestones

| # | Milestone | Done when |
|---|---|---|
| BR1 | First $5k month | Single calendar month with $5k+ received |
| BR2 | First MSP recurring contract | Monthly recurring agreement signed |
| BR3 | Three MSP retainers | Three MSPs paying recurring |
| BR4 | First $10k month | Single calendar month with $10k+ received |
| BR5 | First insurer or compliance buyer | Non-MSP enterprise buyer using evidence reports |

### Liability + legal milestones

| # | Milestone | Done when |
|---|---|---|
| BL1 | Autonomous-action MSA template | Master Service Agreement covering MSP indemnification for auto-actions |
| BL2 | E&O insurance secured | Errors & Omissions coverage for autonomous defensive action |
| BL3 | First incident postmortem | Real incident handled end-to-end including any false-positive remediation |

---

## Stage C — Self-Evolving Defense Swarm (3–5 years)

The product is a multi-surface autonomous defensive swarm with continuous learning, kill-switch-bounded autonomy, and a real moat.

### Engineering milestones

| # | Milestone | Done when |
|---|---|---|
| C1 | Threat-intel ingestion agent | Live pulls from 3+ feeds (CISA KEV, abuse.ch, MITRE ATT&CK, etc.) into Red battery |
| C2 | Second defensive surface live | Auth / identity / endpoint detection live alongside email |
| C3 | Third defensive surface live | Two more surfaces (web, file, network) |
| C4 | Swarm orchestrator in production | Multiple agents coordinating via Blackboard for compound detections |
| C5 | Cross-tenant intelligence shared at scale | Pattern sharing with isolation across 50+ tenants |
| C6 | Continuous evolution observable | Quarterly weakness reports show measurable detection improvement |
| C7 | Full kill-switch + rollback drill | End-to-end test where operator pulls switch mid-attack, rolls back, audits |

### Revenue milestones

| # | Milestone | Done when |
|---|---|---|
| CR1 | $100k ARR | Annualized recurring revenue crosses $100k |
| CR2 | First sub-MSP white-label | Another security vendor embeds NorthStar |
| CR3 | $1M ARR | Annualized recurring revenue crosses $1M |
| CR4 | Acquisition conversation OR Series A | Strategic interest from CrowdStrike / Sophos / Microsoft / Sentinel OR institutional funding round |

---

## Stage-Crossing Watchlist

These items don't belong to any single stage but block stage transitions if ignored.

| Item | Why it matters | First needed by |
|---|---|---|
| Disaster-recovery plan for Blackboard | If audit log is lost, autonomy must halt | Stage B |
| Independent security audit / pen test | Buyers will ask. Pre-empt. | Stage B |
| SOC 2 readiness assessment | Required for enterprise / MSP-of-MSP buyers | Stage B → C |
| Open vs. closed-source policy decision | Affects MSP trust + competitive posture | Stage C |
| Co-founder or first hire | Single-operator scaling limit is real | Stage B mid |

---

## Status Summary (2026-05-23)

- **Stage A engineering:** 7 of 11 done, 1 partial, 3 pending
- **Stage A revenue:** 0 of 7 done — this is the focus per `REVENUE_MAP.md`
- **Stage A documentation:** 4 of 6 done
- **Stage B:** Not started — earliest realistic begin is post-AR2 (first $300 delivered)
- **Stage C:** Architecture sketched, no implementation

**Honest read:** Stage A engineering is genuinely ahead of where most solo-built security products are at this stage. Stage A revenue is at zero. The bottleneck for the next 90 days is not more engineering. It is conversations with buyers.
