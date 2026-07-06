# Claude Handoff — Iceberg Layer 5 Cross-Packet Correlation (A)

**Task id:** `mmi-iceberg-l5-cross-packet-correlation-spec`  
**Assignee:** Claude (Design)  
**Build auth:** NOT_AUTHORIZED — **spec only**  
**Framework:** `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md`

Copy everything inside the fence below into a fresh Claude window.

---

```
<system_role>
Lead Cybernetic Architect — MMI Metadata Iceberg Design lane.
Deliver one bounded design spec. No implementation. No scope expansion.
</system_role>

<production_inventory>
Repo: /mnt/c/MMI
Phase 1 weapon stack: PASS (tiers [4,4,4] — do not re-litigate).

Existing depth layers (match these patterns):
- chaos/canary_metadata_layer.py — L8, hard-drop, pre-signature
- chaos/graph_topology_layer.py — L6, post-signature, verify_transition_edge(metadata)
- chaos/behavioral_fingerprint_layer.py — L4, post-L6, analyze_fingerprint(sender_id, metadata, payload)
- chaos/metadata_ingress_gate.py — tip + L8/L6/L4 wired in admit()

Iceberg doctrine: architecture/MMI_METADATA_ICEBERG_2026-07.md
L4 spec reference: architecture/MMI_ICEBERG_L4_BEHAVIORAL_FINGERPRINT_SPEC_2026-07.md
</production_inventory>

<target_objective>
Write: mmi/project_brain/architecture/MMI_ICEBERG_L5_CROSS_PACKET_CORRELATION_SPEC_2026-07.md

Layer 5 — Cross-packet correlation:
- Judged over the *stream*, not one packet: nonce velocity, arrival bursts, sudden origin_lane diversity
- Replay and injection campaigns show up as stream anomalies even when each packet is individually clean
- Attacker cannot observe gate-side stream state
- Cold start: record-only until minimum window exists per sender — never hard-drop first contact
- Anomaly on established window: route to Mirror Dimension for inspection — NOT hard-drop like CANARY_TRIPPED
- Return API: (ok: bool, dict with error/detail) identical to L4/L6
- Persistence: reuse atomic JSON store pattern from behavioral_fingerprint_layer.py / _NonceStore
- Integration: post-signature slot in MetadataIngressGate.admit() after L4, before nonce commit
</target_objective>

<execution_constraints>
1. Output the markdown spec file only — no chat intro or closeout.
2. Keep it short: operational definition, pass/fail lines, falsification criteria, data schema, integration sketch, non-goals.
3. Include 3 falsifiable test scenarios (cold start, normal stream, burst/replay anomaly).
4. Explicit non-goals: no L7 inter-arrival rhythm baseline (that is L7), no L9 provenance chain depth, no ML training, no raw payload logging.
5. Draw clear boundary vs L4 (per-packet fingerprint) and L7 (temporal cadence).
6. Sign-off line at end: PASS | PASS WITH REVISIONS | FAIL.
</execution_constraints>

<existing_implementation_pattern>
L4 method signature pattern:
  analyze_fingerprint(sender_id, metadata, payload) -> tuple[bool, dict[str, Any]]

L4 anomaly shape:
  ok=True, verdict=ANOMALY, route=MIRROR_DIMENSION, detail={...}

L5 proposed entry point (you may refine):
  analyze_stream(sender_id, metadata, payload, arrival_ts_ms) -> tuple[bool, dict[str, Any]]
</existing_implementation_pattern>

<no_explanations_directive>
Respond with the complete markdown spec file contents only. Assumptions in spec footnotes — not conversational prose.
</no_explanations_directive>
```

---

After Claude returns the spec, relay output path to Cursor PM for closeout. Codex build is a **separate** task (`mmi-iceberg-l5-cross-packet-correlation-build`) requiring `authorize build`.
