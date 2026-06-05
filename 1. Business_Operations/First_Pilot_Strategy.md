# First Pilot Strategy — Thinking Doc

**Status:** Pre-spec strategy / thinking doc. Non-authority, claim-safe, **no pricing locked**. Authored 2026-06-05 by Cursor on Matt Nichol's instruction ("how do we get the first pilot — what it takes, what we're selling, what makes anyone say yes"). This captures the analysis; it commits nothing. Pilot shape, pricing, and free-vs-paid are operator decisions (flagged §9). It does not override `AGENTS.md`, the seven `VISION.md` non-negotiables, the signed `Real_Customer_Data_Controls_Deep_Dive.md`, or the claim boundary in `Compliance_and_Trend_Watch_Process.md`.

**Brand:** buyer-facing = **Mutant Monkey** (Inbox Shield / Security); NorthStar/SwarmCommand are internal codenames.

**Correction note (2026-06-05):** an earlier draft of this doc treated Reddit as a starting channel to "go mine." That was wrong — the operator has already produced a Reddit discovery corpus AND a warm MSP lead. This doc now leads with what already exists (§0.1) and points the first action at that lead, not at cold Reddit.

---

## §0.1 What you've already produced (don't start from zero)

Logged in `Frontier_Intake_Log.md` and synthesized in `4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Section13_Readiness_Packet_20260603.md`:

- **Reddit discovery corpus (2026-06-01 / 06-03):** independent confirmation that underwriters demand proof controls *operate* (not just exist), that bank-detail/vendor-payment changes are high-risk events, and that renewal-week evidence scramble is real. This shaped pain points P02/P07/P10/P13/P15 and confirmed the evidence-package direction. It also surfaced buyer language (e.g. the "is nmap evidence enough?" confusion).
- **A real MSP door: Todd Chapman / CMIT Solutions** — offered coffee to explore mutual value; skeptical of the outreach wording but did not reject the idea. This is the **first real MSP-owner door** and is the live lead.

**What this did and did not do (our own logged rule):** all of the above is **discovery / confirmation signal**, valuable for shaping the product and finding a door. **None of it counts toward D10**, the cheaper-proof go-bar, which requires **2 of 3 relevant MSP conversations** each with a **named SMB anchor** + a **named upcoming insurance/underwriting conversation**, recorded in `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`. That worksheet is currently **empty (0 of 3)**; D10 is **overridden, not met**. So: direction and door = done; pilot proof = not yet.

---

## §1 What we are honestly selling today

Grounded in `4. Product_Roadmap/Product_Sheets/Fraud_Detection_Product_Sheet.md` and `VISION.md` Stage A. We sell a **decision-support, reporting, and evidence layer** for email fraud — not a blocker.

- It **identifies and reports** suspicious email-fraud patterns: vendor invoice fraud, new/unusual banking instructions, wire-transfer pressure, executive impersonation, lookalike sender domains, suspicious attachments/links (ransomware precursors), and behavioral/tone drift.
- It **does not** block, quarantine, delete, or change mail settings. It sits alongside Microsoft 365 / Google Workspace and changes nothing in the customer's environment — **this is a feature for a pilot**: near-zero risk for them to say yes.
- The deliverables a buyer can hold: a **monthly leadership summary**, an optional **daily digest**, **recommended-action labels** (`safe` / `needs_review` / `block` as advisory only), and the **Cyber Insurance Evidence Package**.
- The moat is the **evidence/audit trail** — provable, plain-English documentation of what was reviewed and found.

**Honest gap:** everything we've built and proven is **synthetic/internal**. No real customer, no real underwriter has touched it yet. The first pilot exists to fix exactly that.

---

## §2 Who pilots (target)

**MSP-first is the stronger play than SMB-direct.** An MSP:
- already feels BEC / vendor-payment pain across multiple clients,
- already produces monthly business reviews (our report drops in),
- already fields cyber-insurance renewal questions from clients (our evidence package helps),
- is one relationship that can become several clients,
- pairs us naturally with services they already sell (M365, backup, awareness training).

SMB-direct is possible (owner/finance lead is the buyer) but is a slower trust cycle with lower email volume per deal. Use SMB-direct only if a specific local SMB has an acute, recent fraud scare.

**Kelowna / BC local angle:** a local MSP or a local SMB you can meet in person shortens the trust cycle dramatically versus a cold internet lead. In-person + "I'm local, I built this" beats a Reddit DM.

---

## §3 The hard dependency: real data → signed controls

A pilot uses **real customer emails = real customer data.** The §11-signed `Real_Customer_Data_Controls_Deep_Dive.md` (D1-D15) already governs this: real data is local-AI-audited on a locked machine, in a separate production store, never to an external model. **None of that substrate is built yet.** So:

- We cannot responsibly wire into a customer's live mailbox for a pilot today.
- We can, however, run the **lowest-integration pilot that still produces real evidence**: a **retrospective fraud review** — the customer hands over a bounded batch of real emails they already received (forwarded suspicious messages, or a small mailbox export), we analyze them **on the operator-controlled machine**, and deliver the report + evidence package.

This retrospective framing is the recommended first pilot because it:
- produces the real-world proof D10 needs,
- fits the locked-machine / operator-controlled posture the signed controls already require,
- requires **no live integration, no mail-settings access, no autonomous action**,
- is bounded and one-shot (easy yes, easy to scope, easy to stop).

It still touches real data, so the **minimum we must have first** is a safe, documented intake + handling path on the locked machine (not the full production store, but a written, followed handling procedure). That is a small, concrete pre-pilot build.

---

## §4 The offer that makes someone say yes

Lower every barrier:
1. **No risk to their environment** — we change nothing, block nothing, need no admin access. We review emails they give us.
2. **A concrete deliverable they keep** — a plain-English fraud-review report + a Cyber Insurance Evidence Package they can show leadership and (carefully worded) their underwriter.
3. **Low/no cost for the first one** — a free or nominal first assessment in exchange for honest feedback and (if they're happy) a reference / testimonial. (Dollar figure is your call — §9.)
4. **Their pain is current** — BEC and vendor-payment fraud are top SMB cyber-loss drivers, and insurers increasingly ask for evidence at renewal. We meet a live need, not a hypothetical.
5. **No rip-and-replace** — we sit beside what they have.

The "yes" sentence we want them thinking: *"Low risk, costs me almost nothing, and I walk away with a report I can actually use."*

---

## §5 Proof we can show with ZERO customer data

You can build credibility before anyone hands over a single real email:
- The **synthetic Cyber Insurance Evidence Package + rendered PDF** (already generated) — a real artifact you can show as "this is what you'd receive," with no customer data in it.
- The **internal eval result** (36/40 passing, 100% fraud precision, 0% legit false-positive on the internal `grok-4` gate) — stated honestly as an *internal* benchmark, not a guarantee.
- The **sample monthly report / daily digest demos** already in the repo.

These let you demo and earn trust first, then ask for the retrospective batch.

---

## §6 Reddit — the honest reality

r/msp and r/sysadmin are **hostile to vendor self-promotion**; a "try my product" post gets removed or downvoted and can burn the account. Use Reddit for what it's actually good at:

- **Market research + language mining (primary use).** Read what MSPs and SMB owners say about BEC, vendor-payment fraud, and cyber-insurance renewal pain. Use their exact words to sharpen our offer and our claim-safe copy. Search terms: "BEC", "vendor fraud", "wire fraud", "cyber insurance renewal", "MFA attestation", "phishing client".
- **Subs to read:** r/msp, r/sysadmin, r/cybersecurity, r/smallbusiness (SMB owners directly), r/Kelowna and BC/Canada business subs for local leads.
- **Credibility before pitch.** Participate genuinely; answer questions; become a known helpful person. Soft "I built a free tool, want honest feedback?" framing is *sometimes* tolerated in smaller subs — check each sub's rules first.
- **Leads come from DMs/relationships, not broadcast posts.** Reddit is better as a research + warm-intro channel than a direct sales channel. Treat a found pilot as a bonus, the language/research as the guaranteed value.

---

## §7 Claim-safe language (do / don't)

From `Compliance_and_Trend_Watch_Process.md` §5 carve-outs and the product sheet's safe-claim boundary. **This applies to every Reddit post, DM, call, and deliverable.**

USE: "identifies and reports suspicious email-fraud patterns" / "helps teams review high-risk payment and impersonation emails" / "evidence-friendly reporting" / "audit-ready evidence package" (scoped).

AVOID (forbidden): "stops/prevents all phishing", "guarantees fraud prevention", "compliant", "certified", "insurer-approved", "insurance policy", "quarantines malicious email", "replaces finance approval controls". Never promise an underwriting outcome or premium reduction.

---

## §8 Concrete next actions (operator)

**Lead with the warm lead, not cold Reddit.**
1. **Follow up Todd Chapman / CMIT Solutions** — take the coffee. Run it on `Cyber_Insurance_Vendor_Payment_Integrity_MSP_Call_Pack.md` + the cheaper-proof runbook questions; bring the synthetic evidence-package PDF as the "this is what you'd receive" demo. Goal: understand his clients' vendor-payment/renewal pain and see if a named SMB + a named renewal conversation surface.
2. **Log the outcome in `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`** (currently 0 of 3) — `partial` unless both named anchors appear voluntarily. This is how D10 actually advances.
3. Decide the first-pilot shape (§9) — recommended: retrospective fraud review.
4. (Pre-pilot build, small) a written, locked-machine real-email intake + handling procedure before any real batch arrives.
5. Line up 2-3 more MSP touches (Kelowna-local first) so the 2-of-3 D10 bar is reachable.
6. Use Reddit as *ongoing* research/language-mining and warm-intro hunting (§6) — secondary to working the Todd lead, not the starting point.

---

## §9 Open operator decisions (butterfly — Consequence Matrix available)

These are path-setting (revenue, buyer trust, real-data handling, external identity). Flagging as a **butterfly decision**; run the Consequence Matrix (`4. Product_Roadmap/Consequence_Matrix_Process.md`) before locking any of them:

- **Pilot shape:** retrospective batch review (recommended) vs live mailbox integration (blocked on real-data substrate) vs MSP-channel vs direct-SMB.
- **Free vs paid first pilot**, and the price/terms (testimonial/reference exchange?).
- **How many tenants** in the first pilot, and the data-handling minimum required before accepting real emails.

A score/ranking is advisory; you decide.
