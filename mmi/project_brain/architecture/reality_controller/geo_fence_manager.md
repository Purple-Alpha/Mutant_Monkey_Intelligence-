# Geo-Fence Manager

**Status:** `RESEARCH_DESIGN — CORE TIER` | **Component:** Swarm Command Reality Controller  
**Objective:** Active Reality Entrapment and Synthetic Telemetry Injection.

> **Authority:** Research / lab doctrine only. **Lane 4 PARK.** Not MMI production authority,
> not build authorization for #43, and not production dispatch. See `README.md` and
> `geo_context_43_research_lanes.md`. Escalation to Hack-Bot requires operator gate — see
> `trap_hack_rot_bots.md`.

---

## 1. Core Philosophy: Entrapment by Validation

The `geo-fence-manager` is no longer a passive filter; it is the **Reality Anchor**. When an
attacker initiates contact, they are not just observed — they are **located** within a synthetic
environment that they themselves validate through their own recon tools.

The defensive edge: you do not need to block if you can make them believe they are already in
the real environment, where every action is recorded with forensic fidelity.

**Lane:** 4 (lab-only deception) — entire module.

---

## 2. Advanced Protocol: Reality Anchoring

- **Clock-Skew Fingerprinting:** Measure nanosecond-level drift between the attacker's TCP
  timestamps and the regional NTP baseline of their claimed location. Skew indicating
  cross-planet distance feeds a **Reality Mismatch** signal to the MMI project brain.
- **Synthetic Telemetry Injection:** Serve artifacts (Canvas / WebGL / OS-level variables) that
  cause the attacker's browser and tools to report local environmental data matching the decoy
  reality. Turn their recon tools against them with consistent, false, local metadata.
- **Progressive Entropy (Jitter / Latency):** Avoid flat-line tarpitting. Apply **Regional Jitter
  Models** — e.g. an attacker "in" Kelowna experiences the fluctuating network conditions of a
  saturated local ISP. Infrastructure feels alive, not throttled.

**Multi-Vector Consensus Rule:** No single signal (IP, clock-skew, canvas) may trigger Full
Reality Lock alone. Project brain requires **≥2 agreeing vectors** before Entrapment Score
escalation to tier 71–100.

---

## 3. Intelligence Outputs (The Data Stream)

When processing a request, attach a **Geo-Context Header** to internal traffic:

| Output | Description | Lane |
|--------|-------------|------|
| **Identity Anchoring** | Cross-reference IP-ASN-location with clock-skew and canvas fingerprint | 4 PARK |
| **Entrapment Score** (0–100) | Drives decoy depth — not a fraud verdict | 4 PARK |
| **Reality Mismatch** | Multi-vector divergence from claimed / persona reality | Signal to project brain; may recommend Hack-Bot profile |

**Entrapment Score tiers:**

| Score | Routing |
|-------|---------|
| 0–30 | Transparent route to low-interaction decoys |
| 31–70 | High-interaction environments with synthetic telemetry injection |
| 71–100 | Full Reality Lock — synthetic reality encapsulation; session fully mapped |

**Contextual Mismatch Alert** (e.g. Kelowna business vs offshore data center): in production
analysis this spans Lane 1 (legit client base) + Lane 2 (observed origin). In this module it
feeds decoy persona selection only — **Lane 4 PARK**.

---

## 4. Stealth and Integrity Protocols

- **Invisible Filtering:** Reject nothing. Accept the handshake, establish the connection,
  initiate the Synthetic Reality loop.
- **Reality Mapping:** Each Regional Persona maintains internal consistent state. If an attacker
  moves between decoy endpoints, local time, regional headers, and server latency remain
  consistent across hops (**Session Continuity Contract**).
- **Dynamic Mapping:** Geo-IP updates for VPN / TOR exit identification — defensive signal if
  extracted facts-only (Lane 2); decoy routing here remains Lane 4.
- **Shadow-Serving:** Tokyo and London attackers see different decoy realities for the same
  endpoint.

---

## 5. Integration Architecture (Core Feedback Loop)

- **Input:** Multi-vector packet metadata (TCP, NTP, WebGL / Canvas fingerprints).
- **Process:** Reality Controller requests a **Reality Anchor** from the MMI project brain,
  which generates a consistent, regionalized decoy environment.
- **Output:** Continuous instruction to `network-mutator` to maintain the regional persona
  throughout the session.

**Escalation boundary:** Reality Mismatch or Entrapment Score ≥71 may cause project brain to
**recommend** a Hack-Bot profile — enactment only via operator authorization
(`trap_hack_rot_bots.md`). Geo-fence senses; Hack-Bot strikes.

---

## 6. Evolution Path (Recursive Doctrine)

### 6.1 Adversarial Training Loop

When attackers probe for honeypot indicators (header analysis, packet timing tools), project
brain captures the probe as a **Detection Vector**. Doctrine updates so the next attacker using
that tool receives the response they expect — poisoning their recon data. The swarm becomes
more invisible the more it is attacked.

### 6.2 Predictive Reality (Future)

Move from static regional personas to **predictive personas**: idealized victim profiles derived
from attacker drift analysis — specific software versions, internal network names, bidder-context
for high-value targets. Requires separate legal gate before any production-adjacent use.

### 6.3 Hack-Bot Feedback (Gated)

On Reality Mismatch, project brain may recommend Hack-Bot to mirror attacker tooling **within
the blast chamber only**. Intelligence dominance posture — not autonomous counter-attack.
See `trap_hack_rot_bots.md`.

### 6.4 Governance Refinement

Every Reality Controller evolution updates this signed doctrine. MMI-DEC records material changes.
**Human-in-the-loop (Founder review) is the final gate** — never automate governance of
Reality Controller evolution.

---

## 7. Threat Vectors (Bake-In Now)

| Vector | Mitigation in doctrine |
|--------|------------------------|
| Honeypot detection suites | Adversarial Training Loop (§6.1) |
| Clock-skew evasion | Multi-Vector Consensus Rule — skew is one signal, not sole anchor |
| Anti-fingerprint / headless browsers | Fallback "degraded corporate endpoint" persona |
| Residential proxy with correct geo | Contextual Mismatch vs business client base, not geography alone |
| Cross-endpoint session drift | Session Continuity Contract (§4) |
| Legal / entrapment boundary | Lab-only; separate legal contract; `README.md` hard boundaries |

---

## Relationship to #43 Geo-Context (MMI-DEC-222 hold)

Scoreboard **#43 is not this module.** #43 research targets **Lanes 1–2** (legit geo-context +
defensive geo-risk facts) under the privacy bar. This document is **reference material only** —
do not import deception tactics into #43 ES1 contract.

**Reconciliation:** `#79 GeoVelocityAgent` (geo velocity), `#76 GeoIntelAgent` (Layer 0 brief).

**Authoritative lane map:** `mmi/project_brain/architecture/geo_context_43_research_lanes.md`
