# MMI Phase 1 Stability Harness Spec

**Status:** Built for `mmi-weapon-phase1-stability-harness`  
**Authority:** Matt Option A, 2026-07-01  
**Scope:** Phase 1 measurement only. No Phase 2/3, proof gate, genomic loop, L3 flight tests, metadata-ingress wire, or OPSEC/intel lane changes.

## Purpose

The Phase 1 harness measures whether AGI Phase 1 is stable under the MMI weapon battlefield matrix:

- 3 consecutive independent Chaos Lab runs.
- Each run must score Overall Tier 4.
- Tier spread across runs must be no more than 1.
- Re-run honesty is logged with the SHA256 critic hash of `mmi/project_brain/chaos/mirror_dimension_router.py` per run.
- Matrix Section 7.4 re-run penalization is flagged when repeated runs reuse the same critic hash.

**§7.4 scope (2026-07-01 fix):** Penalty applies only when the **same `lab_id`** is scored multiple times with an unchanged critic hash (same-lab purple re-run gaming). Independent run lab IDs — e.g. `m2_001__phase1_run_01` through `03` — share one authority critic file by design and **do not** trigger the penalty.

## CLI

```bash
python3 scripts/phase1_stability_harness.py --lab-id m2_001 --runs 3 --provisioner
```

Options:

- `--lab-id <id>`: base lab id. Default: `m2_001`.
- `--runs <n>`: number of independent runs. Default: `3`.
- `--provisioner`: execute the canonical lab stack through `scripts/chaos_lab_provisioner.py`.
- `--authority <path>`: authority repo root. Default: `/mnt/c/Architectapp_clean`.
- `--lab-root <path>`: lab root. Default: `/tmp/mmi_chaos_lab`.

For `--runs 3`, per-run lab IDs are:

```text
<lab_id>__phase1_run_01
<lab_id>__phase1_run_02
<lab_id>__phase1_run_03
```

The aggregate summary is written under the base lab:

```text
/tmp/mmi_chaos_lab/<lab_id>/EVIDENCE/phase1_stability_summary.json
```

## Canonical Stack

Each independent run executes this sequence:

```bash
python3 scripts/chaos_lab_provisioner.py smash-all --lab-id <run_lab_id>
python3 scripts/chaos_lab_provisioner.py mesh-smash --lab-id <run_lab_id>
python3 scripts/chaos_lab_provisioner.py purple-evasion --lab-id <run_lab_id>
python3 scripts/chaos_lab_provisioner.py action-integrity --lab-id <run_lab_id>
```

## Recorded Evidence

For each run, the harness records:

- `overall_weapon_tier`
- `axis_a_tier`
- `axis_b_tier`
- `evolution_gate`
- critic hash for `mirror_dimension_router.py`
- evidence paths for:
  - `purple_evasion_summary.json`
  - `m3_mesh_summary.json`
  - `smash_all_summary.json`
  - `action_integrity_summary.json`

## Pass Line

`PASS` requires all of the following:

- Every run is scoreable.
- Every run has Overall Tier 4.
- `max(overall tiers) - min(overall tiers) <= 1`.
- No matrix Section 7.4 critic-hash re-run penalty is flagged.

Any run below Tier 4, unscoreable evidence, tier spread above 1, or **same-lab_id** repeated scoring with unchanged critic hash emits an explicit falsification reason in the summary JSON.
