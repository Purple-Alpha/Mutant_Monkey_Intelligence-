# Fission v2 Scoreboard Reconciliation Plan

**Plan ID:** `FISSION_V2_SCOREBOARD_RECONCILIATION_PLAN`  
**Date:** 2026-06-16  
**Authority:** Planning-only lane — Matt authorized reconciliation **planning**, not scoreboard patch or build  
**Upstream review:** `mmi/reviews/SIGNED_CONTRACT_SCOREBOARD_RECONCILIATION_REVIEW.md` @ `8520243`  
**Branch:** `safety/queue-drift-cleanup-20260528`

---

## Scope and guardrails

| In scope | Out of scope (not authorized) |
|---|---|
| Propose exact `SIGNED_UNBUILT` row text for both v2 contracts | Apply scoreboard edits |
| Define lineage to #90 / #91 | Build or implementation |
| Record conflicts and follow-on patch prerequisites | Dispatcher, routing, authority matrix edits |
| State Matt approvals required before patch | `PROJECT_HANDSHAKE.md`, concept drafts |
| Non-authorization language for MMI doctrine | Threat Intelligence Daemon (external lane — separate track) |

**This plan does not authorize build, scoreboard edits, or implementation.**

---

## Operator decision being implemented (plan only)

Matt approved **scoreboard reconciliation planning** for:

1. Load Fission v2 — `4. Product_Roadmap/Load_Fission_Contract_v2.md`
2. Specialisation Fission v2 — `4. Product_Roadmap/Specialisation_Fission_Contract_v2.md`

Goal: explicit lifecycle rows as `SIGNED_UNBUILT`, preserving #90 and #91 as historical v1 `GATED` lineage.

---

## Recommended reconciliation model

### Sibling amendment rows (recommended)

Add **two new rows** — do **not** rewrite #90 or #91.

| Principle | Rationale |
|---|---|
| #90 / #91 stay `GATED` | Record v1 build closure (2026-06-12); contracts say v2 supersession does not rewrite historical gate records |
| #103 / #104 start `SIGNED_UNBUILT` | Filename-visible lifecycle tracking for v2 contracts; satisfies `mmi_dispatch.py` filename match |
| Load (#103) before Specialisation (#104) | Preserves scoreboard advisory ordering: shared `FissionEventLog` / Load wiring landed first under v1 |
| On v2 closure, new rows go `GATED` | #103/#104 absorb v2 gate evidence; #90/#91 remain v1 historical unless Matt later authorizes a cross-row annotation |

### Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Flip #90 / #91 back to `SIGNED_UNBUILT` | Rewrites closed v1 history; contradicts contract supersession clause |
| Single combined row for both v2 contracts | Breaks per-contract lifecycle, dispatcher row naming, and independent audit/gate paths |
| Amend #90 / #91 status cells in place only | Filename `Load_Fission_Contract_v2.md` still absent — MMI filename check remains unsatisfied |

---

## Proposed row — Load Fission v2 (#103)

### Metadata

| Field | Value |
|---|---|
| **Proposed row #** | `103` |
| **SPARK agent name** | `Load Fission Controller v2` |
| **Source contract** | `4. Product_Roadmap/Load_Fission_Contract_v2.md` |
| **Signature** | §13 — Matt Nichol, June 13th 2026 |
| **Parent / v1 lineage** | Row **#90** `Load Fission Controller` — `GATED` 2026-06-12 under `Load_Fission_Contract.md` (v1) |
| **Placement** | Top of `## Control Plane — Signed, Unbuilt` table (dispatcher emits `[0]` first) |
| **Sequencing** | **First** of the two v2 rows (before #104) |

### Proposed table row (exact paste candidate)

```markdown
| 103 | Load Fission Controller v2 | `SIGNED_UNBUILT` (Layer 6 Control Plane, ES2 Synthetic; §13-signed `4. Product_Roadmap/Load_Fission_Contract_v2.md` 2026-06-13 Matt Nichol — v2 amendment track; supersedes **contract text** of `Load_Fission_Contract.md` only; **does not rewrite** v1 closure on row #90 `GATED` 2026-06-12; scoreboard lifecycle tracking — row status is not build authorization; Matt must name build target separately) | v1 baseline exists under #90: `core/fission/load.py` + `core/fission/event_log.py`; v2 delta **not built** — governed ingestion step, policy-as-code LF2-D10, fission fallback mode, budget-exhaustion handling, Canadian legal alignment, underwriter checklist, Class 2 adversarial tests (contract §12); runtime still cites v1 contract path until v2 build closes | 6 Control Plane | ES2 | v2 amendment; lineage #90 | DEPTH | — | 2026-06-16 (SIGNED_UNBUILT row planned — NOT BUILT) |
```

### v2 delta scope (tracking reference — not built)

From contract §12 implementation gate:

- LF2-D1 through LF2-D12 (including policy-as-code, permission intersection, fresh identity)
- Governed ingestion pipeline before parent consumption
- Fission fallback mode
- Governance artifacts + failure-mode controls
- Class 2 adversarial tests (7 tests, §11)
- ELITE 85+; gate 0 blocking / 0 warnings

---

## Proposed row — Specialisation Fission v2 (#104)

### Metadata

| Field | Value |
|---|---|
| **Proposed row #** | `104` |
| **SPARK agent name** | `Specialisation Fission Controller v2` |
| **Source contract** | `4. Product_Roadmap/Specialisation_Fission_Contract_v2.md` |
| **Signature** | §18 — Matt Nichol, June 13th 2026 |
| **Parent / v1 lineage** | Row **#91** `Specialisation Fission Controller` — `GATED` 2026-06-12 under `Specialisation_Fission_Contract.md` (v1) |
| **Cross-dependency** | §2 incorporates all locked Load Fission v2 decisions — build sequencing should remain Load v2 (#103) before Specialisation v2 (#104) unless Matt overrides |
| **Placement** | Second row in `## Control Plane — Signed, Unbuilt` table (immediately after #103) |

### Proposed table row (exact paste candidate)

```markdown
| 104 | Specialisation Fission Controller v2 | `SIGNED_UNBUILT` (Layer 6 Control Plane, ES2 Synthetic; §18-signed `4. Product_Roadmap/Specialisation_Fission_Contract_v2.md` 2026-06-13 Matt Nichol — v2 amendment track; supersedes **contract text** of `Specialisation_Fission_Contract.md` only; **does not rewrite** v1 closure on row #91 `GATED` 2026-06-12; incorporates Load Fission v2 locked decisions per contract §2; scoreboard lifecycle tracking — row status is not build authorization; Matt must name build target separately) | v1 baseline exists under #91: `core/fission/specialisation.py` + shared `core/fission/event_log.py`; v2 delta **not built** — Purple Fission Curriculum pairing table, Light/Normal/Deep intensity, net-new type gate, twelve fixed child specialization schemas, Red/Blue child boundaries, governed ingestion, fission fallback, Canadian legal alignment, eight adversarial tests (contract §17); runtime still cites v1 contract path until v2 build closes | 6 Control Plane | ES2 | v2 amendment; lineage #91; depends on #103 ordering | DEPTH | — | 2026-06-16 (SIGNED_UNBUILT row planned — NOT BUILT) |
```

### v2 delta scope (tracking reference — not built)

From contract §17 implementation gate:

- All Load Fission v2 locked decisions incorporated
- Purple Fission Curriculum pairing table + intensity levels
- Net-new type gate + anti-semantic safety rule
- Twelve fixed immutable child specialization schemas
- Red / Blue child boundaries
- Governed ingestion, budget exhaustion, fission fallback
- Canadian legal alignment + underwriter checklist
- Eight adversarial tests; ELITE 85+; gate 0/0

---

## Relationship diagram — #90 / #91 vs #103 / #104

```text
v1 contracts (superseded text, not erased history)
  Load_Fission_Contract.md          Specialisation_Fission_Contract.md
           |                                      |
           v                                      v
  #90 GATED (2026-06-12)                #91 GATED (2026-06-12)
  load.py + event_log.py              specialisation.py + event_log.py
           |                                      |
           |  sibling amendment rows (proposed)   |
           v                                      v
  #103 SIGNED_UNBUILT (planned)         #104 SIGNED_UNBUILT (planned)
  Load_Fission_Contract_v2.md           Specialisation_Fission_Contract_v2.md
  §13 signed 2026-06-13                 §18 signed 2026-06-13
```

**Closure path (future, not authorized now):**

```text
#103: SIGNED_UNBUILT → (Matt authorizes build) → implement v2 delta → AWAITING_AUDIT → GATED
#104: same, after #103 unless Matt overrides sequencing
#90 / #91: unchanged unless Matt later authorizes optional cross-reference annotation
```

---

## Why this is tracking only — not build authorization

| Layer | Statement |
|---|---|
| **Contract** | v2 signatures grant implementation authority **within contract scope** — but contracts also state signing does not change scoreboard rows or deploy code |
| **Scoreboard Rule 4** | Status cell records lifecycle state; it is never itself authorization |
| **MMI Operator Decision 1** | Off-scoreboard signed contracts must not read as build-ready; adding `SIGNED_UNBUILT` rows fixes **visibility**, not automatic BUILD queue authority |
| **MMI Operator Decision 2** | `Matt names target`; `BUILD_AUTHORIZATION_IMPLIED: NO` unless Matt explicitly authorizes build |
| **This plan** | Proposes rows so MMI/dispatcher can **see** v2 lifecycle state — does not name a build target |

**Expected post-patch dispatcher behavior (informational):**

- `get_signed_unbuilt()` will return `Load Fission Controller v2` and `Specialisation Fission Controller v2`
- MODE may flip from `ALL_CLEAR` to `BUILD` — that is **sequencer visibility**, not Matt build authorization
- Matt must still authorize a named build round before implementation

Proposed row text includes explicit non-authorization language in the `Runtime status` cell to reduce scoreboard-as-authority bleed.

---

## Conflicts and tensions

| # | Conflict | Severity | Plan handling |
|---|---|---|---|
| 1 | **D2 alias vs MMI filename** — `detect_drift.py` treats v2 as covered via `"Load Fission"` / `"Specialisation Fission"` aliases on #90/#91; MMI requires contract filename in row | Medium | Patch adds filename to rows → MMI satisfied. **Follow-on (patch lane):** consider tightening `_D2_SCOREBOARD_ALIASES` for `_v2` files so D2 does not mask future drift |
| 2 | **Runtime cites v1** — `core/fission/*.py` headers reference v1 contract paths | Low (expected) | v2 build closes when code + tests + gate evidence reference v2 contract; not a blocker to adding rows |
| 3 | **Specialisation depends on Load v2** — contract §2 | Medium | Enforce #103 before #104 in table order; note in #104 `BLOCKERS` column |
| 4 | **`HANDOFF_WAITING_BUILD_CONTRACTS`** — dispatcher still lists Fission v2 as off-scoreboard drift | Low | Resolved when rows land; **separate patch** may remove Fission v2 entries from handoff waiting list after scoreboard patch (dispatcher edit — not in patch authorization unless Matt includes it) |
| 5 | **Section naming** — `Signed, Unbuilt` table contains mostly `GATED` rows | Low (cosmetic) | Do not reorganize entire section in patch lane; insert new `SIGNED_UNBUILT` rows at top only |
| 6 | **Row number collision** | None | #103 / #104 unused; highest existing `#` is 102 |

**No doctrine conflict** with MMI protocol, routing rules, or authority matrix — this plan aligns with reconciliation review recommendations.

---

## Scoreboard patch checklist (for `FISSION_V2_SCOREBOARD_RECONCILIATION_PATCH` — not authorized yet)

When Matt authorizes the patch lane, the executor should:

1. Insert proposed rows #103 and #104 at the top of the `## Control Plane — Signed, Unbuilt` table in `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`
2. Leave rows #90 and #91 **unchanged**
3. Run `python3 scripts/mmi_dispatch.py --verify`
4. Run `python3 scripts/detect_drift.py` and record D2 output
5. Confirm `Load_Fission_Contract_v2.md` and `Specialisation_Fission_Contract_v2.md` appear in scoreboard text
6. **Do not** start build, edit runtime code, or flip MODE interpretation to implicit authorization

Optional follow-ons (require separate Matt authorization):

- Update `MMI_THREAD_HANDOFF.md` waiting list
- Trim `HANDOFF_WAITING_BUILD_CONTRACTS` in `scripts/mmi_dispatch.py`
- Tighten `detect_drift.py` v2 aliases
- Add optional one-line cross-reference on #90/#91 pointing to #103/#104

---

## Exact Matt approvals required before scoreboard edit

| # | Approval | Question for Matt |
|---|---|---|
| **1** | **Reconciliation model** | Approve sibling rows #103 / #104 (recommended) vs any alternative |
| **2** | **Row numbers** | Confirm `#103` Load Fission v2 and `#104` Specialisation Fission v2 |
| **3** | **Proposed row text** | Approve exact `Runtime status`, `Code evidence`, and `BLOCKERS` cells as drafted above (or provide edits) |
| **4** | **Sequencing** | Confirm Load v2 (#103) before Specialisation v2 (#104) |
| **5** | **Patch authorization** | Explicitly authorize `FISSION_V2_SCOREBOARD_RECONCILIATION_PATCH` (scoreboard file only, per checklist) |
| **6** | **Build authorization** | **Separate** future round — naming either v2 item as build target after patch lands |

**Minimum bar to patch:** Approvals **1–5**. Approval **6** is explicitly **not** part of this plan.

---

## Threat Intelligence Daemon (out of scope — recorded for lane discipline)

Per Matt direction: **do not** add Threat Intelligence Daemon as a normal Northstar control-plane scoreboard row in this lane.

Classification remains: `NEEDS_MMI_REVIEW` / `EXTERNAL_LANE_TRACKING_REQUIRED` — separate future planning track.

---

## Plan closure

| Item | Status |
|---|---|
| Load Fission v2 proposed row | **DRAFTED** (#103) |
| Specialisation Fission v2 proposed row | **DRAFTED** (#104) |
| #90 / #91 lineage preserved | **YES — by design** |
| Build authorized | **NO** |
| Scoreboard edited | **NO** |
| Implementation authorized | **NO** |

**This plan does not authorize build, scoreboard edits, or implementation.**

**Next lane (after Matt reviews this plan):** `FISSION_V2_SCOREBOARD_RECONCILIATION_PATCH` — scoreboard insert only.
