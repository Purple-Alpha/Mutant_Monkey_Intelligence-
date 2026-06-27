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

---

## Superintendent action — Lane 1 scope

### Product surface (Lane 1 only)

**#43 Geo-Context Agent** (proposed) ingests **tenant-declared legitimate context** — service area, jurisdiction hints, expected language/locale, and compliance policy-pack references — and emits **closed facts only** for downstream agents to compare against observed session/network context. It does **not** detect anomalies, score fraud, block traffic, or route decoys.

Example: an MSP declares clients in BC + AB; an inbound artifact shows EU hosting context. #43 emits `declared_service_area_mismatch` as an **observation**; **#79** (if invoked) emits `geo_velocity_anomaly`; scoring layers combine facts — none alone is a verdict.

### Explicit out of scope

- Lane 4 deception (Reality Controller, `geo_fence_manager.md`, tarpit, synthetic telemetry, Hack-Bot)
- Person-level tracking or cross-session geo identity (Lane 3 bar)
- Autonomous block / allow / payment / containment
- Re-emitting #76 Layer 0 geo brief or #79 velocity detection logic
- Production dispatch, AUTH-5, or scoreboard lifecycle change from this research pass

### Yes / No question for Matt

**Is tenant service area + jurisdiction context (Lane 1) the intended #43 product surface?**

| Response | Next step |
|----------|-----------|
| **Yes** | Promote `Geo_Context_Agent_Design_Contract_Deep_Dive_DRAFT.md` to formal contract draft; pre-build gate; hold build until Matt authorization |
| **No** | Record alternate surface in Superintendent action; extend hold (MMI-DEC-222) |
| **Extended hold** | Document missing evidence: tenant roster schema, legal review on jurisdiction advisory text, or #79 overlap proof |

### If extended hold — evidence still missing

1. Canonical tenant service-area roster format (caller-owned, #10 lookalike pattern)
2. Legal review DEC if jurisdiction output is customer-facing beyond internal facts
3. Proof that Lane 1 facts integrate with #79 without duplicate `geo_signal` emission

---

## Reconciliation appendix: #43 vs #76 vs #79

| Agent | Layer | Emits | Consumes | #43 must not duplicate |
|-------|-------|-------|----------|------------------------|
| **#76 GeoIntelAgent** | Layer 0 | `GeoBriefing` — brief-only geo intel from inbound artifact metadata | Raw headers / artifact metadata | Raw geo intel re-emission; Layer 0 brief assembly |
| **#79 GeoVelocityAgent** | Layer 1 | `geo_signal` — impossible travel, region-hop anomalies | Layer 0 `GeoBriefing` + session timeline facts | Velocity detection, anomaly scoring, `geo_signal` writer role |
| **#43 Geo-Context (proposed Lane 1)** | Context synthesis | `TenantGeoContextFacts` — declared service area, jurisdiction frame, expected locale, policy-pack ref | Tenant config roster (caller-supplied) + optional #76 brief for comparison | Detection logic, decoy routing, fraud verdict, block/allow |
| **#43 (proposed Lane 2 boundary)** | Risk input only | May pass through anonymization observations already in #76 brief — only if gap proven | #76 output | Anything #79 or scoring pipeline already owns |

### Fact vocabulary (no collision)

| Fact type | Owner |
|-----------|-------|
| `observed_country`, `observed_asn_class`, header-chain parse | #76 |
| `geo_velocity_anomaly`, impossible-travel signal | #79 |
| `declared_service_area`, `declared_jurisdiction_frame`, `expected_locale`, `policy_pack_ref` | **#43 (Lane 1)** |
| `declared_vs_observed_mismatch` (observation, not verdict) | **#43 (Lane 1)** |
| `entrapment_score`, decoy persona, Reality Mismatch | Lane 4 **PARK** — not #43 |

### Integration pattern (target)

```
Tenant roster (caller) -> #43 Geo-Context -> TenantGeoContextFacts
#76 GeoBriefing (read)  ->       |              declared_vs_observed_mismatch (fact)
                                 v
                           Scoring / #79 / human review (downstream — not #43)
```

**Verdict:** Keep #43 as **Lane 1 context synthesis** reconciled with, not merged into, #76 and #79.
