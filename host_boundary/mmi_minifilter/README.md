# MMI Boundary Minifilter (kernel) — Phase 4D-b



**Status:** WDK project wired — build on PC1, load under test signing for live T1/T2.



## Role



- Pre-operation callbacks on authority paths under `Parameters\AuthorityRoot` (default `\MMI`)

- Deny `CREATE` (mutating), `WRITE`, `SET_INFORMATION`, `SET_SECURITY` under that prefix

- Filter service name: **`mmi_boundary`** (detected by `fltmc filters`)

- FileId manifest sync via filter port: follow-up (path prefix closes T1 live probe)



## Build (Developer PowerShell for VS 2022 — PC1)

Use **VS 2022** MSBuild (WDK VSIX + `WindowsKernelModeDriver10.0` toolset). Build Tools 18-only shells may fail.

```powershell

# Developer PowerShell for VS 2022 (PC1)

cd C:\MMI

.\scripts\build_m4_minifilter.ps1

```



Output: `host_boundary\mmi_minifilter\x64\Release\mmi_minifilter.sys`



## Install (Administrator — test signing required)



```powershell

# PowerShell (PC1) — Administrator

bcdedit /set testsigning on

shutdown /r /t 0

```



After reboot:



```powershell

# PowerShell (PC1) — Administrator

cd C:\MMI

.\scripts\install_m4_minifilter.ps1 -AuthorityRoot C:\MMI

fltmc filters

```



## Live gate (driver loaded)



```powershell

# PowerShell (PC1) — Administrator, filter loaded

cd C:\MMI

python scripts/m4_minifilter_suite.py --live --json

```



Expect: `driver_loaded: true`, `live_t1_blocked: true`, `verify_fingerprint_ok: true`



## Contract gate (safe — no driver)



```powershell

python scripts/m4_minifilter_suite.py --json

```



## Uninstall



```powershell

# PowerShell (PC1) — Administrator

.\scripts\uninstall_m4_minifilter.ps1

```



**Not claimed:** live boundary min-viable, M4_MET, containment-proven.

