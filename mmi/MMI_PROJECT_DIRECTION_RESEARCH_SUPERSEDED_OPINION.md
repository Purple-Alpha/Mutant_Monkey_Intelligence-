# PROJECT_DIRECTION_RESEARCH — SUPERSEDED_OPINION (DO NOT USE AS AUTHORITY)

**Status:** SUPERSEDED_OPINION / DO_NOT_USE_AS_AUTHORITY  
**Retired:** 2026-06-20 (MMI-DEC-044)  
**Reason:** Hardcoded maintainer-set 10-axis direction rubric removed from `scripts/mmi_dispatch.py` executable path. Evidence-based candidate ranking is handled by Estimator Mode A (`c742a6c`) as read-only ranking input only.

**Do not use as:** authority, doctrine, Estimator input, route authority, success/path/project identity definition.

Underlying repo artifacts cited by retired directions remain in place (scoreboard, contracts, decision log). Only the hardcoded axis scores and dispatcher ranking behavior are retired.

---

## Classification table (retired hardcoded directions)

| direction_id_or_name | axis_scores (total/20) | source/evidence references | scorer classification | reason |
|---|---|---|---|---|
| Build #48 Verification Outcome Agent (Stage 1 Synthetic wrapper) | rm=2,pf=2,se=2,du=2,dr=2,br=2,ra=2,ot=2,ma=2,dc=1 (19) | Verification_Outcome contract §11; scoreboard #48/#47; PROJECT_HANDSHAKE; CYCLE 25 | **OPINION** (axis scores); evidence refs preserved in repo | Axis scores maintainer-typed; underlying #48 contract/scoreboard evidence remains in repo |
| Draft #47 Case Timeline Agent Design Contract | rm=1,pf=2,se=2,du=2,dr=2,br=1,ra=1,ot=2,ma=2,dc=1 (16) | scoreboard #47/#48; CYCLE 25/27; MMI-DEC-013; REACTION_TIMING_TEST_LOG | **OPINION** (axis scores); evidence refs preserved in repo | Axis scores maintainer-typed; #47/#48 state remains in scoreboard and DEC log |
| Build second Layer 5 Challenge agent (cross-arbitration; closes KG-002) | rm=1,pf=2,se=2,du=1,dr=1,br=1,ra=1,ot=1,ma=2,dc=1 (13) | PROJECT_HANDSHAKE ACTION B; Aggregate Corroboration contract §10 Q1; Layer 5 deep dive | **OPINION** (axis scores); evidence refs preserved in repo | Axis scores maintainer-typed; handshake/contract artifacts remain |
| Stage 1 breadth — wrap #52 Plain-English Explanation detector | rm=2,pf=1,se=1,du=1,dr=1,br=1,ra=2,ot=1,ma=1,dc=2 (13) | scoreboard #52; client_facing_rubric.py | **OPINION** (axis scores); evidence refs preserved in repo | Axis scores maintainer-typed; #52 scoreboard row remains |
| Promote parked roadmap concept drafts to tracked build | all axes 0 (0) | PARKED_DRAFT_CLASSIFICATIONS.md; git untracked drafts | **OPINION** (axis scores); evidence refs preserved in repo | Scores were denial placeholder; classification file remains |
| Real-data intake path (Evidence Stage 2 promotion) | rm=1,pf=1,se=1,du=0,dr=0,br=0,ra=1,ot=0,ma=1,dc=1 (6) | scoreboard DEPTH rows; PROJECT_HANDSHAKE ACTION D | **OPINION** (axis scores); evidence refs preserved in repo | Axis scores maintainer-typed; scoreboard/handshake remain |
| Stabilize — hold new builds; verify and document only | rm=0,pf=0,se=1,du=0,dr=1,br=2,ra=2,ot=2,ma=1,dc=0 (9) | PROJECT_HANDSHAKE ACTION E; MMI_HEALTH_STATE.md | **OPINION** (axis scores); evidence refs preserved in repo | Axis scores maintainer-typed; handshake/health docs remain |

**Axis key:** rm=revenue_market, pf=product_foundation, se=security_evidence, du=dependency_unlock, dr=drift_reduction, br=build_readiness, ra=risk_ambiguity, ot=owner_time, ma=mmi_alignment, dc=demo_customer

**Retired rubric description:** 0-2 per axis, max total 20. risk_ambiguity and owner_time inverse penalties.
