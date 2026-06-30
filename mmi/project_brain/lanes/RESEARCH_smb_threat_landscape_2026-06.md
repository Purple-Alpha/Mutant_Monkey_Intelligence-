# Research: SMB Threat Landscape (2026)

Date ingested: 2026-06-29  
Source: Gemini (main research) — Matt decision **A** (security-intel product lane)  
Status: **Research artifact — PASS WITH REVISIONS** (ChatGPT second opinion 2026-06-29)  
Verification: `lanes/RESEARCH_VERIFICATION_2026-06.md`  
Lane: `lanes/MMI_SECURITY_INTEL_LANE.md`

> **Do not use original exact stats externally.** Purge: 60% closure, 4× targeting, $53k/hour. Keep 88% ransomware only with Verizon 2025 DBIR SMB dataset framing. See verification doc for safe language.

---

## 1. Threat origin & volume

- SMBs targeted **~4×** more frequently than large enterprises (per research — verify source)
- **Ingress:** AI-driven social engineering, hyper-personalized spear-phish at scale
- **Velocity:** Initial access to AD compromise + exfil in **<25 minutes** (enterprise assumption — verify)

---

## 2. Attack types (Big Three)

| Type | Metric (research) | Method |
|------|-------------------|--------|
| **Ransomware** | **88%** of successful SMB data breaches (verify) | Polymorphic loaders, hash shifting |
| **BEC** | **~33%** initial breaches (verify) | Invoice fraud, exec mailbox compromise, deepfake audio |
| **Supply chain** | **30%** of SMB breaches (verify) | MSP / vendor compromise → downstream access |

---

## 3. Defensive efficacy

### Working (research)

| Control | Claim |
|---------|--------|
| Hardware-enforced MFA | ~90% block on credential stuffing/spray |
| Tested IR plans | ~$2.66M average savings vs ad-hoc response (verify) |
| MDR / vCISO | Detection/containment weeks → hours |

### Failing (research)

| Control | Why (per research) |
|---------|---------------------|
| Legacy AV | Fileless, reflective injection, polymorphic stubs |
| Basic awareness training | AI removes grammar/format tells |
| Static online backups | **96%** of ransomware attempts backup destruction first (verify) |

---

## 4. Current mitigations (industry)

1. **Immutable backups (3-2-1-1)** — air-gapped / undeletable cloud copies  
2. **Application whitelisting (WDAC/AppLocker)** — allow-list execution  
3. **MSSPs** — ~40% of SMB security budget to outsourced SOC (verify)

---

## 5. Impact (research)

- **60%** of SMBs out of business within 6 months after major attack (verify)  
- **Manufacturing:** 72–84h recovery downtime (OT)  
- **Healthcare:** high extortion value, crisis spend  
- **$53,000/hour** average SMB downtime cost (verify)

---

## MMI operator alignment (local-first)

| Research theme | Matt MMI stack today |
|----------------|----------------------|
| Backup destruction | Local archive + B2 **cold** push (`--backup-and-push`) |
| Immutable/offline copy | B2 mirror; not live runtime — partial 3-2-1-1 |
| MFA | Apply to B2, email, Backblaze (operator) |
| MDR/swarm/WDAC | **Not** MMI software v1 — separate machine policy |

---

## Product lane implication (Matt decision A)

This research supports a **bounded MMI Security Intel** product:

- **In scope (future MVP):** Research synthesis, ATT&CK-tagged briefs, operator checklists, links to project brain  
- **Out of scope (v1):** Endpoint agents, SEG integration, MSSP automation, enterprise AD tooling  

See `architecture/MMI_SECURITY_INTEL_PRODUCT_SCOPE.md`.

---

## Next steps

1. Evaluator/source-verification pass on statistics  
2. Claude: MVP architecture from both research files (pipeline task)  
3. Keep separate from core war room / queue until MVP spec approved
