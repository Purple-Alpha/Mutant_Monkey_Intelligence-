# Mutant Monkey — Threat Intelligence Ingestion Daemon Concept Doc

**Status:** CONCEPT — no build authorization. Requires design contract and §11 signature before build.
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Scope:** Separate governed lane — threat intelligence only. Does not touch Northstar build system directly.

---

## Purpose

The Threat Intelligence Ingestion Daemon is a background process that continuously monitors global open-source threat intelligence feeds and delivers filtered, tiered intelligence into a governed store. Its job is to ensure Mutant Monkey's adversarial test suite and defensive design never fall behind what attackers are actually doing in the real world.

This is not a detection agent. It is not part of the swarm. It does not produce verdicts. It feeds intelligence into a governed store that humans and adversarial test designers read and act on.

The project scope is intentionally unconstrained. The daemon collects broadly — email fraud, BEC, vendor payment fraud, MSP attacks, and anything else that is moving in the global threat landscape. Relevance filtering happens inside the daemon, not at collection time.

---

## What It Does

1. Monitors a defined list of open-source threat intelligence sources on a schedule
2. Pulls new indicators, TTPs, CVEs, phishing patterns, and attacker tooling updates
3. Filters collected intelligence into three tiers
4. Writes tiered output to a governed file store in its own folder
5. Fires a mid-week notification so the store is never forgotten or stale
6. Never writes directly to the Northstar repo or any signed contract

---

## Intelligence Tiers

Every piece of collected intelligence is classified into one of three tiers before storage.

| Tier | Label | Meaning | Action |
|---|---|---|---|
| 1 | RELEVANT | Directly applicable to Mutant Monkey's current adversarial test suite or defensive design | Review immediately — may generate new adversarial test vectors |
| 2 | WATCH | Not immediately applicable but important to track — attacker TTPs that could become relevant | Review mid-week — flag for future test suite expansion |
| 3 | DISCARD | Not relevant to Mutant Monkey at this time | Logged for 30 days then purged — never acted on |

Tier classification is done by the daemon using keyword vectors. It is not final — Matt can reclassify any item manually.

---

## Source Categories

The daemon monitors the following source categories. Specific sources are defined in the config file, not hardcoded.

- CVE and vulnerability feeds (CISA KEV, NVD)
- Phishing and BEC indicator feeds
- Dark web monitoring aggregators (public/open sources only)
- Threat actor TTP databases (MITRE ATT&CK updates, public threat reports)
- Email security research publications
- MSP and SMB-targeted attack reporting
- Global fraud pattern databases
- General attacker tooling and technique updates

---

## Folder and File Structure

The daemon lives in its own folder, completely separate from the Northstar repo.

```
/home/socialarchitect/mutant_monkey_intel/
├── config/
│   ├── sources.json          — feed source list and credentials
│   ├── keywords.json         — tier classification keyword vectors
│   └── schedule.json         — collection and notification schedule
├── store/
│   ├── tier1_relevant.json   — immediately actionable intelligence
│   ├── tier2_watch.json      — important but not immediate
│   └── tier3_discard.json    — logged before purge (30-day retention)
├── logs/
│   └── daemon.log            — run log, errors, collection events
└── monkey_intel_daemon.py    — the daemon itself
```

Nothing in this folder is part of the Northstar repo. Nothing in this folder is committed to the Northstar branch. The two systems are separate.

---

## Mid-Week Timer

The daemon fires a mid-week notification every Wednesday at a time Matt sets in `schedule.json`. The notification is a terminal output or local log entry that says:

```
MUTANT MONKEY INTEL — MID-WEEK REVIEW DUE
Tier 1 items since last review: [count]
Tier 2 items since last review: [count]
Tier 3 items purged: [count]
Last collection run: [timestamp]
Next collection run: [timestamp]
```

If no review has occurred since the previous Wednesday, the notification repeats daily until acknowledged.

---

## What the Daemon Does NOT Do

- Does not write to the Northstar repo
- Does not modify any signed contract
- Does not feed intelligence directly into the swarm or any detection agent
- Does not make any decisions — it collects and tiers, humans decide
- Does not connect to paid or authenticated dark web sources without a separate signed authorization
- Does not run in cloud infrastructure until Matt authorizes it with a separate decision

---

## How Intelligence Flows Into the Build System

The daemon produces intelligence. A human (Matt) reads it. If a Tier 1 item warrants a new adversarial test vector, Matt brings it to Claude. Claude drafts an addition to the relevant adversarial test suite contract. Matt signs. Cursor implements.

The daemon never bypasses the governance loop. It accelerates it by ensuring the inputs to that loop are current.

---

## Definition of Done

This concept is complete when the daemon can:
- Run as a detached background process on WSL without terminal attachment
- Pull from at least three configured source categories on schedule
- Classify every collected item into Tier 1, 2, or 3
- Write tiered output to the governed file store
- Fire mid-week notification with item counts
- Purge Tier 3 items after 30 days
- Log every collection run and error to daemon.log
- Operate completely independently of the Northstar repo and build system
