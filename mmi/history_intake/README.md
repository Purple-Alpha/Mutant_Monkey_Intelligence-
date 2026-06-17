# mmi/history_intake/ — Chat & Session History Classification

**Authority:** Matt Nichol — evidence intake only  
**Scope:** Documentation/classification. **Does not** modify dispatcher, routing rules,
authority matrix, scoreboard, handshake, or automation.

---

## Purpose

This folder holds **non-authoritative intake reports** that classify chat-history and
session-history material (ChatGPT, Claude, Cursor, Gemini, Grok) against the live repo.
MMI uses these maps to preserve ideas, contradictions, and golden candidates without
promoting them to routing authority.

**Routing authority remains:** `mmi/MMI_GATE_REGISTRY.md`, `mmi/MMI_DECISION_LOG.md`,
and committed `scripts/mmi_dispatch.py --verify` — not anything in this folder.

---

## Intake files

| File | Source | Status |
|---|---|---|
| `MMI_CHATGPT_HISTORY_INTAKE.md` | Repo-grounded classification pass (themes + named artifacts) | Primary repo intake |
| `MMI_CHATGPT_HISTORY_MASTER_INDEX.md` | Pointer to Windows consolidated master (deduped 13→10 drafts) | Secondary reference index |
| `MMI_CLAUDE_CURSOR_HISTORY_INTAKE.md` | Pasted Claude/Cursor compendium + CIS research material | Quarantined buckets |
| `MMI_DISPATCHER_ROUTING_DOCTRINE_INTAKE.md` | Cursor/Matt session on lane-selection doctrine | `NEEDS_MMI_REVIEW` — **not** accepted routing authority |

---

## Secondary corpus (Windows — not primary)

```
/mnt/c/Unified Folder Structure NorthStar + SwarmCommand Venture/chat_history/
  MMI_CHATGPT_HISTORY_INTAKE_MASTER.md
```

WSL repo `/home/socialarchitect/northstar` is primary. The Windows master is preserved
evidence from deduplicated ChatGPT drafts. Do not treat it as authority; use
`MMI_CHATGPT_HISTORY_MASTER_INDEX.md` for how it relates to repo intake.

---

## Separation rule (authority bleed prevention)

While collecting/classifying evidence:

- **Do not** change `scripts/mmi_dispatch.py`, `mmi/MMI_ROUTING_RULES.md`, or
  `mmi/MMI_AUTHORITY_MATRIX.md` in the same pass as intake commits.
- Dispatcher/routing upgrades require **separate explicit authorization** after intake
  cleanup is complete.
- Classify proposed routing changes as `BUILT_NEEDS_VERIFICATION` / `NEEDS_MMI_REVIEW`
  in intake — never as accepted authority from session history alone.

---

## Intake log

See `mmi/MMI_INTAKE_RECORDS.md` for running intake IDs.
