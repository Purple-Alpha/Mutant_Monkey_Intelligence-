"""NorthStar Inbox Shield — email risk scoring agent.

This module is the first NorthStar Inbox Shield agent slotted on top of the
existing SwarmCommand Agent Loop Runtime. It mirrors the shape of
``core/production/regression_detector.py``:

- a frozen ``EmailRiskScoringConfig`` injects dependencies (the LLM client
  callable, tenant id, agent ids, marker workflow id, soft caps);
- ``run_email_risk_scoring_cycle`` is the cycle entry point; and
- ``EmailRiskScoringResult`` aggregates per-cycle counts plus record ids.

Idempotency follows the existing marker pattern used by
``policy_regression_detector_checked`` / ``regression_alert_consumed``: after
the scoring agent finishes one inbound email (success or failure) it writes
an ``audit_verdict`` with ``workflow_id="email_analysis_complete"`` and
``parent_record_id`` pointing at the source ``EMAIL_INBOUND`` record. Future
cycles skip any inbound email that already carries a marker.

Failures are marked the same way as successes — this matches the regression
detector convention (the checked marker is written regardless of whether an
alert was emitted). This prevents an unparseable LLM response from being
retried forever and lets the dead-letter ``EmailAnalysisFailurePayload`` be
inspected out-of-band. (Documented deviation note: rationale.)

No real LLM calls are made. ``config.llm_client`` is a callable injected at
construction time with signature ``(system_prompt, user_prompt) -> raw_json``.
Tests pass deterministic fakes; production wiring is out of scope here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import UUID, uuid4

from pydantic import ValidationError

from core.blackboard import (
    NORTHSTAR_MAX_ACTION_ITEMS,
    NORTHSTAR_MAX_SUMMARY_CHARS,
    AuditStatus,
    AuditVerdictPayload,
    BlackboardRecord,
    EmailAnalysisFailurePayload,
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.operator_state.security_profile import (
    ForcedEscalationEvidence,
    ProfileResolution,
    SecurityProfile,
    load_tenant_profile_state,
    resolve_profile_for_email,
)
from core.orchestrator import (
    RouteContext,
    RouteResult,
    submit_audit_verdict,
    submit_email_analysis,
    submit_email_analysis_failure,
)
from core.orchestrator.routes import blackboard_path
from core.precursor import build_precursor_overlay
from core.scoring.document_metadata_detector import (
    DocumentMetadataAssessment,
    assess_document_metadata_fingerprint,
    vendor_domain_from_sender,
)
from core.scoring.email_authentication_detector import score_email_authentication
from core.scoring.financial_state_ledger import FinancialStateLedgerAssessment
from core.scoring.ghost_thread_detector import score_ghost_thread
from core.scoring.header_divergence_detector import score_header_divergence

EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID = "email_analysis_complete"

LLMClient = Callable[[str, str], str]
"""Pluggable LLM client signature: ``(system_prompt, user_prompt) -> raw_json_str``."""


NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT = """You are NorthStar Inbox Shield, an AI email analyst specialized in human-layer fraud defense and ransomware precursor defense for business users.

Your specialization is fraud detection. Fraud starts in the inbox. Your job is to stop the attack before it becomes an incident.

Your responsibilities:
- Read inbound emails.
- Extract meaning, tasks, and risks.
- Detect vendor invoice fraud, executive impersonation, wire-transfer pressure, invoice-authenticity anomalies, lookalike sender domains, and header inconsistencies.
- Surface behavioral deviations using a controlled enum.
- Produce a structured JSON object that downstream systems can reliably parse.

Rules you must follow:
- Be concise and factual.
- Never invent details not present in the email.
- If information is missing, return null instead of guessing.
- Keep summaries under 3 sentences.
- Keep action items under 5 items.
- Risk score must be between 0 and 100.
- Impersonation likelihood must be between 0 and 100.
- vendor_fraud_score and wire_transfer_anomaly_score must be between 0 and 100.
- invoice_authenticity_score is INVERTED: 100 means appears authentic, 0 means strong forgery signals. Return null when no invoice attachment is present; do NOT guess.
- behavioral_deviation_flags must only contain values from this exact set: ["new_banking_instructions", "out_of_band_pressure", "unusual_dollar_amount", "lookalike_sender_domain", "reply_to_diverges_from_from", "mismatched_invoice_vendor_name", "first_time_sender_with_financial_ask", "urgency_paired_with_finance", "unusual_unicode_obfuscation"]. Do not invent new flag values.
- Always return valid JSON.
- Do not include commentary outside the JSON.
- Do not include explanations of your reasoning.
- Do not include markdown.
- Only output the JSON object.

Scoring rubric (from Phase 1.1 Fraud Prevention Deep Dive §2):

vendor_fraud_score:
- 0-20: no vendor-fraud signals; email is internal, personal, or clearly non-vendor.
- 21-40: one soft signal (e.g. first-time sender from a new domain claiming to be a vendor).
- 41-60: two soft signals OR one strong signal (e.g. attached invoice from a sender whose domain doesn't match the vendor name).
- 61-80: multiple strong signals (sender-domain anomaly + new banking instructions cue + invoice attached).
- 81-100: strong signals + urgency layering, OR sender-domain anomaly + explicit wire instructions in body.

wire_transfer_anomaly_score:
- 0-20: no wire-transfer language.
- 21-40: wire/ACH/SWIFT language present without specific account or amount.
- 41-60: specific wire amount without explicit anomaly indicators.
- 61-80: specific amount + routing/account in body, OR wire request + time pressure.
- 81-100: amount + routing/account + time pressure, OR wire request paired with executive-impersonation or vendor-fraud cues.

invoice_authenticity_score (inverted; null when no invoice attachment):
- 0-20: banking details embedded in invoice body + sender domain not matching vendor name + invoice date anomaly.
- 21-40: two of the above.
- 41-60: one of the above OR vendor name in extracted text not matching sender domain on a first-time sender.
- 61-80: routine-looking invoice from a sender consistent with the vendor name; no anomalies.
- 81-100: invoice consistent with known patterns + sender domain matches vendor + no banking details in body + standard invoice date.

behavioral_deviation_flags:
- Use "unusual_unicode_obfuscation" when non-ASCII Unicode appears in places where it has no legitimate business purpose: zero-width characters in attachment filenames or body text, lookalike Unicode punctuation inside identifiers, or invisible joiners breaking up finance keywords such as "wire", "invoice", "ACH", "ABA", "account", or "payment".
- Boundary: "lookalike_sender_domain" remains the primary flag for sender-domain impersonation. Add "unusual_unicode_obfuscation" when the message also uses unusual Unicode in filenames, body text, attachment text, or other non-domain payload surfaces.

Month 2 recall patch — targeted subcategory rubric refinements (apply in addition to the rubric above, not instead of it):

Banking-instruction strength (vendor_fraud_score floor):
- Any explicit change to where money goes counts as a strong vendor-fraud signal: phrases such as "new ACH details", "new wire instructions", "updated remit-to address", "please use the new banking details", "payment details have changed", "remit to the address/account below", or banking destination details that appear only inside an attached PDF or payment-request attachment.
- When such language is present together with any sender anomaly (lookalike sender domain, first-time sender from a new domain, mismatched vendor name, Unicode obfuscation, header inconsistency), vendor_fraud_score must reach at least 60 and recommended_action must be "needs_review" or "block".
- When such language is present in isolation (no other sender anomaly), vendor_fraud_score must still reach at least 45.
- Emit "new_banking_instructions" whenever this pattern is detected.

Sender-domain obfuscation (lookalike_sender_domain emission):
- Emit "lookalike_sender_domain" for any of: (a) Unicode lookalikes or zero-width characters embedded inside the sender domain; (b) punycode prefixes such as "xn--"; (c) homoglyph substitutions ("rn" for "m", "0" for "o", "1" for "l", Cyrillic look-alikes); (d) a sender domain that is a near-variant of a vendor or brand name appearing elsewhere in the email (extra hyphen, swapped TLD, dropped or doubled character, swapped word order, "-billing" / "-payments" / "-invoices" suffix bolted onto a recognizable vendor stem).
- When Unicode obfuscation is also present in filenames, headers, body text, or attachment text, additionally emit "unusual_unicode_obfuscation". The two flags are not mutually exclusive.
- Do not emit "lookalike_sender_domain" purely because the sender is unknown. There must be an actual domain anomaly tied to a vendor or brand cue present in the email.

Invoice authenticity & PDF-only banking changes (invoice_authenticity_score floor + recommended_action lean):
- invoice_authenticity_score must fall in the 0-40 band whenever any of the following holds: (a) the extracted invoice text names a vendor different from the sender's domain; (b) banking destination details (account, ABA, IBAN, "remit to") appear only inside the attached PDF or payment-request attachment while the email body is terse ("please process the attached", "see attached for details", "use the instructions in the attachment", "following up as discussed"); (c) the invoice's stated date is inconsistent with the email's received date (e.g. future-dated invoice with payment due today).
- When (a) or (b) holds, recommended_action must be "needs_review" or "block"; prefer "block" when urgency, banking change, executive-impersonation cues, or wire-pressure cues are also present. "needs_review" is acceptable only when the case is intentionally ambiguous (no urgency, no banking change, plausible terms).
- Emit "mismatched_invoice_vendor_name" whenever (a) holds.

Phase 1.5 vendor-invoice recall floor (preserve precision, but do not under-score these fraud shapes):
- Treat these as vendor-invoice fraud patterns even when the sender domain looks plausible: explicit new ACH / new banking details with urgency; first invoice after onboarding with remittance instructions only in the PDF; updated remit-to address with "old instructions are no longer valid"; fake thread continuity ("Re:", "following up as discussed below", or "as discussed" with no quoted history); and high-value emergency invoice approval before EOD tied to shipment / operations pressure.
- If the message says "first invoice after onboarding" plus "use the remittance instructions on the attached PDF", emit "first_time_sender_with_financial_ask", keep recommended_action at "needs_review" or "block", and score at least risk_score=60, vendor_fraud_score=55, wire_transfer_anomaly_score=35, invoice_authenticity_score no higher than 55.
- If the message is a high-value emergency invoice asking approval before end of day so shipment is not delayed, emit both "unusual_dollar_amount" and "urgency_paired_with_finance", keep recommended_action at "needs_review" or "block", and score at least risk_score=75, vendor_fraud_score=70, wire_transfer_anomaly_score=45, invoice_authenticity_score no higher than 50.
- If a fake thread-continuity invoice uses "Re:" / "following up as discussed below" with no quoted prior context, keep it in the vendor-invoice fraud lane: risk_score at least 65, vendor_fraud_score at least 60, invoice_authenticity_score no higher than 55, recommended_action "needs_review" or "block".

False-positive protection (do not loosen — these guardrails preserve the 0% legit-FPR target):
- Routine vendor invoices from a sender whose domain matches the vendor identity, with no banking change and no urgency, must remain "safe".
- Do not emit "new_banking_instructions" unless the email or its attachment actually changes a banking destination, account, ABA, IBAN, or remit-to address. A sentence such as "banking details unchanged from last invoice", "standard payment terms apply", or "remit through the existing portal" is the opposite of a banking change and must keep recommended_action at "safe" when no other fraud cue is present.
- Do not emit "lookalike_sender_domain" unless the sender domain is itself anomalous per the four conditions above. A first-time or unknown sender alone is not enough.
- Do not push vendor_fraud_score above 40 on emails with no payment ask, no banking detail, and no invoice attachment.
- A polite reminder, a thank-you note, an internal scheduling message, a calendar invite, a routine HR notice, or a newsletter must keep recommended_action at "safe".

You must return JSON in exactly the following structure:

{
  "summary": "string",
  "action_items": [
    {
      "task": "string",
      "owner": "string | null",
      "due_date": "YYYY-MM-DD | null"
    }
  ],
  "risk_analysis": {
    "risk_score": number,
    "risk_factors": ["string"],
    "phishing_signals": ["string"],
    "urgency_signals": ["string"],
    "financial_risk": "low | medium | high",
    "vendor_fraud_score": number,
    "wire_transfer_anomaly_score": number,
    "invoice_authenticity_score": number | null,
    "behavioral_deviation_flags": ["string from the controlled enum above"]
  },
  "impersonation_analysis": {
    "impersonation_likelihood": number,
    "suspicious_elements": ["string"],
    "sender_legitimacy_notes": "string"
  },
  "recommended_action": "safe | needs_review | block"
}

Worked examples (from Phase 1.1 Fraud Prevention Deep Dive §3). These are the patterns to learn from; do not copy their exact text into new outputs.

Example 1 — High-confidence vendor invoice fraud.
Email: vendor "Acme Manufacturing" from billing@acme-manufacturing.co requests urgent payment for invoice 4471, $48,920, with "new ACH details" embedded in body, "missed last cycle, push through today" pressure, invoice PDF attached (attachment_class="invoice").
Expected risk_analysis: risk_score=88, financial_risk="high", vendor_fraud_score=88, wire_transfer_anomaly_score=72, invoice_authenticity_score=25, behavioral_deviation_flags=["new_banking_instructions", "urgency_paired_with_finance", "lookalike_sender_domain"]. recommended_action="block".

Example 2 — Executive impersonation wire pressure.
Email: From "Sarah Chen" <sarahchen.cfo@gmail.com> ("CFO" display name + freemail), wire $42,000 by 4pm to ABA 121000358 / account 9871234509, "don't call — just confirm by reply when sent", no attachment.
Expected risk_analysis: risk_score=94, financial_risk="high", vendor_fraud_score=35, wire_transfer_anomaly_score=95, invoice_authenticity_score=null (no invoice), behavioral_deviation_flags=["out_of_band_pressure", "urgency_paired_with_finance", "first_time_sender_with_financial_ask"]. impersonation_likelihood=90. recommended_action="block".

Example 3 — Legitimate vendor invoice (negative case).
Email: From ap@acmemanufacturing.com (matching corporate domain), invoice 4471 $48,920, "standard net-30 terms, banking details unchanged from last invoice", invoice PDF attached.
Expected risk_analysis: risk_score=8, financial_risk="low", vendor_fraud_score=5, wire_transfer_anomaly_score=3, invoice_authenticity_score=85, behavioral_deviation_flags=[]. recommended_action="safe".

Example 4 — Ambiguous needs_review (subtle red flags only).
Email: From bob@vendor-co.com, "Please find attached invoice for the April work, $12,400. We've updated our wire details — new ABA below. Standard payment terms apply." No urgency. Invoice attached.
Expected risk_analysis: risk_score=55, financial_risk="medium", vendor_fraud_score=55, wire_transfer_anomaly_score=50, invoice_authenticity_score=45, behavioral_deviation_flags=["new_banking_instructions"]. recommended_action="needs_review".

Example 5 — Thread-hijack vendor invoice (matching sender domain, no banking change, fake thread context).
Email: From billing@vendor-co.example (sender domain matches the vendor name "Vendor Co" in the attached PDF — no domain anomaly), subject "Re: May service invoice", body "Following up as discussed below - please process the attached invoice today. Let me know once it is released." Headers contain In-Reply-To and References pointing at <claimed-thread-5512@example.invalid> but the email body shows no actual quoted thread content. Invoice PDF says "Vendor Co service invoice. Total due $13,770. Payment requested upon receipt." No banking-destination details inside the PDF either.
What to learn from this pattern: the surface looks like a routine matching-domain invoice with no banking change — the FPR-protection guardrail would normally route this to "safe". But the combination of (a) a "Re:" subject with no actual quoted thread content in the body, (b) In-Reply-To / References headers pointing at thread IDs that are not present in the body, and (c) phrasing such as "as discussed below" / "following up as discussed" / "as we discussed" with no real prior history is a **thread-hijack fraud pattern**. Treat thread-hijack as a strong vendor-fraud signal even when the domain matches. Set invoice_authenticity_score into the 30–45 band because the attachment is being used to launder an unverified payment request through fabricated continuity. Do not emit "lookalike_sender_domain" (the domain genuinely matches) and do not emit "new_banking_instructions" (there is no banking change). Emit no behavioral_deviation_flags unless the email also exhibits urgency, banking change, or other named patterns.
Expected risk_analysis: risk_score=70, financial_risk="high", vendor_fraud_score=68, wire_transfer_anomaly_score=10, invoice_authenticity_score=35, behavioral_deviation_flags=[]. recommended_action="needs_review".

Example 6 — Future-dated invoice (date-anomaly authenticity case, sender domain matches).
Email: From ap@northcoast-parts.example (sender domain compresses "North Coast Parts" — natural domain hyphenation, NOT a lookalike), subject "Invoice 9090 due today", body "Please pay the attached invoice today." Invoice PDF extracted text: "North Coast Parts invoice 9090. Invoice date 2026-07-30. Payment due 2026-06-15. Total due $14,880." The email was received on 2026-06-15.
What to learn from this pattern: the **invoice's stated date (2026-07-30) is weeks AFTER the email's received date (2026-06-15)** while the payment-due date is "today". This is a date-anomaly authenticity case. Treat it as an invoice-authenticity failure (`invoice_authenticity_score` in 30–45) and as a vendor-fraud signal of moderate strength (`vendor_fraud_score` ≈ 45–55) because the case is primarily about authenticity, not vendor identity. The terse "Please pay the attached invoice today" combined with the future-dated invoice triggers "urgency_paired_with_finance". Do NOT emit "lookalike_sender_domain" — natural domain hyphenation that compresses a multi-word vendor name (e.g. "North Coast Parts" → "northcoast-parts") is not a near-variant attack. Do NOT emit "new_banking_instructions" — no banking change in the body or attachment.
Expected risk_analysis: risk_score=62, financial_risk="medium", vendor_fraud_score=50, wire_transfer_anomaly_score=10, invoice_authenticity_score=35, behavioral_deviation_flags=["urgency_paired_with_finance"]. recommended_action="needs_review".

Example 7 — Unicode-hyphen lookalike sender domain (sender domain non-ASCII attack).
Email: From billing@coastal‑marine.ca (note: the hyphen in the sender domain is U+2011 "non-breaking hyphen", NOT a normal ASCII hyphen U+002D), to ap@acme‑manufacturing.ca (recipient also uses U+2011), subject "Invoice attached", body empty, with PDF attachment "invoice\u200b_May.pdf" (zero-width space in filename).
What to learn from this pattern: any non-ASCII character in the **sender domain** — including Unicode hyphen variants (U+2010, U+2011, U+2212), homoglyphs (Cyrillic "а" for Latin "a", etc.), or punycode (xn--…) — is a **lookalike sender attack** and must emit "lookalike_sender_domain". The fact that the recipient domain ALSO contains a non-ASCII character does NOT make the sender domain legitimate; the two are evaluated independently. An empty-body invoice from a Unicode-anomalous sender domain is a high-risk vendor-fraud pattern, not a benign delivery. Also emit "unusual_unicode_obfuscation" for the zero-width space in the attachment filename. Treat as vendor fraud of moderate-to-high strength.
Expected risk_analysis: risk_score=68, financial_risk="medium", vendor_fraud_score=58, wire_transfer_anomaly_score=10, invoice_authenticity_score=40, behavioral_deviation_flags=["lookalike_sender_domain", "unusual_unicode_obfuscation"]. recommended_action="needs_review" (or "block" if domain is a near-variant of a known vendor).
"""


@dataclass(frozen=True)
class EmailRiskScoringConfig:
    """Configuration for one Inbox Shield scoring cycle.

    Matches the ``RegressionDetectorConfig`` shape: all fields have defaults
    except the LLM client, which is a required injected dependency. Multi-tenant
    isolation is enforced at the loop boundary by forcing
    ``production_tenant_id`` to the cycle tenant (see
    ``ProductionLoopConfig.email_risk_scoring_config`` wiring).

    ``enable_ransomware_precursor_overlay`` controls the Phase 1.2 deterministic
    overlay added in Month 3. Default ON. When enabled (production path), the
    agent overlays a ``EmailAnalysisRansomwarePrecursorAnalysis`` block onto
    the LLM-validated payload and lifts ``risk_score`` to the deterministic
    precursor floor when the LLM under-scored an obvious ransomware-precursor
    email. Existing Month 1 / Month 2 tests that assert exact LLM-side
    ``risk_score`` values can opt out by passing ``False`` so those fixtures
    keep validating the bare LLM output.
    """

    llm_client: LLMClient
    production_tenant_id: str = "tenant_demo"
    scoring_agent_id: str = "email_risk_scoring_001"
    marker_agent_id: str = "audit_001"
    marker_workflow_id: str = EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID
    max_summary_chars: int = NORTHSTAR_MAX_SUMMARY_CHARS
    max_action_items: int = NORTHSTAR_MAX_ACTION_ITEMS
    enable_ransomware_precursor_overlay: bool = True
    # ---------------- Phase 1.4 (Month 5) lift parameters ---------------
    # All three lifts are integer 0–25 additive amounts per the §3
    # parameter contract. Defaults are 0 so the Month 1 / Month 2 /
    # Month 3 fixtures (and the Month 2 grok-4 PASS gate) keep producing
    # byte-identical scoring output. The production loop reads the live
    # ``ProductionPolicyState.parameters`` and threads the three values
    # into a fresh config per cycle; sandbox in-memory callers
    # (``score_one_email_payload``) keep the defaults so Red battery
    # evaluations stay unbiased.
    fraud_risk_floor_lift: int = 0
    attachment_risk_floor_lift: int = 0
    url_obfuscation_floor_lift: int = 0
    default_profile_when_unset: SecurityProfile = "medium"


@dataclass(frozen=True)
class EmailRiskScoringSuccess:
    source_email_record_id: UUID
    analysis_record_id: UUID
    marker_record_id: UUID


@dataclass(frozen=True)
class EmailRiskScoringFailure:
    source_email_record_id: UUID
    failure_record_id: UUID
    marker_record_id: UUID
    failure_reason: str


@dataclass(frozen=True)
class EmailRiskScoringResult:
    analyzed: int = 0
    failed: int = 0
    skipped: int = 0
    successes: list[EmailRiskScoringSuccess] = field(default_factory=list)
    failures: list[EmailRiskScoringFailure] = field(default_factory=list)
    skipped_source_ids: list[UUID] = field(default_factory=list)


def run_email_risk_scoring_cycle(
    context: RouteContext,
    *,
    config: EmailRiskScoringConfig,
) -> EmailRiskScoringResult:
    """Score every inbound email in the tenant that does not yet have a marker.

    Idempotency: marker-based, keyed on source email record id. Each inbound
    email is processed at most once; both successes and failures write a
    completion marker so failed parses never retry indefinitely.
    """

    kill_switch_state = is_kill_switch_engaged(
        context.blackboard_root, scope="PRODUCTION"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    production_path = blackboard_path(
        context.blackboard_root, Environment.PRODUCTION, config.production_tenant_id
    )
    records = read_records(production_path)
    marker_targets = _completed_source_ids(records, config)

    successes: list[EmailRiskScoringSuccess] = []
    failures: list[EmailRiskScoringFailure] = []
    skipped: list[UUID] = []

    for inbound in _inbound_records_sorted(records):
        if inbound.record_id in marker_targets:
            skipped.append(inbound.record_id)
            continue

        try:
            inbound_payload = EmailInboundPayload.model_validate(inbound.payload)
        except ValidationError as exc:
            failure_record, marker = _record_failure(
                context,
                config=config,
                inbound=inbound,
                raw_output="",
                failure_reason=f"invalid_inbound_payload:{exc.error_count()}_errors",
            )
            failures.append(
                EmailRiskScoringFailure(
                    source_email_record_id=inbound.record_id,
                    failure_record_id=failure_record.record.record_id,
                    marker_record_id=marker.record.record_id,
                    failure_reason="invalid_inbound_payload",
                )
            )
            continue

        user_prompt = _build_user_prompt(inbound.record_id, inbound_payload)
        raw_output: str
        try:
            raw_output = config.llm_client(
                NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT, user_prompt
            )
        except Exception as exc:  # pragma: no cover - explicit guard rail
            failure_record, marker = _record_failure(
                context,
                config=config,
                inbound=inbound,
                raw_output="",
                failure_reason=f"llm_client_raised:{type(exc).__name__}",
            )
            failures.append(
                EmailRiskScoringFailure(
                    source_email_record_id=inbound.record_id,
                    failure_record_id=failure_record.record.record_id,
                    marker_record_id=marker.record.record_id,
                    failure_reason="llm_client_raised",
                )
            )
            continue

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            failure_record, marker = _record_failure(
                context,
                config=config,
                inbound=inbound,
                raw_output=raw_output,
                failure_reason="invalid_json",
            )
            failures.append(
                EmailRiskScoringFailure(
                    source_email_record_id=inbound.record_id,
                    failure_record_id=failure_record.record.record_id,
                    marker_record_id=marker.record.record_id,
                    failure_reason="invalid_json",
                )
            )
            continue

        analysis_payload = _try_build_analysis_payload(
            parsed=parsed,
            source_email_record_id=inbound.record_id,
            config=config,
        )
        if isinstance(analysis_payload, _SchemaValidationError):
            failure_record, marker = _record_failure(
                context,
                config=config,
                inbound=inbound,
                raw_output=raw_output,
                failure_reason=analysis_payload.reason,
            )
            failures.append(
                EmailRiskScoringFailure(
                    source_email_record_id=inbound.record_id,
                    failure_record_id=failure_record.record.record_id,
                    marker_record_id=marker.record.record_id,
                    failure_reason=analysis_payload.reason,
                )
            )
            continue

        if config.enable_ransomware_precursor_overlay:
            profile_resolution = _resolve_profile_for_inbound(
                context.blackboard_root,
                config=config,
                inbound_payload=inbound_payload,
                analysis_payload=analysis_payload,
            )
            document_metadata_assessment: DocumentMetadataAssessment | None = None
            try:
                document_metadata_assessment = assess_document_metadata_fingerprint(
                    tenant_id=config.production_tenant_id,
                    vendor_domain=vendor_domain_from_sender(inbound_payload.sender),
                    email=inbound_payload,
                    now=inbound_payload.received_at,
                )
            except GovernanceError:
                document_metadata_assessment = None
            analysis_payload = _overlay_ransomware_precursor(
                analysis_payload,
                inbound_payload,
                profile_resolution=profile_resolution,
                document_metadata_assessment=document_metadata_assessment,
                fraud_risk_floor_lift=config.fraud_risk_floor_lift,
                attachment_risk_floor_lift=config.attachment_risk_floor_lift,
                url_obfuscation_floor_lift=config.url_obfuscation_floor_lift,
            )

        analysis_record = submit_email_analysis(
            context,
            tenant_id=config.production_tenant_id,
            environment=Environment.PRODUCTION,
            source_agent=config.scoring_agent_id,
            parent_record_id=inbound.record_id,
            payload=analysis_payload,
        )
        marker = _write_marker(
            context,
            config=config,
            inbound=inbound,
            findings=[
                f"analysis_record_id={analysis_record.record.record_id}",
                f"recommended_action={analysis_payload.recommended_action}",
                f"risk_score={analysis_payload.risk_analysis.risk_score}",
            ],
            requires_human_review=analysis_payload.recommended_action == "block",
        )
        successes.append(
            EmailRiskScoringSuccess(
                source_email_record_id=inbound.record_id,
                analysis_record_id=analysis_record.record.record_id,
                marker_record_id=marker.record.record_id,
            )
        )

    return EmailRiskScoringResult(
        analyzed=len(successes),
        failed=len(failures),
        skipped=len(skipped),
        successes=successes,
        failures=failures,
        skipped_source_ids=skipped,
    )


def _inbound_records_sorted(records: list[BlackboardRecord]) -> list[BlackboardRecord]:
    inbound = [r for r in records if r.record_type == RecordType.EMAIL_INBOUND]
    inbound.sort(key=lambda record: record.created_at)
    return inbound


def _completed_source_ids(
    records: list[BlackboardRecord], config: EmailRiskScoringConfig
) -> set[UUID]:
    completed: set[UUID] = set()
    for record in records:
        if record.record_type != RecordType.AUDIT_VERDICT:
            continue
        if record.workflow_id != config.marker_workflow_id:
            continue
        if record.parent_record_id is None:
            continue
        completed.add(record.parent_record_id)
    return completed


def _build_user_prompt(source_record_id: UUID, payload: EmailInboundPayload) -> str:
    """Build the user prompt sent to the LLM client.

    Deterministic, structured JSON so a fake test client can match exactly on
    a known shape, and so real LLM calls have stable inputs across runs.
    """

    body_for_prompt = payload.body_plain
    body_html_present = payload.body_html is not None

    user_block = {
        "source_email_record_id": str(source_record_id),
        "sender": payload.sender,
        "recipient": payload.recipient,
        "subject": payload.subject,
        "received_at": payload.received_at.isoformat(),
        "headers": payload.headers,
        "attachments": [
            attachment.model_dump(mode="json") for attachment in payload.attachments
        ],
        "body_plain": body_for_prompt,
        "body_html_present": body_html_present,
    }
    return json.dumps(user_block, sort_keys=True, ensure_ascii=False)


def _resolve_profile_for_inbound(
    blackboard_root,
    *,
    config: EmailRiskScoringConfig,
    inbound_payload: EmailInboundPayload,
    analysis_payload: EmailAnalysisPayload,
) -> ProfileResolution:
    """Resolve Tiered Detection Intensity for one inbound email.

    The production kill switch has already been checked by the caller. This
    helper is side-effect-free: it reads tenant profile state, evaluates
    always-on detector evidence, and returns the pure profile resolution.
    """

    try:
        tenant_state = load_tenant_profile_state(
            blackboard_root, config.production_tenant_id
        )
    except FileNotFoundError:  # pragma: no cover - defensive; loader defaults absent
        tenant_state = None

    tenant_default = (
        tenant_state.profile if tenant_state is not None else config.default_profile_when_unset
    )
    addon_detectors = tenant_state.addon_detectors if tenant_state is not None else ()
    header_divergence = score_header_divergence(
        sender=inbound_payload.sender,
        headers=inbound_payload.headers,
    )
    ghost_thread = score_ghost_thread(
        subject=inbound_payload.subject,
        headers=inbound_payload.headers,
    )
    return resolve_profile_for_email(
        tenant_default=tenant_default,
        addon_detectors=addon_detectors,
        evidence=ForcedEscalationEvidence(
            llm_risk_score=analysis_payload.risk_analysis.risk_score,
            header_divergence_score=header_divergence.score,
            ghost_thread_score=ghost_thread.score,
            manual_escalation_requested=False,
        ),
    )


@dataclass(frozen=True)
class _SchemaValidationError:
    reason: str


def _try_build_analysis_payload(
    *,
    parsed: Any,
    source_email_record_id: UUID,
    config: EmailRiskScoringConfig,
) -> EmailAnalysisPayload | _SchemaValidationError:
    if not isinstance(parsed, dict):
        return _SchemaValidationError(reason="schema_root_not_object")

    if "action_items" in parsed and isinstance(parsed["action_items"], list):
        if len(parsed["action_items"]) > config.max_action_items:
            return _SchemaValidationError(reason="too_many_action_items")

    construction_input = dict(parsed)
    construction_input["source_email_record_id"] = str(source_email_record_id)
    construction_input.setdefault("produced_at", datetime.now(timezone.utc).isoformat())

    try:
        analysis_payload = EmailAnalysisPayload.model_validate(construction_input)
    except ValidationError as exc:
        reason = "schema_mismatch"
        for error in exc.errors():
            err_type = error.get("type", "")
            if err_type.startswith("greater_than") or err_type.startswith("less_than"):
                reason = "out_of_range"
                break
            if err_type == "literal_error":
                reason = "invalid_enum"
                break
            if err_type == "value_error" and "summary exceeds soft cap" in str(
                error.get("msg", "")
            ):
                reason = "summary_too_long"
                break
            if err_type == "too_long":
                reason = "too_many_action_items"
                break
        return _SchemaValidationError(reason=reason)

    return analysis_payload


def _overlay_ransomware_precursor(
    analysis_payload: EmailAnalysisPayload,
    inbound_payload: EmailInboundPayload,
    *,
    profile_resolution: ProfileResolution | None = None,
    financial_state_ledger_assessment: FinancialStateLedgerAssessment | None = None,
    document_metadata_assessment: DocumentMetadataAssessment | None = None,
    fraud_risk_floor_lift: int = 0,
    attachment_risk_floor_lift: int = 0,
    url_obfuscation_floor_lift: int = 0,
) -> EmailAnalysisPayload:
    """Apply the post-LLM deterministic overlay path.

    Despite the legacy name, this function now applies the union of all
    deterministic post-LLM signals that contribute to ``recommended_risk_floor``:

    1. Phase 1.2 ransomware-precursor sub-scores (attachment, URL, credential,
       MFA) merged into the precursor block on the payload.
    2. From / Reply-To / Return-Path header divergence detection (sender
       identity does not line up — a strong BEC indicator).
    3. Ghost-thread detection (``Re:`` / ``Fwd:`` subject with no
       ``In-Reply-To`` / ``References`` headers — fake thread continuity).
    4. Email authentication header ingestion (SPF/DKIM/DMARC) when the
       effective security profile is MEDIUM or HIGH.
    5. Financial State Ledger / Delta Tripwire risk floor when a caller has
       already performed the required stateful vendor-baseline assessment.
    6. Document Metadata Fingerprinting when the effective security profile
       is MEDIUM or HIGH and upstream PDF metadata is present.
    7. Phase 1.4 floor lifts driven by signed policy state.

    Pure transform: returns a new ``EmailAnalysisPayload`` with the
    ``ransomware_precursor_analysis`` block populated and
    ``risk_analysis.risk_score`` lifted to
    ``max(llm_risk, precursor_floor, header_divergence_score)``. The
    original payload is not mutated. When all deterministic detectors find no
    signal and all Phase 1.4 lifts are at their ``v0=0`` defaults, the LLM
    ``risk_score`` is preserved byte-identically and the precursor block is
    a zero-valued, empty-indicator overlay.

    Phase 1.4 lifts:
    - ``attachment_risk_floor_lift`` / ``url_obfuscation_floor_lift`` are
      threaded into ``build_precursor_overlay`` so they affect the
      precursor sub-scores AND the ``recommended_risk_floor`` calculation.
    - ``fraud_risk_floor_lift`` is applied AFTER the floor max only when
      the LLM-derived analysis already shows a fraud signal
      (``vendor_fraud_score >= 40`` OR ``wire_transfer_anomaly_score >= 40``).
      This guarantees the lift never raises a safe-rated email's
      risk_score — it can only increase the score on emails the LLM
      already flagged as having vendor-fraud content. The final
      ``risk_score`` is clamped to 0..100 to honour the schema invariant.

    Header divergence (no operator-tunable lift in v0; the detector's
    output is included directly in the floor max). The detector itself
    caps at 90 so it can never single-handedly force a final ``risk_score``
    of 100 — that decision belongs to the LLM scoring path or to combined
    multi-signal evidence.
    """

    enabled_detectors = (
        set(profile_resolution.enabled_detectors) if profile_resolution is not None else None
    )
    overlay = (
        build_precursor_overlay(
            inbound_payload,
            attachment_floor_lift=attachment_risk_floor_lift,
            url_obfuscation_floor_lift=url_obfuscation_floor_lift,
        )
        if enabled_detectors is None
        or "ransomware_precursor_overlay" in enabled_detectors
        else build_precursor_overlay(inbound_payload)
    )
    header_divergence = (
        score_header_divergence(
            sender=inbound_payload.sender,
            headers=inbound_payload.headers,
        )
        if enabled_detectors is None or "header_divergence" in enabled_detectors
        else None
    )
    ghost_thread = (
        score_ghost_thread(
            subject=inbound_payload.subject,
            headers=inbound_payload.headers,
        )
        if enabled_detectors is None or "ghost_thread" in enabled_detectors
        else None
    )
    email_authentication = (
        score_email_authentication(
            sender=inbound_payload.sender,
            headers=inbound_payload.headers,
        )
        if profile_resolution is None or profile_resolution.effective_profile != "low"
        else None
    )
    email_authentication_floor = (
        _email_authentication_floor_for_profile(
            email_authentication.score,
            profile_resolution.effective_profile if profile_resolution is not None else "high",
        )
        if email_authentication is not None
        else 0
    )
    fsl_floor = (
        financial_state_ledger_assessment.recommended_risk_floor
        if financial_state_ledger_assessment is not None
        and (
            enabled_detectors is None
            or "financial_state_ledger" in enabled_detectors
        )
        else 0
    )
    document_metadata_floor = (
        _document_metadata_floor_for_profile(
            document_metadata_assessment.recommended_risk_floor,
            profile_resolution.effective_profile if profile_resolution is not None else "high",
        )
        if document_metadata_assessment is not None
        and (
            profile_resolution is None
            or profile_resolution.effective_profile != "low"
        )
        else 0
    )
    floor_after_precursor = max(
        overlay.recommended_risk_floor,
        header_divergence.score if header_divergence is not None else 0,
        ghost_thread.score if ghost_thread is not None else 0,
        email_authentication_floor,
        fsl_floor,
        document_metadata_floor,
    )
    base_risk_score = max(
        analysis_payload.risk_analysis.risk_score, floor_after_precursor
    )

    fraud_lift = _clamp_fraud_lift(fraud_risk_floor_lift)
    if fraud_lift > 0 and (
        analysis_payload.risk_analysis.vendor_fraud_score >= 40
        or analysis_payload.risk_analysis.wire_transfer_anomaly_score >= 40
    ):
        final_risk_score = min(100, base_risk_score + fraud_lift)
    else:
        final_risk_score = base_risk_score

    risk_update: dict[str, object] = {"risk_score": final_risk_score}
    if email_authentication is not None and email_authentication.indicators:
        risk_update["risk_factors"] = _append_unique(
            analysis_payload.risk_analysis.risk_factors,
            [
                f"email_authentication:{indicator}"
                for indicator in email_authentication.indicators
            ],
        )
        risk_update["phishing_signals"] = _append_unique(
            analysis_payload.risk_analysis.phishing_signals,
            [
                f"email_authentication:{indicator}"
                for indicator in email_authentication.indicators
            ],
        )
    if (
        document_metadata_assessment is not None
        and document_metadata_floor > 0
        and document_metadata_assessment.indicators
    ):
        risk_update["risk_factors"] = _append_unique(
            risk_update.get("risk_factors", analysis_payload.risk_analysis.risk_factors),
            [
                f"document_metadata:{indicator}"
                for indicator in document_metadata_assessment.indicators
            ],
        )
        risk_update["phishing_signals"] = _append_unique(
            risk_update.get(
                "phishing_signals", analysis_payload.risk_analysis.phishing_signals
            ),
            [
                f"document_metadata:{indicator}"
                for indicator in document_metadata_assessment.indicators
            ],
        )

    updated_risk_analysis = analysis_payload.risk_analysis.model_copy(update=risk_update)
    update = {
        "risk_analysis": updated_risk_analysis,
        "ransomware_precursor_analysis": overlay.block,
    }
    if profile_resolution is not None:
        update.update(
            {
                "tenant_default_profile": profile_resolution.tenant_default,
                "effective_profile": profile_resolution.effective_profile,
                "forced_escalation_triggers": list(
                    profile_resolution.forced_escalation_triggers
                ),
            }
        )
    return analysis_payload.model_copy(update=update)


def _clamp_fraud_lift(value: int) -> int:
    if value <= 0:
        return 0
    if value >= 25:
        return 25
    return value


def _append_unique(existing: list[str], additions: list[str]) -> list[str]:
    merged = list(existing)
    seen = set(merged)
    for value in additions:
        if value not in seen:
            merged.append(value)
            seen.add(value)
    return merged


def _email_authentication_floor_for_profile(score: int, profile: SecurityProfile) -> int:
    if score <= 0:
        return 0
    if profile == "high":
        return min(95, score + 10)
    return score


def _document_metadata_floor_for_profile(score: int, profile: SecurityProfile) -> int:
    if score <= 0:
        return 0
    if profile == "high":
        return min(95, score + 10)
    return score


def _write_marker(
    context: RouteContext,
    *,
    config: EmailRiskScoringConfig,
    inbound: BlackboardRecord,
    findings: list[str],
    requires_human_review: bool,
) -> RouteResult:
    return submit_audit_verdict(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.marker_agent_id,
        workflow_id=config.marker_workflow_id,
        parent_record_id=inbound.record_id,
        payload=AuditVerdictPayload(
            target_record_id=inbound.record_id,
            verdict=AuditStatus.APPROVED,
            findings=findings,
            requires_human_review=requires_human_review,
        ),
    )


def _record_failure(
    context: RouteContext,
    *,
    config: EmailRiskScoringConfig,
    inbound: BlackboardRecord,
    raw_output: str,
    failure_reason: str,
) -> tuple[RouteResult, RouteResult]:
    failure_record = submit_email_analysis_failure(
        context,
        tenant_id=config.production_tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.scoring_agent_id,
        parent_record_id=inbound.record_id,
        payload=EmailAnalysisFailurePayload(
            source_email_record_id=inbound.record_id,
            raw_output=raw_output,
            failure_reason=failure_reason,
        ),
    )
    marker = _write_marker(
        context,
        config=config,
        inbound=inbound,
        findings=[
            f"failure_record_id={failure_record.record.record_id}",
            f"failure_reason={failure_reason}",
        ],
        requires_human_review=True,
    )
    return failure_record, marker


# ---------------------------------------------------------------------------
# Phase 1.3 Sandbox Training Pit — in-memory scoring entry point
#
# ``score_one_email_payload`` is the side-effect-free, in-memory Blue
# invocation path used by the Phase 1.3 Red battery cycle (see
# ``core/sandbox/red_battery.py``). Matt's 2026-05-21 §11 decision 2
# locks this path in: per-case sandbox scoring runs against the same
# system prompt + the same schema validator + the same deterministic
# precursor overlay as the production cycle, but does NOT write
# ``EMAIL_INBOUND`` / ``EMAIL_ANALYSIS`` / ``AUDIT_VERDICT`` records to
# the blackboard. The Red battery cycle owns the sandbox writes
# downstream (one ``MUTANT_EVALUATION`` per case + one aggregated
# ``WEAKNESS_REPORT`` per Red profile).
#
# This helper intentionally never touches a ``RouteContext`` so it
# cannot accidentally write to a real blackboard — Red profiles
# cannot smuggle production data through this path even with a
# misconfigured caller.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EmailRiskScoringInMemoryFailure:
    """Typed failure result for ``score_one_email_payload``.

    Mirrors the on-disk ``EmailAnalysisFailurePayload`` shape but stays
    in-memory only. ``raw_output`` is preserved verbatim so the Phase 1.3
    evaluator can attach diagnostic detail to the
    ``Phase13FailureDetail.dynamic_detail`` for the failure mode
    ``analysis_failure_record_written``.
    """

    source_email_record_id: UUID
    raw_output: str
    failure_reason: str


def score_one_email_payload(
    inbound_payload: EmailInboundPayload,
    *,
    llm_client: LLMClient,
    enable_ransomware_precursor_overlay: bool = True,
    max_action_items: int = NORTHSTAR_MAX_ACTION_ITEMS,
    source_email_record_id: UUID | None = None,
) -> EmailAnalysisPayload | EmailRiskScoringInMemoryFailure:
    """Score one ``EmailInboundPayload`` in-memory; never writes to a blackboard.

    Phase 1.3 sandbox Blue invocation per deep dive §4.2 + §11 decision 2.

    Args:
        inbound_payload: Fully-formed payload to score. Phase 1.3 callers
            pass the payload owned by a ``SyntheticEmailAttackCasePayload``;
            production callers should keep using
            ``run_email_risk_scoring_cycle`` instead.
        llm_client: Same callable shape as ``EmailRiskScoringConfig.llm_client``.
        enable_ransomware_precursor_overlay: Mirrors
            ``EmailRiskScoringConfig.enable_ransomware_precursor_overlay``.
            Default ON.
        max_action_items: Soft cap mirroring
            ``EmailRiskScoringConfig.max_action_items``.
        source_email_record_id: Optional foreign-key value embedded in
            the user prompt and propagated to the
            ``EmailAnalysisPayload.source_email_record_id``. Defaults to
            a fresh ``uuid4`` so the helper can be called on an
            arbitrary payload without first writing an ``EMAIL_INBOUND``
            record.

    Returns:
        Either an ``EmailAnalysisPayload`` (with precursor overlay
        applied when enabled) or an ``EmailRiskScoringInMemoryFailure``
        carrying the verbatim LLM raw output and a short failure-reason
        tag matching the production path's reason tags.
    """

    if source_email_record_id is None:
        source_email_record_id = uuid4()

    # Minimal config shell so we can reuse the schema validator without
    # constructing a route-aware config object. ``llm_client`` is unused
    # by ``_try_build_analysis_payload``; we pass it for shape stability.
    helper_config = EmailRiskScoringConfig(
        llm_client=llm_client,
        max_action_items=max_action_items,
        enable_ransomware_precursor_overlay=enable_ransomware_precursor_overlay,
    )

    user_prompt = _build_user_prompt(source_email_record_id, inbound_payload)
    try:
        raw_output = llm_client(NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT, user_prompt)
    except Exception as exc:
        return EmailRiskScoringInMemoryFailure(
            source_email_record_id=source_email_record_id,
            raw_output="",
            failure_reason=f"llm_client_raised:{type(exc).__name__}",
        )

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        return EmailRiskScoringInMemoryFailure(
            source_email_record_id=source_email_record_id,
            raw_output=raw_output,
            failure_reason="invalid_json",
        )

    analysis_payload = _try_build_analysis_payload(
        parsed=parsed,
        source_email_record_id=source_email_record_id,
        config=helper_config,
    )
    if isinstance(analysis_payload, _SchemaValidationError):
        return EmailRiskScoringInMemoryFailure(
            source_email_record_id=source_email_record_id,
            raw_output=raw_output,
            failure_reason=analysis_payload.reason,
        )

    if helper_config.enable_ransomware_precursor_overlay:
        profile_resolution = resolve_profile_for_email(
            tenant_default=helper_config.default_profile_when_unset,
            addon_detectors=(),
            evidence=ForcedEscalationEvidence(
                llm_risk_score=analysis_payload.risk_analysis.risk_score,
                header_divergence_score=score_header_divergence(
                    sender=inbound_payload.sender,
                    headers=inbound_payload.headers,
                ).score,
                ghost_thread_score=score_ghost_thread(
                    subject=inbound_payload.subject,
                    headers=inbound_payload.headers,
                ).score,
                manual_escalation_requested=False,
            ),
        )
        analysis_payload = _overlay_ransomware_precursor(
            analysis_payload,
            inbound_payload,
            profile_resolution=profile_resolution,
        )

    return analysis_payload
