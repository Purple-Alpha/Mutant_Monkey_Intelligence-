generated_at: 2026-06-24T23:19:40Z
git_head: 0a096c4
generator: scripts/mmi_operator_map_sync.py

# Operator Map — read this first

**Auto-generated plain-English view.** Rubric ranks; Matt selects.
Not build authorization. Refresh: `python3 scripts/mmi_operator_map_sync.py`

---

## Where we are

- **Dispatcher:** `ALL_CLEAR` — nothing waiting to be built or audited right now
- **Governed agents:** 17 of 70 at production-quality Stage 1 (GOVERNED_AGENT)
- **Promotion queue:** 20 built-and-audited agents waiting for your promotion review

## Why it keeps stalling

Each build cycle ends at **GATED** (built + audited). Moving to **GOVERNED_AGENT**
or starting the next build requires **you** in one sentence. When the pre-loaded
BOR feedstock list is empty, the dispatcher goes **ALL_CLEAR** and the crew stops
until you name the next lane.

**Fix in use:** this map auto-surfaces the promotion queue from the scoreboard
(not a hardcoded short list). Work the queue top-to-bottom to keep rolling.

## What's next (ranked — not authorized until you say so)

1. **Promotion review #2 Mission Context Agent (GATED -> GOVERNED_AGENT when authorized)** — score 5/10
2. **Promotion review #3 Risk Triage Agent (GATED -> GOVERNED_AGENT when authorized)** — score 5/10
3. **Promotion review #61 Test Case Generator (GATED -> GOVERNED_AGENT when authorized)** — score 4/10
4. **Promotion review #62 Regression Test (GATED -> GOVERNED_AGENT when authorized)** — score 4/10
5. **Promotion review #63 Adversarial Test (GATED -> GOVERNED_AGENT when authorized)** — score 4/10

## Promotion queue (built, audited, needs your review)

1. **#2 Mission Context Agent** — GATED, ready for promotion review
2. **#3 Risk Triage Agent** — GATED, ready for promotion review
3. **#64 Failure Classification** — GATED, ready for promotion review
4. **#67 Rule Improvement** — GATED, ready for promotion review
5. **#65 Correction Evidence** — GATED, ready for promotion review
6. **#61 Test Case Generator** — GATED, ready for promotion review
7. **#62 Regression Test** — GATED, ready for promotion review
8. **#63 Adversarial Test** — GATED, ready for promotion review
9. **#72 PhishIntelAgent** — GATED, ready for promotion review
10. **#73 RansomwareIntelAgent** — GATED, ready for promotion review

## What to say to unstick (copy-paste)

```text
Authorize GOVERNED_AGENT promotion review #2 (Mission Context Agent)
```

## What the crew can do without you

- Refresh maps (`mmi_lane_board_sync`, `mmi_dispatch --sync`, this file)
- Run tests and verify (`mmi_dispatch --verify`)
- Draft unsigned contracts (not build, not promotion)

## Machine sources (for tools — not for humans first)

- Ranked board: `mmi/MMI_RANKED_NEXT_ACTIONS.md`
- Handshake pin: `PROJECT_HANDSHAKE.md`
- Staged milestones: `mmi/MMI_MISSION_MAP.md` (may lag — trust this file + ranked board)
- Agent inventory: `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`

