# Todd Coffee Meeting — Field Kit

**Format:** in-person coffee, ~Tuesday. Phone-openable. This is the strong version of the anchor card, tuned to the email Matt actually sent (cyber-insurance renewal-evidence wedge) and to an in-person meeting where wasting Todd's time is the only real failure.

**Posture:** not a pitch, not weak. You are a builder who already has a working engine on synthetic cases and the discipline to not touch real client data until it's provably safe. Confidence comes from the artifact + domain command, not from claims.

**The single failure to avoid:** going in vague. Lead with the case, not with adjectives.

---

## The 60-second open (say it plainly, then stop talking)

"I build the evidence layer an MSP needs when an insurer stops accepting checkbox answers. The case I care about: a vendor emails your client that their banking details changed — pay the new account. It passes SPF, DKIM, DMARC. It looks completely legitimate. It's fraud. My system flags that email despite the clean auth, forces an out-of-band verification before anyone pays, and leaves an audit-ready record of what was observed, what was verified, and what was decided. Right now it runs on synthetic cases only — I haven't pointed it at one byte of real client data, and I won't until I can prove that's safe. Today I mostly want to learn whether the renewal-evidence pain I asked you about is real in your shop."

Then ask a question and listen. Silence is your friend.

---

## The one story that wins the meeting (the Harborline case)

This is a real, synthetic case the system already processed. Show it / tell it on the phone.

- A vendor, "Harborline Marine Services," emails the client's AP team: *invoice 8841, we've updated our banking details, please wire to the new account ending 4288 before end of week.*
- **Authentication-Results: SPF pass, DKIM pass, DMARC pass.** By every gateway check, this email is clean.
- It's a payment-redirect fraud pattern — the most expensive thing that hits SMB finance teams.
- What the engine did, end to end:
  1. **Scored it high-risk anyway** — auth-pass does not mean safe; the *behavior* (banking change + urgency + wire) is the signal.
  2. **Forced a two-channel confirmation** — verify the change through a previously-known phone channel before any payment, not by replying to the email.
  3. **Recorded the outcome** — "payment change reviewed before action," confirmed via the known channel.
  4. **Left durable records + a daily digest** — a trail showing what was seen, what was checked, and what was decided.

The point to land: **"This is the gap your gateway doesn't cover. The email was technically perfect. The defense isn't a better spam filter — it's behavioral suspicion plus a forced verification plus a record you can hand an insurer or a client."**

### If Todd pushes (he should — he's technical)

- **"Isn't this what Defender / Mimecast / Proofpoint already do?"**
  "Those work at the gate — spam, malware, known-bad. This case passed the gate. They don't force a payment-change verification or produce a record of the human review. Different layer: I'm the evidence-and-verification layer *after* the gate says 'looks fine.'"
- **"My clients won't buy another security tool."**
  "I'm not asking them to today. The wedge is the renewal-evidence headache you and I both know is growing — the thing already costing you hours. If it doesn't save that time, it's not worth their money and I want to know that."
- **"Why would I trust a one-person operation with client email?"**
  "You shouldn't yet — and I'm not asking you to. It runs on synthetic data only. What I want from you is whether the *shape* of the evidence is right, not access to anything real."
- **"What does the insurer actually accept?"**
  Honest: "I don't know what your underwriters accept — that's one of the things I'm hoping you'll tell me. I'm not promising premium impact or claim approval; I'm building the record, not the insurer's decision."

---

## What you want to walk out with (4 things — this is the scorecard)

1. **Is the wedge real?** Are insurers making his SMB clients *prove* controls now instead of checkbox — and is gathering that log/evidence genuinely painful? (If yes → the whole thesis is validated by a practitioner.)
2. **The evidence anatomy.** What artifacts does an insurer / client actually ask him for? (Defines the record we build.)
3. **The 60-day situation — as intelligence, not a commitment.** Learn the anatomy of one real renewal headache. Do NOT promise to help that client; you can't touch real data yet.
4. **The "what would make you test it" bar.** What has to be true before an MSP tries this with one low-risk client or a synthetic set? (That's your next milestone, defined by a buyer.)

Get those four and the meeting is a win even if he says "not yet."

---

## Hard boundaries (say these as strength, not apology)

- Won't touch real client data until provably safe. (Discipline = credibility to a security person.)
- No claims of compliance, certification, insurer approval, premium reduction, or fraud "prevention."
- Doesn't block, quarantine, or replace Microsoft/Google today. It's decision-support + evidence.
- Don't over-explain the 70-agent roadmap unless he asks. The case is the story; the architecture is backstage.

---

## The close (no sale)

"If this lines up with what you're seeing, the next step isn't me touching a client's data. It's me showing you a synthetic evidence record end-to-end and you telling me what would have to be true for an MSP to test it safely. If it doesn't line up, the most valuable thing you can do is tell me what I should prove first."

---

## Truth ledger (so you never overclaim in the room)

- **Real:** ingest → live grok-4 scoring → high-risk flag on the auth-pass payment-redirect case → two-channel verification request + confirmed outcome → durable on-disk records + daily digest. Seven detector agents built and tested on synthetic cases.
- **Not real yet:** the polished multi-part "insurance evidence package" document; any real customer; any production deployment; any latency/recall claim from one case. Synthetic only.
- **One case is a demonstration, not a recall claim.** If Todd asks "how accurate is it," the honest answer is "I can't make an accuracy claim from synthetic cases yet — that's part of what a careful first test would establish."
