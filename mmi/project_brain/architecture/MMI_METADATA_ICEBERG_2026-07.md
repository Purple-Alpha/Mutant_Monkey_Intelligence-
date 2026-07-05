# MMI Metadata Iceberg — Layered Ingress Defense

**Status:** DESIGN + BUILT — tip + L4/L5/L6/L7/L8/L9 depth built
**Authority:** Matt (Super)
**Date filed:** 2026-07-01
**Purpose:** Extend the three-stream ingress envelope into a layered "iceberg" so that a perfectly-forged packet still fails against metadata the attacker cannot see.

**Related:**

* `chaos/metadata_ingress_gate.py` — tip (streams 1–3) + L6/L8 integration *(exists)*
* `chaos/canary_metadata_layer.py` — Layer 8 honeytoken canary *(exists)*
* `chaos/graph_topology_layer.py` — Layer 6 lane-transition graph *(exists)*
* `chaos/behavioral_fingerprint_layer.py` — Layer 4 behavioral fingerprint *(exists)*
* `chaos/cross_packet_correlation_layer.py` — Layer 5 stream correlation *(exists)*
* `chaos/temporal_rhythm_layer.py` — Layer 7 temporal rhythm *(exists)*
* `chaos/provenance_chain_depth_layer.py` — Layer 9 provenance chain depth *(exists)*
* `tests/test_cross_packet_correlation_layer.py` — L5 T1-T3 *(exists)*
* `tests/test_temporal_rhythm_layer.py` — L7 T1-T3 *(exists)*
* `tests/test_provenance_chain_depth_layer.py` — L9 T1-T3 *(exists)*
* `architecture/MMI_AGI_EVOLUTION_PATHWAY.md` — where verifiable provenance feeds FGI-SD
* `chaos/action_integrity_gate.py`, `chaos/mmi_control_envelope.py` — downstream gates

---

## 1. The core idea

Every "metadata security envelope" a normal system ships is **fully visible to whoever holds a packet.** An attacker who reverse-engineers the format can produce an envelope that looks flawless — correct fields, correct structure, even a valid signature if a key leaks. That envelope is the **tip of the iceberg.**

The MMI insight: the gate should judge a packet mostly on metadata the sender **never provides and cannot see** — metadata the gate *derives* from the sender's own history and the swarm's topology. You can't forge what you can't observe. That derived mass is the **90% below the waterline.**

```text
────────  WATERLINE — everything an attacker can forge  ────────
   TIP (signed, sent on the packet):  provenance · lineage · volumetric
────────────────────────────────────────────────────────────────
   DEPTH (derived by the gate, never sent):
     behavioral fingerprint · cross-packet correlation ·
     lane-transition graph · temporal rhythm ·
     honeytoken canary · provenance chain depth
```

## 2. Above the waterline — the TIP *(BUILT)*

Streams 1–3, enforced today in `metadata_ingress_gate.py`:

| # | Stream | Enforced check |
|---|--------|----------------|
| 1 | Provenance | Ed25519 per-agent signature, monotonic persisted nonce, ms timestamp window |
| 2 | Lineage | origin lane / clearance / capability checked against the policy table |
| 3 | Volumetric | true UTF-8 byte cap, key count, whitespace ratio, entropy |

This is real and tested. It already drops forged signatures, replays, tampered payloads, lane violations, and padding bombs. But every one of these fields **travels on the packet** — so it defines the ceiling of what a sophisticated attacker could imitate. That is exactly why it is only the tip.

## 3. Below the waterline — the DEPTH *(PARTIAL — L6 + L8 built)*

Each layer is **derived gate-side from state the sender has no access to.** None of it is trusted from the packet; all of it is computed from history after the tip passes.

**Layer 4 — Behavioral fingerprint.** *(BUILT — `behavioral_fingerprint_layer.py`)* A rolling per-sender profile: typical payload size, key-shape, capability mix. A packet that is individually valid but *unlike everything agent_01 has ever sent* is flagged. The attacker doesn't know agent_01's baseline; the gate does.

**Layer 5 — Cross-packet correlation.** *(BUILT — `cross_packet_correlation_layer.py`)* Judged over the *stream*, not one packet: nonce velocity, arrival bursts, sudden lane diversity. Replay and injection campaigns show up as stream anomalies even when each packet is clean.

**Layer 6 — Lane-transition graph.** *(BUILT — `graph_topology_layer.py`)* The swarm topology is a directed graph of legal hops. A packet claiming a hop that isn't an edge (e.g. `USER_INPUT → SYSTEM_CORE`) is rejected even if lane policy on its own would pass — the *transition* is illegal, not just the capability.

**Layer 7 — Temporal rhythm.** *(BUILT — `temporal_rhythm_layer.py`)* Inter-arrival timing baseline per sender. Machine-cadence replay or throttled exfiltration deviates from the human/agent rhythm the gate has learned.

**Layer 8 — Honeytoken canary.** *(BUILT — `canary_metadata_layer.py`)* Decoy metadata fields and phantom lanes seeded into the system. Any packet that references or acts on a canary is, by definition, sourced from someone who scraped internal structure — an instant known-hostile signal with near-zero false positives.

**Layer 9 — Provenance chain depth.** *(BUILT — `provenance_chain_depth_layer.py`)* Data carries how many hops it has taken from its origin. Content that originated in an untrusted lane cannot reach deep/privileged capabilities no matter how it is re-wrapped downstream — depth is tracked, not re-assertable.

## 4. Why depth beats a leaked key

The tip's worst case is a leaked Ed25519 key: the attacker can now sign. **The depth layers still catch them** — the signed packet won't match agent_01's fingerprint (L4), will disturb stream correlation (L5), may claim an illegal transition (L6), will break rhythm (L7), and can trip a canary (L8). Defense-in-depth means a single-point compromise at the tip does not equal a breach.

## 5. Build order

1. **Tip — done.** Streams 1–3 enforced + tested.
2. **L8 Honeytoken canary — done.** `canary_metadata_layer.py`, wired pre-signature.
3. **L6 Lane-transition graph — done.** `graph_topology_layer.py`, wired post-signature.
4. **L4 Behavioral fingerprint — done.** `behavioral_fingerprint_layer.py`, wired post-L6.
5. **L5 correlation — done.** `cross_packet_correlation_layer.py`, wired after L4.
6. **L7 rhythm — done.** `temporal_rhythm_layer.py`, wired after L5 before nonce commit.
7. **L9 chain depth — done.** `provenance_chain_depth_layer.py`, wired after L7 before nonce commit.

Each depth layer returns the same `(ok, {"error": CODE})` shape as the tip, so they chain into `MetadataIngressGate.admit()` as additional post-signature checks without changing the interface.

## 6. Non-Goals

* Depth layers **never trust a value from the packet** — if the sender can set it, it belongs in the tip, not the depth.
* No behavioral layer blocks on a cold start — every derived layer must degrade to "record-only" until it has a baseline, or it will drop legitimate first-contact traffic.
* This is anomaly *flagging into the Mirror Dimension*, not silent dropping, for layers 4/5/7 — a fingerprint miss routes for inspection; it does not hard-drop like a signature failure.
