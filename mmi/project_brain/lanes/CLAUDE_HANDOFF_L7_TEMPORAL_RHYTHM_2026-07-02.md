# Claude Handoff — Iceberg Layer 7 Temporal Rhythm (A)

**Task id:** `mmi-iceberg-l7-temporal-rhythm-spec`  
**Assignee:** Claude (Design)  
**Build auth:** NOT_AUTHORIZED — **spec only**  
**Framework:** `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md`

**Two-message workflow (mandatory):**
1. Paste **MESSAGE 1** below into a fresh Claude window — generation pass.
2. After Claude returns the spec, paste **MESSAGE 2** — adversarial self-review pass.
3. Relay **final revised spec** to Cursor PM for closeout. Do not skip MESSAGE 2.

---

## MESSAGE 1 — Generate spec (paste this first)

```
PROJECT: MMI
TASK ID: mmi-iceberg-l7-temporal-rhythm-spec
ASSIGNEE: Claude (Design)
SCORE: 84
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec only, no implementation
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md

<system_role>
Lead Cybernetic Architect / Purple Team Engineer
Project: Mutant Monkey Intelligence (MMI) — systems-domain AGI matrix
Doctrine: Bounded autonomy, strict deterministic rules over soft prompts, un-fakeable metrics
Design lane only — deliver one bounded markdown spec. No implementation. No scope expansion.
</system_role>

<current_state_inventory>
Repo root: /mnt/c/MMI
Phase 1 weapon stack: PASS (tiers [4,4,4] — do not re-litigate)

Built depth layers:
  - chaos/canary_metadata_layer.py — L8, hard-drop, pre-signature
  - chaos/graph_topology_layer.py — L6, verify_transition_edge(metadata)
  - chaos/behavioral_fingerprint_layer.py — L4, analyze_fingerprint(...)
  - chaos/cross_packet_correlation_layer.py — L5, analyze_stream(..., arrival_ts_ms)
  - chaos/metadata_ingress_gate.py — tip + L8/L6/L4/L5 wired; L5 before nonce commit

Filed specs (match structure and tone):
  - architecture/MMI_ICEBERG_L4_BEHAVIORAL_FINGERPRINT_SPEC_2026-07.md
  - architecture/MMI_ICEBERG_L5_CROSS_PACKET_CORRELATION_SPEC_2026-07.md

Doctrine:
  - architecture/MMI_METADATA_ICEBERG_2026-07.md (section 3 L7, section 6 non-goals)
  - architecture/MMI_DIFFERENTIATOR_2026-07.md
</current_state_inventory>

<existing_implementation_pattern>
L5 boundary (L7 must NOT duplicate — from MMI_ICEBERG_L5_CROSS_PACKET_CORRELATION_SPEC_2026-07.md):

- L5 counts events inside a fixed 60s window (packet velocity, nonce velocity, lane diversity).
- L7 models spacing BETWEEN consecutive arrivals (inter-arrival interval baseline).
- L5 uses analyze_stream(sender_id, metadata, payload, arrival_ts_ms).
- L5 anomaly: ok=True always; verdict=STREAM_ANOMALY; route=MIRROR_DIMENSION; detail dict.

L5 API + verdict shape (structural blueprint for L7 spec):

    def analyze_stream(
        self, sender_id, metadata, payload, arrival_ts_ms
    ) -> tuple[bool, dict[str, Any]]:
        # ok is ALWAYS True for L5 — never hard-drop
        # Warm-up: lifetime_packets < 10 -> STREAM_OK, mode=WARMUP_RECORD_ONLY, CONTINUE
        # Breach: STREAM_ANOMALY, MIRROR_DIMENSION, detail.reason=...

L4 interval statistics pattern (use for L7 inter-arrival mean/stdev in spec):

    # Welch running mean/m2 per sender — O(senders) not O(packets)
    # Anomaly: mean +/- K*stdev (default K=4) on established baseline
    # Cold start: record-only until N intervals (propose N in spec)

L5 persistence pattern (L7 spec must reuse):

    {"schema_version": 1, "senders": {"<sender_id>": {...}}}
    # atomic JSON: tempfile + os.replace; NFKC identity normalize; no raw payload bytes
</existing_implementation_pattern>

<task_definition>
Write the complete markdown spec file:

  mmi/project_brain/architecture/MMI_ICEBERG_L7_TEMPORAL_RHYTHM_SPEC_2026-07.md

Layer 7 — Temporal rhythm:
- Inter-arrival timing baseline per sender (human/agent cadence vs machine-cadence replay or throttled exfiltration)
- Derived ONLY from gate-supplied arrival_ts_ms deltas between consecutive observations per sender
- Attacker cannot observe gate-side rhythm state
- Cold start: record-only until minimum interval sample count — never hard-drop first contact
- Established anomaly: route MIRROR_DIMENSION — NOT hard-drop like CANARY_TRIPPED
- API: analyze_rhythm(sender_id, metadata, payload, arrival_ts_ms) -> tuple[bool, dict]
- Persistence: atomic JSON store (same family as L4/L5)
- Integration: MetadataIngressGate.admit() AFTER L5, BEFORE nonce commit; mirror route skips nonce commit (same as L5)

Required spec sections (mirror L5 spec layout):
  1. Operational Definition (+ signals table)
  2. Boundary vs Adjacent Layers (L4, L5, L9, nonce store)
  3. Pass / Fail Lines (+ hard rules: ok always True, cold start sacred, deterministic ceilings)
  4. Data Schema (persisted rhythm state — no payload bytes)
  5. Integration Sketch (gate order diagram)
  6. Falsifiable Test Scenarios T1-T3
  7. Non-Goals
  Footnotes for assumptions
  SIGN-OFF line: PASS | PASS WITH REVISIONS | FAIL
</task_definition>

<execution_constraints>
1. Deliver the complete markdown spec file only — no chat intro, no closeout prose.
2. No conversational filler, summaries, or post-processing text outside the spec.
3. Deterministic rules only — no ML, no probabilistic soft scoring, no learned models.
4. Never trust attacker-controlled metadata for arrival_ts_ms — gate-supplied clock only.
5. Draw explicit boundary vs L5: no fixed-window velocity ceilings in L7 (that is L5's job).
6. Include 3 falsifiable tests: cold start, normal cadence match, machine-cadence anomaly.
7. MMI hard stops: no L9 chain depth, no unbounded self-modification, no fake pass paths.
</execution_constraints>

<no_explanations_directive>
Respond with the production-grade source code file payload only. Do not provide introductory remarks. Do not provide conversational closeouts or post-code explanations. If there are edge cases or structural assumptions, document them strictly inside native code comments within the file script itself.

DESIGN-LANE ADAPTATION: This task is architecture-only. Respond with the complete markdown spec file contents only — same no-filler rule. Assumptions go in spec footnotes [^n], not chat prose.
</no_explanations_directive>
```

---

## MESSAGE 2 — Self-review / takedown (paste after MESSAGE 1 output)

```
<review_mode>
You just wrote MMI_ICEBERG_L7_TEMPORAL_RHYTHM_SPEC_2026-07.md.

Act as a hostile, professional adversarial penetration tester reviewing your own spec.
Separate generation from critique — this is the mandatory self-correction pass before Matt/Cursor PM closeout.

Hunt for:
- Scope bleed into L5 (fixed-window counts, velocity ceilings, lane diversity — those belong to L5 only)
- Scope bleed into L4 (per-packet fingerprint signals)
- Packet-trust violations (arrival_ts_ms or intervals derived from attacker metadata)
- Cold-start gaps (flagging before sufficient interval samples)
- Fake-pass paths (verdicts that hard-drop like L8; ok=False on established paths; silent drops)
- Missing falsification criteria in T1-T3 (no numbers, no FAIL conditions)
- Nonce commit ordering errors (L7 must run before nonce commit; mirror must not burn nonce)
- Unicode/identity spray gaps (sender_id normalization not specified)
- Persistence bloat (O(packets) store instead of O(senders) aggregate)
- Doctrine conflicts with MMI_METADATA_ICEBERG_2026-07.md section 6 non-goals

Return the COMPLETE revised spec markdown file only — not a diff, not prose commentary.
Apply all fixes inline. Update SIGN-OFF to PASS only if every item above is clean; else PASS WITH REVISIONS with fixes applied.

<no_explanations_directive>
Respond with the production-grade file payload only. No introductory remarks. No conversational closeouts. Assumptions stay in footnotes.
</no_explanations_directive>
</review_mode>
```

---

## PM closeout checklist

After MESSAGE 2:
- [ ] Spec path: `architecture/MMI_ICEBERG_L7_TEMPORAL_RHYTHM_SPEC_2026-07.md`
- [ ] SIGN-OFF: PASS or PASS WITH REVISIONS (not FAIL without Matt decision)
- [ ] L5 boundary section present and non-overlapping
- [ ] T1-T3 have numeric pass/fail lines
- [ ] Relay to Cursor PM — build task stays blocked until Matt `authorize build`
