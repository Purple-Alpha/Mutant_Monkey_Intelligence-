# MMI CONCEPT ADDENDUM: EXECUTIVE PERIMETER ATTACK SURFACE MANAGEMENT (ASM)

**Document Reference:** MMI-CON-2026-06-22

**Status:** CONCEPT ONLY / NOT AUTHORIZED FOR BUILD

**Domain Association:** Bridge track (Domain 1 → Domain 2)

**Filed by:** Matt Nichol (concept capture)

**Sibling concept:** `mmi/concepts/MMI_MULTI_DOMAIN_EXPANSION_CONCEPT_SHEET.md` — this addendum narrows the *bridge* path only; it does not replace or supersede the parent sheet.

**Boundary:** This is a future-direction concept addendum. It selects nothing, authorizes nothing, and changes no current build. Email / Inbox Shield remains domain one and the current build focus.

---

## 1. Objective & Strategic Intent

This addendum establishes the conceptual framework for the **Executive Perimeter**, serving as the non-disruptive narrative and architectural bridge between **Domain 1 (Inbox Shield)** and **Domain 2 (Connected Homes / Property Security)**.

Instead of forcing a premature physical-world integration (which introduces heavy regulatory and hardware dependencies), this track targets the **identity and API access layer** of High-Net-Worth Individuals (HNWIs) and corporate executives. It leverages existing Stage A identity detectors to map and secure physical assets (smart homes and vehicles) via their cloud ecosystems, without writing domain-specific firmware or hardware integration code.

**Strategic placement (plain English):** MMI is not positioned as a cleanup crew behind Microsoft Defender. It is positioned as a **governed scout layer** on the identity/API perimeter — intercepting targeted credential, token, and MFA-abuse patterns **before** they become opaque tenant alerts or autonomous vendor actions.

---

## 2. The Identity Cross-Over (The Shared Attack Surface)

Securing an executive's personal perimeter relies on the same detector *classes* currently exercised in the Stage A laboratory stack. Physical assets (smart hubs, luxury vehicles) are attacked primarily through upstream credential, token, and API vulnerabilities — not by cracking tire-pressure sensors at the roadside.

```text
              [ MMI GOVERNANCE CORE ]
    (Decision log, Safe-Stop, signed specs, completion gates)
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
  [ DOMAIN 1: EMAIL ]          [ BRIDGE: EXECUTIVE ASM ]
  - Ghost thread detection     - Session token hijacking
  - Lookalike domain spoofs    - OAuth telematics app abuse
  - Corporate inbox vectors    - Smart-home gateway API exploits
```

### Shared detector alignment (illustrative — not new build scope)

| Scoreboard / pattern | Email (Domain 1) | Executive perimeter (bridge narrative) |
|---|---|---|
| MFA fatigue (#24) | Push fatigue against corporate MFA gateways | Fraudulent auth pushes to mobile apps controlling locks, gates, or vehicle companion apps |
| Credential phishing (#23) | Harvest corporate login flows | OAuth/token theft on personal devices → enterprise vaults **and** vehicle/home cloud APIs |
| Lookalike / impersonation (#10, #21) | Vendor and executive BEC | Spoofed identity around wealth portals, telematics vendors, IoT account recovery |
| API / webhook abuse (future domain layer) | Misconfigured mail rules and ingress | Cloud webhooks and vendor APIs as single points of control for connected property |

This table is **conceptual mapping only**. It does not authorize new agents, registry wiring, or production dispatch.

---

## 3. Strict Repo & Boundary Enforcement

> ### CRITICAL GOVERNANCE BOUNDARY
> This document does **not** authorize a codebase fork or a new development branch. The following guardrails remain locked under MMI governance discipline:

1. **Zero asset-specific code:** No automotive telematics parsers, CAN bus logic, smart-hub LAN discovery, or physical device APIs in the current build path.
2. **Commander abstraction only (future build decision):** When **#1 Swarm Commander** is built and gated, generic routing may accept a declared **asset type** or equivalent case-context field (e.g. inbox tenant vs cloud API endpoint) — **only** via a narrow §9 build decision and signed routing-policy annex. This addendum does **not** authorize that encoding by itself.
3. **Depth gate maintained:** The depth gate remains **CLOSED**. This bridge track operates on synthetic lab models only. No real-world executive tenant onboarding is authorized.
4. **No default registry promotion:** Bridge narrative must not add Executive ASM agents to `build_default_registry` or production dispatch without separate §11 + build authorization.
5. **Finish Domain 1 first:** Per `MMI_MULTI_DOMAIN_EXPANSION_CONCEPT_SHEET.md` §5 — ship domain one, prove governance portability, then branch deliberately.

### Stacked scoring & verification — no shortcuts

This bridge track does **not** relax MMI discipline. When any slice touches Executive ASM narrative, Domain 1 build, or Command spine work, apply **all** layers that apply — no exceptions, no "good enough" bypass:

- Scoreboard lifecycle + Build Sequencer candidates
- Next-Action Rubric ranking (Matt selects; rubric does not authorize)
- Signed §11 contracts + pre-build contract gates where required
- Implementation tests + Agent Health Score pins where governed
- Completion gate at readiness boundaries (`complete_gate.py`)
- Decision log receipt (`MMI-DEC-*`) + `mmi_dispatch.py --verify` after routing-authority commits
- Estimator / PM Voice posture reads (advisory only)

**Forbidden:** treating this concept sheet as build authorization; skipping gates because the work "feels conceptual"; ad-hoc scoring invented outside existing engines (`AGENTS.md` §3.1 rule 7).

---

## 4. Next Mechanical Actions in Repo (sequential — not authorized by this addendum)

To prevent vision drift from contaminating the build default registry, execution priority remains strictly sequential:

1. **Complete the Command spine:** Build and gate **#1 Swarm Commander** (`SIGNED_UNBUILT`, MMI-DEC-110 reconcile complete; **build not authorized** until Matt names `#1 build`). **#2 Mission Context** is **GATED** (MMI-DEC-109); **#3 Risk Triage** contract signed, not build-authorized.
2. **Generic routing policy (when #1 build is authorized):** Encode asset-type / endpoint abstraction as a narrow §9 build decision inside the Commander implementation — domain-agnostic routing by design, not a Domain 2 product launch.
3. **Archive this concept:** This file remains a static markdown artifact under `mmi/concepts/` to govern future design intent. Day-to-day engineering cycles stay on Domain 1 shippable core until a separate evidenced branch decision.

---

## 5. What This Addendum Does Not Do

- Does not compete with Microsoft on signature volume or tenant-native scale.
- Does not authorize Executive ASM product, MSP packaging, or HNWI onboarding.
- Does not open automotive OEM, ISO 21434, or smart-home hardware certification paths.
- Does not modify Estimator, dispatcher, PM Voice, or scoreboard lifecycle by itself.
- Does not replace Inbox Shield as domain one or rename the active project identity.

---

## 6. One-Line Capture

> Executive Perimeter ASM is the **identity/API bridge narrative** from Inbox Shield to connected-home property security — same attack classes, different asset labels — with **zero** physical-world code until domain one ships and governance is proven portable.

---

## 7. Non-Authority Footer

```
This is a CONCEPT ADDENDUM. It is owner concept input, not authority.
No domain is selected. No branch is authorized. No build changes.
Email / Inbox Shield remains domain one and current focus.
Command spine completion (#1 GATED) precedes any asset-type abstraction work.
This is not doctrine, not a success definition, not a direction decision.
Any future Executive ASM product lane is a separate, evidenced, §11-gated decision.
AUTH-5 remains blocked. Human authority held throughout.
```
