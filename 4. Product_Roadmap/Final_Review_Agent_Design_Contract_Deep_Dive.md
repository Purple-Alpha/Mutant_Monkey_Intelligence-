# Final Review Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_70_FINAL_REVIEW_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** §11 SIGNED 2026-06-26 by Matt Nichol (MMI-DEC-244). Pre-build gate clean **0 blocking / 2 warnings** (MMI-DEC-243; `logs/complete_gate_report.json`). Governs future `FinalReviewAgent` at ES1. **Not** build authorized by signature alone; **not** production dispatch; **not** AUTH-5.

**Scope:** swarm #70 **Slice B only** — case-level DER final review + governance finalization packet assembly. **Slice A** (`audit_tools/complete_gate.py`, `core/evidence_package/package_auditor.py`) remains separate infrastructure per `mmi/project_brain/status/final_review_70_boundary.md` (MMI-DEC-240).

**Owner:** Matt Nichol

**Candidate:** #70 — Final Review Agent

**Track:** BREADTH / Learning–Governance (Layer 6 scoreboard row)

**Lane:** Agent Design Contract (Claude advisory draft → Cursor placement · MMI-DEC-240 follow-on)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** Built `aa38ca3` — scoreboard `AWAITING_AUDIT` (MMI-DEC-248). **Not** GATED; **not** production dispatch.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `mmi/project_brain/status/final_review_70_boundary.md` (Slice A / Slice B split — MMI-DEC-240)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#70 row; Q4 L6 promotion bar)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (§1.5 Final Review; Level 6 authority)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`FINAL_REVIEW_AGENT_ID`, `audit_record_id` write guard)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/evidence_package_agent.py` (#46 builder-auditor separation)
- `4. Product_Roadmap/Correction_Evidence_Agent_Design_Contract_Deep_Dive.md` (#65 — rule-change finalization chain)
- `4. Product_Roadmap/Agent_Health_Score_Deep_Dive.md` (Health Score components; false-miss weighting)
- `mmi/MMI_GATE_REGISTRY.md` (DEPTH component gate status — partial input only; see REPO_RECONCILIATION)
- `audit_tools/complete_gate.py` (Slice A — **not** absorbed by this agent)
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/final_review_agent.py` (`FinalReviewAgent`, agent id `final_review_001`)

---

## Agent Design Contract block

**Boundary:** This contract governs the Final Review **agent wrapper** (`FinalReviewAgent`, Slice B). It is additive governance under template §7.0. It does **not** replace, absorb, or re-home **Slice A** infrastructure (`complete_gate.py`, `package_auditor.py`). It does **not** sign, promote, authorize, or mark anything complete. `READY-FOR-§11` is a **precondition surfaced to a human** — never a decision.

| Field | Value |
|---|---|
| Agent name | Final Review Agent (`FinalReviewAgent`) |
| Swarm inventory ID | #70 — Final Review Agent |
| Canonical layer | 6 — Learning / Governance |
| Canonical team / case type | Cross-cutting — swarm case DER audit + superintendent governance finalization |
| Authority level | Level 6 — Final Review (design tree) |
| Stage posture | VISION Stage A — analyze / recommend / evidence only |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed |
| Role | **(1) FR-DER:** On an assembled `DecisionEvidenceRecord`, verify verdict/evidence/explanation/recommendation coherence; emit audit trail facts; set `audit_record_id` only when internal checks pass. **(2) FR-GOV:** On a governance finalization candidate, assemble a Final Review Packet with per-check status and readiness verdict. Never sign, promote, or authorize. |
| Boundary | Read-only auditor + packet assembler. Surfaces readiness; enacts nothing. Matt §11 mandatory regardless of verdict. |
| Explicit non-authorities | No sign / promote / authorize / GATED / GOVERNED_AGENT lifecycle mutation; no `build_default_registry` at ES1; no production dispatch; no payment or containment action; no self-approval of DER or contract; no absorption of `complete_gate.py` or `package_auditor.py`; no AUTH-5; no scoreboard row mutation from agent output |
| Inputs | **FR-DER:** one explicit case review request: assembled `DecisionEvidenceRecord` (read-only), `MissionContext`, contributor list refs, optional evidence-anchor hash. **FR-GOV:** one explicit finalization candidate envelope: `candidate_kind` (`agent_build` \| `contract_sign` \| `gated_reconcile` \| `governed_promotion`), `candidate_id`, artifact manifest (paths + hashes), scoreboard row ref when applicable |
| Outputs | **FR-DER:** Layer 6 `AgentContribution` with coherence facts + optional `audit_record_id` when all FR-DER checks pass (writer id `final_review_001` only). **FR-GOV:** `FINAL_REVIEW_PACKET_v1` with per-check table, `could_not_verify` section, readiness verdict `READY-FOR-§11` \| `NOT-READY`, reproducibility block (input hashes, agent version). No bare approval token. |
| Evidence emitted | Closed facts only: per-check pass/fail/not-applicable; blocking item ids; `coherence_ok` / `coherence_gap` facts; `readiness_verdict`; `blind_spots` list. No reasoning trace in DER. |
| Data minimization | No raw mailbox body, tenant secrets, payment strings, or package file bytes in contributions/packets — hashes and closed-set refs only at ES1 |
| Tenant isolation | FR-DER reads only the supplied case/DER for the declared `tenant_id`; FR-GOV reads only artifacts scoped to the candidate manifest |
| Two-pass role | Pass 1 analyze only for Layer 6. `challenge()` returns `None`. |
| Decision Evidence Record contribution | `observed_facts`: coherence check outcomes; `interpretations`: none; `assumptions`: upstream assembler (#46 / Commander path) produced cited DER honestly; `missing_evidence`: explicit gaps; `recommended_verification`: none that enact; `final_outcome_contribution`: audit-trail facts only; `retest_or_learning_record`: per template §6.5 on false-ready |
| Human review trigger | **Always** — Matt §11 (contracts) or operator disposition (cases). Agent never clears human review requirement. |
| Verification trigger | None initiated — consumes verification outcomes only |
| Scoring / action posture | Facts-only. No disposition mutation. No rubric/score changes. |
| Default rollout | Evidence Stage 1 — not in `build_default_registry`; explicit callers/tests only |
| Autonomous action | None. `autonomous_action_allowed = False`. |
| Promotion conditions | Per template §6.2 Stage 1→2: clean focused tests, supervised samples, signed promotion record. L6 bar: structural read-only constraint + ≥1 audited decision on record. |
| Demotion conditions | Per template §6.3. **False-ready** (verdict `READY-FOR-§11` while blocking item existed) → highest-severity demotion + permanent regression. **Human-caught miss** at §11 → Final Review miss logged. |
| Retest evidence | Every false-ready / human-caught miss → permanent regression test before re-promotion (template §6.5) |
| Calibration requirement | ES1 synthetic fixtures only; Stage 2 requires supervised historical samples + `#93` privacy path when authorized |
| Failure modes | See §5 |
| Required tests | `tests/test_final_review_agent.py` — FR-DER coherence paths, audit_record_id guard, FR-GOV packet assembly, false-ready rejection, no lifecycle mutation, no Slice A conflation, tenant isolation, no registry default |
| Audit requirements | Step 00 `scripts/validate_agent_contract_block.py` PASS; pre-build gate via `audit_tools/complete_gate.py`; completion gate on implementation slice |
| Signed-spec dependencies | Template, `agent_contract.py` spine, boundary review MMI-DEC-240, #46 builder separation, Health Score deep dive |
| Build Authorization dependency | Contract placement only. No build until §11 + operator build authorization. Slice A tools remain immutable infrastructure. |

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-26 (draft placement · MMI-DEC-242):

| GAP (advisory draft) | Resolved value | Repo evidence |
|---|---|---|
| **Repo path** | `4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md` | All Agent Design Contracts live in `4. Product_Roadmap/` per template §1 |
| **#70 Slice A scope** | **Out of scope.** `complete_gate.py` + `package_auditor.py` stay infrastructure; not merged into `FinalReviewAgent` | `final_review_70_boundary.md` Slice A satisfied |
| **#70 Slice B scope** | Governed wrapper `final_review_001`: FR-DER (DER coherence + `audit_record_id`) + FR-GOV (pre-§11 Final Review Packet) | `agent_contract.py` `FINAL_REVIEW_AGENT_ID`; design tree §1.5 |
| **`MMI_GATE_REGISTRY.md` §3 checklist** | Registry is **DEPTH component status only** (#89–#102, RT) — **not** a full finalization artifact list. Authoritative §3 checklist derived from scoreboard Q4 L6 bar + template §6.2 + superintendent lifecycle (Step 00 → pre-build gate → build → completion gate → GATED → optional GOVERNED_AGENT) | `mmi/MMI_GATE_REGISTRY.md` header; scoreboard Q4 L6; MMI-DEC-* superintendent pattern |
| **Template section numbering** | This file follows template §0–§11 + Agent Design Contract block per #19/#65 pattern | `Agent_Design_Contract_Template_Deep_Dive.md` |
| **Evidence Stage 2/3 naming** | Stage 2 = **Supervised**; Stage 3 = **Production** per template §6.1 (not informal "Historical-real" / "Production-adjacent") | Template §6.0–§6.1 |
| **`READY-FOR-§11` vs lifecycle** | `READY-FOR-§11` ≠ `GATED` ≠ `GOVERNED_AGENT` ≠ build authorization. Packet is input to human §11 only. | MMI-DEC-235/238 GATED vs GOVERNED distinction |
| **#5 / #69 distinction** | #5 Decision Integrity = rubric guard (doc-only). #69 Swarm Health = consistency (separate future contract). #70 does not absorb either. | Scoreboard rows; MMI-DEC-240 |
| **Health Score weighting** | False-ready / human-caught miss hits **Demotion history** (15%) + **Validation** components heaviest per operator intent; logged in `decision_cycles_log.md` | `Agent_Health_Score_Deep_Dive.md` §2 |

**Remaining open (Matt / pre-build gate):**

| Open item | Blocker |
|---|---|
| FR-GOV candidate envelope final field list | PARK build until ES1 schema frozen in implementation |
| FR-DER coherence rules vs `client_facing_rubric` | Confirm non-duplication with #5 Decision Integrity doc surface |
| Contract §11 signature | **Done** — MMI-DEC-244 (`Matt Nichol June 26th 2026`) |
| Pre-build gate on this contract | **Done** — 0 blocking / 2 warnings MMI-DEC-243 (BUILD_QUEUE empty; worktree changed paths — cosmetic) |
| Explicit build authorization | Separate from §11 per established MMI pattern |

---

## §0 Purpose — the one invariant

**This agent assembles and checks the evidence trail and produces a Final Review Packet with a readiness verdict. It never signs, promotes, or authorizes anything.** `READY-FOR-§11` is a *precondition surfaced to a human* — not a decision, not a green light. Matt's §11 remains a mandatory human act performed **on top of** this review, never delegated to it. If this agent's verdict is ever treated as the approval, the contract has failed.

Slice B closes the spine gap left by `FINAL_REVIEW_AGENT_ID`: the Evidence Package Agent (#46) assembles; Final Review audits. Slice A gate tools remain the operator/build choke points for artifact claims — deliberately outside dispatch.

---

## §1 Scope

### In scope (Slice B)

- Agent Design Contract block governing `FinalReviewAgent` (`final_review_001`).
- **FR-DER mode:** read-only DER coherence audit; sole `audit_record_id` writer when checks pass.
- **FR-GOV mode:** Final Review Packet assembly for governance finalization candidates (agent build, contract sign, GATED reconcile, GOVERNED_AGENT promotion review).
- Evidence Stage 1 (Synthetic) declaration.
- Anti-rubber-stamp packet shape (§4).
- False-ready regression requirements (§6.5).

### Out of scope

- **Slice A:** `audit_tools/complete_gate.py`, `core/evidence_package/package_auditor.py` — unchanged infrastructure.
- Signing §11 on any contract or promoting any scoreboard row.
- Swarm Commander routing, detection, verification, or evidence assembly.
- Production dispatch, default registry, AUTH-5.
- Replacing Grok completion gate or package auditor invocation paths.

---

## §2 Locked design decisions

| # | Decision | Locked value |
|---|---|---|
| D1 | Slice split | Slice A = infra gates (satisfied). Slice B = this governed agent only. |
| D2 | Builder-auditor separation | #46 / assembler paths cannot set `audit_record_id`; only `final_review_001` may. |
| D3 | Verdict ≠ authorization | `READY-FOR-§11` and `audit_record_id` write are never approval to ship, promote, or sign. |
| D4 | Anti-rubber-stamp | Packet exposes underlying evidence refs; mandatory `could_not_verify` section; no bare "approved" token. |
| D5 | Layer 6 read-only | No write access to blackboard disposition, scoreboard, registry, or governance files from agent code. |
| D6 | Two entry modes | FR-DER (runtime case) + FR-GOV (superintendent finalization) share packet discipline, distinct input envelopes. |
| D7 | False-ready severity | Highest demotion weight; permanent regression per template §6.5. |
| D8 | Stage discipline | VISION Stage A; Evidence Stage 1 Synthetic default; Stage 2/3 per template §6.2 only. |
| D9 | Slice A immutability | No code path in `FinalReviewAgent` invokes or wraps `complete_gate.py` / `audit_package` as substitute for FR-GOV checks. |
| D10 | Claim-safe boundary | Inherited from `Compliance_and_Trend_Watch_Process.md` — surfaces readiness, not compliance guarantees. |

---

## §3 Review checklist (authoritative — reconciled)

Binding checks the agent must evaluate and surface in FR-GOV packets (and FR-DER where applicable). Source: scoreboard Q4 L6 + template §6.2 + superintendent lifecycle — **not** `MMI_GATE_REGISTRY.md` alone.

| Check ID | Check | Pass condition | Evidence ref type |
|---|---|---|---|
| C1 | Contract present | Agent Design Contract exists at `4. Product_Roadmap/` for the candidate agent/contract; Step 00 field block complete | Path + `validate_agent_contract_block.py` result |
| C2 | Pre-build gate (contract) | When finalizing contract sign: `audit_outputs/mmi_*_contract_gate_*.md` with **0 blocking** (warnings logged, not hidden) | Gate artifact path + hash |
| C3 | Implementation evidence | When finalizing build/GATED: implementation commit + focused test module exists | Git ref + test path |
| C4 | Completion gate | When finalizing GATED: `audit_outputs/<agent>_*.md` with **0 blocking** | Gate artifact path + hash |
| C5 | Evidence Stage | Declared stage matches template §6.1; ES1 default unless signed promotion record | Contract §6 table |
| C6 | Correction Evidence (#65) | When `candidate_kind` involves rule change: `#65` packet `SUFFICIENT` attached | `#65` envelope id |
| C7 | Adversarial hardening | When DEPTH component implicated: matching row in `MMI_GATE_REGISTRY.md` shows GATED + hardening claim satisfied | Registry row |
| C8 | Regression | Focused tests for candidate pass; FR-GOV may additionally require corpus replay fixture result at ES1 | Pytest log / fixture manifest |
| C9 | Blast radius | When mutation/rule surface: bounded blast-radius note present (BRC / sandbox pattern) | Structured note ref |
| C10 | Scoreboard row | Row exists; layer pinned; blockers accurately reflect state | Scoreboard excerpt |
| C11 | Health Score | When promoting GOVERNED_AGENT: Health Score board entry exists per BS-D7 | Scoreboard header row |
| C12 | Open items | **Zero** unresolved `PARK` / `REVISE` / `ESCALATE` in contract REPO_RECONCILIATION or linked MMI-DEC for this candidate | Decision log grep |
| C13 | FR-DER coherence | Verdict, evidence anchor, contributions, and client-safe narrative inputs are mutually consistent; no unsupported claims | DER field audit |
| C14 | Builder-auditor | `audit_writer_agent_id` is `final_review_001` iff `audit_record_id` set; assembler did not self-audit | Schema validation |

Checks marked **not applicable** must say so in the packet — not omitted.

---

## §4 Output — the Final Review Packet (`FINAL_REVIEW_PACKET_v1`)

Required sections:

1. **Candidate identity** — `candidate_kind`, `candidate_id`, `tenant_id` (if any), timestamp, agent version.
2. **Per-check status table** — §3 checks with `PASS` \| `FAIL` \| `N/A` and **evidence references** (paths, SHAs, gate ids) — not summaries-of-summaries.
3. **`could_not_verify`** — plain-language list of anything the agent could not confirm (missing artifact, unreadable path, registry gap).
4. **Readiness verdict** — exactly one of: `READY-FOR-§11` \| `NOT-READY` with blocking check ids.
5. **Reproducibility** — input manifest hashes, packet hash, tool versions.

**Anti-rubber-stamp rules:**

- Must not emit a standalone approval string (`APPROVED`, `SIGN NOW`, `CLEAR TO SHIP`).
- `READY-FOR-§11` requires all applicable §3 checks PASS; any FAIL → `NOT-READY`.
- Human §11 signer catching a defect the packet missed → **Final Review miss** (§6.5).

---

## §5 Failure modes

| Mode | Severity | Response |
|---|---|---|
| **False-ready** | Critical | Certified `READY-FOR-§11` or wrote `audit_record_id` while a §3 check would FAIL → permanent regression + demotion review; heaviest Health Score hit |
| **Human-caught miss** | High | §11 signer finds blocking issue not in packet → logged Final Review miss; feeds §6.5 hardening |
| **False NOT-READY** | Medium | Blocked clean candidate → friction; tune checks only via signed contract amendment, never by dropping C1–C14 below floor |
| **Self-approval** | Critical | Any path that promotes GATED/GOVERNED, signs §11, or marks complete → hard fail |
| **Slice A conflation** | Critical | Replacing `complete_gate.py` / package auditor with agent invocation → hard fail |
| **Enactment creep** | Critical | Mutating disposition, scoreboard, registry, or payment/containment state → hard fail |
| **Reasoning trace leak** | High | Storing chain-of-thought in DER → hard fail (spine rule) |
| **Tenant bleed** | Critical | Cross-tenant artifact or DER access → hard fail |

**Adversarial focus (pre-build / pre-§11):** can a candidate be crafted incomplete (missing completion gate, open PARK item, stale blocker) and still receive `READY-FOR-§11`? Implementation **must** include negative tests for each false-ready class.

---

## §6 Evidence Stage, promotion, and demotion

Per `Agent_Design_Contract_Template_Deep_Dive.md` §6:

| Stage | Data | May do | May NOT do |
|---|---|---|---|
| **1 — Synthetic** *(default)* | Synthetic DER fixtures + synthetic governance finalization manifests | FR-DER + FR-GOV packet assembly in sandbox | Real promotion flow; production dispatch |
| **2 — Supervised** *(proposed)* | Privacy-filtered historical cases (`#93` linkage when authorized) | Validate checks against past finalizations | Live sign-off path |
| **3 — Production** *(proposed)* | Live candidate signal | Produce packets on real candidates | **Sign / promote / authorize — never, any stage** |

### §6.5 Progressive hardening

- Every **false-ready** → new permanent regression test + demotion review input.
- Every **human-caught miss** at §11 → logged; if pattern repeats, new regression test.
- Re-promotion requires passing all hardening tests plus template §6.2 Stage gate.

**Health Score:** Demotion history component weighted heaviest for false-ready events per `Agent_Health_Score_Deep_Dive.md`.

---

## §7 Hard limits

- **No sign / promote / authorize path** — by construction.
- **`READY-FOR-§11` is not authorization.** §11 human review **mandatory regardless of verdict**.
- **`audit_record_id` is not client release.** Case output still requires operator/HITL path per design tree.
- **AUTH-5 blocked.** Safe-Stop (Matt-only) halts the agent.
- Scoreboard row + Health Score when build-authorized; **not** in `build_default_registry` at ES1.
- Dispatcher may route **review** tasks; agent output does not change routing authority.

---

## §8 Legal / non-guarantee

- MMI **surfaces readiness**; does not guarantee correctness of swarm decisions or contract quality.
- Matt / operator retains decision and liability.
- Forbidden-language scope: `Compliance_and_Trend_Watch_Process.md`.
- Final Review does not produce buyer-facing compliance claims.

---

## §9 Open questions (operator-only)

- **OQ-1 — FR-DER vs #5:** Exact boundary between Final Review coherence checks and Decision Integrity rubric guard — document-only overlap acceptable?
- **OQ-2 — FR-GOV automation:** Which superintendent transitions require mandatory FR-GOV packet vs operator manual checklist only at ES1?
- **OQ-3 — `audit_record_id` without FR-GOV:** Confirm FR-DER-only ES1 build is sufficient first slice before FR-GOV manifest parser.
- **OQ-4 — Stage 2 data:** Whether supervised finalization uses `#93` Privacy Filter envelopes exclusively.

---

## §10 Audit requirements

- Step 00: `python3 scripts/validate_agent_contract_block.py` on this file — expect PASS before pre-build gate.
- Pre-build gate: `audit_tools/complete_gate.py` with manifest listing all `files_read` source contracts.
- Adversarial cross-check focus before §11: **false-ready path** — incomplete candidate must not yield `READY-FOR-§11`.
- Completion gate on implementation slice after build authorization.
- Arch review: confirm no sign/promote/authorize code path in wrapper.

---

## §11 Sign-off

SIGNED. This locks D1–D10 for swarm agent #70 Final Review at **Evidence Stage 1 (Synthetic)**. Signing authorizes future `FinalReviewAgent` wrapper build + focused tests **only** after separate operator Build Authorization. Signing authorizes **no** §11 on other contracts, **no** scoreboard promotion to `GOVERNED_AGENT`, **no** default-registry registration, **no** production dispatch, **no** autonomous action, and **no** AUTH-5.

> §11 SIGNATURE — Matt Nichol June 26th 2026

---

## §12 Execution checklist (Cursor — placement complete)

1. [x] Reconcile §3 checklist against scoreboard Q4 L6 + template §6.2 + superintendent lifecycle (`MMI_GATE_REGISTRY.md` is partial).
2. [x] Reconcile against #70 Slice A (`final_review_70_boundary.md` — Slice A out of scope).
3. [x] Confirm placement: `4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md`.
4. [x] Arch review: no sign/promote/authorize path in contract design (D3, D5, §7).
5. [x] Adversarial cross-check documented: false-ready path (§5, §10).
6. [x] Scoreboard row #70 + Health Score weighting noted (post-build).
7. [x] MMI-DEC-242 placement decision recorded.
8. [x] Matt routing: pre-build gate **PASS** (MMI-DEC-243) → **Matt §11** (MMI-DEC-244).
9. [x] Closeout after §11: `lane_board_sync` → `dispatch --sync` → `dispatch --verify` → `pmv`.
