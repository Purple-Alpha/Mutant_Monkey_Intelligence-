# NorthStar + SwarmCommand — Threat Intel Log

**Purpose:** The swarm's evolution is recorded here. Every time a new threat pattern is ingested — from a feed, from a customer report, or from a Red battery synthesis — log it. Every time that intake produces a policy update, link it.

This file is what proves NorthStar is *actually getting smarter over time* rather than just claiming to.

**See also:** `VISION.md` (why this file exists), `MILESTONE_ARC.md` C1 (threat-intel ingestion agent).

**Last reviewed:** 2026-05-23

---

## Intake Sources (Planned)

The threat-intel ingestion agent (Stage C milestone C1) will pull from these sources on a regular cadence. Until that agent exists, intake is manual.

| Source | URL | Cadence | Cost | Status |
|---|---|---|---|---|
| CISA KEV (Known Exploited Vulnerabilities) | `https://www.cisa.gov/known-exploited-vulnerabilities-catalog` | Daily | Free | Planned |
| MITRE ATT&CK | `https://attack.mitre.org/` | Quarterly | Free | Planned |
| abuse.ch URLhaus | `https://urlhaus.abuse.ch/` | Daily | Free | Planned |
| abuse.ch MalwareBazaar | `https://bazaar.abuse.ch/` | Daily | Free | Planned |
| abuse.ch ThreatFox | `https://threatfox.abuse.ch/` | Daily | Free | Planned |
| Phishtank | `https://www.phishtank.com/` | Daily | Free | Planned |
| US-CERT / CISA alerts | `https://www.cisa.gov/news-events/cybersecurity-advisories` | As published | Free | Planned |
| AlienVault OTX | `https://otx.alienvault.com/` | Configurable | Free tier | Planned |

**Operating rule:** Always start from free, high-signal sources. Paid feeds (Recorded Future, Mandiant, etc.) are deferred until ARR justifies them.

---

## Entry Format

```markdown
## YYYY-MM-DD — Short title

**Source:** Where the intel came from (feed name, MSP report, Red battery synthesis, customer escalation).
**Pattern class:** Vendor invoice fraud / executive impersonation / ransomware precursor / etc.
**Pattern shape:** Plain-English description of what the new attack looks like.
**Evidence:** Sample IDs, links, or raw indicators (never store customer data here).
**Action taken:** None / sandbox test added / mutation proposed / policy updated / promoted.
**Policy update link:** Path to the signed policy update, if any.
**Verification:** Test name and result that proves the new pattern is now defended against.
```

---

## Entries

### 2026-05-22 — Vendor-invoice fraud recall floor (5 weak shapes)

**Source:** Phase 1.5 full 40-case `grok-4` rerun diagnostic
**Pattern class:** Vendor invoice fraud
**Pattern shape:** Five weak shapes the locked prompt under-scored:
1. First invoice after onboarding with remittance instructions only inside the attached PDF.
2. Updated remit-to address with old instructions declared invalid.
3. Fake thread continuity (`Re:`, "following up as discussed below", "as discussed" with no quoted history).
4. High-value emergency invoice approval before EOD tied to shipment / operations pressure.
5. Explicit new ACH / banking details with urgency.
**Evidence:** `eval_report_2026_05_22_phase_1_5_rerun.md` (FAIL), `eval_report_2026_05_22_phase_1_5_vf-00{1..5}_diagnostic.md` (5/5 PASS post-patch)
**Action taken:** No-spend prompt remediation. Added "Phase 1.5 vendor-invoice recall floor" section to `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`.
**Policy update link:** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py`
**Verification:** `tests/test_email_risk_scoring_agent.py::test_phase_1_5_vendor_invoice_recall_floor_is_pinned` (28 passed, full suite 472 passed)

---

## Empty Intake Queue

Future entries land below this line as new threat patterns are ingested.

(none yet)
