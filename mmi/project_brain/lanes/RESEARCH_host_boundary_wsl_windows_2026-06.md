# Research: Host Boundary — WSL vs Windows (Lung v2 §3 Extract)

**Status:** RESEARCH — NOT BUILT  
**Authority:** Matt (Super)  
**Source:** Extracted from `lanes/RESEARCH_LUNG_V2_REFACTOR_2026-06.md` §3 for host-boundary focus  
**Date filed:** 2026-07-01

**Full v2 context:** `lanes/RESEARCH_LUNG_V2_REFACTOR_2026-06.md`

---

## Kernel Realities: WSL vs. Host Windows

**A Python wrapper running in user space cannot hooks syscalls like `NtWriteVirtualMemory` or enforce Windows Filtering Platform (WFP) rules natively.** Furthermore, `/mnt/c/Architectapp_clean` is managed by the **DrvFs kernel plugin** inside WSL. You cannot enforce Linux-native file locking or immutable file attributes (`chattr +i`) across a DrvFs mount and expect it to stop a native Windows process from wiping that directory from the Windows host side.

### Grounding the Architecture in Reality:

To make this real, our Python orchestration engine cannot do the heavy lifting itself; it must act merely as a telemetry coordinator that interfaces directly with native OS subsystems via elevated APIs:

```
┌──────────────────────────────────────┐
│       Python Orchestration Layer     │
└──────────────────┬───────────────────┘
                   │ (Elevated API Calls)
                   ▼
┌───────────────────────────────────────────────────────────────────┐
│                    NATIVE KERNEL SUBSYSTEMS                       │
├───────────────────────────────────┬───────────────────────────────┤
│ Windows Filtering Platform (WFP)  │   Windows ETW / Sysmon Core   │
│ (Blocks sockets via PyWFP API)    │  (Direct Kernel-Level Logging)│
└───────────────────────────────────┴───────────────────────────────┘

```

1. **Network Containment:** For network isolation, we interface with the native **Windows Filtering Platform (WFP)** via a compiled C-extension or structured admin utilities (like utilizing Windows `netsh` or native `PyWFP` library calls running with elevated `NT AUTHORITY\SYSTEM` permissions on the host side).
2. **File System Security:** To protect `/mnt/c/Architectapp_clean`, the security model must exist on the **Windows host level** (using Windows Access Control Lists - ACLs, or a miniature Windows File System Minifilter Driver) to block unauthorized write handles to `C:\Architectapp_clean` originating from any binary other than our validated process identities.

### Delivery vector (control plane vs host)

* **Control plane language security** — prevents spoofed orchestration commands to local MMI worker scripts.
* **Delivery vector** — browser → `%TEMP%` / `AppData\Local` drops; neutralized via host monitoring + **WDAC** application whitelisting.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Extract from Lung v2 refactor §3 |
