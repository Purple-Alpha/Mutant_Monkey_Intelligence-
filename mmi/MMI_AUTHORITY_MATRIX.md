# MMI_AUTHORITY_MATRIX.md — Who Can Do What

**Authority:** Matt Nichol — authorized June 16 2026

This matrix locks which model/tool may research, draft, review, build, verify, or approve. It exists to stop the "who audits the auditor" problem and to prevent self-approval.

---

| Action | ChatGPT | Gemini | Claude | Cursor | Matt |
|---|---|---|---|---|---|
| Research | Yes | Yes | Yes | No | Approves |
| Spec draft | Yes | Yes | Yes | No | Signs |
| Adversarial review | Yes | Yes | Review | No | Final |
| Code build | No | No | No | Yes | Authorizes |
| Gate acceptance | Recommend | Recommend | Recommend | No | Final |
| Hardening claim | No | No | No | No | Signs only |
| Contract change | No | No | Draft | No | Signs only |
| Repo creation | No | No | No | No | Final |
| Score logic change | Recommend | Review | Draft | Build if signed | Final |
| Safe-stop override | No | No | No | No | Final |
| Money-movement logic | No | No | Draft | Build if signed | Final |

---

## Rule

> No model gets to both design, build, approve, and audit the same thing.

- Research / cross-check / drafting / build / approval / audit are **separate lanes**.
- A "Recommend" cell means the model may surface a recommendation with evidence; it does not grant the decision.
- "Build if signed" means Cursor may execute only against a §11-signed spec; it never originates authority.
