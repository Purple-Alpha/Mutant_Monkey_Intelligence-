# Geo-Fence Manager

**Status:** `RESEARCH_DESIGN` | **Component:** Swarm Command Reality Controller  
**Objective:** Contextual deception and regional infrastructure tailoring.

> **Authority:** Research doctrine only. Not build authorization. See `README.md`.

---

## 1. Mission Statement

The `geo-fence-manager` serves as the primary "Reality Filter" for Swarm Command.
It ensures that every attacker is served a decoy environment that matches their
perceived origin, increasing the psychological cost of identifying the
infrastructure as a honeypot. It prevents "geographic leakage" — where an attacker
realizes they are being watched because the environment they are accessing does not
match the geographic context of the targeted business entity.

---

## 2. Operational Tactics

- **Regional Mirroring:** Based on the attacker's egress IP, the module dynamically
  modifies decoy portals, login screens, and local service headers to reflect the
  language, currency, and legal framework of that region (e.g., GDPR-compliant
  portals for EU-based attackers).
- **Latency Calibration:** Dynamically adjusts response times to match realistic
  cross-continental latency for the attacker's origin, preventing
  "too-fast-to-be-real" connectivity signals.
- **Geographic Tarpitting:** If an attacker attempts to access infrastructure from
  a high-risk or prohibited territory, the manager engages the `tarpit-orchestrator`
  to slow their connection to a crawl while simultaneously notifying the MMI project
  brain to increase the frequency of forensic logging.

---

## 3. Intelligence Outputs (The Data Stream)

When the manager processes an incoming request, it attaches a "Geo-Context Header"
to all internal traffic:

- **Attacker Origin Profile:** Real-time determination of country, ISP, and ASN.
- **Trust Score:** Assigns an automated score (0–100) based on the attacker's IP
  reputation, which dictates how "lenient" or "suspicious" the decoy environment
  should act.
- **Contextual Mismatch Alert:** Triggers if the attacker's IP origin is
  fundamentally inconsistent with the business's legitimate client base.

---

## 4. Stealth and Integrity Protocols

- **Dynamic Mapping:** Continuously updates Geo-IP databases to identify anonymization attempts (VPNs/TOR exit nodes).
- **Shadow-Serving:** Maintains multiple "regional personas" for the same service.
- **Invisible Filtering:** No rejection at the edge. Geo-filtering happens silently within Swarm Command infrastructure.

---

## 5. Integration Architecture

- **Input:** Raw incoming packet metadata from the edge load balancer.
- **Process:** `geo-fence-manager` performs a Geo-IP lookup and requests a Context
  Profile from the MMI project brain.
- **Output:** Updates the `network-mutator` with instructions on which regional
  "Decoy Persona" to serve to the attacker.

**Scoreboard link:** Related to `#43 Geo-Context` (held for more research per MMI-DEC-222).
