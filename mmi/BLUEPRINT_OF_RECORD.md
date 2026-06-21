# Blueprint of Record

**Status:** CURRENT_PLAN populated 2026-06-21 (MMI-DEC-057). Prior placeholder superseded.

**Classification:** Shared crew artifact · Blueprint of Record

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar`

---

## CURRENT_PLAN — ALL_CLEAR feedstock v1

plan_status: CURRENT_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v1
population_authorization: MMI_BOR_ALL_CLEAR_FEEDSTOCK_v1
population_decision: MMI-DEC-057
created_at: 2026-06-21
source_contract: mmi/MMI_BLUEPRINT_OF_RECORD_GOVERNANCE_CONTRACT.md
architect_blueprint_source: scoreboard print + BUILDABILITY_EXCLUSIONS + next_lane menu 2026-06-21
revision_reason: Restore crew loop when dispatcher ALL_CLEAR and buildable_count=0
non_authority_disclaimer: Advisory flow plan only. Does not authorize build, routing, contract draft, promotion, or registry dispatch.

When dispatcher is ALL_CLEAR and Estimator has no SIGNED_UNBUILT/AWAITING_AUDIT rows, Estimator reads feedstock_entry lines below and emits SCORED_FEEDSTOCK for PM Voice relay.

feedstock_entry: priority=1 candidate_id=#61 lane_type=CONTRACT_DRAFT name=Test Case Generator
feedstock_entry: priority=2 candidate_id=#62 lane_type=CONTRACT_DRAFT name=Regression Test
feedstock_entry: priority=3 candidate_id=#63 lane_type=CONTRACT_DRAFT name=Adversarial Test
feedstock_entry: priority=4 candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement
feedstock_entry: priority=hold candidate_id=#1 lane_type=CONTRACT_DRAFT name=Swarm Commander Agent hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#3 lane_type=CONTRACT_DRAFT name=Risk Triage Agent hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

---

## Prior placeholder (superseded)

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Placeholder shell only before feedstock population.

plan_status: SUPERSEDED_PLAN
version_id: BOR-PLACEHOLDER-v0
supersedes:
revision_reason: Replaced by BOR-ALL-CLEAR-FEEDSTOCK-v1

Content population deferred until Architect build authorization (historical note only).

---
