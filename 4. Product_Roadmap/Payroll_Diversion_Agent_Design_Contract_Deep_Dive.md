# Payroll Diversion Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_22_PAYROLL_DIVERSION_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** **DRAFT (pre-§11).** Formal placement MMI-DEC-262 (feedstock unpark MMI-DEC-261). Step 00 validation target. Not §11 signed. Not build authorization. Not production dispatch.

**Scope:** Scoreboard #22 — **employee payroll / direct-deposit diversion** only. Vendor payment destination change (#14), financial exposure estimation (#20), and executive identity spoof (#21) explicitly excluded.

**Owner:** Matt Nichol

**Candidate:** #22 — Payroll Diversion (direct-deposit change scams)

**Track:** BREADTH · Team 3 Vendor-payment / BEC (employee payroll sub-case)

**Lane:** Agent Design Contract (CONTRACT_DRAFT feedstock MMI-DEC-261)

**Authority repo:** `/home/socialarchitect/northstar`

**Source-of-truth links:**
- `mmi/project_brain/architecture/payroll_diversion_22_research_lanes.md` (scope + cross-link audit + DER sketch)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Payment_Change_Detection_Agent_Design_Contract_Deep_Dive.md` (#14 — vendor FSL boundary; do not merge)
- `4. Product_Roadmap/Executive_Impersonation_Agent_Design_Contract_Deep_Dive.md` (#21 — exec identity boundary)
- `4. Product_Roadmap/Phase4_ReconciliationAgent_Contract.md` (#84 — verdict consumer)
- `4. Product_Roadmap/Phase_1_1_Eval_Dataset_Design_Grid.md` (`ei-002` positive, `lh-002` negative)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#22 row)
- `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (SPARK #22 NET-NEW)

---

## Agent Design Contract block

**Boundary:** This contract governs the future Payroll Diversion **agent wrapper** (`PayrollDiversionAgent`) and its underlying **employee-scoped** payroll-destination detector. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** govern, extend, or invoke `assess_financial_state_delta` / Vendor Baseline Store (#14), executive principal roster logic (#21), or financial exposure overlays (#20).

| Field | Value |
|---|---|
| Agent name | Payroll Diversion Agent (`PayrollDiversionAgent`) |
| Swarm inventory ID | #22 — Payroll Diversion |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Vendor-payment / BEC — **employee payroll diversion** (direct-deposit / payroll-instruction change) |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Email-only Lane 1 validation. Lane 2 HRIS integration is **declared but not built** at ES1. NOT in `build_default_registry` / no production dispatch at ES1. |
| Role | Produce facts-only employee payroll diversion evidence by detecting direct-deposit / payroll-change asks in inbound email (ES1) and, at ES2+, comparing employee payroll-destination hashes against a per-tenant Employee Payroll Baseline Store and optional HRIS bank-account delta events. |
| Boundary | Employee payroll destination scope only. The only authorized ES1 mutation is the signed detector's employee payroll-destination baseline ingest in check-before-ingest order over a **closed employee payroll signal enum** (separate from #14 vendor enum). Must not decide fraud, approve/deny payroll change, execute payment, or issue verdict. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/hold payroll; no vendor-domain scope; no `assess_financial_state_delta`; no Vendor Baseline Store access; no executive principal roster authority; no financial exposure / dollar amount estimation; no HRIS write; no out-of-band verification execution; no `executive_impersonation_pattern` emission; no `payment_signal_type:*` / `new_payment_destination_signal` emission; no default-registry registration; no production dispatch at ES1; no buyer-facing claim. |
| Inputs | ES1: one `EMAIL_INBOUND` Blackboard record via `MissionContext.source_record_id`; reads `recipient`, `sender`, `subject`, `body_plain`, and `attachments[*].extracted_text`; caller-owned payroll mailbox roster and employee token roster at construction; caller-owned aware `now`; no HRIS feed at ES1. ES2+ declared (not ES1 build): signed HRIS change-event feed (`hris_employee_bank_account_delta`), payroll cutoff calendar, Employee Payroll Baseline Store (hash-only, tenant-scoped) — requires separate ES2 promotion. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = closed payroll-diversion vocabulary (see §3). No verification/challenge/evidence/score field. |
| Evidence emitted | Closed indicators: `payroll_diversion_pattern`, `direct_deposit_change_request`, `payroll_vocabulary_signal`, `payroll_mailbox_target`, `employee_payroll_change_reference`, `employee_payroll_signal_type:*`, `payroll_timing_pressure`, bounded counts. ES2+: `new_employee_payroll_destination_signal`, `expired_employee_payroll_destination_signal`, `hris_employee_bank_account_delta`, `payroll_run_imminent_window`. No raw banking strings, employee display names, risk floors, or actions. |
| Data minimization | No raw account/routing/IBAN strings; no employee display names in facts (use `employee_ref:<token>` only); no vendor domain; no email body in contribution; `inputs_digest` = SHA-256 of boundary inputs only. Employee Payroll Baseline Store hash-only at ES2+. |
| Tenant isolation | Reads tenant Blackboard path only; employee baseline and rosters are tenant-scoped; tenant A employee slots never affect tenant B. |
| Two-pass role | Pass 1 Detection only. `challenge()` returns `None`. |
| Decision Evidence Record contribution | `observed_facts`: closed payroll vocabulary; `interpretations`: none; `assumptions`: caller rosters current for tenant; ES1 email-only; `missing_evidence`: no HR out-of-band verification, no payroll-system auth proof, no fraud declaration; `recommended_verification`: none at Layer 2; `final_outcome_contribution`: payroll diversion facts only; `retest_or_learning_record`: per template §6.5 (`ei-002` regression mandatory). |
| Human review trigger | None authored by this agent. Commander / Verification own routing. |
| Verification trigger | None at Layer 2. May pair with #19 Dual-Approval at Verification layer when built. |
| Scoring / action posture | Facts-only. No `recommended_risk_floor`, `recommended_action`, or axis scores in contribution. Existing `risk_triage_agent` `payroll_diversion` axis stub consumes downstream refs — not republished by this agent. |
| Default rollout | ES1: not in `build_default_registry`; explicit callers/tests only. |
| Autonomous action | None. `autonomous_action_allowed = False`. |
| Promotion conditions | Template §6.2. ES1→ES2 requires Lane 2 design review, HRIS integration contract, supervised samples including `lh-002` negative pair. |
| Demotion conditions | Template §6.3. |
| Retest evidence | Template §6.5. `ei-002` and `lh-002` permanent regression bar. |
| Calibration requirement | ES1 email-only detector calibration deferred to build lane review; ES2 HRIS integration calibration is separate from wrapper Evidence Stage promotion per template §6.5. |
| Failure modes | See §5. |
| Required tests | `tests/test_payroll_diversion_agent.py` + detector tests when implemented. |
| Audit requirements | `complete_gate.py` on build slice. |
| Signed-spec dependencies | This contract, Agent Design Contract Template, `VISION.md`, Phase 4 Reconciliation contract (#84 consumer), Vendor Baseline Store spec (contrast only — do not import). |
| Build Authorization dependency | §11 signature places contract only. Implementation requires explicit Matt build authorization + `NEEDS_BUILD_AUTH` clearance on scoreboard. |

---

## §0 Purpose

Place a full Agent Design Contract for swarm #22 Payroll Diversion — the **employee payroll destination** detector absent from the vendor-scoped #14 FSL surface and distinct from executive identity spoof #21. Closes the NET-NEW gap on SPARK Team 3 inventory. Defines facts that feed `CanonicalEvidenceLedger` for `ReconciliationAgent` (#84) ensemble resolution.

**Does not** implement detector or wrapper in this draft slice.

---

## §1 Scope

### In scope
- Agent Design Contract block for `PayrollDiversionAgent`.
- ES1 email-only Lane 1 detection design.
- Declared ES2 Lane 2 HRIS + Employee Payroll Baseline Store boundary (design only).
- Cross-link appendix (#14 / #20 / #21 / #84).
- Closed fact vocabulary for DER / evidence ledger.
- Routing correction target: `mission_context_agent` `payroll_diversion` → `payroll_diversion_detection` agent ref.

### Out of scope
- Vendor Baseline Store / FSL / #14 payment-destination logic.
- Executive principal roster / `executive_impersonation_pattern` (#21).
- Financial exposure / amount estimation (#20 RECLASSIFY surface).
- ReconciliationAgent voter logic changes (#84).
- Default registry / production dispatch at ES1.
- HRIS integration implementation at ES1.
- Autonomous payroll hold/block/deny.

---

## §2 Locked Design Decisions (candidate — confirm at §11)

- **D1 — Identity.** Payroll Diversion is Layer 2 Detection, Authority Level 3, VISION Stage A, Evidence Stage 1 at signing. `agent_id = payroll_diversion_001`.
- **D2 — Employee-scoped stateful boundary.** Separate from #14. Authorized ES1 mutation (when baseline store lands at ES2) is employee payroll-destination hash ingest only, check-before-ingest, over closed enum: `routing_number`, `account_number`, `iban` (employee payroll context — not vendor `payment_signal_type`).
- **D3 — No FSL / no vendor store.** Must not call `assess_financial_state_delta`, `check_signal`, or `ingest_signal` on Vendor Baseline Store. No `vendor_domain` input.
- **D4 — Facts-only contribution.** Closed payroll vocabulary only. No score, risk floor, action, interpretation, raw banking strings, or employee display names.
- **D5 — ES1 input surface.** `EMAIL_INBOUND` via `source_record_id`; caller-owned payroll mailbox roster + employee token roster at construction.
- **D6 — Pattern gate.** `payroll_diversion_pattern` requires payroll-change vocabulary plus at least one corroborator: `employee_payroll_change_reference`, `employee_payroll_signal_type:*`, or `payroll_mailbox_target`. Vocabulary alone is insufficient.
- **D7 — Negative pair.** `lh-002` class (payroll calendar, no DD change) must not emit `payroll_diversion_pattern`.
- **D8 — Persistence + rollout.** Registry-gated `AGENT_CONTRIBUTION`; not in `build_default_registry` at ES1.
- **D9 — Stage A / no autonomy.** No block/quarantine/deny/hold; no payroll execution; no autonomous action.
- **D10 — #84 feed only.** Contributions land on `CanonicalEvidenceLedger` for ensemble consumption; this agent never calls `ReconciliationAgent` directly.
- **D11 — Correlation not duplication with #21.** `ei-002` may produce both `executive_impersonation_pattern` (#21) and `payroll_diversion_pattern` (#22); neither agent suppresses the other.
- **D12 — Tests are ES1 evidence.** Focused suite + `ei-002` / `lh-002` regression before build close.

---

## §3 Data surface and output schema

### ES1 reads
- `EmailInboundPayload.recipient`, `sender`, `subject`, `body_plain`, `attachments[*].extracted_text`.

### ES1 emits (`observed_facts` closed set)
- `payroll_diversion_pattern`
- `direct_deposit_change_request`
- `payroll_vocabulary_signal`
- `payroll_mailbox_target`
- `employee_payroll_change_reference` (format: `employee_ref:<token>`)
- `employee_payroll_signal_type:routing_number`
- `employee_payroll_signal_type:account_number`
- `employee_payroll_signal_type:iban`
- `payroll_timing_pressure`
- `payroll_diversion_finding_count:<n>`

### ES2+ declared (not ES1 build)
- `new_employee_payroll_destination_signal`
- `expired_employee_payroll_destination_signal`
- `hris_employee_bank_account_delta`
- `payroll_run_imminent_window`

### Forbidden emissions (leakage guard)
- `new_payment_destination_signal`, `expired_payment_destination_signal`, `payment_signal_type:*`, `payment_delta_finding_count:*` → **#14 only**
- `executive_impersonation_pattern` → **#21 only**
- `recommended_risk_floor`, `recommended_action`, `requires_out_of_band_verification` → scoring overlay / Command
- Raw financial strings, employee display names, vendor domains, email body

---

## §4 Evidence Stage declaration

- **Current at signature:** Stage 1 — Synthetic. Email-only Lane 1.
- **Stage 2 — Supervised:** Lane 2 HRIS + Employee Payroll Baseline Store + supervised samples; template §6.2 bar.
- **Stage 3 — Production:** Template §6.2 + Drift Watch; no autonomous payroll action authority.

---

## §5 Failure modes

- **Vendor scope creep** — wrapper calls FSL or emits #14 facts. Mitigation: D3 + forbidden vocabulary tests.
- **Executive scope creep** — wrapper emits `executive_impersonation_pattern`. Mitigation: D11 + separate agent tests.
- **Calendar false positive** — `lh-002` fires on payroll vocabulary alone. Mitigation: D6 pattern gate + D7.
- **Raw banking leakage** — account/routing strings in contribution. Mitigation: D4 + data minimization tests.
- **Employee PII leakage** — display names in facts. Mitigation: token-only `employee_ref:<token>`.
- **Verdict creep** — agent issues block/hold or calls #84. Mitigation: D9/D10.
- **Routing debt** — `mission_context` still points payroll cases to #14. Mitigation: hot build bundles routing fix.
- **HRIS premature** — ES1 build wires HRIS without ES2 promotion. Mitigation: ES1 scope lock in §1.

---

## §6 Required tests (ES1 build bar)

1. `PayrollDiversionAgent` satisfies `Agent` protocol.
2. `ei-002` class email emits `payroll_diversion_pattern` + supporting facts.
3. `lh-002` class email emits no `payroll_diversion_pattern`.
4. Payroll vocabulary without corroborator emits no `payroll_diversion_pattern`.
5. Employee token roster match emits `employee_payroll_change_reference` without display name in facts.
6. Banking detail in body emits `employee_payroll_signal_type:*` not `payment_signal_type:*`.
7. Payroll mailbox roster match emits `payroll_mailbox_target`.
8. No financial signal → no pattern fire.
9. Missing `source_record_id` / wrong record type fails closed.
10. Tenant isolation on rosters and future baseline store.
11. No `assess_financial_state_delta` / Vendor Baseline Store calls (spy test).
12. No `executive_impersonation_pattern` emission.
13. `challenge()` returns `None`.
14. Not in `build_default_registry()`.
15. No risk floor / action / raw string leakage in contribution.
16. Contribution persists via `submit_agent_contribution` round-trip.

---

## §7 Cross-link appendix (#14 / #20 / #21 / #84)

| ID | Relationship to #22 |
|----|---------------------|
| **#14** | Disjoint scope. Vendor payment destination vs employee payroll destination. Never share store or fact vocabulary. |
| **#20** | No relationship. #20 RECLASSIFY — no exposure detector to invoke. |
| **#21** | Orthogonal. Identity spoof vs payroll-change content. May co-fire on `ei-002`. |
| **#84** | Downstream consumer only. Reads #22 facts from ledger; #22 never produces verdict. |

Full audit: `payroll_diversion_22_research_lanes.md` § Cross-link audit.

---

## §8 Open before §11

1. Matt confirms ES1 email-only scope + employee-scoped baseline primitive design (hash-only Employee Payroll Baseline Store deferred to ES2).
2. Employee roster token schema frozen (caller-owned, #21 principal roster pattern).
3. Payroll mailbox roster schema frozen (caller-owned).
4. Pre-build gate clean on formal contract file at hot.
5. Routing correction plan accepted (`payroll_diversion_detection` agent ref).

---

## §9 Boundaries (this contract)

- Design / contract draft only until §11
- No build authorization from this document alone
- No production dispatch
- No AUTH-5
- No scoreboard lifecycle change beyond CONTRACT_DRAFT placement

---

## §10 Open Questions (operator-only)

1. **Employee Payroll Baseline Store** — new primitive vs extend `tenant_baseline_ingestion` employee prefixes? Recommendation: **new hash-only store** mirroring Vendor Baseline Store pattern with `employee.payroll_destination.*` keys — ES2 build, not ES1.
2. **HRIS integration** — which HRIS vendors first (Workday, ADP, etc.)? Deferred to ES2 integration contract.
3. **Case linking** — HRIS delta without inbound email: separate `email_id` / case linker required before #84 invocation. Deferred to ES2.

---

## §11 Lockdown Signature

> **UNSIGNED — DRAFT.** Awaiting Matt review of research packet MMI-DEC-258 and explicit §11 authorization.

> Matt Nichol — pending
