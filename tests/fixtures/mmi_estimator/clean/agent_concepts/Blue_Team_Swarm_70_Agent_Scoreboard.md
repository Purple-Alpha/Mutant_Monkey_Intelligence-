# Blue-Team Swarm — Estimator fixture scoreboard

## Agent Health Score Board (Phase 1 — manual, LIVE)

| # | Agent | Layer | Stage | SCORE | Last change |
|---|-------|-------|-------|-------|-------------|
| 48 | Verification Outcome | 3 | ES1 | 87 | baseline |

| # | SPARK agent | Runtime status | Code evidence | Canonical 6-layer | Stage | BLOCKERS | TRACK | LAST_RUBRIC_SCORE | LAST_UPDATED |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Swarm Commander Agent | `DETECTOR_FUNCTION` (partial spine) | `core/orchestrator/routes.py`, `registry.py`, `swarm_commander.py` | 1 Command | A |  | BREADTH | — | adoption |
| 3 | Risk Triage Agent | `DETECTOR_FUNCTION` | `core/scoring/email_risk_scoring_agent.py` | 1 Command | A |  | BREADTH | — | adoption |
| 52 | Plain-English Explanation | `DETECTOR_FUNCTION` | `core/scoring/client_facing_rubric.py` (signed 5-axis rubric) | 4 Evidence | A |  | BREADTH | — | adoption |
| 47 | Case Timeline | `DETECTOR_FUNCTION` | partial | 4 Evidence | A |  | BREADTH | 8 | adoption |
| 48 | Verification Outcome | `GOVERNED_AGENT` | done | 3 Verification | A |  | BREADTH | — | adoption |
| 18 | Callback Verification | `DETECTOR_FUNCTION` | `core/scoring/callback_phishing_detector.py` | 3 Verification | A | NEEDS_SIGNED_CONTRACT | BREADTH | 7 | adoption |
| 16 | Bank Detail Drift | `merged` | merged | 2 Detection | A | merged | BREADTH | — | adoption |
| 7 | Sender Identity | `RECLASSIFY` | triage | 2 Detection | A |  | BREADTH | — | adoption |
| 50 | Depends Blocked | `SIGNED_UNBUILT` | none | 2 Detection | A | DEPENDS_ON:#99 | BREADTH | — | adoption |
| 99 | Missing Dep | `NOT_STARTED` | none | 2 Detection | A | NEEDS_BUILD_AUTH | BREADTH | — | adoption |
