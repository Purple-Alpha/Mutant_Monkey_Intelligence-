# Phase 4E — WFP default-deny egress (T7)

## Scope

User-mode WFP helper registers default-deny outbound filters for the **signed
`policy_manifest.json` clone SID** at:

- `FWPM_LAYER_ALE_AUTH_CONNECT_V4`
- `FWPM_LAYER_ALE_AUTH_CONNECT_V6`

The Rev C 4E slice is ALE-only and installs four filters total:

- allow telemetry V4
- default deny V4
- allow telemetry V6
- default deny V6

Telemetry allowlist comes from signed `wfp_policy.telemetry_egress_allowlist`.
This is a user-mode WFP helper/filter implementation. Kernel-mode enforcement
is outside this 4E slice.

## Non-inheritance

```text
4E does not prove file-boundary containment.
4D_b does not prove network egress containment.
NOT CLAIMED: host containment, M4_MET, GATED, PERFECT.
```

## Install (Administrator)

Install creates local probe account `MmiWfpProbe` (or uses existing), **re-seals**
`policy_manifest.json` with signed `clone_sid` + `probe_account_name`, then binds
WFP filters to that SID only.

```powershell
# optional: $env:MMI_WFP_PROBE_PASSWORD = 'your-probe-password'
.\scripts\install_m4_wfp.ps1
```

**Live probes do not run from the Administrator harness.** The suite calls
`mmi_wfp_helper.exe probe`, which impersonates the signed probe account and
requires `WSAEACCES` (10013) for T7 deny proof — not generic connect failure.
Timeout is ambiguous and does not count as live deny proof.

## Live gate

```powershell
python scripts\m4_wfp_suite.py --live --json
```

`source_context_ok` matches **signed manifest** `wfp_policy.clone_sid` against
probe-observed SID only. Unsigned `wfp_engine_state.json` is audit metadata only.

## Evidence

| Artifact | Path |
|----------|------|
| Deny stream | `boundary/wfp_denies.jsonl` |
| Suite rollup | `boundary/wfp_suite_summary.json` |
| T7 falsifier | `boundary/falsifiers/T7_summary.json` |

## Uninstall

```powershell
.\scripts\uninstall_m4_wfp.ps1
```
