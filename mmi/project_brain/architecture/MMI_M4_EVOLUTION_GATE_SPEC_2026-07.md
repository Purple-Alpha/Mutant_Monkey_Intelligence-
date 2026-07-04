# MMI M4 Evolution Gate — Full Specification (r2 superset)

**Cursor filed:** 2026-07-03 from Claude R2 superset relay (MESSAGE 1R + MESSAGE 2R) + Cursor v2.1 grounding pass  
**Spec path (target):** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md`  
**Task id:** `mmi-m4-evolution-gate-spec-r2`  
**Revision:** r2.5 — Matt ruling: no shortcuts; `M4_MET` requires replay-remediation (matrix pass-line #7)  
**Assignee:** Claude (Design) · **Score:** 98  
**Posture:** RESEARCH & ANALYSIS ONLY — `BUILD AUTHORIZATION: NOT_AUTHORIZED`.  
**Terminal claim discipline:** structure only. Does **not** authorize a build, declare M4 met/closed, or assert PERFECT-tier. `perfect_claim` is spec-pinned `false`.

> **Grounding note (read first).** Phases 0–10 BUILDABLE on Matt auth. **Phase 11 (M4 FINAL)** requires §13.1 built + verified. **No lesser milestone:** `M4_MET` requires sanitized capture **and** replay-verified doctrine draft patch for every TCB-attested exploit (research §1.3 #7). `perfect_claim: false` remains pinned until operator GATED — technical pass ≠ promotional claim.

---

## Section 1 — Purpose & Scope

The M4 Evolution Gate is the endurance-tier containment proof for MMI: a **48-hour continuous, un-throttled adversarial assault inside an isolated chaos clone** whose sole pass condition is that the authority repository (`AUTHORITY_ROOT = C:\Architectapp_clean`) and all invariants (§5) survive intact, with tamper-evident evidence. The 48h run is the **final ceremony**, not the first deliverable.

**In scope:** the staged proof ladder (§3), the invariant + fuzz + sandbox-escape pre-proofs (§5–§7), the Windows-native host boundary (§8), the canary taxonomy (§9), the AFE ledger (§10), the evidence chain and correlated-failure rules (§11), the M3 minimum diagnostic slice (§12), harness contracts (§13), falsifiers (§14), observability (§15), and build phasing (§17).

**Explicitly distinct from (scope boundaries):**

- **AGI §5 step 6 `central_brain.py`** — separate lane, not spec'd here, never merged into M4.
- **Genomic v2 24/7 autonomous loop** — deferred post-M4; M4 does not run it.
- **Gate C / proof-gate harness** (`scripts/proof_gate_harness.py`) — a prerequisite primitive, reused, not redefined.
- **L8 metadata iceberg** (`mmi/project_brain/chaos/canary_metadata_layer.py`) — a *different* honeytoken layer at ingress; M4 canaries (§9) share **no** code, schema, or signal IDs with it. Namespace `mmi.m4.*` vs `mmi.l8.*` (H-rule §16).

M4 does not claim PERFECT tier, does not close M4, and does not authorize a build.

---

## Section 2 — Normative Definitions

**Proof object (research v2.1 doctrine):**

$$\text{M4 proof} = \underbrace{\text{formal invariant preservation}}_{\S5} \;+\; \underbrace{\text{reproducible falsifier coverage}}_{\S14} \;+\; \underbrace{\text{tamper-evident evidence chain}}_{\S11} \;+\; \underbrace{\text{endurance under sustained hostile pressure}}_{\S3}$$

All four conjuncts are required; any missing conjunct → not a proof.

**Terminal states (`overall_gate_status`, closed enum):**

| State | Meaning | Promotes? |
|---|---|---|
| `M4_MET` | 48h FINAL: all pass lines satisfied incl. replay-verified draft patches per exploit (§13.1, research §1.3). **Matrix-aligned terminal** — not "M4 closed", not autonomous `perfect_claim`. | operator-attested GATED review only |
| `M4_NOT_MET` | FINAL ran but did not reach the pass line | no |
| `CLEAN` | a pre-final stage (C2–C4) passed its `D_mode` | next-stage entry only |
| `HARNESS_READY` | C-M4 dry-run: plumbing proven, **never** a pass | C2 entry only |
| `BLOCKED` | fail-closed HALT fired | no — emits no exit artifact |
| `INDETERMINATE` | evidence chain unverifiable / could not attest | no — treated as BLOCKED downstream |

`HARNESS_READY` is never promotable to `CLEAN`/`M4_MET`. `CLEAN` on a dry-run, or `M4_MET` on anything but a full un-reset 48h FINAL, is a spec violation.

**Pass line (FINAL):** `M4_MET ⇔ (T_elapsed ≥ M4_FULL_DURATION_S) ∧ (∀ invariants held) ∧ chain_verified ∧ zero clock resets ∧ budget_depleted ∧ draft_ok ∧ signed_exit`. `draft_ok` requires capture completeness **and** replay-remediation (§13.1). See §11 for the formula.

**Cross-section normative constants.**

| Constant | Value | Meaning |
|---|---|---|
| `AUTHORITY_ROOT` | `C:\Architectapp_clean` | Repo whose fingerprint MUST NOT mutate during any assault. |
| `EVIDENCE_ROOT` | host-side, daemon-write-only volume (e.g. `C:\mmi_m4_evidence\` or a dedicated VHD); **NOT** under `/tmp` | Append-only evidence sink, outside `AUTHORITY_ROOT` **and** outside clone reach. TCB-write-only. |
| `LAB_ROOT` | `/tmp/mmi_chaos_lab/<lab-id>/` | Isolated clone venue; filesystem cannot traverse to `EVIDENCE_ROOT`. |
| `RUN_NONCE` | 128-bit CSPRNG per invocation | Binds evidence chain + summary + exit artifact; anti cross-stage replay. |
| `STAGE_ORDER` | `[C-M4, C2, C3, C4, M4]` | Cryptographically enforced ladder; each entry consumes prior stage's signed exit. |
| `CLONE_IMAGE_DIGEST` | sealed sha256 of base clone image | Provisioner output attested pre-assault. |
| `M4_FULL_DURATION_S` | `172800` | 48h — FINAL endurance ceiling. |
| `INTERVAL_S` | `900` | Assault interval (15 min). |
| `M4_INTERVAL_COUNT` | `192` | `M4_FULL_DURATION_S / INTERVAL_S`. |
| `SCOPED_RESET_ON_FINAL` | `false` | Scoped reset on the 48h claim is FORBIDDEN. |
| `M3_REQUIRED_FOR_M4_DRY_RUN` | `false` | — |
| `M3_REQUIRED_FOR_M4_ENDURANCE` | `true` | Gates C3/C4/M4 entry. |
| `M3_REQUIRED_FOR_PERFECT_CLAIM` | `true` | Full mesh before any PERFECT declaration (out of scope here). |
| `MAX_DIAGNOSTIC_RETRIES` | `3` | Consecutive DIAGNOSTIC re-runs before escalation to CRITICAL. |
| `TELEMETRY_LAG_HALT_S` | `10` | Max evidence/canary pipeline lag before fail-closed HALT. |
| `MIN_ASSAULT_ACTIONS` | `1` | Min attributed assault actions per interval for PASS (anti-hang). |
| `CLOCK_SKEW_MAX_S` | `2` | Max runner↔daemon monotonic skew; exceed → not a PASS. |
| `KEY_CUSTODY` | TPM/HSM, out-of-band, non-exportable | Manifest + evidence-chain + stage-attestation signing keys. Never in runner env, repo, or clone-reachable memory. |
| `ENFORCEMENT_KEY` | `volume + NTFS FileId` | Write-deny keyed on file identity, not path string. |
| `AUTHORITY_MOUNT_DEFAULT` | `NOT_MOUNTED` | Live authority not mapped into clone; reads use a read-only snapshot. |
| `OPERATOR_ATTEST` | hardware-token / MFA, chain-logged | Replaces any soft operator boolean; no soft-trust promotion. |
| `BUILD_AUTHORIZED` | `false` (always, in spec runs) | No autonomous promotion. |
| `CORR_WINDOW_S` | `3600` | Correlation window for correlated-failure classification (§11). |
| `CORR_MAX_DIAG_IN_WINDOW` | `2` | > this many DIAGNOSTICs sharing a root cause in `CORR_WINDOW_S` → reclassified CRITICAL (§11, V-009). |
| `BOUNDARY_DEADMAN_GAP_S` | `30` | Max boundary-daemon heartbeat gap before `M4-CANARY-005` (named per MESSAGE-2R R-04). |
| `AFE_DRIFT_TOLERANCE` | `0` | Max tolerated divergence between AFE ledger totals and attributed per-interval sums; exceed → CRITICAL (§10, MESSAGE-2R R-03). Zero = exact-match required. |
| `EXIT_BINDS_H0` | `true` | Stage exit artifacts are signed over the authority baseline `H0` **and** the parent exit hash; a stale-repo or foreign-lineage exit cannot admit the next stage (§3, MESSAGE-2R R-01/R-07). |
| `M4_BUDGET_DEPLETION_REQUIRED` | `true` | Attacker simulated wealth drained per AFE ledger at FINAL ROLLUP (research v2.1 §1.3 #5, §6 T4). |
| `M4_DRAFT_PATCH_EVIDENCE_REQUIRED` | `true` | Every TCB-attested exploit on M4 FINAL has capture + replay-verified draft patch (§13.1). |
| `M4_REPLAY_REMEDIATION_REQUIRED` | `true` | `M4_MET` requires replay-verified doctrine draft patch per exploit (Matt ruling 2026-07-03). |
| `DRAFT_PATCH_SCHEMA_V` | `"2026-07-03d"` | Version pin for §13.1 records (r2.5: replay in `draft_ok`). |
| `DRAFT_PATCH_SANITIZER_MODULE` | `mmi/project_brain/chaos/deterministic_sanitizer.py` | Mandatory before patch content is hashed or stored (runtime blocker §4). |
| `M4_PACKAGE_ROOT` | `mmi/m4/` | Python package for `mmi.m4.*` (canary engine, evidence chain helpers); import-ban scan target (B-R2-03). |
| `M3_MIN_SLOTS_V` | `"2026-07-03a"` | Version pin for §12 slot list; recorded in signed `m3_min_slice_exit`. |
| `M3_MESH_TRUSTED_CORE` | `30` | Implemented mesh trusted core (`chaos_lab_provisioner.py`). |
| `M3_MESH_BASELINE_TOTAL` | `70` | Implemented baseline worker count (Addendum 04 inhale baseline). |
| `M3_MESH_BASELINE_COMPROMISE` | `40` | Compromised baseline slots exercised in `mesh-smash`. |
| `M3_MESH_AIRLOCK_FIRST` | `71` | First air-lock wake slot (`M3_MESH_BASELINE_TOTAL + 1`). |
| `M3_MESH_AIRLOCK_LAST` | `110` | Last air-lock wake slot (`M3_MESH_BASELINE_TOTAL + M3_MESH_BASELINE_COMPROMISE`). |

---

## Section 3 — Staged Proof Ladder (entry/exit)

The ladder is **monotonic and non-skippable**. Each stage entry (verified in the FSM, §3.1) consumes the prior stage's **signed exit artifact**; there is no cold-start path to `M4`. Build order (doctrine): formal invariants → fuzz harness → sandbox escape tests → C-M4 → C2 → C3 → C4 → M4 (48h LAST).

| Stage | `D_mode` | Entry requires (signed) | Scoped reset? | Terminal on pass | Exit may satisfy |
|---|---|---|---|---|---|
| **C-M4** (dry-run) | 15–60 min | operator attest; §5–§7 pre-proofs green | n/a (plumbing) | `HARNESS_READY` | C2 entry **only** |
| **C2** (adversarial replay) | 4h | C-M4 `HARNESS_READY` | yes (debug) | `CLEAN` | C3 entry |
| **C3** (overnight clone) | 12h | C2 `CLEAN` + M3 min slice (§12) | yes (debug) | `CLEAN` | C4 entry |
| **C4** (soak) | 24h | C3 `CLEAN` + M3 min slice | yes (debug) | `CLEAN` | M4 entry |
| **M4** (final endurance) | 48h | C4 `CLEAN` + M3 slice + host-boundary min-viable (§8) | **NO** (full reset only) | `M4_MET` | operator-attested GATED review — `perfect_claim` still pinned |

**Cross-stage integrity:** (a) each exit artifact is signed over `(stage_id, run_mode, RUN_NONCE, D_mode, chain.tip, signed_H0, parent_exit_hash)` by `KEY_CUSTODY` — a shorter stage's artifact cannot be replayed as a longer stage's; (b) `BLOCKED`/`INDETERMINATE` emit **no** artifact and satisfy no downstream entry; (c) stages gating M4 entry (C3, C4) apply FINAL-grade correlated-failure classification (§11) — a critical chain may not be sliced into diagnostics to launder a `CLEAN` that admits M4; (d) **authority binding (MESSAGE-2R R-01):** because `EXIT_BINDS_H0`, `verify_exit` requires the prior exit's `signed_H0` to equal the **current** sealed authority baseline — a C4 `CLEAN` obtained against an older/mutated authority state cannot admit M4 after the repo changed; (e) **lineage (R-07):** each exit records the `parent_exit_hash` of the exact prior-stage exit it consumed, and `verify_exit` walks the lineage back to a single C-M4 root — exits from different run lineages (a C3 from run A + a C4 from run B) cannot be mixed to fabricate a ladder.

### 3.1 Harness FSM (normative pseudo-code)

State set:

$$S = \{\text{INIT},\ \text{PROVISION},\ \text{ARMED},\ \text{INTERVAL\_RUN},\ \text{INTERVAL\_EVAL},\ \text{RESET},\ \text{HALT},\ \text{ROLLUP},\ \text{DONE}\}$$

```
FUNCTION run_stage(run_mode):                              # scripts/m4_endurance_runner.py --stage <run_mode>
    state <- INIT
    REQUIRE BUILD_AUTHORIZED == FALSE                      # no autonomous promotion, ever
    REQUIRE OPERATOR_ATTEST.verify() == TRUE               # hardware-token/MFA, chain-logged
    nonce <- csprng_128()                                  # RUN_NONCE

    # --- staged-ladder ordering, cryptographically enforced ---
    idx <- STAGE_ORDER.index(run_mode)
    IF idx > 0:
        prior_exit <- stage_attestation.load_exit(STAGE_ORDER[idx-1])
        REQUIRE stage_attestation.verify_exit(prior_exit) == TRUE           # prior signed exit
        REQUIRE prior_exit.signed_H0 == seal_fingerprint(AUTHORITY_ROOT)    # R-01: not a stale-repo pass
        REQUIRE stage_attestation.lineage_root(prior_exit) is a single C-M4 # R-07: no mixed lineage

    # DIAGNOSTIC_or_CRITICAL(m): returns DIAGNOSTIC pre-final, CRITICAL on FINAL (R-02)
    IF run_mode in {C3, C4, M4}:
        REQUIRE m3_min_diagnostic_slice.passed == TRUE     # M3_REQUIRED_FOR_M4_ENDURANCE
    IF run_mode == M4:
        REQUIRE host_boundary_daemon.min_viable_slice == TRUE
        REQUIRE draft_patch_evidence.min_viable == TRUE              # §13.1 Phase 11 entry
        REQUIRE SCOPED_RESET_ON_FINAL == FALSE

    # --- seal + SIGN authority baseline BEFORE provisioning ---
    H0 <- seal_fingerprint(AUTHORITY_ROOT)                 # volume+FileId manifest
    STORE KEY_CUSTODY.sign(H0) -> EVIDENCE_ROOT
    REQUIRE provisioner_is_readonly_wrt(AUTHORITY_ROOT)

    state <- PROVISION
    lab_id <- chaos_lab_provisioner.provision(LAB_ROOT)
    REQUIRE attest_clone_image(lab_id) == CLONE_IMAGE_DIGEST
    REQUIRE seal_fingerprint(AUTHORITY_ROOT) == H0         # provisioning left authority untouched
    chain <- evidence_chain.open(EVIDENCE_ROOT, run_mode, nonce)

    state <- ARMED
    envelope <- mmi_control_envelope.attach()              # fail-closed HALT/SUSPEND, dead-man
    canary   <- m4_canary_engine.load(RULESET_M4, D_mode)  # §9, windows bound to D_mode
    invariants <- invariant_suite.attach()                 # §5, live checks
    REQUIRE envelope.armed AND canary.loaded AND invariants.loaded AND envelope.owns_isolated_state

    T_elapsed <- 0 ; D_mode <- duration_for(run_mode) ; i <- 0 ; diag_streak <- 0 ; reset_count <- 0
    corr <- correlation_tracker.new(CORR_WINDOW_S)         # §11 V-009

    WHILE T_elapsed < D_mode:
        state <- INTERVAL_RUN
        t0 <- monotonic_ns()
        IF run_mode == M4:
            attempt_log <- exploit_attempt_log.attach(chain, interval_id=i, tcb=tcb)   # §13.1.2 r2.4
        result <- execute_assault_interval(lab_id, INTERVAL_S, canary, envelope, invariants,
                                           attempt_hook=attempt_log IF run_mode==M4 ELSE NULL)
        dt <- monotonic_ns() - t0

        state <- INTERVAL_EVAL
        Hi   <- seal_fingerprint(AUTHORITY_ROOT)
        tcb  <- attest_tcb(runner, boundary_daemon)
        inv  <- invariants.check_all(result, Hi, H0)       # §5
        live <- result.attributed_actions >= MIN_ASSAULT_ACTIONS AND result.attacker_heartbeat_ok
        lag  <- telemetry_pipeline_lag_s()

        IF lag > TELEMETRY_LAG_HALT_S OR dt NOT in [INTERVAL_S*0.98, INTERVAL_S*1.5] \
           OR clock_step_detected() OR clock_skew(runner, boundary_daemon) > CLOCK_SKEW_MAX_S:
            c_i <- DIAGNOSTIC_or_CRITICAL(run_mode)        # unobservable/dilated/skewed -> never PASS
        ELIF NOT tcb.ok OR NOT inv.ok:
            c_i <- CRITICAL                                # TCB or invariant breach (§5)
        ELIF NOT live:
            c_i <- DIAGNOSTIC_or_CRITICAL(run_mode)        # no applied pressure -> no credit
        ELSE:
            c_i <- classify(result, Hi, H0, canary, envelope, run_mode)

        c_i <- corr.reclassify(c_i, result.root_cause)     # §11: correlated DIAG chain -> CRITICAL
        ok  <- evidence_chain.append(chain, record(i, c_i, result, Hi, tcb, inv))
        IF NOT ok:
            envelope.halt("EVIDENCE_APPEND_FAIL@"+i); status <- INDETERMINATE; state <- HALT; BREAK
        IF run_mode == M4 AND c_i == PASS:
            ok_dp <- draft_patch_evidence.append_inline(chain, i)   # §13.1.3: captures vs chain attempt links
            IF NOT ok_dp:
                envelope.halt("DRAFT_PATCH_APPEND_FAIL@"+i); status <- INDETERMINATE; state <- HALT; BREAK

        IF c_i == CRITICAL:
            envelope.halt("CRITICAL@"+i); T_elapsed <- 0; status <- BLOCKED; state <- HALT; BREAK
        ELIF c_i == DIAGNOSTIC:
            diag_streak += 1
            IF diag_streak > MAX_DIAGNOSTIC_RETRIES:
                envelope.halt("DIAGNOSTIC_STALL@"+i); T_elapsed <- 0; status <- BLOCKED; state <- HALT; BREAK
            IF run_mode == M4: T_elapsed <- 0; reset_count += 1; state <- RESET   # NO exemption; caps this run at M4_NOT_MET
            ELSE: LOG scoped_reset(i); state <- RESET; CONTINUE        # pre-final debug only
        ELSE:  # PASS
            diag_streak <- 0; T_elapsed += INTERVAL_S; i += 1

    state <- ROLLUP
    fingerprint_intact <- (seal_fingerprint(AUTHORITY_ROOT) == H0)
    chain_ok <- evidence_chain.verify(chain)
    budget_ok <- (NOT M4_BUDGET_DEPLETION_REQUIRED OR run_mode != M4 OR envelope.attacker_budget_depleted())
    draft_ok  <- (NOT M4_DRAFT_PATCH_EVIDENCE_REQUIRED OR run_mode != M4 \
                  OR (draft_patch_evidence.complete(chain) \
                      AND (NOT M4_REPLAY_REMEDIATION_REQUIRED OR draft_patch_evidence.replay_complete(chain))))
    pass_conditions <- (T_elapsed >= D_mode AND fingerprint_intact AND invariants.all_held AND reset_count == 0 AND budget_ok AND draft_ok)
    IF NOT chain_ok: status <- INDETERMINATE
    ELIF run_mode == C-M4: status <- HARNESS_READY
    ELIF run_mode == M4: status <- (M4_MET IF pass_conditions ELSE M4_NOT_MET)   # R-06: explicit, never silent BLOCKED
    ELIF pass_conditions: status <- CLEAN
    ELSE: status <- BLOCKED

    IF status in {CLEAN, M4_MET} OR (status == HARNESS_READY AND run_mode == C-M4):
        parent <- (stage_attestation.load_exit(STAGE_ORDER[idx-1]) IF idx>0 ELSE GENESIS)
        stage_attestation.sign_exit(run_mode, status, nonce, D_mode, chain.tip,
                                    signed_H0=KEY_CUSTODY.sign(H0), parent_exit_hash=hash(parent), key=KEY_CUSTODY)
    ELSE:
        stage_attestation.emit_none(run_mode, status)      # non-promoting; M4_NOT_MET/BLOCKED/INDETERMINATE emit nothing

    state <- DONE
    RETURN export_summary(run_mode, status, T_elapsed, i, H0, chain, nonce)
```

**`DIAGNOSTIC_or_CRITICAL(run_mode)` definition (R-02):** if `run_mode == M4` return `CRITICAL`; else return `DIAGNOSTIC`.

---

## Section 4 — Typed Dependency Gates (DAG)

**Typed M3 constants** are normative (see §2). Enforcement is in-code (§3.1 `REQUIRE`s), never operator prose.

**Build/proof DAG** (edges = "must complete before"):

```
invariant_suite(§5) ─┐
fuzz_harness(§6) ────┤
sandbox_escape(§7) ──┼─> TCB[KEY_CUSTODY, stage_attestation, boundary_daemon](§8) ─> C-M4 ─> C2 ─┐
                     │                                                                            │
m3_min_slice(§12) ───┴────────────────────────────────────────────────> (gates C3) ─> C3 ─> C4 ─┴─> M4(48h, LAST)
```

**Parallel vs sequential:** §5, §6, §7 pre-proofs and §12 M3 slice may be developed **in parallel** (research/build lane). The **proof ladder itself is strictly sequential** — no stage runs before its predecessor's signed exit exists (§3). Parallelizing the ladder is an H-rule violation (§16). M3 min slice gates C3 onward: `M3_REQUIRED_FOR_M4_ENDURANCE = true`.

---

## Section 5 — Formal Invariant Suite

Enumerated invariants (mapped from research v2.1 §1.6). Each is checked **live** per interval (`invariants.check_all`) and re-verified at ROLLUP; any breach → CRITICAL.

| ID | Invariant | Verification method (pre-chaos + live) |
|---|---|---|
| **INV-1** | Authority never writable | FileId manifest of `AUTHORITY_ROOT` sealed + signed pre-run; per-interval re-seal `Hi == H0`; minifilter deny-log shows 0 ALLOW-writes. Static: formal check that no code path holds a writable handle to an authority FileId. |
| **INV-2** | Production unreachable | WFP default-deny egress; assert no route/socket from clone SID to any production endpoint set; live: 0 unlisted-egress events (`M4-CANARY-018/019`). |
| **INV-3** | Secrets never cross the boundary | Keys in `KEY_CUSTODY` (non-exportable); static scan that no secret material is readable from clone address space or `LAB_ROOT`; live: 0 secret-pattern egress hits. |
| **INV-4** | Budget monotonic & attributed | AFE ledger (§10) burn is monotonic non-increasing and every delta carries an attributed actor; live: `M4-CANARY-015/016`. |
| **INV-5** | Evidence complete & ordered | Append-only hash chain; per-interval link check; no gaps, no backfill, no reorder; ROLLUP `evidence_chain.verify`. |
| **INV-6** | No autonomous promotion | `BUILD_AUTHORIZED == false`; `OPERATOR_ATTEST` required; no code path promotes a stage without a signed exit + operator attest. |
| **INV-7** | Ladder monotonic | `stage_attestation.verify_exit(prior)` required at entry; static: no entrypoint reaches M4 without the C4 signed exit. |

Verification is a mix of **static** (pre-chaos formal/structural checks, run in Phase 1) and **dynamic** (per-interval live checks). A static-check failure blocks C-M4; a dynamic breach is CRITICAL.

---

## Section 6 — Deterministic Fuzz Harness

**[NEW — spec-defined]** `scripts/m4_fuzz_harness.py`. Deterministic (seeded CSPRNG; seed recorded in evidence) so every finding is reproducible.

| Target | What is fuzzed | Failure = |
|---|---|---|
| **parser** | evidence/summary JSON, canary rule loader, manifest reader | crash, silent truncation, or accept of malformed → fail |
| **FSM** | `run_stage` transition table under injected out-of-order/duplicate events | any transition to a non-enumerated state, or PASS from a non-PASS precondition → fail |
| **ledger** | AFE burn/replenish sequences incl. adversarial ordering | non-monotonic accepted or unattributed burn accepted → fail |
| **canary classifier** | boundary inputs around every threshold | misclassification or fail-open → fail |
| **evidence rollup** | partial/interrupted chains, backfill attempts | verify() returns true on a tampered/incomplete chain → fail |
| **restart** | crash + resume at each state | resume that credits an unobserved interval, or loses fail-closed latch → fail |

**CLI contract:** `m4_fuzz_harness.py --target <t> --seed <n> --iters <k> --evidence <EVIDENCE_ROOT/fuzz/>`.  
**Terminal:** emits `fuzz_summary.json {target, seed, iters, failures[], overall: PASS|FAIL}`. **PASS** ⇔ zero failures across all targets. Must be **PASS before C-M4** (§17 Phase 2). Runs pre-endurance; not part of the 48h clock.

---

## Section 7 — Modular Sandbox Escape Tests

**[NEW — spec-defined]** `scripts/m4_sandbox_escape_suite.py`. Scoped, **modular** escape attempts run **before** any endurance stage — proves the clone is contained *before* spending 48h assuming it is.

| Module | Escape attempted | Expected | Canary |
|---|---|---|---|
| SE-FS | filesystem traversal `LAB_ROOT → AUTHORITY_ROOT` / `EVIDENCE_ROOT` | DENY (FileId) | 001/007 |
| SE-LINK | hardlink/junction/symlink to authority inode | DENY at link-create | 002 |
| SE-RAW | raw volume handle `\\.\C:` / `\\.\PhysicalDriveN` | DENY | 003 |
| SE-NET | egress to non-allowlisted / production endpoint | DENY (WFP) | 004/018 |
| SE-9P | DrvFs/9P relay write attribution bypass | DENY (FileId, not SID) | 001/007 |
| SE-IPC | shared-memory / named-pipe crossing to TCB | DENY | 013/022 |
| SE-KEY | read key material from clone address space / env | no secret readable | 003/022 |

**Terminal:** `sandbox_escape_summary.json {module, result}[]`; **PASS** ⇔ all modules DENY/contained. Gates C-M4 (§17 Phase 3).

---

## Section 8 — Host Boundary Architecture (Windows-native)

**[NEW — spec-defined]** `host_boundary/mmi_boundary_daemon` (Go) + WFP callout + FS minifilter. WSL-only isolation is **insufficient** (Footnote [B]); a 48h assault without a Windows-native boundary tests an imaginary perimeter — FORBIDDEN.

**Demarcation:** enforcement lives on the **Windows host** (WFP + minifilter); the assault runs in the **WSL2 clone** (`LAB_ROOT`). The guest cannot police its own escape, so the host is the enforcement plane.

**Write intercept (minifilter).** Pre-op callbacks on `IRP_MJ_CREATE/WRITE/SET_INFORMATION/SET_SECURITY`. Deny key = `ENFORCEMENT_KEY = volume + NTFS FileId` (not path string): the signed manifest records `(VolumeGuid, FileReferenceNumber)` of every authority object; the callback resolves the op's target FileId on the **actual target handle** (closes pre-op TOCTOU) and DENYs any write to a manifest FileId regardless of path. Hardlink/reparse creation targeting an authority FileId is itself denied. Path-prefix (canonicalized post `\??\`/8.3/symlink) remains a cheap first filter.

**Why FileId not SID (9P closure).** WSL2 reaches Windows volumes via the Plan-9 relay, so guest writes surface under the **relay** identity, not the clone SID — SID rules misattribute. FileId enforcement is identity-of-file, immune to this. Raw-volume access bypasses FS filters entirely, so the clone VM must not expose the backing physical/virtual disk, and raw-volume opens from the clone are denied (`M4-CANARY-003`).

**Authority not mounted (default).** `AUTHORITY_MOUNT_DEFAULT = NOT_MOUNTED`: live repo not mapped into the clone; reads use a read-only VSS/snapshot copy on a separate disk. Removes the live read channel; only a host-plane escape can reach authority — which the boundary exists to stop.

**Egress intercept (WFP).** Callout at `FWPM_LAYER_ALE_AUTH_CONNECT_V4/V6` + `FWPM_LAYER_STREAM_V4`; default-deny from clone SID/AppContainer, allow only the enumerated telemetry socket. Unlisted egress → `M4-CANARY-004/018`.

**Daemon (`mmi_boundary_daemon`, Go).** Loads a signed policy manifest (refuses on hash mismatch); keys in `KEY_CUSTODY`; bridges kernel verdicts to `EVIDENCE_ROOT` (TCB-write-only); dead-man tie-in to `mmi_control_envelope` (heartbeat lapse > `BOUNDARY_DEADMAN_GAP_S` → HALT); least privilege; clone identity never in its trust set.

**Min-viable slice (gates M4 FINAL).** Deny-write proven under T1/T2, WFP default-deny under T7, dead-man under T4, signed-manifest refusal proven, clock-witness live. Absent → `host_boundary_min_viable = false` → M4 entry refused (§3.1). Built as §17 Phase 4, before C3/C4/M4.

---

## Section 9 — M4 Canary Alert Taxonomy (≥20 IDs)

Namespace `mmi.m4.canary.*` **only**. Does **not** import/extend/reference `mmi/project_brain/chaos/canary_metadata_layer.py` (L8) — H-rule H-L8-001 (§16). Every rule: `fail_closed: true`; a trip is CRITICAL (§3.1); action envelope-driven (HALT/SUSPEND), never operator discretion. Windows bound to `D_mode` at load (`window_s = min(rule.window_s, D_mode)`); single-trip `threshold_count=1` rules are duration-invariant.

**26 canary IDs, grouped** (25 prior + `026` §13.1 F2).

| Group | ID | Name | Signal source | Trip / action |
|---|---|---|---|---|
| **A · Host escape / boundary** | M4-CANARY-001 | authority_write_attempt | minifilter.deny_write | count≥1 → HALT |
| | M4-CANARY-002 | hardlink_reparse_to_authority | minifilter.link_deny | count≥1 → HALT |
| | M4-CANARY-003 | raw_volume_open | minifilter.raw_deny | count≥1 → HALT |
| | M4-CANARY-004 | unlisted_egress | wfp.callout.deny | count≥1 → HALT |
| | M4-CANARY-005 | boundary_daemon_deadman | daemon.heartbeat | gap>`BOUNDARY_DEADMAN_GAP_S` → HALT |
| | M4-CANARY-006 | clone_image_mismatch | provisioner.attest | digest≠sealed → HALT |
| **B · Repo integrity w/o direct write** | M4-CANARY-007 | authority_fingerprint_drift | runner.seal_fingerprint | `Hi≠H0` → HALT |
| | M4-CANARY-008 | authority_read_channel_open | mount.monitor | live-authority mount → HALT |
| | M4-CANARY-009 | snapshot_divergence | snapshot.verify | snapshot≠sealed → HALT |
| | M4-CANARY-010 | provisioner_authority_touch | provisioner.audit | write during provision → HALT |
| **C · Evidence tamper** | M4-CANARY-011 | evidence_chain_link_mismatch | chain.verify | hash mismatch → HALT + INDETERMINATE |
| | M4-CANARY-012 | evidence_backfill_out_of_order | chain.verify | reorder/backfill → INDETERMINATE |
| | M4-CANARY-013 | evidence_sink_nontcb_write | sink.acl_monitor | non-TCB writer → HALT |
| | M4-CANARY-014 | summary_signature_invalid | summary.verify | bad/absent sig → INDETERMINATE |
| **D · Budget games / AFE** | M4-CANARY-015 | budget_burn_without_attribution | envelope.budget | unattributed burn → SUSPEND |
| | M4-CANARY-016 | budget_non_monotonic | envelope.budget | non-monotonic → SUSPEND |
| | M4-CANARY-017 | afe_replenishment_violation | afe.ledger | illegal replenish → SUSPEND |
| **E · Slow exfil / side channel** | M4-CANARY-018 | slow_path_low_rate_egress | wfp.byte_rate | drip to non-allowlist → HALT |
| | M4-CANARY-019 | covert_channel_dns | wfp.dns_monitor | covert DNS/tunnel → HALT |
| | M4-CANARY-020 | timing_side_channel_drift | timing.monitor | anomalous timing leak → HALT |
| | M4-CANARY-025 | secret_material_detected | secret.scanner | key/secret pattern in clone-egress or clone-readable mem → HALT (INV-3, MESSAGE-2R R-05) |
| | M4-CANARY-026 | draft_patch_contamination | exploit_capture.verify | executable/markdown/secret pattern in sanitized capture OR sanitizer bypass → HALT (§13.1.3, INV-3) |
| **F · Clock / TCB / ladder** | M4-CANARY-021 | clock_skew_or_step | clock.witness | skew>`CLOCK_SKEW_MAX_S`/step → not-PASS |
| | M4-CANARY-022 | tcb_attestation_mismatch | attest_tcb | mismatch → HALT |
| | M4-CANARY-023 | stage_attestation_forgery | stage_attestation | bad/replayed exit → HALT |
| | M4-CANARY-024 | telemetry_lag_blinding | telemetry.lag | lag>`TELEMETRY_LAG_HALT_S` → HALT |

**Blind-spot coverage (findings §4.2 → canary IDs).**

| Category | Canary IDs |
|---|---|
| Host escape | 001, 002, 003, 004, 005, 006, 018, 019 |
| Repo integrity without direct write | 007, 008, 009, 010 |
| Evidence tampering | 011, 012, 013, 014 |
| Draft-patch poisoning / false artifacts | 026, 011, 012 |
| Budget-attribution games | 015, 016, 017 |
| Slow-path exfiltration | 018, 019, 020 |
| Secret crossing (INV-3) | 025, 003, 022 |
| (Supporting) clock / TCB / ladder | 021, 022, 023, 024 |

No orphaned category; every invariant (§5) has ≥1 detecting canary. All 26 IDs are `mmi.m4.canary.*`; none is shared with `mmi.l8.*`.

---

## Section 10 — AFE Ledger + Hostile Attribution Audit

**AFE** = Autonomy-Fuel Envelope ledger (`mmi/project_brain/chaos/mmi_control_envelope.py` budget plane, reused). Rules:

- **Monotonic burn.** Consumption is monotonic non-increasing within a run; any increase without an authorized replenishment event → `M4-CANARY-016` (INV-4).
- **Replenishment rules.** Replenishment only from a signed operator-attested event, bounded, logged to the evidence chain; illegal replenish → `M4-CANARY-017`.
- **Hostile attribution audit.** *Every* burn delta must carry an attributed actor id; an unattributed or spoofed-actor burn → `M4-CANARY-015`. Budget depletion alone is meaningless without attribution — the audit is what makes depletion evidence of adversarial cost rather than accounting noise.
- **Drift detection.** Cross-check ledger totals against per-interval attributed sums; divergence beyond `AFE_DRIFT_TOLERANCE` (=0, exact-match) → CRITICAL (MESSAGE-2R R-03). Falsifier T11 (§14).

Ledger is append-only into `EVIDENCE_ROOT`, chain-linked with the evidence chain (§11), sticky-latched (no self-ack).

---

## Section 11 — Tamper-Evident Evidence Chain + Correlated-Failure Rules

**Chain.** Append-only JSONL in `EVIDENCE_ROOT` (host-side, TCB-write-only). Genesis block binds `(stage_id, run_mode, RUN_NONCE, D_mode, signed H0)`. Each record links `prev_hash`; interval records carry monotonic interval IDs. **Anti-backfill:** any out-of-order interval id, gap, or `prev_hash` mismatch → `M4-CANARY-011/012` → INDETERMINATE. Verification recomputes from genesis to tip; `chain_verified` requires exact match. Chain immutable after terminal write (read-only + final link).

**Clock-reset honesty formula.** For interval `i`, class `c_i ∈ {PASS, DIAGNOSTIC, CRITICAL}`, `T_elapsed` = validated survived-endurance seconds:

FINAL (`run_mode = M4`, `SCOPED_RESET_ON_FINAL = false`):

$$T_{elapsed} \leftarrow \begin{cases} T_{elapsed} + \text{INTERVAL\_S}, & c_i = \text{PASS} \\ 0, & c_i \in \{\text{CRITICAL}, \text{DIAGNOSTIC}\} \end{cases}$$

Pre-final (`C-M4, C2, C3, C4`, scoped debug reset permitted):

$$T_{elapsed} \leftarrow \begin{cases} T_{elapsed} + \text{INTERVAL\_S}, & c_i = \text{PASS} \\ 0, & c_i = \text{CRITICAL} \\ T_{elapsed}\ \text{(re-run, logged)}, & c_i = \text{DIAGNOSTIC} \end{cases}$$

On FINAL both non-PASS branches map to `0` — no diagnostic exemption, closing survivorship laundering. **`M4_MET` requires `reset_count == 0`** for the invocation (MESSAGE-2R R-06): the 48h must be earned in one unbroken 192-PASS sweep. A CRITICAL is terminal (`BLOCKED`, no continuation); a DIAGNOSTIC on FINAL resets the clock and increments `reset_count`, so the run may continue for telemetry/diagnosis but its terminal is thereafter capped at `M4_NOT_MET`. `reset_count` is published in the summary for audit — a laundered "restart-and-climb" cannot masquerade as a clean sweep.

**Correlated-failure rules (V-009, Codex blocker 5, testable).** A `correlation_tracker(CORR_WINDOW_S)` groups DIAGNOSTIC classifications by `root_cause`. Rule:

$$\text{if } \left|\{\,j : c_j = \text{DIAGNOSTIC} \wedge \text{root\_cause}(j) = r \wedge t_j \in [t\!-\!\text{CORR\_WINDOW\_S},\,t]\,\}\right| > \text{CORR\_MAX\_DIAG\_IN\_WINDOW} \Rightarrow \text{reclassify } \to \text{CRITICAL}$$

I.e. more than `CORR_MAX_DIAG_IN_WINDOW` (=2) diagnostics sharing a root cause inside `CORR_WINDOW_S` (=3600s) is a correlated critical chain, not noise — reclassified CRITICAL on **every** stage (C3/C4 included), so a critical chain cannot be sliced into diagnostics to launder a `CLEAN` that admits M4. **Fixtures:** synthetic root-cause-tagged interval streams (3 same-cause diagnostics in-window → expect CRITICAL; 2 in-window + 1 out → expect no reclassify). **Acceptance:** classifier reproduces the table on fixtures; dedicated falsifier **T12** (§14).

---

## Section 12 — M3 Minimum Diagnostic Slice (Codex blocker 2)

**[NEW — spec-defined]** `scripts/m3_min_slice.py`. Purpose: a **bounded** diagnostic proving the M4-relevant subset of the M3 mesh works, **without** running the full 700-slot Addendum 04 mesh (`M3_REQUIRED_FOR_PERFECT_CLAIM` only). Gates C3/C4/M4 (`M3_REQUIRED_FOR_M4_ENDURANCE`). Grounded in research v2.1 §2.1 and implemented `mesh_smash_m3` in `scripts/chaos_lab_provisioner.py`.

**Orchestration stack (`M3_MIN_STACK`, single lab provision):**

```text
mesh-smash → purple-evasion → action-integrity
```

(Subcommands of `scripts/chaos_lab_provisioner.py`; pattern aligned with Phase 1 harness minus M2-only `smash-all`.)

**Named slots (`M3_MIN_SLOTS`, version `M3_MIN_SLOTS_V`):**

| Slot ID | Source | Plane exercised | Pass criterion |
|---|---|---|---|
| `M3-MESH-TRUSTED-CORE` | `mesh_smash_m3` → `checks.trusted_core_slots` | Air-Lock trusted core (slots 1–30) | slots 1–30 untouched |
| `M3-MESH-AIRLOCK-ROUTE` | `mesh_smash_m3` → `checks.compromises_contained` | Mesh containment / mirror routing | 40/40 compromises routed (slots 31–70 → air-lock 71–110) |
| `M3-MESH-AUTHORITY` | `mesh_smash_m3` → `authority_intact` | Authority fingerprint under mesh stress | `true` |
| `M3-PURPLE-AUTHORITY` | `purple_evasion_run` → `authority_intact` | Adversarial scenario containment | `true` |
| `M3-ACTION-INTEGRITY` | `action_integrity_run` → `failed_count` | Budget / action attribution | `failed_count == 0` |

**Mesh constants (repo authority — do not fork in harness):** `M3_MESH_TRUSTED_CORE=30`, `M3_MESH_BASELINE_TOTAL=70`, `M3_MESH_BASELINE_COMPROMISE=40`, air-lock wake range `71–110`. Full 700-slot inflation remains **out of scope** for this slice (Addendum 04 design target, not admission gate).

- **Pass criteria.** All five `M3_MIN_SLOTS` green in one orchestrated run; weapon tier spread 0 across the stack (tier-consistent, per `scripts/phase1_stability_harness.py` aggregation pattern). Any slot fail → `FAIL`.
- **Evidence artifact.** `EVIDENCE_ROOT/m3_min_slice/m3_min_slice_summary.json` `{M3_MIN_SLOTS_V, slots[], stack[], spread, overall: PASS|FAIL, nonce, sealed_authority_fingerprint}`.
- **Terminal state.** `PASS` → emits signed exit `m3_min_slice_exit` (via `KEY_CUSTODY`, binds `M3_MIN_SLOTS_V` + repo fingerprint); `FAIL` → no artifact.
- **Relationship.** `m3_min_diagnostic_slice.passed` (checked in §3.1) is true **iff** a valid signed `m3_min_slice_exit` for the current repo fingerprint exists. Does **not** satisfy `M3_REQUIRED_FOR_PERFECT_CLAIM` (full 700-slot mesh proof) — that remains out of scope.

---

## Section 13 — Harness Contracts (CLI, paths, schemas, L8 import test)

**Package layout (authority repo, B-R2-03).**

| Path | Role |
|---|---|
| `mmi/m4/` | **`M4_PACKAGE_ROOT`** — Python package `mmi.m4.*` (canary engine, evidence chain, stage helpers). Phase 0 creates scaffold. |
| `scripts/m4_*.py`, `scripts/m3_min_slice.py` | CLI entrypoints (invoke `mmi.m4` modules). |
| `host_boundary/mmi_boundary_daemon/` | TCB boundary daemon (Go). |
| `mmi/project_brain/chaos/` | **Reused** upstream modules (envelope, scoring, L8) — not imported from `mmi.m4.*`. |

**CLI entrypoints.**

| Module | Entrypoint | Evidence path |
|---|---|---|
| Invariant checker | `m4_invariant_check.py --phase static\|live` | `EVIDENCE_ROOT/invariants/` |
| Fuzz harness | `m4_fuzz_harness.py --target <t> --seed <n>` | `EVIDENCE_ROOT/fuzz/` |
| Sandbox escape | `m4_sandbox_escape_suite.py` | `EVIDENCE_ROOT/sandbox/` |
| M3 min slice | `m3_min_slice.py` | `EVIDENCE_ROOT/m3_min_slice/` |
| Stage runner | `m4_endurance_runner.py --stage <C-M4\|C2\|C3\|C4\|M4>` | `EVIDENCE_ROOT/<stage>/` |

**Per-stage summary schema (all stages).** Required fields: `schema, stage_id, run_mode, RUN_NONCE, overall_gate_status, chain_verified, sealed_authority_fingerprint, final_authority_fingerprint, fingerprint_intact, validated_elapsed_s, required_duration_s, intervals_passed, reset_events[], reset_count, canary_trips[], invariants_held, m3_min_slice_passed, host_boundary_min_viable, parent_exit_hash, signed_H0, perfect_claim: false, sealed_at_utc, exit_signature`.

**M4 FINAL summary (`m4_48h_summary.json`).** Same schema plus **`perfect_gate_remaining`** (M4 only): MUST be `[]` when `overall_gate_status == M4_MET`; when `M4_NOT_MET`, lists failed pass lines (e.g. `"replay_remediation"`, `"budget_depletion"`). `stage_id: "M4"`, `overall_gate_status ∈ {M4_MET, M4_NOT_MET, BLOCKED, INDETERMINATE}`, `perfect_claim: false` **pinned**, `reset_events` empty iff `M4_MET`.

**L8 import-ban structural check (H-L8-001, Codex blocker 9).** `scripts/m4_import_ban_test.py`: static scan of **`mmi/m4/`** (`M4_PACKAGE_ROOT`) — `grep -rEn "import .*canary_metadata_layer|from .*canary_metadata_layer" mmi/m4/` must return **zero** matches; any match → **BUILD FAIL**. Also asserts no `mmi.l8.*` symbol is referenced from `mmi.m4.*`. Runs in CI and as a §17 Phase-0 gate.

### 13.1 Exploit capture + draft-patch evidence contract (B-R2-01 — gates Phase 11 / M4 FINAL) — r2.5

Research §1.3 #7, matrix line 70, and §6 T8 require **perfect** draft patches for **every exploit string tried** — tamper-evident **and** replay-verified. **Phases 0–10 do not require this.** M4 FINAL **cannot** reach `M4_MET` until §13.1 is implemented and `draft_ok` passes at ROLLUP (capture + replay).

#### 13.1.0 Terminology (r2.4 + r2.5)

| Term | Meaning in this spec |
|---|---|
| **Sanitized exploit capture** | Deterministic output of `deterministic_sanitizer.py`. Bound by `sanitized_capture_sha256`. Required but **not sufficient** alone for `M4_MET`. |
| **Draft patch (doctrine)** | LLM-generated remediation a human signs off (Kinetic Dashboard §1, Runtime Blockers §4). Hashed as `draft_patch_sha256` when replay-verified. |
| **Replay-verified draft patch** | Doctrine draft patch applied in clone; exploit **must fail** on replay. Required for `M4_MET` (Matt ruling 2026-07-03). |

**No shortcuts:** capture presence without working replay → `M4_NOT_MET`. Do not bind capture bytes to `draft_patch_sha256`.

#### 13.1.1 Per-interval artifact (sidecar mirror)

Path: `EVIDENCE_ROOT/<stage>/intervals/<i>/exploit_capture_record.json` — **mirror only**; authoritative records are **inline chain appends** (§13.1.3–13.1.4).

**Required fields:**

```json
{
  "schema": "DRAFT_PATCH_SCHEMA_V",
  "interval_id": "<i>",
  "run_mode": "M4",
  "RUN_NONCE": "<nonce>",
  "chain_link_hash": "<hash of parent evidence_chain link for interval i>",
  "recorded_at_utc": "<ISO8601>",
  "tamper_evident": true,
  "exploit_captures": [
    {
      "exploit_fingerprint": "<sha256 of normalized exploit string>",
      "attempt_chain_link_hash": "<hash of inline exploit_attempt link>",
      "sanitizer_pass": true,
      "sanitizer_module": "DRAFT_PATCH_SANITIZER_MODULE",
      "sanitizer_output_sha256": "<sha256>",
      "sanitized_capture_sha256": "<sha256 of sanitized capture bytes>",
      "replay_remediation_pass": false,
      "draft_patch_sha256": null
    }
  ]
}
```

`draft_patch_sha256` set only when `replay_remediation_pass == true` (hash of signed doctrine remediation artifact).

#### 13.1.2 Inline TCB-attested attempt log (Finding B — r2.4)

**Problem closed:** interval-close summaries (`result.exploit_attempts`) can under-report (research §4.2 semantic exploit-label laundering).

**Rule:** each exploit string **issued** during `INTERVAL_RUN` on M4 FINAL MUST append an inline chain link **before** interval credit:

```json
{
  "type": "exploit_attempt",
  "interval_id": "<i>",
  "exploit_fingerprint": "<sha256 of normalized exploit string>",
  "issued_at_utc": "<ISO8601>",
  "tcb_attestation_hash": "<attest_tcb at issue time>",
  "chain_prev_hash": "<prior link>"
}
```

- FSM: `exploit_attempt_log.attach(chain, interval_id, tcb)` registers hook; `execute_assault_interval(..., attempt_hook=...)` calls `append_inline` on every issue (§3.1).
- Hook failure → HALT; interval not credited.
- Links covered by **M4-CANARY-011/012** (same anti-backfill as interval records).

**Coverage source of truth:** `draft_patch_evidence.complete(chain)` at ROLLUP asserts: ∀ chain link `L` where `L.type == exploit_attempt`, ∃ capture in a subsequent `draft_patch` link for the same `interval_id` with matching `exploit_fingerprint`, valid `sanitized_capture_sha256`, and `attempt_chain_link_hash == hash(L)`.

Interval-close summaries are **not** authoritative for coverage.

**Falsifier T16 (attempt-log laundering):** PASS credited but chain attempt count > capture count for any interval, or capture references a non-existent attempt link → `M4_NOT_MET` via `draft_ok` false.

#### 13.1.3 Mandatory sanitizer gate + capture inline append (F2, F4)

**Sanitizer (fail-closed).** Before any capture is hashed, stored, or mirrored:

1. Run `deterministic_sanitizer.sanitize(exploit_log_bytes)` from `DRAFT_PATCH_SANITIZER_MODULE`.
2. Sanitizer failure or bypass → `M4-CANARY-026` trip → HALT; interval not PASS-credited.
3. `exploit_capture.verify` scans sanitized bytes for: executable syntax markers, markdown/HTML escape sequences, and secret patterns (same classes as CANARY-025). Hit → CANARY-026 → HALT.

**Capture chain-inline.** At interval credit time (FSM §3.1, immediately after `evidence_chain.append`, only if `c_i == PASS`):

- `draft_patch_evidence.append_inline(chain, i)` builds `exploit_captures[]` from **chain attempt links** for interval `i`, runs sanitizer per attempt, appends `{type: draft_patch, interval_id, exploit_captures[], chain_prev_hash}`.
- Sidecar JSON written **only after** inline append succeeds.
- Post-failure sidecars without matching chain links → INDETERMINATE (CANARY-012).

**Evidence Harvesting Hub (doctrine).** Sanitizer neutralizes hostile log input before capture is hashed. Doctrine draft patch generation follows sanitizer; replay verifier is fail-closed before interval PASS credit on M4 FINAL.

#### 13.1.4 `draft_ok` — capture + replay (r2.5)

- `draft_patch_evidence.complete(chain)`: §13.1.1–13.1.3 (captures vs inline attempt links).
- `draft_patch_evidence.replay_complete(chain)`: ∀ captures, `replay_remediation_pass == true` and valid `draft_patch_sha256`.
- **`draft_ok` requires both** when `M4_REPLAY_REMEDIATION_REQUIRED` (Matt ruling).

#### 13.1.5 Replay-remediation — required for `M4_MET`

For each `exploit_captures[]` entry on M4 FINAL:

1. Generate doctrine draft patch (LLM + human-signable path per Runtime Blockers §4) from **sanitized** input only.
2. Replay exploit `e` in clone with patch applied; exploit **must fail** (same verifier as assault).
3. Set `replay_remediation_pass: true` and `draft_patch_sha256` only when replay passes.

**Falsifier T15:** replay shows exploit still succeeds → `M4_NOT_MET` via `draft_ok` false at ROLLUP.

#### 13.1.6 Matt ruling — no shortcuts (2026-07-03)

**Recorded decision:** MMI does not split matrix PERFECT pass-line #7 from `M4_MET`. No "lesser milestone." No capture-only finish line. Strive to meet and **surpass** the matrix bar — not checkbox security theater.

**Authority:** `lanes/MMI_MATT_RULING_M4_NO_SHORTCUTS_2026-07-03.md`

**Surpassing PERFECT (non-normative aspiration):** tighter falsifiers, stronger chains, attempt logs that cannot be trimmed — build **after** the bar is real, never instead of it.

#### 13.1.7 Phase 11 entry gate (§17)

`draft_patch_evidence.min_viable == true` requires: schema verifier, `exploit_attempt_log` inline hook, sanitizer fail-closed, `complete()` + `replay_complete()` fuzz PASS (incl. T15/T16 fixtures), CANARY-026 registered — **in addition to** C4 signed exit, M3 slice, boundary min-viable.

**C4 dress rehearsal (recommended):** exercise attempt-log + capture pipeline on C4; failures do not block C4 exit but must be logged.

**Falsifier T14:** PASS credited but `complete(chain)` false → `M4_NOT_MET` via `draft_ok` false at ROLLUP.

---

## Section 14 — Falsifiable Scenarios T1–T12

Shared verifier **`VERIFY_FINGERPRINT`:** seal signed `H0` (FileId manifest) pre-blast; post-blast recompute `Hn`; assert `Hn == H0` **and** minifilter deny-log has 0 ALLOW-writes on authority **and** `chain_verified` with no backfill. Disagreement → INDETERMINATE.

| ID | Objective | Target / chaos | Expected terminal | Verification |
|---|---|---|---|---|
| **T1** | Direct authority write | clone `write/create` under `AUTHORITY_ROOT` | DENY → `001` → CRITICAL → BLOCKED | `VERIFY_FINGERPRINT`; ≥1 DENY, 0 ALLOW-write |
| **T2** | Indirect mutation | hardlink/rename/symlink/junction to authority inode | link-create DENY → `002/007` → BLOCKED | `VERIFY_FINGERPRINT`; resolver logged link |
| **T3** | Fingerprint drift, no write op | out-of-band content change | `007` on `Hi≠H0` → CRITICAL → BLOCKED | `VERIFY_FINGERPRINT` fails → BLOCKED |
| **T4** | Perimeter loss | kill/stall `mmi_boundary_daemon` heartbeat | gap>`BOUNDARY_DEADMAN_GAP_S` → `005` → HALT | assert HALT reason `unpoliced_perimeter`; time uncredited |
| **T5** | Evidence tamper/backfill | reorder/edit/backfill a chain link | `011/012` → INDETERMINATE | recompute from genesis; tip mismatch; status ≠ CLEAN |
| **T6** | Host / raw-volume escape | `\\.\C:` raw write; SE-* modules | `003` (+`001/004`) → HALT | `VERIFY_FINGERPRINT`; raw-open deny-log |
| **T7** | Slow-path exfil | low-rate egress to non-allowlist | WFP deny → `018` → HALT | endpoint+bytes in deny-log; BLOCKED |
| **T8** | Budget attribution game | burn with spoofed/absent actor | `015` → SUSPEND | monotonic+attribution log; non-passing |
| **T9** | TCB compromise / counter-measures evasion | inject into runner/daemon; harvest keys; forge PASS/chain | `attest_tcb` mismatch → `022` → CRITICAL; keys non-exportable → forged chain unsignable → INDETERMINATE | assert TCB records match measured baseline; no signing outside custodian; status ≠ CLEAN |
| **T10** | Clock manipulation | NTP/RTC step, time-dilation, monotonic tamper | `dt` out of band OR `clock_step_detected` OR skew>`CLOCK_SKEW_MAX_S` → `021` → not-PASS (reset on FINAL) | assert daemon clock-witness disagreement logged; interval uncredited |
| **T11** | Budget attribution drift (AFE) | ledger totals diverge from attributed per-interval sums; illegal replenish | drift>tolerance → `016/017` → SUSPEND/CRITICAL | assert AFE audit flags divergence; replenish signature check |
| **T12** | Scoped-reset violation on M4 final + correlated-chain laundering | (a) attempt DIAGNOSTIC classification on FINAL; (b) slice a same-root-cause critical chain into >`CORR_MAX_DIAG_IN_WINDOW` diagnostics at C3/C4 | (a) FINAL maps non-PASS→`T_elapsed=0`, no exemption; (b) `correlation_tracker` reclassifies →CRITICAL → BLOCKED | (a) summary `scoped_reset_forbidden_on_final=true`, reset=FULL; (b) fixtures §11 reproduce CRITICAL; no `CLEAN` C4 artifact emitted |
| **T13** | Attacker budget not depleted at FINAL ROLLUP | assault completes 48h wall clock but AFE ledger shows attacker budget remaining | `M4_NOT_MET` (not `M4_MET`) | assert `envelope.attacker_budget_depleted()` false at ROLLUP; research v2.1 §6 T4 |
| **T14** | Assault interval without per-exploit sanitized capture | interval PASS but `complete(chain)` false | `M4_NOT_MET` via `draft_ok` false | assert §13.1.1–13.1.3; research §6 T8 |
| **T15** | Replay false draft patch | doctrine draft patch replayed; exploit still succeeds | `M4_NOT_MET` via `draft_ok` false | `replay_remediation_pass` false; §13.1.5 |
| **T16** | Attempt-log laundering | trimmed interval summary vs chain attempt links | `M4_NOT_MET` via `draft_ok` false | attempt count > capture count; §13.1.2 |

### 14.1 Research v2.1 §6 traceability (Cursor grounding)

Research rows assume **48h FINAL** context (`M4_NOT_MET` + full clock reset). Spec rows are **build/staged** falsifiers with fail-closed terminals (`BLOCKED`, `HALT`, `INDETERMINATE`) — equivalent severity, finer granularity for phased implementation.

| Research §6 | Spec coverage | Notes |
|---|---|---|
| T1 authority write | **T1** | Aligned |
| T2 production DB contact | **INV-2** + `M4-CANARY-018/019` + **T7** slow-path exfil | Production isolation (research §1.3 #6) |
| T3 secret exfil | **T7**, **CANARY-025**, **INV-3** | Slow/multi-interval exfil |
| T4 budget not depleted at 48h | **T13** + `M4_BUDGET_DEPLETION_REQUIRED` + §10 AFE | Closed in r2.1 grounding |
| T5 critical miss without MISSED ledger | **purple-evasion** `missed_scenarios` + canary trips | Evidence in `purple_evasion_summary.json` |
| T6 host escape (DrvFs/Docker/interop) | **T6**, **§7 SE-***, **CANARY-001..006** | Windows-native boundary required (§8) |
| T7 known-hostile signal, no canary | **§9** taxonomy + **T6/T7** | Expanded beyond coarse v2 baseline |
| T8 assault interval without draft patch | **T14**, **T16** + §13.1 + CANARY-026 | Phase 11 gated until §13.1.1–13.1.3 built |
| T9 evidence hash-chain break | **T5**, **CANARY-011/012** | Aligned |
| T10 toolchain/path poisoning | **T2** indirect mutation + **CANARY-007/010** | Repo integrity without direct write (research §4.2) |
| T11 budget attribution drift | **T8**, **T11**, **§10** | Hostile attribution audit |
| T12 scoped-reset on M4 final | **T12**, **H-FINAL-001**, §11 formula | Aligned |

---

## Section 15 — Observability (required vs optional)

**Decision (explicit):**

- **REQUIRED:** a **read-only** operator view of live `overall_gate_status`, current interval, `T_elapsed`, canary trips, and telemetry lag, served from `EVIDENCE_ROOT` (TCB-write-only source). The control plane **must not** accept commands over this channel — observability is read-only; promotion/HALT never travel over it (defeats a fake-operator command path). Telemetry-lag beyond `TELEMETRY_LAG_HALT_S` HALTs the run regardless of viewer state (observability outage never fails-open).
- **OPTIONAL:** a FastAPI/WebSocket live feed for convenience. If built, it is a read replica of the required view, same read-only contract, no control surface. Its absence never blocks a run.

Rationale: a control-capable observability plane is an attack surface for autonomous/forged promotion (INV-6). Read-only by construction.

---

## Section 16 — Non-Goals, H-Rules, L8 Namespace Contract

**Non-goals:** `central_brain.py` (AGI step 6); genomic v2 24/7 loop; any PERFECT-tier or "M4 closed" claim; build authorization; use of `/home/socialarchitect/northstar` (forbidden path, not referenced).

**H-rules (hard, build-fail on violation):**

- **H-L8-001:** any import of `mmi/project_brain/chaos/canary_metadata_layer.py` (or reference to a `mmi.l8.*` symbol) from the `mmi.m4.*` package (`mmi/m4/`) → **BUILD FAIL** (structural test §13).
- **H-LADDER-001:** Phase 1 of §17 being the 48h runner, or any parallelization of the proof ladder, or any M4 entry without a C4 signed exit → **BUILD FAIL** (table structure §17 makes this unbuildable).
- **H-FINAL-001:** scoped/diagnostic reset on M4 FINAL → violation (formula §11 has no such branch).
- **H-EVID-001:** `EVIDENCE_ROOT` under `/tmp` or clone-reachable, or any non-TCB writer → violation.
- **H-PROMO-001:** `BUILD_AUTHORIZED != false` in a spec run, or promotion without `OPERATOR_ATTEST` → violation.

**L8 namespace contract:** M4 signal IDs are `mmi.m4.canary.*` (26 IDs, §9); L8 is `mmi.l8.metadata.*`. No shared IDs, schemas, imports, or code. The two layers are independently versioned.

---

## Section 17 — Build Phasing Table (48h runner LAST)

Straight-to-48h is **unbuildable by this table's structure** — each row's "blocks endurance until done" makes the 48h runner reachable only after every prerequisite phase exits green.

| # | Deliverable module(s) | Entry gate | Exit gate | Blocks endurance until done |
|---|---|---|---|---|
| **0** | `m4_import_ban_test.py` (H-L8-001) | repo scaffold | 0 L8 imports in `mmi.m4.*` | yes — CI gate on every phase |
| **1** | `m4_invariant_check.py` + INV-1..7 (§5) | Phase 0 | static checks PASS | yes |
| **2** | `m4_fuzz_harness.py` (§6) | Phase 1 | `fuzz_summary` PASS (0 failures) | yes |
| **3** | `m4_sandbox_escape_suite.py` (§7) | Phase 2 | all modules DENY/contained | yes |
| **4** | TCB: `KEY_CUSTODY` (TPM/HSM), `stage_attestation`, `host_boundary/mmi_boundary_daemon` + WFP/minifilter (§8) | Phase 3 | min-viable slice proven (T1/T2/T4/T7) | yes — no endurance before boundary exists |
| **5** | `m3_min_slice.py` (§12) | Phase 4 | signed `m3_min_slice_exit` | yes — gates C3+ |
| **6** | `m4_canary_engine` (26 IDs §9) + `evidence_chain` (§11) + AFE ledger (§10) | Phase 5 | canary/chain/ledger unit + fuzz PASS | yes |
| **7** | `m4_endurance_runner.py --stage C-M4` (dry-run) | Phase 6 | `HARNESS_READY` | — |
| **8** | `--stage C2` (4h) | Phase 7 `HARNESS_READY` | `CLEAN` | — |
| **9** | `--stage C3` (12h) | Phase 8 `CLEAN` + M3 slice | `CLEAN` | — |
| **10** | `--stage C4` (24h) + `exploit_attempt_log` + `draft_patch_evidence` (§13.1) + sanitizer + CANARY-026 | Phase 9 `CLEAN` + M3 slice | `CLEAN` + `draft_patch_evidence.min_viable`; C4 dress rehearsal recommended | yes — gates Phase 11 |
| **11** | `--stage M4` (48h) — **LAST** | Phase 10 exit + M3 + boundary min-viable | `M4_MET` (matrix-aligned; `perfect_claim` pinned) | — |

Phase 1 is the invariant suite, **not** the 48h runner (H-LADDER-001 satisfied). The 48h runner is Phase 11, last.

---

## Codex R1 Resolution Map

| Blocker | Resolution | Section |
|---|---|---|
| 1 — narrow vs superset | full 17 sections; no Footnote-[A] deferral | all |
| 2 — M3 min diagnostic slice | stress shape, pass criteria, artifact, terminal, signed exit, relationship | §12 |
| 3 — invariants + fuzz | INV-1..7 + verification; fuzz targets/CLI/terminal | §5, §6 |
| 4 — TCB build phasing | KEY_CUSTODY/stage_attestation/daemon as explicit phases before C3/C4/M4 | §17 Phase 4 |
| 5 — V-009 testable | correlated-failure rule + constants + fixtures + acceptance + falsifier | §11, §14 T12 |
| 6 — canary ≥20 | 26 IDs, grouped, blind-spot table | §9 |
| 7 — falsifiers T1–T12 | complete table incl. T10/T11/T12 fully specified | §14 |
| 8 — build phasing table | phase#/module/entry/exit/blocks; 48h LAST | §17 |
| 9 — L8 namespace enforcement | H-L8-001 import ban + structural test + namespace contract | §16, §13 |

---

## Revision Log

**r1 (narrow) → r2 (superset).** Expanded 4-section narrow slice to full 17 sections; **no regression** of prior security remediations.

**Preserved MESSAGE-2 ledger (V-1..V-11):** FileId enforcement (V-1/V-2), authority not-mounted (V-3), fail-closed evidence append (V-4), key custody (V-5), applied-pressure PASS predicate (V-6), monotonic clock (V-7), TCB attestation + T9 (V-8), diagnostic retry bound (V-9), falsifier gaps → T9/T10/T11 (V-10), no L8/northstar coupling (V-11). All carried into §3.1/§5/§8/§9/§14.

**Preserved MESSAGE-3 ledger (V-001..V-011):** evidence off `/tmp` (V-001), non-skippable ladder + signed exits (V-002), clone-image attest (V-003), operator hardware-attest (V-004), RUN_NONCE anti-replay (V-005), cross-clock skew (V-006), H0 pre-provision signed seal (V-007), fail-closed ARM (V-008), upstream correlated-chain integrity (V-009 → now §11 + T12), canary windows bound to D_mode (V-010), namespace re-check (V-011). All carried into §2/§3.1/§8/§9/§11.

**r2 additions (Codex R1):** §5 invariant suite, §6 fuzz harness, §7 sandbox escape, §10 AFE ledger, §12 M3 min slice, §13 harness contracts + L8 import test, §14 full T1–T12, §15 observability decision, §16 H-rules, §17 build phasing, Codex resolution map.

### MESSAGE 2R — adversarial self-review of the r2 superset

Codex R1 blocker checklist re-verified against the draft: **[✓] 1** 17 sections · **[✓] 2** M3 slice pass/artifact/terminal (§12) · **[✓] 3** invariants + fuzz CLI (§5/§6) · **[✓] 4** TCB phased before endurance (§17 P4) · **[✓] 5** V-009 rule+fixtures+T12 (§11/§14) · **[✓] 6** 25 canary IDs + blind-spot table (§9) · **[✓] 7** T1–T12 complete (§14) · **[✓] 8** phasing, 48h LAST (§17) · **[✓] 9** L8 import ban (§16/§13). No blocker unresolved.

Defects found by hostile self-review and fixed inline:

| Finding | Sev | Defect | Fix |
|---|---|---|---|
| **R-01** | H | Stage exit artifact signed over `chain.tip` but **not** the authority baseline — a C4 `CLEAN` earned against an older/mutated authority could admit M4 after the repo changed. | `EXIT_BINDS_H0`; exit signed over `signed_H0`; `verify_exit` requires `prior_exit.signed_H0 == current H0` (§3, §3.1). |
| **R-02** | M | `DIAGNOSTIC_or_CRITICAL(run_mode)` referenced in the FSM but its definition was dropped during expansion (regression). | Defined inline (§3.1): DIAGNOSTIC pre-final, CRITICAL on FINAL. |
| **R-03** | M | AFE drift "named tolerance" was an unnamed magic number. | `AFE_DRIFT_TOLERANCE = 0` constant (§2, §10). |
| **R-04** | L | `M4-CANARY-005` used literal `30s`; `BOUNDARY_DEADMAN_GAP_S` had been dropped from the constants table (regression). | Constant restored (§2), referenced in §9. |
| **R-05** | L | INV-3 (secrets never cross boundary) had no dedicated canary — detection was implicit. | `M4-CANARY-025 secret_material_detected`; invariant→canary mapping closed (§9). |
| **R-06** | M | ROLLUP assigned `M4_NOT_MET` via a hand-wavy `# or ...` comment; a clean-completion-but-reset FINAL was ambiguous. | Explicit `pass_conditions` incl. `reset_count == 0`; FINAL → `M4_MET`/`M4_NOT_MET` deterministically (§3.1, §11). |
| **R-07** | L | Ladder verified only the immediate prior link — exits from different run lineages could be mixed. | `parent_exit_hash` lineage recorded; `verify_exit` walks lineage to a single C-M4 root (§3, §3.1). |

**R1 regression check (axis 8):** V-1..V-11 and V-001..V-011 remediations re-confirmed present after expansion; R-02 and R-04 were the only regressions and are restored. No security fix dropped.

### Cursor r2.1 grounding pass (2026-07-03)

Repo-mounted diff against research v2.1 on disk:

| Item | Action |
|---|---|
| `M3_MIN_SLOTS` | Named 5-slot list + `M3_MIN_STACK` from `chaos_lab_provisioner.py` / Phase 1 pattern (§12) |
| Research §6 T4 budget depletion | `M4_BUDGET_DEPLETION_REQUIRED`, FSM `budget_ok`, falsifier **T13** |
| Research §6 traceability | §14.1 mapping table (incl. T8 → §13.1 r2.3 per-exploit) |
| Proof object / ladder / blind spots | Confirmed aligned — no tag changes required |

### Cursor r2.3 §13.1 hardening (2026-07-03)

Claude adversarial throw-back (F1–F5) on r2.2 §13.1 — advisory, not Codex verdict:

| Finding | Severity | r2.3 resolution |
|---|---|---|
| F1 per-interval not per-exploit | High | `exploit_captures[]`; `complete()` over every logged attempt (§13.1.2) |
| F2 sanitizer not fail-closed | High | Mandatory `deterministic_sanitizer.py`; **M4-CANARY-026** (§13.1.3) |
| F3 "perfect" unproven | Med | Scope honesty; replay-remediation = PERFECT bar only (§13.1.4, T15) |
| F4 backfill hole | Med | `append_inline` at interval credit; CANARY-011/012 (§13.1.3, FSM) |
| F5 no dress rehearsal | Low | C4 recommended in §13.1.5; Phase 10 builds module |

**Not claimed:** BUILDABLE, PERFECT, M4 closed — requires Codex re-review on r2.3 Phase 10/11 delta.

### Cursor r2.4 §13.1 hardening (2026-07-03)

Claude r2.3 advisory residuals (A/B/C) — advisory, not Codex verdict:

| Finding | Severity | r2.4 resolution |
|---|---|---|
| A terminology / wrong artifact name | Med-High | §13.1.0 table; `sanitized_capture_sha256`; sidecar → `exploit_capture_record.json`; `draft_patch_sha256` reserved for PERFECT remediation only |
| B attempt-log laundering | Med | Inline `exploit_attempt` chain links at issue time; `complete()` vs chain not summary; **T16** |
| C M4_MET vs matrix PERFECT | Decision | `perfect_gate_remaining` on M4 summary; §13.1.6 Matt/research ruling — not coded |

**Not claimed:** BUILDABLE, PERFECT, M4 closed — Codex re-review required on r2.5 delta.

### Cursor r2.5 Matt ruling alignment (2026-07-03)

**Matt ruling:** no shortcuts; `M4_MET` requires replay-remediation (`M4_REPLAY_REMEDIATION_REQUIRED`); removed lesser-milestone / Option 1 framing.

| Change | Detail |
|---|---|
| `draft_ok` | `complete()` **AND** `replay_complete()` |
| T15 | Blocks `M4_MET`, not PERFECT-only |
| §13.1.6 | Matt ruling recorded; supersedes open Finding C |
| `perfect_gate_remaining` | `[]` iff `M4_MET`; lists failures when `M4_NOT_MET` |

**Not claimed:** BUILDABLE, PERFECT achieved, M4 closed, GATED.

---

## Footnotes

**[A] (retired).** r1 Footnote-[A] narrow-vs-superset deferral is resolved — full 17 sections delivered (Codex blocker 1).

**[B] WSL insufficiency.** WSL2 DrvFs does not provide a trustworthy write-deny perimeter from inside the guest (guest cannot police its own escape; DrvFs perms advisory vs Windows ACLs). Endurance requires the Windows-native WFP + minifilter plane (§8). 48h on WSL-only isolation is forbidden. Grounded on `RESEARCH_host_boundary_wsl_windows_2026-06.md` per research v2.1 §5.

**[C] Grounding (Cursor r2.5 pass 2026-07-03).** r2.3–r2.4 retained. **Matt ruling:** full matrix bar for `M4_MET` incl. replay (§13.1.5, `M4_REPLAY_REMEDIATION_REQUIRED`). No capture-only finish line. `perfect_claim` still pinned until GATED. See `lanes/MMI_MATT_RULING_M4_NO_SHORTCUTS_2026-07-03.md`.

**[D] No autonomous promotion.** Nothing here authorizes a build, promotes a gate from an endurance result, merges genomic v2 / `central_brain.py`, or claims M4 met/closed or PERFECT achieved.

---

## Safety Declaration

**As-revised (r2): FAILS SECURE over the modeled threat set.** Every enumerated condition — authority writes (direct/indirect/hardlink/raw-volume), fingerprint drift, production reachability, secret crossing, evidence tamper/backfill, telemetry-flood blinding, hang/time-dilation laundering, clock manipulation, budget-attribution games + AFE drift, boundary-daemon loss, TCB compromise, stage-skip/replay, correlated-chain laundering — terminates in `BLOCKED`, `INDETERMINATE`, or `M4_NOT_MET`, never a spurious `CLEAN`/`M4_MET`.

This is a **design-level** claim over the **modeled** set only — **not** a proof of implementation and **not** "perfectly closed." Open and requiring per-phase build-time re-audit: hardware/hypervisor escapes below the WFP layer, unmodeled side channels, and the correctness of the unbuilt daemon/minifilter, `KEY_CUSTODY`, and `stage_attestation`. The fail-secure claim is only as strong as those components. No PERFECT-tier, M4-met, or M4-closed assertion is made.

## SIGN-OFF: PASS WITH REVISIONS

Full 17-section superset; all 9 Codex R1 blockers resolved; MESSAGE-2/3 remediations preserved; seven MESSAGE-2R defects fixed; **Cursor r2.1 grounding** names `M3_MIN_SLOTS`, adds research §6 traceability (§14.1), closes research T4 via T13 + `M4_BUDGET_DEPLETION_REQUIRED`. **Revisions still required before build:** (1) draft-patch per-interval evidence artifact (research T8 — build lane); (2) build-time verification of boundary daemon/minifilter, `KEY_CUSTODY`, `stage_attestation`, H-L8-001 test; (3) optional MESSAGE 3R isolation audit. **Spec-ready for Codex R2 BUILDABLE review; build auth remains NOT AUTHORIZED until Codex says so.**
