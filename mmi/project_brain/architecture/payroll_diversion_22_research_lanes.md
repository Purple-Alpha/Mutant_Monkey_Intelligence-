# #22 Payroll Diversion — Research Packet (MMI-DEC-258 hold)

**Date:** 2026-06-27  
**Lane:** `RESEARCH` (Window B — cold feedstock)  
**Authority:** Matt frontier directive. **Not** build authorization. **Not** §11.

**Contract stub:** `4. Product_Roadmap/Payroll_Diversion_Agent_Design_Contract_Deep_Dive.md` (DRAFT pre-§11)

---

## Question

What should scoreboard **#22 Payroll Diversion** become, given adjacent governed agents and existing routing stubs that currently mis-map payroll cases to vendor-payment surfaces?

| Surface | Status | Role |
|---------|--------|------|
| **#22 Payroll Diversion** | `NOT_STARTED` · `NEEDS_BUILD_AUTH` | Direct-deposit / employee payroll diversion detection |
| **#14 Payment Change Detection** | `GOVERNED_AGENT` ES1 | Vendor-scoped FSL / Vendor Baseline Store payment-destination deltas |
| **#20 Financial Exposure** | `RECLASSIFY` | No standalone exposure detector — FSL amount/exposure not governed here |
| **#21 Executive Impersonation** | `GOVERNED_AGENT` ES1 | Executive identity spoof + pressure (`executive_impersonation_pattern`) |
| **#84 ReconciliationAgent** | `GATED` ES2 | Sole verdict producer — consumes Layer 1 `CanonicalEvidenceLedger` contributions |
| **`mission_context_agent.py`** | Routing debt | `payroll_diversion` case type currently routes to `#14` + verification — **must change when #22 is built** |
| **`risk_triage_agent.py`** | Axis stub | `payroll_diversion` → `wire_anomaly` axis floor 75.0 — awaits `#22` fact ref |

---

## Matt's scope (authoritative for this research pass)

### Product surface

**#22 Payroll Diversion Agent** detects **employee payroll diversion** — scams that redirect an employee's wages via direct-deposit or payroll-instruction change, whether the ask arrives by email to payroll/HR or is corroborated by an HRIS bank-account delta.

**Core boundary:** **employee payroll destination** change detection, not vendor payment destination change (#14), not executive identity spoof (#21), not dollar exposure estimation (#20).

### Lane 1 — Email-side payroll diversion *(ES1 Synthetic in-scope)*

| Signal class | Examples | Output shape |
|--------------|----------|--------------|
| Payroll-change vocabulary | "update direct deposit", "change bank account for payroll", "new routing for [employee]" | Closed facts only — no verdict |
| Target mailbox context | Inbound to `payroll@`, `hr@`, or caller-owned payroll mailbox roster | `payroll_mailbox_target` observation |
| Employee reference | Named employee in change request (caller-owned employee roster match) | `employee_payroll_change_reference` |
| Banking detail in body | Routing/account/IBAN embedded in payroll-change ask | `employee_payroll_signal_type:*` (employee-scoped enum — **not** `#14` vocabulary) |
| Payroll timing pressure | "before next payroll run", "by cutoff", "today before 5pm" paired with change ask | `payroll_timing_pressure` |
| Closed pattern fire | Vocabulary + (employee ref OR banking detail OR payroll mailbox target) | `payroll_diversion_pattern` |

**Boundaries:** Facts only. No block/hold/deny. No payment execution. No HRIS write. No vendor-domain scope.

### Lane 2 — HRIS + bank-account deltas *(ES2 Supervised — declared in contract, not ES1 build)*

| Signal class | Examples | Source | Output shape |
|--------------|----------|--------|--------------|
| HRIS bank account change | Employee self-service or admin edit to DD instructions | HRIS change-event feed (signed integration contract) | `hris_employee_bank_account_delta` |
| Baseline compare | New/expired employee payroll-destination hash vs per-tenant Employee Payroll Baseline | Hash-only store (new primitive at build) | `new_employee_payroll_destination_signal` / `expired_employee_payroll_destination_signal` |
| Payroll-run window | Known payroll cutoff within N hours (caller-owned calendar) | Tenant payroll calendar roster | `payroll_run_imminent_window` (context fact for `#84` timing weight) |
| Correlation-only | HRIS delta with no matching authorized change ticket | Pair HRIS fact + email absence | `unauthorized_payroll_destination_change` *(synthesis fact — Layer 2 only when both surfaces wired)* |

**Boundaries:** ES1 build does **not** implement Lane 2. Contract declares Lane 2 inputs so ES2 promotion path is explicit. No raw account numbers in DER — hash-only baseline per Vendor Baseline Store precedent.

### Lane 3 — Privacy / data minimization *(cross-cutting)*

1. No raw employee bank account / routing strings in `AgentContribution` or DER.
2. Employee names in contributions: **closed roster token IDs only** at ES1 (`employee_ref:<token>`) — not display names in facts unless Matt signs ES2 exception.
3. Tenant isolation mandatory — employee baseline never crosses tenants.
4. HRIS PII stays in integration boundary — agent sees change-event class + hash + employee token only.

---

## Evidence / DER sketch — triggers → ReconciliationAgent (#84)

`ReconciliationAgent` does **not** read raw email or HRIS. It reads **Layer 1 contributions** from `CanonicalEvidenceLedger` for one `tenant_id` + `email_id`, then runs R1/R2/R3 ensemble → single `VerdictLedger` entry.

### Path (conceptual)

```
Inbound EMAIL_INBOUND (+ optional HRIS change-event at ES2+)
    → #22 PayrollDiversionAgent.analyze()  [Layer 2 Detection]
    → AgentContribution.observed_facts (closed vocabulary)
    → CanonicalEvidenceLedger (tenant-isolated, email_id keyed)
    → #84 ReconciliationAgent.analyze(tenant_id, email_id, lung_state)
    → VerdictLedger (UNANIMOUS / MAJORITY / ESCALATE)
```

### #22 closed fact vocabulary (proposed — feeds #84)

| Fact | Trigger | Layer | #84 consumer note |
|------|---------|-------|-------------------|
| `payroll_diversion_pattern` | Email Lane 1 pattern fire (vocabulary + corroborator) | 2 | R1 `wire_anomaly` axis weight via `payroll_diversion` ref (existing floor 75) |
| `direct_deposit_change_request` | DD/payroll-update vocabulary in body | 2 | Pattern input for R2 |
| `payroll_vocabulary_signal` | Payroll-specific lexicon without full pattern | 2 | Weak signal — never alone sufficient for verdict |
| `payroll_mailbox_target` | Recipient matches caller payroll mailbox roster | 2 | Case-type context |
| `employee_payroll_change_reference` | `employee_ref:<token>` from caller roster | 2 | Ties ask to known employee slot |
| `employee_payroll_signal_type:routing_number` | Employee-scoped banking extract | 2 | **Not** `#14` `payment_signal_type:*` |
| `employee_payroll_signal_type:account_number` | Same | 2 | Employee enum only |
| `employee_payroll_signal_type:iban` | Same | 2 | Employee enum only |
| `payroll_timing_pressure` | Urgency paired with payroll-change ask | 2 | Amplifier for R1/R2 |
| `new_employee_payroll_destination_signal` | Baseline compare — first-seen employee DD hash | 2 | Lane 2 / ES2+ when store exists |
| `expired_employee_payroll_destination_signal` | Baseline compare — stale DD hash resurfaced | 2 | Lane 2 / ES2+ |
| `hris_employee_bank_account_delta` | HRIS change-event (no email required at ES2) | 2 | Lane 2 — may pair with email_id from case linker |
| `payroll_run_imminent_window` | Cutoff within configured window | 2 | Timing context — not fraud proof |
| `payroll_diversion_finding_count:<n>` | Bounded count | 2 | DER stability |

### DER fields (#22 contribution only)

| DER field | #22 content |
|-----------|-------------|
| `observed_facts` | Closed vocabulary above |
| `interpretations` | **none** |
| `assumptions` | Caller employee roster + payroll mailbox roster current; ES1 email-only |
| `missing_evidence` | No out-of-band HR verification; no payroll-system auth proof; no fraud declaration |
| `recommended_verification` | **none** at Layer 2 |
| `final_outcome_contribution` | Payroll diversion facts only |

### Negative pair (must not fire #22 alone)

- `lh-002` Legit HR / Payroll Calendar Notice — payroll vocabulary, **no** DD change, internal sender → no `payroll_diversion_pattern`
- Legitimate employee self-service DD change with authorized HRIS ticket — Lane 2 only; ES2 supervised samples

---

## Cross-link audit — zero leakage into #14 / #20 / #21

| Adjacent | Their surface | #22 must NOT | #22 MAY correlate |
|----------|---------------|--------------|-------------------|
| **#14 Payment Change** | `assess_financial_state_delta` + Vendor Baseline Store; `vendor_domain`; `new_payment_destination_signal`; `payment_signal_type:*` | Call FSL; mutate vendor store; emit vendor payment facts; scope by vendor domain | Same email may also be vendor fraud — **independent facts** on ledger |
| **#20 Financial Exposure** | `RECLASSIFY` — exposure/amount estimation inside FSL overlay | Emit exposure estimates, dollar amounts, prioritization scores | None — #22 is not an exposure agent |
| **#21 Executive Impersonation** | Principal roster; `executive_impersonation_pattern`; identity mismatch + pressure | Emit exec impersonation facts; reuse principal roster as authority proof | `ei-002` may fire **both** #21 and #22 — ensemble resolves |
| **#19 Dual-Approval** | Verification layer | Authorize payroll change | None at ES1 |
| **#11 Known-Good Contact** | Vendor contact verification | Verify employee DD legitimacy | Future Verification pairing only |

### Routing debt (hot fix at #22 build — not this research pass)

```text
mission_context_agent.py — payroll_diversion required_evidence today:
  ("payment_change_detection", "verification_outcome")  ← WRONG for #22

Target after #22 build:
  ("payroll_diversion_detection", "verification_outcome")
  and/or executive_impersonation when ei-pattern overlap
```

### Vocabulary isolation proof

| Forbidden in #22 facts | Owner |
|------------------------|-------|
| `new_payment_destination_signal` | #14 |
| `payment_signal_type:*` | #14 |
| `payment_delta_finding_count:*` | #14 |
| `executive_impersonation_pattern` | #21 |
| `recommended_risk_floor`, `recommended_action` | Scoring overlay / Command |
| Raw routing/account/IBAN strings | Data minimization |

---

## #22 ↔ #84 verdict posture

| Rule | Detail |
|------|--------|
| #22 never issues verdict | Layer 2 Detection only |
| #84 never re-reads email/HRIS | P4 contract lock |
| `payroll_diversion_pattern` alone | **Insufficient** for HIGH_RISK — R2/R3 still apply |
| `payroll_diversion` + `executive_impersonation_pattern` | Strong ensemble case (`ei-002` class) |
| HRIS delta without email (ES2) | Requires separate case-linking contract before #84 invocation |
| `spam_signal_only` path | Unrelated — #84 §8 delivery surface |

---

## Recommended next steps (operator)

1. **Matt reviews** this research packet + contract DRAFT stub.
2. **Matt confirms** ES1 scope: email-only Lane 1 + employee-scoped baseline primitive design (hash-only).
3. **Pre-§11 gate** on formal contract file at hot `4. Product_Roadmap/`.
4. **Separate build authorization** after §11 — detector + `PayrollDiversionAgent` wrapper.
5. **Hot routing fix** bundled with build: `mission_context_agent` payroll_diversion → `#22` agent ref.

---

## Boundaries (this document)

- Research / design only  
- No build authorization  
- No §11 signing  
- No scoreboard lifecycle change  
- No production dispatch  
- No AUTH-5  
- No hot-tree edits from Window B (feedstock only until Matt merges)

---

## Related

- `4. Product_Roadmap/Payroll_Diversion_Agent_Design_Contract_Deep_Dive.md` (DRAFT stub)  
- `4. Product_Roadmap/Payment_Change_Detection_Agent_Design_Contract_Deep_Dive.md` (#14 boundary)  
- `4. Product_Roadmap/Executive_Impersonation_Agent_Design_Contract_Deep_Dive.md` (#21 boundary)  
- `4. Product_Roadmap/Phase4_ReconciliationAgent_Contract.md` (#84 verdict surface)  
- `4. Product_Roadmap/Phase_1_1_Eval_Dataset_Design_Grid.md` (`ei-002`, `lh-002`)  
- Scoreboard #22, #14, #20, #21, #84  
- MMI-DEC-258 (research hold — this packet)
