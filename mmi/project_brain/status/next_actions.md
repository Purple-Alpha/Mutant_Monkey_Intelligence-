# Next Actions

## Recommended

1. Wire `mmi/project_brain/status/active_task.md` or equivalent milestone data
   into PM voice/rubric scoring.
2. Make `python3 scripts/mmi_pm_voice.py` show `lane:` and `milestone:` after
   the existing four-line console once the data source is stable.
3. Add a drift test that fails when the console recommends a `1/10` task while
   an active `8/10` milestone task exists.

## Hold

- Do not build new agents from GATED rows.
- Do not treat promotion review as signed build authority.
- Do not wire production dispatch from project-brain docs alone.

