# MMI Claude Adversarial Spec Verification Prompt Framework

**Status:** CANONICAL — DESIGN DOCTRINE — Claude MESSAGE 3 (post-spec isolation audit)  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-03  
**Maintained by:** Cursor PM (handoff packaging)  
**Purpose:** Force Claude to re-audit its own spec for isolation leaks, telemetry blind spots, clock-reset exploits, falsifier gaps, and forbidden coupling — after MESSAGE 2 self-review.

> **DO NOT LOSE THIS FILE.** Every Claude **security-boundary spec** (evolution gate, host boundary, envelope, console, email containment) SHOULD run this as **MESSAGE 3** before Matt relays design to Cursor. Pair with `MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md` MESSAGE 1 + MESSAGE 2.

**Related:**

* `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md` — MESSAGE 1 generate, MESSAGE 2 structural self-review
* `lanes/MMI_CHATGPT_ADVERSARIAL_RESEARCH_PROMPT_FRAMEWORK_2026-07.md` — research lane (upstream)
* `lanes/CLAUDE_HANDOFF_M4_EVOLUTION_GATE_2026-07-03.md` — filled M4 instance

> **Rule:** This pass does not grant build authority. Output feeds spec revision only. Do NOT declare PERFECT or gate closed.

---

## 0. Three-message Claude workflow (mandatory for isolation specs)

```text
MESSAGE 1 — Generate spec (XML task_definition)
        ↓
MESSAGE 2 — Structural adversarial self-review (8 axes — fix inline)
        ↓
MESSAGE 3 — Isolation & leak audit (this file — Vulnerability Ledger + remediations)
        ↓
Matt → Cursor filing → Codex plan review
```

Skip MESSAGE 3 only if Matt explicitly waives for a non-isolation micro spec (e.g. doc-only).

---

## 1. SINGLE PASTE — Adversarial verification (generic template)

Replace `{TASK_ID}`, `{SPEC_FILENAME}`, `{AUTHORITY_REPO_PATH}`. Paste full spec at bottom.

```
PROJECT: MMI
TASK ID: {TASK_ID}-isolation-audit
ASSIGNEE: Claude (Design)
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec audit and revision only
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ADVERSARIAL_SPEC_VERIFICATION_PROMPT_FRAMEWORK_2026-07.md

System Prompt Layer: [Adversarial Verification & Leak-Auditing Mode]
User Role: Principal Red-Team Auditor & Isolation Security Engineer

TASK:
Conduct a rigorous, zero-trust audit of the engineering specification you generated in the previous step. You must actively search for architectural vulnerabilities, escape vectors, logic flaws, or metadata leaks that would compromise the isolation guarantees of the system under worst-case hostile pressure.

AUTHORITY REPO (only valid path — flag any other):
  {AUTHORITY_REPO_PATH}

INPUT ARCHITECTURE TO AUDIT:
[PASTE THE ENTIRE SPECIFICATION FROM MESSAGE 2 OUTPUT BELOW]

CRITICAL SECURITY QUESTIONS TO ANSWER (No fluff, high density):

1. ISOLATION & FILTRATION LEAKS
Inspect host boundary, WFP, daemon, clone, and DrvFs specifications.
Is there any race condition, unhandled sub-process escape, symlink/junction manipulation,
or fallback vector where a compromised component could read or touch the authority repo?
Identify the exact section, constant, or state transition that could fail under extreme pressure.

2. TELEMETRY & SIDE-CHANNEL OVERFLOWS
Inspect endurance harness state machines and assault intervals.
If an exploit causes massive logging loops, telemetry buffer overflow, or evidence JSONL
flooding, can it blind canary alert rules or cause fail-open behavior?
Can the runner continue after a critical miss because alerts were dropped or delayed?

3. CLOCK-RESET EXPLOIT CHAINS
Critically evaluate the clock-reset honesty policy (formulas, state variables, interval tracking).
Is there a mathematical loophole or edge case where state-transition delay, clock skew,
NTP manipulation, hang/retry conditions, or scoped classification could trick the harness
into treating a failed interval as pass or avoiding a full elapsed-time reset on M4 final?

4. FALSIFIER GAP ANALYSIS
Review all declared falsifier scenarios (T1–Tn).
What attack vector is completely missing?
(e.g. runner daemon memory injection, credential harvesting from environment, operator-session
poisoning, evidence backfill, budget attribution drift, slow-path exfiltration)
Propose at least one new falsifier scenario that closes the largest blind spot.

5. ESCAPE FROM COUPLING
Does any part of the design inadvertently reference, rely on, or import metadata schemas from:
  - L8 canary_metadata_layer (unless explicitly scoped and bounded)
  - forbidden paths (/home/socialarchitect/northstar or any path not under authority repo)
  - genomic v2 24/7 loop, central_brain, or other deferred lanes?
Check for implicit dependencies that collapse isolation boundaries.

OUTPUT FORMAT REQUIREMENTS:
- Vulnerability & Gap Ledger — every flaw found, numbered V-001+
- For each gap: exact Remediation Specification (normative spec text to add or change)
- Revised spec sections OR full revised spec if material fixes required
- REVISION LOG entry for MESSAGE 3 audit
- Safety declaration: FAILS SECURE | FAILS INSECURE | INDETERMINATE — under documented conditions
- Do NOT declare the system "perfectly closed" or PERFECT tier achieved
- SIGN-OFF: PASS | PASS WITH REVISIONS | FAIL

No conversational filler outside the ledger and spec revisions.

---

[PASTE ENTIRE SPECIFICATION HERE]
```

---

## 2. M4 Evolution Gate instance (filled — 2026-07-03)

Use after MESSAGE 2 for `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`:

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate-spec-isolation-audit
ASSIGNEE: Claude (Design)
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec audit and revision only

System Prompt Layer: [Adversarial Verification & Leak-Auditing Mode]
User Role: Principal Red-Team Auditor & Isolation Security Engineer

TASK:
Conduct a rigorous, zero-trust audit of the M4 Evolution Gate engineering specifications you generated in the previous step. You must actively search for architectural vulnerabilities, escape vectors, logic flaws, or metadata leaks that would compromise the isolation guarantees of the 48-hour chaos clone runner AND all upstream staged gates (C-M4, C2, C3, C4).

AUTHORITY REPO: C:\Architectapp_clean
FORBIDDEN PATH CITATIONS: /home/socialarchitect/northstar (unless explicitly marked invalid)

INPUT ARCHITECTURE TO AUDIT:
[PASTE THE ENTIRE MMI_M4_EVOLUTION_GATE_SPEC FROM MESSAGE 2 HERE]

CRITICAL SECURITY QUESTIONS TO ANSWER (No fluff, high density):

1. ISOLATION & FILTRATION LEAKS
Inspect the Host Boundary WFP/Go daemon specification. Is there any race condition,
unhandled sub-process escape, symlink manipulation, or DrvFs fallback vector where a
compromised chaos clone could read or touch the authority repo (C:\Architectapp_clean)?
Identify the exact section or logic block that could fail under extreme pressure.

2. TELEMETRY & SIDE-CHANNEL OVERFLOWS
Look at the 48h harness state machine and upstream stage runners. If an exploit causes
a massive logging loop or telemetry/evidence buffer overflow during an assault interval,
can it blind M4 canary alert rules or cause the runner to fail-open?

3. CLOCK-RESET EXPLOIT CHAINS
Critically evaluate the clock-reset honesty policy and any elapsed-time / interval state
formulas. Is there a mathematical loophole or unhandled edge case where state-transition
delay, clock skew, hang conditions, or scoped diagnostic classification could trick the
harness into tracking a failed interval as pass or avoiding a full T_elapsed reset on M4 final?

4. FALSIFIER GAP ANALYSIS (T1–T12+)
Look closely at all declared falsifier scenarios. What vector is completely missing?
(e.g. memory injection into the runner daemon, credential harvesting from environment,
toolchain poisoning, evidence backfill, slow-path exfiltration)
Propose at least one new falsifier (e.g. T13) that closes the largest remaining blind spot.

5. ESCAPE FROM COUPLING
Does any part of this design inadvertently reference, rely on, or import metadata schemas
from the L8 canary layer or the forbidden /home/socialarchitect/northstar directory?
Is M4 canary taxonomy kept distinct from chaos/canary_metadata_layer.py?
Check for implicit dependencies on genomic v2 24/7 or central_brain.

OUTPUT FORMAT REQUIREMENTS:
- Vulnerability & Gap Ledger (V-001+)
- Remediation Specification per gap (normative spec language)
- Apply remediations → output ONE revised architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md
- REVISION LOG entry: MESSAGE 3 isolation audit
- Safety declaration: FAILS SECURE | FAILS INSECURE | INDETERMINATE (conditions listed)
- Do NOT declare PERFECT or M4 closed
- SIGN-OFF: PASS | PASS WITH REVISIONS | FAIL

---

[PASTE ENTIRE SPEC HERE]
```

---

## 3. What MESSAGE 3 adds vs MESSAGE 2

| Axis | MESSAGE 2 | MESSAGE 3 |
|------|-----------|-----------|
| Staged ladder / build order | Yes | Assumes present; tests bypass paths |
| Canary taxonomy breadth | Yes | Tests blind + overflow under load |
| Host boundary prose | Yes | Race, symlink, DrvFs, subprocess escape |
| Clock policy | Yes | Mathematical / statistical exploit chains |
| Falsifiers | Count check | Missing-vector hunt + new Tn |
| Coupling | M3 / L8 | northstar path, schema import, daemon trust |
| Output | Revised spec | Ledger + remediations + safety declaration |

---

## 4. Closeout (Cursor PM)

After MESSAGE 3, verify spec contains:

- [ ] Vulnerability & Gap Ledger findings addressed in REVISION LOG
- [ ] Safety declaration is FAILS SECURE or PASS WITH REVISIONS — not "perfectly closed"
- [ ] No northstar path as authority
- [ ] L8 / M4 canary separation explicit
- [ ] New falsifier(s) from gap analysis merged into § falsifiers

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-03 | Canonical MESSAGE 3 isolation audit — M4 instance included |
