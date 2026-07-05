"""Deterministic fuzz engine for §6 targets."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass

from mmi.m4.afe_ledger import AfeLedger, LedgerError, ReplenishEvent
from mmi.m4.canary_classifier import CanaryOutcome, ClassifierError, classify_signal
from mmi.m4.evidence_chain import ChainError, EvidenceChain
from mmi.m4.parser_surface import (
    ParseSurfaceError,
    parse_canary_rules,
    parse_evidence_json,
    parse_manifest,
    parse_summary_json,
)
from mmi.m4.restart_latch import RestartError, RestartLatch
from mmi.m4.stage_fsm import FsmError, FsmEvent, FsmState, apply_event, credit_pass_allowed

FUZZ_TARGETS = ("parser", "fsm", "ledger", "canary", "evidence", "restart", "all")

VALID_SUMMARY = json.dumps(
    {
        "schema": "m4_stage_summary/v1",
        "stage_id": "C-M4",
        "run_mode": "C-M4",
        "overall_gate_status": "HARNESS_READY",
        "chain_verified": True,
        "perfect_claim": False,
    }
)

VALID_MANIFEST = json.dumps({"manifest_version": "1", "files": []})

VALID_CANARY_RULES = json.dumps(
    {
        "rules": [
            {"rule_id": "M4-CANARY-001", "threshold": 0.9, "comparator": "gt"},
            {"rule_id": "M4-CANARY-002", "threshold": 100.0, "comparator": "lt"},
        ]
    }
)


@dataclass
class FuzzFailure:
    target: str
    iteration: int
    seed: int
    detail: str


def _mutate_text(rng: random.Random, text: str) -> str:
    if not text:
        return text
    buf = list(text)
    op = rng.randint(0, 3)
    if op == 0 and buf:
        idx = rng.randrange(len(buf))
        buf[idx] = rng.choice("xyz{[(")
    elif op == 1 and len(buf) > 1:
        idx = rng.randrange(len(buf) - 1)
        del buf[idx]
    elif op == 2:
        idx = rng.randrange(len(buf) + 1)
        buf.insert(idx, rng.choice("{}[],:"))
    else:
        buf.append(rng.choice("}" if "{" in text else " "))
    return "".join(buf)


def _fuzz_parser(rng: random.Random, iters: int, seed: int) -> list[FuzzFailure]:
    failures: list[FuzzFailure] = []
    reject_cases = [
        ("evidence", parse_evidence_json, ""),
        ("evidence", parse_evidence_json, "{"),
        ("evidence", parse_evidence_json, '{"a":1}extra'),
        ("summary", parse_summary_json, '{"perfect_claim": true, "schema": "x", "stage_id": "C-M4", "run_mode": "C-M4", "overall_gate_status": "X", "chain_verified": true}'),
        ("manifest", parse_manifest, '{"manifest_version": 1}junk'),
        ("canary_rules", parse_canary_rules, '{"rules": [{"rule_id": "x", "threshold": 1, "comparator": "bogus"}]}'),
    ]
    for label, fn, sample in reject_cases:
        try:
            fn(sample)
        except (ParseSurfaceError, json.JSONDecodeError, ValueError, TypeError):
            continue
        except Exception as exc:
            failures.append(FuzzFailure("parser", -1, seed, f"{label} crash on reject sample: {exc}"))
            continue
        failures.append(FuzzFailure("parser", -1, seed, f"{label} accepted reject sample"))

    valid_cases = [
        ("summary", VALID_SUMMARY, parse_summary_json),
        ("manifest", VALID_MANIFEST, parse_manifest),
        ("canary_rules", VALID_CANARY_RULES, parse_canary_rules),
    ]
    for label, text, fn in valid_cases:
        try:
            fn(text)
        except Exception as exc:
            failures.append(FuzzFailure("parser", -1, seed, f"{label} rejected valid sample: {exc}"))

    for i in range(iters):
        base = rng.choice([VALID_SUMMARY, VALID_MANIFEST, VALID_CANARY_RULES])
        mutated = _mutate_text(rng, base)
        for label, fn in [
            ("summary", parse_summary_json),
            ("manifest", parse_manifest),
            ("canary_rules", parse_canary_rules),
        ]:
            try:
                fn(mutated)
            except (ParseSurfaceError, json.JSONDecodeError, ValueError, TypeError):
                continue
            except Exception as exc:
                failures.append(FuzzFailure("parser", i, seed, f"{label} crash: {exc}"))
    return failures


def _fuzz_fsm(rng: random.Random, iters: int, seed: int) -> list[FuzzFailure]:
    failures: list[FuzzFailure] = []
    events = list(FsmEvent)
    legal_bootstrap = [
        FsmEvent.START_PROVISION,
        FsmEvent.PROVISION_DONE,
        FsmEvent.ARM,
    ]
    for i in range(iters):
        state = FsmState.INIT
        try:
            for ev in legal_bootstrap:
                state = apply_event(state, ev)
        except FsmError as exc:
            failures.append(FuzzFailure("fsm", i, seed, f"bootstrap failed: {exc}"))
            continue
        for _ in range(rng.randint(1, 12)):
            ev = rng.choice(events)
            try:
                new_state = apply_event(state, ev)
            except FsmError:
                continue
            if ev == FsmEvent.END_INTERVAL_PASS and not credit_pass_allowed(state, ev):
                failures.append(FuzzFailure("fsm", i, seed, "PASS from illegal precondition"))
            if new_state not in FsmState:
                failures.append(FuzzFailure("fsm", i, seed, f"non-enumerated state {new_state}"))
            state = new_state
    return failures


def _fuzz_ledger(rng: random.Random, iters: int, seed: int) -> list[FuzzFailure]:
    failures: list[FuzzFailure] = []
    for i in range(iters):
        ledger = AfeLedger(balance=rng.randint(10, 500))
        ops = rng.randint(1, 20)
        for _ in range(ops):
            roll = rng.random()
            try:
                if roll < 0.7:
                    actor = rng.choice(["attacker", "defender", ""])
                    amount = rng.randint(0, 50)
                    ledger.apply_burn(actor, amount)
                else:
                    actor = "operator"
                    amount = rng.randint(1, 20)
                    sig = ReplenishEvent(actor, amount, "bad").signature
                    if rng.random() < 0.5:
                        import hashlib

                        sig = hashlib.sha256(f"{actor}:{amount}".encode()).hexdigest()[:16]
                    ledger.apply_replenish(ReplenishEvent(actor, amount, sig))
            except LedgerError:
                continue
            except Exception as exc:
                failures.append(FuzzFailure("ledger", i, seed, f"crash: {exc}"))
                break
        else:
            if not ledger.monotonic():
                failures.append(FuzzFailure("ledger", i, seed, "non-monotonic ledger accepted"))
    return failures


def _fuzz_canary(rng: random.Random, iters: int, seed: int) -> list[FuzzFailure]:
    failures: list[FuzzFailure] = []
    rules = parse_canary_rules(VALID_CANARY_RULES)
    for i in range(iters):
        value = rng.uniform(-5.0, 200.0)
        try:
            outcome = classify_signal(value, rules)
        except ClassifierError:
            continue
        except Exception as exc:
            failures.append(FuzzFailure("canary", i, seed, f"crash: {exc}"))
            continue
        if outcome not in CanaryOutcome:
            failures.append(FuzzFailure("canary", i, seed, "fail-open misclassification"))
    try:
        classify_signal(0.5, [])
    except ClassifierError:
        pass
    else:
        failures.append(FuzzFailure("canary", -1, seed, "empty rules fail-open"))
    return failures


def _fuzz_evidence(rng: random.Random, iters: int, seed: int) -> list[FuzzFailure]:
    failures: list[FuzzFailure] = []
    for i in range(iters):
        chain = EvidenceChain(stage_id="C-M4", run_nonce=f"nonce-{seed}-{i}")
        count = rng.randint(0, 8)
        ok = True
        for interval in range(count):
            try:
                chain.append(interval, {"result": "PASS"})
            except ChainError:
                ok = False
                break
        if ok and chain.verify():
            if rng.random() < 0.3 and len(chain.links) > 1:
                chain.links[-1]["hash"] = "tampered"
                if chain.verify():
                    failures.append(FuzzFailure("evidence", i, seed, "verify true on tampered chain"))
            if rng.random() < 0.3 and len(chain.links) > 1:
                try:
                    chain.append(interval + 2, {"result": "PASS"})
                except ChainError:
                    pass
                else:
                    failures.append(FuzzFailure("evidence", i, seed, "gap/backfill accepted"))
        elif ok:
            failures.append(FuzzFailure("evidence", i, seed, "valid chain failed verify"))
    return failures


def _fuzz_restart(rng: random.Random, iters: int, seed: int) -> list[FuzzFailure]:
    failures: list[FuzzFailure] = []
    for i in range(iters):
        latch = RestartLatch()
        try:
            steps = rng.randint(1, 6)
            for step in range(steps):
                latch.observe_interval(step, credited=rng.random() < 0.8)
            snap = latch.crash()
            if rng.random() < 0.5:
                try:
                    latch.resume(snap, credit_unobserved=True)
                except RestartError:
                    pass
                else:
                    failures.append(FuzzFailure("restart", i, seed, "credited unobserved interval"))
            else:
                latch.resume(snap)
            if latch.latched_halt and not latch.checkpoint.fail_closed_latched:
                failures.append(FuzzFailure("restart", i, seed, "fail-closed latch lost"))
        except RestartError:
            continue
        except Exception as exc:
            failures.append(FuzzFailure("restart", i, seed, f"crash: {exc}"))
    return failures


_TARGET_RUNNERS = {
    "parser": _fuzz_parser,
    "fsm": _fuzz_fsm,
    "ledger": _fuzz_ledger,
    "canary": _fuzz_canary,
    "evidence": _fuzz_evidence,
    "restart": _fuzz_restart,
}


def run_fuzz_target(target: str, seed: int, iters: int) -> list[FuzzFailure]:
    if target not in _TARGET_RUNNERS:
        raise ValueError(f"unknown fuzz target: {target}")
    rng = random.Random(seed)
    return _TARGET_RUNNERS[target](rng, iters, seed)


def run_all_targets(seed: int, iters: int) -> list[FuzzFailure]:
    failures: list[FuzzFailure] = []
    for name in _TARGET_RUNNERS:
        failures.extend(run_fuzz_target(name, seed, iters))
    return failures
