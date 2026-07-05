# MMI Control Envelope — Budget Ceiling + Dead-Man Switch Spec (2026-07) — REV A (adversarial self-review applied)

**File target:** `mmi/project_brain/architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md`
**Module target:** `chaos/mmi_control_envelope.py` (EXTEND — additive to `MMIControlEnvelope`)
**Harness target:** `scripts/control_envelope_harness.py` (name fixed by task)
**Doctrine:** MMI_AGI_EVOLUTION_PATHWAY §2 Pillar 2 (guardrails), §5 step 3, §6 non-goals — bounded autonomy, deterministic rules, un-fakeable metrics.
**Status:** Design spec only. BUILD AUTHORIZATION: NOT_AUTHORIZED.
**Gate context:** Evolution gate OUTSTANDING — 48h proof NOT built; this spec does not claim PERFECT and does not unblock M4.
**Threat model (this revision):** a hostile operator OR the governed loop itself, with full
write access to `/tmp` state files and the ability to call the envelope API with chosen
arguments. Consequence: the loop cannot be trusted to report its own attendance, and any state
file the loop can write, the loop can forge. Every rule below is re-derived so the *stop*
decision does not depend on loop-supplied truth.
**Revision:** REV A — fixes: (1) counter-reset / ledger-emptying via monotonic lifetime spend
seal (§1.2, §4); (2) loop self-acking the dead-man via `record_heartbeat(ack=True)` — ack
channel separated from liveness, loop can no longer assert human attendance (§1.3, §3);
(3) post-verdict continued execution via sticky HALT/SUSPEND latch (§3 rule 4, §1.4);
(4) `now_ms` spoofing hardened to test-only (§3 rule 1); (5) restart counter tamper via same
monotonic seal (§1.2).

---

## 1. Operational Definition

This spec extends `MMIControlEnvelope` from an output-shape validator into a **loop
governor**: the deterministic authority that decides, *before every self-directed
iteration*, whether the loop may run at all. Two independent kill conditions, either
sufficient to stop the loop:

- **Budget ceiling** — metered spend allowance per rolling hour and per rolling day. Breach ⇒
  `SUSPENDED`. Economic bound: a runaway loop cannot burn unbounded resource.
- **Dead-man switch** — the loop must see a fresh **human** ack and must not exhibit runaway
  patterns (cost spike, restart-loop). Stale ack or runaway ⇒ `HALTED`. Attendance bound: an
  unattended or thrashing loop cannot keep running.

Both are **fail-closed**: any error, missing file, unreadable state, or *detected tamper*
resolves to STOP, never "continue." No decision is ever a soft score — each is a
named-constant comparison with a boolean outcome.

Design invariants: **no silent overspend**, **no unattended loop without a human ack**, and
(REV A) **no self-attested attendance and no counter that can move backward.**

### 1.1 Unit choice — tokens, not compute cycles

`SPEND_UNIT = tokens`. Justification: tokens are the un-fakeable, gate-observable unit —
counted at the model boundary the envelope already sits on, deterministic per request, mapping
directly to cost. Compute cycles are host-dependent and not observable from the envelope's
position without trusting host telemetry (`kinetic_telemetry.py` is lab economics, explicitly
NOT a kill-switch — §2). One unit, counted where the envelope can see it. [^1]

### 1.2 Monotonic seal — defeats counter-reset and ledger-emptying (REV A)

Rolling windows alone are insufficient: an attacker who truncates the ledger to `events: []`
produces a schema-valid file that reads as *zero spend*, resetting the ceiling. Rolling-window
math cannot tell "genuinely idle" from "counter wiped."

Fix: the ledger carries a **monotonic `lifetime_spend`** and a **monotonic `lifetime_starts`**
that only ever increase. On load, the envelope compares the on-disk seal against a
last-known-good seal cached in the separate heartbeat state (and vice-versa — the two files
cross-witness each other). Any *decrease* in either monotonic counter, or a rolling-window sum
that exceeds `lifetime_spend`, is `LEDGER_TAMPER` ⇒ fail-closed STOP. Rolling windows still
drive the cap decision; the seal only detects rollback. This makes "split spend across windows
then wipe the counter" observable — the wipe shows up as a lifetime decrease even though the
window sum drops. [^3]

### 1.3 Ack channel ≠ liveness channel — defeats self-acking (REV A)

The prior draft's `record_heartbeat(ack: bool)` let the loop pass `ack=True` and certify its
own human attendance — the dead-man's core failure. Fix: two separate facts, two separate
writers.

- **Liveness** (`last_heartbeat_ms`) is loop-written — proves the *process* is alive. Useful
  only for restart/runaway math; it NEVER satisfies the attendance requirement.
- **Human ack** (`last_ack_ms` + `ack_seq`) is written ONLY through an ack channel the loop is
  not permitted to write: a human increments a strictly-monotonic `ack_seq` out-of-band (file
  written by a human/console, or step-4 Ed25519 signed). Attendance is satisfied iff `ack_seq`
  has advanced within `ACK_STALE_MS`. A stale-or-unchanged `ack_seq` is `STALE_ACK` even if the
  loop is writing liveness every tick. `record_heartbeat()` therefore takes **no `ack`
  argument** — the loop cannot assert human presence. [^2]

### 1.4 Sticky stop latch — defeats post-verdict execution (REV A)

A verdict the caller can ignore is not a control. Fix: on any `SUSPENDED`/`HALTED`, the
envelope writes a **latch file** (`STOP_LATCH_PATH`) recording verdict + reason + evidence
path. While the latch exists, `pre_iteration_gate` returns the latched stop **regardless** of
current budget/heartbeat readings. A `SUSPENDED` latch clears only on a human window-reset ack;
a `HALTED` latch clears ONLY on a human evidence-acknowledged resume (advancing a dedicated
`resume_seq`) — never on a timer, never by the loop. This removes the "wait for the window to
roll, then resume myself" path.

### Constants (spec-fixed; changes require spec revision, not config edit)

| Constant | Value | Meaning |
|---|---|---|
| `SPEND_UNIT` | `tokens` | Accounting unit (justification §1.1) |
| `DEFAULT_PER_HOUR_CAP` | 800,000 tokens | Rolling-1h ceiling (Matt signed 2026-07-03 — 1/10 of day cap for burst) |
| `DEFAULT_PER_DAY_CAP` | 8,000,000 tokens | Rolling-24h ceiling (Matt signed 2026-07-03 — Full Matrix headroom) |
| `HOUR_WINDOW_MS` | 3,600,000 | Rolling hour |
| `DAY_WINDOW_MS` | 86,400,000 | Rolling day |
| `HEARTBEAT_INTERVAL_MIN` | 15 | Liveness/check cadence N (Matt lock) |
| `HEARTBEAT_INTERVAL_MS` | 900,000 | = N × 60,000 |
| `ACK_STALE_MS` | 1,800,000 | Human ack older than 2× interval ⇒ stale ⇒ HALT |
| `RUNAWAY_SPIKE_FACTOR` | 4 | Iteration spend > 4× trailing mean ⇒ runaway |
| `RUNAWAY_SPIKE_MIN_SAMPLES` | 5 | Trailing-mean warm-up before spike test arms |
| `RESTART_WINDOW_MS` | 900,000 | Restart-loop detection window (= one interval) |
| `RESTART_MAX_COUNT` | 3 | > 3 process starts in `RESTART_WINDOW_MS` ⇒ runaway |
| `EVIDENCE_ROOT` | `/tmp/mmi_control_envelope/<run_id>/EVIDENCE/` | All artifacts; outside authority repo |
| `LEDGER_PATH` | `/tmp/mmi_control_envelope/state/spend_ledger.json` | Spend state; outside authority repo |
| `HEARTBEAT_PATH` | `/tmp/mmi_control_envelope/state/heartbeat.json` | Liveness + ack + seal witness |
| `STOP_LATCH_PATH` | `/tmp/mmi_control_envelope/state/stop_latch.json` | Sticky stop latch (§1.4) |

---

## 2. Boundary vs Adjacent Systems

- **`enforce_boundary()` v0 (same class):** validates a single agent *output* (volumetric,
  forbidden-directive, JSON-schema). Unchanged. Budget/dead-man govern the *loop*, not the
  output — orthogonal axes on the same object. No v0 code path is modified (§3 rule 5).
- **`proof_gate_harness.py` (Gate B):** evidence-outside-authority pattern. This spec's
  harness **mirrors** it but is a *separate* harness — it does not extend or re-run Gate B.
- **`kinetic_telemetry.py` (AFE ledger):** lab economics / accounting display. **Not a
  kill-switch, not a trust source, and never read by the budget module.** The budget module
  maintains its own sealed ledger; a compromised or absent AFE cannot disable, feed, or relax
  the ceiling. Confusing AFE display numbers with enforcement is a defect (§7).
- **Future `console_server.py` (AGI step 4, Ed25519 ack):** OUT OF SCOPE. File-based ack is
  interim; the §1.3 ack-channel interface is shaped so step 4 swaps the human-writer for a
  signed writer without touching budget/heartbeat/latch logic.

---

## 3. Pass / Fail Lines

### Budget ceiling

| Condition | Verdict | Action |
|---|---|---|
| Rolling-1h ≤ `per_hour_cap` AND rolling-24h ≤ `per_day_cap` AND seal intact | `BUDGET_OK` | iteration permitted |
| Rolling-1h > `per_hour_cap` OR rolling-24h > `per_day_cap` | `SUSPENDED` | latch + alert artifact; resume only via human window-reset ack |
| Ledger unreadable / corrupt / missing on an established run | `SUSPENDED`, `reason=LEDGER_FAULT` | fail-closed |
| `lifetime_spend`/`lifetime_starts` decreased, or window sum > lifetime, or cross-witness mismatch | `SUSPENDED`, `reason=LEDGER_TAMPER` | fail-closed (§1.2) |

### Dead-man switch

| Condition | Verdict | Action |
|---|---|---|
| `ack_seq` advanced within `ACK_STALE_MS` AND no runaway | `HEARTBEAT_OK` | iteration permitted |
| `ack_seq` age > `ACK_STALE_MS`, unchanged, or heartbeat/ack missing | `HALTED`, `reason=STALE_ACK` | latch + evidence bundle |
| Iteration spend > `RUNAWAY_SPIKE_FACTOR` × trailing mean (≥ `RUNAWAY_SPIKE_MIN_SAMPLES`) | `HALTED`, `reason=RUNAWAY_COST_SPIKE` | latch + evidence bundle |
| `lifetime_starts` delta > `RESTART_MAX_COUNT` within `RESTART_WINDOW_MS` | `HALTED`, `reason=RESTART_LOOP` | latch + evidence bundle |
| Heartbeat state unreadable / corrupt / seal mismatch | `HALTED`, `reason=HEARTBEAT_FAULT` | fail-closed |

Combined pre-iteration verdict: if a stop latch exists, it is returned verbatim (§1.4);
otherwise `PROCEED` **iff** `BUDGET_OK` AND `HEARTBEAT_OK`; otherwise the strongest stop wins
(`HALTED` > `SUSPENDED`) and the loop does not iterate.

Hard rules:

1. **Fail-closed, always — including clock.** Any missing/corrupt/ambiguous/tampered state ⇒
   STOP. In production `now_ms` is read from the gate wall clock ONLY; the parameter exists in
   test builds and any production build MUST ignore caller-supplied `now_ms` (a loop passing a
   backdated clock to freshen ack or age-out spend is a fail-open regression). [^2]
2. **No silent overspend.** A budget breach MUST write the alert artifact AND the latch before
   returning; a `SUSPENDED` verdict with no artifact/latch on disk is a defect, not a pass.
3. **No unattended loop, no self-acking.** Attendance = a human-advanced `ack_seq` within
   window (§1.3). Absence of ack state is `STALE_ACK`. The loop cannot set, forge, or advance
   `ack_seq`; liveness writes never satisfy attendance.
4. **Stops are sticky (§1.4).** `HALTED` clears only on a human-advanced `resume_seq` with an
   evidence acknowledgement; `SUSPENDED` clears only on a human window-reset ack. Neither
   auto-clears on a timer or by loop action. While latched, `pre_iteration_gate` never returns
   `PROCEED`.
5. **v0 preserved, additive only.** `__init__` keeps `max_token_length=2048` default;
   `enforce_boundary(raw_agent_output, expected_schema) -> (bool, str)` signature and behavior
   unchanged; `metadata_ingress_gate.py` references must not break. New methods are additive.
6. **Deterministic constants only.** Every threshold is a named constant (§1). No ML, no soft
   scoring, no self-retuning of caps, intervals, or thresholds by the loop.

### New API (additive to `MMIControlEnvelope`)

```python
# Budget
def record_spend(self, amount: int) -> None: ...          # advances lifetime_spend seal
def check_budget(self) -> tuple[bool, dict]:
    # (ok, {"verdict": "BUDGET_OK"|"SUSPENDED", "reason": ...,
    #       "hour_spend": ..., "day_spend": ..., "alert_path": ...})

# Dead-man
def record_heartbeat(self) -> None: ...                   # liveness only; NO ack argument
def check_heartbeat(self) -> tuple[bool, dict]:
    # (ok, {"verdict": "HEARTBEAT_OK"|"HALTED", "reason": ...,
    #       "ack_seq": ..., "last_ack_ms": ..., "evidence_path": ...})

# Combined pre-iteration gate (the one a loop calls)
def pre_iteration_gate(self) -> tuple[bool, dict]:
    # honors STOP_LATCH first; then budget + heartbeat
    # (proceed, {"verdict": "PROCEED"|"SUSPENDED"|"HALTED", "budget": {...},
    #            "heartbeat": {...}, "latched": bool, "evidence_path": ...})

# Human-only channels (loop has no method to advance these; written out-of-band / step-4 signed)
#   ack_seq  -> attendance
#   resume_seq -> clears a HALT latch with evidence acknowledgement
#   window_reset -> clears a SUSPENDED latch
```

`now_ms` injection (test builds only) is omitted from the production signatures above to make
rule 1 structurally enforced, not merely documented.

---

## 4. Data Schema (persisted state — never in authority repo)

Atomic write: temp in same dir → `os.replace()` → durable rename. `os.replace` is atomic on
POSIX, so a crash mid-write cannot leave a half-written ledger reading as low spend (a
silent-overspend path) — the reader sees old-complete or new-complete, never torn. [^3]

Spend ledger (`LEDGER_PATH`) — rolling events + monotonic seal:

```json
{
  "schema_version": 2,
  "run_id": "2026-07-02T14-03-11Z-ab12",
  "lifetime_spend": 3712000,
  "lifetime_starts": 2,
  "events": [ {"ts_ms": 1751406000123, "amount": 1024} ]
}
```

Events older than `DAY_WINDOW_MS` pruned on every `record_spend`; hour/day spend are sums over
the sub-windows. `lifetime_spend`/`lifetime_starts` never decrease and are cross-witnessed by
heartbeat state (§1.2). Bounded by cap ÷ min-charge, not by uptime.

Heartbeat state (`HEARTBEAT_PATH`):

```json
{
  "schema_version": 2,
  "last_heartbeat_ms": 1751406000123,
  "last_ack_ms": 1751405900000,
  "ack_seq": 41,
  "resume_seq": 3,
  "recent_starts_ms": [1751405000000, 1751405400000],
  "trailing_spend": [1000, 1100, 980, 1050, 1020],
  "witness_lifetime_spend": 3712000,
  "witness_lifetime_starts": 2
}
```

`recent_starts_ms` pruned to `RESTART_WINDOW_MS`; `trailing_spend` is a fixed-length ring — O(1)
per tick, never O(iterations). `witness_*` mirror the ledger seal for cross-check.

Stop latch (`STOP_LATCH_PATH`) — presence = stopped:

```json
{ "verdict": "HALTED", "reason": "STALE_ACK", "since_ms": 1751406900000,
  "evidence_path": "/tmp/mmi_control_envelope/<run>/EVIDENCE/halt_...json",
  "clears_on": "resume_seq>=4" }
```

Halt/suspend evidence bundle under `EVIDENCE_ROOT`:

```json
{ "verdict": "HALTED", "reason": "STALE_ACK", "detected_ts_ms": 1751406900000,
  "last_heartbeat_ms": 1751406000123, "last_ack_ms": 1751405900000, "ack_seq": 41,
  "hour_spend": 412000, "day_spend": 3300000,
  "constants_snapshot": {"ACK_STALE_MS": 1800000, "per_hour_cap": 500000} }
```

All four paths are canonicalized and asserted **outside the authority repo** before any write;
a target resolving inside `/mnt/c/Architectapp_clean`, or reachable via symlink into it, is a
fail-closed abort, not a warning. [^4]

---

## 5. Integration Sketch

Pre-iteration call order for any future self-directed loop (loop is NOT built here):

```
loop tick
  → envelope.pre_iteration_gate()
        ├─ STOP_LATCH present?  → return latched SUSPENDED/HALTED (no further checks)
        ├─ check_heartbeat()    # STALE_ACK / RUNAWAY_* → HALTED (+latch)
        └─ check_budget()       # cap breach / tamper → SUSPENDED (+latch)
  → verdict == PROCEED ?
        ├─ NO  → evidence bundle already written; STOP loop; surface artifact path
        └─ YES → run ONE iteration
                   → envelope.record_spend(tokens_used)     # advances seal
                   → envelope.record_heartbeat()            # liveness only
  → next tick
   # human ack_seq / resume_seq / window_reset arrive out-of-band, never from the loop
```

Ordering rationale: latch first (a stopped loop stays stopped), then heartbeat/halt before
budget (an unattended or thrashing loop must stop even if under budget; HALT outranks SUSPEND),
then budget. `record_spend` runs after the iteration with actual tokens so the next tick
reflects real spend. The gate is the loop's only entry permission; no code path runs an
iteration without a live `PROCEED`. Orchestrator wiring is out of scope (§7).

---

## 6. Falsifiable Test Scenarios

Harness `scripts/control_envelope_harness.py` mirrors `proof_gate_harness.py`: authority repo
read-only throughout; all evidence/state under the `/tmp` roots; exit 0 with JSON verdict
carrying `overall_gate_status`; asserts every write path outside authority before writing.
pytest runs the same scenarios headless.

**T1 — Budget breach + counter-reset attempt → SUSPENDED (falsifies no-silent-overspend AND
seal, §1.2):**
Fresh run, fresh ack. `record_spend` accumulates to `per_hour_cap + 1`. Expected:
`proceed=False`, `verdict=SUSPENDED`, hour-cap reason; alert artifact AND stop latch EXIST; no
iteration permitted. Then the attacker rewrites the ledger to `events: []` (window sum → 0) while
leaving `lifetime_spend` unchanged is impossible without lowering it: setting `lifetime_spend`
below the witness → `reason=LEDGER_TAMPER` (still SUSPENDED); leaving it high while emptying
events → window sum ≤ lifetime holds but the latch from step 1 still blocks PROCEED. Any PROCEED
after either move, or a SUSPENDED with no artifact/latch, = FAIL.

**T2 — Self-ack + stale human ack → HALTED (falsifies §1.3 ack-channel separation):**
Loop calls `record_heartbeat()` every tick (liveness fresh) but `ack_seq` is unchanged and its
`last_ack_ms` is `ACK_STALE_MS + 1` in the past. Expected: `proceed=False`, `verdict=HALTED`,
`reason=STALE_ACK`; evidence bundle EXISTS; the fresh liveness writes do NOT satisfy attendance.
Also assert: heartbeat file absent entirely → still `HALTED`. Any PROCEED on self-liveness or
absent ack = FAIL. (There is no API by which the loop can advance `ack_seq` — assert the method
does not exist / rejects loop authority.)

**T3 — Runaway + sticky-latch resume attempt → HALTED (falsifies runaway thresholds AND §1.4):**
(a) trailing `[1000]×5` then an iteration records `4001` (> factor×mean) → `HALTED`,
`RUNAWAY_COST_SPIKE`. (b) `lifetime_starts` advances `RESTART_MAX_COUNT + 1` within
`RESTART_WINDOW_MS` → `HALTED`, `RESTART_LOOP`. For both: after the HALT, advancing time past any
window and supplying a fresh `ack_seq` must STILL return `HALTED` (latch clears only on
`resume_seq` advance) — a fresh ack does not override a runaway HALT. Boundary check: spend at
exactly `factor×mean`, or starts at exactly `RESTART_MAX_COUNT`, must NOT halt (exclusive
boundary). Any timer/ack-cleared runaway HALT, or a halt on the legal boundary, = FAIL.

---

## 7. Non-Goals

- **`console_server.py` Ed25519 ack gate (AGI step 4).** File-based ack is interim; the §1.3
  ack channel is shaped for later signed replacement.
- **`genomic_realignment_loop` (AGI step 5).** The governed loop itself is not built here.
- **Gate C 15-minute soak harness implementation.** Spec-note only; `HEARTBEAT_INTERVAL_MIN=15`
  is defined for Gate C to consume, but the soak runner is out of scope.
- **M4 48h assault, canary alert rules, host boundary daemon.** M4 proof remains OUTSTANDING;
  this spec does not claim PERFECT and does not unblock M4.
- **Production orchestrator wiring.** Only the pre-iteration gate *contract* is specified.
- **AFE ledger as enforcement.** `kinetic_telemetry.py` is display/economics only; using it as
  a budget source is explicitly excluded (§2).
- **No unbounded self-modification.** The loop can neither raise caps, extend its ack window,
  advance `ack_seq`/`resume_seq`, nor clear a latch; all are spec-fixed or human-only.
- **No fake pass paths.** Evidence-absent success, timer-cleared HALT, self-attested ack,
  backward-moving counters, and half-written-ledger low reads are all defects, not passes.

---

[^1]: Assumption: token counts are available to the envelope when `record_spend` is called
      (loop passes actual usage post-iteration). If a future boundary hides token counts, the
      ceiling falls back to a per-iteration request cap — flagged as a dependency, not solved.
[^2]: Assumption: the ack channel is writable only by a human/console and never by the loop
      process identity (enforced by file ownership/permissions in the interim, by Ed25519 in
      step 4). If the loop and the ack writer share an identity, §1.3 collapses and attendance
      cannot be trusted — this is a deployment prerequisite, not something the layer can self-
      enforce. Production wall clock assumed monotonic; caller `now_ms` ignored in production
      builds (§3 rule 1).
[^3]: Assumption: state files sit on a POSIX filesystem where `os.replace` is atomic and
      same-dir temp+rename does not cross a mount. The monotonic seal (§1.2) detects rollback
      but NOT a fully-consistent forge in which an attacker advances lifetime and window
      together to a chosen value; that requires the ack/permission boundary of [^2] to hold.
      Seal defeats accidental/naive resets and truncation, not a root-level rewrite of all
      state — which is out of this layer's authority and belongs to host boundary (non-goal).
[^4]: Assumption: authority repo root is knowable at runtime. Outside-authority assertion is a
      prefix check after canonicalization; symlink escape into the repo is a fail-closed abort.

---

**SIGN-OFF:** PASS WITH REVISIONS — REV A closes the material findings: monotonic spend/start
seal with cross-witness (counter-reset & ledger-emptying), ack-channel/liveness separation with
no loop-writable ack (self-acking), sticky HALT/SUSPEND latch with human-only clear
(post-verdict execution), production `now_ms` ignore (clock spoofing), and reaffirmed AFE
non-read + additive v0 preservation. Two residuals are honestly bounded, NOT closed, and gate
promotion to PASS: (1) a root-level attacker who rewrites *all* state files consistently defeats
the seal — this is explicitly delegated to the host-boundary daemon (non-goal) and the ack
file-permission prerequisite [^2]; the layer detects naive tampering, not a full consistent
forge. (2) Backward-compatibility of `enforce_boundary` and `metadata_ingress_gate.py` call
sites is asserted from the inventory snapshot — `/mnt/c/Architectapp_clean` is not mounted this
session, so it is unverified against source. Cap figures remain proposals pending Matt's
economic sign-off. Promote to PASS after source-verifying v0 and confirming the
permission/host-boundary prerequisites are deployed.

---

## Cursor PM source verification (2026-07-03)

**Residual (2) — v0 backward-compat:** VERIFIED against `C:\Architectapp_clean`.

| Check | Result |
|-------|--------|
| `MMIControlEnvelope.__init__(max_token_length=2048)` | Matches v0 |
| `enforce_boundary(raw_agent_output, expected_schema) -> Tuple[bool, str]` | Matches v0 signature and behavior |
| `metadata_ingress_gate.py` runtime import/call | **None** — docstring reference only (lines 28–29) |
| Other Python importers of `MMIControlEnvelope` | **None** in repo |

Additive extension is safe. Residual (2) may be closed for build planning.

**Residual (1) — root-level consistent forge / ack file permissions:** Still open — deployment prerequisite per [^2]; host-boundary daemon remains non-goal.

**Cap figures:** Matt signed **8,000,000 tokens/day** + **800,000 tokens/hour** on 2026-07-03. See `status/MMI_CONTROL_ENVELOPE_CAP_DECISION_2026-07-03.md`.
