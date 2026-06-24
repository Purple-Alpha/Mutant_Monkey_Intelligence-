# The Lung — Concept Specification (Updated)
**Status:** Advisory lane — concept doc. NOT §11 signed. No build authorization.
**Date:** June 9, 2026 · buyer voice aligned MMI-DEC-128 (Lung Multiplier; not "Agent Fission" in GTM)
**Commit reference:** fe355da
**Source:** Matt Nichol session — June 9 2026
**Operator vocabulary:** `mmi/concepts/MMI_OPERATOR_LUNG_DIAL_SPEC.md` · governance pin: `mmi/concepts/MMI_LUNG_MULTIPLIER_VS_FISSION_GOVERNANCE_ADDENDUM.md`

---

## What The Lung Is

The Lung is the elastic operating layer of the Mutant Monkey swarm. It controls two things:

1. **How hard the swarm breathes** — protection depth per tenant
2. **What the swarm is breathing for** — threat focus per tenant

These are two separate dials. They operate independently.

---

## Dial 1 — Protection Depth

Controls what happens AFTER a verdict fires. Not how detection works — what the swarm does with the result.

| Setting | Behaviour | Use case |
|---|---|---|
| Light breath | Inform only. No quarantine. Flag for operator awareness. | Defender is down. Legitimate deal email locked. Tech turns dial to Light, evidence chain confirms sender is known, email releases. Deal closes. |
| Normal breath | Quarantine high confidence. Notify operator on borderline. | Default operating mode for most MSP clients. |
| Deep breath | Hold everything suspicious. Require documented human override to release. | Law firm. Financial institution. Wire transfer environment. Cost of a miss is catastrophic. |

**The Defender outage scenario is the canonical use case for this dial.**
3:30pm. $50k deal. Defender down. Legitimate vendor email locked. Tech opens Playhouse, reads evidence chain — 40 prior emails from this sender, DKIM pass, known vendor, geo matches Canada. Turns dial to Light for this tenant. Email releases. Deal closes by 5:30. Decision logged with tech person's name and reason attached.

This is what Microsoft cannot do. No override path. No evidence chain. No dial.

---

## Dial 2 — Threat Focus

Controls which knowledge agents and detection agents the swarm prioritises for this tenant. Same swarm. Different breathing pattern based on the client's industry and risk profile.

| Focus setting | Primary agents activated | Typical client |
|---|---|---|
| Spam / Bulk | ImageClassifier, ContentAnalyzer, AIGenContentIntelAgent | Marketing agency, newsletter-heavy sender |
| Phishing | PhishIntelAgent, URLReceptor, CredentialPhishingAgent | Any SMB — default baseline |
| BEC / Fraud | BECIntelAgent, SenderHistoryAgent, GeoVelocityAgent | Professional services, law firm, accountant |
| Ransomware | RansomwareIntelAgent, AttachmentSandbox, TrojanDeliveryIntelAgent | Healthcare, municipal government, critical infrastructure |
| Full spectrum | All agents active | Enterprise, high-value target, any client post-incident |

The MSP operator sets this per client at onboarding. It can be changed at any time from the Playhouse. Every change is logged.

---

## The Lung Breathing Model — Elastic Scaling

Under normal conditions the swarm runs at baseline. Under coordinated attack it inhales.

**Inhale trigger:** volume spike + pattern match across multiple tenants simultaneously. Not just volume — pattern. A flood of identical phishing attempts hitting three tenants at once is an inhale trigger. Normal Monday morning email volume is not.

**What happens on inhale:** agent instances multiply to meet demand. The number is not fixed — it scales to the load. One agent becomes two. Two become four. The swarm grows until the attack is absorbed.

**Exhale:** cooldown period confirmed before scaling back. The swarm does not exhale mid-attack.

**Scaling events do not generate false positives.** New instances are listeners only until they have input to process.

---

## Lung Multiplier — elastic capacity (buyer voice)

This is distinct from pattern mutation (3-shot confirmation learning). The **Lung Multiplier** is the governed elastic layer — inhale under pressure, exhale when clear.

**What it is:**
When volume or complexity demands more coverage, the **Lung Multiplier** expands capacity under control-plane gates — parallel copies of existing specialists, or (separate signed path) narrower specialist types. Example shape under sustained load:

- PhishIntelAgent-Credential — credential harvesting patterns
- PhishIntelAgent-Social — social engineering patterns

Each child is more specialised than the parent. The swarm doesn't just scale — it differentiates under pressure **without autonomous field splitting**.

**Why this matters:**
Elastic defense with receipts — expansion is logged, time-bounded, and tripwired (Safe-Stop / Mode Controller), not uncontrolled agent birth.

**Governance requirements (must be in contract before build):**
- Lung Multiplier expansion requires a signed trigger threshold
- Child agents must inherit the parent's evidence schema — no new output types without a signed amendment
- Multiplier events logged to the governance audit trail with timestamp and reason
- Child agents require their own scoreboard rows after expansion
- Matt signs off on any expansion that creates a net-new agent type

**Current status:** Concept in this doc; mechanical substrate **GATED** as Load Fission `#90` / `#103` (engineering row IDs unchanged).

---

## What The Lung Is NOT

- Not a replacement for the signed Tiered Detection Intensity spec — it extends it
- Not a security bypass — the evidence chain still runs at every protection depth level
- Not autonomous — every dial change is operator-initiated and logged
- Not phase 1 — the Lung contract cannot be signed until at minimum Phase 3 (Reconciliation) is gated

---

## Calibration Unknowns (honest — these need real tenant data)

These are not blockers to building Phase 1-3. They are blockers to signing the Lung contract:

1. **Inhale threshold numbers** — what volume constitutes an attack vs normal traffic? Needs at least one real tenant's baseline data to calibrate.
2. **Lung Multiplier expansion threshold** — what complexity/volume level justifies inhale? Needs real detection data.
3. **Infrastructure cost at scale** — 10x baseline agent instances is manageable. The cost model needs to be validated before the Lung contract is signed.

None of these stop the current build. They stop the Lung contract specifically.

---

## Dependency Chain

The Lung cannot be built until:
- Phase 1 infrastructure — `core/blackboard/`, RoleSeparationController, TokenUsageTracker — SIGNED ✅
- Phase 2 knowledge agents — all six Layer 0 agents operational
- Phase 3 ReconciliationAgent — operational and gated
- Tiered Detection Intensity spec — already signed ✅ — Lung extends this via companion spec

---

## Next Action

When Phase 3 is gated and at least one real tenant is onboarded:
1. Pull baseline traffic data
2. Calibrate inhale threshold
3. Draft Lung Agent Design Contract as companion to Tiered Detection Intensity spec
4. Matt signs
5. Build begins
