# MMI Autonomous Brain Foundation — Review Material (Pre-Contract)

**Status:** `DRAFT FOR ADVERSARIAL REVIEW — NOT SIGNED — NOT A CONTRACT`

**Classification:** `NEEDS_MMI_REVIEW` · `RESEARCH_INPUT` · `ADVERSARIAL_REVIEW` · doctrine/governance review material only

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Date placed:** 2026-06-19

**Reconciliation patch:** 2026-06-19 (`MMI_AUTONOMOUS_BRAIN_REVIEW_MATERIAL_RECONCILIATION_PATCH`)

**Hardening patch:** 2026-06-19 (`MMI_AUTONOMOUS_BRAIN_REVIEW_HARDENING_AND_TIER1_CONTRACT_DRAFT`) — adversarial review PASS WITH CHANGES wording fixes.

**Placement authorization:** Review-material placement, reconciliation, hardening, and Tier 1 contract **draft** only — not Tier 1 implementation.

---

## Non-authorization block (read first)

This document is **review material only**. It does **not**:

- constitute a signed spec, §11 contract, or build authorization
- authorize implementation, automation, runtime wiring, or production dispatch
- authorize Tier 1 schema/template file creation (see separate Tier 1 contract draft; unsigned)
- authorize Cursor handoff beyond placement, reconciliation, hardening, adversarial review, or Tier 1 contract drafting
- authorize dispatcher rewrite, `scripts/mmi_dispatch.py` edits, or routing-behavior change (**AUTH-2 alone never grants edits**; see **AUTH-2-EDIT**)
- authorize scoreboard schema change, scoreboard row promotion, or `SIGNED_UNBUILT` reconcile
- authorize parked roadmap draft promotion, git-tracking of parked drafts, or contract drafting from parked material
- imply Matt Nichol §11 signature or any operator signature
- authorize autonomous selection of build targets without Matt (pre-AUTH-5) or without separate AUTH-5 approval (post-AUTH-5)
- authorize registry population with live tasks, auto-prompt generation, contradiction-detection automation, dashboard/UI work, or always-on sync daemons/hooks/watchers
- authorize changes to `#47 Case Timeline` or `#48 Verification Outcome Agent`
- authorize Architectapp work or any non-authority-repo path
- activate any `AUTH-*` gate (including AUTH-1 passive recording automation)

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

## §1 Source evidence (repo baseline)

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

**Approved repo surfaces for evidence read (lifecycle §7):** scoreboard, gate registry, decision log, intake records, signed contracts in repo, git status, `scripts/verify_build_truth.py`, committed test output referenced in MMI records — not chat transcripts, not Architectapp, not unpromoted parked drafts as authority.

**Tier 1 stability (candidate — for future Tier 2 promotion discussion):** `--verify` PASS, 0 drift BLOCK from `verify_build_truth.py`, and N consecutive worker cycles satisfying lifecycle §7 — not activated by this document.

---

## §2 Authorization tiering (no tier approved by this document)

No tier is activated by this review material. **AUTH-5 cannot be bundled with earlier tiers.** `MMI_BOARD_ADVISORY_LAYER_CONCEPT.md` is **outside** this foundation tier model until its own signed contract.

| Tier | Name | Scope | Example capabilities (future only) |
|---|---|---|---|
| **Tier 1** | Passive / foundation only | Read approved surfaces; record; score; rank; **record contradiction flags for operator review**; append Decision Audit Appendix entries; **no** dispatcher edits; **no** autonomous selection; **no** contradiction automation | Passive MMI records, scoring rubrics, manual/operator-reviewed flags, appendix append |
| **Tier 2** | Tooling on trusted Tier 1 foundation | Requires Tier 1 stable + **separate AUTH gate per tool** (not one bundled “Tier 2 package”) | AUTH-3A registry format, AUTH-3B write mechanics, AUTH-4 auto-prompt, AUTH-7 contradiction tooling |
| **Tier 3** | Autonomy last | Requires Tier 1 + Tier 2 foundations + **standalone AUTH-5** | AUTH-5 autonomous MMI task selection only — terminal, highest-risk, never bundled |

**Tier 1 contradiction rule:** Tier 1 may **record or flag** contradictions for **operator review only**. Tier 1 must **not** create contradiction-detection automation, automated halt/block scanning, or report tooling. Automated contradiction halt, block, scanning, or report tooling requires **AUTH-7** or an explicit future `MMI-DEC-*` naming that scope.

**Rule:** Tier 3 (AUTH-5) is never approved together with Tier 1 or Tier 2 in a single operator authorization. AUTH-5 is a standalone terminal gate.

---

## §3 Authorization gates (future — separate Matt approvals)

Each gate is a **hard stop**. Nothing below is activated by this review material.

| Gate | Scope | Authorized by this file? |
|---|---|---|
| **AUTH-1** | **Passive records only** — MMI may read approved surfaces and append passive doctrine/evidence records (intake, decision log entries, Decision Audit Appendix); **no** dispatcher edits; **no** autonomous selection; **no** registry writes; **no** scoreboard/gate-registry mutation by automation; **no** contradiction automation | **NO** |
| **AUTH-2** | **Dispatcher respect-only** — MMI must **read and honor** current `scripts/mmi_dispatch.py` output and routing doctrine; **AUTH-2 alone never authorizes** editing `scripts/mmi_dispatch.py`, changing dispatcher modes/scoring/`--verify` doctrine, or altering dispatcher output semantics | **NO** |
| **AUTH-2-EDIT** | **Dispatcher code/behavior change** — any edit to `scripts/mmi_dispatch.py`, dispatcher output fields, routing derivation logic, or `--verify` doctrine checks; requires explicit operator authorization **and** recorded `MMI-DEC-*` naming AUTH-2-EDIT (or equivalent); **not** implied by AUTH-2 | **NO** |
| **AUTH-3A** | Machine-readable **registry format only** — schema, field names, closed enums, empty template; **human-maintained**; no live task population | **NO** |
| **AUTH-3B** | MMI **write-access / status-transition mechanics** — governed automation that mutates MMI authority files per fail-closed rules | **NO** |
| **AUTH-4** | **Auto-prompt generation** — assembly of worker handoff text from routing state; must repeat `CANDIDATES_NOT_AUTHORIZATION` / recommendation-not-authorization guards | **NO** |
| **AUTH-5** | **Autonomous MMI task selection** — MMI may select the next task/build target without Matt phase pick; **final / highest-risk / terminal standalone gate**; **isolated** — never bundled with AUTH-1–4, AUTH-2-EDIT, Tier 2 tooling, or AUTH-7 | **NO** |
| **AUTH-6** | **Owner brief / dashboard mode** — operator-facing summary surface (read-only or advisory); verify-before-brief ordering required | **NO** |

### Additive future-only gates (do not change AUTH-1–6 meanings)

| Gate | Scope | Notes |
|---|---|---|
| **AUTH-7** | Contradiction-detection **tooling** (Tier 2) — automated doc/code/scoreboard **reports** or automated halt; report-only default; no silent resolution; **not** AUTH-5 | **NO** — additive; autonomy stays AUTH-5 only |
| **AUTH-8** | Promotion to signed MMI Autonomous Brain **§11 deep-dive contract** | **NO** — meta-gate for contract path only |

### AUTH-3 split rationale (hardening)

Prior combined "registry + write mechanics" gates create builder/auditor collapse risk. Split enforces:

- **AUTH-3A:** format-only — reviewers approve schema without approving writes.
- **AUTH-3B:** mechanics-only — write automation requires separate fail-closed review.

### AUTH-3A — registry format only (draft schema sketch — not active)

Proposed path only: `mmi/MMI_TASK_REGISTRY.json` or `.yaml` — **do not create without AUTH-3A approval**.

Closed fields (candidate):

```text
task_id          — stable identifier
classification   — closed enum aligned with delegation scoring
status           — open | delegated | completed | parked | blocked
source_evidence  — file paths / commit hashes
assigned_worker  — Cursor | Codex | Claude | ...
operator_action_required — yes | no
matt_approval_required   — yes | no
blockers         — closed vocabulary only
```

**Non-goals at AUTH-3A:** no runtime dispatcher reader; no auto-population from scoreboard; no default tasks.

### AUTH-3B — write mechanics (draft requirements sketch — not active)

Any future write automation must:

1. Fail closed if `--verify` would FAIL after the write.
2. Never append ACCEPT without evidence fields populated.
3. Never flip scoreboard rows or gate registry without matching `MMI-DEC-*` decision record.
4. Never set `GOVERNED_AGENT`, `GATED`, or hardening claims without Matt decision log entry.
5. Preserve manual override: Matt can edit files directly; automation must not fight operator edits.
6. Log every mutation with timestamp, worker lane, and triggering commit hash.

### AUTH-5 isolation rule

AUTH-5 is the **only** gate that grants autonomous task selection. It is:

- **Terminal** — highest-risk authorization in this foundation model.
- **Standalone** — cannot be approved in the same operator instruction as AUTH-1–4, AUTH-2-EDIT, AUTH-3A, AUTH-3B, Tier 2 tooling, or AUTH-7.
- **Post-conditions** — if ever authorized, `decided_by = MMI` only for selection events (§6) recorded in Decision Audit Appendix; all other decisions remain `decided_by = MATT` unless separately authorized.

---

## §4 Task registry authority boundary (`MMI_TASK_REGISTRY`)

When AUTH-3A is approved in the future, `MMI_TASK_REGISTRY` (or equivalent) is source of truth for **task lifecycle state only**.

It is **not**:

- signed contract authority
- component build authority
- git truth
- scoreboard authority
- gate-registry authority
- dispatcher input surface (until separate authorization names registry-fed routing)
- operator signature or §11 signature substitute

**Registry not dispatcher input:** `MMI_TASK_REGISTRY` is **not** a dispatcher input surface until a separate authorization (e.g. future `MMI-DEC-*` or dedicated gate) explicitly names **registry-fed routing**. Registry existence, schema publication, or empty template files must **not** change `scripts/mmi_dispatch.py` routing behavior.

Today `collect_delegation_tasks()` **derives** candidates from repo evidence; it does not read a populated `MMI_TASK_REGISTRY`. The registry must not be confused with scoreboard rows or `SIGNED_UNBUILT` visibility.

---

## §5 Dispatcher authority boundary

| Rule | Requirement |
|---|---|
| Routing scope | Dispatcher-derived state in `MMI_CURRENT_STATE.md` routing block governs **current routing state only** — MODE, delegated task, direction scoreboard display |
| Direct authority | Scoreboard, gate registry, decision log, signed §11 contracts, and git state remain **direct authority evidence** |
| Conflict handling | If dispatcher output contradicts direct repo/git/signed-contract/scoreboard evidence, MMI must flag a **BLOCK contradiction** (authority BLOCK — distinct from drift BLOCK in `verify_build_truth.py`) and **halt advancement** |
| No silent override | Dispatcher output does **not** silently override direct authority evidence |
| AUTH-2 | **Respect-only** — read and honor dispatcher output; **never** edit dispatcher code or output semantics under AUTH-2 alone |
| AUTH-2-EDIT | Any dispatcher behavior/code/output change requires **AUTH-2-EDIT** plus recorded `MMI-DEC-*` and explicit operator authorization |

---

## §6 Decision Audit Appendix and selection events (doctrine — not built)

Future Tier 1 passive recording surface (append-only). Not activated by this review material.

### Selection event (definition)

A **selection event** is any point where a single candidate becomes the active routed target, including when:

- `NEXT_DELEGATED_TASK` is set (including mechanical top-score delegation under `MODE: DELEGATE`)
- `RECOMMENDED_DIRECTION` is emitted under `MODE: PROJECT_DIRECTION_RESEARCH`
- any equivalent current-state routed target field names the single active candidate

Each selection event requires a Decision Audit Appendix entry when the appendix exists (including mechanical delegation — alternatives must still be preserved).

### `decided_by` rules

- **Before AUTH-5:** `decided_by = MATT` for all selection events (including when dispatcher mechanically picks top delegation task — Matt retains phase authority).
- **After AUTH-5 only,** if ever separately authorized: `decided_by = MMI` for autonomous-selection events within AUTH-5 scope only — never for signatures, hardening claims, or gate promotions.

### Appendix requirements

1. Record **every eligible candidate** considered at a selection point.
2. Preserve **lower-ranked and non-selected** alternatives with scores/reasoning.
3. Store **full scoring reasoning** (axis breakdown where applicable).
4. **Append-only / non-deleting** — rejected, parked, and superseded entries are never deleted.
5. **`decided_by`** per rules above.

Proposed path (not created without authorization): `mmi/MMI_DECISION_AUDIT_APPENDIX.md` or structured JSONL under `mmi/history_intake/`.

---

## §7 Lifecycle ordering (mandatory chain)

### Routing state advance (definition)

**Routing state advance** means a new **MODE**, **NEXT_DELEGATED_TASK**, **RECOMMENDED_DIRECTION**, scoreboard lifecycle flip, or equivalent **active routing change** — not prose-only `LAST_COMPLETED` edits alone.

`python3 scripts/mmi_dispatch.py --sync` alone is **not** final advancement unless followed by **commit** (when routing-authority files changed) and **`--verify` PASS**.

### Mandatory chain

No step may be skipped. Failure at any step **blocks advancement**.

```text
1. Evidence read from approved repo surfaces (§1)
2. MMI detects candidate, gap, contradiction, or stale state
3. MMI scores candidates (delegation rubric or project-direction rubric)
4. MMI marks each candidate eligible or blocked (with reason + evidence cite)
5. If BLOCK contradiction vs direct authority → halt (§5); no advance
6. PRE-AUTH-5: Matt selects among scored candidates (recommendation ≠ authorization)
7. POST-AUTH-5: MMI may select only if AUTH-5 separately authorized — if ever
8. Worker lane assigned by MMI routing doctrine (Matt does not pick lane routinely)
9. Worker prompt generated only if AUTH-4 separately authorized — else manual prompt
10. Matt manually dispatches worker under current rules (no automatic worker dispatch without authorization)
11. Worker returns completion packet (§8 I15 — closed field set)
12. Incomplete packet → auto-reject; no MMI record advance
13. MMI updates its own records first (intake / decision log / LAST_COMPLETED / appendix)
14. python3 scripts/mmi_dispatch.py --sync
15. If routing-authority files changed → commit required before final verify/complete
16. python3 scripts/mmi_dispatch.py --verify
17. Verify FAIL → halt; no owner brief; no promotion; no routing state advance
18. Owner brief / dashboard (AUTH-6) only after verify PASS — if AUTH-6 ever authorized
```

---

## §8 Non-negotiable invariants (closed list)

| ID | Invariant |
|---|---|
| I1 | **Evidence-only assertions** — no claim without file path, commit hash, test output, or signed decision record |
| I2 | **Recommendation is not authorization** — scores, rankings, and `RECOMMENDED_DIRECTION` do not authorize work |
| I3 | **Update-before-advance** — MMI records updated before routing state advances (§7 definition) |
| I4 | **Incomplete packet auto-reject** — missing completion fields block intake advance |
| I5 | **Verify failure halts advancement** — `--verify` FAIL stops delegation, brief, promotion, and routing state advance |
| I6 | **Non-deletion** — rejected, parked, and superseded entries are never deleted from appendix or intake history |
| I7 | **Lane purity** — one lane per task; no model designs, builds, approves, and audits the same slice |
| I8 | **No MMI self-expansion** — MMI cannot authorize its own scope growth; Matt authorizes each AUTH gate |
| I9 | **Architectapp out of scope** — governed swarm/MMI runtime authority repo only |
| I10 | **No silent contradiction resolution** — BLOCK contradictions halt; Matt or explicit decision record resolves |
| I11 | **Alternatives preserved** — Decision Audit Appendix retains non-selected candidates |
| I12 | **AUTH-5 isolated** — autonomous selection is terminal standalone authorization; never bundled |
| I13 | **`BUILD_AUTHORIZATION_IMPLIED` disarmed** — mechanical dispatcher/sequencer language only; never operator build authorization; cannot override signed contract state, scoreboard state, lifecycle-visible evidence, or Matt authorization |
| I14 | **Grok / gate discipline** — substantive contract/build slices that claim gate closure require applicable gate evidence, including `complete_gate.py` Grok result where current MMI workflow requires it |
| I15 | **Worker packet / manifest discipline** — worker completion must include a closed packet: files changed, scope check, tests/gates run, deviations, verify output, git status, and no-out-of-scope confirmations |
| I16 | **CANDIDATES not authorization** — lower-ranked `CANDIDATES`, scored alternatives, and direction options are context only; not delegable work unless Matt selects or separately authorizes |

---

## §9 Falsifiable acceptance tests (review-stage — not implementation)

These tests validate **review material and future doctrine compliance**. They do not authorize building test harnesses unless separately approved.

| Test ID | Name | Pass condition |
|---|---|---|
| T1 | Evidence citation | Every scored candidate cites at least one approved surface path or commit hash |
| T2 | Rejection | Incomplete worker packet (missing any I15 field) is rejected without MMI record advance |
| T3 | Authority boundary | Dispatcher recommendation does not flip scoreboard or gate registry without `MMI-DEC-*` |
| T4 | Non-deletion | Parked/rejected/superseded appendix entries remain after new selections |
| T5 | Lane purity | Same slice is not assigned to build + audit + accept in one lane chain |
| T6 | Out-of-scope leakage | No Architectapp path, parked draft, or #47/#48 mutation in MMI brain scope |
| T7 | Ordering | Verify runs after MMI record update and required commit; brief never precedes verify PASS |
| T8 | Menu-framing | Output includes `CANDIDATES_NOT_AUTHORIZATION` or equivalent guard |
| T9 | Silent resolution | BLOCK contradiction does not auto-clear without operator decision record |
| T10 | Alternative preservation | Decision Audit Appendix lists non-selected candidates with scores and `decided_by` |
| T11 | AUTH-5 isolation | Autonomous selection authorization is never co-issued with AUTH-1–4, AUTH-2-EDIT, or Tier 2 tooling |
| T12 | Dispatcher-vs-scoreboard conflict | Injected conflict (e.g. MODE:BUILD with 0 SIGNED_UNBUILT) triggers BLOCK contradiction flag and halts advance — when enforcement exists |
| T13 | BUILD_AUTHORIZATION_IMPLIED disarmed | `BUILD_AUTHORIZATION_IMPLIED: YES` with 0 SIGNED_UNBUILT does not authorize build or override scoreboard |
| T14 | Registry not dispatcher input | Creating registry schema/template does not change `collect_delegation_tasks()` or routing output unless registry-fed routing separately authorized |
| T15 | Selection event + decided_by | Every selection event (§6) produces appendix entry with alternatives and correct `decided_by` — when appendix exists |
| T16 | Incomplete packet auto-reject | Packet missing verify output or git status is rejected without record advance |

---

## §10 What must NOT be built yet

This review material authorizes **none** of the following:

- dispatcher rewrite or `scripts/mmi_dispatch.py` edits (requires AUTH-2-EDIT)
- populated `MMI_TASK_REGISTRY` with live delegable tasks
- registry-fed dispatcher routing without separate authorization
- scoreboard schema changes or row promotion
- auto-prompt generation code (AUTH-4)
- contradiction-detection automation (AUTH-7)
- dashboard / UI / owner brief runtime (AUTH-6)
- automatic worker dispatch without Matt manual dispatch under current rules
- always-on sync daemon, hooks, background automation, watcher processes, or scheduled `--sync`
- parked roadmap draft promotion or git-tracking
- `#47 Case Timeline` or `#48 Verification Outcome Agent` changes
- Architectapp integration or ops-surface wiring
- AUTH-5 autonomous task selection (pre-standalone AUTH-5 approval)
- Tier 1 schema/template **implementation** without signed Tier 1 contract + separate build authorization

---

## §11 Adversarial review questions

1. Does AUTH-3A/3B split prevent registry-write authority collapse?
2. Does AUTH-5 isolation prevent bundling autonomy with tooling gates?
3. Does AUTH-2 / AUTH-2-EDIT split prevent accidental dispatcher rewrite authorization?
4. Does BLOCK-on-conflict (§5) prevent dispatcher laundering over scoreboard/contracts?
5. Does Decision Audit Appendix prevent alternative deletion and decision laundering?
6. Does lifecycle §7 prevent verify-after-brief ordering violations?
7. Does I13 prevent `BUILD_AUTHORIZATION_IMPLIED` laundering as build approval?
8. Does "autonomous brain" language violate `MMI_PROTOCOL.md` ("not one big AI brain")?
9. Does AUTH-4 prompt generation repeat recommendation-not-authorization guards?
10. Does AUTH-6 owner brief expose client-facing or insurance-forbidden claims?

---

## §12 Relationship to sibling concepts

| Sibling | Relationship |
|---|---|
| `MMI_BOARD_ADVISORY_LAYER_CONCEPT.md` | Outside foundation tier model until own signed contract |
| `MMI_BRAIN_IMMUNE_LUNG_*` | Runtime swarm control loop; orthogonal to file-based MMI brain |
| `MMI_DISPATCHER_ROUTING_ALIGNMENT_REVIEW.md` | Gap analysis; dispatcher edits require **AUTH-2-EDIT** |
| `MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` | Tier 1 implementation contract draft — unsigned; not implementation auth |
| Parked roadmap drafts | Unrelated; no promotion implied |

---

## §13 Open questions (operator-only)

1. Should Decision Audit Appendix live as markdown or JSONL?
2. Should AUTH-3B writes include gate registry or only intake + `LAST_COMPLETED`?
3. **AUTH-7 default:** contradiction reports flag BLOCK for Matt review only (Tier 1 posture); automated halt requires explicit `MMI-DEC-*` — default per hardening patch unless Matt changes.
4. Does AUTH-8 deep-dive live in `4. Product_Roadmap/` or `mmi/`?

No fork resolved until Matt records a decision in `MMI_DECISION_LOG.md`.

---

## §14 Stage 1 doctrine-only gaps (not enforced in code today)

At review-material stage, the following are **doctrine only** — not implemented or enforced in `scripts/mmi_dispatch.py` or runtime:

| Capability | Status |
|---|---|
| BLOCK-on-conflict (authority BLOCK vs scoreboard/contracts) | Doctrine §5 — not wired in dispatcher |
| Decision Audit Appendix | Doctrine §6 — no file/surface exists |
| `MMI_TASK_REGISTRY` mechanics | Schema may be drafted; no populated registry; not dispatcher input |
| Registry-fed routing | Not authorized; dispatcher unchanged |
| Auto-prompt generation | AUTH-4 — not built |
| Contradiction tooling / automation | AUTH-7 — not built; Tier 1 flags manual only |
| Owner dashboard / brief | AUTH-6 — not built |
| Autonomous task selection | AUTH-5 — not authorized |
| AUTH-2-EDIT dispatcher changes | Not authorized |
| Always-on sync / hooks / watchers | Prohibited §10 |

Promoting to signed contract or implementation requires explicit gap closure per gate, not assumption that prose equals runtime behavior.

---

## §15 Sign-off

**UNSIGNED — NOT A CONTRACT — NO §11 BLOCK.**

Promotion to signed contract requires separate **AUTH-8** authorization, adversarial review completion, Grok gate on the contract slice, and Matt §11 signature on a future deep-dive.

> Matt Nichol ____________________  Date __________  (not required for this review material)

---

**End of review material. Hardening patch does not authorize implementation.**
