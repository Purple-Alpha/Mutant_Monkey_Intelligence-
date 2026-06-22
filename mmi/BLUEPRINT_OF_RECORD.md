# Blueprint of Record

**Status:** CURRENT_PLAN populated 2026-06-21 (MMI-DEC-093). #105 SIGNED_CONTRACT complete; hold-only feedstock; Estimator missing-contract advisory #1/#3.

**Classification:** Shared crew artifact · Blueprint of Record

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar`

---

## CURRENT_PLAN — ALL_CLEAR feedstock v6

plan_status: CURRENT_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v6
population_authorization: MMI_BOR_ALL_CLEAR_FEEDSTOCK_v6
population_decision: MMI-DEC-093
created_at: 2026-06-21
source_contract: mmi/MMI_BLUEPRINT_OF_RECORD_GOVERNANCE_CONTRACT.md
architect_blueprint_source: scoreboard print + #105 SIGNED_CONTRACT closeout (MMI-DEC-092)
revision_reason: #105 §11 signed + SIGNED_CONTRACT reconcile complete; remove stale CONTRACT_REVIEW feedstock; restore hold-only ALL_CLEAR feedstock; Estimator missing_contract_count=2 advisory (#1, #3) when Matt unparks
non_authority_disclaimer: Advisory flow plan only. Does not authorize build, routing, contract draft, promotion, or registry dispatch.

When dispatcher is ALL_CLEAR and Estimator has no SIGNED_UNBUILT/AWAITING_AUDIT rows, Estimator reads feedstock_entry lines below and emits SCORED_FEEDSTOCK for PM Voice relay.

feedstock_entry: priority=hold candidate_id=#1 lane_type=CONTRACT_DRAFT name=Swarm Commander Agent hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#3 lane_type=CONTRACT_DRAFT name=Risk Triage Agent hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

Completed rows omitted from feedstock (Estimator skips CLOSED lifecycle rows automatically):
  #105 MMI Governance Invariants Testing Framework — SIGNED_CONTRACT + Lane 1 probe (MMI-DEC-092)
  #61 Test Case Generator, #62 Regression Test, #63 Adversarial Test, #64 Failure Classification — GATED

Estimator BUILDABILITY_EXCLUSIONS advisory (not feedstock authorization): missing Agent Design Contract on disk for #1 and #3 when Matt removes hold.

---

## Prior ALL_CLEAR v5 (superseded)

plan_status: SUPERSEDED_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v5
supersedes: BOR-ALL-CLEAR-FEEDSTOCK-v4
population_decision: MMI-DEC-090
revision_reason: Superseded by v6 after #105 §11 sign + SIGNED_CONTRACT (MMI-DEC-092)

Historical v5 feedstock (inactive — do not parse):
  priority=1 #105 CONTRACT_REVIEW MMI Governance Invariants Testing Framework
  priority=hold #67 CONTRACT_DRAFT Rule Improvement
  priority=hold #1 CONTRACT_DRAFT Swarm Commander Agent
  priority=hold #3 CONTRACT_DRAFT Risk Triage Agent
  priority=hold #47 PROMOTION_REVIEW Case Timeline
  priority=hold #52 PROMOTION_REVIEW Plain-English Explanation

---

## Prior GSTF pivot plan (superseded)

plan_status: SUPERSEDED_PLAN
version_id: BOR-GSTF-DESIGN-FEEDSTOCK-v2
supersedes: BOR-ALL-CLEAR-FEEDSTOCK-v1
revision_reason: Temporary invariants-framework pivot (MMI-DEC-080 through MMI-DEC-082); restored by MMI-DEC-083

---

## Prior ALL_CLEAR v1 (superseded)

plan_status: SUPERSEDED_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v1
population_decision: MMI-DEC-057
revision_reason: Superseded by GSTF pivot v2, then restored as v3

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Placeholder shell only before feedstock population.

plan_status: SUPERSEDED_PLAN
version_id: BOR-PLACEHOLDER-v0
supersedes:
revision_reason: Replaced by BOR-ALL-CLEAR-FEEDSTOCK-v1

Content population deferred until Architect build authorization (historical note only).

---
