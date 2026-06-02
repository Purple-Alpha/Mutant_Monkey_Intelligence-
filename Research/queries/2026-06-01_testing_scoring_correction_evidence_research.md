# 2026-06-01 — Testing / Scoring / Correction-Evidence Research

**Captured:** 2026-06-01 ~18:35 PT (Pacific) by Cursor (Claude Opus 4.7) at operator request.
**Status:** Internal research only. Pre-spec. No D10 progress. No implementation. No client-facing copy. No gate required.
**Companion brief:** `Research/queries/2026-06-01_testing_scoring_correction_evidence_brief.md`
**Active task:** Informs `4. Product_Roadmap/Research_Inputs/Testing_Score_Sheet_Schema.md` (M1 + M2 + M3); see `PROGRESS.md` handoff note.
**Authorship boundary:** Operator-supplied research text below is preserved as provided. Header above is AI-drafted under operator instruction.

---

## Part A — Research Brief: Testing, Scoring, and Correction-Evidence Discipline for NorthStar Inbox Shield

Prepared for: Project NorthStar — Pre-Spec Shaping Phase
Date: 2026-06-01
Status: Internal Research Only — No D10 Progress — No Implementation — No Client-Facing Copy
Scope: Validation of seven specific questions against external industry precedent. This document contains no compliance claims, no certification claims, and no insurer-approval language.

### Framing

The NorthStar Inbox Shield system is being built with a testing and scoring discipline that treats every test event — pass or fail — as a permanent, scannable record. The intent is to accumulate a body of evidence over time that demonstrates the system's character: not through marketing claims, but through the unbroken chain of what was tested, what failed, why it failed, what correction was applied, and how that correction was verified. The seven questions below ask whether this discipline has external precedent, what it is called in mature engineering organizations, and where the proposed discipline is ahead of or behind typical industry practice.

### Question 1: Is "Preserve Failure + Record Why + Scoped Correction + Retest" a Recognized Discipline?

**Verdict:** Yes — recognized across multiple mature engineering disciplines under several canonical names.

The discipline of preserving failure records, documenting root causes, applying scoped corrections, and retesting is not novel. It is the operational backbone of Site Reliability Engineering (SRE), information security management, and continuous improvement manufacturing.

**Google SRE Blameless Postmortem Culture.** Google's Site Reliability Engineering book, authored by John Lunney and Sue Lueder, defines a postmortem as "a written record of an incident, its impact, the actions taken to mitigate or resolve it, the root cause(s), and the follow-up actions to prevent the incident from recurring." The philosophy is explicit: "Writing a postmortem is not punishment — it is a learning opportunity for the entire company." The standard requires that the failure record be preserved without assigning individual blame, because blame suppresses future reporting and destroys the institutional memory the record is meant to build. The Google SRE model also mandates that postmortems not be left unreviewed: "An unreviewed postmortem might as well never have existed."

**ISO 27001:2022 Clause 10.2 — Nonconformity and Corrective Action.** This international standard for information security management systems mandates a structured, evidence-based response to any nonconformity (failure). The organization must react to the nonconformity, take action to control and correct it, deal with the consequences, evaluate the need for action to eliminate root causes, implement the action, review its effectiveness (the retest step), and retain documented information as evidence of the nature of the nonconformity and any subsequent action taken. The 2022 revision elevated Continual Improvement to Clause 10.1, explicitly signaling that improvement — not just correction — is the primary goal of the management system. The standard defines the Improvement Log as the central artifact: a structured record of what failed, what was done, and whether it worked.

**Chaos Engineering.** Pioneered by Netflix and formalized in the Chaos Engineering discipline, this practice involves deliberately injecting failures into a system to expose weaknesses before they manifest in production. The canonical process requires defining a measurable steady state, hypothesizing that the steady state will continue in both a control group and an experimental group, introducing variables that reflect real-world events (failures), and attempting to disprove the hypothesis. The failures are expected, recorded, and used to drive scoped corrections. The discipline explicitly requires that corrections be verified by re-running the same failure injection.

| Discipline | Canonical Name for Failure Record | Retest Required? | Correction Scope Enforced? |
|---|---|---|---|
| Google SRE | Blameless Postmortem | Yes (action item tracking) | Yes (action items must be proportionate) |
| ISO 27001 | Nonconformity and Corrective Action Log | Yes (effectiveness review) | Yes (root cause must be addressed) |
| Chaos Engineering | Experiment Result | Yes (steady state re-validation) | Yes (hypothesis must be re-tested) |

### Question 2: Is "Never Weaken a Test to Make it Pass" a Recognized Industry Principle?

**Verdict:** Yes — it is foundational in safety-critical software engineering and is the implicit contract of Test-Driven Development.

The prohibition against weakening tests to achieve a passing result is most rigorously codified in aviation software certification, where the consequences of a test failure being hidden are catastrophic.

**FAA DO-178C — Software Considerations in Airborne Systems and Equipment Certification.** DO-178C is the primary standard by which certification authorities (FAA, EASA) approve all commercial software-based aerospace systems. Its core discipline is that software is never delivered — only its evidence set is. Every requirement, design element, code block, and test case is a controlled Configuration Item (CI). Tests are derived strictly from requirements, not from code behavior. If a test fails, the only permissible responses are: (a) the code is wrong and must be fixed, or (b) the requirement is wrong and must be changed through a formal Engineering Change Proposal (ECP) reviewed by an independent Change Control Board (CCB). There is no third option of changing the test to match the code's actual behavior. As one analysis of the standard notes: "Functionality without proof is meaningless under DO-178C." The standard further requires that for DAL-A and DAL-B software, no requirement may be verified by its authors — all test design and execution must be done by people independent of the development team, specifically to prevent the subtle weakening of tests that occurs when the author of the code also authors the test.

**Test-Driven Development (TDD) — Red-Green-Refactor Cycle.** TDD, formalized by Kent Beck and widely adopted in commercial software engineering, establishes the same principle at the unit level. The cycle begins with writing a failing test (Red) that precisely defines the required behavior. The developer then writes the minimum code necessary to make the test pass (Green). Refactoring occurs only after the test passes. The inviolable rule of TDD is that the test defines the requirement, not the other way around. Weakening a test to make it pass is equivalent to changing the requirement without acknowledging the change — it destroys the traceability between the test and the behavior it was meant to enforce.

**NASA Software Assurance.** NASA's software assurance standards, developed for mission-critical systems, enforce the same principle through independent verification and validation (IV&V). IV&V teams are organizationally separate from the development team and are responsible for verifying that the software meets its requirements and validating that those requirements are correct. The separation of duties prevents any single team from both defining the test and deciding whether the test is adequate.

### Question 3: Is the Failure Record Itself the Durable Evidence of System Character?

**Verdict:** Yes — this is the explicit philosophy of the highest-reliability engineering domains.

The idea that the accumulated record of failures, root causes, and corrections constitutes the primary evidence of an organization's or system's maturity is not a novel claim. It is the operating philosophy of aviation accident investigation, automotive manufacturing quality, and information security management.

**NTSB Accident Investigation Reports.** The National Transportation Safety Board (NTSB) publishes exhaustive reports on every significant aviation accident. These reports are not merely administrative records — they are the institutional character of the aviation safety system. Each report documents the probable cause, contributing factors, and safety recommendations. The recommendations from past reports are tracked for implementation by the FAA and airlines. The accumulated body of NTSB reports is the primary mechanism by which aviation has achieved its extraordinary safety record over decades. The reports do not hide failures; they are the failures, preserved in permanent, public, searchable form.

**Toyota Production System — Andon Cord and Five Whys.** The Andon cord in Toyota's manufacturing system is a physical mechanism that empowers any worker to stop the entire production line when a defect is detected. This is followed by a "Five Whys" root-cause analysis, which asks "why" five times to trace the defect back to its systemic origin. The record of every Andon pull, every Five Whys analysis, and every resulting systemic fix is the tangible, accumulated evidence of Toyota's quality discipline. Toyota's competitive advantage in quality is not a claim — it is the sum of every recorded failure and its documented correction. The Andon cord is explicitly designed to make failure visible and permanent, not to hide it.

**ISO 27001 Continual Improvement (Clause 10.1).** The 2022 revision of ISO 27001 defines the Improvement Log as the central artifact of the ISMS. Auditors specifically ask: "Show me your Continual Improvement Log. What improvements have you implemented in the last six months that were not just fixing a direct audit finding?" The standard's audit focus on the improvement log — rather than on the absence of incidents — reflects the same philosophy: the failure record is the evidence of maturity, not a liability to be minimized.

### Question 4: Buyer-Facing Disclosure Norms — How Much of the Failure Record Should Be External?

**Verdict:** Partially — mature organizations share the process and the nature of corrections, but not the raw failure data.

The question of how much of an internal failure record to expose to external buyers (cyber-insurance underwriters, MSP clients) is one where industry practice is nuanced and deliberately tiered.

**The Internal / External Abstraction Layer.** The consensus across mature engineering organizations is that the internal failure record and the external-facing disclosure are two distinct artifacts serving two distinct purposes. The internal record is optimized for technical depth, candor, and learning. The external record is optimized for accountability, trust, and risk communication without exposing exploitable details. Rootly's analysis of public versus private postmortems notes that "private postmortems are optimized for internal collaboration and technical clarity," while "public-facing versions prioritize clarity, reassurance, and accountability for users, partners, and external stakeholders."

**Cloudflare's Public Postmortem Model.** Cloudflare is widely cited as a best-practice example of external transparency. Their public incident reports include a timeline of user-visible events, a high-level root cause, the actions taken to resolve the issue, and the systemic changes made to prevent recurrence. What they intentionally omit is: internal architecture details, specific employee names, raw logs, and any information that could serve as a roadmap for future attacks. The philosophy, as articulated in their engineering culture, is that "failure isn't shameful, hiding it is" — but the public record is a curated summary, not a raw dump.

**SOC 2 Type II as the B2B Standard.** For B2B SaaS products, the SOC 2 Type II report is the standard vehicle for demonstrating security posture to buyers. The report covers five Trust Service Criteria (Security, Availability, Processing Integrity, Confidentiality, and Privacy) and documents both the controls in place and the auditor's testing of those controls over a defined period (typically six to twelve months). The buyer receives the auditor's attestation of the process — not the raw internal failure logs. The SOC 2 framework explicitly separates the internal evidence (which the auditor reviews) from the external report (which the buyer receives).

| Audience | Appropriate Disclosure Level | Format |
|---|---|---|
| Internal engineering team | Full raw failure record, all root causes, all correction details | Internal postmortem / correction log |
| Cyber-insurance underwriter | Process description, control evidence, correction methodology, aggregate statistics | SOC 2 Type II, security questionnaire |
| MSP client review | Nature of correction, scope of fix, retest outcome, no raw exploit details | Curated incident summary |
| Public / press | Timeline, root cause category, systemic fix, no architecture details | Public postmortem blog post |

### Question 5: Is There Precedent for a Per-Event "Scoring Sheet" Distinct from a Metrics Dashboard?

**Verdict:** Yes — this artifact exists in both safety-critical certification and quality assurance, though terminology varies.

The per-event scoring sheet — a structured record that captures pass/fail status with plain-English reasoning for a single test event, distinct from aggregate metrics — is a recognized artifact in several engineering domains.

**DO-178C Individual Test Result Records.** DO-178C requires that every test case produce an explicit, traceable result record. The record includes the test case identifier, the requirement being tested, the test procedure, the expected result, the actual result, the pass/fail verdict, and the evidence supporting the verdict. This is not a dashboard or a summary — it is a per-event record tied to a specific requirement. The standard further requires that these records be retained as controlled Configuration Items, meaning they cannot be modified after the fact without a formal change record. The Vector DO-178C whitepaper notes that "the user has full control over which test case attributes are passed back to the requirements database," including the test name and test result.

**QA Evaluation Scorecards.** In customer experience quality assurance, scorecards are used to evaluate individual interactions (calls, emails, chat sessions) against defined criteria. Each scorecard captures the specific criteria evaluated, the score for each criterion, and the reasoning behind the score in plain language. This is explicitly designed to be distinct from aggregate metrics dashboards: the scorecard is the per-event record, while the dashboard aggregates scorecard results over time. The distinction matters because the scorecard is the primary evidence of what happened in a specific case, while the dashboard is a secondary summary.

**The Key Distinction.** The per-event scoring sheet and the metrics dashboard serve fundamentally different purposes. The scoring sheet is the primary evidence artifact — it answers "what happened in this specific case and why?" The dashboard is a secondary analytical tool — it answers "what is the trend across many cases?" A system that only produces dashboards cannot answer questions about specific cases. A system that only produces per-event records cannot answer trend questions. Both are necessary, but the per-event record is the foundation.

### Question 6: Is There a Recognized Term for Tests Designed to Fail Until Correction?

**Verdict:** Yes — the closest recognized terms are "Adversarial Exposure Validation" (AEV) and "Purple Teaming," both distinct from standard negative testing.

Standard negative testing checks that a system handles invalid inputs gracefully. The concept described here — tests that are specifically designed to demonstrate a defensive failure, and that are expected to continue failing until a scoped correction is applied and verified — is a distinct discipline with its own terminology.

**Adversarial Exposure Validation (AEV).** AEV, recognized by Gartner as an emerging security testing category, is defined as "the practice of executing attacker-like behavior to prove an attack path is exploitable in your environment, measuring detection, then re-running the same path after remediation to verify it stays closed." The key distinction from negative testing is the closed-loop verification requirement: the test is not considered complete when the failure is documented — it is only complete when the remediation has been applied and the same attack path has been re-executed and confirmed to fail. AEV explicitly treats remediation as a hypothesis to be tested, not an outcome to be assumed.

**Purple Teaming.** Purple teaming is a collaborative security testing methodology that combines Red Team (offensive) and Blue Team (defensive) capabilities. The Red Team executes attacks designed to expose specific defensive gaps. The Blue Team works to detect and remediate those gaps. The process is iterative: the Red Team re-executes the same attack after each Blue Team remediation to verify that the gap has been closed. The attacks are explicitly designed to fail (from the defender's perspective) until the correction is applied. Purple teaming is distinct from Red Teaming (which is adversarial and covert) and from standard penetration testing (which is point-in-time).

**MurphyGuard — Failure-First AI Agent Guardrails.** A 2026 paper by Nandan Singh proposes a framework for AI agent guardrail design rooted in Murphy's Law: "Anything that can go wrong, will go wrong." The framework formalizes failure-mode enumeration, layered defense architecture, chaos engineering for agents, and continuous adversarial validation. The paper explicitly describes the goal as shifting "AI safety engineering from reactive incident response to proactive, assumption-driven design — where every capability is treated as a potential failure surface until proven otherwise." This is the closest published precedent for applying the failure-first testing philosophy specifically to AI agent systems.

| Term | Domain | Key Characteristic |
|---|---|---|
| Adversarial Exposure Validation (AEV) | Security engineering | Closed-loop: execute, observe, remediate, re-execute |
| Purple Teaming | Security operations | Iterative: attack until defense is corrected |
| Chaos Engineering | SRE / infrastructure | Proactive: inject failure before it occurs naturally |
| Failure-First Design (MurphyGuard) | AI agent governance | Assumption-driven: treat every capability as a failure surface |
| Negative Testing | General QA | Reactive: verify graceful handling of invalid inputs |

### Question 7: AI Governance — System Proposes, Human Promotes

**Verdict:** Yes — the operator-authorization boundary is a standard governance control in GitOps, MLOps, and SOC 2 change management.

The principle that an automated or AI system may propose a correction but only a human operator may authorize its promotion to production is not a novel constraint — it is the standard governance model in mature DevOps, MLOps, and security compliance frameworks.

**GitOps Pull Request Approval Gates.** In GitOps workflows, all infrastructure and application changes are proposed as Pull Requests (PRs) in a version control system. Automated checks (linting, unit tests, security scans) run against the PR, but the final merge to the main branch — the promotion to production — requires explicit human approval from a designated reviewer. This enforces a strict separation of duties: the system (or an automated agent) may propose the change, but a human must authorize it. The approval is logged with the approver's identity and timestamp, creating an immutable audit trail.

**ML Model Governance with Approval Workflows.** In MLOps, the promotion of a machine learning model from development to staging or production is governed by explicit approval workflows. A data scientist may train and propose a model, but a manager or QA specialist must review the model's performance metrics and approve the promotion. The approval workflow maintains a complete log of who approved what and when. This prevents unverified models from affecting production systems and ensures that every production model can be traced back to a specific human authorization decision.

**SOC 2 Change Management Controls.** SOC 2 Type II audits specifically examine change management controls, which govern how changes to production systems are proposed, reviewed, tested, and approved. The standard requires that changes be authorized by appropriate personnel before implementation, that testing be completed before promotion, and that the authorization be documented. Automated systems may propose and even test changes, but the authorization step must involve a human with appropriate authority.

**The IEEE Governance Framework for AI Pipelines.** A 2025 IEEE paper on governance frameworks for AI development and operations pipelines describes an "enterprise governance control tower that offers decision gates" with "a waived status where risk tiers permit" and explicit requirements that gate decisions appear in a "gate decision log, enabling deterministic replay of approval history." This is precisely the operator-authorization boundary described in the NorthStar discipline: the system proposes, the gate records the decision, and only an authorized human can approve promotion.

### Gap Analysis (Part A)

The primary gap between the NorthStar Inbox Shield discipline and external best practice lies in the buyer-facing disclosure layer (Question 4). The discipline's intent to build long-term credibility through transparency is well-founded and aligns with the best practices of organizations like Cloudflare and those adhering to SOC 2. However, the discipline does not yet define the abstraction layer between the internal "agent bible" (the raw, unvarnished failure and correction record) and the external-facing disclosure (the curated summary appropriate for underwriting conversations or MSP client reviews). Mature organizations maintain this separation rigorously: the internal record contains everything, while the external record contains only what is necessary to demonstrate process maturity without exposing exploitable details. The NorthStar discipline should explicitly define what fields from the internal correction-evidence record are eligible for external disclosure, and under what conditions.

A secondary gap is in the terminology for adversarial tests (Question 6). The discipline describes tests designed to fail until correction, but does not yet use the recognized industry terms (Adversarial Exposure Validation, Purple Teaming, failure-first design). Adopting these terms would make the discipline legible to external reviewers (auditors, underwriters, technical buyers) who are familiar with the security engineering vocabulary.

### Rigor Assessment — Where NorthStar Is Already Ahead (Part A)

The NorthStar discipline is more rigorous than typical commercial software practice in two specific areas.

First, the absolute prohibition against weakening tests (Question 2) places the discipline at the level of DO-178C aviation software certification — a standard that most commercial software organizations, outside of aviation and medical devices, do not approach. In typical commercial practice, tests are routinely modified to accommodate changing code behavior without formal requirements review. The NorthStar doctrine that "corrections must be scoped, proportionate, and retestable; the failure record must persist regardless" is a materially higher standard than what most B2B SaaS organizations maintain.

Second, the treatment of the accumulated failure and correction log as the primary, durable evidence of the system's character (Question 3) is a level of engineering discipline usually reserved for the highest-stakes environments — NTSB investigations, Toyota's manufacturing floor, and ISO 27001-certified organizations. Most commercial software organizations rely on point-in-time metrics dashboards as their primary evidence of quality. The NorthStar discipline's insistence that the failure record itself is the evidence — not a summary derived from it — is ahead of typical industry practice and represents a genuine competitive differentiator in the cyber-insurance and MSP markets, where buyers are increasingly sophisticated about the difference between claimed security posture and demonstrated security discipline.

This document is a pre-spec research artifact. It does not constitute compliance documentation, certification evidence, or client-facing copy. All references to external standards and organizations are for research and validation purposes only.

---

## Part B — External Validation of a Failure-Preserving Test Discipline for NorthStar Inbox Shield

Across mature engineering domains, the closest analogue to the discipline you described is not one single doctrine but a stack of recognized practices: blameless postmortems, corrective-and-preventive action, requirements-based verification, defect tracking to closure, and controlled change management with effectiveness checks. The external record also supports your buyer-facing instinct that failures should be preserved internally and learned from, while external disclosure should usually be tiered and audience-specific rather than a raw dump of internal artifacts.

### Preserve failure, explain it, correct proportionately, and retest

**Google SRE — Blameless Postmortem for System Resilience.** Google defines a postmortem as a written record of an incident, its impact, actions taken, root causes, and follow-up actions to prevent recurrence. It explicitly says the goals are to document the incident, understand contributing causes, and put effective preventive actions in place, which is very close to your "preserve failure + record why + corrective action + retest" discipline.

**FDA — Corrective and Preventive Actions and CAPA basics.** FDA's CAPA materials describe the purpose of corrective and preventive action as collecting and analyzing information about actual and potential quality problems, taking appropriate action, and then verifying or validating the effectiveness of those actions. That is a near-direct match to your correction-evidence record, especially the "why warranted" and "retest evidence" fields.

**NIST — SP 800-61 Revision 3.** NIST says lessons learned from incident response activities and root cause analysis improve cybersecurity risk management and governance, and better prepare organizations for future detection, response, and recovery. In security engineering terms, that is a canonical "learn from failure and institutionalize the correction" model.

**Principles of Chaos Engineering.** Chaos engineering is explicitly defined as experimenting on a system to build confidence in its ability to withstand turbulent conditions. It is a recognized failure-injection discipline, although it is more about controlled resilience experiments than about keeping a per-case corrective-action dossier.

**Verdict:** Yes. Your discipline aligns strongly with recognized mature practices. The closest canonical names are blameless postmortem, CAPA, incident lessons learned, and, for the experimental side, chaos engineering / failure injection.

### Never weaken a test to make it pass

**FDA — General Principles of Software Validation.** FDA says an essential element of a software test case is the expected result, and that this expected result must come from a corresponding predefined specification. It also warns that testing that finds no errors may simply have been superficial, which supports your hard boundary against weakening or trivializing tests after the fact.

**FDA — Blood Establishment Computer System Validation in the User's Facility.** FDA states that each executed test case in a pre-defined written test plan should include input, expected output, actual output, acceptance criteria, and pass/fail status. That structure implies the acceptance bar is set before execution; changing the bar post-failure is contrary to the logic of the record.

**NASA — NPR 7150.2B and the SWEHB test-report guidance.** NASA requires projects to evaluate test results and record the evaluation, record defects identified during testing and track them to closure, update test plans and procedures so they remain consistent with software requirements, and maintain bidirectional traceability from test procedures to requirements. The NASA handbook also expects reports to capture problems encountered, deviations, anomalies, and the rationale for decisions, which again favors fixing the system or changing requirements under control rather than relaxing the test ad hoc.

**FAA public DO-178C guidance.** FAA's public guidance summarizing DO-178C emphasizes traceability from requirements to test cases and test results, and clarifies that testing is requirements-based. It also requires validation and verification of data across requirements management, problem reporting, change impact, and reviews, which supports the principle that if a test fails, the response must be justified through controlled engineering change rather than by quietly diluting the test.

**Verdict:** Partially. The industry principle is absolutely recognized, but usually under the language of predefined acceptance criteria, requirements-based testing, traceability, independence, and configuration/change control rather than a single slogan reading "never weaken a test to make it pass." The origin is strongest in safety-critical and regulated assurance cultures, not in one universally quoted maxim.

### Failure histories as durable evidence

**Google SRE — postmortems as institutional memory.** Google says that honest, timely postmortems reviewed by stakeholders and shared broadly are key to identifying corrective actions, and that aggregating structured data across many postmortems reveals trends and larger organizational investment needs. That is very close to your idea that the accumulation of failure records becomes the durable "character" of the system.

**NTSB — investigation reports.** The NTSB states that its accident reports contain the factual record, analysis, conclusions, probable cause, and related safety recommendations, and that its mission is to determine probable causes and issue recommendations aimed at preventing recurrence. That is a public-sector example of the failure record itself becoming the official evidence base for organizational learning and future design changes.

**Toyota Production System — jidoka, andon, kaizen, and Five Whys.** Toyota describes jidoka as stopping immediately when abnormalities are detected, preventing recurrence by clearly detecting abnormalities, and using andon to surface problems so supervisors can respond. Toyota's own materials also frame TPS as "consistently uncover issues, improve each issue, raise management standards," which is a strong analogue for your "agent bible" concept.

**NIST — incident lessons learned as governance input.** NIST SP 800-61r3 explicitly connects incident-response lessons learned and root-cause analysis to broader cybersecurity governance. That means the historical record of failures is not just tactical debris; it is governance evidence.

**Verdict:** Partially. There is strong published precedent for failure records serving as institutional memory, governance evidence, and continuous-improvement substrate. The exact phrase "evidence of character" is your framing, but it is a faithful interpretation of how mature organizations use postmortems, accident reports, and kaizen records.

### What to expose externally and what to keep internal

**AWS Well-Architected — tailored communication.** AWS recommends reviewing customer-impacting events, identifying contributing factors and preventative actions, and communicating contributing factors and corrective actions "as appropriate, tailored to target audiences." That is direct support for a tiered disclosure model rather than full raw exposure.

**Google Cloud — customer notification tied to impact.** Google Cloud's data-incident process says notifying customers is a key remediation activity when incidents affect customer data, and that product, legal, and communications leads evaluate the facts and build the communication plan. In practice, that means external disclosure is impact-driven and curated.

**AICPA — SOC 2 versus SOC 3.** AICPA says SOC 3 covers similar trust criteria as SOC 2 but with less detail and is general-use and freely distributable; its illustrative SOC 2 Type 2 materials, by contrast, include tests of controls and results. This is a mature assurance pattern: summarized public confidence artifact externally, more detailed restricted artifact for qualified reviewers.

**NIST SP 800-150 and ENISA cyber-insurance guidance.** NIST's threat-sharing guidance says organizations should define what may be shared, under what conditions, with which recipients, and with what redaction or handling rules, based on sensitivity and recipient trustworthiness. ENISA's cyber-insurance guidance similarly shows underwriters asking for evidence of formal programs, exercises, and maturity, while recognizing that some evidence may be anonymized or disclosed for insurer validation rather than public release.

**Verdict:** Yes. External precedent strongly supports exposing summarized impact, root cause category, corrective actions, and assurance artifacts to customers and reviewers, while keeping raw defect records, exploit-sensitive details, internal hypotheses, and unrestricted evidence trails inside controlled channels. That is what mature cloud and assurance organizations already do.

### Internal scoring sheets and per-event reasoning records

**FDA — executed test-case record.** FDA's validation guidance says each executed test case should record input, expected output, actual output, acceptance criteria, pass/fail, performer, and date. That is a published precedent for a per-event record that is distinct from dashboards and closer to your proposed scoring sheet.

**NASA SWEHB — software test report and test log.** NASA's guidance says a software test report should include remaining deficiencies, problems encountered, deviations from procedures, test logs, and "rationale for decisions." It also says test reports document how results match or differ from expected results and capture anomalies plus related corrective actions or problem reports.

**GAO citing IEEE 29119.** GAO criticized Federal Student Aid because many test cases lacked actual results or enough information to determine whether they passed, failed, or were executed at all, and it cited IEEE guidance that actual results should be documented and compared to expected results to determine the final result. This is a strong public example that the underlying artifact is expected to be an execution record, not merely a dashboard.

**FDA — device-software submission guidance.** FDA's device-software guidance expects system-level and lower-level test protocols to include expected results, observed results, pass/fail determination, and corresponding reports. That again supports the shape of your schema.

**Verdict:** Yes. The published precedents exist, but the standard names are usually test case execution record, test log, software test report, and sometimes test incident/problem report, not "scoring sheet." Your addition of a concise plain-English "why" column makes the artifact more readable than many standard implementations, not less aligned.

### Fail-first adversarial testing terms

**pytest — expected failure.** Pytest's xfail mechanism explicitly marks a test as one you expect to fail, commonly because a feature is not implemented or a bug is not fixed; if it unexpectedly passes, that is reported separately as an xpass. That is a recognized software-testing term for "designed to fail until correction."

**Martin Fowler — TDD "Red-Green-Refactor."** In TDD, the first step is deliberately to write a test that fails, then make it pass, then refactor. That is fail-first by design, though it is a development pattern rather than a defensive-assurance program.

**MITRE ATT&CK — adversary emulation and atomic testing.** MITRE describes adversary emulation as a type of red-team engagement that mimics a known threat using threat intelligence, and it describes Atomic Red Team as a way to test whether behaviors are detected as expected. MITRE's example explicitly walks through a case where the expected alert does not fire, the team fixes the issue, and thereby improves future defense.

**NIST — Red Team/Blue Team approach.** NIST defines red teaming as emulating a potential adversary to demonstrate the impact of successful attacks and what works for defenders in an operational environment. That is the recognized security term, but it does not by itself imply "known failing until corrected" in the same explicit way that xfail or TDD's red phase does.

**Verdict:** Partially. There is no single cross-domain term that perfectly means "adversarial tests designed to fail until correction." The best-matching terms are expected failure / xfail and red phase in software testing, and adversary emulation / atomic testing / red-team validation in security testing.

### Human-gated governance for AI-proposed corrections

**NIST AI RMF Playbook — governance, human roles, and approval states.** NIST's AI governance playbook says organizations should detail testing and validation processes, define and differentiate human roles and responsibilities for oversight, include legal and risk review processes, and establish policies for approval, conditional approval, and disapproval of design, implementation, and deployment. That is direct support for "system proposes, human authorizes promotion."

**NIST SP 800-171r3 — configuration change control.** NIST says organizations should review proposed configuration-controlled changes, approve or disapprove them with explicit consideration for security impacts, implement and document approved changes, and monitor/review associated activities. That is a formal public control statement for a human-gated promotion model.

**NIST SP 800-128 — change control and security impact analysis.** NIST describes configuration change control as a documented process involving proposal, justification, implementation, testing/evaluation, review, and disposition of changes; it also says security impact analysis determines how a change affects the system's security posture and is performed by qualified staff. This strongly favors sandboxed proposal plus reviewed promotion, not self-promoting mutation.

**OpenGitOps — versioned desired state.** OpenGitOps defines GitOps as a structured, standardized approach where desired state is versioned and becomes the control point for operational change. By itself that does not mandate human approval, but combined with NIST-style approval/disapproval controls it is a natural governance model for keeping AI-generated fixes in proposal space until a human promotes them.

**Verdict:** Yes. The recognized governance pattern is human-reviewed change control over versioned proposed state, with explicit approval/disapproval and impact analysis before implementation. Nothing in these sources pushes toward auto-promotion; if anything, they argue the opposite.

### Gaps and places you are already ahead (Part B)

The main gap I would consider addressing is formalization of decision rights and closure criteria. External best practice suggests that once you preserve failures, you should also make explicit who is allowed to approve a corrective action, what counts as sufficient retest evidence, when independent review is required, how change-impact analysis is recorded, and what external disclosure tier a given failure belongs to. In your case, that likely means adding a hard approval state to the correction-evidence object, a mandatory impact-analysis field for neighboring detections and false-positive risk, and an audience-classification field for buyer-safe summaries versus internal-only evidence. That recommendation is an inference from NIST's approval/disapproval and risk-governance language, NASA/FDA's emphasis on objective evidence and traceability, and NIST/AICPA guidance on sensitivity-based sharing.

Where your discipline already appears more rigorous than typical industry practice is in the insistence on a single scannable record that keeps the original failure alive, names the failure type, explains the reasoning in plain English, records why the corrective action was warranted, and preserves retest evidence plus proportionality. The public precedents generally distribute those elements across separate artifacts — test execution records, defect logs, postmortems, CAPA records, and restricted assurance reports — rather than unifying them into one durable per-case evidence object. So your design is not merely aligned; in this respect it is stricter and more inspectable than what many mature organizations publicly document. That is an inference from the shape of FDA, NASA, Google SRE, and AICPA artifacts.

---

**End of research capture. No gate required.**
