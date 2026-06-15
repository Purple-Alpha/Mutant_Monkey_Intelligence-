# Mutant Monkey — Threat Intelligence Ingestion Daemon Design Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Threat_Intelligence_Daemon_Concept_Doc.md — June 14 2026
**Scope:** Separate governed lane — completely independent of Northstar repo and build system

---

## §11 Signature Block

```
Signed: Matt Nichol
Name:   Matt Nichol
Date:   June 14th 2026
Authority: Sole signing authority — Mutant Monkey Inbox Shield
```

---

## Purpose

This contract governs the Threat Intelligence Ingestion Daemon — a background process that monitors global open-source threat intelligence feeds, tiers collected intelligence by relevance, stores it in a governed file structure, and fires a mid-week notification to ensure the store is never forgotten.

The daemon is a collection and tiering system only. It makes no decisions. It feeds no agent, model, or component directly. All intelligence flows through Matt before entering the build system.

---

## Section 1 — Folder and File Structure

The daemon lives at:

```
/home/socialarchitect/mutant_monkey_intel/
```

This path is completely separate from `/home/socialarchitect/northstar/`. The two directories share no files, no commits, and no state.

Required structure — Cursor must create exactly this layout:

```
/home/socialarchitect/mutant_monkey_intel/
├── config/
│   ├── sources.json          — feed source list and fetch config
│   ├── keywords.json         — tier classification keyword vectors
│   └── schedule.json         — collection schedule and notification time
├── store/
│   ├── tier1_relevant.json   — immediately actionable intelligence
│   ├── tier2_watch.json      — important but not immediately actionable
│   └── tier3_discard.json    — logged before purge, 30-day retention
├── logs/
│   └── daemon.log            — run log, errors, collection events
└── monkey_intel_daemon.py    — the daemon process
```

No other files may be created in this directory by the daemon without a signed amendment.

---

## Section 2 — Source Categories

The daemon monitors sources across the following categories. Specific URLs and credentials are defined in `config/sources.json` — not hardcoded in the daemon.

Required source categories at launch:

1. CVE and vulnerability feeds — CISA KEV, NVD
2. Phishing and BEC indicator feeds
3. Threat actor TTP databases — MITRE ATT&CK updates, public threat reports
4. Email security research publications
5. MSP and SMB-targeted attack reporting
6. Global fraud pattern databases
7. General attacker tooling and technique updates

Additional sources may be added by editing `config/sources.json` without a contract amendment, provided they are open-source and do not require authenticated dark web access.

Authenticated dark web sources require a separate signed authorization from Matt before they may be added.

---

## Section 3 — Collection Schedule

Collection runs are defined in `config/schedule.json`.

Default schedule:
- Collection frequency: twice daily — 06:00 and 18:00 local WSL time
- Mid-week review notification: every Wednesday at a time Matt sets in `schedule.json`
- If no review acknowledgement since previous Wednesday: notification repeats daily until acknowledged

Acknowledgement is a manual entry in `daemon.log` by Matt or a designated reviewer. The daemon checks for acknowledgement before suppressing repeat notifications.

---

## Section 4 — Intelligence Tiering

Every collected item is classified into exactly one tier before storage. Classification uses keyword vectors defined in `config/keywords.json`. Matt may reclassify any item manually at any time.

| Tier | Label | Meaning | Storage file | Retention |
|---|---|---|---|---|
| 1 | RELEVANT | Directly applicable to current adversarial test suite or defensive design | tier1_relevant.json | Until manually cleared |
| 2 | WATCH | Important to track — may become relevant | tier2_watch.json | Until manually cleared |
| 3 | DISCARD | Not relevant at this time | tier3_discard.json | 30 days then purged automatically |

Tiering rules:
- An item matching any Tier 1 keyword vector is classified Tier 1 regardless of other matches
- An item matching no Tier 1 keyword but any Tier 2 keyword is classified Tier 2
- An item matching no Tier 1 or Tier 2 keyword is classified Tier 3
- Classification is logged with the matched keyword vector for auditability
- No item is silently dropped — every collected item enters exactly one tier

---

## Section 5 — Store Format

Each tier file is a JSON array. Every entry must contain:

| Field | Content |
|---|---|
| `item_id` | Unique identifier — UUID |
| `collected_at` | ISO 8601 timestamp |
| `source` | Source name from sources.json |
| `source_url` | Direct URL of the collected item |
| `title` | Title or headline of the item |
| `summary` | 2-5 sentence plain-English summary |
| `tier` | 1, 2, or 3 |
| `matched_keywords` | List of keyword vectors that triggered tier classification |
| `raw_content_hash` | SHA-256 hash of the raw collected content |
| `reviewed` | Boolean — false until Matt marks it reviewed |
| `reclassified_by` | Null unless manually reclassified — then Matt's identifier and timestamp |
| `purge_after` | ISO 8601 date — only present on Tier 3 items |

---

## Section 6 — Mid-Week Notification

Every Wednesday the daemon writes the following to `daemon.log` and prints to stdout if a terminal is attached:

```
========================================
MUTANT MONKEY INTEL — MID-WEEK REVIEW DUE
========================================
Tier 1 items unreviewed since last Wednesday: [count]
Tier 2 items unreviewed since last Wednesday: [count]
Tier 3 items purged this week: [count]
Last collection run: [timestamp]
Next collection run: [timestamp]
To acknowledge: add REVIEW_ACK [date] to daemon.log
========================================
```

If no `REVIEW_ACK` entry exists in `daemon.log` since the previous Wednesday, the notification repeats every day at the same time until acknowledged.

---

## Section 7 — Daemon Behavior Rules

| Rule | Requirement |
|---|---|
| TI-R1 | Daemon runs as a detached background process — survives terminal close |
| TI-R2 | Daemon never writes to `/home/socialarchitect/northstar/` or any subdirectory |
| TI-R3 | Daemon never modifies any signed contract |
| TI-R4 | Daemon never feeds intelligence directly to any swarm agent, detection component, or build system |
| TI-R5 | Daemon never makes classification decisions that cannot be reversed by Matt |
| TI-R6 | Every collection run is logged to `daemon.log` with timestamp, source, item count, and any errors |
| TI-R7 | Every classification decision is logged with the matched keyword vector |
| TI-R8 | Tier 3 purge is logged before deletion — purged items listed in `daemon.log` |
| TI-R9 | Daemon fails closed on source fetch error — logs error, skips source, continues other sources |
| TI-R10 | Daemon never connects to authenticated dark web sources without a separately signed authorization |
| TI-R11 | Daemon never stores raw content — only summary, hash, metadata, and source URL |
| TI-R12 | Duplicate items (same `raw_content_hash`) are not stored twice — logged as duplicate and skipped |

---

## Section 8 — Testable Invariants

| # | Invariant | Falsifiable test |
|---|---|---|
| TI-INV-1 | Daemon survives terminal close | Close terminal, verify PID still active via `ps aux` |
| TI-INV-2 | Daemon never writes to Northstar repo | Run daemon, verify no file changes in `/home/socialarchitect/northstar/` |
| TI-INV-3 | Every collected item enters exactly one tier | Collect 100 items — verify each has exactly one tier value, none missing |
| TI-INV-4 | Tier 1 keyword match overrides all other tiers | Submit item matching both Tier 1 and Tier 2 keywords — verify Tier 1 assigned |
| TI-INV-5 | Mid-week notification fires every Wednesday | Simulate Wednesday — verify notification written to daemon.log |
| TI-INV-6 | Daily repeat fires if no REVIEW_ACK since last Wednesday | Simulate no acknowledgement — verify daily repeat on Thursday and Friday |
| TI-INV-7 | Daily repeat stops after REVIEW_ACK logged | Add REVIEW_ACK entry — verify repeat notification stops |
| TI-INV-8 | Tier 3 items purged after 30 days | Insert Tier 3 item with `purge_after` 30 days past — verify purged and logged |
| TI-INV-9 | Source fetch error does not stop other sources | Kill one source endpoint — verify other sources still collected |
| TI-INV-10 | Duplicate items not stored twice | Submit same item twice — verify only one entry, duplicate logged |
| TI-INV-11 | Raw content never stored — only hash | Inspect store files — verify no raw content fields present |
| TI-INV-12 | Every classification decision includes matched keyword vector | Inspect all tier entries — verify `matched_keywords` populated on every item |

---

## Section 9 — Out of Scope

- Any write to the Northstar repo or build system
- Any direct connection to swarm agents, detection components, or contracts
- Automated generation of adversarial test vectors without human review
- Authenticated dark web source access
- Cloud deployment of any kind
- Storage of raw collected content
- Any autonomous decision-making beyond keyword-based tier classification

---

## Non-Authorizations

- This contract does not authorize cloud deployment — local WSL only until separately authorized.
- This contract does not authorize authenticated dark web source access.
- This contract does not authorize the daemon to feed intelligence directly into any Northstar component.
- Signing this contract authorizes Cursor to build the daemon, folder structure, tiering system, store format, schedule, and mid-week notification only — within the scope defined above.
