# Vendor Payment Verification — Workflow Design Contract (Deep Dive)

**Draft ID:** `MMI_VPV_WORKFLOW_DESIGN_CONTRACT_DRAFT`

**Status:** DRAFT (pre-§11). Advisory placement only — **not** §11 signed, **not** build authorized, **not** scoreboard promotion. Upstream repair lane for `#19` Dual-Approval (MMI-DEC-225 pre-build gate BLOCKED on prior ergonomics-only feedstock).

**Owner:** Matt Nichol

**Lane:** Workflow Design Contract (verification + evidence packet) — distinct from disposition ergonomics sibling.

**Authority repo:** `/home/socialarchitect/northstar`

**Downstream consumer:** `#19` Dual-Approval Agent — consumes §4 `vpv_evidence_packet_v1` (versioned together).

**Source-of-truth links:**
- `4. Product_Roadmap/Vendor_Payment_Verification_Workflow_Ergonomics_Deep_Dive.md` (sibling — human disposition **after** OOB; DRAFT pre-§11)
- `4. Product_Roadmap/Dual_Approval_Agent_Design_Contract_Deep_Dive.md` (#19 — dual-approval requirement from this packet)
- `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` (§11 signed — Tier B banking delta)
- `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` (baseline primitive)
- `4. Product_Roadmap/Two_Channel_Confirmation_Enforcement_Deep_Dive.md` (§11 signed — OOB confirmation presence)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (Evidence Stage §6 naming)
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` (forbidden-language + advise boundary)
- `4. Product_Roadmap/Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Design_Contract.md` (#97 TBI — Tier B baseline governance)
- `4. Product_Roadmap/Cortex_Immune_Interface_Design_Contract.md` (OQ-5 seven-trigger operator approval)
- `core/privacy_filter/` (#93 Privacy Filter — ADVERSARIALLY HARDENED; in-path before baseline broadcast)
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/workflows/vendor_payment_verification.py`

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-26 (upstream repair · MMI-DEC-225 / MMI-DEC-226):

| GAP (advisory draft) | Resolved value | Repo evidence |
|---|---|---|
| **Placement** | `4. Product_Roadmap/Vendor_Payment_Verification_Workflow_Design_Contract_Deep_Dive.md` | All roadmap deep dives + agent contracts live here; runtime under `core/workflows/` |
| **Relationship to ergonomics doc** | **This contract** = verification checks + evidence packet + risk verdict. **Ergonomics sibling** = human disposition recording after OOB. Complementary; not superseded. | Ergonomics §0 defers FSL UI; disposition enum §3 |
| **Tier A engine surfaces** | See §3.1 table — read-only orchestration over existing detectors/workflows | `email_authentication_detector.py`, `lookalike_domain_detector.py`, `header_divergence_detector.py`, `ghost_thread_detector.py`, `callback_phishing_detector.py`, `two_channel_confirmation.py` |
| **Tier B engine surfaces** | `assess_financial_state_delta` + `vendor_baseline.check_signal` + Gap5 TBI (#97 GATED) when authorized | FSL §11 signed; Vendor Baseline Store; `core/tenant_baseline_ingestion/` |
| **Privacy Filter #93** | In-path before any baseline-derived field enters the packet or broadcasts | Scoreboard #93 GOVERNED_AGENT / #98 adversarial hardening |
| **OQ-5 baseline approval** | Above-threshold baseline writes require Matt operator approval (seven triggers per Cortex Immune) | `Cortex_Immune_Interface_Design_Contract.md` §CI; `Safe_Stop_State_Machine_Concept_Doc.md` OQ-5 |
| **Template Evidence Stage naming** | Stage 1 Synthetic / Stage 2 Supervised / Stage 3 Production | Template §6.1 |
| **Legal advise framing** | Inherited from `Compliance_and_Trend_Watch_Process.md` + ergonomics D5/D8 + `VISION.md` | See §10 |

**Remaining open (Matt / sibling specs):**

| Open item | Blocker |
|---|---|
| Ergonomics §10 Q1–Q6 + §11 | Disposition-layer feedstock still UNSIGNED — does not block §4 packet schema but blocks full end-to-end disposition integration |
| Tier B live wiring before TBI + OQ-5 authorization | Stage 1 = Tier A only by design |
| Locked `risk_verdict` threshold policy (ELEVATED vs HIGH) | OQ-2 — product policy |
| Contract §11 signature | Required before build |
| `#19` re-gate | Partially cleared — §4 schema fixed; §11 on both contracts still open |

---

## §0 Purpose — the one invariant

**This workflow verifies a vendor payment request and emits an evidence packet + risk verdict. It never moves, holds, approves, or blocks a payment.** The verdict is evidence — consumed by `#19` and read by a human. It is not a decision and not a guarantee.

Examine vendor payment requests and banking-detail changes, run a fixed set of verification checks, and produce a **Vendor Payment Verification evidence packet** (`vpv_evidence_packet_v1`). That packet is the upstream trigger source for `#19` Dual-Approval — the direct counter to "vendor email, mid-thread, new banking details."

---

## §1 Scope

### In scope

- Orchestrated verification checks (Tier A at ES1; Tier B when baseline governance authorized).
- Closed evidence packet schema (§4) versioned with `#19`.
- `risk_verdict` enum: `CLEAR` \| `ELEVATED` \| `HIGH` (evidence only — not pay/don't-pay).
- Reproducibility metadata (input hashes, engine versions).
- Read-only consumption of §11-signed detectors and workflows.

### Out of scope

- Payment movement, hold, approval, block, or release.
- Making the out-of-band verification call (human/customer action).
- Disposition recording (ergonomics sibling).
- Dual-approval requirement emission (`#19` owns that layer).
- Raw financial strings or PII in the packet.
- Autonomous action or buyer-facing compliance claims.

---

## §2 Locked Design Decisions

- **D1 — Verify-and-evidence only.** Produces verdict + packet; never payment instructions.
- **D2 — Evidence ≠ decision.** Packet feeds `#19` + human; never "pay / don't pay."
- **D3 — Stage 1 default.** Evidence Stage 1 (Synthetic); Tier A checks only until baseline governance authorized.
- **D4 — Schema versioning.** Packet uses `schema_version: vpv_evidence_packet_v1`; any field change requires joint version bump with `#19`.
- **D5 — Read-only detectors.** Workflow orchestrates; does not mutate signed detector logic or Two-Channel write paths.
- **D6 — Privacy Filter in-path.** `#93` filters baseline-derived content before packet assembly or broadcast.
- **D7 — OQ-5 gate on Tier B writes.** Baseline ingestion above defined risk threshold requires operator approval before Tier B fields are populated from live baseline.
- **D8 — Tenant isolation.** One tenant's vendor baseline never bleeds into another.
- **D9 — False-negative severity.** Cleared fraudulent payment change (`CLEAR` when should be `HIGH`) is the highest-severity failure — template §6.5.
- **D10 — No sensitivity floor relaxation.** False-positive tuning never drops checks below agreed floor without signed policy change.

---

## §3 Verification checks

Two tiers, split by data dependency.

### §3.1 Tier A — baseline-free (Stage 1 Synthetic)

| Check | Packet field | Repo engine (read-only) |
|---|---|---|
| Sender authentication (SPF / DKIM / DMARC) | `sender_auth` | `core/scoring/email_authentication_detector.py` |
| Look-alike / mismatched sender domain | `domain_similarity` | `core/scoring/lookalike_domain_detector.py` (`extract_identity_domains`) |
| Thread integrity / reply-chain forgery | `thread_integrity` | `core/scoring/header_divergence_detector.py`, `core/scoring/ghost_thread_detector.py` |
| Urgency / pressure / out-of-band-change language | `urgency_markers` | `core/scoring/callback_phishing_detector.py`; Layer 2 pressure facts by reference (#21) |
| Out-of-band confirmation **presence** | `oob_confirmation` | `core/workflows/two_channel_confirmation.py` — `summarize_confirmation_status` (present/absent/pending; no write) |

### §3.2 Tier B — baseline-dependent (gated)

| Check | Packet field | Repo engine (read-only) |
|---|---|---|
| Banking-detail delta vs known-good vendor | `banking_delta` | `core/scoring/financial_state_ledger.py` — `assess_financial_state_delta` |
| New / unrecognized vendor vs history | `vendor_known` | `core/production_state/vendor_baseline.py` — `check_signal` |
| Payment-pattern anomaly vs baseline | `payment_pattern_anomaly` | Gap5 TBI behavioral signals (`Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Design_Contract.md`) when `#97` authorized |

**Tier B gate:** Privacy Filter `#93` + OQ-5 operator approval for above-threshold baseline ingestion (`Cortex_Immune_Interface_Design_Contract.md`). Until authorized: Tier B fields emit `not_available_at_stage` — workflow still runs Tier A.

---

## §4 Evidence output schema — `vpv_evidence_packet_v1`

**Wire contract to `#19`.** Version together; breaking change = new `schema_version`.

| Field | Type / values | Content | Maps to `#19` trigger |
|---|---|---|---|
| `schema_version` | `vpv_evidence_packet_v1` | Schema lock | version pin |
| `tenant_id` | string | Tenant scope | isolation |
| `finding_id` | string | Upstream finding key | linkage |
| `sender_auth` | closed verdict | SPF/DKIM/DMARC aggregate | auth / domain risk |
| `domain_similarity` | closed verdict + bounded score band | look-alike posture | look-alike domain |
| `thread_integrity` | closed verdict | forgery indicators | reply-chain / thread-forgery |
| `banking_delta` | closed verdict \| `not_available_at_stage` | changed payee details (Tier B) | new/changed banking |
| `vendor_known` | closed verdict \| `not_available_at_stage` | new vs known vendor (Tier B) | new/unrecognized vendor |
| `payment_pattern_anomaly` | closed verdict \| `not_available_at_stage` | baseline anomaly (Tier B) | pattern risk |
| `oob_confirmation` | `present` \| `absent` \| `pending` | separate-channel confirmation evidence | OOB / urgency context |
| `urgency_markers` | closed flags | pressure-language markers | urgency markers |
| `risk_verdict` | `CLEAR` \| `ELEVATED` \| `HIGH` | **Evidence only** — drives `#19` raise logic | `#19` §3.3 |
| `reproducibility` | struct | input corpus hashes, engine versions, run_id | audit / re-run |

### §4.1 `risk_verdict` → `#19` binding (joint policy — draft)

| `risk_verdict` | `#19` behavior (draft) |
|---|---|
| `HIGH` | Raise `dual_approval_required` |
| `ELEVATED` | Raise `dual_approval_required` unless signed policy carves out (OQ-2) |
| `CLEAR` | Emit `dual_approval_not_applicable` from packet — **not** "safe to pay" |

---

## §5 Vendor baseline / tenant-data governance

Tier B checks require known-good vendor records = governed tenant data ingestion.

- **Privacy Filter (`#93`)** — adversarially hardened; in-path before baseline fields enter packet.
- **OQ-5** — operator (Matt) approval above defined risk threshold before baseline ingestion writes (seven triggers per Cortex Immune).
- **Tenant isolation** — per-tenant baseline only.
- **Stage 1** — Tier A only; workflow delivers value before any ingestion is approved.

---

## §6 What the workflow does — and does not

| Does | Does NOT |
|---|---|
| Run checks, emit verdict + evidence packet | Move, hold, approve, or block a payment |
| Feed `#19` and surface to humans | Decide "pay / don't pay" |
| Flag absence of out-of-band confirmation | Make the out-of-band call |
| Log reproducibility metadata for audit | Guarantee legitimacy of any transaction |

---

## §7 Evidence Stages

Per `Agent_Design_Contract_Template_Deep_Dive.md` §6:

| Stage | Data | May do | May NOT do |
|---|---|---|---|
| **1 — Synthetic** *(default)* | Synthetic payment scenarios; **Tier A only** | Verify + emit packet in sandbox | Tenant baseline; touch live payments |
| **2 — Supervised** *(proposed)* | Privacy-filtered real past cases; Tier B with approved baseline | Validate checks vs actual incidents | Live payment systems |
| **3 — Production** *(proposed)* | Live request signal | Emit verdicts on real flow | **Move/approve/block money — never, any stage** |

---

## §8 Failure modes

- **False-negative (dangerous):** fraudulent payment change returns `CLEAR` → permanent regression + demotion (heaviest Health Score weight).
- **False-positive:** legit payment flagged `HIGH` → friction; tune only with signed policy — never silent sensitivity drop.
- **Enactment creep:** any hold/approve/block path → hard fail.
- **Schema drift:** `#19` consumes different shape than §4 without version bump → hard fail.
- **Privacy leak:** raw financial strings / PII in packet → hard fail.
- **Tier B without OQ-5:** populating baseline fields from unauthorized ingestion → hard fail.

---

## §9 Hard limits

- **No money-movement / block / approval path** — by construction.
- **AUTH-5 blocked.** Safe-Stop (Matt-only) halts the workflow.
- **Verdict is evidence, not authorization** — human + `#19` downstream.
- Scoreboard evidence label update deferred until Matt §11 + explicit reconcile.

---

## §10 Legal / non-guarantee

Money-loss surface. Binding posture:

- Workflow **advises via evidence**; does not guarantee transaction legitimacy.
- Customer retains decision + liability.
- `CLEAR` verdict is **not** payment authorization.
- Forbidden-language: `Compliance_and_Trend_Watch_Process.md`.
- Shares `#19` legal-scoping prerequisite — resolve together before either §11.

---

## §11 Sign-off

```
§11 — Vendor Payment Verification Workflow Design Contract (Deep Dive)
Authority: Matt Nichol (sole signer)
Signature: __________________________   Date: __________
[UNSIGNED — advisory lane; pre-build gate not run; not build authorization]
```

---

## §12 `#19` re-gate hook

Once this contract lands and §4 schema is fixed:

1. `#19` §3 triggers bind to §4 field set (`vpv_evidence_packet_v1`) — **done in draft re-gate 2026-06-26**.
2. `#19` §3.2 upstream schema replaced by this packet — versioned together.
3. MMI-DEC-225 VERIFY item "Vendor Payment Verification reconciliation" → **partially cleared** (packet layer); ergonomics §10 Q1–Q6 remain for disposition integration.
4. Re-run `#19` pre-build gate after Matt §11 on this contract OR explicit carve-out recorded.

---

## §13 Open questions (operator-only)

- **OQ-1 — ELEVATED handling:** Does `ELEVATED` always raise dual-approval, or only `HIGH`?
- **OQ-2 — Tier B promotion:** Which OQ-5 triggers unlock Tier B for a given tenant?
- **OQ-3 — Ergonomics integration:** How does disposition enum relate to packet `risk_verdict` without conflating evidence and human outcome?
- **OQ-4 — Runtime packaging:** Single `vendor_payment_verification.py` module vs orchestrator agent wrapper — decide at build authorization.

---

## Execution checklist (post-§11 — not authorized in this slice)

1. Matt §11 on this contract (jointly scoped with `#19` legal §10).
2. Codex pre-build gate — adversarial focus: **can an attacker craft a payment change that returns `CLEAR`?**
3. Re-run `#19` pre-build gate with `files_read` including this contract.
4. Operator build authorization → `core/workflows/vendor_payment_verification.py`.
5. Re-gate `#19` build after workflow ES1 exists.
6. Closeout: `lane_board_sync` → `dispatch --verify` → `pmv`.
