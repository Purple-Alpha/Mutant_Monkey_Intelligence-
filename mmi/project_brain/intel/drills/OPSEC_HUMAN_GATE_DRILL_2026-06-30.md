# OPSEC Human Gate — Vendor/Email Defense Baseline & Matt's Gate

**Task:** `mmi-opsec-human-gate-tightening` (worksheet phase — **task not closed**)  
**Mode:** LOCAL / NON-DESTRUCTIVE / HUMAN-ONLY / ADVISORY  
**Authority:** Matt (Super) — Canadian operator  
**Intel drivers:**
- `intel/briefs/INTEL_polymorphic-ransomware-delivery_2026-07.md` (T1566.002, T1204.001, T1027.006 — delivery/execution; no SEG on Mini PC)
- `intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md` (T1486/T1490 — impact/recovery; OPSEC-9 at first suspicion)

**Purpose:** Before marking OPSEC-4, OPSEC-5, or OPSEC-9 `DONE`, document what common email/vendor-platform defenses **can** prove vs what they **cannot** prove. Matt's human gate covers the gap — especially for **action-bearing vendor email** (payment, banking, login, admin, credential, or link/attachment that triggers action).

**Hard stops:** No vendor guarantees safety. No claim that email alone establishes business truth. No SOAR, EDR, endpoint agents, auto-containment, or automation. Platform defenses and human gate are **separate layers**.

---

## 1. Vendor / email-platform defense baseline

What enterprise and consumer email stacks **typically** add (configuration-dependent; Matt may have some, none, or partial on any given mailbox). Listed for **baseline literacy**, not as Matt's deployed stack claim.

### Microsoft Defender for Office 365 (Exchange Online / M365)

| Control | What it tries to do |
|---------|---------------------|
| Anti-phishing policies | Detect impersonation, spoofing patterns, suspicious senders |
| Anti-spoofing / impersonation protection | Flag lookalike domains, display-name spoofing, VIP impersonation |
| Safe Links | Rewrite/wrap URLs; time-of-click scan against known threats |
| Safe Attachments | Detonate attachments in sandbox; block known-malicious payloads |
| SPF/DKIM/DMARC alignment (tenant + DNS) | Reject or quarantine mail that fails authentication policy |

### Google Workspace / Gmail

| Control | What it tries to do |
|---------|---------------------|
| SPF / DKIM / DMARC requirements | Enforce or warn on authentication failures per admin policy |
| Phishing & malware protection | Filter known-bad senders, links, and attachments |
| Spoofing & authentication protection | Warn on unauthenticated or suspicious sender patterns |
| Security Sandbox (Advanced) | Dynamic analysis of attachments/links in Google infrastructure |

### Optional third-party SEG examples (Proofpoint, Mimecast, similar)

| Control | What it tries to do |
|---------|---------------------|
| BEC / impersonation detection | Heuristics on executive/vendor fraud patterns |
| Supplier / domain compromise awareness | Watch for compromised partner domains or thread hijacks |
| URL protection / rewrite | Time-of-click analysis, categorization, block lists |
| Reporting & quarantine | User report phish; admin release/hold workflows |

**Matt's Mini PC / local-first MMI context:** MMI v1 does **not** deploy or operate these controls. They may exist on Matt's personal or business mailboxes elsewhere — but **absence on the operator workstation** means the human gate remains the pre-execution control per `INTEL_polymorphic-ransomware-delivery_2026-07.md` §2.

---

## 2. What these controls can prove

Platform defenses, when configured and functioning, can support **technical mail hygiene** — not **business authorization**.

| Platform can show (sometimes) | Meaning |
|-------------------------------|---------|
| Message passed configured policy checks | Mail was not blocked by rules the tenant actually enforces |
| SPF/DKIM/DMARC may align | Sending infrastructure matched DNS policy at receipt — **not** that the human sender intended the request |
| Known-malicious URL or attachment may be blocked | Blocklist/sandbox caught a **known** pattern |
| Some spoofing / impersonation may be flagged | Display-name or domain lookalike heuristics fired |
| Quarantine / warning banner may appear | Platform doubted the message — operator may still override |

**Label:** `[Platform hygiene — not business truth]`

---

## 3. What these controls cannot prove

This is the gap Matt's human gate must cover.

| Platform cannot prove | Why it matters for Matt |
|-----------------------|-------------------------|
| The vendor **intended** the request | Compromised vendor mailbox, forged thread, or insider fraud looks like "real" mail |
| A payment or banking change is **legitimate** | BEC and invoice fraud pass SPF; urgency is social, not cryptographic |
| A real vendor mailbox is **not compromised** | Authenticated mail from a hacked account is still authenticated |
| A delivered link or attachment is **safe enough to act on** | HTML smuggling (T1027.006), human-only triggers, and time-of-click evasion bypass first-pass filters |
| The email thread itself is **authority** | Reply-chain hijack and lookalike domains exploit trust in the thread |
| Urgency is **justified** | Pressure tactics are content, not a signal platforms reliably score |
| Contact details in the message are **trustworthy** | Phone numbers and reply addresses in the suspicious mail are attacker-controlled |

**Core separation:**

```text
Platform defense  →  "This message met (or failed) our mail-security rules."
Human gate        →  "I have verified business truth through a channel I already trust."
```

Email alone never satisfies the second line for action-bearing vendor mail.

---

## 4. Matt's human gate (action-bearing vendor email)

**Scope:** Any vendor or supplier email that asks Matt to **pay, change banking, log in, reset credentials, approve admin access, open an unexpected attachment/link, or act under urgency** — whether or not a platform banner says "safe."

### 4.1 Pause triggers (any one → stop before acting)

- **New** — first time this vendor asks for this action type  
- **Unusual** — amount, account, domain, tone, or process differs from prior known-good pattern  
- **Urgent** — pressure to bypass normal verification  
- **Payment-related** — invoice, wire, EFT, banking detail change  
- **Login-related** — password reset, MFA change, "verify account"  
- **Admin-related** — new user, API key, domain/DNS change  
- **Attachment/link-heavy** — unexpected file or link is the primary call to action  
- **Unverifiable** — no independent way to confirm except the email itself  

### 4.2 Rules (non-negotiable for action-bearing vendor mail)

| Rule | Rationale |
|------|-----------|
| **Do not use contact details from the suspicious email** | Phone numbers, reply addresses, and "call this number" in the thread are attacker-controlled |
| **Verify through a known-good channel** | Prior saved contact, vendor portal logged in separately (typed URL), or phone number from contract/onboarding file — not from the email |
| **Record the decision at first suspicion (OPSEC-9)** | Timestamp before investigation spirals; feeds war room Axis B |
| **Link-hover + sender/reply-to/domain check (OPSEC-4)** | Before any click on unexpected mail — blunts T1566.002 / pre-T1204.001 |
| **Out-of-band confirm before payment/credential change (OPSEC-5)** | Business-truth layer on top of platform hygiene |

### 4.3 What "known-good channel" means

| Acceptable | Not acceptable |
|------------|------------------|
| Phone number from signed contract or vendor onboarding record | Number or link in the suspicious email |
| Vendor portal: type URL from bookmark/password manager | Click link in email to "portal" |
| Separate chat thread established **before** this request | Reply-all on the suspicious thread only |
| Callback to accounting contact on file | "Press 1" or SMS from unknown sender |

### 4.4 Mini PC / no-SEG note

Even if Matt's mailbox elsewhere has Defender or Gmail protection, **the Mini PC operator path** has no MMI-level mail filter or EDR. Human gate is the only pre-execution control between click and payload (`INTEL_polymorphic-ransomware-delivery_2026-07.md` §2).

---

## 5. Closeout criteria for OPSEC-4 / OPSEC-5 / OPSEC-9

Checklist items stay **`NOT_STARTED`** until Matt completes evidence below. Worksheet defines criteria; **habit proof is Matt's closeout step** — not assumed by this file alone.

### OPSEC-4 — Link-hover + sender / reply-to / domain check

**Documented habit (this worksheet):** Before clicking any unexpected link, Matt hovers the URL, checks display name vs From address, inspects Reply-To if shown, and compares domain to prior known-good vendor pattern.

**Evidence required to mark DONE:**

- [ ] Matt self-attestation date recorded in checklist  
- [ ] One weekly spot-check note: one real email reviewed against the four checks (no PII in repo — "reviewed 2026-__-__; domain mismatch flagged on marketing mail" suffices)

### OPSEC-5 — Known-good out-of-band confirmation

**Documented rule (this worksheet):** No payment detail change, wire, or credential change initiated from email alone. Confirm via known-good channel per §4.3.

**Evidence required to mark DONE:**

- [ ] Rule acknowledged in checklist `verify_method`  
- [ ] One real or drill invocation logged in decision log (§6 dry-run counts for **worksheet** evidence only — real invocation preferred for DONE)

### OPSEC-9 — Decision log at first suspicion

**Documented template:** §6 below (aligned with `WAR_ROOM_SCORING_MATRIX_v2.md` §7 decision log block).

**Evidence required to mark DONE:**

- [ ] Template copied to a real or drill incident path  
- [ ] First entry timestamped **before** further investigation  
- [ ] Dry-run below completed for worksheet phase; replace with real incident entry when applicable

---

## 6. Decision log — template + dry-run entry

### Template (copy per incident or drill)

```markdown
decision_log_id: DL-<yyyy-mm-dd>-<short-slug>
opened_at: <ISO8601 local>
opened_by: Matt
trigger: <first suspicion — one line>
platform_banner_seen: yes | no | n/a
action_bearing_vendor_email: yes | no
human_gate_applied: OPSEC-4 | OPSEC-5 | OPSEC-9 | none yet
known_good_channel_used: <describe channel — no secrets>
outcome: paused | verified-legit | false-alarm | drill-only
next_action: <one line>
```

### Dry-run entry (worksheet evidence — drill-only)

```markdown
decision_log_id: DL-2026-06-30-vendor-wire-drill
opened_at: 2026-06-30T16:00:00-07:00
opened_by: Matt
trigger: Drill — simulated vendor email requests urgent wire to new bank account; display name matches known supplier.
platform_banner_seen: n/a (drill — no live mail processed)
action_bearing_vendor_email: yes
human_gate_applied: OPSEC-9 (log opened first) → OPSEC-4 (hover: lookalike domain vendor-payments-secure.com vs known acme-supplier.ca) → OPSEC-5 (declined to use phone in email; called accounting contact from onboarding PDF on file)
known_good_channel_used: Phone from 2024 vendor onboarding record — not from email body
outcome: drill-only — would have paused live payment
next_action: No wire; would request invoice through portal bookmark; real vendor notified out-of-band if live
```

**Dry-run proves the workflow is defined — not that the habit is automatic.** OPSEC-9 remains habit-dependent until Matt repeats under real or quarterly drill conditions.

---

## 7. Mapping: platform layer vs human gate vs intel brief

| Stage | Platform (if present) | Matt human gate | Intel ref |
|-------|----------------------|-----------------|-----------|
| Delivery (link in mail) | May warn/quarantine | OPSEC-4 pause | T1566.002 |
| Execution (click) | Safe Links may miss smuggled/HTML | OPSEC-4 — don't click unverified | T1204.001, T1027.006 |
| Business action (pay/credential) | BEC heuristics incomplete | OPSEC-5 known-good channel | T1204.001 (social) |
| First suspicion | N/A | OPSEC-9 log timestamp | Axis B; T1486 if escalates |
| Impact (encryption) | N/A | OPSEC-6/7/8 recovery | T1486 |

---

When evidence lands, update `OPERATOR_OPSEC_CHECKLIST.md` only.

---

## 8. Addendum — unsourced Canadian SMB email summary (research input only)

**Source:** Matt-pulled Google/AI-style summary about Canadian SMB email behaviour (2026-06-30).  
**Classification:** **RESEARCH INPUT ONLY — NOT AUTHORITY.** Do not cite exact statistics from this source in checklist, brief headlines, or operator-facing claims without a named primary benchmark.

### 8.1 Claim classification

| Topic | Classification | MMI use |
|-------|----------------|---------|
| CASL / PIPEDA compliance framing | **PARTIALLY SUPPORTED** — narrow wording required | See §8.2; not proof of vendor suspicious-email handling |
| Email open-rate, CTR, MPP, behaviour-email statistics | **NEEDS VERIFY** | Do not use exact numbers without primary benchmark source |
| Deliverability, SPF/DKIM/DMARC, platform tooling | **DIRECTIONALLY SUPPORTED** | Platform hygiene only — same layer as §2, not business truth |
| Vendor suspicious-email inspection routines | **NOT SUPPORTED by this source** | Do not treat this summary as evidence of how vendors verify operational mail |

### 8.2 CASL / PIPEDA — narrow wording

**CASL** applies to **commercial electronic messages (CEMs)**, not every ordinary business email. **PIPEDA** governs personal information handling in commercial activity — including electronic addresses in many contexts.

Together they support this **narrow** statement only:

> Canadian vendors face compliance pressure around **marketing/commercial email** and **electronic-address handling**.

They **do not** prove:

- How vendors inspect **suspicious operational emails** (invoices, wire requests, credential changes)  
- That compliance equals **safe-to-act** status for Matt  
- **Vendor intent**, payment legitimacy, or uncompromised mailboxes  

### 8.3 MMI rule (reaffirmed)

```text
Platform hygiene + legal compliance  ≠  business truth
Human known-good verification          =  required for action-bearing suspicious email
```

This addendum does **not** change OPSEC-4/5/9 checklist state. Habit evidence remains Matt-owned per §5.

---

## Sign-off

**PASS WITH REVISIONS — task closed; operator habit evidence NOT proven**

Vendor/email-platform defense baseline documented; provable vs non-provable separation explicit; Matt's human gate defined for action-bearing vendor email; OPSEC-4/5/9 closeout criteria and decision-log dry-run present; §8 addendum quarantines unsourced SMB email stats.

```text
Task closed ≠ OPSEC controls proven.
```

**Task `mmi-opsec-human-gate-tightening`:** closed at worksheet + criteria layer. **OPSEC-4/5/9 checklist rows remain `NOT_STARTED` (known operator-risk).** No fabricated `last_done` dates; dry-run is definition evidence only, not habit proof.

**NOT DONE (Matt-owned, no timeline assumed):**

- [ ] OPSEC-4 real spot-check attestation  
- [ ] OPSEC-5 real out-of-band invocation  
- [ ] OPSEC-9 real decision-log habit  

When evidence lands, update `OPERATOR_OPSEC_CHECKLIST.md` only — do not treat worksheet completion as habit proof.
