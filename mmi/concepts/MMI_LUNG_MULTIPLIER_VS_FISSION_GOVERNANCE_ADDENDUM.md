# MMI CONCEPT ADDENDUM: LUNG MULTIPLIER VS AUTONOMOUS FISSION (GOVERNANCE PIN)

**Document Reference:** MMI-CON-2026-06-23

**Status:** CONCEPT ONLY / NOT AUTHORIZED FOR BUILD

**Filed by:** Matt Nichol (concept capture; operator feedback session 2026-06-23)

**Sibling concepts:**

- `mmi/concepts/MMI_BRAIN_IMMUNE_LUNG_ZERO_TRUST_CONTROL_LOOP_CONCEPT.md` — broader Manus/homeostasis research input (2026-06-18)
- `4. Product_Roadmap/Load_Fission_Contract.md` + scoreboard #90 / #103 — **mechanical substrate already GATED on disk**

**Boundary:** This addendum **pins governance vocabulary only**. It does not authorize lung inflation code, a parallel Multiplier stack, Commander spawn wiring, or registry changes.

---

## 1. Objective

Prevent metaphor drift: the **Lung Multiplier** (centralized elastic defense) must not be conflated with **autonomous agent fission** (decentralized cell division). MMI accepts the first under existing control-plane contracts; it rejects the second as an ungoverned birth path.

---

## 2. Plain-English distinction (operator feedback, captured)

| | **Lung Multiplier (accepted metaphor)** | **Autonomous fission (rejected pattern)** |
|---|---|---|
| Who spawns? | Central brain stem — Swarm Commander (#1) + control plane + watcher proposal | The agent in the field splits itself |
| Birth record | Signed ID, registry-known type, `FissionEventLog`, expiry / exhale | Often no conveyor-belt contract or DEC trail |
| Clone shape | Identical sterile blueprint; prompt/tool **parameters** only | Child inherits parent state, memory, or code permissions |
| Death | Mandatory exhale / timer / Safe-Stop cluster kill | Unclear; drift and cost runaway risk |
| MMI gates | Can pass SIGNED_UNBUILT → completion gate → GATED | Bypasses scoreboard lifecycle |

**Takeaway:** Fission as *autonomous splitting* breaks MMI gates and decision-log discipline. **Lung Multiplier** is *centralized, gated elasticity* — not a second physics engine.

---

## 3. Repo mapping (verification anchor — not build authorization)

The inhalation/exhalation cycle **already exists** under another name:

| Lung metaphor | On-disk authority (GATED unless noted) |
|---|---|
| Inhalation (spawn copies) | Load Fission Controller `#90` / v2 `#103`; watcher proposals `#85–87` |
| Exhalation (retire copies) | LF-D8 automatic exhale; threat floor drop |
| Brain stem (no self-spawn) | Swarm Commander `#1` RC-AUTH — routes caller-declared agents; **does not** inflate lungs today |
| Tripwire (kill cluster) | Safe-Stop `#94`, Mode Controller `#92`, Blast Radius `#89` |
| Append-only spawn ledger | `core/fission/event_log.py` (`FissionEventLog`) |

**Do not build a parallel “Multiplier” runtime** that bypasses Load Fission contracts. Future work **extends** `#90`/`#103` and a **signed Commander spawn-policy annex** — not a fork.

**Specialisation Fission `#91`** remains a **separate**, higher-risk qualitative expansion path (net-new types → operator sign-off). It is **not** the lung burst-defense path.

---

## 4. Forbidden patterns (governance)

1. Agent-initiated self-fission without watcher → control plane → registry → log.
2. Clones without expiration / exhale policy.
3. Clones without Safe-Stop / Mode Controller tripwire to terminate the spawned cluster.
4. Spawning without scoreboard + contract lifecycle (SIGNED_UNBUILT → gate → GATED) for any **new** agent type.
5. Treating chat metaphor (“100x clones”) as an authorized copy cap without a signed contract number.

---

## 5. Stacked discipline (no shortcuts)

Any future lung/multiplier build lane must stack applicable gates: contract §11 → pre-build gate → wrapper build authorization → completion gate → GATED reconcile → **no** default registry without separate authorization. Scores rank; Matt decides.

---

## 6. Explicit non-authorization

This addendum does **not** authorize:

- Implementation or runtime wiring
- Commander auto-spawn / lung inflation
- New copy caps or threat floors
- Executive Perimeter micro-scout blueprints
- GOVERNED_AGENT promotion
- AUTH-5 or registry-fed routing

Matt remains final authority.
