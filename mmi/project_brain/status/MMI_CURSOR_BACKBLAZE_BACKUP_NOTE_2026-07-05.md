# MMI Cursor Backblaze Backup Note

Date: 2026-07-05
Authority repo: `C:\MMI` / `/mnt/c/MMI`

## Rule

Cursor normally performs the Backblaze backup. Do not invent a replacement flow.

GitHub remote should be synced first. Then, when Cursor is available, run the normal Cursor/Backblaze backup routine for:

- `C:\MMI`
- `C:\Users\mattn\Documents\Codex\2026-07-05\mmi-handoff\outputs`
- `C:\MMI\mmi\project_brain\status\MMI_POST_PUSH_HYGIENE_AUDIT_203B010_2026-07-05.md`

Do not delete `C:\_delete_after_mmi_audit_20260705` until backup is confirmed.
