# Mutant Monkey Testing Lab — Protocol (v1)

**Status:** ACTIVE PROTOCOL — repeatable lab discipline, not a daemon, not an authority.
**Authority note:** The lab produces *evidence* about whether an artifact is strong
enough to move forward. It does **not** decide product direction, repair files,
promote contracts, or change routing. Matt / MMI decide. The lab only tests.

---

## 1. Purpose

The lab tests every concept, contract, build, and promotion against the same frame:

> **Concept → Threat Test → Evidence Test → Market Test → Governance Test → Build Readiness Test → Retest Record**

It protects against three dangers:

- building cool but useless machinery,
- accepting weak specs because they sound intelligent,
- drifting away from the core product: **authenticated deception detection +
  evidence-backed vendor-fraud defense**.

### The clean operating rule

> Every Mutant Monkey concept must either improve **detection, evidence, governance,
> insurance value, or attacker-cost economics**. If it does none of those, it gets parked.

---

## 2. Where the lab attaches (four points)

| Point | When | Output token |
|---|---|---|
| **A. Concept intake** | before a concept becomes a contract | `LAB_VERDICT: ACCEPT \| REVISE \| PARK \| REJECT` |
| **B. Contract review** | before a contract is signed | `CONTRACT_TEST: PASS \| PASS_WITH_WARNINGS \| FAIL` |
| **C. Build validation** | after code is built | `BUILD_LAB_RESULT: PASS \| FAIL \| NEEDS_RETEST` |
| **D. Promotion / release** | before anything is trusted/gated/promoted | `PROMOTION_LAB_RESULT: APPROVE \| HOLD \| REJECT` |

The lab gives MMI better evidence at each point. It never becomes MMI.

---

## 3. The six benches

Every idea/build walks across these benches.

### Bench 1 — Product Truth Bench
> Does this belong in Mutant Monkey?
- Tied to vendor fraud, email deception, cyber-insurance evidence, trust layers, or swarm governance?
- Helps Canadian MSPs / SMBs? Strengthens the Evidence Engine?
- Is it a Defender-replacement trap? Too broad?

### Bench 2 — Threat Intelligence Bench
> What attacker behavior does this help us understand or stop?
- Which attacker tactic does it map to? Helps with *authenticated* deception?
- Detects behavior / payment / geo / identity / evidence drift?
- Could an attacker bypass it? Poison it? Could it create false confidence?

### Bench 3 — Evidence Bench
> Can this produce proof, not just an opinion?
- What evidence does it create? Human-readable? Audit-friendly?
- Can an MSP explain it to a client? Support cyber-insurance docs?
- Is the proof chain reversible/reviewable? Does it avoid guarantee language?

### Bench 4 — Governance Bench
> Does this preserve control, authority, and safety?
- Does it make decisions it should not? Secretly change routing? Bypass operator approval?
- Allow self-approval? Modify files? Create auditor-of-the-auditor recursion? Respect MMI authority?

### Bench 5 — Build Readiness Bench
> Can this be built cleanly without making the project fragile?
- Spec precise? Files named? Dependencies controlled? Tests obvious?
- Exit codes defined? Failure modes listed? Rollback simple? Runs in WSL + GitHub cleanly?

### Bench 6 — Cutting Edge Bench (the elite filter)
> What does this teach Mutant Monkey that normal tools do not know?
- Improves authenticated-deception detection? Catches valid-authentication fraud, not just phishing?
- Strengthens vendor-relationship memory? Improves explainability? Creates insurance-grade evidence?
- Helps MSPs prove what happened? Reduces attacker reuse? Adds a new swarm test case?
- Improves tenant-specific baselines? Makes the system harder to poison?

---

## 4. Lab record format

Every concept/build produces one short lab record under `lab_records/`.

```text
============================================================
MUTANT MONKEY TESTING LAB RECORD
============================================================
Artifact:
Type: Concept | Contract | Build | Promotion | Research
Date:
Operator:
Repo/Branch:
Related Files:

LAB SUMMARY
Product Truth:        PASS | WARN | FAIL
Threat Intelligence:  PASS | WARN | FAIL
Evidence Quality:     PASS | WARN | FAIL
Governance Safety:    PASS | WARN | FAIL
Build Readiness:      PASS | WARN | FAIL
Cutting Edge:         PASS | WARN | FAIL

FINDINGS
[BLOCK]
[WARN]
[INFO]

REQUIRED RETESTS
-

FINAL LAB VERDICT
ACCEPT | REVISE | PARK | REJECT | HOLD

Reason:
```

Over time `lab_records/` becomes the lab notebook — how Mutant Monkey thinks, tests,
fails, fixes, and improves.

---

## 5. How the lab fits with MMI

| Layer | Role |
|---|---|
| MMI (`mmi_dispatch.py`) | Decides routing state and authority |
| Testing Lab | Tests whether artifacts are strong enough |
| `verify_build_truth.py` | Checks doc/code truth |
| `detect_drift.py` | Checks cross-artifact drift |
| Scoreboard | Tracks governed maturity |
| Operator (Matt) | Final approval authority |

The lab gives MMI better evidence. It does not become MMI.

---

## 6. Implementation path (anti-overbuild)

- **Phase 1 — Protocol only (this document).** No code. ✅
- **Phase 2 — Apply manually to the next 3 concepts.** First specimen: the Project
  Drift Detector (`lab_records/2026-06-14_project_drift_detector_lab_record.md`).
  Then Tenant Baseline Ingestion, then the next detection-agent contract.
- **Phase 3 — Convert repeatable checks into scripts** only after the manual lab
  proves useful (missing test records, missing evidence paths, invalid commit hashes,
  dirty routing files, signed contracts without scoreboard rows, missing rollback
  sections, missing operator-approval fields). `detect_drift.py` is the first such
  automation and already covers several of these as advisory checks.
- **Phase 4 — Add lab status to the scoreboard:**
  `LAB_STATUS: NOT_TESTED | LAB_WARN | LAB_PASS | LAB_HOLD` (proposal — needs sign-off).
- **Phase 5 — Promote only hard evidence checks into gates:** phantom evidence,
  signed contract with no scoreboard row, missing test record, missing rollback path
  for authority-changing components, self-approval, and money/IAM/alert-suppression
  auto-promotion violations. Everything else stays advisory.

---

## 7. What the lab must NOT become

- a live autonomous swarm / background watcher,
- an automatic file editor or contract promoter,
- an automatic scoreboard updater,
- an auto-gate that blocks on every warning,
- broad "AI critique" with no falsifiable tests,
- a market-research rabbit hole on every small build.

The lab is **sharp, repeatable, and evidence-first**. It reveals; it does not rule.
