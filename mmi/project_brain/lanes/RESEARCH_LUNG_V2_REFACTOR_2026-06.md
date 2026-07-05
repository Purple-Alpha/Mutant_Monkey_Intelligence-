# MMI Lung v2 Refactor — Verbatim Archive

**Status:** RESEARCH / CONCEPT — NOT BUILT  
**Authority:** Matt (Super)  
**Date captured:** 2026-06 (session response to peer review)  
**Date filed:** 2026-07-01  
**Purpose:** Preserve Matt's v2 refactor verbatim — Ed25519, cgroups, WFP/WDAC/ACL boundaries — without dilution.

**Related:** `lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md` (§3 extracted for host-boundary focus)  
**Not build authorization.**

---

You just executed a flawless, surgical peer-review. This critique strips out the "cyber-fantasy" and exposes the exact mechanical realities we have to account for if we want this thing to hold up in an actual production environment.

You are completely right. If we run the previous draft verbatim, we don't build a defense platform—we build a self-inflicted Denial of Service engine that hands the attacker the exact system resources they need to kill our workstation.

Let's tear down the fantasy elements you pointed out and refactor them into actual, low-level engineering implementations.

---

## 1. Code-Level & Cryptographic Flaws (Fixed)

### The String Escape Bug

Good catch on the invalid hex escape. `\xmm` is complete pseudo-code. Standard Python interprets this as a syntax error (`ValueError: invalid \x escape`). It must be proper hexadecimal bytes.

### The Security-Through-Obscurity & Symmetric Key Trap

Using a shared `secret_seed` stored locally means if an attacker compromises the user-space context, they can read the script, scrape the memory, and forge commands easily. We must replace this with a **public-key asymmetric cryptography model (Ed25519)** using memory-locked signing keys.

```python
import time
import struct
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

class MMISecurePipe:
    def __init__(self, verify_key_bytes: bytes = None):
        # The agent ONLY holds the public VerifyKey in memory; Private key sits off-box or isolated
        self.verifier = VerifyKey(verify_key_bytes) if verify_key_bytes else None

    def verify_and_route_payload(self, signed_packet: bytes) -> tuple:
        """
        No symmetric seeds. Every orchestration command must carry an asymmetric 
        Ed25519 signature verifiable by the public key.
        """
        try:
            # Layout: [4 Bytes Magic] [8 Bytes Timestamp] [64 Bytes Signature] [Payload]
            magic, timestamp = struct.unpack(">4sQ", signed_packet[:12])
            
            if magic != b"\xde\xad\xbe\xef":  # Corrected hex literal
                raise ValueError("Invalid magic header sequence.")

            # Validate time window to prevent replay attacks (max 5-second skew)
            current_time = int(time.time())
            if abs(current_time - timestamp) > 5:
                raise ValueError("Stale instruction packet window expired.")

            # Extract signature and actual payload message
            signature = signed_packet[12:76]
            payload = signed_packet[76:]

            # Verify cryptographic integrity of origin
            self.verifier.verify(payload, signature)
            return True, payload

        except (BadSignatureError, ValueError) as e:
            return False, str(e)

```

---

## 2. Infrastructure Reality Checks (Fixing the Self-DoS)

Your point on resource allocation is critical. Spawning 700 unconstrained Python processes via a memory fork will trigger instant memory thrashing and CPU starvation on a Mini PC, doing the ransomware's job for it.

### The Real-World Defensive Shift: Control Groups (`cgroups`)

Instead of duplicating processes, modern systems architecture uses **Control Groups (`cgroups v2`)** to constrain the offending process tree immediately. If anomalies are detected in user space, we manipulate the Linux kernel filesystem (`/sys/fs/cgroup`) to throttle the compromised process tree to `< 5%` CPU allocation and freeze its execution loops (`cgroup.freeze`), buying time for containment.

---

## 3. Kernel Realities: WSL vs. Host Windows

Your critique on the boundary layer is entirely accurate: **A Python wrapper running in user space cannot hooks syscalls like `NtWriteVirtualMemory` or enforce Windows Filtering Platform (WFP) rules natively.** Furthermore, `/mnt/c/Architectapp_clean` is managed by the **DrvFs kernel plugin** inside WSL. You cannot enforce Linux-native file locking or immutable file attributes (`chattr +i`) across a DrvFs mount and expect it to stop a native Windows process from wiping that directory from the Windows host side.

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

---

## 4. Threat Model Refocus

You correctly identified a massive scope mismatch in the original draft: **Enforcing a bytecode validation language on our command-line pipe protects the *control plane* (preventing someone from injecting bad tasks into our swarm), but it does absolutely nothing to stop an inbound browser exploit or an HTML Smuggling delivery chain.**

### Revised Pipeline Alignment

* **Our Control Plane Language Security:** Retained strictly to ensure that no rogue script or low-privilege system entry can spoof orchestration commands to our local MMI worker scripts.
* **The Delivery Vector (The Actual Threat):** Neutralizing polymorphic delivery chains (like HTML Smuggling) requires our host-level monitoring layer to flag when productivity applications (`msedge.exe`, `chrome.exe`) drop unmapped binary file payloads into transient disk paths (`%TEMP%` or `AppData\Local`) and prevent those binaries from launching using strict, pre-configured **Application Whitelisting Policies (WDAC)**.

This strips out the hype. We are no longer discussing an unconstrained process-cloning script; we are defining an asymmetric, cryptographic control loop that manipulates native OS kernel features to enforce boundary limits.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Verbatim archive from Matt session |
