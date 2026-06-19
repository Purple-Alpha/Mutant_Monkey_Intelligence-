# MMI_AUTHORITY_MATRIX.md — Who Can Do What

**Authority:** Matt Nichol — authorized June 16 2026

This matrix locks which model/tool may research, draft, review, build, verify, or approve. It exists to stop the "who audits the auditor" problem and to prevent self-approval.
`AGENTS.md` §2.2 remains the higher-level orientation source if wording conflicts.

**Repo scope:** Mutant Monkey Security authority repo at `/home/socialarchitect/northstar`.
Architectapp (`/home/socialarchitect/projects/Architectapp_clean`, `/mnt/c/Architectapp_clean`) is out of scope for governed swarm builds.

---

| Action | ChatGPT | Gemini | Claude | Cursor | Codex | Matt |
|---|---|---|---|---|---|---|
| Research | Yes | Yes | Yes | No | No | Approves |
| Spec draft | Yes | Yes | Yes | No | No | Signs |
| Adversarial review | Yes | Yes | Review | No | Yes | Final |
| Pre-build plan review | No | No | No | Draft plan | Yes | Authorizes |
| Post-build / diff review | No | No | No | No | Yes | Final |
| Independent review (adversarial evidence) | No | No | No | No | Yes | Final (hardening claim) |
| Code build | No | No | No | Yes | No | Authorizes |
| Gate acceptance | Recommend | Recommend | Recommend | No | Recommend | Final |
| Hardening claim | No | No | No | No | No | Signs only |
| Contract change | No | No | Draft | No | No | Signs only |
| Repo creation | No | No | No | No | No | Final |
| Score logic change | Recommend | Review | Draft | Build if signed | Review | Final |
| Safe-stop override | No | No | No | No | No | Final |
| Money-movement logic | No | No | Draft | Build if signed | Review | Final |

---

## Rule

> No model gets to both design, build, approve, and audit the same thing.

- Research / cross-check / drafting / build / approval / audit are **separate lanes**.
- A "Recommend" cell means the model may surface a recommendation with evidence; it does not grant the decision.
- "Build if signed" means Cursor may execute only against a §11-signed spec; it never originates authority.
- Codex reviews and critiques; it does not build production code or sign acceptance or hardened claims.

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

