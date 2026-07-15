# MMI Cursor Ghost-Session Incident Handoff — 2026-07-14

**Authority:** Matt
**Recorder:** Codex in WSL
**Class:** Incident reconstruction and containment handoff; documentation only
**Status:** `CONTAINMENT_COMPLETED_LATER_2026-07-14`

> Historical-state note: the evidence and "Actions not taken" sections below record the pre-containment capture. Matt subsequently authorized containment; the Cursor process tree was terminated and separate containment evidence was preserved.

## Mission sequence

1. Contain Cursor so it cannot remain active as a ghost session, restore a live MMI editor surface, or mutate live MMI files outside a bounded authorization.
2. Audit and repair Codex task-instruction behavior. Codex supplied incorrect or incomplete Cursor instructions over multiple days and contributed upstream to agent failures.
3. Only after both control failures are repaired, return to the Sentinel watchdog mission. Product work remains blocked by the custody-maintenance freeze until Matt explicitly lifts it.

## Incident chain

Two distinct causes participated in one incident chain:

1. An incomplete/incorrect outbound task packet caused Cursor to search its open workspace, substitute the NorthStar constitution, and produce an irrelevant audit rather than stop.
2. Cursor retained writable access and restored editor/session state. That boundary allowed an automatic EOL rewrite or similar editor-level mutation of live MMI files.

A mechanically complete task packet is necessary to prevent wrong-project substitution. It is not sufficient to prevent an already-open writable editor tab from touching disk. Both packet validation and a non-writable review boundary are required.

## Evidence captured on 2026-07-14

- Windows `tasklist` showed 17 running `Cursor.exe` processes.
- The visible parent window title was `Cursor Agents`.
- Cursor global storage recorded two WSL empty-window backup sessions:
  - `1783200840462`
  - `1784058447933`
- The last active window pointed to `C:\Users\mattn\AppData\Roaming\Cursor\Backups\1784058447933` with remote authority `wsl+Ubuntu`.
- Cursor `settings.json` had `chat.agent.enabled: false`, but the separate Cursor Agents process surface was still active.
- No explicit `window.restoreWindows: "none"` control was present in the inspected settings.
- Current `workspaceStorage/*/workspace.json` mappings did not directly name `C:\MMI`.
- Cursor retrieval checkpoints and local history did contain references to live MMI content. This is evidence of retained MMI-associated state, not proof that a current workspace mapping is open.

## Actions not taken

- Cursor was not closed or terminated.
- No Cursor settings, backups, checkpoints, history, or workspace metadata were changed or deleted.
- No live MMI file was restored or normalized.
- No commit or push was performed.

These actions remain blocked because closing Cursor can discard unsaved editor or chat state, and quarantine/deletion requires a bounded Matt authorization and evidence plan.

## Current repository state at capture

Pre-existing loose state was preserved without modification:

- Modified: `mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json`
- Untracked: `scripts/mmi_task_emit_gate.py`
- Untracked: `tests/test_mmi_task_emit_gate.py`

The two untracked files appear related to mechanical outbound task-packet validation. Their provenance and correctness have not yet been accepted.

## Next safe action

Obtain Matt authorization for a narrow Cursor containment operation that:

1. captures the final process/session evidence and preserves any explicitly requested unsaved material;
2. closes the complete Cursor process tree;
3. backs up Cursor configuration and session metadata before changing it;
4. disables automatic window/session restoration;
5. quarantines, rather than silently deletes, retained sessions and MMI-linked review state;
6. relaunches Cursor only into an empty or isolated review location;
7. proves that Cursor does not restore MMI and causes no repository mutation.

Suggested authorization phrase:

```text
MATT_AUTHORIZES_CURSOR_CONTAINMENT:ghost-session-and-live-mmi-boundary:2026-07-14
```

After containment evidence passes, open a separate Codex instruction-quality audit. Do not merge that audit with Sentinel product implementation.
