# Phase 2 — Knowledge Foundation Agent Design Contract
## Layer 0: Six Threat Intelligence Agents

**Document type:** Agent Design Contract (pre-§11)
**Status:** §11 SIGNED — Matt Nichol June 10th 2026. Build authorization granted per §11 scope.
**Date drafted:** June 10, 2026
**Drafted by:** Claude (advisory lane) — per AGENTS.md §2.1
**Authority:** Matt Nichol — sole signing authority
**Repo path:** `4. Product_Roadmap/Phase2_Knowledge_Foundation_Agent_Design_Contract.md`
**Depends on:** Phase 1 Infrastructure Contract §11 SIGNED `fe355da`

---

## §0 — Purpose

This contract governs all six Layer 0 Threat Intelligence agents. These agents form the knowledge foundation the detection swarm reads from before making any determination. They brief — they do not detect, score, flag, or produce verdicts. Ever.

All six share the same pattern, the same Evidence Stage, and the same governance rules. One contract covers all six. They can be built in parallel off this single signature.

---

## §1 — Scope

### In scope
1. **PhishIntelAgent** — phishing tactics, lookalike domains, credential harvest patterns, social engineering templates
2. **RansomwareIntelAgent** — ransomware delivery vectors, malicious attachment patterns, known campaign lures
3. **BECIntelAgent** — business email compromise schemes, invoice fraud templates, CEO impersonation patterns, wire transfer language
4. **TrojanDeliveryIntelAgent** — Trojan delivery methods, weaponised documents, macro-enabled files, delayed payload patterns
5. **GeoIntelAgent** — IP ranges associated with known campaigns, geo-velocity threat context, time-of-day anomaly patterns
6. **AIGenContentIntelAgent** — AI-generated text patterns, deepfake image indicators, AI-assisted phishing language signatures

### Explicitly out of scope
- Detection — no knowledge agent may flag, score, or produce a verdict on any email
- Layer 1 detection agents — separate contracts required
- ReconciliationAgent — separate contract required
- The Lung — separate contract required, blocked on real tenant data
- Collective Immune System — DEPTH GATE CLOSED
- Mutation Engine extension — separate contract required
- Any Stage B autonomy capability — STAGE_B GATE CLOSED
- Any change to Phase 1 signed surfaces

---

## §2 — Locked Design Decisions

| # | Decision | Locked value |
|---|---|---|
| P2-D1 | Role of all six agents | Brief only. No detection. No scoring. No verdicts. No AgentContributions to the evidence ledger. |
| P2-D2 | Output format | Structured briefing object — closed schema per agent, defined in §3 |
| P2-D3 | Evidence Stage | ES1 at build. ES2 requires adversarial synthetic tests. ES3 requires real-data signals. All six start at ES1. |
| P2-D4 | Knowledge source at build | Seeded manually from curated threat intelligence. No autonomous web ingestion at Phase 2. Automated ingestion is Phase 5+ territory. |
| P2-D5 | Mutation gate | No knowledge agent may update its own knowledge base autonomously. All updates require the signed mutation process (Phase 5). |
| P2-D6 | Tenant isolation | Knowledge base is global — same briefings available to all tenants. No tenant-specific knowledge at this stage. |
| P2-D7 | Write to blackboard | Knowledge agents do NOT write to `core/blackboard/`. They are read-only references for Layer 1 agents. |
| P2-D8 | Parallel build | All six agents may be built simultaneously. Same pattern. Same test classes. Same governance rules. |
| P2-D9 | Linux-primary path | All files land at `/home/socialarchitect/northstar/` in Linux working copy. No Windows paths. |

---

## §3 — Agent Definitions and Briefing Schemas

All six agents return a briefing object when queried by a Layer 1 agent. The briefing object is read-only. No Layer 1 agent may modify it.

### PhishIntelAgent
**Path:** `core/knowledge/phish_intel_agent.py`
**Briefing schema:**
```
known_phish_domains:     list[str]  — confirmed malicious domains
lookalike_patterns:      list[str]  — regex patterns for domain spoofing
credential_harvest_urls: list[str]  — known credential harvest pages
social_engineering_cues: list[str]  — language patterns associated with phishing
last_updated:            str        — ISO 8601
confidence_floor:        float      — minimum confidence to surface a match
```

### RansomwareIntelAgent
**Path:** `core/knowledge/ransomware_intel_agent.py`
**Briefing schema:**
```
known_delivery_hashes:   list[str]  — attachment hashes associated with ransomware
lure_language_patterns:  list[str]  — subject/body language used in ransomware lures
known_c2_domains:        list[str]  — command and control domains
file_extension_flags:    list[str]  — extensions commonly used in ransomware delivery
last_updated:            str
confidence_floor:        float
```

### BECIntelAgent
**Path:** `core/knowledge/bec_intel_agent.py`
**Briefing schema:**
```
ceo_impersonation_patterns:    list[str]  — display name spoofing patterns
invoice_fraud_templates:       list[str]  — known invoice manipulation language
wire_transfer_trigger_phrases: list[str]  — phrases that precede wire transfer requests
vendor_redirect_patterns:      list[str]  — payment redirect language patterns
last_updated:                  str
confidence_floor:              float
```

### TrojanDeliveryIntelAgent
**Path:** `core/knowledge/trojan_delivery_intel_agent.py`
**Briefing schema:**
```
weaponised_extensions:    list[str]  — file extensions used in Trojan delivery
macro_trigger_patterns:   list[str]  — document types known to carry malicious macros
delayed_payload_markers:  list[str]  — indicators of staged/delayed payload delivery
known_dropper_hashes:     list[str]  — hashes of known dropper files
last_updated:             str
confidence_floor:         float
```

### GeoIntelAgent
**Path:** `core/knowledge/geo_intel_agent.py`
**Briefing schema:**
```
high_risk_ip_ranges:      list[str]  — CIDR ranges associated with known campaigns
high_risk_countries:      list[str]  — ISO country codes with elevated threat activity
time_anomaly_windows:     list[dict] — time windows where geo anomalies are significant
known_vpn_exit_nodes:     list[str]  — IP ranges associated with anonymisation services
last_updated:             str
confidence_floor:         float
```

### AIGenContentIntelAgent
**Path:** `core/knowledge/ai_gen_content_intel_agent.py`
**Briefing schema:**
```
ai_text_signatures:       list[str]  — language patterns associated with AI-generated copy
deepfake_image_markers:   list[str]  — visual artifact patterns in AI-generated images
ai_phishing_templates:    list[str]  — known AI-assisted phishing language structures
image_ratio_thresholds:   dict       — image-to-text ratios that indicate bulk/AI content
last_updated:             str
confidence_floor:         float
```

---

## §4 — What These Agents Do NOT Authorize

- No knowledge agent may write to `core/blackboard/`
- No knowledge agent may produce a score, flag, or verdict
- No knowledge agent may update its own knowledge base — all updates via Phase 5 mutation process
- No knowledge agent may access tenant email data directly
- No autonomous ingestion from external sources — Phase 5 territory
- No change to any Phase 1 signed surface

---

## §5 — Test Requirements

Three test classes required per agent per AGENTS.md §5:

**Class 1 — Expected pass**
- Briefing object returns correctly structured output on valid query
- All required fields present and correctly typed
- `last_updated` is a valid ISO 8601 timestamp
- `confidence_floor` is between 0.0 and 1.0

**Class 2 — Adversarial**
- Query with malformed input returns safe error, not crash
- Query attempting to write to blackboard is rejected
- Query attempting to modify briefing schema is rejected
- Briefing object cannot be mutated by the calling agent

**Class 3 — Known-gap xfail**
- Real-time threat feed ingestion — deferred. Reason: autonomous ingestion not authorized until Phase 5. Completion path: Phase 5 mutation engine contract.
- Cross-tenant knowledge differentiation — deferred. Reason: global knowledge base sufficient at Phase 2. Completion path: post-launch tenant data analysis.

---

## §6 — Failure Modes

| Failure mode | Detection | Response |
|---|---|---|
| Knowledge agent produces a verdict | Test Class 2 + gate | Immediate fail — agent cannot ship |
| Knowledge agent writes to blackboard | Test Class 2 + gate | Immediate fail — scope violation |
| Autonomous knowledge update | Drift detection monitor | Flag to Matt — mutation process required |
| Stale knowledge base | `last_updated` field monitoring | Alert to operator — manual refresh required |
| Schema drift | Schema validation on every query | Gate rejects malformed output |

---

## §7 — Relationship To Existing Signed Specs

| Existing signed spec | Relationship |
|---|---|
| Phase 1 Infrastructure Contract | All six agents read from global knowledge base. They do not write to `core/blackboard/`. Phase 1 surfaces untouched. |
| Agent Health Score Rubric | All six agents scored at ES1 on build. Health scores calculated after gate clean. |
| Swarm Build Map | Phase 2 — all six can be built in parallel. Gate requirement: all six must score 70+ before Phase 3 begins. |
| Tiered Detection Intensity spec | Not touched by this contract. |

---

## §8 — Scoreboard Updates Required On Signing

Add six new rows to `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`:

| Row | Agent | Status | Layer | Priority |
|---|---|---|---|---|
| #72 | PhishIntelAgent | NEEDS_SIGNED_CONTRACT → GOVERNED on sign | 6 Learning/Governance | BREADTH |
| #73 | RansomwareIntelAgent | NEEDS_SIGNED_CONTRACT → GOVERNED on sign | 6 Learning/Governance | BREADTH |
| #74 | BECIntelAgent | NEEDS_SIGNED_CONTRACT → GOVERNED on sign | 6 Learning/Governance | BREADTH |
| #75 | TrojanDeliveryIntelAgent | NEEDS_SIGNED_CONTRACT → GOVERNED on sign | 6 Learning/Governance | BREADTH |
| #76 | GeoIntelAgent | NEEDS_SIGNED_CONTRACT → GOVERNED on sign | 6 Learning/Governance | BREADTH |
| #77 | AIGenContentIntelAgent | NEEDS_SIGNED_CONTRACT → GOVERNED on sign | 6 Learning/Governance | BREADTH |

---

## §9 — Open Questions For Next Session

1. Initial knowledge base seeding — does Matt want to provide curated threat intel manually, or does Cursor seed from public sources (MITRE ATT&CK, APWG) at build time?
2. Knowledge refresh cadence — how often does the knowledge base get manually updated before Phase 5 mutation is live?
3. Phase 3 contract — one contract for all Layer 1 detection agents or split by agent? Recommendation: individual contracts because detection agents have different evidence types and boundary conditions.

---

## §10 — Phase Gate Requirement

Phase 2 closes when:
- All six agents gate-clean at 0/0
- All six agents score 70+ on Agent Health Score Rubric
- Scoreboard rows #72-77 updated to GATED
- Matt signs phase closure
- `decision_cycles_log.md` entry logged: type PHASE_CLOSURE, phase 2

---

## §11 — Operator Sign-Off

**Signed:** Matt Nichol
**Date:** June 10th 2026
