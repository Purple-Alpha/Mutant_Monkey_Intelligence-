# MMI Cyber Security Intelligence Input — APT29 / EnvyScout Example

**Classification:** `RESEARCH_INPUT` · `CYBER_SECURITY_INTELLIGENCE_INPUT` · `NOT_AUTHORITY` · `NOT_PRODUCT_DOCTRINE` · `NOT_MMI_SUCCESS_DEFINITION` · `NOT_BUILD_AUTHORIZATION`

**Status:** Operator-supplied concept intake only. Not signed. Not doctrine.

**Owner:** Matt Nichol (source concept)

**Created:** 2026-06-19

---

## 1. Title

MMI Cyber Security Intelligence Input — APT29 / EnvyScout Campaign Example

---

## 2. Authority status

This document is **research and classification intake only**.

It is **not** routing authority, **not** a signed spec, **not** product doctrine, **not** an MMI success definition, and **not** build authorization.

It does **not** authorize detection engineering, agent contracts, runtime rules, dispatcher changes, registry-fed routing, or scoreboard updates.

Matt decides whether any future doctrine, contract, or build follows from this input.

---

## 3. Source summary

Matt supplied an APT29 / EnvyScout-style campaign example to illustrate how raw indicators differ from decision-useful cyber security intelligence.

The example is preserved here as MMI input material for future review. It is not a claim that Mutant Monkey Security has validated this campaign against live telemetry, customer data, or insurer-facing evidence packages.

---

## 4. Data vs indicator vs intelligence distinction

| Layer | What it is | Durability | Decision value |
|---|---|---|---|
| **Data** | Raw observations: file bytes, DNS logs, proxy events, process telemetry | High volume, noisy | Low alone — needs interpretation |
| **Indicator** | Atomic artifact tied to one campaign moment: hash, domain, IP, filename | Fragile — adversaries rotate quickly | Useful for short-window blocking; decays fast |
| **Intelligence** | Behavior- and TTP-grounded understanding that changes defensive decisions | More durable when expressed as behavior, chains, and monitoring logic | High — informs detection design, monitoring scope, and response posture |

**Intake rule:** MMI should treat hashes and domains as perishable indicators unless anchored to durable behavior logic.

**Intake rule:** Intelligence is decision-useful when it converts adversary behavior into monitoring or detection logic that remains useful after artifact rotation.

---

## 5. APT29 / EnvyScout example summary

Matt's supplied example describes an APT29-associated EnvyScout-style delivery pattern where:

- Initial access may use HTML smuggling to assemble payload content locally in the browser rather than delivering a classic malicious attachment upfront.
- Follow-on stages may use ISO mounting to bypass naive attachment or download-only assumptions.
- Execution may chain through LNK files and living-off-the-land process sequences rather than obvious dropped binaries.
- Observable value shifts from static file/domain artifacts toward **how** delivery, mounting, and execution unfold.

This intake records the **conceptual lesson**, not a verified IOC list or customer-specific incident report.

---

## 6. Durable behavior / TTP observations

From Matt's example, durable observations include:

1. **HTML smuggling** — adversary logic that builds or reveals payload content in-browser; monitoring should consider DOM/script/blob/download patterns, not only attachment hashes.
2. **ISO / container mounting** — delivery that sidesteps simple "blocked attachment type" policies; monitoring should include mount events and subsequent execution paths.
3. **LNK execution chains** — shortcut-mediated execution that may invoke legitimate system binaries; detection should favor parent/child process chains over filename alone.
4. **Living-off-the-land (LOTL)** — abuse of trusted binaries and scripts; intelligence should map **allowed tool + suspicious chain + context**, not a single hash.
5. **Rapid artifact rotation** — hashes and domains change faster than defensive policy cycles; behavior-based logic outlasts point indicators.

---

## 7. Defensive decision logic derived from behavior

Decision-useful intelligence from this example would answer questions such as:

- Should monitoring expand beyond attachment scanning to browser-side assembly and download-to-mount sequences?
- Should detection prioritize process ancestry and LOLT chains over static blocklists?
- Should response playbooks assume indicator expiry and require behavior confirmation before closure?
- Should evidence collection preserve chain-of-execution context, not only the first malicious hash seen?

**Intake only:** These are candidate decision lenses. They do not authorize building any specific detector, agent, or customer-facing claim.

---

## 8. What MMI should learn from this

MMI should learn that cyber security intelligence intake may need to distinguish:

- **Perishable indicators** suitable for short-lived correlation
- **Durable TTP and behavior patterns** suitable for doctrine, detection design review, and future agent boundaries
- **Decision impact** — intelligence that does not change monitoring, detection, or response scope is weaker intelligence

MMI may later use this input when reviewing whether future intelligence doctrine, evidence packages, or swarm agents reason about behavior durability rather than artifact worship.

---

## 9. What MMI must not assume from this

MMI must **not** assume:

- This document fully defines cyber security intelligence for Mutant Monkey Security
- Mutant Monkey Security should build these detections now
- Any specific APT29 or EnvyScout IOC set is validated in-repo
- This intake satisfies insurer, compliance, or customer-facing evidence claims
- HTML smuggling / ISO / LNK monitoring is authorized product scope
- A detection-agent contract or runtime rule set is implied

---

## 10. How this may inform a future intelligence doctrine

If Matt later authorizes intelligence doctrine work, this intake may inform:

- A vocabulary for **indicator half-life** vs **behavior durability**
- Review criteria for whether swarm or MMI outputs are "data," "indicator," or "intelligence"
- Boundaries for when intelligence may influence defensive decisions without becoming autonomous action
- Separation between threat research input and governed build authorization

No doctrine file is created by this intake.

---

## 11. Open questions for Matt

1. Should MMI maintain a standing `mmi/research/` lane for cyber intelligence inputs separate from product roadmap drafts?
2. When should an intelligence input graduate from `RESEARCH_INPUT` to a signed doctrine or agent design contract?
3. Should behavior/TTP durability be a scored axis in future MMI review rubrics?
4. How should perishable IOCs be cited in evidence packages without overstating longevity?
5. Is APT29 / EnvyScout the right canonical example, or a placeholder for a broader "artifact rotation" pattern class?
6. Should future intelligence doctrine explicitly forbid hash-only closure of cases?

---

## 12. Explicit non-authority footer

**NOT AUTHORITY.** This file is `RESEARCH_INPUT` and `CYBER_SECURITY_INTELLIGENCE_INPUT` only.

It is **not** product doctrine, **not** an MMI success definition, and **not** build authorization.

It does **not** create detection-agent contracts, product requirements, runtime rules, dispatcher input, registry-fed routing, or scoreboard changes.

Matt selects any future promotion path. Rubrics rank; Matt decides.
