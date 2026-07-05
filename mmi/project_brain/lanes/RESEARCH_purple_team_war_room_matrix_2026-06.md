# Research: Purple Team, War Room Scoring & Active Defense

Date ingested: 2026-06-30  
Source: Matt research (Gemini/conversation) — enterprise purple-team + war room matrix  
Status: **Research artifact** — mixed enterprise reference + MMI-adaptable concepts  
Jurisdiction: **Canadian legal refs** (Criminal Code s.342.1) + global MITRE  
Lane: `lanes/MMI_SECURITY_INTEL_LANE.md`  
Rigor: `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` — Canada-first for legal claims; MITRE IDs verify against attack.mitre.org

---

## MMI fit summary

| Content block | MMI home | Build now? |
|---------------|----------|------------|
| Purple Team exercise template (6 phases, ATT&CK) | `intel/templates/PURPLE_TEAM_EXERCISE_TEMPLATE.md` | **Design** — after IR template |
| War Room detection scoring matrix (Tier 1–4) | `intel/WAR_ROOM_SCORING_MATRIX.md` | **Design** — adapt tiers for **local MMI war room**, not enterprise SIEM |
| MITRE threat-actor test planning flow | Intel brief / exercise annex | **Research OK** |
| Active defense legal boundary (CA s.342.1, no hack-back) | `intel/ACTIVE_DEFENSE_LEGAL_BOUNDARY.md` | **Yes — Canadian vital** |
| Rust DSL war room parser | `lanes/RESEARCH_control_plane_dsl_2026-06.md` (future) | **Research only** — not MMI v1; advisory CLI stays Python |
| ADCS ESC1 purple scenario | Enterprise appendix | **Reference only** — assumes AD; not solo-operator Mini PC |
| Honey-token legal checklist | `intel/HONEYTOKEN_LEGAL_CHECKLIST.md` | **Design** — before any deception deploy |
| Honeypot Docker / Sigma / SOAR playbook | Out of MMI software scope | **No build** without Matt auth + separate infra |

**War room Phase 6 (Impact)** correctly points to: *read-only dashboard + communication protocols* — that **is** current `mmi/war_room.py`. It does **not** mean EDR isolation or SOAR automation from MMI Python.

---

## 1. Purple Team Exercise Template (enterprise reference)

| Phase | ATT&CK | Red | Blue |
|-------|--------|-----|------|
| 1 Initial Access | T1566.001 Spearphishing Attachment | Macro beacon email | Email gateway, EDR macro policy |
| 2 Persistence | T1547.001 Registry Run Keys | HKCU Run key | SIEM registry alerts |
| 3 Credential Access | T1003.001 LSASS dump | Non-standard dump | EDR block/alert |
| 4 Lateral Movement | T1021.002 SMB Admin Shares | C$ with creds | Network analytics |
| 5 Exfiltration | T1041 Exfil over C2 | 1GB dummy via DNS/HTTPS | Egress baseline, firewall |
| 6 Impact | T1486 Data Encrypted for Impact | BitLocker test dir lock | **War room checklist + read-only panel** |

**MMI adaptation:** For Matt's stack, Phase 6 maps to:
- `mmi/war_room.py --watch` (orient)
- `INCIDENT_RESPONSE_TEMPLATE.md` + `INCIDENT_COMMANDER_CHECKLIST.md` (when filed)
- `scripts/mmi_cold_backup.py --backup-and-push` (recovery anchor)

Phases 1–5 assume **enterprise controls** (EDR, SIEM, AD). Tag `[Enterprise Reference — Requires Localization]` for Canadian SMB context.

---

## 2. War Room & Technical Detection Scoring Matrix

| Tier | Technical (Blue) | Leadership / War Room |
|------|------------------|----------------------|
| **4 Optimized** | Auto-block; SIEM context <5 min | Strategic lead maps cascade <15 min; dashboards auto-update |
| **3 Proficient** | Alert <15 min; manual correlation | IC contains <30 min; complexity breaks |
| **2 Lagging** | Detection >1 hr or post-impact | Tunnel vision; manual exec updates |
| **1 Failed** | Undetected until red disclosure | No chain of command; evidence destroyed |

**MMI v1 reality check:**

| Enterprise assumption | MMI war room today |
|----------------------|-------------------|
| SIEM auto-parse <5 min | **No SIEM** — local `tasks.json` + project brain |
| Executive dashboard auto-update | **`war_room.py --watch`** — manual refresh interval |
| Automated host isolation | **Out of scope** — advisory docs only |
| Tier scoring | **Future:** self-assessment worksheet in `intel/WAR_ROOM_SCORING_MATRIX.md`, not live scoring in CLI |

Prototype scoring for **Matt MMI operator** (not enterprise SOC):

| Tier | MMI operator criteria |
|------|----------------------|
| 4 | Pipe loaded, backup verified today, IR template open, decision log started <15 min |
| 3 | Active task clear, backup within 24h, roles assigned |
| 2 | Pipe DRY or stale backup, ad-hoc response |
| 1 | No war room, no backup, no decision log |

---

## 3. MITRE ATT&CK collaborative test planning

```
Profile Threat Actor → Map TTPs → Execute & Log → Heat map gaps
```

- Use [MITRE ATT&CK Groups](https://attack.mitre.org/groups/) — **verified global framework**
- Example: LockBit → T1486 + T1078
- Log results with exact ATT&CK IDs in project brain

**Canada-first:** Actor profile may be global; **legal/notification** section of exercise debrief stays PIPEDA/Law 25/CCCS.

---

## 4. Active defense — legal boundary (Canadian)

**Hard line:** Hacking back = illegal (US CFAA; **Canada Criminal Code s.342.1** — unauthorized use of computer).

**Legal inside owned boundary:**
- Tarpitting / LaBrea-style time-waste
- Honey-tokens (passive beacon only)
- Honeypots with synthetic data
- Threat-intel poisoning of **your own** telemetry feeds

**Gray / caution:**
- Web-bug docx beacons — legal to place; risky if causes external machine harm
- Mid-incident VPS takedown — legal but may burn attacker infra before eviction complete

**MMI rule:** Document legal checklist **before** any deception asset. MMI software does **not** deploy honeypots or beacons.

---

## 5. Custom language / Rust DSL (research — not build auth)

Strict typed DSL (`CMD:ISOLATE|ID:1234`) — rejects injection via `u32` parse.

**Fits MMI as:** control-plane hardening **research** (Ed25519 + typed envelope), not production Rust runtime on Mini PC v1.

**Does not fit:** `IsolateHost` as automated MMI action — contradicts advisory-only doctrine.

Reconcile with `lanes/RESEARCH_instruction_set_randomization_mtd_2026-06.md` (if filed) and Ed25519 control-plane v0.

---

## 6. ADCS ESC1 scenario (enterprise appendix)

Assumes: Certify, domain CA, Rubeus, Event 4887/4768, PKINIT.

**Status:** `[Enterprise Reference]` — valid purple-team content for orgs with AD CS; **not** Matt solo-operator Mini PC baseline.

---

## 7. Honey-token legal checklist (file as design doc)

1. **No hacking back** — honeypot on owned paths; beacon = passive outbound only  
2. **Workplace privacy** — AUP disclosure; avoid false accusations on employees  
3. **Asset integrity** — no real PII on honeypots; synthetic data only; no pivot to third parties  

---

## 8. Honeypot / Docker / Sigma / SOAR (out of MMI v1 build)

| Item | Verdict |
|------|---------|
| `honeypot_db.py` | Reference architecture — do not run on MMI Mini PC without isolated lab |
| `docker-compose.yml` internal network | Valid pattern — **separate lab project**, not `mmi/` Codex task |
| Sigma PB-DECEPT-01 | Enterprise SIEM — reference for future if Matt has Windows file server + SIEM |
| SOAR EDR isolation curl | **Out of MMI scope** — human invokes via IR checklist, not MMI Python |

---

## Recommended pipeline seeds (after intel brief + IR template)

| Order | Task | Output |
|-------|------|--------|
| 1 | Purple team template (Claude) | `intel/templates/PURPLE_TEAM_EXERCISE_TEMPLATE.md` |
| 2 | MMI-adapted scoring matrix (Claude) | `intel/WAR_ROOM_SCORING_MATRIX.md` |
| 3 | Active defense legal boundary (Claude) | `intel/ACTIVE_DEFENSE_LEGAL_BOUNDARY.md` |
| 4 | Honey-token legal checklist (Claude) | `intel/HONEYTOKEN_LEGAL_CHECKLIST.md` |

**Do not seed:** Rust DSL build, Docker honeypot, SOAR automation — unless Matt explicitly authorizes lab infra.

---

## Hard stops

- MMI war room stays **read-only** — no auto-isolation from CLI  
- No hack-back; Canada Criminal Code s.342.1 applies  
- Enterprise purple content ≠ solo-operator default — always label jurisdiction and environment  
- Unverified vendor blog links in source paste — `NEEDS VERIFY` if cited as stats
