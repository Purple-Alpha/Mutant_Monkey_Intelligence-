# Specialisation Fission v2 — Canadian Legal Alignment & Underwriter Checklist

**Contract:** `4. Product_Roadmap/Specialisation_Fission_Contract_v2.md` §14–§15  
**Scoreboard row:** #104 Specialisation Fission Controller v2  
**Date:** 2026-06-18  
**Status:** Documentation artifact for v2 implementation gate — not buyer-facing release

---

## §14 Canadian Legal Alignment (summary)

Mutant Monkey Inbox Shield produces **evidence, not decisions**. Human authority retains final decision power. The system does not guarantee fraud prevention or detection of every malicious email. No autonomous client-facing financial decisions. Red children create bounded internal pressure scenarios only — not external attack instructions. Blue children create structured evidence, not decisions. Parent aggregation remains evidence aggregation, not final authority.

### Shared Responsibility Matrix

| Party | Responsibility |
|---|---|
| Operator | Approves policy changes, signs governed promotions, reviews incident posture |
| SOC / governance approver | Approves Deep intensity when required by policy |
| MSP | Configures tenant posture, monitors alerts, validates client workflow fit |
| Client | Maintains business process controls and final approval for sensitive actions |
| Infrastructure provider | Platform availability and account controls |
| Mutant Monkey Inbox Shield | Governed evidence, audit logs, control records, bounded recommendations |

---

## §15 Underwriter Documentation Checklist

| Item | v2 implementation evidence |
|---|---|
| Architecture diagram | Fission modules: `specialisation.py` (v2), shared `event_log.py`, `load_governance.py` |
| Governance policy | `SpecialisationFissionPolicy` versioned immutable policy (SF2 §2) |
| Red team results | `tests/test_specialisation_fission_v2.py` — 8 Class 2 adversarial tests |
| Evidence chain integrity | Append-only `FissionEventLog`, `LifecycleLog`, `SpecialisationSpawnDecisionRecord` |
| Spawn governance controls | Quota tracker, circuit breaker, watcher-only triggers, net-new type gate |
| Fission fallback mode | `SpecialisationFissionPolicy.fallback_disabled` + denial logs |
| Purple Fission Curriculum role map | `PURPLE_FISSION_CURRICULUM` pairing table in `specialisation.py` |
| Intensity-level controls | `IntensityLevel` Light/Normal/Deep validation in controller |
| Net-new agent type gate | `NetNewTypeSignOffGate` + `SubTypeRegistry` |
| Schema guarantees (12 specializations) | `FIXED_SCHEMA_ALLOWED_FIELDS` + `PROHIBITED_OUTPUT_FIELDS` |
| Governed ingestion step | `SpecialisationGovernedIngestionPipeline` with scenario lock + Red/Blue boundaries |
| Audit log retention | Recorded as operator commitment — not implemented in code |
| Policy-as-code versioning | `SpecialisationFissionPolicyStore` |
| Lifecycle log schema | `LifecycleLogEntry` / `LifecycleEventKind` (shared with Load Fission v2) |

---

**Note:** This file satisfies the contract documentation gate for underwriter review prep. It does not authorize buyer-facing release or production deployment.
