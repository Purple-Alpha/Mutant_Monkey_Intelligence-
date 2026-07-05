# MMI Chaos Level 3 — L3-04 Intel Headline Laundering (Staged)

**Task:** `mmi-chaos-l3-04-intel-headline-laundering`  
**Scenario:** L3-04 from `MMI_CHAOS_LEVEL3_PLAN_2026-07.md`  
**Date:** 2026-07-01  
**Executor:** Cursor PM  
**Authority:** Matt — L3-04 only (not batch Level 3)

---

## Sign-off

**PASS WITH REVISIONS**

Staged §1 headline laundering **detected** on FAULT copy. Both live intel briefs **unchanged** (SHA256 match) and **clean** under `intel-briefs` batch scan.

**Revision caveat:** H2 detection is read-only `mmi_verify.py intel-brief` — not yet a mandatory brief filing gate. Global/vendor stats remain properly quarantined in live §5 claims tables; this test proves regression in §1 would be caught if the tool is run.

**Truth boundary tested:**

```text
Global/vendor evidence must never become a Canadian headline claim.
```

---

## Fixture path

```text
mmi/project_brain/chaos/fixtures/v3/L3-04/
├── BEFORE/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md
├── FAULT/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md
├── EVIDENCE/
│   ├── pre_check.json
│   ├── detection_output.json
│   ├── post_check_live_unchanged.json
│   └── signoff.txt
├── ROLLBACK.md
├── _setup_fixture.py
└── _post_check.py
```

---

## Injected fault (FAULT copy only)

**Target brief:** `INTEL_ransomware-backup-targeting_2026-06.md`  
**Location:** `## 1. Threat summary`  
**Injection:**

```text
Verizon reports 88% of Canadian SMB breaches involve ransomware.
```

Mirrors Level 2 T03 / chaos fixture `test03_headline_launder` — global vendor stat promoted into operator-facing Canadian headline context without `[Global Data` quarantine tag.

Live intel briefs were **not** modified. `INTEL_INDEX.md` **not** changed.

---

## Live brief pre-check (SHA256)

| Brief | SHA256 |
|-------|--------|
| `INTEL_ransomware-backup-targeting_2026-06.md` | `112d282b30bcac6d18b383178f0a2ffa32fff3b02b30b2daeccc43627c6c1898` |
| `INTEL_polymorphic-ransomware-delivery_2026-07.md` | `7d0564a137e29609b13449e6bb7192f610bd38a7ff49b17e5968bd9f8c7ce070` |

Source: `EVIDENCE/pre_check.json`

---

## Detection command / result

### Staged FAULT (expect violation)

```bash
python3 scripts/mmi_verify.py intel-brief \
  mmi/project_brain/chaos/fixtures/v3/L3-04/FAULT/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md
```

| Field | Result |
|-------|--------|
| `ok` | **false** |
| Exit code | **1** (expected — fault detected) |
| Context | `section_1_threat_summary` |
| Pattern | `\d+%` (Verizon 88% line) |

### Live briefs (expect clean)

```bash
python3 scripts/mmi_verify.py intel-briefs
```

| Field | Result |
|-------|--------|
| `ok` | **true** |
| `briefs_scanned` | **2** |
| `failed` | **0** |

Full JSON: `fixtures/v3/L3-04/EVIDENCE/detection_output.json` and `post_check_live_unchanged.json`

---

## Live brief post-check

| Check | Result |
|-------|--------|
| SHA256 matches pre | **Yes** (both briefs) |
| `intel-briefs` batch | **PASS** — 2 scanned, 0 failed |
| Live briefs written? | **No** |

---

## Rollback / cleanup

| Check | Result |
|-------|--------|
| FAULT retained as evidence | **Yes** |
| Live rollback required | **No** |
| B2 mutated | **No** |

See `fixtures/v3/L3-04/ROLLBACK.md`.

---

## Hard stops honored

| Stop | Result |
|------|--------|
| Live intel briefs mutated | **NO** |
| `INTEL_INDEX.md` changed | **NO** |
| Other Level 3 scenarios | **NO** |
| Batch Level 3 | **NO** |
| OPSEC-4/5/9 changed | **NO** |
| B2 mutated | **NO** |
| Level 4 | **NOT STARTED** |

---

## Next

- Optional B2 mirror L3-04 evidence (Matt-authorized, separate pass)
- Next eligible: **L3-05 only** when separately authorized

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | L3-04 staged headline laundering — PASS WITH REVISIONS |
