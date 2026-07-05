# MMI Iceberg L9 — Provenance Chain Depth Spec (2026-07) — REV A

**File target:** `mmi/project_brain/architecture/MMI_ICEBERG_L9_PROVENANCE_CHAIN_DEPTH_SPEC_2026-07.md`
**Module target:** `chaos/provenance_chain_depth_layer.py` (BUILT — this spec documents and constrains it)
**Doctrine:** MMI_METADATA_ICEBERG_2026-07 §3 (L9), §6 (non-goals) — bounded autonomy, deterministic rules, un-fakeable metrics.
**Status:** BUILT alignment spec. BUILD AUTHORIZATION: AUTHORIZED_BY_MATT_2026-07-02 (module pre-existed; spec is retroactive alignment).
**Threat model (this revision):** purple-team attacker holding a leaked Ed25519 signing key with full packet-format knowledge. Consequence: signature validity and signed identity prove NOTHING about origin trust — a valid signature is now assumed compromised. Every rule below that would rest on "the signature says so" is re-derived to rest on gate-observed facts instead.
**Revision:** REV A — fixes: (1) first-contact laundering hole in cold-start rule (§3), (2) signed-identity trust dependency → lane-derived + monotonic-decreasing trust (§1, §3), (3) content-hash severance made an explicit named residual with canonicalization mandate (§1, §7), (4) privileged-target determination pinned to gate routing, not packet claim (§1).

---

## 1. Operational Definition

L9 answers a lineage question no other layer asks: **where did this content originally come from, and how many hands has it passed through?** A payload that first entered the matrix through an untrusted origin lane must not reach deep/privileged capabilities later by being re-wrapped, re-signed, and re-sent by downstream senders — no matter how many individually-legal hops (L6-clean), well-fingerprinted packets (L4-clean), well-paced streams (L5/L7-clean) carry it. Under the leaked-key threat model, "re-signed by a trusted-looking identity" is the *expected* attacker move, not an edge case.

Core asymmetries:

- **The attacker cannot observe gate-side chain state.** Chain records, depth counters, and origin-trust live server-side only; verdicts leak no chain internals. [^1]
- **The attacker cannot reset lineage.** Origin lane and origin trust are bound at first gate observation of a content hash and only ever move toward *less* trust thereafter. Packet metadata claiming `depth=0`, `origin=trusted`, or any provenance assertion is ignored unread by L9 logic (input-trust rule).

### Mechanism

Content lineage is keyed by **SHA-256 of the canonical payload bytes** (gate serializer's canonical form [^2]). Per content hash the gate maintains:

- `first_origin_lane` — the gate-observed ingress lane at first observation. **Frozen.**
- `origin_trust` — trust class of the origin, **monotonic-decreasing**: initialized from the first observation's lane-trust, and *downgraded* (never upgraded) if the same content is ever later observed arriving from a less-trusted lane. Rationale in §3 rule 3. [^3]
- `max_depth` — increments by 1 whenever the current normalized `sender_id` differs from the immediately previous observation's sender for this content hash (the re-wrap signal).

**Trust and privilege are both gate-derived, never packet-derived.** `origin_trust` comes from the gate's lane-trust map applied to the *network-observed* ingress lane — not from the signed identity (leaked key ⇒ identity is worthless) and not from any claimed origin field. "Privileged target" is the capability/lane the **gate is about to route the packet to**, supplied by the gate as explicit routing parameters — never read from packet metadata inside L9.

### Signals / depth rules (all deterministic, all per content hash)

| Signal | Definition | Rule |
|---|---|---|
| Origin bind | First observation sets `first_origin_lane`, initial `origin_trust` | `first_origin_lane` frozen; `origin_trust` may only decrease |
| Trust downgrade | Same hash later seen from a less-trusted lane | `origin_trust` drops to the lower class immediately |
| Re-wrap depth | `max_depth` += 1 on sender change for same content hash | Tracked; reported in every verdict `detail` |
| Untrusted→privileged | `origin_trust=UNTRUSTED` AND gate routing to privileged capability/lane | `CHAIN_DEPTH_ANOMALY` → `MIRROR_DIMENSION`, **evaluated from observation 1** |
| Depth ceiling (optional, if built) | `max_depth` ≥ configured max re-wraps | `CHAIN_DEPTH_ANOMALY` → `MIRROR_DIMENSION`, evaluated after warm-up |

### Input-trust rule (hard)

L9 MAY read: `payload` bytes (solely to compute the canonical SHA-256 — never stored); gate-derived `sender_id` (normalized); gate-supplied `ingress_lane`, `routing_capability`, and `routing_target_lane` (post-signature, post-L6 routing state passed by `MetadataIngressGate.admit()`). L9 MUST ignore: `metadata` and every packet-asserted provenance field. Any revision that reads packet metadata inside L9 is a packet-trust violation and voids this spec.

### Constants (spec-fixed; changes require spec revision, not config edit)

| Constant | Value |
|---|---|
| MIN_CHAIN_OBSERVATIONS (depth-signal warm-up) | 2 |
| Content key | SHA-256 over canonical payload |
| MAX_TRACKED_CHAINS | 100,000 |
| IDLE_EVICT_MS | 86,400,000 ms (24 h) |
| MAX_SENDER_ID_LENGTH | 256 code points (post-NFKC) |

---

## 2. Boundary vs Adjacent Layers

- **L6 (graph topology):** validates ONE claimed hop — `origin_lane → target_lane` against `DEFAULT_LEGAL_TRANSITIONS` — and **hard-drops** illegal topology (`TOPOLOGY_VIOLATION`). L9 never re-checks single-hop legality. **L6 asks "is this step legal?"; L9 asks "is this journey legal?"**
- **L4 (behavioral fingerprint):** per-packet shape. L9 reads no metadata structure.
- **L5 (cross-packet correlation):** fixed-window event counts per sender. L9 counts nothing per window; its counters are per content-hash lineage, unbounded in time.
- **L7 (temporal rhythm):** inter-arrival deltas. L9 is timing-blind (idle eviction aside).
- **Tip lineage fields:** display/UX provenance at the tip is untrusted decoration; L9 neither reads nor validates it.
- **Nonce store:** duplicate-nonce rejection stays with nonce commit. Identical content legitimately re-sent under one sender does not increment depth and is not L9's concern.

---

## 3. Pass / Fail Lines

| Condition | Verdict | Route |
|---|---|---|
| `origin_trust=UNTRUSTED` AND gate routing to privileged capability/lane | `CHAIN_DEPTH_ANOMALY`, `reason=UNTRUSTED_ORIGIN_PRIVILEGED_TARGET` | `MIRROR_DIMENSION` — **fires from observation 1** |
| Depth-based signal (ceiling) with observations < 2 | `CHAIN_OK`, `mode=WARMUP_RECORD_ONLY` | `CONTINUE` — record origin/depth, no depth flag |
| Trusted origin, any depth, any target | `CHAIN_OK` | `CONTINUE` — depth reported in `detail` |
| Untrusted origin, non-privileged target | `CHAIN_OK` | `CONTINUE` — lineage watched, not blocked |
| Established chain, depth ceiling exceeded (if built) | `CHAIN_DEPTH_ANOMALY`, `reason=DEPTH_CEILING_EXCEEDED` | `MIRROR_DIMENSION` |
| Malformed / empty-after-normalization `sender_id`; unhashable payload | `CHAIN_DEPTH_ANOMALY`, `reason=MALFORMED_*` | `MIRROR_DIMENSION` |

Hard rules:

1. **`ok` is always `True`.** L9 is a mirror-path layer like L4/L5/L7 — never the L8 `CANARY_TRIPPED` kill path.
2. **Cold start is scoped to history-dependent signals only.** The untrusted-origin→privileged-target check fires from observation 1. Only depth-ceiling signals wait for `MIN_CHAIN_OBSERVATIONS`.
3. **Origin trust is monotonic-decreasing and lane-derived.** `first_origin_lane` freezes; `origin_trust` initializes from it and thereafter only drops via `min(origin_trust, observed_lane_trust)`.
4. **Origin frozen, depth only grows.** No path may overwrite `first_origin_lane`, raise `origin_trust`, or decrement `max_depth`.
5. **Identity discipline.** `sender_id` NFKC-normalized before depth comparison. Chain table capped at 100,000 with idle-sweep eviction.
6. **Deterministic rules only.** No ML, no learned trust scores.

### Return API

```python
analyze_chain(
    sender_id,
    metadata,
    payload,
    *,
    ingress_lane: str,
    routing_capability: str,
    routing_target_lane: str = "",
    arrival_ts_ms: int | None = None,
) -> tuple[bool, dict[str, Any]]
```

`metadata` exists for API uniformity; L9 MUST ignore it.

---

## 4. Data Schema (persisted chain state)

```json
{
  "schema_version": 1,
  "chains": {
    "sha256:<hex>": {
      "first_origin_lane": "USER_INPUT",
      "origin_trust": "UNTRUSTED",
      "max_depth": 3,
      "observations": 4,
      "last_sender_id": "<normalized>",
      "last_seen_ts_ms": 1751406000123
    }
  }
}
```

No raw payload bytes, ever.

---

## 5. Integration Sketch

```
L8 canary (pre-signature, hard-drop)
  → signature verify
  → L6 verify_transition_edge(metadata)
  → L4 analyze_fingerprint(...)
  → L5 analyze_stream(..., arrival_ts_ms)
  → L7 analyze_rhythm(..., arrival_ts_ms)
  → L9 analyze_chain(..., ingress_lane=..., routing_capability=..., routing_target_lane=...)
  → nonce commit
```

Gate error code: `CHAIN_DEPTH_ANOMALY`. Mirror route skips nonce commit.

---

## 6. Falsifiable Test Scenarios

**T1 — First-contact laundering:** New hash, ingress `USER_INPUT`, routing to privileged target on observation 1 → `CHAIN_DEPTH_ANOMALY` / `UNTRUSTED_ORIGIN_PRIVILEGED_TARGET` / `MIRROR_DIMENSION` / `ok=True`. Observation 1 returning `CHAIN_OK` = FAIL.

**T2 — Trusted lineage, deep re-wrap:** First ingress TRUSTED, 4 senders (3 sender changes), privileged target, never untrusted lane → all `CHAIN_OK`; `max_depth=3`.

**T3 — Leaked-key forgery + trust downgrade:** UNTRUSTED first ingress; re-wrap toward privileged with valid signature → Mirror; trust downgrade from later UNTRUSTED ingress observation on trusted-first chain.

---

## 7. Non-Goals

- No single-hop legality (L6).
- No content semantics / paraphrase detection.
- No ML training / learned trust.
- No raw payload logging.
- No hard-drop authority (L8 only).
- No cross-chain correlation.

### Named residual — content-hash severance

Lineage bound to canonical payload hash. Mitigation: canonicalization strips non-semantic variation; L4/L5/L7 compensate for genuine mutation.

---

[^1]: Mirror routing externally indistinguishable from normal admit (inherited L5/L7 assumption).
[^2]: Gate serializer canonical form is load-bearing; must have tests.
[^3]: Trust classes totally ordered; `origin_trust ← min(origin_trust, observed_lane_trust)`.
[^4]: If built code warms up untrusted→privileged check, that is a code defect.

---

**SIGN-OFF:** PASS WITH REVISIONS (REV A applied; code aligned in repo closeout).
