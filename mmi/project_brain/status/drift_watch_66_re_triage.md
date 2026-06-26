# #66 Drift Watch — Re-Triage (MMI-DEC-236)

**Date:** 2026-06-26  
**Lane:** `DRIFT_CHECK`  
**Authority:** Matt depth-queue selection (MMI-DEC-222) after #19 GATED (MMI-DEC-235). **Not** build authorization.

---

## Question

Does scoreboard **#66 Drift Watch** need a new Agent Design Contract, ES1 wrapper build, or merge with **#86 W2 DriftWatcher**?

---

## Evidence reviewed

| Source | Finding |
|--------|---------|
| Scoreboard #66 | `GOVERNANCE_DOC_ONLY`; blocker `NEEDS_BUILD_AUTH`; cites `Compliance_and_Trend_Watch_Process.md` |
| `Compliance_and_Trend_Watch_Process.md` | §11 signed 2026-05-26. **Explicit:** "process spec, not a runtime feature"; "introduces no new agent, no new infrastructure, no new runtime code path" |
| `Frontier_Intake_Log.md` | Operational artifact for the process (operator-driven reviews → candidates → think_sheet staging) |
| Scoreboard #86 | `W2 DriftWatcher` — **GATED**; `core/watchers/drift_watcher.py`; confidence-distribution vs signed baseline (Layer 6 watcher) |
| `Watcher_Agents_Contract.md` | #86 watches **agent confidence drift inside the swarm** — unrelated to threat-landscape / compliance frontier intake |
| Architecture map | #66 = "Compliance and Trend Watch Process (signed)" — governance process, not W2 watcher |
| Design tree Team 9 | "Drift Watch Agent" task = "Watch attacker behavior drift" — **conceptual** label; implemented as operator process, not `#86` |

---

## Verdict

**RECLASSIFY — not a buildable agent row at ES1.**

1. **#66 is already satisfied** by the signed process spec + `Frontier_Intake_Log.md` operator discipline. No missing runtime module.
2. **#86 is a different concept** (swarm confidence drift). Shared word "drift" is a naming collision only — do not merge or conflate.
3. **`NEEDS_BUILD_AUTH` was stale** — implied a Cursor build lane that the signed process explicitly forbids without a new contract scope.
4. **Future automation** (e.g. agent that reads intake logs) would need a **new** Agent Design Contract and explicit Matt authorization — out of scope for this re-triage.

---

## Scoreboard action

- Status: `RECLASSIFY` (depth triage MMI-DEC-236)
- Blockers: **cleared** (empty)
- Re-triage trigger: Matt authorizes a bounded read-only agent contract over frontier-intake artifacts, or amends the process spec to require runtime automation

---

## Next depth target (MMI-DEC-222)

**#70 Final Review Agent** — boundary/design review (`GOVERNANCE_DOC_ONLY` partial; `complete_gate.py` + package auditor surfaces).

---

## Boundaries

- No build authorization
- No §11 signing
- No scoreboard change to #86
- No production dispatch
