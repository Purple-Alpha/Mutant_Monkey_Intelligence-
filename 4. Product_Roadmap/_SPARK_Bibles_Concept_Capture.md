# Bibles — Spark Capture

**Status:** SPARK ONLY. Pre-spec. Unsigned. Not §11. Not a roadmap commitment.
**Captured:** 2026-05-24, 23:19 PT (post-stop, post-time-box, late-night idea preservation)
**Architect:** Matt. The structure, scope, and content of both bibles are Matt's to design.
**Purpose:** Preserve the kernel of an idea so it survives the night. Do not begin construction without Matt's lead.

---

## 2026-05-25 deferral decision

Matt's call after a long working session: **hold off on writing either bible. Do not bury them. Build them only at NorthStar revolution moments** — i.e. when something genuinely new is true about the company or the swarm that the existing distributed constitution (`VISION.md`, signed §11 specs, Decision Auditor, pre-ship gate, kill-switch, Blackboard, tenant isolation tests, registry) can no longer carry alone.

Until then: keep this file alive, append to it whenever the topic comes up, do not promote any of it to a signed document.

### What today's discussion actually produced (preserve, do not draft from)

These are Matt's working claims from the 2026-05-25 session. They are recorded here verbatim in spirit so the next pass does not lose the ground that was already covered.

- **Two bibles, two audiences, two purposes.**
  - *Shield Bible* — outward-facing **identity document**. Tells clients exactly who NorthStar is and what it stands for. Not a marketing campaign. The trust covenant.
  - *Agent Bible* — inward-facing **experimental constitution**. Real engineering bet that values-as-principal is more robust than rules-as-list. Tests whether a swarm given a real constitution behaves more intelligently and more disciplinedly than a swarm given only individual specs.
- **Implementation mechanism (when it eventually exists):**
  - Shield Bible lives as a reference document.
  - Agent Bible lives as a **system-prompt anchor** — its content loaded into every agent's runtime prompt so the constitution actively shapes behavior rather than sitting on a shelf.
  - Shield Bible is the source the Agent Bible's system-prompt anchor would partially draw from.
- **Layered structure (Matt's breakthrough framing, not a draft):**
  - **Layer 1 — Moral principles.** What NorthStar believes / what the swarm answers to.
  - **Layer 2 — Operational commands.** Concrete enforceable rules that operationalize Layer 1.
  - This split is the difference between "constitution" and "ordinary software documentation." Standard exec-summary / operating-section / glossary templates miss this and should not be used as the structure.
- **Candidate Layer 1 fragments Matt floated** (not endorsed, not signed, just preserved):
  - "NorthStar will never give up somebody's data or security."
  - "NorthStar aims to provide complete security and anonymity to any and all clients."
  - "NorthStar will never store anyone's data or security on the cloud" — flagged for honesty review later (current runtime architecture and any future MSP integration must match the claim word-for-word).
- **Candidate Layer 2 fragments Matt floated** (drawn from his 2026-05-25 list):
  - Emergency stop overrides all automation.
  - Every autonomous action logged with actor, time, input, output, outcome.
  - Every reversible autonomous action has a rollback path.
  - Irreversible or high-impact actions require explicit human approval.
  - Tenant isolation is sacred; customer data never crosses tenants.
  - Least privilege by default.
  - Fail closed, not open.
  - Suspicious / untrusted / adversarial updates require human review before activation.
  - Production deployments and policy changes require signed approval and traceable change control.
  - Human approval required for high-risk, external, or client-facing actions.
  - No secret material in prompts, logs, or model-visible memory.
  - Exceptions are time-bound, documented, reviewed.
- **Tonal hazard (already raised):** Bible-voice contaminating outreach-voice. Whatever gets drafted later, the Shield Bible cannot drift into LinkedIn-style language ("what we thrive for", "unbreakable", marketing positivity).
- **Tonal hazard (added today):** Borrowed-from-the-internet "core values" templates ("Uncompromising Integrity", "Zero-Trust Accountability", "Privacy & Client-First Confidentiality", "Relentless Continuous Learning") are explicitly **not** the path. NorthStar's bibles must be unique to this build, not a generic cybersecurity values poster.

### Trigger conditions for un-deferring

Open the bibles only when **at least one** of the following is true:

1. A NorthStar revolution moment has happened — a new capability, customer category, or swarm property exists that the distributed constitution cannot describe.
2. Five real MSP discovery conversations have produced specific commitments NorthStar wants to make publicly. Then the Shield Bible drafts itself from real promises rather than from speculation.
3. The agent registry has expanded to a size where "constitution governs swarm" is mechanically testable rather than prophylactic.
4. A signed §11 spec needs a value-level rule that cannot be cleanly placed in the existing distributed constitution. That spec then triggers a corresponding bible append, not a full draft.

When any of those fire: do not draft from a generic template. Use the Layer-1 / Layer-2 architecture above and let the trigger event populate it.

---

## The two bibles, in Matt's framing

### 1. Agent Bible — what the swarm lives by

> "something they will live by ... this concept of an idea will make our swarm so much more intelligent and disciplined"
>
> "this is truly my experiment on the limits of ai and swarms ... i am going to see what we can all do and where the limits are"
>
> "if my hunch is correct on the intelligence of the ai and swarms than this bible idea will be one of the best ideas of this build"

**Frame (Matt's):**
- A constitution, not technical documentation.
- Faces inward — governs the colony.
- Experimental hypothesis: agents given a real constitution will display more intelligent AND more disciplined behavior than agents given only individual specs. This is a research-shaped claim, eventually testable once the bible is in force and the agent registry is large enough to compare against.
- Lives at a layer above any single spec — every spec must answer to the bible, not the other way around.

### 2. NorthStar Security Shield Bible — what we stand for

> "the northstar security shield bible will be what we stand for what we thrive for and what we are thriving towards"
>
> "like an unbreakable document of our morals and values that we can stand by and be trusted for"

**Frame (Matt's):**
- Morals and values, not features or marketing copy.
- Faces outward — the trust covenant with customers, partners, and the public.
- Identity document: who NorthStar is, what it refuses to do, what it commits to upholding regardless of commercial pressure.
- "Unbreakable" — the standard the company is held to, by itself, even when nobody is watching.

---

## What this spark deliberately does NOT include

- No candidate commandments.
- No proposed values.
- No structure, formatting, section list, length, or governance hooks.
- No prioritization between the two bibles.

These are all Matt's to design. Anything pre-populated here would shape the outcome and undermine the experiment.

---

## Possible raw material (for Matt's reference, not prescription)

When Matt decides to draft, the bibles may draw on existing material — but neither should be a re-skin of these. The bibles sit above them.

- `VISION.md` — current outward-facing positioning (raw material candidate for Shield Bible)
- `PROJECT_HANDSHAKE.md` — current discipline norms (raw material candidate for Agent Bible)
- `4. Product_Roadmap/*.md` — signed §11 deep-dive specs (existing constraints every agent already respects)
- `core/orchestrator/registry.py` — where Agent Bible compliance would eventually be mechanically enforced
- `audit_tools/decision_audit_runner.py` — the governance gate the bibles would integrate with
- `audit_tools/pre_ship_audit.py` — the enforcement surface that would check bible compliance on every change

---

## Suggested tomorrow path (Matt's call to accept or reject)

1. Open this file. Decide if the spark still resonates in daylight, or if it was an 11 PM thought that doesn't survive the morning.
2. If yes: write a Decision Auditor packet — *"Should NorthStar produce two reference bibles, on what timeline, with what governance treatment, and which one is drafted first?"*
3. Let the audit verdict shape the design.
4. Then — and only then — begin drafting. Matt leads the structure.

Tomorrow's actual first move remains the cheaper-proof headers. The bibles are not the gate. The proof is.

---

## Why this file exists at all

Late-night ideas usually die overnight. The disciplined response to "I don't want to lose this" is to capture it in writing in a clearly-marked unsigned location — not to start building, and not to extinguish the spark. This file is the holding pattern. Nothing more, nothing less.
