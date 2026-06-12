"""Phase 3 — Layer 1 Detection Swarm tests (six agents).

Three test classes per agent per AGENTS.md §5 and
``Phase3_Detection_Swarm_Agent_Design_Contract.md`` §5 + Amendment 1 §D:
  Class 1 — expected pass
  Class 2 — adversarial / break-it (P3-D1 no verdict, P3-D2 type closure,
            P3-D5 tenant isolation, Amendment §B sender_domain, Amendment §C
            token attribution)
  Class 3 — known-gap xfail (documented, with completion path)

Driven by a registry so every one of the six agents gets all three classes.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

import pytest

from core.blackboard import (
    CanonicalEvidenceLedger,
    EvidenceStage,
    EvidenceType,
    LedgerSchemaError,
    TokenActionType,
    TokenUsageTracker,
)
from core.detectors import (
    AttachmentInput,
    AttachmentSandbox,
    ContentAnalyzer,
    DetectionError,
    EmailContext,
    GeoVelocityAgent,
    ImageClassifier,
    SenderHistoryAgent,
    SenderHistoryStore,
    URLReceptor,
    normalize_sender_domain,
)
from core.knowledge import (
    AIGenContentIntelAgent,
    BECIntelAgent,
    GeoIntelAgent,
    PhishIntelAgent,
    RansomwareIntelAgent,
    TrojanDeliveryIntelAgent,
)

# ---------------------------------------------------------------------------
# Registry — one entry per agent: (factory, evidence_type, detail_keys, module)
# ---------------------------------------------------------------------------

def _make_sender(ledger: CanonicalEvidenceLedger) -> SenderHistoryAgent:
    store = SenderHistoryStore(
        {
            ("tenant-a", "vendor.example"): {
                "prior_interaction_count": 12,
                "last_contact_date": "2026-05-01T00:00:00+00:00",
                "established_vendor": True,
            }
        }
    )
    return SenderHistoryAgent(ledger, store=store)


def _make_geo(ledger: CanonicalEvidenceLedger) -> GeoVelocityAgent:
    return GeoVelocityAgent(ledger, GeoIntelAgent())


def _make_content(
    ledger: CanonicalEvidenceLedger, token_tracker: TokenUsageTracker
) -> ContentAnalyzer:
    return ContentAnalyzer(
        ledger, PhishIntelAgent(), BECIntelAgent(), token_tracker
    )


def _make_url(ledger: CanonicalEvidenceLedger) -> URLReceptor:
    return URLReceptor(ledger, PhishIntelAgent())


def _make_attachment(
    ledger: CanonicalEvidenceLedger, token_tracker: TokenUsageTracker
) -> AttachmentSandbox:
    return AttachmentSandbox(
        ledger,
        TrojanDeliveryIntelAgent(),
        RansomwareIntelAgent(),
        token_tracker,
    )


def _make_image(ledger: CanonicalEvidenceLedger) -> ImageClassifier:
    return ImageClassifier(ledger, AIGenContentIntelAgent())


AGENTS = [
    (
        "SenderHistoryAgent",
        _make_sender,
        EvidenceType.SENDER_SIGNAL,
        (
            "sender_domain",
            "known_contact",
            "first_time_sender",
            "prior_interaction_count",
            "last_contact_date",
            "established_vendor",
        ),
        "core.detectors.sender_history_agent",
        False,
    ),
    (
        "GeoVelocityAgent",
        _make_geo,
        EvidenceType.GEO_SIGNAL,
        (
            "sender_domain",
            "sending_ip",
            "ip_country",
            "account_home_country",
            "velocity_flag",
            "high_risk_region",
            "vpn_detected",
            "sender_history_match",
        ),
        "core.detectors.geo_velocity_agent",
        False,
    ),
    (
        "ContentAnalyzer",
        _make_content,
        EvidenceType.CONTENT_SIGNAL,
        (
            "urgency_detected",
            "bec_pattern_match",
            "wire_transfer_request",
            "ceo_impersonation_flag",
            "policy_violation",
            "sentiment_score",
            "language_anomaly",
        ),
        "core.detectors.content_analyzer",
        True,
    ),
    (
        "URLReceptor",
        _make_url,
        EvidenceType.URL_SIGNAL,
        (
            "urls_found",
            "malicious_url_detected",
            "redirect_chain_anomaly",
            "final_destination",
            "credential_harvest_flag",
            "reputation_score",
        ),
        "core.detectors.url_receptor",
        False,
    ),
    (
        "AttachmentSandbox",
        _make_attachment,
        EvidenceType.ATTACHMENT_SIGNAL,
        (
            "attachment_present",
            "file_hash",
            "known_malicious_hash",
            "execution_attempted",
            "network_callback_detected",
            "callback_destination",
            "file_drop_detected",
            "macro_execution",
            "zero_day_candidate",
        ),
        "core.detectors.attachment_sandbox",
        True,
    ),
    (
        "ImageClassifier",
        _make_image,
        EvidenceType.IMAGE_SIGNAL,
        (
            "images_present",
            "image_count",
            "image_text_ratio",
            "ai_generated_detected",
            "deepfake_indicator",
            "bulk_content_flag",
            "spam_signal_only",
        ),
        "core.detectors.image_classifier",
        False,
    ),
]

_IDS = [a[0] for a in AGENTS]

_FORBIDDEN_NETWORK_IMPORTS = (
    "socket",
    "requests",
    "urllib",
    "httpx",
    "aiohttp",
    "subprocess",
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def ledger(tmp_path: Path) -> CanonicalEvidenceLedger:
    return CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")


@pytest.fixture
def token_tracker(tmp_path: Path) -> TokenUsageTracker:
    return TokenUsageTracker(tmp_path / "tokens.jsonl")


def _sample_email(**overrides) -> EmailContext:
    base = dict(
        email_id="email-001",
        tenant_id="tenant-a",
        from_domain="Vendor.Example.",
        sending_ip="192.0.2.10",
        ip_country="US",
        account_home_country="US",
        subject="Urgent wire transfer needed today",
        body=(
            "Please remit to the new account below. "
            "This must be completed today and kept confidential."
        ),
        urls=(
            "https://secure-login-verify.example/login",
            "https://account-update-portal.example/session/validate",
        ),
        attachments=(
            AttachmentInput(
                filename="invoice.docm",
                sha256=(
                    "SYNTHETIC-SEED-000000000000000000000000000000000000000000000000000000000A"
                ),
                extension=".docm",
            ),
        ),
        image_count=2,
    )
    base.update(overrides)
    return EmailContext(**base)


def _build_agent(
    name: str,
    factory,
    ledger: CanonicalEvidenceLedger,
    token_tracker: TokenUsageTracker,
):
    if name in ("ContentAnalyzer", "AttachmentSandbox"):
        return factory(ledger, token_tracker)
    return factory(ledger)


def _imported_modules(module) -> set[str]:
    tree = ast.parse(inspect.getsource(module))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


# ---------------------------------------------------------------------------
# Class 1 — Expected pass
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name, factory, evidence_type, detail_keys, _mod, _token",
    AGENTS,
    ids=_IDS,
)
def test_writes_correct_evidence_type(
    name, factory, evidence_type, detail_keys, _mod, _token, ledger, token_tracker
):
    agent = _build_agent(name, factory, ledger, token_tracker)
    entry = agent.analyze(_sample_email())
    assert entry.evidence_type == evidence_type
    assert entry.agent_id == agent.AGENT_ID
    assert entry.tenant_id == "tenant-a"
    assert entry.email_id == "email-001"
    assert 0.0 <= entry.confidence <= 1.0
    assert entry.stage == EvidenceStage.ES2


@pytest.mark.parametrize(
    "name, factory, evidence_type, detail_keys, _mod, _token",
    AGENTS,
    ids=_IDS,
)
def test_details_schema_complete(
    name, factory, evidence_type, detail_keys, _mod, _token, ledger, token_tracker
):
    agent = _build_agent(name, factory, ledger, token_tracker)
    entry = agent.analyze(_sample_email())
    assert set(entry.details.keys()) == set(detail_keys)


@pytest.mark.parametrize(
    "name, factory, evidence_type, detail_keys, _mod, _token",
    AGENTS,
    ids=_IDS,
)
def test_tenant_isolation_on_write(
    name, factory, evidence_type, detail_keys, _mod, _token, ledger, token_tracker
):
    agent = _build_agent(name, factory, ledger, token_tracker)
    agent.analyze(_sample_email(tenant_id="tenant-a"))
    assert ledger.count_for_tenant("tenant-a") == 1
    assert ledger.count_for_tenant("tenant-b") == 0


def test_sender_domain_normalization_examples():
    assert normalize_sender_domain("Example.COM.") == "example.com"
    assert normalize_sender_domain("EXAMPLE.com") == "example.com"
    assert normalize_sender_domain("mail.example.com:443") == "mail.example.com"
    assert normalize_sender_domain("  vendor.example.  ") == "vendor.example"


def test_sender_domain_idn_punycode():
    result = normalize_sender_domain("MÜNICH.de")
    assert result.startswith("xn--")
    assert result.endswith(".de")


def test_sender_history_known_contact():
    agent = _make_sender(
        CanonicalEvidenceLedger(Path("/dev/null"))  # overwritten below
    )
    # Use a real temp ledger for the write.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        led = CanonicalEvidenceLedger(Path(tmp) / "evidence.jsonl")
        agent = _make_sender(led)
        entry = agent.analyze(_sample_email(from_domain="vendor.example"))
        assert entry.details["known_contact"] is True
        assert entry.details["sender_domain"] == "vendor.example"
        assert entry.details["prior_interaction_count"] == 12


def test_geo_velocity_high_risk_ip():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        led = CanonicalEvidenceLedger(Path(tmp) / "evidence.jsonl")
        agent = _make_geo(led)
        entry = agent.analyze(_sample_email(sending_ip="192.0.2.10"))
        assert entry.details["high_risk_region"] is True
        assert entry.details["sender_domain"] == "vendor.example"


def test_content_analyzer_bec_signals():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        led = CanonicalEvidenceLedger(Path(tmp) / "evidence.jsonl")
        tok = TokenUsageTracker(Path(tmp) / "tokens.jsonl")
        agent = _make_content(led, tok)
        entry = agent.analyze(_sample_email())
        assert entry.details["wire_transfer_request"] is True
        assert entry.details["bec_pattern_match"] is True


def test_url_receptor_malicious_url():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        led = CanonicalEvidenceLedger(Path(tmp) / "evidence.jsonl")
        agent = _make_url(led)
        entry = agent.analyze(_sample_email())
        assert entry.details["malicious_url_detected"] is True
        assert entry.details["credential_harvest_flag"] is True


def test_attachment_sandbox_known_hash():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        led = CanonicalEvidenceLedger(Path(tmp) / "evidence.jsonl")
        tok = TokenUsageTracker(Path(tmp) / "tokens.jsonl")
        agent = _make_attachment(led, tok)
        entry = agent.analyze(_sample_email())
        assert entry.details["known_malicious_hash"] is True
        assert entry.details["macro_execution"] is True


def test_image_classifier_bulk_flag():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        led = CanonicalEvidenceLedger(Path(tmp) / "evidence.jsonl")
        agent = _make_image(led)
        entry = agent.analyze(_sample_email(image_count=10, body="hi"))
        assert entry.details["images_present"] is True
        assert entry.details["bulk_content_flag"] is True


# ---------------------------------------------------------------------------
# Class 2 — Adversarial / break-it
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name, factory, evidence_type, detail_keys, _mod, _token",
    AGENTS,
    ids=_IDS,
)
def test_no_verdict_field_in_details(
    name, factory, evidence_type, detail_keys, _mod, _token, ledger, token_tracker
):
    agent = _build_agent(name, factory, ledger, token_tracker)
    entry = agent.analyze(_sample_email())
    assert "verdict" not in entry.details


@pytest.mark.parametrize(
    "name, factory, evidence_type, detail_keys, _mod, _token",
    AGENTS,
    ids=_IDS,
)
def test_malformed_input_safe_error(
    name, factory, evidence_type, detail_keys, _mod, _token, ledger, token_tracker
):
    agent = _build_agent(name, factory, ledger, token_tracker)
    with pytest.raises(DetectionError):
        agent.analyze({"not": "an EmailContext"})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "name, factory, evidence_type, detail_keys, mod_name, _token",
    AGENTS,
    ids=_IDS,
)
def test_no_client_side_network_imports(
    name, factory, evidence_type, detail_keys, mod_name, _token
):
    module = importlib.import_module(mod_name)
    imported = _imported_modules(module)
    for forbidden in _FORBIDDEN_NETWORK_IMPORTS:
        assert not any(
            name.startswith(forbidden) for name in imported
        ), f"{mod_name} imports {forbidden!r} (P3-D4 cloud-side only): {imported}"


def test_sender_and_geo_sender_domain_byte_identical():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        led = CanonicalEvidenceLedger(Path(tmp) / "evidence.jsonl")
        sender = _make_sender(led)
        geo = _make_geo(led)
        email = _sample_email(from_domain="Example.COM:443")
        sender_entry = sender.analyze(email)
        geo_entry = geo.analyze(email)
        assert sender_entry.details["sender_domain"] == geo_entry.details["sender_domain"]
        assert sender_entry.details["sender_domain"] == "example.com"


def test_content_analyzer_token_charged_to_tenant(ledger, token_tracker):
    agent = _make_content(ledger, token_tracker)
    agent.analyze(_sample_email(tenant_id="tenant-a"))
    records = token_tracker.read_for_tenant("tenant-a")
    assert records, "ContentAnalyzer must record token usage (Amendment §C)"
    assert all(r.tenant_id == "tenant-a" for r in records)
    assert all(r.agent_id == ContentAnalyzer.AGENT_ID for r in records)
    assert all(r.action_type == TokenActionType.DETECTION for r in records)


def test_attachment_sandbox_token_charged_to_tenant(ledger, token_tracker):
    agent = _make_attachment(ledger, token_tracker)
    agent.analyze(_sample_email(tenant_id="tenant-a"))
    records = token_tracker.read_for_tenant("tenant-a")
    assert records, "AttachmentSandbox must record token usage (Amendment §C)"
    assert all(r.tenant_id == "tenant-a" for r in records)
    assert all(r.agent_id == AttachmentSandbox.AGENT_ID for r in records)


@pytest.mark.parametrize("factory", [_make_sender, _make_geo, _make_url, _make_image])
def test_lookup_agents_do_not_record_tokens(factory, ledger, token_tracker):
    agent = factory(ledger) if factory != _make_sender else factory(ledger)
    agent.analyze(_sample_email(tenant_id="tenant-a"))
    assert token_tracker.read_for_tenant("tenant-a") == []


def test_zero_day_candidate_does_not_auto_deploy():
    agent = AttachmentSandbox(
        CanonicalEvidenceLedger(Path("/dev/null")),
        TrojanDeliveryIntelAgent(),
        RansomwareIntelAgent(),
        TokenUsageTracker(Path("/dev/null")),
    )
    assert not hasattr(agent, "deploy_rule")
    assert not hasattr(agent, "auto_deploy")


def test_image_classifier_no_fraud_route_method():
    agent = ImageClassifier(
        CanonicalEvidenceLedger(Path("/dev/null")), AIGenContentIntelAgent()
    )
    assert not hasattr(agent, "route_to_fraud")
    assert not hasattr(agent, "trigger_fraud_action")


def test_geo_velocity_requires_briefing(ledger):
    with pytest.raises(DetectionError):
        GeoVelocityAgent(ledger, None)  # type: ignore[arg-type]


def test_content_analyzer_requires_token_tracker(ledger):
    with pytest.raises(DetectionError):
        ContentAnalyzer(ledger, PhishIntelAgent(), BECIntelAgent(), None)  # type: ignore[arg-type]


def test_verdict_field_rejected_by_ledger(tmp_path):
    """A top-level ``verdict`` field is rejected — P3-D1, no verdict exists."""
    led = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    with pytest.raises(LedgerSchemaError):
        led.append(
            {
                "agent_id": "sender_history_agent",
                "tenant_id": "tenant-a",
                "email_id": "email-001",
                "evidence_type": "sender_signal",
                "details": {"sender_domain": "example.com"},
                "confidence": 0.5,
                "stage": "ES2",
                "verdict": "malicious",
            }
        )


# ---------------------------------------------------------------------------
# Class 3 — Known-gap xfail (documented; completion path per contract §5)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Real-data signal testing deferred (contract §5 Class 3): requires "
        "production tenant traffic. Completion path: ES3 after first real tenant "
        "onboarded."
    ),
    strict=True,
)
def test_real_data_signal_testing():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        led = CanonicalEvidenceLedger(Path(tmp) / "evidence.jsonl")
        agent = _make_sender(led)
        entry = agent.analyze(_sample_email())
        assert entry.stage == EvidenceStage.ES3


@pytest.mark.xfail(
    reason=(
        "Cross-agent reconciliation testing deferred (contract §5 Class 3): "
        "ReconciliationAgent not yet built. Completion path: Phase 4."
    ),
    strict=True,
)
def test_cross_agent_reconciliation():
    from core.detectors import ReconciliationAgent  # noqa: F401


@pytest.mark.xfail(
    reason=(
        "Collective Immune System propagation deferred (contract §5 Class 3): "
        "DEPTH GATE CLOSED. Completion path: Phase 6."
    ),
    strict=True,
)
def test_collective_immune_system_propagation():
    agent = URLReceptor(
        CanonicalEvidenceLedger(Path("/dev/null")), PhishIntelAgent()
    )
    assert hasattr(agent, "propagate_to_cis")
