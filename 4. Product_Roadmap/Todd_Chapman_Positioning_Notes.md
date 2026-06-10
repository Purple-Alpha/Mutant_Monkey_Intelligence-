# Todd Chapman Positioning Notes — CMIT Solutions Kelowna
**Status:** Working draft — NOT §11 signed. Advisory lane only. No build authorization.
**Last updated:** June 9, 2026
**Source:** Matt Nichol verbal debrief from Todd Chapman meeting

---

## What Todd Told Us

### 1. Cyber insurance is NOT a must in Canada
- In the US, cyber insurance is increasingly mandatory or lender-required.
- In Canada it is still largely optional / suggestive.
- **Impact on positioning:** Do not lean on "helps with cyber insurance" as the primary hook for Canadian MSP clients. It will not land the same way. It can be a secondary benefit but cannot be the wedge.
- **What this kills:** the v0.1 Product Bible framing that leaned into insurance as a core value driver needs to be softened or repositioned for a Canadian audience.

### 2. We cannot compete behind Microsoft — we must be ahead of them
- Todd's direct feedback: competing on price with Barracuda is a losing game.
- Microsoft Defender is the floor, not the ceiling. Being "as good as Defender" is not a product.
- We need to position as the layer that catches what Microsoft cannot, explains what Microsoft will not, and unblocks what Microsoft has locked.

### 3. The Microsoft Defender outage / false fraud lock — real example
- **What happened:** Microsoft Defender went down a few months ago. A company was trying to close a deal. Microsoft had already flagged the vendor email as fraud. It was not fraud. The company knew it was not fraud.
- **The real problem:** What can a company actually do when Microsoft Defender has declared something fraud and the system is locked or unavailable? There is no appeal surface. There is no evidence chain. There is no explanation. You just get a block with no way out.
- **This is our wedge.** Microsoft blocks without explaining. We explain without blocking. And when you know the email is legitimate, we give you the evidence chain to prove it and the context to act on it.
- **Sales language:** "What do you do when Microsoft says it's fraud and you know it's not? Right now, your answer is nothing. We change that."

---

## Three Real-World False Positive Scenarios (from Todd debrief)

These are the stories that open doors with MSP clients. Use them in conversations, product sheets, and demo scripts.

### Scenario A — Geo-Tracking Lock (Ukraine Office Problem)
- **Situation:** A company legitimately sends email from Ukraine. Their office is in Canada. Microsoft and most security tools see a Ukrainian IP and flag the email as suspicious or fraudulent.
- **The real problem:** The IP or geo-origin is flagged, but the sender is completely legitimate. No tool explains why it was flagged. No tool gives you a way to whitelist with evidence.
- **Our answer:** We surface the geo-velocity signal AND the context — known sender, established thread, matching header pattern. We do not block. We give the operator the facts and let them decide. We document the decision either way.
- **One-liner:** "We see Ukraine. We also see that this sender has emailed you 47 times in the last 6 months. That context matters."

### Scenario B — Newsletter / Image-Heavy Email Flagged as Spam
- **Situation:** A company sends a legitimate newsletter. It has a lot of images — maybe AI-generated images or design-heavy content. The email gets flagged as spam. It is not spam. It is just visually rich.
- **The real problem:** The spam flag is based on surface signals (image ratio, layout density, AI-generated content patterns). The tool cannot distinguish "this looks like spam" from "this IS spam."
- **Our answer:** We surface the reason for the flag — image ratio, AI content pattern, layout density — and distinguish it from actual fraud signals. No payment request. No impersonation. No domain spoofing. This is a delivery problem, not a fraud problem. Different action path.
- **One-liner:** "Your newsletter isn't spam. It just looks like it. We tell you why it was flagged and what to fix — instead of just killing it."

### Scenario C — Defender Down, Deal Locked
- **Situation:** Microsoft Defender flags a legitimate vendor email as fraud and goes offline. The company cannot close the deal because the email is blocked and the tool is unavailable. No audit trail. No appeal. No override.
- **Our answer:** We have already built the evidence chain for that vendor — confirmed sender, payment history, header integrity, two-channel verification. When Defender is wrong or unavailable, we are the second opinion with receipts.
- **One-liner:** "When Microsoft goes down, we keep going. And when Microsoft is wrong, we can prove it."

---

## Core Positioning Statement (updated post-Todd)

> **Microsoft blocks without explaining. We explain without blocking.**
> When a tool flags something as fraud, most platforms give you a verdict with no context.
> We give you the evidence chain — what triggered the flag, what the context says, and what a human should do with that information.
> False positives cost deals. We help you tell the difference.

---

## What Changes in the Product Bible (v0.2 requirements)

1. **Soften the cyber insurance angle for Canada.** Reframe as "supports insurance documentation if you carry it" not "required for insurance." Do not lead with it.
2. **Add the scope boundary statement from the signed Cyber Insurance spec** (verbatim — still outstanding from v0.1 fix list).
3. **Add the false positive problem as the primary wedge.** Three scenarios above go in the Bible as named examples.
4. **Replace "helps with Microsoft" language with "ahead of Microsoft" language.** We are not a complement — we are a layer that catches what they miss and explains what they will not.
5. **Add the Defender outage story** as a named real-world case study (anonymized). This is the conversation opener for MSP sales.

---

## What This Does NOT Change

- Product capabilities, build scope, or agent design — this is positioning only.
- Any signed spec — the Product Bible is a sales/marketing artifact, not a governance document.
- The evidence-first philosophy — it actually reinforces it. The whole sales story is built on the evidence chain.

---

## Decision Cycles Log Entry Required

This debrief should be logged in `decision_cycles_log.md` as a `type: POSITIONING` entry before the next buyer-facing surface is updated.

---

## Next Action

Produce Product Bible v0.2 on Matt's direction, incorporating:
- Softened insurance angle
- Verbatim scope boundary from Cyber Insurance spec
- False positive wedge as primary angle
- Three scenarios above as named examples
- Defender outage story
- "Ahead of Microsoft" positioning throughout
