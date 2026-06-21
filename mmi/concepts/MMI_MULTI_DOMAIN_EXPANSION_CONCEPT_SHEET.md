# MMI MULTI-DOMAIN EXPANSION — CONCEPT SHEET

**Status:** CONCEPT / NOT AUTHORITY / NOT A DIRECTION DECISION
**Captured:** 2026-06-21
**Filed by:** Matt Nichol June 21st 2026
**Authority level:** Owner concept input — strongest-signal exploration, not selected path
**Boundary:** This is a future-direction concept sheet. It selects nothing, authorizes
nothing, and changes no current build. Email / Inbox Shield remains domain one and the
current build focus. Nothing here is §11-signed doctrine.

---

## 1. The Core Thesis (kept wide on purpose)

The thing being built is not "an email fraud product." The thing being built is a
**domain-agnostic governed multi-agent intelligence layer** — a system that can take a swarm
of AI/automated agents and let them build, operate, verify, and protect a complex system
*without the whole thing drifting into a compromised, unaccountable, or dishonest state.*

Email fraud defense (Inbox Shield) is **domain one** — the first real-world thing MMI is
pointed at, and the proving ground. It is not the identity. It is the first instance of a
general capability.

The general capability, stated as wide as it honestly goes:

> MMI is an evidence-first, human-authority-held governance brain for any safety-critical or
> integrity-critical multi-agent system — one that preserves truth, detects drift, classifies
> evidence, protects authority, verifies before acting, and keeps a human holding every
> consequential lever. The domain it watches is interchangeable. The governance is the product.

Deliberately **not narrowed**: this is not "MMI for cybersecurity." Cybersecurity is one
arena. The thesis is broader — *governed multi-agent integrity for any system where drift,
silent failure, or unaccountable autonomy is dangerous.* That includes domains not yet named.

---

## 2. Why This Thesis Is Credible (not just ambition)

The architecture already mirrors how the most safety-critical physical systems on earth
protect their integrity. The same governance pattern appears independently in:

- **Automotive security** — signed-config verification before OTA updates apply; domain
  isolation / firewalled gateways so one subsystem can't command another; behavioral-baseline
  drift detection; human/sandboxed authority over safety-critical commands.
- **Aircraft avionics** — partitioned systems, formal verification, no single component
  trusted to self-certify.
- **Medical device firmware** — signed updates, verified-against-spec before activation,
  human-in-the-loop for consequential action.
- **Industrial control systems (ICS / SCADA)** — baseline behavioral monitoring, change
  control, authority separation.

MMI was not copied from these. It arrived at the same discipline because **all integrity-
critical multi-agent systems converge on the same governance laws.** That convergence is the
evidence the thesis is real: the pattern is general, so the engine that implements it is too.

---

## 3. Domain Map (wide — a landscape, not a shortlist)

Domains are recorded as *candidates the general capability could one day serve*, ranked only
by rough reachability, not by commitment. None is selected.

### Domain One — CURRENT / PROVING GROUND
- **Email fraud defense (Inbox Shield)** — MSPs / SMBs. The build in progress. The first
  proof. Must be finished and shipped before any branch. Funds and validates everything.

### Near-Future Candidate Domains (reachable, lower barrier)
- **Connected homes / smart buildings / property security** — multi-device systems (cameras,
  locks, sensors, hubs, HVAC, energy) needing drift detection, verify-before-act, human-held
  authority. *Closest adjacent branch:* reachable through the existing MSP channel, since MSPs
  and SMBs increasingly manage physical / building security. Stakes real but not life-safety-
  certified. **Strongest near-future second-domain candidate.**
- **Small-business operational systems** — POS, access control, inventory, IoT fleets. Same
  governance need, same MSP buyer.
- **Other AI-agent build pipelines** — using MMI to govern *other people's* agent swarms
  building software (the most literal generalization: MMI as a governance layer sold to teams
  who build with AI agents and need them not to drift). Possibly the purest expression of the
  thesis.

### Aspirational / Long-Horizon Domains (high barrier, years out, partners/funding needed)
- **Vehicles / automotive cybersecurity** — real structural fit, but brutal entry: ISO 21434,
  multi-year OEM certification, Tier-1 supply chains, life-safety liability. Keep as a someday
  destination, *not* something to architect toward specifically now.
- **Aviation / avionics, medical devices, industrial control** — same fit, same or higher
  barriers. Aspirational. Recorded to keep the thesis wide, not to chase.
- **Critical infrastructure / energy grid / utilities** — extreme fit, extreme barrier.
  Furthest horizon.

### Open / Unnamed Domains
- Deliberately left open. The thesis is domain-agnostic; the right domain N may be something
  not yet listed. The concept must not be narrowed to the domains imagined today.

---

## 4. The One Discipline This Concept Imposes NOW

Whether or not any branch ever happens, the thesis pays off as a **single architectural
discipline applied to current work**:

> **Build the MMI governance core as if it will govern a system not yet named.**

- The governance engine (Estimator, Architect, Superintendent, PM, dispatcher, handoff log,
  drift / contradiction detection, evidence gating) must have **no email-fraud assumptions
  baked into the core.** It governs *a build*; it must not assume the build is a detector
  swarm.
- Domain-specific logic (what email fraud *is*, what a phishing signal *means*) lives in a
  **separate, pluggable domain layer** that sits on top of the generic governance core.
- If this separation holds, branching to a new domain costs a **plug-in layer**, not a rebuild.
- If it does not hold — if email assumptions leak into the core — every future branch means
  tearing the engine apart.

This is the only thing the concept changes about today. Everything else stays the course.

---

## 5. Sequencing (how a branch happens honestly, when it happens)

Strict order. No domain-two work begins before domain one is proven.

1. **Finish & ship Inbox Shield (domain one).** Email need not excite the owner — it must be
   *finished*, because a governance engine that never governed a real shipped product is just a
   clever design. Domain one is the proof that makes any branch credible.
2. **Onboard a real tenant.** MMI governs a real product end to end, with a real customer.
   This is the moment "MMI works" stops being a claim and becomes evidence.
3. **Keep the core domain-clean throughout** (Section 4).
4. **Prove domain-agnosticism cheaply.** Before any serious branch, point MMI at *one* second
   build problem — ideally connected-home / property, reachable through the existing channel —
   and watch it govern that too with minimal core changes. This is the experiment that turns
   "MMI is bigger than email" from feeling into evidence.
5. **Then branch deliberately**, domain by domain, near-future first (homes), aspirational
   later (vehicles), each as its own evidenced decision — never a flight from boredom, never
   off a single conversation.

---

## 6. Dangerous Assumptions To Avoid

- **"Bored of domain one = domain one is wrong."** Boredom is about owner attention in the
  unglamorous finishing phase, not about product value. The boredom returns in every domain.
  It is not a direction signal.
- **"Structural resemblance = should become that domain."** MMI resembling automotive security
  does not mean branch to cars. It resembles *all* integrity-critical systems. Resemblance is
  validation of the thesis, not a destination.
- **"Interesting domain = next domain."** Chasing the exciting domain is a treadmill; the
  finishing-phase boredom recurs everywhere. The next domain is chosen on reachability and
  proof, not novelty.
- **"This concept = a direction decision."** It is not. It is captured signal. Selecting any
  branch is a separate, future, evidenced, §11-gated decision.
- **Narrowing the thesis to today's imagined domains.** The capability is general; domain N
  may be unlisted. Keep it wide.

---

## 7. What Must Remain Open

- The final identity of MMI — still not named, by design, until the system has governed enough
  for there to be something real to name.
- Whether MMI is ultimately a *product feature* (governance for Inbox Shield), a *standalone
  product* (governance engine sold on its own), or a *platform* (governance for others' agent
  swarms). All three remain live.
- Which domain is actually two, three, N. Homes is the strongest near-future candidate, not a
  locked choice.
- Whether vehicles / aviation / medical / infrastructure are ever entered at all.

---

## 8. One-Line Capture

> MMI is a domain-agnostic, evidence-first, human-authority-held governance brain for
> integrity-critical multi-agent systems. Email fraud is domain one and the proving ground.
> Homes / property is the strongest near-future second domain; vehicles and other safety-
> critical systems are aspirational horizons. The thesis is kept wide on purpose. The only
> action it requires today is: keep the governance core domain-clean. Everything else: finish
> domain one first.

---

## 9. Non-Authority Footer

```
This is a CONCEPT SHEET. It is owner concept input, not authority.
No domain is selected. No branch is authorized. No build changes.
Email / Inbox Shield remains domain one and current focus.
The thesis is intentionally not narrowed.
This is not doctrine, not a success definition, not a direction decision.
Any future branch is a separate, evidenced, §11-gated decision.
AUTH-5 remains blocked. Human authority held throughout.
```
