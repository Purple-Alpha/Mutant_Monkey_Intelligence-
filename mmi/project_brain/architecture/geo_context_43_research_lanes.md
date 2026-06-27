# #43 Geo-Context — Research Lanes (MMI-DEC-222 hold)

**Date:** 2026-06-27  
**Lane:** `RESEARCH`  
**Authority:** Matt geo-tracking research framing. **Not** build authorization. **Not** §11.

**Reference material (read-only):** `mmi/project_brain/architecture/reality_controller/geo_fence_manager.md`  
That document is **Reality Controller / lab deception research** — not a build spec for #43.

---

## Question

What should scoreboard **#43 Geo-Context** become, given:

| Surface | Status | Role |
|---------|--------|------|
| **#43 Geo-Context** | `SPEC_ONLY` · `NEEDS_SIGNED_CONTRACT` | Sender provenance / geo-velocity *proof protocol* (scoreboard label) |
| **#79 GeoVelocityAgent** | `GOVERNED_AGENT` ES2 | Layer 1 detection — `geo_signal` from Layer 0 `GeoIntelAgent` brief |
| **#76 GeoIntelAgent** | `GOVERNED_AGENT` ES1 | Layer 0 brief-only geo intel |
| **`received_chain_parser.py`** | Code foundation | Header chain parsing — not a governed #43 wrapper |
| **`geo_fence_manager.md`** | `RESEARCH_DESIGN` | Lab decoy persona / tarpit / shadow-serving — **parked** |

---

## Matt's lane split (authoritative for this research pass)

### Lane 1 — Legit geo-context *(in scope for future contract)*

**Purpose:** Tenant-facing, non-adversarial context for analysis and compliance posture.

| Signal class | Examples | Output shape |
|--------------|----------|--------------|
| Service area | MSP/client declared regions, allowed countries | Facts only — no block/allow |
| Jurisdiction | Data residency hints, regulatory frame (advisory) | Structured context, not legal advice |
| Language / locale | Expected comms language vs observed | Mismatch as *observation*, not verdict |
| Compliance context | Which policy pack applies (reference to signed process docs) | Links to operator process, not auto-enforcement |

**Boundaries:** No payment action, no blocking, no person-level tracking. Caller-owned tenant policy roster (same pattern as #10 lookalike known-good domains).

**Relationship to #79:** #79 detects impossible travel / geo velocity **anomalies**. Lane 1 supplies **declared legitimate context** #79 (or downstream agents) may compare against — not replace #79.

---

### Lane 2 — Defensive geo-risk *(partially satisfied; clarify before build)*

**Purpose:** Security-relevant geo and network posture signals for fraud/risk scoring.

| Signal class | Examples | Existing home |
|--------------|----------|---------------|
| IP reputation | ASN, hosting provider, known-bad ranges | May overlap scoring pipeline / future dedicated detector |
| Anonymization | VPN, TOR, proxy exit hints | Partially in geo intel / header paths |
| Geo velocity | Impossible travel, region hop | **#79 GeoVelocityAgent** (governed) |
| Fraud/risk floor | Geo contributes to risk, never alone as verdict | AUTH-4 / scoring layer doctrine |

**Boundaries:** Facts and risk *signals* only — no autonomous block, no customer scanning, no active probing.

**Reconciliation:** Before any #43 build, document explicitly: **what #43 adds that #79 + #76 do not already emit.**

---

### Lane 3 — Privacy boundary *(cross-cutting — all lanes)*

**Hard rules:**

1. **No person-level tracking** unless Matt explicitly authorizes **and** legal review is recorded (separate DEC).
2. **No persistent cross-session identity** from geo alone at ES1.
3. **No raw PII in DER** — country/region/ASN class signals only; tenant isolation mandatory.
4. **No "track the user"** language in contracts — "observe session/network context" only.
5. Geo derived from **inbound artifact metadata** (headers, declared tenant config) — not browser GPS, not device geolocation APIs, unless a future signed contract says otherwise after legal gate.

Applies to Lanes 1–2. Lane 4 remains parked regardless.

---

### Lane 4 — Lab-only deception *(PARK — do not import into #43 ES1)*

**Source:** Concepts in `geo_fence_manager.md` map **here only**:

| geo_fence_manager concept | Disposition |
|---------------------------|-------------|
| Reality Anchor / entrapment by validation | **PARK** — v2 core tier |
| Clock-skew fingerprinting | **PARK** |
| Synthetic telemetry injection (Canvas/WebGL) | **PARK** |
| Progressive entropy / regional jitter | **PARK** |
| Entrapment Score tiers (0–100) | **PARK** — not fraud verdict |
| Regional mirroring / decoy personas | **PARK** — Reality Controller / legal gate |
| Geographic tarpitting | **PARK** — `tarpit_orchestrator.md` |
| Shadow-serving / invisible filtering | **PARK** |
| Reality Mismatch → Hack-Bot recommendation | **PARK** — operator gate; `trap_hack_rot_bots.md` |
| Geo-Context Header on internal traffic | **Split:** fraud/risk facts → Lane 2 if ever built; decoy routing → Lane 4 only |

**Do not** merge Reality Controller modules into #43 Agent Design Contract without separate legal/safety contract (see `reality_controller/README.md`).

---

## Mapping: geo_fence_manager.md → lanes

```
geo_fence_manager.md (REFERENCE ONLY)
├── Regional mirroring, decoy portals     → Lane 4 PARK
├── Latency calibration                   → Lane 4 PARK
├── Geographic tarpitting                 → Lane 4 PARK
├── Attacker origin profile (country/ASN) → Lane 2 (if facts-only) OR PARK if tied to decoy
├── Trust score for decoy behavior        → Lane 4 PARK
├── Contextual mismatch alert             → Lane 1 + Lane 2 (legit base vs observed)
└── VPN/TOR detection                     → Lane 2 (defensive geo-risk)
```

---

## #43 ↔ #79 verdict

| Option | Recommendation |
|--------|----------------|
| **A. Merge #43 into #79** | **Reject** — different layers (#43 scoreboard = protocol/synthesis; #79 = ES2 detector) |
| **B. #43 = Lane 1 legit context agent** | **Preferred research direction** — tenant-declared service area + jurisdiction facts; consumes no decoy logic |
| **C. #43 = RECLASSIFY** | **Defer** — only if Lane 1+2 fully covered by #79 + scoring with no gap |
| **D. #43 = build geo_fence_manager** | **Reject** — Lane 4 parked; high liability |

**Interim scoreboard posture:** Keep `#43` **`SPEC_ONLY` / `NEEDS_SIGNED_CONTRACT`**. Do not advance to `NEEDS_BUILD_AUTH` until a **Lane 1–2 only** Agent Design Contract draft exists and pre-build gate is clean.

---

## Recommended next steps (operator)

1. **Matt confirms** Lane 1 scope: is "tenant service area + jurisdiction context" the intended #43 product surface?
2. **Claude/Codex:** Draft `Geo_Context_Agent_Design_Contract_Deep_Dive.md` scoped to **Lanes 1–2 + Lane 3 privacy bar** — explicitly exclude Lane 4 by reference.
3. **Reconciliation appendix:** One-page #43 vs #79 vs #76 fact vocabulary — no duplicate `geo_signal` emission.
4. **Hold** deception / Reality Controller integration until legal contract exists.

---

## Boundaries (this document)

- Research / design only  
- No build authorization  
- No §11 signing  
- No scoreboard lifecycle change  
- No production dispatch  
- No AUTH-5  
- No person-level tracking  
- Lane 4 stays **PARK**

---

## Related

- `mmi/project_brain/architecture/reality_controller/geo_fence_manager.md` (reference only)  
- `mmi/project_brain/architecture/reality_controller/README.md`  
- `mmi/project_brain/architecture/purple_translation_layer.md`  
- Scoreboard #43, #76, #79  
- MMI-DEC-222 (#43 held for research)
- v2 Reality Anchor doctrine — commit `448315a` (entrapment-by-validation; Lane 4 PARK)
