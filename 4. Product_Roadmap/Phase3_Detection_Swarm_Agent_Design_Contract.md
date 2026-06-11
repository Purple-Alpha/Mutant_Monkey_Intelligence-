# Phase 3 — Detection Swarm Agent Design Contract
## Layer 1: Six Detection Agents

**Document type:** Agent Design Contract (pre-§11)
**Status:** §11 SIGNED — Matt Nichol June 10th 2026. Build authorization granted per §11 scope.
**Date drafted:** June 10, 2026
**Drafted by:** Claude (advisory lane) — per AGENTS.md §2.1
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Phase 1 §11 SIGNED fe355da + Phase 2 §11 SIGNED 43b5511

---

## §0 — Purpose

This contract governs all six Layer 1 Detection Agents. Active detection swarm. Each inspects one dimension of an inbound email and produces a structured evidence contribution to core/blackboard/. No agent produces a verdict. Ever. One signature covers all six. ELITE health score 85+ is the target for every agent.

---

## §1 — Scope

### In scope
1. SenderHistoryAgent — sender relationship mapping, prior contact history
2. GeoVelocityAgent — geographic origin analysis, IP context against sender history
3. ContentAnalyzer — NLP content analysis, urgency detection, BEC language matching
4. URLReceptor — URL reputation, redirect chain analysis, destination scanning
5. AttachmentSandbox — attachment behaviour, payload detonation in isolated cloud environment
6. ImageClassifier — image ratio analysis, AI-generated content detection

### Explicitly out of scope
- Verdicts — no detection agent may issue a verdict. ReconciliationAgent only.
- ReconciliationAgent — separate contract required
- The Lung — separate contract, blocked on real tenant data
- Collective Immune System — DEPTH GATE CLOSED
- Mutation Engine — separate contract required
- Any Stage B autonomy — STAGE_B GATE CLOSED
- Any change to Phase 1 or Phase 2 signed surfaces

---

## §2 — Locked Design Decisions

| # | Decision | Locked value |
|---|---|---|
| P3-D1 | Agent output | Structured evidence contribution only. Written to core/blackboard/ per Phase 1 schema. No verdict field exists. |
| P3-D2 | Evidence type per agent | Closed enum per agent boundary section. No agent may write outside its assigned evidence type. |
| P3-D3 | Layer 0 dependency | Each agent must query its assigned knowledge agent before producing a contribution. Briefing is mandatory input. |
| P3-D4 | Execution environment | All processing cloud-side. No client-side compute. No network traversal of client infrastructure. |
| P3-D5 | Tenant isolation | Every blackboard write includes tenant_id. Reads filtered by tenant_id. No cross-tenant data access. |
| P3-D6 | Health score target | ELITE — 85+ on signed Agent Health Score Rubric. Gate does not close below 85 for any agent. |
| P3-D7 | Attacker cost contribution | Every agent documents its contribution to the Attacker Cost Model in §4 — money, time, anonymity, reputation. |
| P3-D8 | Evidence Stage target | ES2 minimum at build. ES3 as the goal. Adversarial synthetic tests required. |
| P3-D9 | Linux-primary path | All files at /home/socialarchitect/northstar/core/detectors/. No Windows paths. |

---

## §3 — Agent Boundary Sections

### §3.1 — SenderHistoryAgent
**Path:** core/detectors/sender_history_agent.py
**Evidence type:** sender_signal
**Layer 0 dependency:** None — reads from internal sender history store
**Boundary:** May only write sender_signal. May not access email body, attachments, or URLs.
**Attacker cost:** Strips anonymity — first-time sender impersonating known vendor surfaced immediately.

**Evidence contribution schema:**
```
known_contact:             bool   — sender in prior communication history
first_time_sender:         bool   — no prior contact record exists
prior_interaction_count:   int    — number of prior emails from this sender
last_contact_date:         str    — ISO 8601 of most recent prior contact
established_vendor:        bool   — sender matches known vendor profile
confidence:                float
```

---

### §3.2 — GeoVelocityAgent
**Path:** core/detectors/geo_velocity_agent.py
**Evidence type:** geo_signal
**Layer 0 dependency:** GeoIntelAgent (mandatory)
**Boundary:** May only write geo_signal. May read SenderHistoryAgent blackboard entry for same email_id. May not access email body or attachments.
**Attacker cost:** Strips anonymity — foreign infrastructure impersonating local vendor contextualised against sender history. Burns money maintaining clean IP infrastructure.

**Evidence contribution schema:**
```
sending_ip:            str    — originating IP
ip_country:            str    — ISO country code of sending IP
account_home_country:  str    — country from sender history
velocity_flag:         bool   — impossible travel or anomalous origin
high_risk_region:      bool   — IP in GeoIntelAgent high-risk range
vpn_detected:          bool   — IP matches known VPN exit node
sender_history_match:  bool   — geo consistent with prior contact history
confidence:            float
```

---

### §3.3 — ContentAnalyzer
**Path:** core/detectors/content_analyzer.py
**Evidence type:** content_signal
**Layer 0 dependency:** PhishIntelAgent + BECIntelAgent (both mandatory)
**Boundary:** May only write content_signal. May read subject and body only. May not access attachments, URLs, or headers directly.
**Attacker cost:** Costs time — BEC attacks require carefully crafted language that gets pattern-matched against continuously updated knowledge base.

**Evidence contribution schema:**
```
urgency_detected:          bool   — high-urgency language present
bec_pattern_match:         bool   — matches known BEC language pattern
wire_transfer_request:     bool   — explicit wire transfer language detected
ceo_impersonation_flag:    bool   — display name or language inconsistency
policy_violation:          str    — named policy violated if applicable
sentiment_score:           float  — 0.0 neutral to 1.0 high pressure
language_anomaly:          bool   — style inconsistent with sender history
confidence:                float
```

---

### §3.4 — URLReceptor
**Path:** core/detectors/url_receptor.py
**Evidence type:** url_signal
**Layer 0 dependency:** PhishIntelAgent (mandatory)
**Boundary:** May only write url_signal. URL resolution cloud-side only. May not access attachments or headers.
**Attacker cost:** Burns money — every malicious URL and redirect chain extracted, resolved, added to shared indicator database. Domain investment worthless after first detection.

**Evidence contribution schema:**
```
urls_found:                list   — all URLs extracted
malicious_url_detected:    bool   — match against known phishing domains
redirect_chain_anomaly:    bool   — redirect chain leads to suspicious destination
final_destination:         str    — resolved final URL
credential_harvest_flag:   bool   — destination matches credential harvest pattern
reputation_score:          float  — 0.0 clean to 1.0 malicious
confidence:                float
```

---

### §3.5 — AttachmentSandbox
**Path:** core/detectors/attachment_sandbox.py
**Evidence type:** attachment_signal
**Layer 0 dependency:** TrojanDeliveryIntelAgent + RansomwareIntelAgent (both mandatory)
**Boundary:** May only write attachment_signal. Sandbox fully isolated cloud-side. Zero-day candidate flag feeds mutation engine tracker only — does not auto-deploy any rule.
**Attacker cost — all four dimensions:**
- Money — infrastructure burned on first detonation, hash propagated to all tenants
- Time — behaviour-based detection means signature evasion is worthless
- Anonymity — callback destination extracted and logged on every execution attempt
- Reputation — zero-day candidates enter mutation pipeline, attack permanently documented

**Evidence contribution schema:**
```
attachment_present:          bool   — email contains attachment
file_hash:                   str    — cryptographic hash of attachment
known_malicious_hash:        bool   — hash matches known threat database
execution_attempted:         bool   — payload attempted to execute
network_callback_detected:   bool   — payload attempted external connection
callback_destination:        str    — IP or domain of attempted callback
file_drop_detected:          bool   — payload attempted to write files
macro_execution:             bool   — macro or script executed
zero_day_candidate:          bool   — unknown behaviour detected, feeds mutation engine only
confidence:                  float
```

---

### §3.6 — ImageClassifier
**Path:** core/detectors/image_classifier.py
**Evidence type:** image_signal
**Layer 0 dependency:** AIGenContentIntelAgent (mandatory)
**Boundary:** May only write image_signal. spam_signal_only field is critical — when true tells ReconciliationAgent this is a delivery problem not a fraud problem. Different action path.
**Attacker cost:** Costs time — AI-generated phishing imagery flagged and pattern-matched against continuously updated signature library.

**Evidence contribution schema:**
```
images_present:         bool   — email contains images
image_count:            int    — number of images detected
image_text_ratio:       float  — ratio of image content to text
ai_generated_detected:  bool   — AI generation artifacts present
deepfake_indicator:     bool   — deepfake patterns detected
bulk_content_flag:      bool   — image ratio consistent with newsletter or bulk send
spam_signal_only:       bool   — surface signals suggest spam but no fraud indicators present
confidence:             float
```

---

## §4 — Attacker Cost Model

| Dimension | What it means | Primary agents |
|---|---|---|
| Money | Attack infrastructure destroyed on first contact — domains burned, IPs flagged, hashes propagated globally | URLReceptor, AttachmentSandbox |
| Time | Swarm resolves faster than attackers can adapt — behaviour-based means signature evasion buys zero time | AttachmentSandbox, ContentAnalyzer |
| Anonymity | Every layer strips attacker cover — geo origin, sender history mismatch, callback destination, URL redirect chain | GeoVelocityAgent, SenderHistoryAgent, URLReceptor, AttachmentSandbox |
| Reputation | Burned indicators propagate to every tenant instantly — attack tools become liabilities | All six via Collective Immune System Phase 6 |

This is purely defensive architecture. We do not touch attacker systems. We do not retaliate. We make attacking our platform the worst ROI decision available.

---

## §5 — Test Requirements

**Class 1 — Expected pass**
- Evidence contribution writes correctly to core/blackboard/ with valid schema
- All required fields present and correctly typed
- Tenant isolation confirmed
- Layer 0 briefing consumed before contribution written

**Class 2 — Adversarial (ELITE standard)**
- Agent cannot write outside its assigned evidence type — attempt fails and logs
- Agent cannot produce a verdict field — fails at schema validation
- Agent cannot access another tenant's blackboard entries
- Agent cannot execute client-side — all confirmed cloud-side
- Malformed input returns safe error not crash
- Zero-day candidate flag cannot auto-deploy any rule — logs only
- ImageClassifier spam_signal_only must not trigger fraud action path

**Class 3 — Known-gap xfail**
- Real-data signal testing — deferred. Reason: requires production tenant traffic. Completion path: ES3 after first real tenant onboarded.
- Cross-agent reconciliation testing — deferred. Reason: ReconciliationAgent not yet built. Completion path: Phase 4.
- Collective Immune System propagation — deferred. Reason: DEPTH GATE CLOSED. Completion path: Phase 6.

---

## §6 — Failure Modes

| Failure mode | Detection | Response |
|---|---|---|
| Agent produces verdict field | Schema validation + Class 2 | Immediate fail — cannot ship |
| Agent writes outside evidence type | Schema validation + Class 2 | Immediate fail — scope violation |
| Client-side execution detected | Class 2 + architecture review | Immediate halt — Matt notified |
| Zero-day auto-deploys rule | Class 2 | Immediate fail — mutation process required |
| Tenant isolation breach | Class 2 | Immediate fail — ledger integrity at risk |
| spam_signal_only routes to fraud path | Class 2 | Immediate fail — false positive protection violated |
| Health score below 85 | Agent Health Score Rubric | Phase does not close — agent reworked until ELITE |

---

## §7 — Relationship To Existing Signed Specs

| Existing signed spec | Relationship |
|---|---|
| Phase 1 Infrastructure Contract | All six write to core/blackboard/ per Phase 1 schema |
| Phase 2 Knowledge Foundation Contract | All six consume Layer 0 briefings as mandatory input |
| Agent Health Score Rubric | ELITE 85+ required for all six |
| Swarm Build Map | Phase 3 — all six parallel. Gate: all six 85+ before Phase 4. |

---

## §8 — Scoreboard Updates Required On Signing

| Row | Agent | Status | Layer | Priority |
|---|---|---|---|---|
| 78 | SenderHistoryAgent | GOVERNED | 2 Detection | BREADTH |
| 79 | GeoVelocityAgent | GOVERNED | 2 Detection | BREADTH |
| 80 | ContentAnalyzer | GOVERNED | 2 Detection | BREADTH |
| 81 | URLReceptor | GOVERNED | 2 Detection | BREADTH |
| 82 | AttachmentSandbox | GOVERNED | 2 Detection | BREADTH |
| 83 | ImageClassifier | GOVERNED | 2 Detection | BREADTH |

---

## §9 — Open Questions For Next Session

1. AttachmentSandbox zero-day candidate flag — immediate Matt notification or queue for next mutation review session?
2. URLReceptor cloud-side DNS resolution infrastructure — needs a decision before build.
3. Phase 4 contract — ReconciliationAgent. Single agent, single contract. Ready to draft after Phase 3 gated.

---

## §10 — Phase Gate Requirement

Phase 3 closes when:
- All six agents gate-clean at 0/0
- All six agents score 85+ ELITE on Agent Health Score Rubric
- Scoreboard rows 78-83 updated to GATED
- Matt signs phase closure
- decision_cycles_log.md entry: type PHASE_CLOSURE, phase 3

---

## §11 — Operator Sign-Off

**Signed:** Matt Nichol
**Date:** June 10th 2026
