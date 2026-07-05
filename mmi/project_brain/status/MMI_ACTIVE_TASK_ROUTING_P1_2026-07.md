# MMI Active Task Routing — P1 Closeout Gate

**Last updated:** 2026-07-01  
**Authority:** Matt (Super) — routing model confirmed  
**Active task:** `mmi-quality-slice-p1-closeout-gate`

---

## Verdict

**ROUTING CONFIRMED** — `scripts/next_task.py` emits **Codex** as assignee. Cursor PM is **not** the default executor for this task.

---

## Deployer check (live)

```bash
python3 scripts/next_task.py
```

Expected (2026-07-01):

```text
TASK: mmi-quality-slice-p1-closeout-gate
SCORE: 88
GOES TO: Codex (Backbone / runtime support)
```

---

## Lane assignment

| Role | Responsibility |
|------|----------------|
| **Codex** | Implement P1 closeout gate hardening (`complete_task.py`, H1 mandatory paths) — **after Matt build auth** |
| **Cursor PM** | Queue, routing, status docs, handoff packet, closeout hygiene **after** Codex deliverable reviewed |
| **Matt** | Explicit build authorization; final authority; GATED |
| **ChatGPT** | Adversarial/secondary review — only if separately assigned |
| **Claude** | Design review — only if separately assigned |
| **Gemini / Gemini Paid** | Research/audit — only if separately assigned |

---

## Hard rules

1. **`assignee != Cursor PM`** → Cursor PM routes and records status; does **not** silently implement.
2. **`build_authorization: NOT_AUTHORIZED`** on task — seeded/pending is **not** permission to code.
3. **No Level 3** (L3-05+) while P1 is active pending implementation.
4. **No OPSEC-4/5/9** checklist state changes.
5. **MMI only** — no Social Architect swarm hierarchy; no NorthStar bridge; advisory-only; no SOAR/EDR/auto-containment.

---

## Scope boundaries (preserved)

```text
MMI only · local-first · advisory-only
No NorthStar bridge · no swarm hierarchy
No Level 3 continuation · no OPSEC-4/5/9 mutation
```

---

## References

- `mmi/project_brain/status/MMI_LANE_ROUTING.md` — lane owners + P1 handoff block  
- `mmi/project_brain/architecture/MMI_QUALITY_ELEVATION_REDESIGN_2026-07.md` — Slice P1 spec  
- `tasks.json` — `build_authorization`, `routing_note` on active task  

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | P1 routing confirmed; Codex assignee; Cursor PM route-only |
