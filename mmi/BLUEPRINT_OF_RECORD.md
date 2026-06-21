# Blueprint of Record

**Status:** CURRENT_PLAN populated 2026-06-21 (MMI-DEC-089). #64 Failure Classification GATED; hold-only ALL_CLEAR feedstock.

**Classification:** Shared crew artifact · Blueprint of Record

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar`

---

## CURRENT_PLAN — ALL_CLEAR feedstock v4

plan_status: CURRENT_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v4
population_authorization: MMI_BOR_ALL_CLEAR_FEEDSTOCK_v4
population_decision: MMI-DEC-089
created_at: 2026-06-21
source_contract: mmi/MMI_BLUEPRINT_OF_RECORD_GOVERNANCE_CONTRACT.md
architect_blueprint_source: scoreboard print + #64 Failure Classification GATED closeout (MMI-DEC-088/089)
revision_reason: #64 Failure Classification GATED; remove rank-1 CONTRACT_DRAFT feedstock; hold-only entries remain
non_authority_disclaimer: Advisory flow plan only. Does not authorize build, routing, contract draft, promotion, or registry dispatch.

When dispatcher is ALL_CLEAR and Estimator has no SIGNED_UNBUILT/AWAITING_AUDIT rows, Estimator reads feedstock_entry lines below and emits SCORED_FEEDSTOCK for PM Voice relay.

feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#105 lane_type=CONTRACT_REVIEW name=MMI Governance Invariants Testing Framework hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#1 lane_type=CONTRACT_DRAFT name=Swarm Commander Agent hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#3 lane_type=CONTRACT_DRAFT name=Risk Triage Agent hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

Completed GATED rows (#61 Test Case Generator, #62 Regression Test, #63 Adversarial Test, #64 Failure Classification) are omitted from feedstock; Estimator skips CLOSED lifecycle rows automatically.

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
