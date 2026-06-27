# Geo-Context Agent Design Contract — Spec-First Deep Dive (DRAFT)

**Draft ID:** `MMI_43_GEO_CONTEXT_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** **DRAFT — RESEARCH FEEDSTOCK ONLY.** Not §11 signed. Not build authorization. Not production dispatch. Matt Lane 1 scope confirmation required before promotion to formal contract.

**Scope:** Scoreboard #43 — **Lanes 1–2 + Lane 3 privacy bar only.** Lane 4 deception explicitly excluded — see `mmi/project_brain/architecture/reality_controller/README.md` and `geo_context_43_research_lanes.md`.

**Owner:** Matt Nichol

**Candidate:** #43 — Geo-Context

**Track:** BREADTH

**Authority repo:** `/home/socialarchitect/northstar` (feedstock drafted on cold worktree)

**Source-of-truth links:**
- `mmi/project_brain/architecture/geo_context_43_research_lanes.md`
- `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md`
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#43, #76, #79 rows — read-only)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`

---

## Agent Design Contract block (DRAFT)

| Field | Value |
|---|---|
| Agent name | Geo-Context Agent (`GeoContextAgent`) |
| Swarm inventory ID | #43 — Geo-Context |
| Canonical layer | TBD — context synthesis (not Layer 0 brief, not Layer 1 velocity detector) |
| Role | Emit tenant-declared legitimate geo-context facts and declared-vs-observed mismatch observations |
| Boundary | Facts only. No block/allow. No fraud verdict. No decoy routing. No person-level tracking |
| Explicit non-authorities | No Lane 4 Reality Controller; no re-emission of #76 `GeoBriefing` or #79 `geo_signal`; no AUTH-5; no scoreboard mutation |
| Inputs | Caller-supplied tenant roster; optional read-only #76 `GeoBriefing` for comparison |
| Outputs | `TenantGeoContextFacts` DER contribution |
| Privacy (Lane 3) | No person-level tracking; no persistent cross-session geo identity at ES1; tenant isolation mandatory |

---

## Lane 4 exclusion (mandatory)

Do not import from `geo_fence_manager.md`: Reality Anchor, synthetic telemetry, Entrapment Score, tarpit, shadow-serving, Hack-Bot escalation.

---

## Open before formal contract

1. Matt confirms Lane 1 scope (Superintendent action in research artifact)
2. Reconciliation appendix signed off
3. Tenant roster schema frozen (caller-owned, #10 lookalike pattern)
4. Pre-build gate clean on formal contract file (not this _DRAFT suffix)

---

## Boundaries (this draft)

- Feedstock / design only
- No §11
- No build authorization
- No scoreboard lifecycle change from cold lane
