# Blueprint of Record

**Status:** CURRENT_PLAN populated 2026-06-24 (MMI-DEC-117). Command spine #1–#3 GATED at wrapper layer; PMV chain relay to routing-policy annex fork.

**Classification:** Shared crew artifact · Blueprint of Record

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar`

---

## CURRENT_PLAN — ALL_CLEAR feedstock v11

plan_status: CURRENT_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v11
population_authorization: MMI_BOR_ALL_CLEAR_FEEDSTOCK_v11
population_decision: MMI-DEC-117
created_at: 2026-06-24
source_contract: mmi/MMI_BLUEPRINT_OF_RECORD_GOVERNANCE_CONTRACT.md
architect_blueprint_source: Command spine #1–#3 GATED at wrapper layer (MMI-DEC-112/109/116); PMV chain relay
revision_reason: Command spine wrappers complete; chain-of-command next fork is routing-policy annex draft; hold-only feedstock unchanged
non_authority_disclaimer: Advisory flow plan only. Does not authorize build, routing, contract draft, promotion, or registry dispatch.

When dispatcher is ALL_CLEAR and Estimator has no SIGNED_UNBUILT/AWAITING_AUDIT rows, Estimator reads feedstock_entry lines below and emits SCORED_FEEDSTOCK for PM Voice relay.

feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

Completed rows omitted from feedstock (Estimator skips CLOSED lifecycle rows automatically):
  Command spine #1 Swarm Commander — GATED wrapper (MMI-DEC-112); not GOVERNED_AGENT; not wired
  Command spine #2 Mission Context — GATED wrapper (MMI-DEC-109); not GOVERNED_AGENT; not wired
  Command spine #3 Risk Triage — GATED wrapper (MMI-DEC-116); not GOVERNED_AGENT; not wired
  #105 MMI Governance Invariants Testing Framework — SIGNED_CONTRACT + Lane 1 probe (MMI-DEC-092)
  #61 Test Case Generator, #62 Regression Test, #63 Adversarial Test, #64 Failure Classification — GATED

Chain-of-command next fork (PMV relay; not feedstock authorization): routing-policy annex draft for #1 at `docs/mmi/contracts/001_swarm_commander_routing_policy_annex.md` — **DRAFT on disk (MMI-DEC-118); pre-build gate pending; not §11**.

Estimator BUILDABILITY_EXCLUSIONS advisory (not feedstock authorization): hold-only feedstock; spine wrappers GATED; PMV reads live rubric for chain relay.

---

## Prior ALL_CLEAR v10 (superseded)

plan_status: SUPERSEDED_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v10
supersedes: BOR-ALL-CLEAR-FEEDSTOCK-v9
population_decision: MMI-DEC-102
revision_reason: Superseded by v11 after Command spine #1–#3 GATED (MMI-DEC-116) + PMV chain relay (MMI-DEC-117)

Historical v10 feedstock (inactive — do not parse):
  feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

---

## Prior ALL_CLEAR v9 (superseded)

plan_status: SUPERSEDED_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v9
supersedes: BOR-ALL-CLEAR-FEEDSTOCK-v8
population_decision: MMI-DEC-099
revision_reason: Superseded by v10 after #1 §11 sign (MMI-DEC-102)

Historical v9 feedstock (inactive — do not parse):
  feedstock_entry: priority=1 candidate_id=#1 lane_type=CONTRACT_DRAFT name=Swarm Commander Agent
  feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

---

## Prior ALL_CLEAR v8 (superseded)

plan_status: SUPERSEDED_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v8
supersedes: BOR-ALL-CLEAR-FEEDSTOCK-v7
population_decision: MMI-DEC-098
revision_reason: Superseded by v9 after #1 unpark (MMI-DEC-099)

Historical v8 feedstock (inactive — do not parse):
  feedstock_entry: priority=hold candidate_id=#1 lane_type=CONTRACT_DRAFT name=Swarm Commander Agent hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

---

## Prior ALL_CLEAR v7 (superseded)

plan_status: SUPERSEDED_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v7
supersedes: BOR-ALL-CLEAR-FEEDSTOCK-v6
population_decision: MMI-DEC-096
revision_reason: Superseded by v8 after #3 §11 sign (MMI-DEC-098)

Historical v7 feedstock (inactive — do not parse):
  feedstock_entry: priority=1 candidate_id=#3 lane_type=CONTRACT_REVIEW name=Risk Triage Agent
  feedstock_entry: priority=hold candidate_id=#1 lane_type=CONTRACT_DRAFT name=Swarm Commander Agent hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

---

## Prior ALL_CLEAR v6 (superseded)

plan_status: SUPERSEDED_PLAN
version_id: BOR-ALL-CLEAR-FEEDSTOCK-v6
supersedes: BOR-ALL-CLEAR-FEEDSTOCK-v5
population_decision: MMI-DEC-093
revision_reason: Superseded by v7 after #3 unpark (MMI-DEC-096)

Historical v6 feedstock (inactive — do not parse):
  feedstock_entry: priority=hold candidate_id=#1 lane_type=CONTRACT_DRAFT name=Swarm Commander Agent hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#3 lane_type=CONTRACT_DRAFT name=Risk Triage Agent hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#67 lane_type=CONTRACT_DRAFT name=Rule Improvement hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#47 lane_type=PROMOTION_REVIEW name=Case Timeline hold_unless_matt=true
  feedstock_entry: priority=hold candidate_id=#52 lane_type=PROMOTION_REVIEW name=Plain-English Explanation hold_unless_matt=true

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
