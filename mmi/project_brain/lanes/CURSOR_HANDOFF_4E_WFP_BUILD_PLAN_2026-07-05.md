# Cursor Handoff — Phase 4E WFP Build Plan (Codex Plan Review)

**Date:** 2026-07-05 (rev c — ALE-only live-proof correction)  
**Lane:** Cursor build plan → **Codex BUILDABLE gate** (hard stop before implementation)  
**Checkout:** `C:\Architectapp_clean` (build lane — **this file must exist here for Codex review**)  
**Prerequisites:** `4D_b_kernel_minifilter_live_verify_pc1` PASS filed; PM pipe extend  
**Parent plan BUILDABLE:** `CODEX_HANDOFF_M4_EVOLUTION_GATE_PLAN_REVIEW_PHASE4_2026-07-04.md` (2026-07-04) — does **not** auto-validate this 4E sub-plan  
**Spec anchors:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` §8, §14 T7, lines ~323, ~613  
**Parent plan §4E:** `MMI_M4_PHASE4_TCB_HOST_BOUNDARY_PLAN_2026-07-04.md` lines ~282–286  
**Audit mirror:** `mmi/project_brain/lanes/RESEARCH_M4_4D_B_TO_4E_PERFECTION_GAP_2026-07.md`  
**Cross-repo audit commit:** northstar `dc61670` — see `RESEARCH_FILING_CROSSREPO_4E_2026-07-05.md`

**Authority class:** `SPEC_PREP_AND_BUILD_PLAN` — **BUILD_AUTHORIZED: NO**

```text
4E_SPEC_PREP_ALLOWED_WITH_BLOCKERS_RECORDED
This authorizes scoped specification preparation only.
It does not prove boundary containment. It does not close M4.
It does not advance PERFECT. It does not authorize build.
```

---

## Non-inheritance (mandatory in all 4E artifacts)

```text
4E does not prove file-boundary containment.
4D_b does not prove network egress containment.
4D_b + 4E do not prove host containment, sandbox escape closure, PC2→PC1 closure, M4 closure, or PERFECT.
Claim supported only within explicitly tested scope; no cross-layer closure inferred.
```

---

## 1. Objective (4E slice only)

Implement **live WFP default-deny egress (T7)** on PC1:

- Intercept at `FWPM_LAYER_ALE_AUTH_CONNECT_V4/V6` only: four filters total (`allow/block` for V4 and V6). `FWPM_LAYER_STREAM_V4` is explicitly excluded from 4E Rev C because live install proved simple `BLOCK/PERMIT` filters at STREAM fail with `0x8032002C` (`FWP_E_ACTION_INCOMPATIBLE_WITH_SUBLAYER`).
- Default-deny from clone/AppContainer identity except **telemetry allowlist** from signed policy manifest
- Unlisted connect → **DENY** → append `boundary/wfp_denies.jsonl` → map to CANARY-018 path in 4G
- **Fail-closed** if WFP callout unavailable (P4-Q9 — no monitor-only mode)

**4E exit (this sub-phase only):**

```text
python scripts/m4_wfp_suite.py --live --json
→ top-level passed: true
→ selftest.min_viable_live_t7: true
→ selftest.wfp_loaded: true
→ selftest.live_t7_blocked: true
→ selftest.live_telemetry_ok: true
→ selftest.source_context_ok: true
→ selftest.contract_pass: true
```

**Not 4E exit:** `host_boundary_min_viable`, T4 dead-man, T1/T2 re-proof, Codex Phase 4 diff CLEAN, GATED.

---

## 2. Deliverables (files to create — not present at plan review)

| Path | Role |
|------|------|
| `host_boundary/mmi_wfp/` | User-mode WFP helper source/project and filter definitions (no kernel callout driver in Rev C) |
| `host_boundary/mmi_wfp/mmi_wfp_helper.cpp` / `.vcxproj` | User-mode helper build inputs |
| `scripts/build_m4_wfp.ps1` | Build (-TestSign); `FileDigestAlgorithm=sha256` |
| `scripts/install_m4_wfp.ps1` | Admin install (mirror 4D CAT staging + attach) |
| `scripts/uninstall_m4_wfp.ps1` | Remove driver + filters |
| `mmi/m4/wfp_policy.py` | Contract policy engine + live probe helpers |
| `scripts/m4_wfp_suite.py` | Harness CLI (this plan §4) |
| `tests/test_m4_wfp_policy.py` | Contract unit tests (no kernel) |
| `host_boundary/mmi_wfp/README.md` | Build/install/live + non-inheritance |

**Evidence (under `EVIDENCE_ROOT/boundary/`):**

| Artifact | Path |
|----------|------|
| Deny stream | `wfp_denies.jsonl` |
| Suite rollup | `wfp_suite_summary.json` |
| T7 falsifier | `falsifiers/T7_summary.json` |

---

## 3. WFP policy model (`mmi/m4/wfp_policy.py`)

### 3.1 Allowlist source

Load telemetry endpoint(s) from signed `policy_manifest.json` (reuse `load_policy_manifest` pattern from `minifilter_policy.py` / `boundary_daemon.py`).

Manifest must also declare **WFP rule target identity** (clone SID and/or AppContainer name — exact keys TBD; e.g. `clone_sid`, `app_container_name`).

Default dev stub: `127.0.0.1:9xxx` or manifest field `telemetry_egress_allowlist` (must be in signed manifest for live).

### 3.2 Contract evaluation (no kernel)

`evaluate_egress(destination, protocol, fixture_id)` → `PolicyVerdict` with:

- `decision`: `ALLOW` | `DENY`
- `rule_id`: e.g. `M4-WFP-ALLOW-TELEMETRY`, `M4-WFP-001-T7`
- Fields per perfection-gap §3: `test_id`, `policy_hash`, `destination`, `protocol`, `expected_action`, `observed_action` (contract: observed = policy decision)

### 3.3 Live helpers (P4E-B5 — source context)

**Rule:** WFP filters target **clone/AppContainer identity**, not an arbitrary harness process. Live T7 proof is **invalid** if probes run from Administrator/harness identity while WFP only filters clone SID.

```python
def resolve_live_source_context() -> dict[str, object]:
    """Return observed process name, SID string, AppContainer (if any), and namespace hint."""

def source_context_matches_policy(observed: dict, policy_manifest) -> bool:
    """True iff observed identity matches manifest clone/AppContainer target."""

def wfp_loaded(engine_name: str = "mmi_wfp") -> bool:
    """True iff user-mode WFP helper reports four active ALE_AUTH_CONNECT filters for engine_name."""

def attempt_live_connect(
    host: str,
    port: int,
    *,
    timeout_s: float = 3.0,
    required_source_context: dict | None = None,
) -> tuple[bool, str | None]:
    """Return (connect_succeeded, error_message). If required_source_context set and current identity mismatches, return (False, 'source_context_mismatch') without claiming T7 proof."""

def run_wfp_selftest(
    evidence_dir: Path,
    policy_manifest_path: Path,
    *,
    live: bool = False,
) -> dict[str, object]:
    ...
```

**Live-mode fail-closed:** If `source_context_matches_policy()` is **false**, set `source_context_ok: false` and **FAIL** live gate — do not run T7-L1/T7-L2 or treat results as T7 evidence.

**Implementation options (pick one in build, must document in README):**

1. Launch probe subprocess under clone/AppContainer identity (preferred), or  
2. Dedicated probe helper exe registered in manifest, or  
3. Fail closed with `source_context_ok: false` when harness cannot assume clone identity (acceptable for plan; live PASS blocked until probe runner exists).

---

## 4. Harness contract (`scripts/m4_wfp_suite.py`)

Mirrors `scripts/m4_minifilter_suite.py` structure.

### 4.1 CLI

```
python scripts/m4_wfp_suite.py [--authority PATH] [--evidence PATH]
                               [--policy-manifest PATH] [--live] [--json]
```

Exit codes: `0` = PASS, `1` = FAIL, `2` = missing prerequisites.

### 4.2 Top-level JSON envelope

Standard fields: `harness`, `phase`, `spec_section`, `passed`, `perfect_claim: false`, `evidence_dir`, `sealed_at_utc`, `selftest`.

### 4.3 `selftest` object (required keys)

| Key | Contract mode | Live mode |
|-----|---------------|-----------|
| `schema_v` | `"2026-07-05b"` | same |
| `mode` | `"contract"` | `"live"` |
| `wfp_loaded` | `false` (or query if cheap) | **must be `true` for PASS; helper status must report `filter_count >= 4`** |
| `contract_pass` | allow + deny fixtures pass | must stay `true` |
| `source_context_ok` | `null` | **must be `true` for PASS** |
| `live_t7_blocked` | `null` | **must be `true` for PASS** |
| `live_telemetry_ok` | `null` | **must be `true` for PASS** |
| `min_viable_live_t7` | `false` | see §4.4 formula |
| `contract` | `{ verdicts: [...] }` | same |
| `policy_hash` | from manifest | same |
| `observed_source_context` | `null` | dict with SID/AppContainer/process |

### 4.4 PASS/FAIL logic (P4E-B4 fix)

```python
min_viable_live_t7 = (
    live
    and wfp_loaded
    and source_context_ok
    and live_t7_blocked is True
    and live_telemetry_ok is True
    and contract_pass
)

passed = selftest["contract_pass"] is True
if args.live:
    passed = passed and selftest["min_viable_live_t7"] is True
```

**Invariant:** `live_telemetry_ok` and `source_context_ok` are **required** for live PASS — not optional telemetry metadata.

No `verify_fingerprint` in 4E v1 (egress probes must not mutate authority tree).

### 4.5 Contract fixtures (T7-C*)

| fixture_id | destination | expected |
|------------|-------------|----------|
| T7-C1 | non-allowlist IPv4 (e.g. `203.0.113.1:443`) | DENY |
| T7-C2 | allowlisted telemetry endpoint | ALLOW |
| T7-C3 | non-allowlist loopback high port | DENY |

### 4.6 Live fixtures (T7-L*)

| fixture_id | probe | expected live |
|------------|-------|---------------|
| T7-L1 | TCP connect to controlled local non-allowlist listener (`127.0.0.1:19999`) from **matched clone context** | blocked/timeout under local listener control → `live_t7_blocked: true` |
| T7-L2 | TCP connect to controlled local allowlisted telemetry listener (`127.0.0.1:9443`) from **matched clone context** | succeeds → `live_telemetry_ok: true` |

### 4.7 Deny log line schema (`wfp_denies.jsonl`) — P4E-B6

Each line JSON object **must** include (perfection-gap audit §3 + plan):

```text
test_id
policy_hash
active_rule_snapshot
source_process
source_namespace_or_context
destination
protocol
expected_action
observed_action
rule_id
event_log_pointer
timestamp_utc
timestamp_source
pass_fail
residual_risk_link
```

Field mapping:

| Field | Source |
|-------|--------|
| `source_namespace_or_context` | AppContainer name, clone SID, or `process@SID` string |
| `event_log_pointer` | WFP audit/event record id, ETW handle, or `wfp_event_{seq}` path under evidence |
| `timestamp_source` | e.g. `utc_system`, `evidence_sealed_at`, `wfp_audit_timestamp` |

`residual_risk_link`: `"R-001"`, `"R-002"` — not closure claims.

---

## 5. T7 negative tests (perfection-gap §3)

T7-N1..N7 unchanged (default-deny, IPv4/IPv6, DNS, loopback, proxy, WFP unload fail-closed).

---

## 6. Fail-closed (P4-Q9 + P4E-B5)

| Condition | Suite behavior |
|-----------|----------------|
| WFP callout not installed | `wfp_loaded: false` → live **FAIL** |
| WFP engine stopped | live **FAIL** |
| Missing policy manifest | exit code `2` |
| **Source context mismatch** | `source_context_ok: false` → live **FAIL** (no T7 inference) |
| **Allowlist connect fails** | `live_telemetry_ok: false` → live **FAIL** |

---

## 7. Build sequence (after Codex BUILDABLE + Matt authorize)

1. `wfp_policy.py` + contract tests  
2. `m4_wfp_suite.py` contract mode  
3. User-mode WFP helper + install scripts (`ALE_AUTH_CONNECT_V4/V6`, four-filter expectation)  
4. Clone-context probe runner + controlled local live gate (`127.0.0.1:19999` deny, `127.0.0.1:9443` allow)  
5. **STOP** — no 4F/4G in same pass  

---

## 8. Residual risk posture

Unchanged — R-001/R-002 scoped REDUCED only; R-008/R-030/R-031 OPEN constraints unchanged.

---

## 9. Codex plan review — blocker resolution

| Blocker | Resolution |
|---------|------------|
| P4E-B1 | Handoff present in Architectapp_clean checkout |
| P4E-B2 | §4 defines `m4_wfp_suite` contract |
| P4E-B3 | Cross-repo filing note + audit mirror |
| **P4E-B4** | §4.4: `min_viable_live_t7` requires `live_telemetry_ok`; PASS logic explicit |
| **P4E-B5** | §3.3 + §6: `source_context_ok` required; fail-closed on identity mismatch |
| **P4E-B6** | §4.7: deny log adds `source_namespace_or_context`, `event_log_pointer`, `timestamp_source` |

**Verdict requested:** `BUILDABLE` | `NOT BUILDABLE`

**If BUILDABLE:** Matt `authorize build 4E` → Cursor implements → STOP until 4G for Codex diff.

---

## 10. Explicit non-claims

```text
NOT CLAIMED: file-boundary containment, host containment, M4_MET, GATED, PERFECT,
containment-proven, PC2 isolation, R-031 CLOSED, build authorized from this document alone.
```


---

## 11. Rev C Codex PM Note

Codex prior verdict: `NOT BUILDABLE as written`.

Rev C resolves the build-plan blockers by narrowing 4E to the live-proven shape:

- `ALE_AUTH_CONNECT_V4/V6` only.
- Four filters expected: V4 allow, V4 block, V6 allow, V6 block.
- User-mode WFP helper scope; no kernel callout driver claim.
- Controlled local live probes for T7-L1/T7-L2.
- `BUILD_AUTHORIZED: NO` remains unchanged.

Rev C is still plan/spec preparation only. It does not authorize implementation, does not close M4, and does not claim host containment.

Codex Rev C verdict: `BUILDABLE AS PLAN`.

Build remains blocked until Matt explicitly says `authorize build 4E`.
