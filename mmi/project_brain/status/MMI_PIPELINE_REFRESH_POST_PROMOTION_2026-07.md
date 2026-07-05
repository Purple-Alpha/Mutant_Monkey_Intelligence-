# MMI Pipeline Refresh — Post Promotion 110548

**Task:** Closeout of `mmi-promote-latest-good-stub-110548` + seed `mmi-weapon-phase1-stability-harness`  
**Authority:** Matt Option A (2026-07-01)  
**Recorded by:** Cursor PM  
**Sign-off:** **PASS**

---

## 1. Promotion closeout

| Field | Value |
|-------|--------|
| Archive | `mmi_backup_20260701_110548.tar.gz` |
| SHA256 | `5f6203e04f357127e4923793bb522ed32981a123d23e16f40f43b92e736e81df` |
| Stub | `mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md` — **points to 110548** |
| Restore-check | PASS — `MMI_RESTORE_CHECK_110548_2026-07.md` |
| validate-promotion | ALLOWED |

---

## 2. Matt directive consumed

**Option A:** Close stub promotion → seed weapon Phase 1 stability harness (Codex).

**Not seeded (held):**

- Option B — metadata-ingress provisioner wire (await separate Matt directive)
- Option C — OPSEC/intel lane hold (not selected)

---

## 3. Active task (deployer)

| Field | Value |
|-------|--------|
| **Task id** | `mmi-weapon-phase1-stability-harness` |
| **Assignee** | **Codex** |
| **Tier** | Backbone / runtime support |
| **Build authorization** | **NOT_AUTHORIZED** — Matt must say authorize build |
| **Cursor PM** | Route handoff to Codex; do not implement |

Verify: `python scripts/next_task.py`

---

## 4. Harness scope (for Codex handoff)

**Pass line (AGI Phase 1):** 3 consecutive independent lab runs, each **Overall Tier 4**, no >1-tier variance between runs.

**Canonical stack per run:**

```bash
python3 scripts/chaos_lab_provisioner.py smash-all --lab-id <lab_id>
python3 scripts/chaos_lab_provisioner.py mesh-smash --lab-id <lab_id>
python3 scripts/chaos_lab_provisioner.py purple-evasion --lab-id <lab_id>
python3 scripts/chaos_lab_provisioner.py action-integrity --lab-id <lab_id>
```

**Honesty requirements:**

- Log `mirror_dimension_router.py` critic hash each run (matrix §7.4 re-run penalization)
- Record evidence JSON paths under `/tmp/mmi_chaos_lab/<lab_id>/EVIDENCE/`
- FAIL loudly on any run below Tier 4

**Out of scope:** Phase 2/3, proof gate, genomic loop, L3 flight tests, metadata-ingress wire (Option B — not seeded).

---

## Sign-off

**PASS** — Pipe LOADED. Promotion complete. Weapon Phase 1 harness seeded for Codex pending build auth.
