# MMI Research Advisory — IFM & Pneumatic Lung: Aligns / Conflicts / Park

**Classification:** `RESEARCH_INPUT` · `ADVISORY_MEMO` · `EXPLICITLY_NOT_DOCTRINE` · `ZERO_ROUTING_INFLUENCE` · `NOT_BUILD_AUTHORIZATION`

**Subject:** Immune Federation Mesh (IFM) & Pneumatic Lung Hardening — Aligns / Conflicts / Park

**Reference:** MMI-DEC-092 · `#105` Governance Invariants · MMI-DEC-140 · `docs/mmi/contracts/004_immune_federation_mesh_contract.md`

**Date:** 2026-06-25

**Source:** Lead Researcher advisory (operator correction reset) — research lane input only

**Boundary:** Advisory brainstorming only. Does not override signed MMI doctrine. No decision log entry. No BOR feedstock. No build influence. No routing authority. Matt §11 and Operator Authority remain sole promotion and execution gates.

---

## 1. ALIGNS (Adopted into Design)

These concepts are consistent with existing MMI doctrine and should be developed further in the Design/Audit lanes.

- **Threat-Shape Sanitization:** Develop the Mesh as a pulse bus for sharing sanitized threat metadata, utilizing ReconciliationAgent `#84` for egress and Mode Controller `#92` for local response. Governing principle: shared threat shape; never shared tenant truth (Guardrail 11; IFM contract MMI-DEC-140).
- **Event-Driven Telemetry:** Utilize system stress (latency, probe failure, CPU variance) as **candidate** triggers for Mode Controller evaluation — not automatic hardening without operator-defined Mode Controller paths.
- **Axiom Mapping:** Perform a rigorous **cross-check against `#105` LAW 1–9** to ensure any new security design proposal is compliant with existing Governance Invariants before submission to the Operator. This is compliance verification, not drafting new immutable axioms.
- **Adversarial Hardening:** Prioritize HMAC, anti-replay, and anti-poisoning controls as primary security concerns for the IFM (per MMI-DEC-131 closeout and hardening addendum).

---

## 2. CONFLICTS (Rejected / Redacted)

These concepts violate signed MMI doctrine and are removed from the implementation path.

- **Autonomous Quorum Authorization:** The proposal for agents to "vote" or "sign off" on actions to bypass Matt's §11 signature is **REJECTED**. All promotion and execution gate decisions remain solely with the Operator (Matt).
- **Crypto-Quorum Promotion:** Any system where agents promote GATED → GOVERNED_AGENT based on consensus is **REJECTED**. Lifecycle promotion is an Operator-decision process involving verifiable evidence.
- **Mesh as an Execution Engine:** Using a script (e.g. `mmi_federation_mesh.py`) as an "Axiom Enforcer" that clears work independently is **REJECTED**. The Evidence → Operator Decision → Execution flow remains immutable.
- **Automatic Hardening:** The notion of "auto-authorizing" a hardened state (e.g. within 10ms) without an operator-defined Mode Controller path is **REJECTED**.

---

## 3. PARK (Deferred for Future Review)

Concepts that are theoretically interesting but currently lack a signed authority path.

- **Peer-to-Peer Consensus:** Parked. MMI doctrine relies on centralized Operator authority; any movement toward P2P consensus requires a formal Governance Invariant amendment (`#105`).
- **Independent Node Identity (via Disk/Files):** Parked. Current MMI architecture uses Python wrappers/orchestration in the authority repo. Any shift to independent identity-based nodes must be evaluated against the Blackboard/Sandbox architectural pattern before design promotion.

---

## 4. Next actions (lane pointers — not authorization)

| Lane | Suggested next work |
|------|---------------------|
| **RESEARCH** | No active fork — IFM §11 signed (MMI-DEC-140); park unless new research intake |
| **DESIGN** | Hardening review **complete** (MMI-DEC-140); resolve remaining §13 items when Matt selects (copy cap, legal consent, pool boundary, pilot, protobuf) |
| **AUDIT** | Populate adversarial review checklist for mesh controls (HMAC, replay, anti-poisoning) |
| **BUILD** | Blocked — no separate build authorization |

---

**Status:** Filed as advisory research input only. Holds no execution authority.
