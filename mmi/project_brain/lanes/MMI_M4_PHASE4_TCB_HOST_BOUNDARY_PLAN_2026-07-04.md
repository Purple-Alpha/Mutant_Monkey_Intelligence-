# MMI Phase 4 — TCB / Host-Boundary Min-Viable Plan

**Lane:** Claude/Codex plan (contract + architecture)  
**Date:** 2026-07-04  
**Task id:** `mmi-m4-evolution-gate`  
**Spec:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §8, §3.1, §17 Phase 4, §14 T1/T2/T4/T7  
**Prerequisites:** Phase 0–3 Codex CLEAN; Phase 3 policy-model scope only  
**Authority topology:** `MMI_MATT_DECISION_DUAL_PC_HARDWARE_2026-07-03.md`

**Status:** PLAN ARTIFACT — pre-build gate answers for P4-Q1..Q10  
**Not claimed:** BUILDABLE (until Codex plan review), build authorization, M4_MET, containment-proven, GATED, PERFECT

---

## 1. Purpose and bounds

Phase 4 is the **ceiling test** for live Windows-native enforcement. It replaces Phase 3’s **policy model** with kernel-visible mechanics on **PC1 (Authority/TCB)**.

**Min-viable slice exit** (§8, §17 Phase 4 — gates M4 FINAL entry only after this passes):

| Gate | Falsifier | Canary / signal |
|------|-----------|-----------------|
| Deny-write under assault | T1 direct write ALLOW | CANARY-001 |
| Indirect mutation deny | T2 link-create ALLOW | CANARY-002/007 |
| Dead-man on perimeter loss | T4 heartbeat gap uncaught | CANARY-005 |
| WFP default-deny | T7 unlisted egress ALLOW | CANARY-004/018 |
| Signed-manifest refusal | Daemon arms on hash mismatch | CANARY-022 |
| Clock-witness live | T10 skew uncredited | CANARY-021 |

**Explicitly out of min-viable scope** (later §17 phases):

- Endurance stages C-M4 → M4 (Phases 7–11)
- Full 26-canary engine runtime (Phase 6)
- AFE ledger live assault (Phase 6)
- M3 min slice (Phase 5)
- §13.1 draft-patch / replay pipeline (Phase 10)
- Honest dual-PC purple (requires PC2 hardware — ops proof separate from min-viable build)

**Language:** MMI remains **containment-targeting** after Phase 4 pass. Phase 4 proves the **min-viable boundary slice**, not M4_MET or containment-proven.

---

## 2. Pre-build gate — P4-Q1..Q10 (answered)

### P4-Q1 — What is inside the TCB?

**Spec anchor:** §8, §17 Phase 4, §2 constants (`KEY_CUSTODY`, `EVIDENCE_ROOT`, `ENFORCEMENT_KEY`)

The **Trusted Computing Base** for Phase 4 is everything on **PC1** that can (a) enforce authority integrity, (b) sign or verify ladder artifacts, or (c) append to `EVIDENCE_ROOT`:

| Component | Role | Trust property |
|-----------|------|----------------|
| **`KEY_CUSTODY`** (TPM 2.0 or HSM, PC1) | Non-exportable signing for H0 manifest, policy manifest, evidence-chain records, stage exit artifacts | Keys never in repo, runner env, clone memory, or PC2 |
| **`stage_attestation`** (`mmi/m4/` verify/sign module + CLI hooks) | `verify_exit`, `sign_exit`, lineage walk to single C-M4 root; enforces `EXIT_BINDS_H0` | Verification uses custodian public material only; no signing in Python runner |
| **`host_boundary/mmi_boundary_daemon/`** (Go) | Loads signed policy manifest; bridges minifilter/WFP verdicts to evidence; dead-man heartbeat; refuses arm on manifest mismatch | Least privilege; clone SID/AppContainer **not** in trust set |
| **FS minifilter** (kernel + userland comms) | Pre-op deny on authority FileIds (`IRP_MJ_CREATE/WRITE/SET_INFORMATION/SET_SECURITY`); link-create to authority FileId denied | Enforcement on **actual target handle FileId** (TOCTOU closed) |
| **WFP callout** (kernel + userland) | Default-deny egress from clone identity; allowlist-only telemetry socket | Unlisted connect → deny logged |
| **`EVIDENCE_ROOT` volume** | Append-only evidence sink (`C:\mmi_m4_evidence\` or dedicated VHD) | TCB-write-only ACL (H-EVID-001); outside `AUTHORITY_ROOT` and clone reach |
| **`seal_fingerprint` / H0** | Pre-provision FileId manifest of `AUTHORITY_ROOT` | Signed by `KEY_CUSTODY` before any clone provision |
| **`mmi_control_envelope` dead-man path** | Heartbeat consumer; gap > `BOUNDARY_DEADMAN_GAP_S` → HALT | Tie-in from daemon; not operator-discretionary |
| **Clock witness** (daemon-side) | Monotonic/skew check vs runner; `CLOCK_SKEW_MAX_S` | Live at min-viable exit (CANARY-021 path) |
| **Signed policy manifest** | Enumerates `(VolumeGuid, FileReferenceNumber)` for every authority object | Hash mismatch → daemon **refuses to arm** |

**Not in TCB:** WSL2 guest, PC2 forge, Python fuzz/sandbox modules, upstream `mmi/project_brain/chaos/*`, operator UI (read-only observability §15).

---

### P4-Q2 — What is outside the TCB?

**Spec anchor:** §8 demarcation, dual-PC decision, `AUTHORITY_MOUNT_DEFAULT`, `LAB_ROOT`

| Zone | Location | Capabilities (bounded) |
|------|----------|------------------------|
| **Chaos / clone venue** | PC2 (target) or PC1 `LAB_ROOT` during single-host dev | Assault execution inside WSL2/isolated clone; **no** enforcement authority |
| **Read-only authority snapshot** | Separate disk/VSS copy | Clone may **read** sealed snapshot only; live `AUTHORITY_ROOT` **not mounted** (`AUTHORITY_MOUNT_DEFAULT = NOT_MOUNTED`) |
| **Endurance runner** | PC1 user session | Orchestrates stages; holds **no** signing keys; must pass `stage_attestation.verify_exit` at entry |
| **Provisioner** | PC1 (read-only w.r.t. authority) | Creates clone; clone-image digest attestation (CANARY-006) — not a signer |
| **Reused chaos modules** | `mmi/project_brain/chaos/*` | Envelope, scoring, L8 — **not imported from `mmi.m4.*`** (H-L8-001) |
| **Observability channel** | Read-only view of `EVIDENCE_ROOT` | No commands; promotion/HALT never over this path (§15) |
| **PC2 local LLM shards** | PC2 GPU | Critic/assault inference; sanitizer before any hostile log read |
| **Cloud/API LLMs** | External | Research/spec lanes only; not boundary enforcement |

**Trust boundary line:** Windows **host enforcement plane** (WFP + minifilter + daemon on PC1) vs everything that runs **inside or from** the clone/forge identity.

---

### P4-Q3 — Which keys exist and where do they live?

**Spec anchor:** §2 `KEY_CUSTODY`, §3 cross-stage integrity, §8 daemon

| Key / material | Purpose | Custody | Must never appear in |
|----------------|---------|---------|----------------------|
| **Stage attestation signing key** | Signs exit artifacts over `(stage_id, run_mode, RUN_NONCE, D_mode, chain.tip, signed_H0, parent_exit_hash)` | TPM/HSM `KEY_CUSTODY` on PC1 | Repo, `.env`, runner, clone env, PC2, logs |
| **H0 manifest signing key** | Signs authority baseline at stage entry (pre-provision) | Same custodian (may be same key with distinct context labels) | Same |
| **Policy manifest signing key** | Signs FileId manifest consumed by daemon at arm-time | Same custodian | Same |
| **Evidence-chain record signing key** | Signs append records (genesis binds stage + nonce + H0) | Same custodian | Same |
| **Verify-only public material** | `verify_exit`, manifest hash check, chain verify | Published to runner/daemon read-only | N/A — public by design |
| **`ENFORCEMENT_KEY`** | **Not a crypto key** — `(VolumeGuid, NTFS FileReferenceNumber)` identity set in signed manifest | Manifest in `EVIDENCE_ROOT`; enforced by minifilter | Must not be confused with signing keys |

**Phase 4 build proof (non-export):** custodian self-test demonstrating sign works, export/read of private material fails, and static scan (INV-3) finds no secret patterns in clone-reachable paths.

**Transition note:** Until TPM path is wired, plan allows **software HSM stub on PC1 dev** only for unit tests — **min-viable exit requires TPM or hardware HSM** per spec constant; stub cannot satisfy exit gate.

---

### P4-Q4 — What signs stage exits?

**Spec anchor:** §3.1 FSM ROLLUP, §3 cross-stage integrity

On terminal **promoting** states only (`HARNESS_READY`, `CLEAN`, `M4_MET`):

1. Runner computes current `H0 = seal_fingerprint(AUTHORITY_ROOT)`.
2. Runner loads prior stage exit (if any) and passes lineage inputs to custodian.
3. **`KEY_CUSTODY.sign_exit`** produces artifact containing:
   - `stage_id`, `run_mode`, `RUN_NONCE`, `D_mode`
   - `chain.tip` (may be genesis tip at C-M4)
   - `signed_H0` (= custodian signature over current H0)
   - `parent_exit_hash` (= hash of consumed prior exit, or GENESIS)
   - `exit_signature` over the full tuple

**Non-promoting terminals** (`BLOCKED`, `INDETERMINATE`, `M4_NOT_MET`, diagnostic pre-final where applicable): **`stage_attestation.emit_none`** — no artifact; downstream entry impossible.

**H0 is also signed pre-provision** (§3.1) and stored to `EVIDENCE_ROOT` before clone exists — separate from exit artifact but same custodian.

---

### P4-Q5 — What validates stage exits?

**Spec anchor:** `verify_exit`, `EXIT_BINDS_H0`, §3.1 entry gate

At every stage entry where `STAGE_ORDER[idx] > 0`:

```
prior_exit <- load_exit(STAGE_ORDER[idx-1])
REQUIRE verify_exit(prior_exit) == TRUE
REQUIRE prior_exit.signed_H0 verifies under KEY_CUSTODY public material
REQUIRE prior_exit.signed_H0 == seal_fingerprint(AUTHORITY_ROOT)   # R-01 stale-repo block
REQUIRE lineage_root(prior_exit) is single C-M4 root                 # R-07 mixed-lineage block
REQUIRE prior_exit.stage_id == STAGE_ORDER[idx-1]
REQUIRE RUN_NONCE / run_mode / D_mode consistent with current invocation policy
```

**Forged or replayed exit** → `M4-CANARY-023` path → HALT; status ≠ CLEAN.

**Implementation split:**

- **`stage_attestation` Python module:** pure verify + artifact I/O (unit-testable)
- **Runner entry gate:** calls verify before PROVISION
- **Optional daemon attestation hook:** CANARY-022 TCB baseline match

Phase 4 min-viable requires **unit tests** for verify/sign round-trip, stale-H0 rejection, and mixed-lineage rejection — not yet endurance integration.

---

### P4-Q6 — What can the chaos side read?

**Spec anchor:** §8 `AUTHORITY_MOUNT_DEFAULT`, dual-PC rules, §7 SE-* read implications

| Readable by chaos identity | Condition |
|----------------------------|-----------|
| **Read-only authority snapshot** | Sealed copy on separate volume; digest attested at provision (CANARY-006/009) |
| **Its own `LAB_ROOT` / clone filesystem** | Full read/write inside lab venue only |
| **Allowlisted telemetry responses** | Only what WFP permits (e.g., evidence ingest socket ACK/metadata — not authority content) |
| **Public verify keys / policy manifest hash** | If explicitly published for attestation — **no private keys** |

| **Forbidden reads** | Enforcement |
|---------------------|-------------|
| Live `AUTHORITY_ROOT` via mount | `AUTHORITY_MOUNT_DEFAULT = NOT_MOUNTED`; CANARY-008 on live mount |
| `EVIDENCE_ROOT` write or TCB-only append paths | ACL + CANARY-013 |
| `KEY_CUSTODY` private material | TPM/HSM + INV-3 + CANARY-025 |
| Production endpoints / non-allowlist network | WFP default-deny |

**PC2 (when online):** may mirror assault telemetry; does **not** read live PC1 authority tree. Any read path to authority content is **snapshot-only**, never live brain.

---

### P4-Q7 — What can the chaos side write?

**Spec anchor:** §8 minifilter FileId deny, §14 T1/T2, SE-9P / R-031

**Default: nothing to authority or evidence.**

| Target | Expected result |
|--------|-----------------|
| Any file whose `(VolumeGuid, FileId)` ∈ signed manifest | **DENY** all mutating IRPs (T1) |
| Hardlink/reparse/junction targeting authority FileId | **DENY** at link-create (T2) |
| Raw volume `\\.\C:` / physical drive from clone | **DENY** (T6 partial; CANARY-003) — clone must not expose backing disk |
| `EVIDENCE_ROOT` | **DENY** for non-TCB writer (H-EVID-001) |
| Non-allowlist network egress | **DENY** (T7) |
| `LAB_ROOT` interior | **ALLOW** (clone sandbox) |

**9P/DrvFs closure (R-031):** enforcement uses **FileId on the actual target handle**, not SID. Relay identity writes still DENY if FileId matches manifest — required negative test in Phase 4 exit.

**Verification:** `VERIFY_FINGERPRINT` post-blast — `Hn == H0`, deny-log shows ≥1 DENY and **0 ALLOW-write** on authority FileIds.

---

### P4-Q8 — What happens on daemon death?

**Spec anchor:** CANARY-005, `BOUNDARY_DEADMAN_GAP_S`, §14 T4, §3.1 HALT

1. Daemon emits heartbeat to `mmi_control_envelope` on interval **<** `BOUNDARY_DEADMAN_GAP_S` (30s).
2. On process kill, stall, or unrecoverable error:
   - Heartbeat gap exceeds 30s → **`M4-CANARY-005`** fires
   - Control envelope → **HALT** (fail-closed, not degrade-to-monitor)
   - HALT reason logged: `unpoliced_perimeter`
   - Current interval **not credited**; endurance clock unchanged for that interval
3. Runner cannot ARM without live daemon + manifest match (arm-time gate).
4. **No silent fail-open:** absence of daemon = unpoliced perimeter, same class as minifilter unload (see P4-Q9).

**T4 falsifier fixture:** inject kill/stop; assert HALT within gap bound; assert fingerprint intact if no ALLOW-write occurred.

---

### P4-Q9 — What happens on WFP or minifilter failure?

**Spec anchor:** §8 fail-closed, §14 T7, CANARY-022/005

| Failure mode | System response |
|--------------|-----------------|
| **WFP callout error / filter unload** | Treat as **unprotected egress** → fail-closed: stop ARMED intervals, HALT, log `wfp_unavailable` |
| **Minifilter detach / callback failure** | Treat as **unprotected writes** → dead-man path + CANARY-022 attestation mismatch → HALT |
| **Daemon cannot reach kernel bridge** | Refuse ARMED; if mid-run, dead-man T4 |
| **Signed manifest hash mismatch at load** | Daemon **refuses to start/arm** — no enforcement without valid manifest |
| **Policy manifest stale vs current H0** | Re-seal required before arm; mismatch → BLOCKED |

**Design rule:** there is **no** "monitor-only" degradation mode for min-viable. WFP/minifilter/daemon form a **single fail-closed enforcement triad**.

**T7 falsifier:** low-rate connect to non-allowlist endpoint → WFP deny → CANARY-018 → HALT; bytes + endpoint in deny log.

---

### P4-Q10 — What proves PC2 cannot mutate PC1 authority?

**Spec anchor:** dual-PC decision, R-030, §8 FileId, §14 T1/T2

Phase 4 min-viable proof is **layered** — full R-030 ops proof requires PC2 online; build slice proves **mechanism** on PC1:

| Layer | Proof artifact |
|-------|----------------|
| **Network (ops)** | Firewall/VLAN rules: no SMB admin share, no git push to live brain, no shared temp workflow; documented checklist before PC2 plug-in |
| **FileId enforcement (build)** | T1/T2 + 9P relay fixture — write attempts from clone/relay identity → DENY with FileId logged |
| **Mount policy** | Live authority not mapped into clone; CANARY-008 monitor |
| **Fingerprint** | `VERIFY_FINGERPRINT` — post-assault `Hn == H0` |
| **Evidence discipline** | Chain append + signing only on PC1 TCB; PC2 emits telemetry only |
| **Identity separation** | Clone SID/AppContainer excluded from daemon trust set and EVIDENCE_ROOT ACL |

**Honest residual:** Until PC2 assault traffic hits live boundary under dual-machine topology, R-030 remains **OPEN (ops)** even if PC1 min-viable slice passes. Phase 4 exit claim is: **"min-viable boundary slice on PC1 proven T1/T2/T4/T7"** — not **"PC2 isolation proven in production topology."**

**Recommended PC2 bring-up gate (ops, not code):** purple attempt from PC2 against PC1 authority path → expect DENY + logged CANARY; network packet capture showing no write-capable path to `AUTHORITY_ROOT` share.

---

## 3. Bounded build plan — Phase 4 sub-phases

Build order is **sequential**; each sub-phase has a Codex-reviewable exit before the next starts. No endurance until **4G** passes.

### 4A — Custody + attestation core

**Deliverables:** `KEY_CUSTODY` adapter (TPM/HSM), `stage_attestation` sign/verify/lineage, unit tests  
**Exit:** sign/verify round-trip; export fails; stale-H0 + mixed-lineage rejected; no keys in repo scan  
**Blocks:** 4B–4G

### 4B — Authority seal + policy manifest

**Deliverables:** `seal_fingerprint` FileId manifest generator; signed policy manifest pipeline; H0 pre-provision store to `EVIDENCE_ROOT`  
**Exit:** manifest lists all authority FileIds; hash mismatch refusal test; H0 signed before provision flag  
**Blocks:** 4C–4G

### 4C — Go daemon skeleton

**Deliverables:** `host_boundary/mmi_boundary_daemon/` — manifest load, arm/refuse, heartbeat, evidence bridge stub  
**Exit:** refuses arm on bad manifest; heartbeat visible to envelope stub; structured logs to `EVIDENCE_ROOT/boundary/`  
**Blocks:** 4D–4G

### 4D — Minifilter FileId enforcement

**Deliverables:** kernel minifilter + daemon comms; pre-op FileId resolution on target handle  
**Exit:** T1 PASS (DENY, 0 ALLOW); T2 PASS; 9P/relay FileId case PASS (R-031 mechanism)  
**Blocks:** 4E–4G

### 4E — WFP default-deny

**Deliverables:** WFP callout; clone SID allowlist (telemetry only)  
**Exit:** T7 PASS; unlisted egress deny logged  
**Blocks:** 4F–4G

### 4F — Dead-man + clock witness

**Deliverables:** envelope integration; T4 fixture; clock-witness skew detection  
**Exit:** T4 PASS (HALT `unpoliced_perimeter`); clock-witness live (CANARY-021 path wired, not full T10 endurance)  
**Blocks:** 4G

### 4G — Min-viable integration gate

**Deliverables:** `host_boundary_min_viable` probe; CLI/harness (`scripts/m4_boundary_min_viable.py` or equivalent — **named in plan only**); evidence bundle  
**Exit:** all §8 min-viable criteria green:

```text
host_boundary_min_viable == true  IFF
  T1 PASS AND T2 PASS AND T4 PASS AND T7 PASS AND
  signed_manifest_refusal PASS AND
  clock_witness_live AND
  VERIFY_FINGERPRINT PASS
```

**Codex diff review target:** Phase 4 CLEAN with assurance scope statement.

---

## 4. Evidence artifacts (Phase 4 exit)

| Artifact | Path (under `EVIDENCE_ROOT`) |
|----------|------------------------------|
| Boundary event log | `boundary/daemon.jsonl` |
| Minifilter deny capture | `boundary/minifilter_denies.jsonl` |
| WFP deny capture | `boundary/wfp_denies.jsonl` |
| T1/T2/T4/T7 fixture results | `boundary/falsifiers/T{1,2,4,7}_summary.json` |
| KEY_CUSTODY non-export proof | `boundary/key_custody_selftest.json` |
| Stage attestation unit results | `boundary/stage_attestation_tests.json` |
| Min-viable verdict | `boundary/host_boundary_min_viable.json` |

---

## 5. Residual risks after Phase 4 pass (honest)

Passing Phase 4 **mitigates mechanism** for R-001, R-008, R-031, R-032 at **min-viable scope** only. Rows remain **OPEN** until endurance + dual-PC ops proof:

| ID | After Phase 4 min-viable |
|----|--------------------------|
| R-001 | **MITIGATED (P4 min-viable)** for T1/T2 fixtures — OPEN for 48h assault |
| R-008 | **MITIGATED (P4 min-viable)** for instrumented escape — OPEN for novel vectors |
| R-031 | **MITIGATED (P4 min-viable)** for FileId relay fixture — OPEN for driver edge cases |
| R-032 | **MITIGATED (P4 min-viable)** for raw-open deny — OPEN for hypervisor-layer escape |
| R-030 | **OPEN (ops)** until PC2 firewall + assault proof |
| R-002 | **OPEN** until Phase 6+ live WFP production-endpoint classification under endurance |
| R-006, R-007 | **Partially addressed** by stage_attestation — OPEN until runner integration Phases 7–11 |

**Forbidden inference:** "authority untouchable," "containment proven," "M4 safe."

**Permitted inference:** "host_boundary_min_viable slice proven on PC1 per T1/T2/T4/T7; endurance not yet run."

---

## 6. Authority dependencies (no build auth here)

| Step | Owner | Status |
|------|-------|--------|
| P4-Q1..Q10 answered | Plan lane (this doc) | **DONE** |
| Codex plan review | Codex | **PENDING** → BUILDABLE \| NOT BUILDABLE |
| Matt `matt_auth_phase4` | Matt | **NOT AUTHORIZED** |
| Cursor build 4A→4G | Cursor | Blocked |
| Codex diff review | Codex | Blocked |
| Completion gate | Grok/Gemini audit_tools | Blocked |

---

## 7. Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-04 | Initial bounded Phase 4 plan; P4-Q1..Q10 answered |
