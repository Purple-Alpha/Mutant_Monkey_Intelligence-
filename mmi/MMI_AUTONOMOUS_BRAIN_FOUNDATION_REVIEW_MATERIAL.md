# MMI Autonomous Brain Foundation — Review Material (Pre-Contract)

**Status:** `DRAFT FOR ADVERSARIAL REVIEW — NOT SIGNED — NOT A CONTRACT`

**Classification:** `NEEDS_MMI_REVIEW` · `RESEARCH_INPUT` · `ADVERSARIAL_REVIEW` · doctrine/governance review material only

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Date placed:** 2026-06-19

**Placement authorization:** `MMI_AUTONOMOUS_BRAIN_REVIEW_MATERIAL_PLACEMENT` only

---

## Non-authorization block (read first)

This document is **review material only**. It does **not**:

- constitute a signed spec, §11 contract, or build authorization
- authorize implementation, automation, runtime wiring, or production dispatch
- authorize Cursor handoff beyond this single placement task
- authorize dispatcher rewrite, `scripts/mmi_dispatch.py` edits, or routing-behavior change
- authorize scoreboard schema change, scoreboard row promotion, or `SIGNED_UNBUILT` reconcile
- authorize parked roadmap draft promotion, git-tracking of parked drafts, or contract drafting from parked material
- imply Matt Nichol §11 signature or any operator signature
- authorize autonomous selection of build targets without Matt
- authorize registry population with live tasks, auto-prompt generation, contradiction-detection code, or dashboard/UI work
- authorize changes to `#47 Case Timeline` or `#48 Verification Outcome Agent`
- authorize Architectapp work or any non-authority-repo path

**All `AUTH-*` gates below remain future separate Matt approvals.** Nothing in this file activates a gate.

Matt Nichol remains final authority. MMI ranks and routes; Matt authorizes phase, scope, signatures, and hardening claims.

---

## §0 Purpose

Define the **foundation doctrine** for evolving Mutant Monkey Intelligence (MMI) from Stage 1 file-based governance (`mmi/*.md` + `scripts/mmi_dispatch.py --sync` / `--verify`) toward a safer **autonomous project brain** — without collapsing operator authority, builder/auditor separation, or evidence discipline.

The brain must:

1. Maintain **current project truth** from repo evidence (scoreboard, gate registry, decision log, git state).
2. **Score directions** and delegate the correct lane when evidence supports delegation.
3. Require **worker completions to update MMI first** before advancing routing state.
4. **Never** substitute rubric scores or dispatcher output for Matt's authorization decisions.

This file is pre-contract review input for adversarial critique (Codex/Gemini/Grok/Matt). It is not a deep-dive contract and carries no §11 block.

---

## §1 Source evidence (repo baseline at placement)

| Surface | Role today | Authority |
|---|---|---|
| `mmi/MMI_PROTOCOL.md` | MMI constitution; six outcomes; evidence standard | Stage 1 governance |
| `mmi/MMI_ROUTING_RULES.md` | Lane table; delegation scoring; worker-completion MMI-first rule | Stage 1 governance |
| `mmi/MMI_AUTHORITY_MATRIX.md` | Separation of duties; pre-build review posture | Stage 1 governance |
| `mmi/MMI_GATE_REGISTRY.md` | Component/gate status | Authority for gate truth |
| `mmi/MMI_DECISION_LOG.md` | Decision memory (`MMI-DEC-*`) | Authority for decisions |
| `mmi/MMI_INTAKE_RECORDS.md` | Intake before routing | Evidence intake |
| `MMI_CURRENT_STATE.md` | Derived routing block + human `LAST_COMPLETED` prose | Routing block = dispatcher-derived |
| `scripts/mmi_dispatch.py` | Derives MODE, TASK_SCOREBOARD, DIRECTION_SCOREBOARD, `--verify` | Executable Stage 1 brain |
| `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` | Build sequencer / BLOCKERS | Build truth input |
| `mmi/concepts/MMI_BOARD_ADVISORY_LAYER_CONCEPT.md` | Future advisory layer (parked concept) | Non-authoritative |
| `mmi/concepts/MMI_BRAIN_IMMUNE_LUNG_ZERO_TRUST_CONTROL_LOOP_CONCEPT.md` | Runtime control-loop research (parked) | Non-authoritative |
| `mmi/reviews/MMI_DISPATCHER_ROUTING_ALIGNMENT_REVIEW.md` | Gap analysis vs golden doctrine | Review only |

**Current dispatcher modes (derived, not rewritten here):** `BUILD`, `AUDIT`, `REVIEW`, `DESIGN`, `DELEGATE`, `PROJECT_DIRECTION_RESEARCH`, `ALL_CLEAR`.

**Worker-completion rule (existing doctrine):** append MMI evidence → update `LAST_COMPLETED` → `--sync` → commit routing-authority files → `--verify` PASS.

---

## §2 Foundation principles (candidate — adversarial review target)

| # | Principle | Repo anchor |
|---|---|---|
| P1 | Matt authorizes phase, scope, signatures, and acceptance; MMI assigns lane by task shape | `MMI_ROUTING_RULES.md` § Matt target vs MMI lane |
| P2 | A claim is not accepted without file path, commit hash, test output, or signed decision record | `MMI_PROTOCOL.md` evidence standard |
| P3 | Rubrics and dispatcher scores **rank**; they do not **decide** | `AGENTS.md` authority model |
| P4 | No model designs, builds, approves, and audits the same slice | `MMI_PROTOCOL.md` separation |
| P5 | Stage 1 MMI is file-based; runtime automation is not implied by this review material | `PROJECT_HANDSHAKE.md` / `MMI_PROTOCOL.md` Stage 1 |
| P6 | Worker completion updates MMI records before routing advances | `MMI_ROUTING_RULES.md` worker-completion section |
| P7 | ALL_CLEAR ≠ next-phase authorization; scored directions ≠ authorization | `MMI_ROUTING_RULES.md` |
| P8 | Parked drafts stay classified; intake classification ≠ promotion | `mmi/PARKED_DRAFT_CLASSIFICATIONS.md` |
| P9 | Authority repo only; Architectapp is not the governed swarm surface | `MMI_PROTOCOL.md` repo identity guard |

---

## §3 Proposed foundation layers (doctrine only — not built)

These layers describe a **future** autonomous brain stack. None are authorized by this file.

```text
Layer A — Truth surfaces (exists today)
  scoreboard + gate registry + decision log + git status + verify_build_truth

Layer B — Routing brain (exists today, Stage 1)
  mmi_dispatch.py derives MODE, delegation scores, project-direction scores

Layer C — Machine-readable task registry (NOT built)
  human-maintained structured task list; schema only at AUTH-3A

Layer D — MMI write mechanics (NOT built)
  governed updates to intake/decision/state on worker completion; AUTH-3B

Layer E — Prompt assembly (NOT built)
  auto-prompt generation from routing block; AUTH-4

Layer F — Contradiction surfacing (NOT built)
  automated doc/code contradiction reports; AUTH-5

Layer G — Operator dashboard (NOT built)
  read-only or advisory UI; AUTH-6
```

Layer C must not be confused with `collect_delegation_tasks()` — today that function **derives** tasks from repo evidence; it does not read a populated external registry file.

---

## §4 Authorization gates (future — separate Matt approvals)

Each gate is a **hard stop**. Implementation, dispatcher edits, or runtime behavior change require explicit operator authorization **after** adversarial review of this material (and usually a signed contract or promotion record).

| Gate | Scope | Authorized by this file? |
|---|---|---|
| **AUTH-1** | Place this review material in `mmi/` as DRAFT adversarial input | **YES** — `MMI_AUTONOMOUS_BRAIN_REVIEW_MATERIAL_PLACEMENT` only |
| **AUTH-2** | Dispatcher behavior change (new modes, scoring weights, lane rules, `--verify` doctrine checks) | **NO** |
| **AUTH-3A** | Machine-readable **registry format only** — schema, field names, closed enums, example empty template; **human-maintained**; no live task population | **NO** |
| **AUTH-3B** | MMI **write-access / status-transition mechanics** — code or automation that mutates `MMI_INTAKE_RECORDS.md`, `MMI_DECISION_LOG.md`, `MMI_GATE_REGISTRY.md`, or `MMI_CURRENT_STATE.md` routing block outside manual worker workflow | **NO** |
| **AUTH-4** | Auto-prompt generation (Cursor/Codex/Claude handoff text from routing state) | **NO** |
| **AUTH-5** | Contradiction-detection automation (doc vs code vs scoreboard scanners) | **NO** |
| **AUTH-6** | Dashboard / UI for MMI state | **NO** |
| **AUTH-7** | Autonomous target selection (dispatcher chooses build without Matt phase authorization) | **NO** |
| **AUTH-8** | Promotion to signed MMI Autonomous Brain contract (§11 deep-dive) | **NO** |

### AUTH-3 split rationale (hardening)

Prior combined "registry + write mechanics" gates create builder/auditor collapse risk: a single approval could both define the task schema and grant automation that writes authority files. Split enforces:

- **AUTH-3A:** format-only — reviewers can approve schema without approving writes.
- **AUTH-3B:** mechanics-only — write automation requires separate review of fail-closed rules, Matt-approval triggers, and audit trail.

### AUTH-3A — registry format only (draft schema sketch — not active)

Human-maintained file (proposed path only): `mmi/MMI_TASK_REGISTRY.json` or `.yaml` — **do not create at AUTH-1**.

Closed fields (candidate):

```text
task_id          — stable identifier
classification   — closed enum aligned with delegation scoring (SCOREBOARD_READY, INTAKE_CLASSIFY_BATCH, ...)
status           — open | delegated | completed | parked | blocked
source_evidence  — file paths / commit hashes
assigned_worker  — Cursor | Codex | Claude | ...
operator_action_required — yes | no
matt_approval_required   — yes | no
blockers         — closed vocabulary only
```

**Non-goals at AUTH-3A:** no runtime reader in dispatcher; no auto-population from scoreboard; no default tasks.

### AUTH-3B — write mechanics (draft requirements sketch — not active)

Any future write automation must:

1. Fail closed if `--verify` would FAIL after the write.
2. Never append ACCEPT without evidence fields populated.
3. Never flip scoreboard rows or gate registry without matching `MMI-DEC-*` decision record.
4. Never set `GOVERNED_AGENT`, `GATED`, or hardening claims without Matt decision log entry.
5. Preserve manual override: Matt can edit files directly; automation must not fight operator edits.
6. Log every mutation with timestamp, worker lane, and triggering commit hash.

---

## §5 Explicit non-goals

- Not a replacement for `mmi/MMI_GATE_REGISTRY.md` or scoreboard.
- Not authorization to populate a real task registry with live delegable work.
- Not authorization to run always-on MMI daemon, hooks, or silent background sync.
- Not authorization to push, deploy, or integrate Architectapp ops surfaces.
- Not authorization to merge parked concept docs into authority.
- Not authorization to skip Grok `complete_gate.py` on substantive implementation slices.
- Not authorization to treat `PROJECT_DIRECTION_RESEARCH` recommendation as build approval.

---

## §6 Adversarial review questions

Reviewers should attack:

1. Does AUTH-3A/3B split prevent registry-write authority collapse?
2. Does any prose imply Matt signature or §11 lock without a signature block?
3. Does "autonomous brain" language violate `MMI_PROTOCOL.md` ("not one big AI brain")?
4. Would AUTH-3B automation recreate authority drift (model accepts its own work)?
5. Does Layer C registry duplicate `collect_delegation_tasks()` without clear boundary?
6. Does prompt generation (AUTH-4) launder dispatcher output as operator authorization?
7. Are contradiction scanners (AUTH-5) scoped to report-only without auto-REJECT?
8. Does dashboard work (AUTH-6) expose client-facing or insurance-forbidden claims?

---

## §7 Relationship to sibling concepts

| Sibling | Relationship |
|---|---|
| `MMI_BOARD_ADVISORY_LAYER_CONCEPT.md` | Future advisory scoring layer; this foundation is routing/truth/evidence substrate |
| `MMI_BRAIN_IMMUNE_LUNG_*` | Runtime swarm control loop; orthogonal to file-based MMI brain |
| `MMI_DISPATCHER_ROUTING_ALIGNMENT_REVIEW.md` | Documents gaps in committed dispatcher vs golden doctrine; patches need AUTH-2 |
| Parked roadmap drafts | Unrelated; no promotion implied |

---

## §8 Open questions (operator-only)

1. Should AUTH-3A registry live under `mmi/` or `audit_outputs/`?
2. Should AUTH-3B writes be limited to `LAST_COMPLETED` + intake append, or also gate registry?
3. Is AUTH-4 prompt generation allowed to include scored direction text without `CANDIDATES_NOT_AUTHORIZATION` guard repetition?
4. Does AUTH-8 deep-dive live in `4. Product_Roadmap/` or `mmi/`?

No fork resolved until Matt records a decision in `MMI_DECISION_LOG.md`.

---

## §9 Sign-off

**UNSIGNED — NOT A CONTRACT — NO §11 BLOCK.**

This review material does not carry a signature line. Promotion to signed contract requires separate `AUTH-8` authorization, adversarial review completion, Grok gate on the contract slice, and Matt §11 signature on a future deep-dive.

> Matt Nichol ____________________  Date __________  (not required for this review material)

---

**End of review material. Placement does not authorize implementation.**
