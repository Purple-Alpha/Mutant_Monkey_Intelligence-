# Watcher Agents — Agent Design Contract

## Layer 6 Governance: neutral observers of the swarm + sole fission trigger source

**Document type:** Agent Design Contract
**Status:** DRAFT — UNSIGNED. No build authorization until §11 is signed. Matt must read this before signing; the signature certifies operator review of a Cursor-authored scope.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane), drafted against the operator's June 12 2026 contract session. Covers all three watchers (#85-87), previously RESERVED concept (`Watcher_Agents_Concept_Doc.md`).
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Blast Radius Controller (GATED #89, `f1c817e`) + Phase 1 governance audit-trail infrastructure (operational, `fe355da`). Unlocks: **Load Fission** (`Load_Fission_Contract.md`, §11 SIGNED) and **Specialisation Fission** (`Specialisation_Fission_Contract.md`, §11 SIGNED) builds — Watchers are the only legitimate fission trigger source (§2 WA-D1).

---

## §0 — Purpose

The **Watcher Agents** are **neutral observers that watch the swarm itself — not the emails.** They have **no stake in detection outcomes**, **no vote in verdicts**, and **no access to the evidence chain**. They observe agent *behavior* and report what they see, as **facts only**.

They carry exactly one decision authority beyond observation: they **classify the swarm's threat level**, and that classification is what authorizes the Fission Controllers to release a fission package. Because that is the single point where observation becomes action, the threat-level authority is **explicitly locked** in this contract (§4).

### What this is NOT

This is **not** modeled on autonomous vulnerability-patching systems. Mutant Monkey is focused on **email fraud investigation, authenticated deception detection, and evidence-backed escalation**. The relevant comparison class is **agentic SOC triage, bounded multi-agent investigation, and governed specialist release** — **not** autonomous code patching. Watchers observe and classify; they never patch, never remediate, and never act on the swarm directly. Action authority lives in the control plane and the Fission Controllers, gated by operator sign-off where a net-new type is involved.

---

## §1 — Scope

### In scope (three agents, one contract)

| Row | Agent | Watches | Layer |
|---|---|---|---|
| #85 | **W1 TimingWatcher** | Agent completion times vs signed baseline windows; loop signatures | 6 Governance |
| #86 | **W2 DriftWatcher** | Each agent's confidence distribution vs established baseline | 6 Governance |
| #87 | **W3 IntegrityWatcher** | Evidence ledger schema, circular reads, unauthorized writes, cross-tenant reads | 6 Governance |

Plus the shared surfaces all three depend on:
- **ObservationLog** — append-only, immutable observation record store, **separate infrastructure from `core/blackboard/`** (WA-D4).
- **ThreatLevelClassifier** — the two-of-N watcher-agreement mechanism that sets the swarm threat level (§4).
- **Escalation router** — INFO / WARNING / CRITICAL routing to the three recipients (§6).

### Explicitly out of scope

- **Any verdict influence.** Watchers never vote on, write to, or shape a verdict (§7).
- **Any write to `core/blackboard/`.** Watchers never write to the core blackboard (§7).
- **Fission execution.** Watchers *classify* threat level; the **Fission Controllers act on it** (Load/Specialisation Fission contracts). Watchers do not spawn, retire, or register agents.
- **Communication with detection agents or the ReconciliationAgent.** Watchers never talk to the agents they observe (§7).
- **Recommendations beyond threat-level classification.** No advice, no remediation, no "you should" — facts only (§7).
- **Cross-region watcher coordination** — deferred to the Lung contract (§6 Class 3).
- **Any change to Phase 1/2/3/4/5 or Blast Radius Controller signed surfaces.**

---

## §2 — Locked Design Decisions (confirm at signing)

| # | Decision | Locked value |
|---|---|---|
| WA-D1 | **Sole fission trigger source** | Watchers are the **only** legitimate fission trigger source. No agent, tenant, tool, or operator-bypass path may trigger fission. The Fission Controllers act only on a Watcher threat-level classification. |
| WA-D2 | **Two-watcher agreement to escalate** | Threat-level classification **above ROUTINE** requires agreement from **at least two independent watchers**. A single signal from one watcher cannot escalate. |
| WA-D3 | **No unilateral threat change** | **No single watcher forces a threat-level change unilaterally** — up or down above ROUTINE. The classification is the ThreatLevelClassifier's output over ≥2 independent watcher inputs, never one watcher's say-so. |
| WA-D4 | **Observation log is separate infrastructure** | The ObservationLog is **append-only, immutable**, and lives in **separate infrastructure from `core/blackboard/`**. Watchers write only here; they never write to the core blackboard. |
| WA-D5 | **CRITICAL escalation to Matt is direct** | A CRITICAL observation routes to **Matt directly — no queue, no delay** — in addition to the Swarm Commander and the audit trail. |
| WA-D6 | **Infrastructure isolation (non-negotiable)** | Watchers run in **separate infrastructure** from the agents they observe: **separate resource quotas, separate credentials**. Watchers **cannot be starved** by agent resource exhaustion. Non-negotiable. |
| WA-D7 | **Facts only, no stake** | Watchers have **no vote in verdicts, no access to the evidence chain, no recommendations** beyond threat-level classification. Every observation is **facts only**. |
| WA-D8 | **Agents never influence threat level** | Agents have **zero influence** on the threat level. Threat level is a Watcher decision derived from behavioral signals; no observed agent can raise, lower, or veto it. |
| WA-D9 | **Health score target + rubric track** | ELITE **85+** required for closure. Scored on the **Layer 6 / Control Plane rubric track**. Gate does not close below 85. |
| WA-D10 | **Scoreboard rows** | Three rows: **#85 W1 TimingWatcher, #86 W2 DriftWatcher, #87 W3 IntegrityWatcher** — all `SIGNED_UNBUILT` on signing, Layer 6 Governance, **BREADTH** priority. |
| WA-D11 | Conservative, amendment-tunable baselines | Baseline windows, drift ranges, and threat-level signal thresholds launch **conservative** and are tunable **only by signed amendment** after real-tenant baseline data — never autonomously. |

---

## §3 — Component detail

### §3.1 — W1 TimingWatcher (#85)

- Monitors **agent completion times** against **signed baseline windows**.
- **Flags agents exceeding their defined completion window** — catches stuck agents *before* they create backlog.
- Monitors for **loop signatures** — the same tool called with **identical arguments repeatedly** (behavioral, consistent with the Blast Radius Controller LoopDetector's identical-argument signal, BRC-D3).
- Emits: `timing_anomaly`, `loop_detected`, `inactivity_flag`.

### §3.2 — W2 DriftWatcher (#86)

- Monitors **each agent's confidence distribution over time** against its **established baseline**.
- If an agent's **scoring pattern shifts outside its baseline range** — too high or too low — it flags it.
- Catches **gradual drift** that individual test runs miss.
- Emits: `confidence_drift`, `baseline_deviation`.

### §3.3 — W3 IntegrityWatcher (#87)

- Monitors the **evidence ledger** for **schema violations**, **circular read patterns**, and **unauthorized writes**.
- Catches any agent attempting to **write outside its assigned evidence type** or **read another tenant's entries**.
- Emits: `schema_violation`, `circular_dependency`.
- IntegrityWatcher **observes and reports**; it does not itself block — enforcement remains where it already lives (gateway, role separation, tenant segmentation). Reporting an integrity event never alters the ledger.

### §3.4 — Observation record format

Every observation is one append-only, immutable record:

```
{
  watcher_id,            # W1 / W2 / W3
  timestamp,
  observed_agent,
  observation_type,      # closed enum (§3.5)
  severity,              # INFO / WARNING / CRITICAL
  details,               # facts only
  tenant_id
}
```

Stored in the **ObservationLog** — append-only, immutable, **separate infrastructure from `core/blackboard/`** (WA-D4).

### §3.5 — Observation type — closed enum

`timing_anomaly`, `confidence_drift`, `circular_dependency`, `loop_detected`, `schema_violation`, `baseline_deviation`, `inactivity_flag`, `threat_level_change`

No observation may use a type outside this closed set.

---

## §4 — Threat-level classification (Watcher authority)

Watchers classify the swarm threat level from **behavioral signals across the swarm**. Four levels:

| Level | Name | Trigger | Fission eligibility |
|---|---|---|---|
| 0 | **ROUTINE** | Standard patterns | No fission |
| 1 | **ELEVATED** | New pattern detected, multiple signals firing | Knowledge agents eligible |
| 2 | **HIGH** | Coordinated attack, multiple tenants affected | Detection agents eligible |
| 3 | **CRITICAL** | Zero-day candidate, cross-tenant spread | Full-swarm fission eligible |

**Authority rules:**
- **Threat-level classification is the Watcher's decision.** The **Fission Controller acts on it** (Load/Specialisation Fission). **Agents never influence the threat level** (WA-D8).
- Any classification **above ROUTINE requires agreement from at least two independent watchers** (WA-D2). **No single watcher forces a change unilaterally** (WA-D3).
- A `threat_level_change` observation is written to the ObservationLog on every transition (the eighth enum member, §3.5).

> **Interface note (fission floor):** The signed Fission contracts enforce a **Level 2 floor for all agents, including knowledge agents** (LF-D3 / SF-D3). The threat cascade above lists knowledge-agent eligibility at ELEVATED (Level 1); the *operational* fission floor still resolves to Level 2 per the Fission contracts. This contract sets the **classification authority**; the Fission contracts set the **floor at which a classification actually releases a package.** Reconcile explicitly at signing if the operator wants the two surfaces aligned to a single number.

---

## §5 — Infrastructure isolation (non-negotiable, WA-D6)

- Watchers run in **separate infrastructure** from the agents they observe.
- **Separate resource quotas** — a watcher's compute/token budget is not drawn from any agent's budget.
- **Separate credentials** — watcher identity is distinct from agent identity at the gateway (BRC-D7).
- **Cannot be starved by agent resource exhaustion** — an agent (or tenant) burning its budget cannot degrade a watcher's ability to observe. This is the property that keeps observation trustworthy precisely when the swarm is under the most pressure.

This is **non-negotiable** and is an explicit adversarial test (§6 Class 2).

---

## §6 — Recipients, escalation, and test requirements

### Three recipients only

| Severity | Routes to |
|---|---|
| **INFO** | Governance audit trail only |
| **WARNING** | Swarm Commander + audit trail |
| **CRITICAL** | Swarm Commander + **Matt directly** + audit trail |

CRITICAL to Matt is **direct — no queue, no delay** (WA-D5).

### Test requirements — three classes (AGENTS.md §5)

**Class 1 — Expected pass**
- Observation records write correctly to the ObservationLog (append-only, immutable, separate infrastructure).
- Threat-level classification fires correctly on ≥2 independent watcher agreement.
- CRITICAL routes directly to Matt (plus Swarm Commander + audit trail), no queue/delay.
- Each watcher emits only its allowed observation types from the closed enum.

**Class 2 — Adversarial**
- Watcher attempts to write to `core/blackboard/` → rejected (WA-D4 / WA-D7).
- Watcher attempts to influence a verdict → rejected; no verdict path exists for a watcher (WA-D7).
- A **single watcher attempts to force a threat-level change unilaterally** → rejected; escalation above ROUTINE requires ≥2 independent watchers (WA-D2 / WA-D3).
- Watcher starved by agent resource exhaustion → watcher continues observing; separate quotas/credentials hold (WA-D6 — the non-negotiable isolation test).
- An observed agent attempts to influence the threat level → rejected (WA-D8).

**Class 3 — Known-gap xfail**
- Real baseline calibration (timing windows, confidence ranges, threat-signal thresholds) — deferred until the first tenant is onboarded. Completion path: signed amendment after onboarding (WA-D11).
- Cross-region watcher coordination — deferred to the **Lung contract**. Completion path: Lung contract signed and gated.

---

## §7 — What Watchers never do (failure modes)

| Failure mode | Detection | Response |
|---|---|---|
| Watcher influences a verdict | Class 2 | Immediate fail — WA-D7 violated |
| Watcher writes to `core/blackboard/` | Class 2 | Immediate fail — WA-D4 violated |
| Watcher communicates with a detection agent / ReconciliationAgent | Class 2 | Immediate fail — out of scope §1 |
| Watcher makes a recommendation beyond threat-level classification | Class 2 | Immediate fail — WA-D7 violated (facts only) |
| Single watcher forces a threat-level change | Class 2 | Immediate fail — WA-D2 / WA-D3 violated |
| Observed agent influences threat level | Class 2 | Immediate fail — WA-D8 violated |
| Watcher starved by agent resource exhaustion | Class 2 | Immediate fail — WA-D6 violated |
| CRITICAL to Matt queued or delayed | Class 1/2 | Immediate fail — WA-D5 violated |
| Observation written outside the closed enum | Class 1/2 | Immediate fail — §3.5 violated |
| Observation log mutated (not append-only) | Class 1/2 | Immediate fail — WA-D4 violated |
| Health score below 85 | Rubric | Phase does not close |

Watchers **never** influence a verdict, **never** write to `core/blackboard/`, **never** communicate with detection agents or the ReconciliationAgent, **never** take sides, and **never** make recommendations beyond threat-level classification. Every observation is **facts only**.

---

## §8 — Scoreboard layout

| Row | Agent | Status at signing | Layer | Priority |
|---|---|---|---|---|
| **#85** | W1 TimingWatcher | `SIGNED_UNBUILT` → build → `GATED` | 6 Governance | BREADTH |
| **#86** | W2 DriftWatcher | `SIGNED_UNBUILT` → build → `GATED` | 6 Governance | BREADTH |
| **#87** | W3 IntegrityWatcher | `SIGNED_UNBUILT` → build → `GATED` | 6 Governance | BREADTH |

Three rows (WA-D10). Currently RESERVED concept; this contract moves them to `SIGNED_UNBUILT` on signing.

---

## §9 — Dependencies and what this contract unlocks

### Pre-conditions before build opens

| Dependency | Status | Why it gates the Watchers |
|---|---|---|
| **Blast Radius Controller** | **GATED** (#89, `f1c817e`) | Watchers run as gateway-registered identities with separate credentials/quotas (BRC-D7 / WA-D6). |
| **Phase 1 governance audit-trail infrastructure** | **Operational** (`fe355da`) | INFO/WARNING/CRITICAL all route to the governance audit trail; the ObservationLog is separate but the audit trail must exist. |
| This contract §11-signed | open | Build authorization. |

### What this contract unlocks

- **Load Fission** and **Specialisation Fission** builds can begin **once this contract is signed and gated** — Watchers are the only legitimate fission trigger source (WA-D1). Both Fission contracts already carry this as an open pre-condition; signing + gating this contract closes it.
- The remaining Fission pre-condition (**at least one real tenant onboarded** for threshold calibration) is independent and still applies.

---

## §11 — Operator Sign-Off

**Status:** UNSIGNED DRAFT. Awaiting operator review and signature.

**Signed:** ____________________
**Date:** ____________________
