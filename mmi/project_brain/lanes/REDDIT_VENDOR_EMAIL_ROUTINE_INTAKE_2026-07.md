# Reddit Vendor Email Routine — Field Evidence Intake

**Date:** 2026-07-01  
**Authority:** Matt (Super) — field input lane  
**Status:** **Informal field evidence — NOT authority, NOT statistics**  
**Purpose:** Collect and classify informal Reddit evidence about how SMB operators/vendors handle business email. Guides MMI design and human-gate research — must not become headline claims or Canadian-primary evidence unless commenter explicitly states Canadian context.

**Related:** `intel/drills/OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` (platform vs business-truth gap); OPSEC-4/5/9 remain **NOT_STARTED** on live checklist.

**Hard rules:**

- Reddit = behaviour patterns, not verified facts  
- Do not convert anecdotes into statistics  
- Do not invent industry, country, size, or tooling not stated  
- Do not treat as Canadian-primary unless commenter says so  
- No new intel brief; no OPSEC state changes from this file  

**Community (Matt confirmed 2026-07-02):** [r/CyberSecurityAdvice](https://www.reddit.com/r/CyberSecurityAdvice/) — OP-1 thread on r/CyberSecurityAdvice (Matt paste 2026-07-03; permalink still not supplied).

---

## Capture template (per response)

```text
Source: Reddit
Thread/topic:
Date captured:
Responder type if stated:
Industry if stated:
Business size if stated:
Country/jurisdiction if stated:
Exact behaviour described:
Security tools mentioned:
Human checks mentioned:
Verification habits:
What they ignore/delete/archive:
Pain points:
Confidence:
Use in MMI:
```

---

## Classification buckets

| Label | Meaning |
|-------|---------|
| `REAL_ROUTINE` | What they actually do day to day |
| `PLATFORM_DEPENDENCE` | Relies on Microsoft, Google, spam filter, Defender, etc. |
| `HUMAN_GATE` | Sender check, link hover, call vendor, verify payments |
| `NO_FORMAL_PROCESS` | Wing it, gut feel, no routine |
| `PAIN_POINT` | Friction, wish software did better |
| `CONTRADICTION` | Vendors/operators do opposite things |
| `SECURITY_GAP` | Behaviour that creates risk |
| `PRODUCT_DIRECTION_INPUT` | Field pressure on product scope, positioning, or workflow fit |
| `OP_RESEARCH_QUESTION` | Original poster question / outreach framing — not responder behaviour |
| `NOT_USEFUL` | Joke, vague, no operational value |

---

## OP / research question captures

*These are outreach posts — useful for how we frame questions, not as evidence of SMB behaviour.*

### OP-1 — Matt outreach (SMB vendor email routines)

| Field | Value |
|-------|--------|
| **ID** | OP-1 |
| **Source** | Reddit post (Matt outreach — self-reported) |
| **Community** | **r/CyberSecurityAdvice** (Matt confirmed 2026-07-02) |
| **Thread/topic** | SMB vendor email routines — Matt OP (r/CyberSecurityAdvice; permalink not supplied) |
| **Date captured** | 2026-07-03 (OP active on thread) |
| **Poster type** | Brand new, self-taught builder |
| **Stated product intent** | Cybersecurity software to help **Canadian SMBs** |
| **Labels** | `OP_RESEARCH_QUESTION`, `PRODUCT_DIRECTION_INPUT` |
| **Confidence** | N/A — not field behaviour; captures **research framing** only |

**Source text (verbatim):**

```text
Hey peeps i was just wondering what smb vendors do with all there business emails when they come in

I'm building cybersecurity software to help canadian smb's and i'm trying to understand what people actually do with emails day to day not theory

When you get invoices vendor requests payment changes attachments links password resets or account updates what rules do you follow before opening or trusting them

How do you check your not getting scammed do you look at the sender hover over links call the vendor check the domain rely on spam filters or just go by gut feeling

I'm not looking for private info or company names just trying to learn what real people actually do with email
```

**What OP-1 is good for:**

- Honest learner framing — asks for **real routines**, not theory  
- Lists **action-bearing mail types** — invoices, payment changes, password resets, account updates (aligns with business-action integrity lane)  
- Asks about **verification habits** — sender, hover, call vendor, domain, spam filter, gut feel  

**Tension with field responses (R3, R5, R6, R7):**

| OP-1 framing | Responder pushback |
|--------------|-------------------|
| Centered on **email day-to-day** | "Email is only part of the process" |
| Trust/opening rules **in the inbox** | Payment may already verify in AP / callback **outside** email |
| "Cybersecurity software" + Canadian SMB | Reads as crowded spam-filter / awareness lane unless wedge is explicit; invites builder-credibility challenge (R7) |
| Open question — all operators | Responders: pick **target demographic** (Sally vs SOC) |

**MMI use (design only — not authority):**

- Keep OP-style outreach for **habit discovery** — but follow-up questions should include: *"What happens after you read the email — who approves payment, matches invoice, calls vendor?"*  
- Do **not** use OP's Canadian SMB line as field evidence — it's **builder intent**, not commenter jurisdiction  
- Product research should trace **email → business action**, not stop at "how do you trust this message"  

**What must NOT be claimed:**

- Do not cite OP-1 as proof of what Canadian SMBs do  
- Do not treat responses to this thread as Canadian-primary unless commenters say so  
- Do not position MMI in outreach as generic "cybersecurity software" — invites R3/R6/R7 crowded-lane and builder-trust critique  

---

## Response cards

### R1 — Matt-supplied (thread context: SMB vendor email routines)

| Field | Value |
|-------|--------|
| **Source** | Reddit (Matt capture — raw paste) |
| **Thread/topic** | SMB vendor email routines (exact thread URL not supplied) |
| **Date captured** | 2026-07-01 |
| **Responder type** | Not stated |
| **Industry** | Not stated |
| **Business size** | Not stated |
| **Country/jurisdiction** | Not stated — **do not treat as Canadian evidence** |
| **Exact behaviour** | "Delete all I can especially spam. Archive when needed. Resolve. Target: zero inbox" |
| **Security tools mentioned** | None named (implicit inbox/spam handling only) |
| **Human checks mentioned** | None explicit — no sender hover, no out-of-band verify |
| **Verification habits** | None described for payment/credential changes |
| **Ignore/delete/archive** | Delete (especially spam); archive when needed; resolve items; inbox-zero target |
| **Pain points** | Implied volume/spam burden (delete-heavy workflow) |
| **Labels** | `REAL_ROUTINE`, `PAIN_POINT`, `SECURITY_GAP` (see gap analysis) |
| **Confidence** | **LOW** — single anecdote, no responder metadata, no suspicious-email branch described |
| **Use in MMI** | Illustrates **normal email hygiene** vs missing **action-bearing suspicious branch**; supports human-gate worksheet §3 gap — platform/inbox workflow ≠ payment/link verification |

**Routine described (normal handling):**

```text
Normal:
Delete spam aggressively; archive when needed; resolve threads; pursue inbox zero.
Relies on triage/delete/archive — not on verifying vendor intent for operational mail.
```

**Gap analysis (normal vs suspicious/action-bearing):**

```text
Normal:
Open/triage/delete/archive — optimize for inbox zero and spam removal.

Suspicious / action-bearing:
Not described — no rule for payment-detail changes, unexpected links, or vendor impersonation.

Gap:
Operator may treat all mail through the same delete/archive/resolve funnel.
Urgent invoice or wire-request email may get "resolved" or archived without known-good verification.
Link/sender checks and OPSEC-4/5 behaviours are absent from this self-reported routine.
```

**MMI relevance:**

- Confirms Level 1/2 chaos finding: **interpretation layer** — inbox hygiene ≠ human gate for action-bearing mail  
- Does **not** support any prevalence or Canadian stat  
- Informs OPSEC-4/5 worksheet examples only (field colour, not proof)  
- Contrasts with `OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` §4 — platform hygiene does not prove business truth  

---

### R2 — Reddit field response (SMB informal email handling)

| Field | Value |
|-------|--------|
| **ID** | R2 |
| **Source** | Reddit field response |
| **Thread/topic** | SMB email handling / informal trust patterns (exact thread URL not supplied) |
| **Date captured** | 2026-07-01 |
| **Responder type** | Not specified |
| **Industry** | Not stated |
| **Business size** | SMB (general framing in response — not quantified) |
| **Country/jurisdiction** | **Unknown — not Canadian-primary evidence** |
| **Labels** | `REAL_ROUTINE`, `HUMAN_GATE`, `NO_FORMAL_PROCESS`, `PAIN_POINT`, `SECURITY_GAP` |
| **Confidence** | **MEDIUM** — richer operational detail than R1; still anecdote, no jurisdiction |

**Source text (verbatim):**

```text
From what I've seen with most SMBs, email handling is pretty informal unless they've already been burned. Usually it's a quick skim of sender name and subject, maybe checking if it "feels" right, then opening it. A lot of trust is based on familiarity rather than real verification. Only a few consistently check domains, hover links, or verify attachments before opening. Rules and processes usually show up after a scare, not before. If your product can fit naturally into that fast, low-friction workflow without requiring people to think like security pros, that's where it'll actually get used.
```

**Behaviour described:**

The responder says SMB email handling is often informal unless the business has already been burned. Typical handling is a quick skim of sender name and subject, checking whether the email "feels" right, then opening it.

**Human checks mentioned:**

- Sender-name skim  
- Subject-line skim  
- Gut-feel / familiarity check  
- Some users check domains  
- Some users hover links  
- Some users verify attachments  

**Security gap:**

Trust is often based on familiarity rather than verification. Formal rules and processes usually appear after a scare, not before.

**Product implication:**

The product must fit into a fast, low-friction SMB workflow. It should not require users to think like security professionals. It should add lightweight verification at the point where an email asks for action.

**MMI relevance:**

- Supports the human-gate model, OPSEC-4/5/9 known operator-risk, and the quality redesign finding that **interpretation-layer failures** are still the main snap surface  
- Aligns with `MMI_QUALITY_ELEVATION_REDESIGN_2026-07.md` — Great blocks bad evidence; SMBs need **low-friction** verification at action points, not heavy security workflows  

**What must NOT be claimed:**

- Do not treat this as a statistic  
- Do not treat this as Canadian-primary evidence  
- Do not claim "most Canadian SMBs" behave this way  
- Do not convert Reddit anecdote into verified market fact  

**Product truth captured (design input only):**

```text
SMB email trust often starts with familiarity and gut-feel, not formal verification.
MMI must reduce verification friction instead of forcing SMBs into heavy security workflows.
```

**Gap analysis (R2 vs OPSEC-4/5):**

```text
Described routine:
Skim sender/subject → gut-feel → open. Familiarity > verification.

Partial human gate:
Domain check, link hover, attachment verify — "only a few" consistently.

Missing for MMI OPSEC-4/5:
No out-of-band payment confirmation; no decision-log at suspicion;
no distinction between "feels familiar" and "verified vendor intent."
Post-scare process adoption ≠ proactive human gate.
```

---

### R3 — Email is only part of the business process

| Field | Value |
|-------|--------|
| **ID** | R3 |
| **Source** | Reddit field response |
| **Thread/topic** | SMB email / vendor workflow / product scope challenge (exact thread URL not supplied) |
| **Date captured** | 2026-07-01 |
| **Responder type** | Not specified |
| **Industry** | Not stated |
| **Business size** | Not stated (general business framing) |
| **Country/jurisdiction** | **Unknown — not Canadian-primary evidence** |
| **Labels** | `REAL_ROUTINE`, `PAIN_POINT`, `SECURITY_GAP`, `CONTRADICTION`, `PRODUCT_DIRECTION_INPUT` |
| **Confidence** | **MEDIUM-HIGH** — detailed workflow critique; still anecdote, no jurisdiction |

**Source text (verbatim):**

```text
email is only part of the process.

Like invoices might have a second verification system in place to match up against before anything is paid or a way to confirm with the requesting company.

But what are you really trying to solve? There are hundreds of companies already in this space and some are doing very well. It sounds like you are looking to develop a spam filter, mail tips and a security awareness training system in one without having a decent idea of how a business works. Remember IT enables business and every business is different. You could build a new workflow and try to get the business to change their ways to fit your product or work with the business to work with their workflows.

And to top this off, the people vary too. You could have an old Sally in accounting that clicks everything or sharp eyed SOC analyst putting everything under 5 different microscopes. So if you are building software you need to figure out your target user demographic so you can build your tool to suit them.
```

**Behaviour / process described:**

The responder says email is only one part of the business workflow. For invoices and payments, some businesses may already have a second verification process, matching system, approval workflow, or direct confirmation path with the requesting company before payment is made.

**Human / business checks mentioned:**

- Invoice/payment verification may happen outside email  
- Invoices may be matched against another system before payment  
- Requests may be confirmed with the requesting company  
- Controls vary heavily by business  
- Users vary from high-risk clickers to trained analysts  

**Security gap:**

A product focused only on email may miss the actual decision point. The risk may not be "email received" but "email causes payment, login, approval, or process change." Different businesses may already have partial controls outside the inbox.

**Product challenge:**

The responder challenges whether the product is really solving a specific business problem or trying to combine spam filtering, mail tips, and awareness training without enough workflow understanding.

**Product implication:**

MMI should not position itself as just another spam filter or generic awareness tool. The stronger direction is workflow-aware verification support for action-bearing email, especially vendor/payment/admin requests.

The product should fit the business's existing workflow instead of forcing a new workflow too early.

**MMI relevance:**

- Email is an input, not authority.  
- Business truth often lives outside the email thread.  
- Known-good verification matters.  
- Target user demographic must be defined clearly.  
- Low-friction workflow fit matters more than generic security advice.  

**What must NOT be claimed:**

- Do not treat this as a statistic  
- Do not treat this as Canadian-primary evidence  
- Do not claim all SMBs have second verification systems  
- Do not claim all users are careless or all users are sophisticated  
- Do not use this as proof that the product is invalid; use it as product-scope pressure  

**Product truth captured (design input only):**

```text
Email is not the whole process. The product must protect the business decision that follows the email, not just classify the email itself.

MMI should work with existing SMB workflows instead of assuming all businesses handle invoices, vendors, and approvals the same way.
```

**Gap analysis (R3 vs MMI doctrine):**

```text
Described reality:
Email triggers downstream business actions; controls may live in AP, ERP, or direct vendor confirmation.

Product risk if MMI stops at inbox:
Misses payment/approval/login decision points; duplicates spam-filter/awareness crowded market.

MMI alignment:
Workflow-aware verification at action-bearing moments; fit existing process; define target user demographic.
```

---

### R4 — Existing baseline: spam filtering + basic security training

| Field | Value |
|-------|--------|
| **ID** | R4 |
| **Source** | Reddit field response |
| **Community** | r/CyberSecurityAdvice |
| **Thread/topic** | SMB / business email baseline controls (exact thread URL not supplied) |
| **Date captured** | 2026-07-01 |
| **Responder type** | Not specified |
| **Industry** | Not stated |
| **Business size** | Not stated |
| **Country/jurisdiction** | **Unknown — not Canadian-primary evidence** |
| **Labels** | `REAL_ROUTINE`, `BASELINE_CONTROL`, `SECURITY_TRAINING`, `PRODUCT_DIRECTION_INPUT` |
| **Confidence** | **MEDIUM** — operational baseline description; still anecdote, no jurisdiction |

**Source text (verbatim):**

```text
There's spam filtering, and basic security/phishing training. Don't download anything, view everything in email if possible
```

**Behaviour / process described:**

The responder describes the common baseline as spam filtering plus basic phishing/security training. The practical user guidance is to avoid downloading files and view content inside email where possible.

**Controls mentioned:**

- Spam filtering  
- Basic security / phishing training  
- Avoid downloading attachments  
- View content inside the email client where possible  

**Product implication:**

This suggests that a generic product framed as spam filtering, mail tips, or awareness training risks being undifferentiated.

MMI should not position itself as another spam filter or generic phishing training tool.

The stronger product lane remains:

`business-action verification and evidence support for risky email-triggered decisions`

**MMI relevance:**

- Existing tools already cover basic filtering and training  
- User advice alone is weak because humans still click, download, approve, or trust  
- MMI should focus on action-bearing emails, verification, evidence, and recovery  
- The product must add value after baseline controls have already existed  

**What must NOT be claimed:**

- Do not claim all businesses have sufficient spam filtering  
- Do not claim training is effective  
- Do not treat this as a statistic  
- Do not treat this as Canadian-primary evidence  
- Do not use this as proof the product is invalid  

**Product truth captured (design input only):**

```text
Spam filtering and basic awareness training are already expected baseline controls.
MMI must provide something beyond baseline inbox protection.
```

**Gap analysis (R4 vs MMI doctrine):**

```text
Described baseline:
SEG + awareness training + "don't download" + view-in-client.

MMI gap if positioned as filter/training:
Undifferentiated; duplicates crowded market.

MMI alignment:
Action-bearing verification after baseline controls — payment, vendor change, credential, approval.
```

---

### R5 — Email is only part of the business process (extended classification)

| Field | Value |
|-------|--------|
| **ID** | R5 |
| **Source** | Reddit field response |
| **Community** | r/CyberSecurityAdvice |
| **Thread/topic** | SMB email / vendor workflow / product scope challenge (exact thread URL not supplied) |
| **Date captured** | 2026-07-01 |
| **Responder type** | Not specified |
| **Industry** | Not stated |
| **Business size** | Not stated (general business framing) |
| **Country/jurisdiction** | **Unknown — not Canadian-primary evidence** |
| **Labels** | `REAL_ROUTINE`, `HUMAN_GATE`, `BUSINESS_WORKFLOW`, `PAIN_POINT`, `SECURITY_GAP`, `PRODUCT_DIRECTION_INPUT`, `CONTRADICTION` |
| **Confidence** | **MEDIUM-HIGH** — detailed workflow critique; still anecdote, no jurisdiction |
| **Note** | Verbatim matches **R3** — separate card retained for extended classification and product-framing pass |

**Source text (verbatim):**

```text
email is only part of the process.

Like invoices might have a second verification system in place to match up against before anything is paid or a way to confirm with the requesting company.

But what are you really trying to solve? There are hundreds of companies already in this space and some are doing very well. It sounds like you are looking to develop a spam filter, mail tips and a security awareness training system in one without having a decent idea of how a business works. Remember IT enables business and every business is different. You could build a new workflow and try to get the business to change their ways to fit your product or work with the business to work with their workflows.

And to top this off, the people vary too. You could have an old Sally in accounting that clicks everything or sharp eyed SOC analyst putting everything under 5 different microscopes. So if you are building software you need to figure out your target user demographic so you can build your tool to suit them.
```

**Behaviour / process described:**

The responder says email is only one part of the business process. For invoices and payments, some businesses may already have a second verification process, matching system, approval workflow, or direct confirmation path with the requesting company before payment is made.

The responder also challenges whether the product is solving a specific business problem or accidentally combining spam filtering, mail tips, and security awareness training.

**Human / business checks mentioned:**

- Invoice/payment verification may happen outside email  
- Invoices may be matched against another system before payment  
- Requests may be confirmed with the requesting company  
- Controls vary heavily by business  
- Users vary from high-risk clickers to trained analysts  
- Product must fit the business workflow, not assume one universal workflow  

**Security gap:**

A product focused only on email may miss the actual decision point.

The risk may not be "email received."

The risk may be:

`email causes payment, approval, credential action, vendor change, file opening, or process change`

Different businesses may already have partial controls outside the inbox.

**Product challenge:**

The responder challenges whether MMI is really solving a specific business problem or drifting into an overloaded category:

- spam filter  
- mail tips  
- security awareness training  
- workflow tool  

This is a useful contradiction / product-pressure signal.

**Product implication:**

MMI should not be positioned as generic email security.

MMI should be positioned around:

`business-action integrity for email-triggered decisions`

The product should work with existing business workflows before trying to replace them.

**MMI relevance:**

- Email is an input, not authority  
- Business truth often lives outside the email thread  
- Known-good verification matters  
- Target user demographic must be defined clearly  
- Low-friction workflow fit matters more than generic security advice  
- Assume-click / post-acceptance defense remains relevant because user skill varies widely  

**What must NOT be claimed:**

- Do not treat this as a statistic  
- Do not treat it as Canadian-primary evidence  
- Do not claim all SMBs have second verification systems  
- Do not claim all users are careless  
- Do not claim all users are sophisticated  
- Do not use this as proof the product is invalid  
- Do not use this to abandon the product  
- Use it as product-scope pressure  

**Product truth captured (design input only):**

```text
Email is not the whole process. The product must protect the business decision that follows the email, not just classify the email itself.

MMI should work with existing SMB workflows instead of assuming all businesses handle invoices, vendors, and approvals the same way.

MMI should protect action-bearing email: money, credentials, vendor changes, approvals, files, admin access, and sensitive information.
```

---

## Emerging Reddit field pattern

The early Reddit evidence is pushing MMI away from generic inbox protection and toward **business-action integrity**.

**Current observed pattern (n=8 — provisional only):**

1. Some users rely on basic spam filtering and phishing training (R4).  
2. Some users handle email informally through familiarity, gut feel, delete/archive/resolve habits, or inbox hygiene (R1, R2).  
3. Some responders emphasize that invoices/payments may already have verification outside email (R3, R5, R6).  
4. Business workflows vary heavily (R3, R5, R6).  
5. User skill varies heavily (R3, R5, R6) — from "Sally in accounting" (R6) to practitioner stacks (R8).  
6. A product that only says "this email is suspicious" risks becoming generic (R3, R4, R5, R6).  
7. The stronger product lane is protecting the **action after the email** (R3, R5).  
8. Security-advice audiences challenge **builder credibility** before workflow fit (R7).  
9. Practitioner-grade operators already stack platform + DNS + sandbox + personal sanitization — still no payment-branch described (R8).

**Updated product framing (design input only — not authority):**

```text
MMI is not a spam filter.

MMI is not generic phishing training.

MMI is a business-action integrity and evidence system for risky email-triggered decisions.

MMI helps pause, verify, document, and recover when email tries to cause money movement,
vendor change, credential action, file trust, approval, admin change, or sensitive information disclosure.
```

**Current design implication:**

Do not build only for inbox classification.

Build around the workflow moment where email becomes business action:

```text
email arrives → user reads → action requested → business verification needed
→ evidence recorded → action allowed / held / escalated / recovered
```

**Status:** Field evidence only. Not authority. Not a statistic. Not Canadian-primary. Preserve as product-pressure evidence for future MMI review.

**Corroboration (2026-07-02):** R6 — u/MonkeyBrains09 on **r/CyberSecurityAdvice** (2 upvotes on OP-1 thread). Same thesis as R3/R5; strengthens workflow-fit / crowded-market pressure.

**New captures (2026-07-03):** R7 — builder trust / "vibe code" challenge (1 upvote). R8 — u/Fresh_Heron_3707 practitioner stack: Zoho + DNS auth + link sandbox + attachment JSON reformat (1 upvote). Thread URL still not supplied.

---

## Common patterns (n=8 — provisional only)

| Pattern | Count | Notes |
|---------|-------|-------|
| Delete-first spam handling | 1 | R1 |
| Archive as secondary | 1 | R1 |
| Inbox-zero orientation | 1 | R1 |
| Sender/subject skim + gut-feel open | 1 | R2 |
| Familiarity-based trust | 1 | R2 |
| Formal process only after scare | 1 | R2 |
| Domain / hover / attachment check (minority) | 1 | R2 — "only a few" |
| Email is only part of broader business workflow | 3 | R3, R5, R6 |
| Second verification / matching outside inbox (some businesses) | 3 | R3, R5, R6 — not universal |
| User demographic variance (low-risk vs high-risk operators) | 3 | R3, R5, R6 |
| Crowded market pressure — spam filter + mail tips + awareness | 3 | R3, R5, R6 |
| Baseline spam filter + phishing training expected | 1 | R4 |
| "Don't download; view in email" user guidance | 1 | R4 |
| Product must go beyond baseline inbox protection | 2 | R4, R8 |
| Builder credibility / trust challenge on outreach | 1 | R7 |
| Named email platform (Zoho) + DNS auth stack | 1 | R8 |
| Link pre-scan + sandbox open (can fail) | 1 | R8 |
| Attachment reformat/sanitize before view (post sender check) | 1 | R8 |
| Threat model with defined scope and budget | 1 | R8 |
| Explicit human verification for payments | 0 | **Gap** (R1, R2, R8); partial outside-email controls noted (R3, R5, R6) |
| Named security platform | 1 | R8 — Zoho |

*Update this section as more responses are ingested. Do not summarize n=8 as industry norm.*

---

### R6 — r/CyberSecurityAdvice corroboration (workflow-fit / crowded-market critique)

| Field | Value |
|-------|--------|
| **ID** | R6 |
| **Source** | Reddit field response |
| **Community** | **r/CyberSecurityAdvice** |
| **Thread/topic** | Product scope / SMB workflow fit challenge (exact thread URL not supplied) |
| **Date captured** | 2026-07-02 |
| **Social signal** | 2 upvotes (weak — not prevalence) |
| **Responder handle** | u/MonkeyBrains09 |
| **Posted** | ~1d before Matt capture (2026-07-03) |
| **Responder type** | Not specified |
| **Industry** | Not stated |
| **Business size** | Not stated (general business framing) |
| **Country/jurisdiction** | **Unknown — not Canadian-primary evidence** |
| **Labels** | `REAL_ROUTINE`, `HUMAN_GATE`, `BUSINESS_WORKFLOW`, `PAIN_POINT`, `SECURITY_GAP`, `PRODUCT_DIRECTION_INPUT`, `CONTRADICTION`, `CORROBORATION` |
| **Confidence** | **MEDIUM-HIGH** — same detailed critique as R3/R5; community context adds placement signal only |
| **Note** | Verbatim matches **R3/R5** — filed as separate card because community (**r/CyberSecurityAdvice**) and capture date differ; counts as corroboration, not new pattern |

**Source text (verbatim):**

```text
email is only part of the process.

Like invoices might have a second verification system in place to match up against before anything is paid or a way to confirm with the requesting company.

But what are you really trying to solve? There are hundreds of companies already in this space and some are doing very well. It sounds like you are looking to develop a spam filter, mail tips and a security awareness training system in one without having a decent idea of how a business works. Remember IT enables business and every business is different. You could build a new workflow and try to get the business to change their ways to fit your product or work with the business to work with their workflows.

And to top this off, the people vary too. You could have an old Sally in accounting that clicks everything or sharp eyed SOC analyst putting everything under 5 different microscopes. So if you are building software you need to figure out your target user demographic so you can build your tool to suit them.
```

**Why this capture matters (corroboration only):**

- Same critique now appears on a **security-advice** subreddit — audience expects practical business fit, not vendor pitch.  
- Reinforces that **email ≠ payment authority** — AP matching / vendor callback may already exist.  
- Reinforces **crowded lane** — spam filter + tips + SAT bundled reads as naive.  
- Reinforces **IT enables business** — workflow adaptation beats forcing greenfield process.  
- Reinforces **user demographic fork** — "Sally in accounting" vs SOC analyst = one product cannot serve both without explicit target.  

**MMI wedge pressure (design input — not build auth):**

```text
Least expected ≠ another inbox product.
Special = integrity at the business-action moment AFTER email,
fitted to whatever verification the business already has (AP match, callback, approval),
for ONE chosen operator demographic — not universal SMB.
```

**What must NOT be claimed:**

- Do not treat 1 upvote as validation of MMI or rejection of competitors  
- Do not treat corroboration as n=3 independent studies  
- Do not claim all businesses have second verification (responder says "might")  
- Do not use this to justify building spam filter + SAT + mail tips  

---

### R7 — Builder credibility / "vibe code" trust challenge

| Field | Value |
|-------|--------|
| **ID** | R7 |
| **Source** | Reddit field response |
| **Community** | **r/CyberSecurityAdvice** |
| **Thread/topic** | OP-1 Matt outreach — builder trust / product legitimacy challenge |
| **Date captured** | 2026-07-03 |
| **Social signal** | 1 upvote (weak — not prevalence) |
| **Responder type** | Not specified |
| **Industry** | Not stated |
| **Business size** | Not stated |
| **Country/jurisdiction** | **Unknown — not Canadian-primary evidence** |
| **Labels** | `PRODUCT_DIRECTION_INPUT`, `CONTRADICTION`, `PAIN_POINT` |
| **Confidence** | **MEDIUM** — sharp positioning critique; no operational email routine described |

**Source text (verbatim):**

```text
Brand new and self taught wants to build software for SMBs? Isn't that a bad combination? Are you going to vibe code it? Why would anybody trust it and place their business at its mercy?
```

**Behaviour / process described:**

No SMB email routine described. Responder challenges **builder credibility** and **trust to run security software for a business** — frames "brand new + self taught" as risky for SMB-facing product.

**Human / business checks mentioned:**

None — this is meta-product trust, not inbox handling.

**Security gap:**

N/A for operator behaviour. **Product gap:** outreach that surfaces builder inexperience invites trust objections before workflow value is discussed.

**Product challenge:**

- "Vibe code" framing — product must be **evidence-backed, falsifiable, auditable** (aligns with MMI doctrine)  
- "Place their business at its mercy" — autonomy requires **budget ceiling + dead-man switch + human gate** (AGI pathway)  
- Trust is earned by **provable containment**, not marketing claims  

**MMI relevance:**

- Reinforces MMI moat: **numbers, evidence bundles, proof gates** — not another black-box security app  
- Outreach should lead with **problem wedge + falsifiable test**, not "I'm building cybersecurity software"  
- Does **not** invalidate product — trust objection is addressable with architecture transparency  

**What must NOT be claimed:**

- Do not treat 1 upvote as market rejection  
- Do not treat as proof SMBs won't adopt new tools  
- Do not cite as Canadian operator evidence  

**Product truth captured (design input only):**

```text
Security-advice audiences will challenge builder credibility before workflow fit.
MMI differentiation must be provable containment + business-action integrity — not "trust me" software.
```

---

### R8 — Technical SMB stack (Zoho + DNS + link sandbox + attachment JSON reformat)

| Field | Value |
|-------|--------|
| **ID** | R8 |
| **Source** | Reddit field response |
| **Community** | **r/CyberSecurityAdvice** |
| **Thread/topic** | OP-1 Matt outreach — SMB email security stack / technical controls |
| **Date captured** | 2026-07-03 |
| **Social signal** | 1 upvote (weak — not prevalence) |
| **Responder handle** | u/Fresh_Heron_3707 |
| **Posted** | ~4h before Matt capture (2026-07-03) |
| **Responder type** | Security-aware practitioner (inferred — not stated) |
| **Industry** | Not stated |
| **Business size** | SMB framing (Zoho pricing cited) |
| **Country/jurisdiction** | **Unknown — not Canadian-primary evidence** |
| **Labels** | `REAL_ROUTINE`, `PLATFORM_DEPENDENCE`, `HUMAN_GATE`, `SECURITY_GAP`, `PRODUCT_DIRECTION_INPUT` |
| **Confidence** | **MEDIUM-HIGH** — specific controls named; still single anecdote, no jurisdiction |

**Source text (verbatim):**

```text
Just like anything else you need to threat model with a defined scope and budget. https://www.zoho.com/mail/zohomail-pricing.html Zoho is really the best bang for buck when it comes to SMB email, with 6 usd a month per user you can get s/mime, MDM, and more. Then you have the DNS settings like, Dmarc, TLS reporting, MTA sts, dkim, adkim, spf, aspf, spam filter settings, end point hardening. The best approach to links is pre scanning them and opening them in a sandox environment. (This is not a challenge and can fail.) Dmarc reports will give you real insights to what email you are receiving and what tests it passes.

Personally I reformat all attachment into json before viewing them after the sender is validated. The reformatting isn't always pretty but it works.
```

**Behaviour / process described:**

Responder advocates **threat model with defined scope and budget** before tooling. Recommends Zoho Mail for SMB email ($6/user/month — s/MIME, MDM). Layers **DNS/email auth** (DMARC, TLS reporting, MTA-STS, DKIM, ADKIM, SPF, ASPF) plus spam filter settings and endpoint hardening.

For links: **pre-scan and open in sandbox** — explicitly notes sandbox **can fail**.

For attachments: **reformat to JSON before viewing** — only **after sender is validated**. Acknowledges reformatting is not always pretty but works.

Uses **DMARC reports** for visibility into received mail and auth test results.

**Controls / tools mentioned:**

- Zoho Mail (platform)  
- s/MIME, MDM  
- DMARC, TLS reporting, MTA-STS, DKIM, ADKIM, SPF, ASPF  
- Spam filter settings, endpoint hardening  
- Link pre-scan + sandbox open  
- Attachment → JSON reformat (post sender validation)  
- DMARC report analysis  

**Human checks mentioned:**

- Sender validation **before** attachment handling  
- Threat model scoping (process discipline)  

**Security gap:**

- Link sandbox **can fail** (responder admits)  
- Attachment JSON reformat is personal workaround — not a standard SMB routine  
- Stack is **platform + DNS + endpoint** heavy — high friction for non-practitioner SMB operators (contrast R2)  
- No payment/wire/vendor-change verification branch described  

**Product implication:**

- Baseline for security-aware SMB/practitioner is **already stacked** — MMI must add value **after** platform controls, at **business-action** moments  
- **Sender validated → then attachment** mirrors human-gate ordering — aligns with OPSEC-4/5  
- **Threat model + budget** language aligns with MMI AGI control envelope / bounded autonomy doctrine  
- Do not compete on "best email provider" or DNS checklist — crowded with Zoho/Microsoft/Google lanes  

**MMI relevance:**

- R8 is the **most technical** response in thread — practitioner-grade, not "Sally in accounting"  
- Confirms **platform layer ≠ business truth** — even with DMARC/sandbox, responder adds personal attachment sanitization  
- **JSON attachment reformat** = deterministic sanitizer / inert-view pattern (see weapon runtime blockers doctrine)  
- Reinforces target demographic fork: R8 operator ≠ R2 informal SMB operator  

**What must NOT be claimed:**

- Do not treat Zoho as "best" for all Canadian SMBs (single opinion, USD pricing)  
- Do not treat sandbox as sufficient (responder says it can fail)  
- Do not treat attachment JSON trick as universal or pretty  
- Do not use as Canadian-primary evidence  

**Product truth captured (design input only):**

```text
Security-aware operators already stack platform + DNS + sandbox + personal attachment sanitization.
MMI must assume strong platform controls exist and still protect business-action decisions email triggers.
Threat-model-with-budget framing matches bounded-autonomy product architecture.
```

**Gap analysis (R8 vs MMI doctrine):**

```text
Described stack:
Platform (Zoho) + DNS auth + SEG + endpoint + link sandbox + attachment JSON reformat after sender check.

Missing for MMI OPSEC-4/5:
No out-of-band payment confirmation; no decision log; no vendor wire-change branch.

MMI alignment:
Post-platform integrity at action moment; deterministic inert-view for harvested content;
budget/scope language in control envelope — not another mail provider pitch.
```

---

## Repeated pain points (provisional)

- Spam volume drives delete-heavy workflow (R1)  
- No described branch for suspicious operational mail (R1)  
- Informal trust / gut-feel before open (R2)  
- Security process often reactive — after a scare, not before (R2)  
- Heavy security workflows unlikely to be adopted (R2 product implication)  
- Email-only product scope may miss real decision points — payment/approval/login (R3)  
- Businesses vary — partial controls may already exist outside inbox (R3)  
- Target user demographic must be explicit — operators range from high-risk to analyst-grade (R3)  
- Crowded market pressure — spam filter + mail tips + awareness ≠ differentiated workflow fit (R3, R5, R6)  
- Baseline SEG + awareness training treated as normal — MMI must differentiate beyond that (R4)  
- "Don't download / view in email" — weak alone; action still happens (R4)  
- Protect action-bearing email: money, credentials, vendor change, approval, files, admin (R5)  
- Builder credibility challenged on outreach — "vibe code" / trust to run SMB security (R7)  
- Practitioner stacks platform + DNS + sandbox but still adds personal attachment sanitization (R8)  
- Link sandbox admitted to fail — platform controls not sufficient alone (R8)  

---

## Product implications (design only — not build auth)

1. MMI human-gate docs should separate **inbox hygiene** from **action-bearing verification** — R1 is hygiene-only.  
2. OPSEC-4/5 prompts may need explicit "payment/wire/login = stop, not resolve/archive" language.  
3. Reddit intake stays **internal field lane** — never headline in intel briefs without primary source.  
4. **R2:** Product must fit **fast, low-friction** email routine — lightweight verification at action point, not "think like security pros."  
5. **R2:** Familiarity-based trust is the default SMB pattern — MMI should guide verification without adding heavy workflow.  
6. **R3:** Protect the **business decision after the email** — not just classify the message.  
7. **R3:** Fit existing SMB workflows (AP matching, vendor confirmation) — do not assume greenfield process change.  
8. **R3/R5:** Define target user demographic clearly; avoid one-size-fits-all for accounting vs analyst operators.  
9. **R4:** Do not position MMI as spam filter or generic awareness training — baseline already expected.  
10. **R4/R5:** Stronger lane = business-action integrity + evidence at the decision moment after email.  
11. **Synthesis:** Build for `email → action → verify → evidence → allow/hold/escalate/recover` — not inbox classification alone.  
12. **OP-1:** Outreach is email-centric; extend questions to post-email business verification (AP, callback, approval) to avoid R3/R6 mismatch.  
13. **R7:** Lead with falsifiable containment / evidence architecture — not "I'm building cybersecurity software."  
14. **R8:** Assume platform + DNS + sandbox may already exist; MMI adds post-platform business-action integrity + deterministic inert-view patterns.  
15. **R8:** "Threat model with scope and budget" aligns with AGI control envelope — product language opportunity, not competitor to Zoho.

---

## What still needs verification

- Whether SMB operators commonly conflate inbox-zero with security (needs more field input or primary research)  
- Any stated use of Microsoft/Google/SEG (not in R1)  
- Canadian operator patterns (no jurisdiction in R1)  
- Suspicious-email branch behaviours from additional Reddit captures  
- Whether SMBs commonly have second verification / AP matching outside email (R3 anecdote only — needs primary research)  
- Target user demographic for MMI v1 (accounting operator vs security-aware admin)  

---

## What must NOT be claimed from Reddit

- Canadian SMB email security rates or prevalence  
- That "most vendors" delete spam and therefore are safe  
- That inbox zero reduces ransomware/phish risk for action-bearing mail  
- Vendor/platform effectiveness percentages  
- OPSEC-4/5/9 completion or habit proof  
- That all SMBs have second verification systems before payment (R3)  
- That all operators are careless or all are sophisticated (R3)  
- That crowded-market Reddit critique invalidates MMI scope (R3, R5 — pressure, not verdict)  
- That spam filtering + training alone is sufficient security (R4)  
- That MMI should compete as another SEG or awareness product (R4)  
- That Zoho or any single vendor is "best" for Canadian SMB email (R8 — single opinion)  
- That link sandboxing is sufficient protection (R8 — responder says it can fail)  
- That Reddit trust critique (R7) invalidates MMI — pressure to prove architecture, not verdict  

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Initial intake — R1 Matt-supplied paste; classified REAL_ROUTINE + PAIN_POINT + SECURITY_GAP |
| 1.1 | 2026-07-01 | R2 Reddit field response — informal SMB trust/gut-feel; MEDIUM confidence; not Canadian-primary |
| 1.2 | 2026-07-01 | R3 Reddit field response — email as partial workflow; workflow-fit product pressure; MEDIUM-HIGH; not Canadian-primary |
| 1.3 | 2026-07-01 | R4 baseline SEG + training; R5 extended workflow/product-scope card; emerging field pattern synthesis; n=5 provisional |
| 1.4 | 2026-07-02 | R6 r/CyberSecurityAdvice corroboration of R3/R5 workflow-fit critique; n=6 provisional; wedge pressure note |
| 1.5 | 2026-07-02 | OP-1 Matt outreach question capture; OP vs R3/R6 framing tension |
| 1.6 | 2026-07-02 | Community confirmed r/CyberSecurityAdvice for OP-1; doc header link |
| 1.7 | 2026-07-03 | OP-1 verbatim corrected; R7 builder-trust challenge; R8 u/Fresh_Heron_3707 practitioner stack; R6 handle/upvotes; n=8 provisional |
