# Beacon Injector

**Status:** `RESEARCH_DESIGN` | **Component:** Swarm Command Reality Controller  
**Objective:** Universal attribution and telemetry harvesting through artifact weaponization (lab decoys only).

> **Authority:** Research doctrine only. Not build authorization. See `README.md`.

---

## 1. Mission Statement

The `beacon-injector` module transforms static exfiltrated assets into high-fidelity
intelligence nodes. Its function is to neutralize the attacker's anonymity by
forcing their execution environment to report back to Swarm Command, regardless of
VPN, Tor, or Proxy obfuscation — **within an isolated lab decoy context only**.

---

## 2. Execution Tactics

- **Hidden Resource Loading:** Injects standard `<img>` or `<iframe>` tags into
  documents (PDF/DOCX) that point to unique, cryptographically signed URLs.
- **Environment-Aware Scripting:** Embeds lightweight, obfuscated JavaScript/Macro
  logic designed to execute upon open to scrape local `systeminfo`, `whoami` output,
  and browser-stored environment variables.
- **Persistent Metadata:** Injects "Canary UUIDs" into internal file properties
  (e.g., `Author`, `RevisionID`, `Comments`). If the attacker moves the file across
  different machines, these UUIDs persist and continue to report the file's location
  back to our systems.

---

## 3. Intelligence Outputs (The Data Stream)

When an artifact "phones home," the `beacon-injector` captures and validates:

- **The "True Origin" IP:** Bypassing proxy headers to correlate the specific egress point.
- **Device Fingerprint:** Hostname, OS version, hardware ID, and active user privileges.
- **Network Context:** The presence of internal domains, DNS suffixes, and local gateway information.

---

## 4. Stealth and Integrity Protocols

- **Adaptive Obfuscation:** Trigger mechanisms are randomized. No two artifacts share the same callback pattern.
- **Zero-Entropy Shift:** File size and checksums remain within "standard deviation" limits of legitimate business documents to bypass static heuristic analysis.
- **Kill-Switch:** If the `reality-controller` identifies a high-risk security sweep (e.g., an automated AV scan), the module can issue an instantaneous "nuke" command to force the artifact to self-delete or overwrite itself with legitimate, benign filler data.
