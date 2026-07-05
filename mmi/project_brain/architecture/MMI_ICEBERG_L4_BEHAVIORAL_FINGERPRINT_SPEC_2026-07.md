# MMI Iceberg Layer 4 — Behavioral Fingerprint Spec

**Status:** BUILT — wired in metadata_ingress_gate (NOT full Mirror router)
**Authority:** Matt (Super)
**Date filed:** 2026-07-01
**Purpose:** Specify the gate-side per-sender behavioral fingerprint (Iceberg Layer 4). Derived-only, cold-start-safe, routes anomalies to the Mirror Dimension — never hard-drops first contact.

**Related:**

* `chaos/metadata_ingress_gate.py` — tip + L6/L8; L4 wires post-signature, after L6
* `chaos/graph_topology_layer.py` — L6, the check L4 runs after
* `chaos/canary_metadata_layer.py` — L8, the hard-drop contrast case
* `architecture/MMI_METADATA_ICEBERG_2026-07.md` — §3 (L4), §6 (non-goals)

---

## 1. Operational definition

L4 builds a rolling per-sender profile from **already-trusted** metadata (post-signature) and compares each new packet to that sender's own history. It answers one question: *is this packet unlike everything `sender_id` has ever sent?*

Derived signals (all from signed metadata + verified payload — never from unsigned fields):

* `payload_byte_size` — from signed `volumetric.payload_byte_size`
* `payload_key_count` — from signed `volumetric.payload_key_count`
* `target_capability` — from signed `lineage.target_capability`; tracked as a per-sender frequency map (the "capability mix")

L4 runs **only after the tip signature verifies and L6 passes.** By that point every input signal is authenticated, so the fingerprint cannot be poisoned by a forged field.

## 2. Verdict model

| Condition | Verdict | Action |
|-----------|---------|--------|
| Sender has `< N` accepted packets | **COLD_START** | Record signals, return ok. Never flag. |
| Established sender, packet within baseline | **MATCH** | Update baseline, return ok. |
| Established sender, packet outside baseline | **ANOMALY** | Route to Mirror Dimension for inspection. Do **not** hard-drop. |

This is the deliberate contrast with L8 `CANARY_TRIPPED` (instant hard-drop). A fingerprint miss is *suspicion*, not *proof* — a legitimate agent can legitimately do something new. Hard-dropping it would break the swarm; routing it inspects it.

`N` (cold-start threshold) default: **20** accepted packets per sender.

### Anomaly rule (per-signal, established baseline)

For numeric signals (`payload_byte_size`, `payload_key_count`), maintain a running mean and variance per sender. A signal is out-of-band when it exceeds **`mean ± K·stdev`** (default `K = 4`). For `target_capability`, out-of-band = a capability with observed frequency **below `min_capability_freq`** (default `0.02`) for that sender. A packet is **ANOMALY** if **≥ 1** signal is out-of-band; the returned `detail` names which.

## 3. Persistence schema

Atomic JSON store, same pattern as `_NonceStore` in `metadata_ingress_gate.py` (tempfile + `os.replace`, mkdir parents, tolerant load on corrupt/missing). One record per sender:

```json
{
  "agent_01": {
    "count": 142,
    "byte_size": {"mean": 512.4, "m2": 88213.0},
    "key_count": {"mean": 6.1, "m2": 40.2},
    "capability_mix": {"READ_ONLY": 130, "WRITE": 12}
  }
}
```

`mean`/`m2` are Welch running-moments (stdev derived as `sqrt(m2 / count)`), so the store never grows with packet volume — it is O(senders), not O(packets). Non-Goal: retaining raw payloads or a packet log.

## 4. API

```
analyze_fingerprint(sender_id: str, metadata: dict, payload: dict) -> tuple[bool, dict]
```

* Returns `(True, {...})` on COLD_START and MATCH.
* Returns `(True, {"verdict": "ANOMALY", "route": "MIRROR_DIMENSION", "detail": "..."})` on anomaly — **`ok` stays True** because L4 does not drop; the gate reads `route` to divert.
* Uses the key **`detail`** (singular), matching gate convention.
* Commits the updated baseline only after the verdict is computed (COLD_START and MATCH update; ANOMALY records the observation but is flagged for inspection).

Return dict always carries: `verdict` (`COLD_START|MATCH|ANOMALY`), `detail`, and — when applicable — `route`.

## 5. Integration slot

In `admit()`, post-signature, **after L6** (`verify_transition_edge`) and after volumetric/lane checks. Because L4 does not hard-drop, it does not raise `EnvelopeRejected`; instead the gate inspects the returned dict:

```
# ... tip verified, L6 passed ...
ok4, fp = self._fingerprint.analyze_fingerprint(sender_id, metadata, payload)
if fp.get("route") == "MIRROR_DIMENSION":
    # divert for inspection; packet is NOT admitted to the live lane
    return self._divert_to_mirror(payload, reason=fp["detail"])
# else: admit normally
```

L4 is the last derived check before admission, so a packet reaches it only if authenticated, lane-legal, and canary-clean.

## 6. Falsifiable test scenarios

**T1 — Cold start never flags.** Register a fresh sender. Send `N-1` wildly varying valid packets (tiny → large byte sizes, mixed capabilities). Expect: every verdict `COLD_START`, every `ok = True`, zero `MIRROR_DIMENSION` routes. *Falsified if any cold-start packet is flagged or dropped.*

**T2 — Established baseline catches the outlier.** Feed `≥ N` packets of a stable shape (e.g. ~500B, `READ_ONLY`). Then send one packet at 50× the byte-size mean. Expect: verdict `ANOMALY`, `route = "MIRROR_DIMENSION"`, `detail` names `payload_byte_size`, and `ok = True` (not a hard-drop). *Falsified if it hard-drops, or if the outlier is scored MATCH.*

**T3 — Capability novelty routes, doesn't drop.** Train a sender whose mix is 100% `READ_ONLY`. Send a valid, lane-legal `WRITE`-capability packet. Expect: verdict `ANOMALY` on `target_capability`, routed to Mirror, `ok = True`; the *lane policy* (tip) must have already permitted it, proving L4 flags novelty **without** overriding a legitimate authorization. *Falsified if L4 rejects a lane-legal packet as if it were unauthorized, or fails to flag the novel capability.*

## 7. Non-Goals

* **Not L5/L7/L9.** No cross-packet/stream correlation, no inter-arrival timing, no provenance chain depth — L4 judges one packet against one sender's own aggregate baseline only.
* **No implementation code in this spec.** Design lane only.
* **No hard-drop.** L4 never returns a drop; its worst action is diversion to the Mirror Dimension.
* **No unbounded execution or learning.** Fixed O(senders) moment store; no raw payload retention, no packet log, no model training loop.
* **No trust of unsigned fields.** Every signal is read post-signature from bound metadata/payload.

---

## Sign-off

**Verdict: PASS**

Scope matches the L4 slot: derived-only signals from signed metadata, atomic `_NonceStore`-pattern persistence, cold-start record-only, Mirror-Dimension routing (not hard-drop), `analyze_fingerprint(sender_id, metadata, payload) -> (ok, dict)` with `detail`, integration post-signature after L6, and three falsifiable scenarios. No scope bleed into L5/L7/L9 or implementation code.

*PASS | PASS WITH REVISIONS | FAIL*
