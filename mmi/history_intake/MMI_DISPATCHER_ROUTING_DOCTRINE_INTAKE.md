# MMI_DISPATCHER_ROUTING_DOCTRINE_INTAKE.md — Dispatcher Lane-Selection History

> **NON-AUTHORITATIVE INTAKE — EVIDENCE, NOT AUTHORITY.**
> This file classifies Cursor/Matt and ChatGPT/Matt session history about **MMI dispatcher
> routing doctrine becoming executable**. It does **not** authorize build, change routing
> authority, or promote claims without repo verification.
>
> **Source type:** ChatGPT/Matt or Cursor/Matt MMI routing-status history  
> **Authority:** Evidence only until repo verified  
> **Primary classification:** `NEEDS_MMI_REVIEW`  
> **Secondary:** `BUILT_NEEDS_VERIFICATION`, `SUPPORTED_BY_REPO` (where verified below),
> `CONTRADICTION`, `GOVERNANCE/MMI ITEM`  
> **Compiled:** 2026-06-16  
> **Matt approval required:** Review golden doctrine for promotion into standing MMI authority

---

## Intake entry (canonical summary)

```
Item:
MMI dispatcher lane-selection doctrine and Stage 1 routing status

Classification:
NEEDS_MMI_REVIEW / BUILT_NEEDS_VERIFICATION

Evidence summary:
History claims MMI dispatcher routes from scoreboard (not hand-edited prose); Codex added
to routing rules and authority matrix; BUILD lane = Cursor → Codex pre-build review →
Cursor build; independent review routes to Codex with OPERATOR_ACTION_REQUIRED: NO;
MMI_CURRENT_STATE auto-syncs on default dispatcher run; ALL_CLEAR means Matt names next
phase target but does not manually pick Cursor vs Codex.

Golden candidate:
"Matt names the authorized target; MMI assigns the lane."

Repo verification required:
scripts/mmi_dispatch.py, mmi/MMI_ROUTING_RULES.md, mmi/MMI_AUTHORITY_MATRIX.md,
MMI_CURRENT_STATE.md, PROJECT_HANDSHAKE.md, mmi/MMI_GATE_REGISTRY.md, scoreboard,
mmi_dispatch.py --verify output.

Do not promote without verification:
ALL_CLEAR, #99–#102 accepted, parents hardened, dispatcher active, auto-sync, verify PASS.
```

---

## Golden doctrine (candidate — not authority until MMI/Matt promotes)

These principles are **worth preserving** and align with `AGENTS.md` §2.2:

1. **Authority split:** Matt picks phase / authority. MMI picks the lane. Matt should not
   manually choose Cursor vs Codex on every routine task.

2. **BUILD lane policy:**
   ```
   Cursor (draft plan) → Codex (pre-build review) → Cursor (build)
   ```

3. **Independent review policy:**
   ```
   Independent review → Codex
   OPERATOR_ACTION_REQUIRED: NO (for normal independent-review routing)
   ```

4. **ALL_CLEAR semantics:**
   ```
   ALL_CLEAR = queue empty for scoreboard-derived work
   ALL_CLEAR ≠ authorization of the next phase
   Matt still names the next target (build / research / design)
   ```

**Promotion status:** `NEEDS_MMI_REVIEW` — doctrine is reflected in uncommitted
`mmi/MMI_ROUTING_RULES.md` and `scripts/mmi_dispatch.py`; not yet committed or verified
clean by `--verify`.

---

## 4. Governance / MMI items

| Item | Evidence | Classification |
|---|---|---|
| Lane-selection doctrine: Matt = phase/authority; MMI = lane | Session history; `AGENTS.md` §2.2; uncommitted `mmi/MMI_ROUTING_RULES.md` L5–36 | `GOVERNANCE/MMI ITEM` — `NEEDS_MMI_REVIEW` |
| BUILD lane Codex pre-build step wired in dispatcher | Uncommitted `scripts/mmi_dispatch.py` (`PRE_BUILD_REVIEW`, `ASSIGNED_TO` BUILD branch) | `BUILT_NEEDS_VERIFICATION` |
| Independent review → Codex in dispatcher | Uncommitted `scripts/mmi_dispatch.py` REVIEW branch | `BUILT_NEEDS_VERIFICATION` |
| Codex column in authority matrix | Uncommitted `mmi/MMI_AUTHORITY_MATRIX.md` | `BUILT_NEEDS_VERIFICATION` |
| Default auto-sync of `MMI_CURRENT_STATE.md` routing block | Uncommitted `scripts/mmi_dispatch.py` (`--no-sync` opt-out) | `BUILT_NEEDS_VERIFICATION` |
| Stage 1 MMI: file-based governance + executable dispatcher | `mmi/MMI_PROTOCOL.md`; `scripts/mmi_dispatch.py`; `mmi/MMI_GATE_REGISTRY.md` | `SUPPORTED_BY_REPO` (governance exists); runtime automation still `NOT active` per handshake |
| ALL_CLEAR terminal state when queue empty | Live dispatcher output 2026-06-16 | `SUPPORTED_BY_REPO` (verified run) |

---

## 9. Contradictions or drift risks

| # | Risk | Evidence | Classification |
|---|---|---|---|
| 1 | **`PROJECT_HANDSHAKE.md` says "Dispatcher integration: NOT active"** while dispatcher runs and derives routing | `PROJECT_HANDSHAKE.md` L38 vs live `python3 scripts/mmi_dispatch.py` | `CONTRADICTION` — handshake stale on dispatcher status |
| 2 | **Handshake HEAD/date block stale** (50b58a8 / 2026-06-13) vs current adversarial/MMI state | `PROJECT_HANDSHAKE.md` L6–17 vs `mmi/MMI_GATE_REGISTRY.md` | `CONTRADICTION` (pre-existing; see ChatGPT intake §9) |
| 3 | **Doctrine in chat vs committed repo** — Codex routing + auto-sync exist only in **uncommitted** diff | `git status` 2026-06-16: `M mmi/MMI_*.md`, `M scripts/mmi_dispatch.py` | `CONTRADICTION` / drift until committed |
| 4 | **`--verify` FAIL while routing changes uncommitted** | Verify output: `routing-authority files committed — uncommitted: scripts/mmi_dispatch.py` | Expected; do not treat as "verify broken" — treat as **work-in-progress** |
| 5 | **Multiple current-state surfaces** can disagree | `PROJECT_HANDSHAKE`, `MMI_CURRENT_STATE`, `MMI_HEALTH_STATE`, scoreboard | Standing risk; authority precedence = gate registry + decision log + dispatcher `--verify` |

---

## 10. Items that need repo verification

Repo check run: **2026-06-16** (`python3 scripts/mmi_dispatch.py --no-sync`, `--verify`, `git status`, scoreboard grep).

| Claim from session history | Verification result | Classification after check |
|---|---|---|
| `MODE: ALL_CLEAR` | **Confirmed** — dispatcher emitted ALL_CLEAR, SOURCE: derived from scoreboard | `SUPPORTED_BY_REPO` |
| `#99–#102 accepted` | **Confirmed** — scoreboard rows GATED with Matt acceptance language; `mmi/MMI_GATE_REGISTRY.md` ACCEPTED / hardened | `SUPPORTED_BY_REPO` |
| Parents #92/#84/#89/#94 ADVERSARIALLY HARDENED | **Confirmed** — scoreboard + gate registry cross-reference via #99/#100/#101/#102 | `SUPPORTED_BY_REPO` |
| Dispatcher active (executable) | **Confirmed** — script runs and derives route; **contradicts** handshake "NOT active" | `SUPPORTED_BY_REPO` + `CONTRADICTION` with handshake |
| Codex in BUILD + REVIEW routing | **Confirmed in working tree** — not committed | `BUILT_NEEDS_VERIFICATION` |
| Auto-sync on default run | **Confirmed** — default run prints `sync: ... already current`; `--no-sync` skips | `BUILT_NEEDS_VERIFICATION` (uncommitted) |
| Verify gate intact | **Partial** — verify runs all checks; **VERDICT: FAIL** until `scripts/mmi_dispatch.py` committed | `BUILT_NEEDS_VERIFICATION` |
| Files modified locally | **Confirmed** — 3 modified MMI/dispatcher files; 4 untracked concept drafts unrelated | `SUPPORTED_BY_REPO` (fact) |
| `PROJECT_HANDSHAKE.md` stale | **Confirmed** — dispatcher line + old HEAD block | `CONTRADICTION` |

**Commands used:**
```bash
python3 scripts/mmi_dispatch.py --no-sync
python3 scripts/mmi_dispatch.py --verify
python3 scripts/mmi_dispatch.py          # default sync behavior
git status --short
```

**Not verified in this pass:** full adversarial audit artifact presence at cited commits;
full test suite re-run; Threat Intelligence Daemon sign state.

---

## 11. Items that may be golden but require MMI review

| Item | Why golden | Promotion gate |
|---|---|---|
| "Matt names target; MMI assigns lane" | Reduces Matt's routing burden without reducing authority | Matt review + commit routing docs + `--verify` PASS |
| BUILD = Cursor → Codex → Cursor | Concrete policy vs vague "send to whoever" | Same; must survive `--verify` and align with `AGENTS.md` §2.1.2 |
| ALL_CLEAR ≠ next-phase authorization | Clean split automation vs authority | Already reflected in dispatcher; promote to protocol if Matt agrees |
| Default auto-sync | Reduces stale `MMI_CURRENT_STATE.md` drift | Review: confirm Matt wants sync-on-every-run vs explicit `--sync` only |

---

## Recommended MMI actions (Matt decides)

1. **Keep this intake** — not random history; documents executable routing upgrade.
2. **Review golden doctrine** — promote to `mmi/MMI_PROTOCOL.md` or leave in routing rules only.
3. **Commit dispatcher + routing docs** when authorized — required for `--verify` PASS.
4. **Reconcile `PROJECT_HANDSHAKE.md`** dispatcher status line (separate doc pass).
5. **Do not treat session prose as authority** until rows in §10 show `SUPPORTED_BY_REPO` or Matt signs promotion.

---

## Authority footer

This intake file is **non-authoritative**. Current routing authority remains:
`mmi/MMI_GATE_REGISTRY.md`, `mmi/MMI_DECISION_LOG.md`, and `scripts/mmi_dispatch.py --verify`
(after committed state).
