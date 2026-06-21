# Blueprint of Record

**Status:** CURRENT_PLAN populated 2026-06-22 (MMI-DEC-080). Prior feedstock v1 superseded.

**Classification:** Shared crew artifact · Blueprint of Record

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar`

---

## CURRENT_PLAN — GSTF multi-lane design feedstock v2

plan_status: CURRENT_PLAN
version_id: BOR-GSTF-DESIGN-FEEDSTOCK-v2
population_authorization: MMI_BOR_GSTF_DESIGN_PIVOT_v1
population_decision: MMI-DEC-080
created_at: 2026-06-22
source_contract: mmi/MMI_BLUEPRINT_OF_RECORD_GOVERNANCE_CONTRACT.md
architect_blueprint_source: operator pivot — governance stress testing design before #67 resume
revision_reason: Park #67 Claude contract-draft; elevate #105 GSTF multi-lane advisory design
non_authority_disclaimer: Advisory flow plan only. Does not authorize build, routing, §11, promotion, or registry dispatch.

When dispatcher is ALL_CLEAR and Estimator has no SIGNED_UNBUILT/AWAITING_AUDIT rows, Estimator reads feedstock_entry lines below and emits SCORED_FEEDSTOCK for PM Voice relay.

feedstock_entry: priority=1 candidate_id=#105 lane_type=CONTRACT_REVIEW name=MMI Governance Invariants Testing Framework
feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
feedstock_entry: priority=2 candidate_id=#64 lane_type=CONTRACT_DRAFT name=Failure Classification
feedstock_entry: priority=completed candidate_id=#61 lane_type=GATED name=Test Case Generator completed_gated=true
feedstock_entry: priority=completed candidate_id=#62 lane_type=GATED name=Regression Test completed_gated=true
feedstock_entry: priority=completed candidate_id=#63 lane_type=GATED name=Adversarial Test completed_gated=true
feedstock_entry: priority=hold candidate_id=#1 lane_type=CONTRACT_DRAFT name=Swarm Commander Agent hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#3 lane_type=CONTRACT_DRAFT name=Risk Triage Agent hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

---

## Prior placeholder (superseded)

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Placeholder shell only before feedstock population.

plan_status: SUPERSEDED_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v1
supersedes: BOR-PLACEHOLDER-v0
revision_reason: Replaced by BOR-GSTF-DESIGN-FEEDSTOCK-v2 (MMI-DEC-080)

Content population deferred until Architect build authorization (historical note only).

---
