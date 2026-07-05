# MMI Boundary Daemon (Go skeleton)

**Phase:** §17 Phase 4C  
**Status:** Skeleton — hash/arm/heartbeat contract only (no minifilter/WFP yet)

## Build (PC1 with Go)

```powershell
cd host_boundary\mmi_boundary_daemon
go build -o mmi_boundary_daemon.exe .
```

## Selftest

Requires `policy_manifest.json` and `authority_manifest.json` from:

```powershell
python scripts\m4_authority_seal.py --store --json
```

Then:

```powershell
.\mmi_boundary_daemon.exe --selftest --policy C:\mmi_m4_evidence\boundary\policy_manifest.json --authority-manifest C:\mmi_m4_evidence\boundary\authority_manifest.json --evidence C:\mmi_m4_evidence\boundary
```

## Dev host without Go

Use Python skeleton (same contract):

```powershell
python scripts\m4_boundary_daemon.py --json
```

**Not claimed:** live boundary, M4_MET, containment-proven.
