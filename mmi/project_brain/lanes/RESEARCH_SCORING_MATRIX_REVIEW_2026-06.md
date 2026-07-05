# Research Review — WAR_ROOM_SCORING_MATRIX 2026-06 (ChatGPT)

**Status:** FILED — reconciled against active v2 (`intel/WAR_ROOM_SCORING_MATRIX_v2.md`, Matt approved 2026-06-30)  
**Sign-off:** **PASS WITH REVISIONS**  
**Downstream:** Claude v2 addresses §9 Crucible findings — see v2 §11 Resolution Log

## 1. Executive Summary

This review is **not a rubber stamp**. The scoring matrix can become a defensible operator-tier war-room tool, but v2 must remove false precision, Canadianize legal triggers, and stop comparing Matt's solo local-first stack to enterprise SOC maturity. The draft content itself was not pasted after the artifact marker, so this review audits the criteria implied by your prompt: Axis A detection, Axis B leadership, four-tier scoring, 15/60/72h/24h thresholds, "two independent signals," regulatory triggers, signal catalog, worksheet, purple-team mapping, and enterprise comparison. The strongest Canadian anchors are CCCS Baseline Controls for Small and Medium Organizations, CCCS incident-response planning guidance, CCCS Ransomware Playbook, Statistics Canada CSCSC 2023, OPC PIPEDA breach guidance, Quebec Law 25, CAFC/RCMP reporting guidance, and CCCS Cyber Security Readiness Goals. The matrix should not claim that specific time thresholds are Canadian-validated unless a primary Canadian source says so. For MMI v1, scoring must be **manual, evidence-backed, worksheet-driven, and advisory-only**. No SOAR, no endpoint swarm, no auto-isolate, no live telemetry requirement. The correct v2 posture is: **operator-ready if manually measurable; untrusted if it depends on enterprise tooling Matt does not have.**

## 2. Methodology & Limitations

I treated Canadian government and statutory sources as highest authority: CCCS, Statistics Canada, OPC, federal/provincial legislation, RCMP, and CAFC. Global sources such as NIST, CISA, ISO, MITRE, and VERIS are useful vocabulary and structure, but every global control is marked as requiring localization before it becomes Canadian operating truth. Vendor survey material such as CIRA can inform trends, but it is not equivalent to law or government guidance; it should be labeled survey evidence, not universal fact.

Hard limitation: I do **not** have the actual full text of `mmi/project_brain/intel/WAR_ROOM_SCORING_MATRIX.md`. Therefore, any "current criterion" wording below is reconstructed from the prompt, not quoted from the file. Claude should treat this as a **crucible review packet**, then reconcile it against the exact file before writing v2.

**PM note (2026-06-30):** v2 shipped and Matt approved. This review remains the evidence packet; v2 §11 maps finding resolution.

## 3. Framework Landscape

| Framework | Jurisdiction | Relevant section | Maps to MMI Axis A/B? | Gap vs current draft |
|-----------|--------------|------------------|------------------------|----------------------|
| CCCS Baseline Cyber Security Controls for SMOs | Canada | 80/20 practicality model for SMOs | Axis A + B | Best primary anchor for MMI v1 |
| CCCS ITSAP.40.003 — Incident Response Plan | Canada | Roles, comms, stakeholder notification | Axis B strong | Map leadership to documented artifacts |
| CCCS Ransomware Playbook ITSM.00.099 | Canada | Report to police, CAFC, Cyber Centre | Axis A + B | Canadian ransomware spine |
| Statistics Canada CSCSC 2023 | Canada | 16% businesses impacted; 13% ransomware among impacted | Context only | Not tier thresholds |
| OPC PIPEDA breach guidance | Canada | RROSH reporting; record all breaches | Axis B | Distinguish record vs report |
| PIPEDA s.10.1–10.3 | Canada | RROSH; notify as soon as feasible; records | Axis B mandatory | No universal 72h |
| Quebec Law 25 | Quebec | Serious injury → CAI + individuals | Axis B if QC in scope | Not federal default |
| CAFC / RCMP | Canada | Cybercrime/fraud reporting | Axis B criminal branch | Not OPC substitute |
| Criminal Code s.342.1 | Canada | Unauthorized computer use | Legal context tag | Not CFAA |
| NIST CSF 2.0 / SP 800-61r3 | Global — Requires Localization | Detect/Respond/Recover | Structure only | No invented time thresholds |
| ISO 27035-1, VERIS, MITRE D3FEND | Global — Requires Localization | IR vocabulary / mapping | Worksheet fields | Not maturity mandate |

Full table with links preserved in ChatGPT source ingested 2026-06-30.

## 4. Tier Criteria Adjudication

See ChatGPT full adjudication table (Tiers 1–4, Axes A/B). Key verdicts: soften time thresholds; define two-signal rule; keep weakest-link `min(A,B)`.

## 5. Canadian Regulatory Audit

Critical fixes required before v2 (all addressed in active v2):

- PIPEDA: RROSH + as soon as feasible — **not** universal 72h
- Record every breach of safeguards (2 years)
- Law 25 separate from PIPEDA
- CCCS voluntary/support vs emergency = local police
- CAFC/RCMP ≠ privacy regulator
- Criminal Code s.342.1 context — not CFAA

## 6. Signal Catalog Revision

P1/P2/P3 catalog for Windows + WSL + local repo + B2 + cloud identity. Two independent signals = separate evidence families, non-derivative.

## 7. Worksheet & Drill Improvements

Evidence ledger, regulatory triage, comms blackout, PIR stub day-0, 15–30 min quarterly drill. See v2 §7 and §12.

## 8. Enterprise Comparison Critique

Replace enterprise SOC comparison with solo-operator / CCCS SMB framing. **Done in v2 §14.**

## 9. Crucible Findings Register

| # | Finding | Severity | v2 status |
|---|---------|----------|-----------|
| 1 | Thresholds without validation | High | Fixed §4 |
| 2 | PIPEDA 72h wrong | Critical | Fixed §5, §7.4, §9 |
| 3 | CAFC/CCCS/OPC conflated | High | Fixed §9 |
| 4 | Enterprise false inferiority | Medium | Fixed §14 |
| 5 | Two signals undefined | High | Fixed §6 |
| 6 | Security theater | High | Fixed §7.2–7.3 |
| 7 | Missing WSL/local signals | High | Fixed §8 |
| 8 | Missing cloud identity signals | High | Fixed §8 |
| 9 | US legal framing | High | Fixed §7.4, §9 |
| 10 | Advisory-only conflict | Critical | Fixed §1 |
| 11 | Local-first conflict | Critical | Fixed §1 |
| 12 | Missing restore drill | High | Fixed §5, §7.3 A7 |
| 13 | Missing comms blackout | Medium | Fixed §7.5 |
| 14 | Missing PIR linkage | Medium | Fixed §7.7 |

## 10. Recommended v2 Structure

Implemented in `WAR_ROOM_SCORING_MATRIX_v2.md` (17 sections).

## 11. Safe Language Pack

See ChatGPT source — incorporated into v2 tier tables and §7.4.

## 12. Outstanding Gaps

| Gap | Owner | Status |
|-----|-------|--------|
| Reconcile exact v1 text | Done — v2 supersedes v1 | Closed |
| Sector-specific 24h/72h rules | Matt / counsel | Open |
| Quebec Law 25 in scope | Matt / counsel | Open |
| B2/rclone logging validation | Matt / Evaluator | Open |
| Identity provider confirmation | Matt | Open |
| Sysmon deployed? | Matt | Open — not mandatory in v2 |

## 13. Per-Claim Rigor Table

See ChatGPT source §13 — Canadian claims 9–10/10 confidence on PIPEDA, CCCS, OPC, Law 25, CAFC, s.342.1.

## Sign-off

**PASS WITH REVISIONS.** v2 is the active operator matrix pending counsel review on sector-specific deadlines and Quebec scope.

## Source links

- [CCCS Baseline Controls SMOs](https://www.cyber.gc.ca/en/guidance/baseline-cyber-security-controls-small-and-medium-organizations)
- [CCCS ITSAP.40.003](https://www.cyber.gc.ca/en/guidance/developing-your-incident-response-plan-itsap40003)
- [CCCS Ransomware Playbook](https://www.cyber.gc.ca/en/guidance/ransomware-playbook-itsm00099)
- [Statistics Canada CSCSC 2023](https://www150.statcan.gc.ca/n1/daily-quotidien/241021/dq241021a-eng.htm)
- [OPC breach guidance](https://www.priv.gc.ca/en/privacy-topics/business-privacy/breaches-and-safeguards/privacy-breaches-at-your-business/gd_pb_201810/)
- [PIPEDA](https://laws-lois.justice.gc.ca/eng/acts/p-8.6/page-3.html)
- [Quebec Law 25 / private-sector act](https://legisquebec.gouv.qc.ca/en/showdoc/cs/p-39.1)
- [CAFC report](https://antifraudcentre-centreantifraude.ca/report-signalez-eng.htm)
- [Criminal Code s.342.1](https://laws-lois.justice.gc.ca/eng/acts/C-46/section-342.1.html)
- [CCCS Report a cyber incident](https://www.cyber.gc.ca/en/incident-management)
- [RCMP report cybercrime](https://rcmp.ca/en/federal-policing/cybercrime/national-cybercrime-coordination-centre/report-cybercrime-and-fraud)
- [MITRE D3FEND T1486](https://d3fend.mitre.org/offensive-technique/attack/T1486/)
