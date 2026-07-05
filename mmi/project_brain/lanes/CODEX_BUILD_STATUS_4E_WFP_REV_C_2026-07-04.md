# Codex Build Status — 4E WFP Rev C Cleanup

**Timestamp:** 2026-07-04T20:46:54-07:00  
**Repo:** `C:\Architectapp_clean` / `/mnt/c/Architectapp_clean`  
**Authority:** Matt build direction in Codex desktop, 2026-07-04  
**Scope:** 4E WFP cleanup/build only  

## Status

**CONTRACT PASS. LIVE ADMIN PROOF NOT RUN IN CODEX.**

Codex cleaned the 4E implementation surface to match Rev C:

- ALE-only 4E scope documented.
- Four expected filters retained: allow V4, deny V4, allow V6, deny V6.
- User-mode WFP helper/filter scope documented; kernel-mode scope excluded from this slice.
- Live deny proof requires explicit access-denied (`WSAEACCES` / access denied), not timeout.
- Contract deny fixtures moved to controlled local endpoints.

## Files Updated

- `mmi/m4/wfp_policy.py`
- `host_boundary/mmi_wfp/README.md`
- `host_boundary/mmi_wfp/mmi_wfp_helper.cpp`
- `tests/test_m4_wfp_policy.py`

## Verification Run

```text
python3 -m pytest tests/test_m4_wfp_policy.py -q
......                                                                   [100%]
6 passed, 1 warning in 0.58s
```

Warning observed:

```text
PytestCacheWarning: could not create cache path /mnt/c/Architectapp_clean/.pytest_cache/v/cache/nodeids: [Errno 13] Permission denied
```

This warning does not affect the 4E test result.

Temporary contract harness evidence was written outside authority root:

```text
/mnt/c/mmi_m4_evidence/contract_4e_boundary
```

Seal command:

```text
python3 scripts/m4_authority_seal.py --authority /tmp/mmi_4e_authority --evidence /mnt/c/mmi_m4_evidence/contract_4e_boundary --store --json
```

Result:

```text
"passed": true
"manifest_hash": "sha256:2a16f00b86269344c9f63bec3129b4649c978cb1ba09483156bcde3cc5f302fd"
```

4E contract harness command:

```text
python3 scripts/m4_wfp_suite.py --authority /tmp/mmi_4e_authority --evidence /mnt/c/mmi_m4_evidence/contract_4e_boundary --json
```

Result:

```text
"harness": "m4_wfp_suite"
"phase": "17_phase_4E"
"passed": true
"schema_v": "2026-07-05c"
"contract_pass": true
"mode": "contract"
"t7_c1_decision": "DENY"
"t7_c2_decision": "ALLOW"
"t7_c3_decision": "DENY"
"min_viable_live_t7": false
"perfect_claim": false
```

Contract fixture endpoints are controlled local:

```text
T7-C1 DENY  127.0.0.1:19998
T7-C2 ALLOW 127.0.0.1:9443
T7-C3 DENY  127.0.0.1:19999
```

## Live/Admin Commands For Matt PowerShell

Run from Administrator PowerShell:

```powershell
cd C:\Architectapp_clean
.\scripts\build_m4_wfp.ps1
.\scripts\install_m4_wfp.ps1
python scripts\m4_wfp_suite.py --live --json
```

Optional password override before install:

```powershell
$env:MMI_WFP_PROBE_PASSWORD = '<operator-held-password>'
```

Uninstall:

```powershell
cd C:\Architectapp_clean
.\scripts\uninstall_m4_wfp.ps1
```

## Non-Claims

This does not claim `GATED`, `PERFECT`, M4 closure, PC2 isolation, host containment, or file-boundary containment. Live T7 remains unproven until the Administrator PowerShell install and `--live` suite pass on PC1.
