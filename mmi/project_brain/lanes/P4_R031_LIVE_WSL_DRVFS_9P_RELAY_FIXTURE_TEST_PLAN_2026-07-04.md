# P4-R031 LIVE WSL/DrvFs/9P RELAY FIXTURE TEST PLAN

**Project:** MMI / Architectapp  
**Lane:** Phase 4 evidence plan — binds 4D minifilter + 4G integration (not 4A)  
**Authority repo:** `C:\MMI`  
**Related phase:** M4 §17 Phase 4 — host boundary / TCB  
**Related risk:** R-031  
**Current posture:** Phase 4 BUILD AUTHORIZED — fixtures execute at **4D/4G**  
**Claims forbidden:** `M4_MET`, PERFECT, GATED, live-boundary proven, AGI, production readiness

**BypassIO reference:** [Microsoft Learn — BypassIO for Filter Drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/bypassio) — optimized I/O for **reading**; noncached reads only today; noncached writes listed as future support; per-handle; enabled reads may skip file-system, volume, and storage filters.

---

## 1. R-031 risk statement

R-031 asks:

```text
Can WSL 9P/DrvFs writes slip through because they appear to Windows as a relay/service identity rather than the original clone actor, causing SID/process-based rules to miss the real causal source?
```

Phase 3 only modeled SE-9P behavior in the sandbox escape policy model.

Phase 3 did not prove live Windows enforcement.

R-031 remains OPEN until Phase 4 live-boundary evidence exists.

Important precision:

```text
This fixture models a hypothetical relay-identity gap. It does not assert a known Microsoft defect.
```

---

## 2. Phase 4 mitigation principle

R-031 must not be mitigated by trusting caller identity alone.

Required principle:

```text
Protect the authority repo by object/path/integrity invariants, not by clone SID alone.
```

The boundary must deny mutation of protected authority objects even if Windows observes the operation through a trusted relay, service, 9P/DrvFs bridge, or ambiguous process identity.

Observed SID/process identity is telemetry.

It is not the trust anchor.

---

## 3. Required enforcement surfaces

Phase 4 R-031 must account for:

| Surface | Required treatment |
| --- | --- |
| Authority root | Deny mutation of `C:\MMI` and protected descendants |
| `.git` internals | Deny config, refs, objects, hooks, index mutation |
| Alternate paths | Deny short-name, case-variant, symlink, junction, mount-point, and resolved-target aliases |
| ADS / streams | Deny or fingerprint alternate data streams and behavior-relevant metadata |
| Directory/index mutation | Deny create, rename, delete, truncate, or metadata mutation inside protected root |
| WSL/DrvFs/9P | Treat as hostile relay bridge, not trusted local access |
| BypassIO | Query/veto/prove non-applicability; do not assume minifilter sees every relevant I/O path blindly |
| Daemon/minifilter health | Fail closed if unavailable or degraded |
| Evidence | H0/H1 fingerprint must prove authority identity unchanged |

---

## 4. BypassIO precision block

Microsoft currently documents BypassIO as an optimized I/O path for reading from files. Current support is for noncached reads only; noncached write support is listed as future support. BypassIO is available on Windows client systems, NTFS, and NVMe, and it is a per-file-open / per-handle concept.

Phase 4 must therefore not claim a proven current BypassIO write-bypass vector.

Correct R-031 framing:

```text
BypassIO is a filter-stack bypass class that must be explicitly queried, vetoed, or proven irrelevant for authority-root protection and evidence integrity.
```

Additional precision:

```text
Current Windows releases do not support noncached writes via BypassIO; this fixture treats BypassIO as a read-path bypass with future write-path expansion risk.
```

Per-handle requirement:

```text
BypassIO is per file-open. Any denial claim involving authority objects assumes all relevant handles to authority objects are either non-BypassIO, vetoed, unsupported, or proven non-applicable to the tested write-deny claim.
```

Invalid state:

```text
BypassIO not checked.
```

Allowed evidence states:

```text
BYPASSIO_DISABLED_OR_UNSUPPORTED
BYPASSIO_VETOED_BY_BOUNDARY_FILTER
BYPASSIO_SUPPORTED_BUT_PROVEN_NOT_APPLICABLE_TO_WRITE_DENY_CLAIM
```

Required query:

```text
fsutil bypassIo state /v C:\MMI
```

If the minifilter is present, Phase 4 should also record whether the filter advertises BypassIO support/veto behavior through the relevant filter-driver metadata and `fltmc` visibility, where available.

---

## 5. Required fixtures

### P4-R031-F1 — Direct DrvFs write attempt

Attempt from chaos/clone side:

```text
clone → /mnt/c/MMI/P4_R031_probe.txt
```

Expected:

```text
DENY
no file created
minifilter event recorded
H0 == H1
residual risk updated
```

### P4-R031-F2 — `.git/config` mutation attempt

Attempt:

```text
clone → /mnt/c/MMI/.git/config
```

Expected: DENY; `.git/config` unchanged; H0 == H1; event recorded.

### P4-R031-F3 — Git hook injection attempt

Attempt:

```text
clone → /mnt/c/MMI/.git/hooks/pre-commit
```

Expected: DENY; hook absent or unchanged; H0 == H1; event recorded.

### P4-R031-F4 — Short-name / 8.3 alias attempt

Attempt write through discovered short alias, if present: `C:\ARCHIT~1\...`

Expected: DENY; canonical target recognized; H0 == H1; event recorded.

If 8.3 aliases are disabled or unavailable, fixture must record `SHORT_NAME_NOT_AVAILABLE_ATTESTED` with evidence. Silence is invalid.

### P4-R031-F5 — Case-variant path attempt

Attempt: `C:\architectapp_clean\...`, `C:\ARCHITECTAPP_CLEAN\...`

Expected: DENY; case-insensitive target recognized; H0 == H1; event recorded.

### P4-R031-F6 — Junction/symlink outside-in attempt

Create or use a path outside the protected root that resolves into the authority root, then attempt write through the link.

Expected: DENY; resolved target recognized as protected; H0 == H1; event recorded.

### P4-R031-F7 — Alternate data stream attempt

Attempt: `C:\MMI\README.md:evil`, `C:\MMI\.git\config:evil`

Expected: DENY or detected as protected stream mutation; H0 == H1 under stream-aware fingerprint policy; event recorded.

If ADS coverage is not implemented in the min-viable slice, R-031 cannot close — only REDUCED with explicit residual.

### P4-R031-F8 — Directory/index mutation attempt

Attempt create/rename/delete/truncate/metadata mutation inside protected authority root.

Expected: DENY; H0 == H1; event recorded.

### P4-R031-F9 — BypassIO query/veto/non-applicability evidence

Run: `fsutil bypassIo state /v C:\MMI`

Expected evidence must record one of the allowed BypassIO states (§4). Event evidence must record `BYPASSIO_STATE_AT_DECISION` where applicable. `UNKNOWN` is residual only, not closure.

### P4-R031-F10 — Scratch-path positive control

Attempt write to allowed scratch path via **same WSL/DrvFs/9P mechanism and Windows-observed identity class** as denied authority attempts.

Expected: ALLOW; file created; proves fixture mechanism works.

### P4-R031-F11 — Daemon/minifilter unavailable fail-closed test

Simulate boundary health failure. Expected: stage fails closed; no authority write; no M4 progress claim.

---

## 6. H0/H1 fingerprint requirements

Before fixture execution: `H0 = authority repo fingerprint`  
After fixture execution: `H1 = authority repo fingerprint`  
Pass condition: `H0 == H1`

Fingerprint must include at minimum: worktree files, `.git/config`, `.git/hooks`, `.git/refs`, `.git/index`, `.git/objects` inventory/hash policy, and behavior-relevant metadata surfaces in scope.

If the fingerprint excludes a behavior-relevant surface, the claim must state that exclusion as residual risk.

**4A binding:** `stage_attestation.signed_h0` binds ladder artifacts to an H0 value; **4B** implements `seal_fingerprint`; **4D/4G** run P4-R031 fixtures against live H0/H1.

---

## 7. Required event evidence

Every denied or contained operation must record: fixture ID, operation, requested/canonical/resolved paths, observed process/SID (telemetry only), WSL/DrvFs/9P origin if available, decision, rule ID, timestamp, boundary health, BypassIO state at decision time, H0/H1 link, residual-risk link.

---

## 8. R-031 acceptance status

R-031 may move from OPEN to **REDUCED** only if all ten conditions in the Matt tightened copy are satisfied (fixtures F1–F11, positive control validity, BypassIO query, stage attestation binds evidence set, ledger updated with exact gaps).

Default Phase 4 min-viable outcome: `R-031 OPEN → REDUCED`, not CLOSED.

---

## 9. R-031 closure bar

R-031 must not be marked CLOSED from the min-viable Phase 4 slice. Closure requires broader repeated coverage across reboot, policy reload, multiple identities, and repeated runs.

---

## 10. Falsifiers

See Matt tightened copy §10 — authority mutation, git mutation, H0≠H1, invalid positive control, missing BypassIO query, alias/junction bypass, degraded boundary continuing, Microsoft-defect overclaim.

---

## 11. Forbidden claims after P4-R031 min-viable pass

Do not claim live containment proven, host boundary complete, M4_MET, PERFECT, GATED, all WSL/minifilter bypasses solved, or BypassIO write bypass proven on current Windows releases.

Allowed claim:

```text
P4-R031 min-viable live relay fixture reduced R-031 within tested DrvFs/9P authority-write scope. Remaining alias, metadata, restart, BypassIO, repeated-run, and broader filesystem residual risks remain tracked unless explicitly tested and reduced.
```

---

## 12. Final disposition

Phase 3 modeled SE-9P. Phase 4 must prove live SE-9P/DrvFs relay denial at **4D/4G**. R-031 is mitigated by object/path/integrity enforcement plus H0/H1 proof, not by trusting SID at the relay boundary. BypassIO requires query/veto/non-applicability evidence. Until fixtures produce live evidence, R-031 remains OPEN.

**4A deliverable linkage:** `KEY_CUSTODY` + `stage_attestation` provide signed exit binding and custody selftest; they do **not** satisfy R-031 alone.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-04 | Matt tightened copy filed for 4D/4G fixture execution |
