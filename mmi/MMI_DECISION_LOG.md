# MMI_DECISION_LOG.md — Official Decision History

**Authority:** Matt Nichol — authorized June 16 2026

Every important decision is recorded here with its evidence. This is the project's decision memory.

---

## Decision record template

```
Decision ID:
Date:
Component:
Input evidence:
Decision:
Reason:
Risks:
Required follow-up:
Approved by:
```

---

## Decision log

> Reconciliation note (2026-06-16): DEC-004 and DEC-005 were originally seeded as REVISE from a pre-acceptance snapshot. They are now reconciled to the committed scoreboard, where the #99 and #102 gate-scope re-runs landed clean (0/0) and Matt accepted all four adversarial suites, granting the parent hardening claims (#92 / #84 / #89 / #94).

```
MMI-DEC-001 | 2026-06-16 | #100 ReconciliationAgent Adversarial | audit_outputs/reconciliation_agent_adversarial_20260615T030712Z.md blocking=0 warnings=1 (LungState patch — disclosed) | ACCEPT | Evidence complete, warning reviewed and accepted; ReconciliationAgent #84 marked ADVERSARIALLY HARDENED via this row | None | None | Matt Nichol

MMI-DEC-002 | 2026-06-16 | #101 BRC Adversarial | audit_outputs/blast_radius_controller_adversarial_runtime_20260615T051019Z.md + gate_scope + tests — all blocking=0 warnings=0 | ACCEPT | Three clean Grok audits, all 47 BRC-ADV IDs covered; Blast Radius Controller #89 marked ADVERSARIALLY HARDENED via this row | None | None | Matt Nichol

MMI-DEC-003 | 2026-06-16 | Runtime Instrumentation | audit_outputs/runtime_instrumentation_20260615T034659Z.md blocking=0 warnings=0 20 files reviewed | ACCEPT | Clean Grok audit across all touched files | None | None | Matt Nichol

MMI-DEC-004 | 2026-06-16 | #99 Mode Controller Adversarial | clean gate-scope re-run audit_outputs/mode_controller_adversarial_gate_scope_20260616T032356Z.md blocking=0 warnings=0 (earlier 20260615T021703Z attempt blocked on working-tree hygiene only) + test slice audit_outputs/mode_controller_adversarial_20260615T021608Z.md blocking=0 warnings=0 | ACCEPT | Gate-scope re-gated clean with corrected manifest; all 50 MC-ADV IDs covered; Mode Controller #92 marked ADVERSARIALLY HARDENED via this row | None | None | Matt Nichol

MMI-DEC-005 | 2026-06-16 | #102 Safe-Stop Adversarial | clean gate-scope audit_outputs/safe_stop_adversarial_gate_scope_20260616T023345Z.md blocking=0 warnings=0 (earlier 20260616T022942Z attempt blocked on manifest coverage only) + test slice audit_outputs/safe_stop_adversarial_tests_20260616T023420Z.md blocking=0 warnings=0 | ACCEPT | Gate-scope re-gated clean; all 97 SS-ADV IDs covered; Safe-Stop State Machine #94 marked ADVERSARIALLY HARDENED via this row | None | None | Matt Nichol

MMI-DEC-006 | 2026-06-18 | MMI delegation restore | scripts/mmi_dispatch.py collect_delegation_tasks + MODE:DELEGATE; tests/test_mmi_dispatch_routing.py | ACCEPT | Passive ALL_CLEAR ("Matt names next target") replaced with evidence-scored delegation; TID reclassified EXTERNAL_LANE; worker-completion MMI-first rule documented | Stale handoff prose may lag until next session sync | Run mmi_dispatch.py --sync after commit | Matt Nichol (authorize patch)

MMI-DEC-007 | 2026-06-18 | MMI project-direction research/scoring | scripts/mmi_dispatch.py collect_project_direction_candidates + MODE:PROJECT_DIRECTION_RESEARCH; mmi/MMI_ROUTING_RULES.md; mmi/MMI_PROTOCOL.md; tests/test_mmi_dispatch_routing.py | ACCEPT | Empty delegation queue now triggers 10-axis direction scoring and owner-ready recommendation instead of "Matt supplies next evidence"; ALL_CLEAR reserved for genuinely missing repo evidence | Scoreboard #48 row still drifts vs signed contract — reconcile on build start | Run mmi_dispatch.py --sync after commit | Matt Nichol (authorize MMI_PROJECT_DIRECTION_RESEARCH_AND_SCORING only)

MMI-DEC-008 | 2026-06-18 | #48 scoreboard lifecycle reconcile | agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md #48 row; contract 4. Product_Roadmap/Verification_Outcome_Agent_Design_Contract_Deep_Dive.md §11 SIGNED f34cc4f | ACCEPT | #48 flipped SPEC_ONLY/NEEDS_SIGNED_CONTRACT -> SIGNED_UNBUILT with empty BLOCKERS; MMI can route MODE:BUILD; no wrapper implementation | #47 remains DEPENDS_ON:#48 until #48 becomes GOVERNED_AGENT | Delegate build lane on operator confirm | Matt Nichol (authorize MMI_RECOMMENDED_48_SCOREBOARD_RECONCILE only)

MMI-DEC-009 | 2026-06-18 | MMI naming authority correction | PROJECT_HANDSHAKE.md; MMI_THREAD_HANDOFF.md; mmi/MMI_PROTOCOL.md; mmi/MMI_ROUTING_RULES.md; mmi/MMI_AUTHORITY_MATRIX.md; scripts/mmi_dispatch.py output labels | ACCEPT | Active project identity locked to Mutant Monkey Security / MMI; legacy path /home/socialarchitect/northstar documented; Architectapp separation + #48 build-surface guard added for workers | Historical NorthStar internal-codename refs in signed specs preserved | Run mmi_dispatch.py --sync after commit | Matt Nichol (authorize MMI_NAMING_AUTHORITY_CORRECTION only)

MMI-DEC-010 | 2026-06-19 | #48 Verification Outcome build + AWAITING_AUDIT lane | verification_outcome_agent.py + tests (e1afc56); scoreboard #48 row | ACCEPT | Stage 1 wrapper built on authority-repo surface; 21 tests passed; scoreboard AWAITING_AUDIT; MMI routes MODE:AUDIT | Grok gate 0/0 required before GATED | Run complete_gate.py --task verification_outcome | Matt Nichol (authorize #48_BUILD_COMMIT_AND_SCOREBOARD_AUDIT_LANE)

MMI-DEC-011 | 2026-06-19 | #48 Verification Outcome Grok gate + GATED promotion | audit_outputs/verification_outcome_20260619T032930Z.md (0/0); scoreboard #48 row | ACCEPT | Post-commit Grok gate clean 0/0 on authority-repo build; scoreboard #48 AWAITING_AUDIT -> GATED; parked drafts excluded from packet via .git/info/exclude | #47 remains DEPENDS_ON:#48 until GOVERNED_AGENT promotion | Run mmi_dispatch.py --sync after commit | Matt Nichol (authorize Grok gate run + GATED flip)

MMI-DEC-012 | 2026-06-19 | #48 GOVERNED_AGENT promotion review | scoreboard #48 row; decision_cycles_log CYCLE 26; health score board | ACCEPT | Repo evidence supports promotion: §11 contract, build e1afc56, 21 tests, Grok 0/0, L3 bar cleared; #48 GATED -> GOVERNED_AGENT; breadth runway 14; #47 dependency satisfied for re-triage only | No #47 build or Layer 5 direction started | Run mmi_dispatch.py --sync after commit | Matt Nichol (authorize MMI_48_GOVERNED_AGENT_PROMOTION_REVIEW only)

MMI-DEC-013 | 2026-06-19 | #47 Case Timeline dependency re-triage after #48 | scoreboard #47 row; decision_cycles_log CYCLE 27 | ACCEPT | DEPENDS_ON:#48 cleared; #48 GOVERNED_AGENT is governed verification-outcome input; no §11 Case Timeline contract in repo; #47 remains DETECTOR_FUNCTION partial with NEEDS_SIGNED_CONTRACT; not build-ready | Contract draft + Matt §11 required before SIGNED_UNBUILT | Run mmi_dispatch.py --sync after commit | Matt Nichol (authorize MMI_47_DEPENDENCY_RETRIAGE_AFTER_48 only)

MMI-DEC-014 | 2026-06-19 | MMI project-direction scoring include #47 | scripts/mmi_dispatch.py collect_project_direction_candidates | ACCEPT | #47 Case Timeline contract-draft direction added to 10-axis rubric when NEEDS_SIGNED_CONTRACT + #48 GOVERNED_AGENT; rubric ranks; no SIGNED_UNBUILT flip | Contract draft not started | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_PROJECT_DIRECTION_SCOREBOARD_INCLUDE_47 only)

MMI-DEC-015 | 2026-06-19 | #47 Case Timeline Agent Design Contract draft | 4. Product_Roadmap/Case_Timeline_Agent_Design_Contract_Deep_Dive.md | ACCEPT | Draft authored from scoreboard #47, CYCLE 25/27, DecisionTimestamps, REACTION_TIMING_TEST_LOG, #48 GOVERNED_AGENT input rule; §11 UNSIGNED; no build/scoreboard flip | Grok draft gate + Matt §11 required before SIGNED_UNBUILT | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_RECOMMENDED_47_CASE_TIMELINE_CONTRACT_DRAFT only)

MMI-DEC-016 | 2026-06-19 | MMI Autonomous Brain Foundation review material placement | mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md | ACCEPT | DRAFT adversarial review material placed; AUTH-3 split to AUTH-3A (registry format) + AUTH-3B (write mechanics); no dispatcher/code/scoreboard change | Adversarial review + separate AUTH gates before any implementation | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_REVIEW_MATERIAL_PLACEMENT only)

MMI-DEC-017 | 2026-06-19 | MMI Autonomous Brain Foundation review material reconciliation patch | mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md | ACCEPT | Reconciled to external-reviewed AUTH-1–6 semantics, Tier 1/2/3, registry/dispatcher boundaries, Decision Audit Appendix, lifecycle ordering, invariants, acceptance tests; AUTH-5 = autonomous selection isolated; AUTH-2 = dispatcher respect-only; review material only | Adversarial review on reconciled text; no AUTH gate activation | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_REVIEW_MATERIAL_RECONCILIATION_PATCH only)

MMI-DEC-018 | 2026-06-19 | MMI Autonomous Brain review hardening + Tier 1 contract draft | mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md; mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md | ACCEPT | Adversarial PASS WITH CHANGES wording applied (AUTH-2-EDIT, I13–I16, T12–T16, §14 gaps); Tier 1 contract drafted UNSIGNED; no Tier 1 implementation | Matt §11 on Tier 1 contract + separate build auth before artifact creation | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_REVIEW_HARDENING_AND_TIER1_CONTRACT_DRAFT only)

MMI-DEC-019 | 2026-06-19 | Tier 1 MMI Autonomous Brain contract wording patch | mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md | ACCEPT | Tier 1 contract review PASS WITH CHANGES wording fixes (T1-T1/§7, F2/F4, §4 AUTH split, §7 I15 packet); contract draft only; not §11 signed; not implementation | Matt §11 signature + separate build authorization before F1–F5 | Run mmi_dispatch.py --verify after commit | Matt Nichol (Tier 1 contract wording patch commit)

MMI-DEC-020 | 2026-06-18 | Tier 1 MMI Autonomous Brain contract §11 signature | mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md (`f7ac7f2` base) | ACCEPT | Matt §11 signed Tier 1 passive foundation contract; authorizes F1–F5 only upon separate build authorization; not implementation | Explicit Tier 1 build authorization before F1–F5 artifact creation | Run mmi_dispatch.py --verify after commit | Matt Nichol (Tier 1 contract signature update only)

MMI-DEC-021 | 2026-06-18 | Tier 1 MMI Autonomous Brain foundation build (F1–F5) | mmi/MMI_REPO_SURFACE_REGISTRY.md; mmi/MMI_TASK_REGISTRY_SCHEMA.md; mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md; mmi/MMI_DECISION_AUDIT_APPENDIX_SCHEMA.md; mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md | ACCEPT | Passive Tier 1 foundation artifacts F1–F5 created per signed contract `1972df7`; schema-only F2/F4; no dispatcher/code/runtime/scoreboard change; no live registry; no automation | Tier 2 tooling and AUTH-5 remain blocked until separate gates | Run mmi_dispatch.py --sync + --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_BUILD only)

MMI-DEC-022 | 2026-06-18 | Tier 2A Worker Packet Intake contract draft placement | mmi/MMI_AUTONOMOUS_BRAIN_TIER2A_WORKER_PACKET_INTAKE_CONTRACT_DRAFT.md | ACCEPT | DRAFT UNSIGNED placement only; §11 hardened — signature approves contract only, not implementation; Mode A default / Mode B config only; no `scripts/mmi_packet_intake.py`; implementation blocked | Matt §11 + separate build authorization before Tier 2A code | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_TIER2A_CONTRACT_DRAFT_PLACEMENT only)

MMI-DEC-023 | 2026-06-18 | Tier 2A Worker Packet Intake contract wording patch | mmi/MMI_AUTONOMOUS_BRAIN_TIER2A_WORKER_PACKET_INTAKE_CONTRACT_DRAFT.md | ACCEPT | Review PASS WITH CHANGES applied: locked stdout vocabulary (`ACCEPT_FOR_MMI_REVIEW` / `REJECT_INCOMPLETE_PACKET`), structural-only validation, exit-code semantics, rollback/demotion, Mode B parked, acceptance tests T2A-T8–T12; contract wording only; not §11 signed; not implementation | Matt §11 + separate build authorization before Tier 2A code | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_TIER2A_CONTRACT_WORDING_PATCH only)

MMI-DEC-024 | 2026-06-19 | Tier 2A Worker Packet Intake contract §11 signature | mmi/MMI_AUTONOMOUS_BRAIN_TIER2A_WORKER_PACKET_INTAKE_CONTRACT_DRAFT.md (`07b9ff4` base) | ACCEPT | Matt §11 signed Tier 2A packet intake contract; Mode A selected (stdout-only, zero file-write); Mode B not selected (parked); contract only — not implementation; separate build authorization required before `scripts/mmi_packet_intake.py` | Explicit Tier 2A Mode A build authorization before code | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_TIER2A_CONTRACT_SIGNATURE_ONLY)

MMI-DEC-025 | 2026-06-19 | Tier 2A Mode A packet intake validator build | scripts/mmi_packet_intake.py; tests/test_mmi_packet_intake.py; tests/fixtures/mmi_packets/* | ACCEPT | Mode A stdout-only structural validator per signed contract `e08792a`; `ACCEPT_FOR_MMI_REVIEW` / `REJECT_INCOMPLETE_PACKET`; 20 tests T2A-T1–T12; no dispatcher/scoreboard/runtime writes; Mode B not implemented | None | Run mmi_dispatch.py --sync + --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_TIER2A_PACKET_INTAKE_MODE_A_BUILD only)

MMI-DEC-026 | 2026-06-19 | Tier 2B Passive Task Registry contract draft placement | mmi/MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT.md | ACCEPT | DRAFT UNSIGNED placement only; passive human-maintained registry mechanics contract; not dispatcher input; AUTH-5 blocked; Mode A registry file recommended / Mode B validator parked; no `mmi/MMI_TASK_REGISTRY.yaml`; no validator code; implementation blocked | Matt §11 + separate build authorization before Tier 2B implementation | Run mmi_dispatch.py --sync + --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_TIER2B_CONTRACT_DRAFT_PLACEMENT only)

MMI-DEC-027 | 2026-06-19 | Tier 2B Passive Task Registry contract §11 signature | mmi/MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT.md (`495ef8b` base) | ACCEPT | Matt §11 signed Tier 2B passive task registry contract; Mode A selected (human-maintained registry instance only); Mode B not selected (parked); contract only — not implementation; AUTH-5 blocked; registry-fed routing forbidden; separate build authorization required before `mmi/MMI_TASK_REGISTRY.yaml` or validator code | Explicit Tier 2B Mode A build authorization before implementation | Run mmi_dispatch.py --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_TIER2B_CONTRACT_SIGNATURE_ONLY)

MMI-DEC-028 | 2026-06-19 | Tier 2B Mode A passive task registry build | mmi/MMI_TASK_REGISTRY.yaml; mmi/MMI_TASK_REGISTRY_UPDATE_RULES.md | ACCEPT | Mode A human-maintained registry instance per signed contract `7d245f8`; empty `tasks` envelope; `dispatcher_reads: false`; `autonomous_selection: false`; no validator code; no dispatcher/scoreboard/runtime change; Mode B not implemented; AUTH-5 blocked; registry-fed routing forbidden | None | Run mmi_dispatch.py --sync + --verify after commit | Matt Nichol (authorize MMI_AUTONOMOUS_BRAIN_TIER2B_MODE_A_BUILD only)

## Active Project Identity Guard

Active project identity: **Mutant Monkey Security**.

Central project brain: **Mutant Monkey Intelligence (MMI)**.

Legacy filesystem path: `/home/socialarchitect/northstar`.

The word `northstar` may appear as a legacy folder path, commit history, or historical reference only. It must not be used as the current active project identity.

Separate app repo surfaces such as `/home/socialarchitect/projects/Architectapp_clean` or `/mnt/c/Architectapp_clean` are not the governed MMI / swarm runtime authority surface.

For governed MMI / swarm runtime work, use:

- Project: Mutant Monkey Security
- Brain: Mutant Monkey Intelligence / MMI
- Authority repo path: `/home/socialarchitect/northstar`

#48 Verification Outcome Agent belongs only in:

`/home/socialarchitect/northstar/core/orchestrator/verification_outcome_agent.py`

Do not build governed MMI / swarm runtime artifacts in Architectapp.

