# Blackboard-Mesh Governance Foundation — Infrastructure Design Contract (Deep Dive)

**Draft ID:** `MMI_BLACKBOARD_MESH_GOVERNANCE_FOUNDATION_DRAFT`

**Status:** §11 SIGNED 2026-06-27 by Matt Nichol (MMI-DEC-271). Pre-build gate 0/0 MMI-DEC-270. Governs future infrastructure build slices (Mode A ledger gate, Evidence Backer, Crucible failure log). **Not** build until separate Build Authorization. **Not** production dispatch. **Not** AUTH-5. **Not** cryptographic signing (`MMI_CRYPTOGRAPHIC_SIGNING_CONTRACT` remains parked).

**Lane type:** Infrastructure / cross-cutting governance (not a swarm agent scoreboard row).

**Authority repo:** `/home/socialarchitect/northstar`

**Owner:** Matt Nichol

**Governs:** Evidence ledger write boundary, verdict separation, read-only proof layer (Evidence Backer), synthetic crucible failure logging (Phoenix), and authority-leakage mitigations.

**Explicitly does NOT govern:** Live production chaos injection, SIGKILL of Commander agents, or replacement of Matt §11 with machine signature.

---

## §0 INVARIANT — Detect-not-Enact at the Mesh Boundary

The blackboard accepts **observations** only. An observation states a fact; it never states an outcome. Schema-level rejection is the enforcement mechanism — a misbehaving agent must be **physically unable** to post a verdict, clearance, or authority claim on the evidence surface.

**Three ontologies (never merge):**

| Ontology | Question | Write surface |
|----------|----------|---------------|
| Evidence | What was observed? | `CanonicalEvidenceLedger` / `EvidenceLedgerEntry` |
| Verdict | What did reconciliation conclude? | `VerdictLedger` / `ReconciliationVerdict` |
| Authority | Who allowed action? | `MMI_DECISION_LOG.md`, operator signature records |

**Total swarm failure is a data point.** Iterative Crucible Mode treats destructive test outcomes as evidence inputs to contract/schema refinement — not as reasons to restore from unproven backup fiction.

---

## §1 Repo identity correction (mandatory — prevents agent-ID drift)

Other prose may mislabel scoreboard rows. This contract uses **repo-accurate IDs only:**

| Mislabel (reject) | Repo truth |
|-------------------|------------|
| "Chaos Controller #99" | **#99** = Mode Controller **Adversarial Test Suite** (50 MC-ADV IDs; hardens #92) |
| "Integrity Auditor #89" | **#89** = **Blast Radius Controller** ensemble (`GatewayController` + eight components; hardened via #101) |
| "Challenge Agent #67" | **#67** = Rule Improvement (Layer 6 Governance, sandbox proposals). Layer 5 Challenge peers: **#64**, Team 9 (#61–#63), `aggregate_corroboration_agent` |
| "GatewayController #89" as separate from BRC | Gateway is **inside** #89 ensemble row — not a standalone agent # |
| Live "Crucible running" without artifact | **Not authoritative** until `scripts/evidence_backer.py` + crucible harness emit signed reports |

---

## §2 Locked design decisions (BM-D1–BM-D10 — §11 MMI-DEC-271)

- **BM-D1 — Mode A schema gate (structural).** `EvidenceLedgerEntry` top-level keys are exactly the closed Phase 1 Component 1 set — no additions at this contract layer: `agent_id`, `tenant_id`, `email_id`, `evidence_type`, `details`, `confidence`, `timestamp`, `stage` (per `Phase1_Infrastructure_Agent_Design_Contract.md` §3 Component 1). Any forbidden top-level key → reject. Unknown extra top-level keys (including `entry_id`, `schema_version`, or other metadata) → reject until a signed Phase 1 amendment adds them. `StrictModel(extra="forbid")` is necessary but not sufficient.

- **BM-D2 — Mode A schema gate (semantic).** Before evidence ledger append, scan `details` and observation strings for **authority-shadow tokens** from a **version-pinned config** (not inline hard-code). Hit → reject as governance failure; log `agent_id`. `confidence` is observation calibration only — never a release/clearance signal.

- **BM-D3 — Forbidden top-level key set (evidence surface).** Closed reject set includes: `verdict`, `conclusion`, `decision`, `outcome`, `final`, `action`, `route`, `block`, `release`, `approved`, `authorized`, `cleared`, `safe`, `disposition`. Matt confirms no collision with the Phase 1 §3 Component 1 allowlist before §11; implementation reconciliation at Mode A build.

- **BM-D4 — Writer allowlist.** Verdict ledger writable only by ReconciliationAgent path (`reconciliation_agent_001` / Phase 4 contract). All other agents → evidence ledger only. Enforced at **ledger boundary**, not by convention.

- **BM-D5 — Reconciliation is advisory.** `ReconciliationVerdict` prepares the operator package; it does **not** satisfy the human gate. `plain_english_chain` describes evidence; it must not bless. Same authority-shadow scan applies to verdict writes.

- **BM-D6 — Evidence Backer is read-only.** `scripts/evidence_backer.py` proves chain integrity; it never decides, never enacts, never promotes. Output verdict ∈ `{PROVABLE, INCOMPLETE, VIOLATION, NOT_APPLICABLE}` — never soft green.

- **BM-D7 — Phoenix / Crucible is synthetic-first.** Crucible runs use ES1 fixtures, adversarial suites (#99, #101, Team 9), and injected fault catalogs — **not** live SIGKILL of #1 Swarm Commander in production. Leader-silence tests are scripted scenarios with expected fail-closed outcomes.

- **BM-D8 — Fail-closed default.** Unknown schema shape, orphan verdict ref, or shadow token → reject / VIOLATION. Never write-and-flag on the evidence surface.

- **BM-D9 — Crypto parked.** `MMI_CRYPTOGRAPHIC_SIGNING_CONTRACT` is out of scope. §11 here remains non-cryptographic typed-name (LAW 9).

- **BM-D10 — Build trigger.** Infrastructure build authorized only after §11 **and** explicit operator build auth **and** (DEPTH gate open **or** pilot evidence requirement **or** Matt pin).

---

## §3 Data surfaces

### §3.1 Evidence ledger (to formalize — Phase 1 §3 Component 1)

Target: `core/blackboard/canonical_ledger.py` — `EvidenceLedgerEntry` with **exactly** the signed Phase 1 top-level schema:

- `agent_id`, `tenant_id`, `email_id`, `evidence_type` (closed enum per Phase 1), `details`, `confidence`, `timestamp`, `stage`

**Not in Phase 1 schema at this layer:** `entry_id`, `schema_version` — require a signed Phase 1 amendment before any Mode A build may add them.

**Gap to close at build:** formalize ledger module; nested `details` validation; writer allowlist; semantic scan config.

### §3.2 Verdict ledger (to formalize — Phase 4)

Target: `core/blackboard/verdict_ledger.py` — `ReconciliationVerdict`:

- `verdict`, `ensemble_outcome`, voter fields, `contributing_evidence`, `plain_english_chain`, state flags (`lockdown_applied`, `delivery_problem_path`)

**Documentation requirement:** state flags are **not** clearance substitutes (leakage vector #3).

### §3.3 Contract registry (to assemble — read-only index)

Machine-readable index derived from:

- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`
- `4. Product_Roadmap/*_Agent_Design_Contract*.md`
- `mmi/MMI_DECISION_LOG.md`

Fields: `agent_id`, `signed_contract_path`, `§11_status`, `allowed_inputs`, `allowed_outputs`, `forbidden_actions`, `evidence_stage`, `build_authorization_status`, `build_sha`.

### §3.4 Evidence Backer report (to build)

CLI:

```bash
python3 scripts/evidence_backer.py --tenant-id TENANT1 --email-id EMAIL123
```

Graph walk: `EMAIL_INBOUND` → contributions → evidence entries → challenge results (if any) → verdict (if any) → human DEC / gate SHA.

### §3.5 Crucible failure log (to build)

Append-only: `mmi/crucible/CRUCIBLE_FAILURE_LOG.md` (or JSONL sibling).

Each entry: `crucible_run_id`, `failure_class`, `agents_involved`, `evidence_backer_report_sha`, `governance_rule_id`, `phoenix_action` (contract amend / test add / schema tighten).

---

## §4 Implicit authority leakage — four vectors (mitigations)

| Vector | Risk | Mitigation |
|--------|------|------------|
| **#1 Omission-as-safety** | No signals → treated as LOW_RISK | **Target mitigation (Phase 4 amendment — not mandated by this contract):** voters should support `INSUFFICIENT_EVIDENCE` / fail-closed path; no default-safe. Crucible + Evidence Backer flag the live gap until amended. |
| **#2 Confidence-as-clearance** | High `confidence` read as approved | Schema doc + consumer lint; R1 must not be sole clearance path. |
| **#3 Status-flag leakage** | `lockdown_applied: false` read as cleared | Verdict schema doc: state flags ≠ authority. |
| **#4 Unanimous ensemble finality** | `ensemble_outcome: unanimous` → gate satisfied | Label advisory; Evidence Backer flags if consumer treats as authority. |

---

## §5 Phoenix Protocol (Iterative Crucible Mode)

1. **Destruction as discovery** — synthetic fault injection → Evidence Backer report → identify authority leak or logical stutter → amend contract/schema (not vibes patch).

2. **God Mode goal** — tighter swarm logic: more skeptical cross-reasoning, not "smarter" individual prompts alone.

3. **Velocity** — fail-analyze-refactor loop measured in hours requires **automated** Mode A checks + crucible harness + gate reports — not manual narrative.

**Crucible v1 scope (synthetic):**

- Existing adversarial suites: #99 (Mode Controller), #101 (Blast Radius / Gateway)
- Team 9 generators (#61–#63) + #64 failure classification
- Injected faults: evidence poison, leader-silence **scenario** (not production kill), orphaned verdict attempt

**Command spine (#1–#3) in crucible:** **Yes — included in synthetic scenarios** after crucible contract §11. Highest drift value: Mission Context (#2) classify-only under malformed routing input; Swarm Commander (#1) route-only under leader-silence fixture. Expected outcome: **fail-closed**, not proactive continuity bypass.

---

## §6 Required tests (infrastructure build bar)

1. Evidence append rejects forbidden top-level key on `EvidenceLedgerEntry`.
2. Evidence append rejects authority-shadow token inside `details` (version-pinned list).
3. Non-reconciliation `agent_id` cannot append to `VerdictLedger` (boundary enforced).
4. Evidence Backer returns `VIOLATION` on orphan `contributing_evidence` ref.
5. Evidence Backer returns `INCOMPLETE` when human gate required but no DEC record.
6. Omission fixture: sparse contributions → Evidence Backer flags `VIOLATION` or `INCOMPLETE` for omission-as-safety gap; Phase 4 voter fail-closed behavior validated only after signed Phase 4 amendment.
7. Cross-tenant leak fixture → `VIOLATION`.
8. Crucible run appends one `CRUCIBLE_FAILURE_LOG` entry with backer report SHA.
9. Gateway semantic filter + ledger gate do not double-reject benign observation payloads.
10. Regression: existing blast-radius adversarial suite (#101) remains clean after ledger gate wiring.

---

## §7 Cross-link appendix

| ID | Relationship |
|----|--------------|
| **Phase 1** | `CanonicalEvidenceLedger` — P1-D2 append-only |
| **Phase 4 #84** | `ReconciliationAgent` — sole verdict producer; DEPTH GATED |
| **#89 / #101** | Gateway hardening — adversarial proof, not chaos fiction |
| **#99** | Mode Controller adversarial suite — template for crucible automation |
| **#105** | Invariants framework — LAW 9 crypto parked |
| **Aggregate Corroboration** | Layer 5 challenge peer to detectors |
| **MMI_TRANSITION_GATE_MAP** | Tier B infrastructure evidence bar slots after Step 04 |

---

## §8 Open before build (§11 signed — resolve at build authorization)

1. ~~Matt confirms forbidden-key set vs Phase 1 §3 Component 1 allowlist~~ — confirmed at §11 (MMI-DEC-271).
2. Operator decision: reject vs quarantine-and-log on semantic scan hit.
3. Authority-shadow token list location + version pin (`mmi/config/authority_shadow_tokens_v1.json` candidate).
4. `details` closed sub-schema per `evidence_type` vs observation-bag + Gate 2 only.
5. ~~Pre-build gate on this contract file (Codex 0/0)~~ — PASS MMI-DEC-270.
6. Reconciliation voter amendment for omission-as-safety — separate Phase 4 amendment or bundled DEC?
7. Dual write path declared: blackboard `AgentContribution` JSONL vs `CanonicalEvidenceLedger` — backer must read both or unify.

---

## §9 Boundaries (this contract)

- No live production chaos
- No AUTH-5
- No crypto signing
- No scoreboard agent row promotion from this document alone
- No other model may §11-sign on Matt's behalf

---

## §11 Sign-off

SIGNED. This locks BM-D1–BM-D10 for Blackboard-Mesh infrastructure governance. Signing authorizes future build slices (Mode A ledger gate, Evidence Backer read-only verifier, Crucible failure log) **only** after separate operator Build Authorization. Signing authorizes **no** production dispatch, **no** live SIGKILL chaos, **no** AUTH-5 unlock, and **no** cryptographic signing (LAW 9 parked).

> §11 SIGNATURE — Matt Nichol June 27th 2026

---

**End.** Next steps: operator build authorization → Mode A ledger gate → `evidence_backer.py` → crucible failure log (hot lane).
