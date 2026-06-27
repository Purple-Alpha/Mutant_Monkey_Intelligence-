# Geo-Context Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_43_GEO_CONTEXT_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** **DRAFT (pre-§11).** Matt confirmed Lane 1 scope 2026-06-27 (MMI-DEC-250). Pre-build gate **PASS** (`geo_context_contract_gate` 0 blocking / 1 warning). Not §11 signed. Not build authorization. Not production dispatch.

**Scope:** Scoreboard #43 — **Lanes 1–2 + Lane 3 privacy bar only.** Lane 4 deception explicitly excluded — see `mmi/project_brain/architecture/reality_controller/README.md` and `geo_context_43_research_lanes.md`.

**Owner:** Matt Nichol

**Candidate:** #43 — Geo-Context

**Track:** BREADTH

**Lane:** Agent Design Contract (cold feedstock `607d86f` → hot formal placement MMI-DEC-250)

**Authority repo:** `/home/socialarchitect/northstar`

**Proposed future build path:** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/geo_context_agent.py` (`GeoContextAgent`, `geo_context_001`)

**Source-of-truth links:**
- `mmi/project_brain/architecture/geo_context_43_research_lanes.md` (Lane 1 scope + #43 vs #76/#79 reconciliation)
- `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md`
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Lookalike_Domain_Agent_Design_Contract_Deep_Dive.md` (caller-owned roster pattern)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#43, #76, #79 rows — read-only)
- `VISION.md`

---

## Agent Design Contract block

| Field | Value |
|---|---|
| Agent name | Geo-Context Agent (`GeoContextAgent`) |
| Swarm inventory ID | #43 — Geo-Context |
| Canonical layer | 2 — Detection (Lane 1 context synthesis; not Layer 0 brief, not Layer 1 velocity detector) |
| Canonical team / case type | Inbound artifact geo-context; tenant-declared legitimate service area / jurisdiction / locale vs observed session-network context |
| Authority level | Level 3 — Specialist Agent (facts-only context synthesis; matches #10 / #21 ES1 peers) |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (see template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic.** Validated on synthetic test data only; intentionally NOT registered in `build_default_registry` / production dispatch. |
| Role | Emit tenant-declared legitimate geo-context facts and closed `declared_vs_observed_mismatch` observations by comparing caller-supplied `TenantGeoContextRosterV1` against optional read-only #76 `GeoBriefing` fields — never anomaly detection, fraud verdict, or decoy routing. |
| Boundary | Context facts are not the decision. The agent must not decide fraud, approve/deny mail, block/quarantine, change payment behavior, emit `geo_signal`, re-assemble Layer 0 geo briefs, route decoys, or claim compliance / legal advice. |
| Explicit non-authorities | No Lane 4 Reality Controller; no person-level tracking; no persistent cross-session geo identity at ES1; no re-emission of #76 `GeoBriefing` or #79 `geo_signal`; no AUTH-5; no scoreboard mutation; no autonomous action; no production dispatch at ES1; no raw PII in DER. |
| Inputs | Caller-owned frozen `TenantGeoContextRosterV1` supplied at agent construction (per-tenant wiring). Optional read-only `GeoBriefing` from #76 for declared-vs-observed comparison when caller wires it. One `MissionContext` + tenant-scoped Blackboard read path when session artifact context is required. |
| Outputs | One `AgentContribution` (layer 2): closed `observed_facts` from the Lane 1 vocabulary (§4) when roster-vs-observed comparison yields a fact; otherwise empty. No score, block recommendation, or `geo_signal`. |
| Evidence emitted | `TenantGeoContextFacts` DER slice: `declared_service_area`, `declared_jurisdiction_frame`, `expected_locale`, `policy_pack_ref`, and/or `declared_vs_observed_mismatch` — closed-set fact names only per §4. No `geo_velocity_anomaly`, no entrapment/decoy tokens. |
| Data minimization | No mailbox body content; no raw header dumps; no person-level identifiers; no cross-tenant roster fields in contribution; `inputs_digest` is SHA-256 of canonical roster + compared brief digest, not raw payloads. Country/region/ASN **class** tokens only. |
| Tenant isolation | Caller supplies per-tenant `TenantGeoContextRosterV1` at construction; tenant A roster must never be reused for tenant B at the wiring boundary; agent reads only the tenant-scoped Blackboard path when artifact context is used. |
| Two-pass role | Pass 1 (context fact emit) only. `challenge()` returns `None`. |
| Decision Evidence Record contribution | `observed_facts`: Lane 1 closed facts from §4 when present; `interpretations`: none; `assumptions`: caller roster is current for tenant; `missing_evidence`: empty roster or absent comparison brief yields no mismatch fact; `recommended_verification`: none authored at Layer 2; `final_outcome_contribution`: declared-context facts and mismatch observations only; `retest_or_learning_record`: per template §6.5. |
| Human review trigger | None authored by this agent; Commander disposition and downstream layers own escalation. |
| Verification trigger | None authored at Layer 2; mismatch facts may feed Verification / #79 / human review downstream — not authored as verdict here. |
| Scoring / action posture | Facts-only contribution. No scoring lift authored by this wrapper; no block/allow; pipeline default-off integration remains outside this agent. |
| Default rollout | Evidence Stage 1: not in `build_default_registry`; explicit callers/tests only until signed Stage 2 promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`. |
| Promotion conditions | Per template §6.2 Stage 1→2 bar: clean tests, real-sample review, signed promotion record, reconciliation proof vs #76/#79 maintained. |
| Demotion conditions | Per template §6.3 — including duplicate `geo_signal` emission, decoy vocabulary leakage, or cross-tenant roster bleed. |
| Retest evidence | Per template §6.5 progressive hardening. |
| Calibration requirement | None at ES1 beyond focused synthetic tests; Stage 2 promotion may require tenant-roster integration review. |
| Failure modes | See §7. |
| Required tests | `tests/test_geo_context_agent.py` — must prove: roster declared facts emit; mismatch observation when brief disagrees with declared service area; no fire on empty roster; no `geo_signal` / velocity tokens; no Lane 4 vocabulary; tenant isolation; `challenge()` None; facts-only boundary. |
| Audit requirements | `complete_gate.py` on contract slice before §11; separate build-slice gate after implementation. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `geo_context_43_research_lanes.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, #76 / #79 governed contracts (read-only reconciliation). |
| Build Authorization dependency | §11 signature authorizes contract only — **not** implementation. Wrapper build requires §11-signed contract + explicit operator `MODE: BUILD` / named build lane + focused tests. No Stage 2/3 registration without separate promotion record. At signing, Evidence Stage **1** only. |

---

## §0 Purpose

Place a full Agent Design Contract for swarm #43 **Geo-Context Agent** scoped to **Lane 1** tenant-declared legitimate context (service area, jurisdiction frame, expected locale, policy-pack references) reconciled against governed **#76 GeoIntelAgent** and **#79 GeoVelocityAgent** without absorbing their layers. Lane 4 deception remains **PARK**. **Does not** authorize build in this document.

---

## §1 Scope

### In scope
- Lane 1 context synthesis via `TenantGeoContextRosterV1` (frozen §3).
- Closed `TenantGeoContextFacts` vocabulary (§4).
- Optional read-only comparison against #76 `GeoBriefing`.
- Reconciliation appendix vs #76 / #79 (§5).
- Evidence Stage 1 (Synthetic) declaration.
- Focused test plan for future `GeoContextAgent` wrapper.

### Out of scope
- Lane 4 Reality Controller / `geo_fence_manager.md` deception imports.
- Person-level tracking or cross-session geo identity.
- #79 velocity detection or `geo_signal` writer role.
- #76 Layer 0 brief re-assembly.
- Block/allow/payment/containment actions.
- Default registry / production dispatch at ES1.
- Legal advice or customer-facing compliance claims.

---

## §2 Locked Design Decisions

- **D1 — Identity.** Geo-Context is Layer 2 context synthesis, Authority Level 3, VISION Stage A, Evidence Stage 1 at signing. `agent_id = geo_context_001`.
- **D2 — Lane 1 product surface.** Tenant service area + jurisdiction context + expected locale + policy-pack refs — confirmed Matt 2026-06-27 (MMI-DEC-250).
- **D3 — Facts-only.** Emits closed Lane 1 fact names only; no fraud verdict, no `geo_signal`, no decoy routing.
- **D4 — Caller-owned roster.** `TenantGeoContextRosterV1` at construction — same wiring pattern as #10 `known_good_domains` / #21 principal roster; no Vendor Baseline Store reads at ES1.
- **D5 — #76 / #79 separation.** #43 consumes optional `GeoBriefing` read-only; never re-emits Layer 0 brief or Layer 1 velocity logic (§5).
- **D6 — Stage A / no autonomy.** No block/quarantine/deny; no autonomous action.
- **D7 — Evidence Stage governance.** Template §6.2 / §6.3 / §6.5 apply.
- **D8 — Privacy bar (Lane 3).** No person-level tracking; no persistent cross-session geo identity at ES1; tenant isolation mandatory.
- **D9 — Lane 4 hard boundary.** Reality Anchor, tarpit, synthetic telemetry, Hack-Bot — **PARK**; not importable into #43 ES1.

---

## §3 TenantGeoContextRosterV1 (FROZEN — caller-owned)

**Status:** **FROZEN** for §11 and ES1 build. Caller supplies at `GeoContextAgent` construction; wrapper does not persist or mutate roster storage at ES1.

```text
TenantGeoContextRosterV1
  tenant_id: str                          # required; must match MissionContext tenant
  declared_service_areas: tuple[str, ...] # ISO 3166-1 alpha-2 and/or signed region tokens
  declared_jurisdiction_frames: tuple[str, ...]  # advisory internal frame ids (not legal advice)
  expected_locales: tuple[str, ...]      # BCP 47 language tags (e.g. en-CA)
  compliance_policy_pack_refs: tuple[str, ...]   # opaque refs to signed operator process docs
```

**Rules:**
1. All fields are **declared legitimate context** — not observed network facts.
2. Empty tuple = field not declared (not an error); mismatch facts emit only when comparison surface exists.
3. Wrapper **never** fetches roster from cross-tenant stores at ES1.
4. Stage 2 may add Vendor Baseline Store wiring only via separate signed promotion — not in ES1.

---

## §4 TenantGeoContextFacts vocabulary (closed set)

| Fact name | When emitted | Owner |
|-----------|--------------|-------|
| `declared_service_area` | Roster declares service area token applied to session | #43 |
| `declared_jurisdiction_frame` | Roster declares jurisdiction frame token | #43 |
| `expected_locale` | Roster declares expected locale token | #43 |
| `policy_pack_ref` | Roster declares compliance policy-pack reference | #43 |
| `declared_vs_observed_mismatch` | Declared roster token disagrees with optional #76 brief class token — **observation only** | #43 |

**Forbidden in #43 contribution:** `geo_velocity_anomaly`, `geo_signal`, `entrapment_score`, decoy/tarpit tokens, raw country strings from headers, person-level identifiers.

---

## §5 Reconciliation vs #76 and #79

| Agent | Layer | Emits | #43 must not duplicate |
|-------|-------|-------|------------------------|
| **#76 GeoIntelAgent** | Layer 0 | `GeoBriefing` | Raw geo intel re-emission; brief assembly |
| **#79 GeoVelocityAgent** | Layer 1 | `geo_signal` | Velocity detection; impossible-travel logic |
| **#43 Geo-Context** | Layer 2 context | `TenantGeoContextFacts` | Detection verdicts; decoy routing |

**Integration pattern:**

```text
TenantGeoContextRosterV1 (caller) -> #43 -> TenantGeoContextFacts
GeoBriefing (#76, optional read)  ->  |     -> declared_vs_observed_mismatch (fact)
                                      v
                            Scoring / #79 / review (downstream)
```

---

## §6 Lane 4 exclusion (mandatory)

Do not import from `geo_fence_manager.md`: Reality Anchor, synthetic telemetry, Entrapment Score, tarpit, shadow-serving, Hack-Bot escalation. See `mmi/project_brain/architecture/reality_controller/README.md`.

---

## §7 Failure modes

- Empty roster with mismatch expected → no `declared_vs_observed_mismatch` fire (missing comparison baseline).
- Cross-tenant roster wiring → governance failure.
- Emission of `geo_signal` or velocity tokens → schema/policy failure.
- Lane 4 vocabulary in contribution → hard boundary violation.
- Jurisdiction frame presented as legal advice → claim-safe / compliance failure.
- Person-level or cross-session geo tracking → privacy bar failure.

---

## §8 Required tests (future build slice)

`tests/test_geo_context_agent.py` must prove: declared facts emit from roster; mismatch observation when brief disagrees; no fire on empty roster; no `geo_signal` / velocity / Lane 4 tokens; tenant isolation; `challenge()` returns `None`; facts-only DER contribution boundary.

---

## §9 Evidence Stage declaration

- **Current:** Stage 1 — Synthetic.
- **Stage 2/3:** Separate Matt-signed promotion per template §6.2.

---

## §10 Open before §11

1. ~~Matt confirms Lane 1 scope~~ — **confirmed** MMI-DEC-250
2. ~~Reconciliation appendix~~ — **documented** §5 + research artifact
3. ~~Roster schema (§3 `TenantGeoContextRosterV1`)~~ — **complete**
4. ~~Pre-build gate clean on this formal contract file~~ — **PASS** (`geo_context_contract_gate` 0 blocking)

---

## §11 Sign-off

**UNSIGNED.** Pre-build gate must report **0 blocking** before Matt §11. Signing locks D1–D9 for swarm #43 at **Evidence Stage 1 (Synthetic)**. Signing authorizes future `GeoContextAgent` wrapper + focused tests **only** after separate operator Build Authorization. Signing authorizes **no** production dispatch, **no** default-registry registration, **no** Lane 4 import, and **no** autonomous action.

> §11 SIGNATURE — (pending clean pre-build gate)

---

## Boundaries (this contract)

- Design / contract draft only until §11
- No build authorization from this file alone
- No production dispatch
- No AUTH-5
