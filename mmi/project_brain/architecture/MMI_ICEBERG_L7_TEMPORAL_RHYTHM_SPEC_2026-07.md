# MMI Iceberg L7 — Temporal Rhythm Spec (2026-07)

**File target:** `mmi/project_brain/architecture/MMI_ICEBERG_L7_TEMPORAL_RHYTHM_SPEC_2026-07.md`
**Module target:** `chaos/temporal_rhythm_layer.py`
**Doctrine:** MMI_METADATA_ICEBERG_2026-07 §3 (L7), §6 (non-goals) — bounded autonomy, deterministic rules, un-fakeable metrics.
**Status:** BUILT (REV A spec). BUILD AUTHORIZATION: AUTHORIZED_BY_MATT_2026-07-02.
**Revision:** REV A — adversarial self-review applied (session-gap baseline exclusion, epoch roll anti-latch, identity/input-trust hard rules).

---

## 1. Operational Definition

L7 judges **spacing between consecutive arrivals**, per sender. L5 counts events inside a
fixed window; L7 models the *rhythm* of the gaps. Human- and agent-originated traffic
carries irregular cadence (think-time jitter, scheduler noise). Replay rigs and throttled
exfiltration loops carry machine cadence: intervals too regular, or intervals that violate
the sender's own established rhythm.

Core asymmetry: **the attacker cannot observe gate-side rhythm state.** Baseline mean,
variance, epoch position, and warm-up progress are server-side only; verdicts leak no
rhythm internals. [^1]

Input-trust rule (hard): the ONLY input L7 consumes is `arrival_ts_ms`, and it is
**gate-sequencer-supplied only** — never read from sender metadata. The `metadata` and
`payload` parameters exist solely for API uniformity with L4/L5/L6 and MUST be ignored by
L7 logic; any future revision that reads them is a packet-trust violation and voids this
spec. Interval `Δt = arrival_ts_ms − last_arrival_ts_ms` for the same normalized
`sender_id`. Non-positive `Δt` (gate clock anomaly, not sender behavior) is discarded:
baseline untouched, gate-health counter incremented, `CONTINUE`. [^2]

### Signals (all deterministic, all per `sender_id`, all over Δt only)

| Signal | Definition | Rule |
|---|---|---|
| Rhythm deviation | Δt vs sender's own baseline | anomaly if Δt < mean − K·stdev (K = 4) |
| Machine cadence | Regularity of established baseline | anomaly if CV = stdev / mean < 0.01 AND intervals ≥ warm-up |
| Session gap | Δt > 300,000 ms (5 min) | benign — resets interval chain; **silence is never anomalous** |

Baseline: Welford running mean / m2 per sender (L4 interval-statistics pattern) —
O(senders) memory, O(1) update, no stored interval history.

Baseline hygiene rules:

- **Session-gap intervals are excluded from the baseline.** A Δt above the session gap
  resets `last_arrival_ts_ms` but is NOT fed to Welford — otherwise one lunch break
  permanently inflates mean/stdev and widens the anomaly band (baseline contamination).
- Deviation test is **one-sided (too fast)**: abnormally slow arrival is handled by the
  session-gap reset, never flagged.
- stdev is clamped to a 5 ms floor for the deviation test only; the machine-cadence CV
  test uses the unclamped value — near-zero variance is exactly the signal. [^3]

### Constants (spec-fixed; changes require spec revision, not config edit)

| Constant | Value |
|---|---|
| K (deviation band) | 4 |
| CV floor (machine cadence) | 0.01 |
| Warm-up | 20 intervals (21 packets) |
| Session gap | 300,000 ms |
| stdev clamp (deviation test only) | 5 ms |
| Epoch length (baseline roll) | 512 intervals |
| MAX_SENDER_ID_LENGTH | 256 code points (post-NFKC) |
| MAX_TRACKED_SENDERS | 100,000 |
| IDLE_EVICT_MS | 86,400,000 ms (24 h) |

---

## 2. Boundary vs Adjacent Layers

- **L4 (behavioral fingerprint):** per-packet content-shape question. L7 never inspects
  metadata fields or payload structure; it consumes exactly one number per packet (Δt).
- **L5 (cross-packet correlation):** fixed-window event *counts* (packet velocity, nonce
  velocity, lane diversity). L7 defines **no fixed-window ceilings of any kind** — if a
  rule can be stated as "more than N events per window," it is L5's and is out of scope
  here. The session gap and epoch constants are chain/baseline lifecycle rules over Δt,
  not event-count windows. L7 owns only statistics over consecutive-arrival deltas.
- **L9 (provenance chain):** origin lineage and chain depth. Out of scope (MMI hard stop).
- **Nonce store:** exact-replay rejection of a duplicate nonce stays with nonce commit.
  L7 detects replay *cadence* (the rig's clock), not replay *content*.

---

## 3. Pass / Fail Lines

| Condition | Verdict | Route |
|---|---|---|
| First contact (no `last_arrival_ts_ms` for sender) | `RHYTHM_OK`, `mode=FIRST_CONTACT` | `CONTINUE` — record arrival, no interval exists yet |
| Intervals in current epoch < 20 (warm-up) | `RHYTHM_OK`, `mode=WARMUP_RECORD_ONLY` | `CONTINUE` — record, never flag, never drop |
| Δt > session gap (300,000 ms) | `RHYTHM_OK`, `mode=SESSION_RESET` | `CONTINUE` — chain resets, interval excluded from baseline |
| Non-positive Δt (gate clock anomaly) | `RHYTHM_OK`, `mode=CLOCK_DISCARD` | `CONTINUE` — baseline untouched, gate-health counter++ |
| Established baseline, Δt within band, CV ≥ 0.01 | `RHYTHM_OK` | `CONTINUE` |
| Δt < mean − 4·stdev on established baseline | `RHYTHM_ANOMALY`, `reason=RHYTHM_DEVIATION` | `MIRROR_DIMENSION` |
| CV < 0.01 on established baseline | `RHYTHM_ANOMALY`, `reason=MACHINE_CADENCE` | `MIRROR_DIMENSION` |
| Malformed / empty-after-normalization `sender_id`; non-dict metadata | `RHYTHM_ANOMALY`, `reason=MALFORMED_SENDER_ID` / `MALFORMED_METADATA` | `MIRROR_DIMENSION` |

Hard rules:

1. **`ok` is always `True`.** L7 never hard-drops. Anomalies route to Mirror Dimension —
   explicitly NOT the L8 `CANARY_TRIPPED` kill path. No fake pass paths: every Mirror
   route is recorded in `detail`; no verdict is silently converted to `RHYTHM_OK`; no
   packet is silently discarded (even `CLOCK_DISCARD` returns an explicit mode).
2. **Cold start is sacred.** Record-only until 20 intervals exist in the current epoch.
   First contact is never flagged on rhythm evidence.
3. **Identity discipline (inherited from L5 hardening, mandatory here).** `sender_id` is
   NFKC-normalized + casefolded + Cf-stripped and capped at 256 code points *before* any
   keying; empty-after-normalization is `MALFORMED_SENDER_ID` → Mirror. Sender table is
   capped at 100,000 with idle-sweep eviction (idle > 24 h); at saturation with no
   evictable senders, new senders route to Mirror with `reason=SENDER_TABLE_SATURATED` —
   loud, never silent.
4. **Epoch roll (anti-latch).** Every 512 intervals the Welford baseline resets and the
   sender re-enters 20-interval warm-up. Purpose: (a) a `MACHINE_CADENCE` flag cannot
   latch forever on accumulated statistics — a legitimately stable sender (heartbeat
   monitor) is re-evaluated on fresh evidence at most 512 intervals later; (b) baselines
   track current behavior, not ancient history. Accepted trade-off: an attacker gets a
   20-interval record-only blind spot per epoch — during which L5's window ceilings still
   apply in full, so the blind spot is rhythm-only, not coverage-loss. [^4]
5. **Deterministic ceilings only.** All constants per §1 table. No ML, no learned models,
   no soft scoring, no self-retuning.
6. **Silence is never anomalous.** Long gaps reset the chain; they never flag and never
   enter the baseline.

### Return API (identical shape to L4/L5/L6)

```python
analyze_rhythm(sender_id, metadata, payload, arrival_ts_ms) -> tuple[bool, dict[str, Any]]

# Anomaly shape (matches L5 pattern):
(True, {
  "verdict": "RHYTHM_ANOMALY",
  "route":   "MIRROR_DIMENSION",
  "detail":  {"reason": "MACHINE_CADENCE", "interval_count": 312, "epoch": 4,
              "baseline_mean_ms": 2000, "baseline_stdev_ms": 3,
              "observed_delta_ms": 2001, "k": 4, "cv_floor": 0.01}
})
```

---

## 4. Data Schema (persisted rhythm state)

Atomic JSON store, same family as L4/L5 (`tempfile` + `os.replace`; identity discipline
per §3 rule 3). Welford state only — **no interval history array, no payload bytes, no
raw nonces, no metadata fields**:

```json
{
  "schema_version": 2,
  "senders": {
    "<sender_id>": {
      "epoch": 4,
      "interval_count": 312,
      "last_arrival_ts_ms": 1751406000123,
      "mean_ms": 2000.4,
      "m2": 8812.7
    }
  }
}
```

Fixed size per sender (5 numbers) regardless of traffic volume — O(senders), never
O(packets); the store cannot be inflated by flooding a single identity, and identity
spray is bounded by the 100,000-sender cap + idle sweep.

---

## 5. Integration Sketch

`MetadataIngressGate.admit()` order — L7 slots **after L5, before nonce commit**:

```
L8 canary (pre-signature, hard-drop)
  → signature verify
  → L6 verify_transition_edge(metadata)
  → L4 analyze_fingerprint(sender_id, metadata, payload)
  → L5 analyze_stream(sender_id, metadata, payload, arrival_ts_ms)
  → L7 analyze_rhythm(sender_id, metadata, payload, arrival_ts_ms)   # ← new
  → nonce commit
```

Rationale: L7 must see only signature-valid, L5-screened traffic so garbage floods cannot
poison baselines, and must run *before* nonce commit so a Mirror-routed packet's nonce is
not burned (same rule as L5). On `route=MIRROR_DIMENSION`, `admit()` forwards packet +
`detail` to the Mirror inspection queue, skips nonce commit, and returns an admit result
externally indistinguishable from normal flow. L5 and L7 verdicts are independent; either
alone routes to Mirror. `arrival_ts_ms` is the same gate-sequencer value passed to L5 —
one clock, one reading, both layers. L7 state update (Welford + last-arrival) happens
even when the packet is Mirror-routed by L5: rhythm observation is about arrival, not
admission. [^2]

---

## 6. Falsifiable Test Scenarios

**T1 — Cold start (falsifies warm-up rule if it fails):**
Fresh sender emits 21 packets at perfectly metronomic 1000 ms spacing (would trip
`MACHINE_CADENCE` if evaluated). Expected: packet 1 → `FIRST_CONTACT`; packets 2–21
(intervals 1–20) → `RHYTHM_OK` / `WARMUP_RECORD_ONLY`. Any anomaly verdict before
interval 21, or any hard-drop, = FAIL.

**T2 — Normal cadence match + gap hygiene (falsifies false-positive bound AND
baseline-contamination fix):**
Established sender (≥20 intervals, baseline mean ≈ 2000 ms, stdev ≈ 400 ms) sends 200
packets with jittered spacing in [1200, 2800] ms, including one 20-minute gap mid-run.
Expected: 200× `RHYTHM_OK`; the gap returns `mode=SESSION_RESET`, not an anomaly; zero
Mirror routes; AND persisted `mean_ms` after the run remains in [1200, 2800] — proving
the 1,200,000 ms gap interval never entered Welford. Any flag, or contaminated mean,
= FAIL.

**T3 — Machine-cadence anomaly + recovery bound (falsifies detection claim AND anti-latch):**
Established sender is replaced by a replay rig sending at 2000 ± 1 ms (CV ≈ 0.0005).
Expected: once running CV crosses below 0.01 (at or after interval 21 of the epoch),
`RHYTHM_ANOMALY` / `reason=MACHINE_CADENCE` / `route=MIRROR_DIMENSION` / `ok=True`, and
no nonce committed for any Mirror-routed packet. Separately, a burst packet at
Δt = 5 ms → `RHYTHM_ANOMALY` / `reason=RHYTHM_DEVIATION`. Then: if the rig is replaced
by legitimate jittered traffic (CV ≥ 0.01), flags MUST cease within one epoch roll
(≤ 512 intervals + 20 warm-up). Missed detection, any hard-drop, any burned nonce on a
Mirror route, or a flag that persists past one epoch of clean traffic = FAIL.

---

## 7. Non-Goals

- **No fixed-window velocity or diversity ceilings.** Event counting per window is L5.
- **No L9 provenance chain depth.** MMI hard stop; origin lineage is not L7's question.
- **No ML training / learned models.** Welford statistics with fixed constants only.
- **No raw payload logging.** L7 persists five numbers per sender; nothing else.
- **No hard-drop authority.** Kill decisions remain with L8. L7 routes; it does not execute.
- **No cross-sender correlation.** Fleet-level rhythm clustering is a separate future spec.
- **No unbounded self-modification.** Constants are spec-fixed; the layer cannot retune itself.
- **No allowlisting inside L7.** Exempting known-benign metronomic senders (heartbeats) is
  gate-configuration policy, not layer logic — L7 reports; policy decides.

---

[^1]: Assumption: Mirror Dimension routing remains externally indistinguishable from normal
      admit latency within jitter tolerance (inherited from L5 spec assumption [^1]); if
      inspection adds measurable delay, an attacker gains a rhythm-state oracle and the
      no-observability claim must be re-validated.
[^2]: Assumption: gate sequencer clock is monotonic per process. Non-positive Δt therefore
      indicates gate restart or clock step, not sender behavior — the interval is discarded
      (`CLOCK_DISCARD`, baseline untouched) and a gate-health counter increments. If
      `arrival_ts_ms` is ever sourced from sender metadata, this spec is void and must be
      revised with the L5 hardening clamps (future-skew + per-sender monotonic) made mandatory.
[^3]: Boundary rule: the 5 ms stdev clamp prevents division-by-near-zero and instant-flag
      pathology in the deviation test; the CV test deliberately uses unclamped stdev. A
      baseline with mean < 10 ms is machine-range by definition but is judged by the same
      two rules — no special casing.
[^4]: Residual risks, accepted and documented: (a) an attacker who injects ≥1% coefficient
      of variation into their rig's timing evades the CV floor — L7 narrows the attacker's
      timing freedom, it does not eliminate replay (L5 ceilings and nonce commit remain the
      complementary controls); (b) legitimate metronomic automation (heartbeats, cron) will
      be Mirror-routed each epoch until gate policy exempts it — Mirror is inspection, not
      drop, so the cost is triage load, not availability; (c) the per-epoch 20-interval
      rhythm blind spot per §3 rule 4.

---

**SIGN-OFF:** PASS WITH REVISIONS — REV A applied; PM accepts for closeout. Codex build requires Matt `authorize build`.
