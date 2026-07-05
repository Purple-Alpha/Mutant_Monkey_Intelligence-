# Claude Handoff — Iceberg Layer 4 Behavioral Fingerprint (A)

**Task id:** `mmi-iceberg-l4-behavioral-fingerprint-spec`  
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
Repo: /mnt/c/Architectapp_clean
Phase 1 weapon stack: PASS (tiers [4,4,4] — do not re-litigate).

Existing depth layers (match these patterns):
- chaos/canary_metadata_layer.py — L8, hard-drop, pre-signature
- chaos/graph_topology_layer.py — L6, post-signature, verify_transition_edge(metadata)
- chaos/metadata_ingress_gate.py — tip + L6/L8 wired in admit()

Iceberg doctrine: architecture/MMI_METADATA_ICEBERG_2026-07.md
</production_inventory>

<target_objective>
Write: mmi/project_brain/architecture/MMI_ICEBERG_L4_BEHAVIORAL_FINGERPRINT_SPEC_2026-07.md

Layer 4 — Behavioral fingerprint:
- Rolling per-sender profile derived gate-side (payload UTF-8 byte size, payload key-count/shape, target_capability mix)
- Attacker with leaked Ed25519 key cannot know agent_01's baseline
- Cold start: record-only until baseline exists (minimum N packets per sender) — never hard-drop first contact
- Anomaly on established baseline: route to Mirror Dimension for inspection — NOT hard-drop like CANARY_TRIPPED or SIGNATURE_MISMATCH
- Return API: (ok: bool, dict with error/detail) identical to L6/L8
- Persistence: reuse _NonceStore pattern from metadata_ingress_gate.py (atomic JSON on disk)
- Integration: post-signature slot in MetadataIngressGate.admit() after L6
</target_objective>

<execution_constraints>
1. Output the markdown spec file only — no chat intro or closeout.
2. Keep it short: operational definition, pass/fail lines, falsification criteria, data schema, integration sketch, non-goals.
3. Include 3 falsifiable test scenarios (cold start, normal match, anomaly flag).
4. Explicit non-goals: no L5 correlation, no L7 rhythm, no L9 chain depth, no unbounded code execution.
5. Sign-off line at end: PASS | PASS WITH REVISIONS | FAIL.
</execution_constraints>

<existing_implementation_pattern>
L6 method signature pattern:
  verify_transition_edge(metadata: dict) -> tuple[bool, dict[str, Any]]

L8 error shape:
  {"error": "CANARY_TRIPPED", "detail": "..."}

L4 proposed error codes (you may refine):
  FINGERPRINT_COLD_START (ok=True, record only)
  FINGERPRINT_ANOMALY (ok=False or soft-flag per spec — must route Mirror Dimension not silent drop)
</existing_implementation_pattern>

<no_explanations_directive>
Respond with the complete markdown spec file contents only. Assumptions in spec footnotes — not conversational prose.
</no_explanations_directive>
```

---

After Claude returns the spec, relay output path to Cursor PM for closeout. Codex build is a **separate** task requiring `authorize build`.
