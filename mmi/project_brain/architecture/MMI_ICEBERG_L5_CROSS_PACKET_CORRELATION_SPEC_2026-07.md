# MMI Iceberg L5 — Cross-Packet Correlation Spec (2026-07)

**File target:** `mmi/project_brain/architecture/MMI_ICEBERG_L5_CROSS_PACKET_CORRELATION_SPEC_2026-07.md`
**Module target:** `chaos/cross_packet_correlation_layer.py`
**Doctrine:** MMI_METADATA_ICEBERG_2026-07 — bounded autonomy, deterministic rules, un-fakeable metrics.
**Status:** BUILT — wired in metadata_ingress_gate (post-L4, pre-nonce commit)

---

## 1. Operational Definition

L5 judges the **stream**, not the packet. A packet that is individually clean (valid signature,
clean L8/L6/L4 verdicts) can still belong to a hostile *campaign*: replay floods, injection
bursts, lane-hopping distribution. L5 detects these by correlating per-sender arrival state
across a rolling window that only the gate can see.

Core asymmetry: **the attacker cannot observe gate-side stream state.** All window counters,
prune boundaries, and warm-up progress live server-side. An attacker tuning a campaign is
shooting at thresholds they cannot measure; the gate's verdicts leak no window internals. [^1]

### Signals (all deterministic, all per `sender_id`)

| Signal | Definition | Ceiling |
|---|---|---|
| Packet velocity | Packets observed in rolling window | 120 / window |
| Nonce velocity | Distinct nonces observed in rolling window | 120 / window |
| Lane diversity | Distinct `origin_lane` values in rolling window | 3 / window |

Window: **60,000 ms**, half-open interval `(now − 60000, now]` — an entry exactly 60,000 ms
old is outside. Pruned on every call.

---

## 2. Boundary vs Adjacent Layers

- **L4 (behavioral fingerprint):** per-packet question — *does this packet look like this
  sender?* L5 never inspects packet internals or fingerprint distance. If a check needs only
  one packet to answer, it is L4's, not L5's.
- **L7 (temporal cadence):** rhythm question — *inter-arrival interval distributions, cadence
  baselines, jitter profiles.* L5 counts events inside a fixed window; it never models
  spacing *between* events. Any statistic over inter-arrival deltas is L7 and is out of scope.
- **Nonce store:** duplicate-nonce rejection (exact replay of a single nonce) remains the
  nonce commit step's job. L5 measures nonce *rate*, not nonce *uniqueness*.

---

## 3. Pass / Fail Lines

| Condition | Verdict | Route |
|---|---|---|
| Lifetime packets for sender < 10 (warm-up) | `STREAM_OK`, `mode=WARMUP_RECORD_ONLY` | `CONTINUE` — record, never flag, never drop |
| Window counts all ≤ ceilings | `STREAM_OK` | `CONTINUE` |
| Any ceiling exceeded (121st packet, 121st nonce, 4th lane) | `STREAM_ANOMALY` | `MIRROR_DIMENSION` |
| Malformed `sender_id` / metadata | `STREAM_ANOMALY`, `reason=MALFORMED_*` | `MIRROR_DIMENSION` |

Hard rules:

1. **`ok` is always `True`.** L5 never hard-drops. Anomalies route to Mirror Dimension for
   inspection — this is explicitly NOT the L8 `CANARY_TRIPPED` kill path.
2. **Cold start is sacred.** First contact is record-only until 10 lifetime packets exist.
   A sender must never be flagged on insufficient evidence.
3. **Ceilings are ceilings.** 120 packets in-window is legal; the 121st breaches. 3 lanes
   legal; the 4th breaches. No soft scoring, no probabilistic verdicts.

### Return API (identical shape to L4/L6)

```python
analyze_stream(sender_id, metadata, payload, arrival_ts_ms) -> tuple[bool, dict[str, Any]]

# Anomaly shape (matches L4 pattern):
(True, {
  "verdict": "STREAM_ANOMALY",
  "route":   "MIRROR_DIMENSION",
  "detail":  {"reason": "VELOCITY_CEILING_EXCEEDED", "window_packet_count": 121,
              "window_lanes": [...], "window_ms": 60000, "observed_ts_ms": ...}
})
```

`arrival_ts_ms` is the gate sequencer's clock — authoritative and gate-supplied, never taken
from attacker-controlled metadata fields. [^2]

---

## 4. Data Schema (persisted stream state)

Reuse the atomic JSON store pattern from `behavioral_fingerprint_layer.py` / `_NonceStore`
(write-temp → fsync → atomic rename). One document, keyed by normalized `sender_id`:

```json
{
  "schema_version": 1,
  "senders": {
    "<sender_id>": {
      "lifetime_packets": 37,
      "window": [
        {"ts_ms": 1751406000123, "lane": "LANE_A", "nonce_h": "sha256:ab12…"}
      ]
    }
  }
}
```

Rules: window entries pruned before persist (store never grows past ceilings + 1 per sender);
`nonce_h` is a hash, never the raw nonce; sender table capped with idle-sweep eviction;
`sender_id` and `lane` NFKC-normalized and length-capped before keying. No payload bytes,
ever (see non-goals).

---

## 5. Integration Sketch

`MetadataIngressGate.admit()` order — L5 slots **post-signature, after L4, before nonce commit**:

```
L8 canary (pre-signature, hard-drop)
  → signature verify
  → L6 verify_transition_edge(metadata)
  → L4 analyze_fingerprint(sender_id, metadata, payload)
  → L5 analyze_stream(sender_id, metadata, payload, arrival_ts_ms)   # ← new
  → nonce commit
```

Rationale: L5 must see only signature-valid traffic (otherwise floods of garbage inflate
windows), and must run *before* nonce commit so a Mirror-routed packet's nonce is not burned
into the committed set. On `route=MIRROR_DIMENSION`, `admit()` forwards packet + `detail`
to the Mirror inspection queue and skips nonce commit; the caller sees an admit result
consistent with normal flow (no state leak to sender).

---

## 6. Falsifiable Test Scenarios

**T1 — Cold start (falsifies warm-up rule if it fails):**
Fresh sender, 9 packets in 5 s across 4 lanes (would breach lane ceiling if evaluated).
Expected: all 9 return `STREAM_OK` / `WARMUP_RECORD_ONLY`. Any anomaly verdict before
packet 10 = FAIL.

**T2 — Normal stream (falsifies false-positive bound):**
Established sender (≥10 lifetime), 100 packets over 60 s, 2 lanes, unique nonces.
Expected: 100× `STREAM_OK`, zero Mirror routes. Any anomaly = FAIL.

**T3 — Burst / replay campaign (falsifies detection claim):**
Established sender replays 121 individually-valid packets inside one window, then hops to a
4th lane. Expected: packet 121 → `STREAM_ANOMALY` (`VELOCITY_CEILING_EXCEEDED`), lane hop →
`STREAM_ANOMALY` (`LANE_DIVERSITY_EXCEEDED`), both `route=MIRROR_DIMENSION`, both `ok=True`
(no hard-drop). Missed detection, or any hard-drop, = FAIL. Additionally: after a 61 s quiet
gap, the same sender must return to `STREAM_OK` (window actually rolls) — a latched-forever
flag = FAIL.

---

## 7. Non-Goals

- **No L7 inter-arrival rhythm baseline.** Cadence/jitter modeling is L7. L5 counts, L7 times.
- **No L9 provenance chain depth.** Origin lineage analysis belongs to L9.
- **No ML training.** All thresholds are fixed constants; no learned models, no drift.
- **No raw payload logging.** L5 persists timestamps, lane labels, and nonce hashes only.
- **No hard-drop authority.** Kill decisions remain with L8. L5 routes; it does not execute.
- **No per-packet fingerprinting.** That is L4; L5 does not duplicate it.

---

[^1]: Assumption: Mirror Dimension routing is externally indistinguishable from normal admit
      latency within jitter tolerance; if inspection adds measurable delay, the no-observability
      claim weakens and must be re-validated at integration.
[^2]: Assumption: gate sequencer clock is monotonic per process. If `arrival_ts_ms` can ever be
      derived from sender metadata, the future-skew clamp and per-sender monotonic clamp from
      the L5 hardening review become mandatory, not optional.

---

**SIGN-OFF:** PASS
