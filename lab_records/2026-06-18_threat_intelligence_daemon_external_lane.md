# Threat Intelligence Daemon — External Lane Build Record

**Date:** 2026-06-18  
**Authority:** `4. Product_Roadmap/Threat_Intelligence_Daemon_Design_Contract.md` §11 SIGNED (Matt Nichol, 2026-06-14)  
**Build root:** `/home/socialarchitect/mutant_monkey_intel/` (independent of Northstar — TI-R2)

---

## Scope verified

| Contract section | Status |
|---|---|
| Section 1 — folder layout | PASS — `config/`, `store/`, `logs/`, `monkey_intel_daemon.py` |
| Section 2 — source categories | PASS — 7 categories in `config/sources.json` (APWG fraud feed disabled pending URL verify) |
| Section 3 — schedule | PASS — `config/schedule.json` twice-daily + Wednesday notification |
| Section 4 — tiering | PASS — keyword vectors in `config/keywords.json` |
| Section 5 — store format | PASS — tier JSON arrays with required fields |
| Section 6 — mid-week notification | PASS — `format_notification` / `emit_notification` |
| Section 7 — behavior rules TI-R1..R12 | PASS — stdlib daemon, Northstar write guard, dedup, fail-closed fetch |
| Section 8 — testable invariants | PASS — `test_monkey_intel_daemon.py` (offline falsifiable suite) |

---

## Tests run

```text
cd /home/socialarchitect/mutant_monkey_intel
python3 -m unittest test_monkey_intel_daemon -v
```

Covers: TI-INV-2, 3, 4, 5, 6, 7, 8, 9, 10, 11 (layout + governed lane structure).

Live collection (`collect-once`) previously executed 2026-06-14 per `logs/daemon.log` — not re-run in this verification pass (no new live-fetch authorization required for build closure).

---

## Northstar isolation (TI-INV-2)

No files under `/home/socialarchitect/northstar/` modified by the daemon process. MMI completion records updated in Northstar only as post-build governance (this lab record + external lane registry).

---

## Operator notes

- Daemon PID file: `/tmp/monkey_intel_daemon.pid`
- Commands: `python3 monkey_intel_daemon.py start|stop|status|collect-once|purge|notify`
- Intelligence does not auto-enter Northstar build loop — Matt review required per contract Purpose
