# Research: Polymorphic Ransomware Delivery via Adversarial Email Fraud

Date ingested: 2026-06-29  
Source: Gemini (main research) — Matt decision **A** (security-intel product lane)  
Status: **Research artifact — PASS WITH REVISIONS** (ChatGPT second opinion 2026-06-29)  
Verification: `lanes/RESEARCH_VERIFICATION_2026-06.md`  
Lane: `lanes/MMI_SECURITY_INTEL_LANE.md`

> **MITRE IDs verified.** HTML smuggling (T1027.006) confirmed. Kerberoasting context-limited to AD. Predictions = `FORECAST_LOW_CONFIDENCE`. Endpoint swarm = research only, not build.

---

## Context encapsulation

- **Target threat domain:** Evolving polymorphic ransomware delivery via adversarial email fraud
- **Raw indicators:** Weaponized links and payload drop chains bypassing standard SEGs/EDRs via dynamic infrastructure rotation, runtime obfuscation, context-aware delivery

---

## MITRE ATT&CK mapping (summary)

| Tactic | Technique | ID | Notes |
|--------|-----------|-----|-------|
| Initial Access | Spearphishing Link | T1566.002 | Personalized vectors, redirect infrastructure |
| Execution | User Execution: Malicious Link | T1204.001 | Browser exploit or social-engineered download |
| Defense Evasion | Obfuscated Files/Information | T1027 | Homoglyphs, polymorphic JS, runtime decryption |
| Discovery | System Information Discovery | T1082 | Client fingerprinting before stage-2 |
| C2 | Web Protocols | T1071.001 | HTTPS, domain fronting, ephemeral tunnels |
| Impact | Data Encrypted for Impact | T1486 | Ransomware, shadow copy deletion |

**Kill chain (conceptual):** Spearphish link → client profiling → (sandbox) benign 404 OR (human) HTML smuggling → HTTPS C2 → ransomware execution.

---

## Technical primitives (research notes)

### Delivery obfuscation

- Ephemeral domains, homoglyph spoofing, conditional redirects via compromised CMS as TDS

### HTML smuggling (T1027.006)

- Benign page with base64 Blob; client-side JS builds download in browser cache — bypasses proxy file inspection on first click

### Stage-1 loader

- Sleep intervals, indirect syscalls / API hooking evasion, environmental checks (registry, processes, language packs)

### Lateral movement (enterprise context)

- Kerberoasting (T1558.003), SMB/RPC sweep, memory-only paths — **assumes AD environment**

---

## Evasion vs defenses (research)

| Defender control | Adversarial response (per research) |
|------------------|-------------------------------------|
| SEG sandbox (120–180s) | Extended delays, human-only triggers |
| IP/domain reputation | High-reputation cloud / edge abuse |
| EDR memory inspection | Polymorphic crypters, opcode mutation |
| Behavioral alerts on vssadmin | Decoupled execution via RPC/WMI under trusted processes |

### 6–12 month predictions (unverified)

1. AI-assisted JIT compilation in delivery scripts  
2. C2 via signed enterprise workflows (Apps Script, Power Automate, Cloudflare Workers)

---

## Proposed defensive layers (research — not MMI build auth)

- Network: TLS inspection, default-deny egress  
- Endpoint: block browser/email spawning script interpreters; CET where available  
- Identity: ZTNA posture, admin credential isolation  
- Application: WDAC/AppLocker, block execution from user-writable paths  

### Theoretical agentic swarm (research only — **not authorized for MMI implementation**)

Ingress → Evaluator (entropy/gRPC) → Containment (WFP isolation, process suspend).  
**Gap analysis in source:** latency, BYOVD kernel blindness, compromised agent pipeline.

---

## MMI relevance

| Relevant to MMI operator | Not MMI codebase scope |
|--------------------------|-------------------------|
| Phish/link discipline on Mini PC | Endpoint Ingress/Containment agents |
| Cold backup as recovery layer | Enterprise SEG/EDR integration |
| Research input for security-intel product lane | gRPC swarm on workstation |

---

## Next research actions

1. Source verification pass (ChatGPT/Gemini) for cited tactics  
2. Claude: synthesize into `architecture/MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` (pipeline task)  
3. Do not conflate with `mmi/command_center.py` operator scope without MVP spec
