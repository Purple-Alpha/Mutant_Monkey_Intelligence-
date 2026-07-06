# Claude Handoff — Iceberg Layer 9 Provenance Chain Depth (A)

**Task id:** `mmi-iceberg-l9-provenance-chain-depth-spec`  
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
TASK ID: mmi-iceberg-l9-provenance-chain-depth-spec
ASSIGNEE: Claude (Design)
SCORE: 85
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
  - chaos/graph_topology_layer.py — L6, verify_transition_edge(metadata) — single-hop graph
  - chaos/behavioral_fingerprint_layer.py — L4, analyze_fingerprint(...)
  - chaos/cross_packet_correlation_layer.py — L5, analyze_stream(..., arrival_ts_ms)
  - chaos/temporal_rhythm_layer.py — L7, analyze_rhythm(..., arrival_ts_ms)
  - chaos/metadata_ingress_gate.py — tip + L8/L6/L4/L5/L7 wired; L7 before nonce commit

Filed specs (match structure and tone):
  - architecture/MMI_ICEBERG_L4_BEHAVIORAL_FINGERPRINT_SPEC_2026-07.md
  - architecture/MMI_ICEBERG_L5_CROSS_PACKET_CORRELATION_SPEC_2026-07.md
  - architecture/MMI_ICEBERG_L7_TEMPORAL_RHYTHM_SPEC_2026-07.md

Doctrine:
  - architecture/MMI_METADATA_ICEBERG_2026-07.md (section 3 L9, section 6 non-goals)
  - architecture/MMI_DIFFERENTIATOR_2026-07.md
</current_state_inventory>

<existing_implementation_pattern>
L6 boundary (L9 must NOT duplicate — from graph_topology_layer.py):

- L6 validates ONE claimed hop: origin_lane → target_lane against DEFAULT_LEGAL_TRANSITIONS.
- L6 hard-drops illegal topology (TOPOLOGY_VIOLATION / ILLEGAL_LANE_TRANSITION).
- L9 tracks cumulative provenance chain depth from origin — content that originated in an
  untrusted lane cannot reach deep/privileged capabilities via downstream re-wrap.
- Depth is gate-derived and NOT re-assertable from sender metadata (attacker cannot reset depth).

L7 API + verdict shape (structural blueprint for L9 spec):

    def analyze_rhythm(
        self, sender_id, metadata, payload, arrival_ts_ms
    ) -> tuple[bool, dict[str, Any]]:
        # ok is ALWAYS True for L7 — never hard-drop
        # Warm-up -> RHYTHM_OK, mode=WARMUP_RECORD_ONLY, CONTINUE
        # Anomaly: RHYTHM_ANOMALY, MIRROR_DIMENSION, detail.reason=...

L5/L7 persistence pattern (L9 spec must reuse family):

    {"schema_version": N, "senders": {...}}  or chain-indexed store as appropriate
    # atomic JSON: tempfile + os.replace; NFKC identity normalize; no raw payload bytes
</existing_implementation_pattern>

<task_definition>
Write the complete markdown spec file:

  mmi/project_brain/architecture/MMI_ICEBERG_L9_PROVENANCE_CHAIN_DEPTH_SPEC_2026-07.md

Layer 9 — Provenance chain depth:
- Gate-derived hop-depth / origin-trust tracking per content lineage (or per sender-content binding — justify choice)
- Content from untrusted origin lanes cannot reach deep/privileged capabilities no matter how re-wrapped downstream
- Attacker cannot observe or reset gate-side chain state; packet claims of "depth=0" or "trusted origin" are ignored
- Cold start: record-only until minimum evidence — never hard-drop first contact
- Established anomaly: route MIRROR_DIMENSION — NOT hard-drop like CANARY_TRIPPED (match L4/L5/L7)
- API: propose analyze_chain(...) or equivalent -> tuple[bool, dict] matching depth-layer family
- Persistence: atomic JSON store (same family as L4/L5/L7)
- Integration: MetadataIngressGate.admit() AFTER L7, BEFORE nonce commit; mirror route skips nonce commit

Required spec sections (mirror L5/L7 spec layout):
  1. Operational Definition (+ signals / depth rules table)
  2. Boundary vs Adjacent Layers (L6 single-hop graph, L4/L5/L7, tip lineage fields, nonce store)
  3. Pass / Fail Lines (+ hard rules: ok always True for mirror-path layers, cold start sacred)
  4. Data Schema (persisted chain state — no payload bytes)
  5. Integration Sketch (gate order diagram)
  6. Falsifiable Test Scenarios T1-T3
  7. Non-Goals
  Footnotes for assumptions
  SIGN-OFF line: PASS | PASS WITH REVISIONS | FAIL
</task_definition>

<execution_constraints>
1. Deliver the complete markdown spec file only — no chat intro, no closeout prose.
2. Spec-only. No Python. No tasks.json edits. No build authorization.
3. Draw explicit boundary vs L6: single-hop legality is L6; cumulative depth / origin-trust is L9.
4. Input-trust rule: define which metadata fields L9 may read vs must ignore (prefer gate-derived only).
5. Three falsifiable T1-T3 scenarios with expected verdict + route.
6. MMI hard stops: no ML training, no raw payload logging, no unbounded self-modification.
</execution_constraints>
```

---

## MESSAGE 2 — Adversarial self-review (paste after MESSAGE 1 output)

```
<review_mode>
You just wrote MMI_ICEBERG_L9_PROVENANCE_CHAIN_DEPTH_SPEC_2026-07.md.

Adversarial self-review — assume a purple-team attacker with a leaked Ed25519 key and full packet-format knowledge. Find every gap that would let them:
- Reset or lie about provenance depth via metadata fields
- Reach SYSTEM_CORE or privileged capabilities from USER_INPUT origin via re-wrap chains
- Bypass cold-start protections
- Cause false positives on legitimate first-contact traffic
- Confuse L9 scope with L6 (single hop) or L5 (window counts) or L7 (inter-arrival)

Fix every finding inline. Output the COMPLETE revised spec file (not a diff). Update SIGN-OFF to PASS WITH REVISIONS if you changed anything material.
</review_mode>
```

---

## Closeout checklist (Cursor PM)

- [ ] Spec path: `architecture/MMI_ICEBERG_L9_PROVENANCE_CHAIN_DEPTH_SPEC_2026-07.md`
- [ ] SIGN-OFF: PASS or PASS WITH REVISIONS
- [ ] T1-T3 falsifiable scenarios present
- [ ] L6 boundary explicit (single-hop vs cumulative depth)
- [ ] Integration slot: after L7, before nonce commit
- [ ] `tasks.json` spec task → completed; build task remains pending until Matt `authorize build`
