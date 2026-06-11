"""Phase 2 — Layer 0 Knowledge Foundation tests (six intel agents).

Three test classes per agent per AGENTS.md §5 and
``Phase2_Knowledge_Foundation_Agent_Design_Contract.md`` §5:
  Class 1 — expected pass
  Class 2 — adversarial / break-it (enforces P2-D1 brief-only and P2-D7 no-blackboard)
  Class 3 — known-gap xfail (documented, with completion path)

Driven by a registry so every one of the six agents gets all three classes.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from datetime import datetime

import pytest
from pydantic import ValidationError

from core.knowledge import (
    AIGenContentBriefing,
    AIGenContentIntelAgent,
    BECBriefing,
    BECIntelAgent,
    GeoBriefing,
    GeoIntelAgent,
    ImageRatioThresholds,
    PhishBriefing,
    PhishIntelAgent,
    RansomwareBriefing,
    RansomwareIntelAgent,
    TimeAnomalyWindow,
    TrojanDeliveryBriefing,
    TrojanDeliveryIntelAgent,
)

# (agent class, briefing type, tuple-of-str field names, module name).
AGENTS = [
    (
        PhishIntelAgent,
        PhishBriefing,
        (
            "known_phish_domains",
            "lookalike_patterns",
            "credential_harvest_urls",
            "social_engineering_cues",
        ),
        "core.knowledge.phish_intel_agent",
    ),
    (
        RansomwareIntelAgent,
        RansomwareBriefing,
        (
            "known_delivery_hashes",
            "lure_language_patterns",
            "known_c2_domains",
            "file_extension_flags",
        ),
        "core.knowledge.ransomware_intel_agent",
    ),
    (
        BECIntelAgent,
        BECBriefing,
        (
            "ceo_impersonation_patterns",
            "invoice_fraud_templates",
            "wire_transfer_trigger_phrases",
            "vendor_redirect_patterns",
        ),
        "core.knowledge.bec_intel_agent",
    ),
    (
        TrojanDeliveryIntelAgent,
        TrojanDeliveryBriefing,
        (
            "weaponised_extensions",
            "macro_trigger_patterns",
            "delayed_payload_markers",
            "known_dropper_hashes",
        ),
        "core.knowledge.trojan_delivery_intel_agent",
    ),
    (
        GeoIntelAgent,
        GeoBriefing,
        ("high_risk_ip_ranges", "high_risk_countries", "known_vpn_exit_nodes"),
        "core.knowledge.geo_intel_agent",
    ),
    (
        AIGenContentIntelAgent,
        AIGenContentBriefing,
        ("ai_text_signatures", "deepfake_image_markers", "ai_phishing_templates"),
        "core.knowledge.ai_gen_content_intel_agent",
    ),
]

_IDS = [a[0].__name__ for a in AGENTS]

# Capabilities a brief-only knowledge agent must never expose (P2-D1 / P2-D7).
_FORBIDDEN_METHODS = (
    "detect",
    "score",
    "flag",
    "verdict",
    "classify",
    "evaluate",
    "write",
    "write_blackboard",
    "record",
    "contribute",
    "append",
    "update_knowledge",
)


def _imported_modules(module) -> set[str]:
    """All module names imported by ``module`` (AST of its source)."""

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


@pytest.mark.parametrize("agent_cls, briefing_cls, tuple_fields, _mod", AGENTS, ids=_IDS)
def test_brief_returns_correct_structure(agent_cls, briefing_cls, tuple_fields, _mod):
    briefing = agent_cls().brief()
    assert isinstance(briefing, briefing_cls)
    for field in tuple_fields:
        assert isinstance(getattr(briefing, field), tuple)
        assert all(isinstance(item, str) for item in getattr(briefing, field))


@pytest.mark.parametrize("agent_cls, briefing_cls, tuple_fields, _mod", AGENTS, ids=_IDS)
def test_last_updated_is_iso8601(agent_cls, briefing_cls, tuple_fields, _mod):
    briefing = agent_cls().brief()
    parsed = datetime.fromisoformat(briefing.last_updated)
    assert parsed.year == 2026


@pytest.mark.parametrize("agent_cls, briefing_cls, tuple_fields, _mod", AGENTS, ids=_IDS)
def test_confidence_floor_in_range(agent_cls, briefing_cls, tuple_fields, _mod):
    briefing = agent_cls().brief()
    assert 0.0 <= briefing.confidence_floor <= 1.0


def test_geo_time_windows_are_frozen_structured():
    briefing = GeoIntelAgent().brief()
    assert all(isinstance(w, TimeAnomalyWindow) for w in briefing.time_anomaly_windows)
    for w in briefing.time_anomaly_windows:
        assert 0 <= w.start_hour_utc <= 23
        assert 0 <= w.end_hour_utc <= 23


def test_aigen_thresholds_are_frozen_structured():
    briefing = AIGenContentIntelAgent().brief()
    assert isinstance(briefing.image_ratio_thresholds, ImageRatioThresholds)
    assert 0.0 <= briefing.image_ratio_thresholds.images_to_text_warn <= 1.0


# ---------------------------------------------------------------------------
# Class 2 — Adversarial / break-it
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent_cls, briefing_cls, tuple_fields, _mod", AGENTS, ids=_IDS)
def test_briefing_is_immutable(agent_cls, briefing_cls, tuple_fields, _mod):
    briefing = agent_cls().brief()
    # Frozen model: reassigning a field is rejected, not silently accepted.
    with pytest.raises((ValidationError, TypeError, AttributeError)):
        briefing.confidence_floor = 0.99
    # Tuple fields: no in-place mutation surface (a list would allow .append()).
    for field in tuple_fields:
        assert not hasattr(getattr(briefing, field), "append")


@pytest.mark.parametrize("agent_cls, briefing_cls, tuple_fields, _mod", AGENTS, ids=_IDS)
def test_extra_field_rejected(agent_cls, briefing_cls, tuple_fields, _mod):
    base = agent_cls().brief().model_dump()
    base["smuggled_field"] = "x"
    with pytest.raises(ValidationError):
        briefing_cls(**base)


@pytest.mark.parametrize("agent_cls, briefing_cls, tuple_fields, _mod", AGENTS, ids=_IDS)
def test_malformed_confidence_floor_safe_error(agent_cls, briefing_cls, tuple_fields, _mod):
    base = agent_cls().brief().model_dump()
    base["confidence_floor"] = 2.5  # out of [0,1]
    with pytest.raises(ValidationError):
        briefing_cls(**base)


@pytest.mark.parametrize("agent_cls, briefing_cls, tuple_fields, _mod", AGENTS, ids=_IDS)
def test_agent_exposes_no_detection_or_write_surface(
    agent_cls, briefing_cls, tuple_fields, _mod
):
    agent = agent_cls()
    for name in _FORBIDDEN_METHODS:
        assert not hasattr(agent, name), f"{agent_cls.__name__} must not expose {name!r}"
    # The only public capability is brief().
    public = [n for n in dir(agent) if not n.startswith("_")]
    assert public == ["brief"], f"{agent_cls.__name__} public surface: {public}"


@pytest.mark.parametrize("agent_cls, briefing_cls, tuple_fields, mod_name", AGENTS, ids=_IDS)
def test_module_does_not_import_blackboard(agent_cls, briefing_cls, tuple_fields, mod_name):
    module = importlib.import_module(mod_name)
    imported = _imported_modules(module)
    assert not any("blackboard" in name for name in imported), (
        f"{mod_name} imports a blackboard module (P2-D7 violation): {imported}"
    )


# ---------------------------------------------------------------------------
# Class 3 — Known-gap xfail (documented; completion path per contract §5)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Real-time threat-feed ingestion deferred (contract §5 Class 3): autonomous "
        "ingestion is not authorized until Phase 5. Completion path: Phase 5 mutation "
        "engine contract."
    ),
    strict=True,
)
def test_real_time_feed_ingestion():
    agent = PhishIntelAgent()
    assert hasattr(agent, "refresh_from_feed"), (
        "no autonomous feed ingestion at Phase 2 (static seed only, P2-D4)"
    )


@pytest.mark.xfail(
    reason=(
        "Cross-tenant knowledge differentiation deferred (contract §5 Class 3): the "
        "global knowledge base is sufficient at Phase 2 (P2-D6). Completion path: "
        "post-launch tenant data analysis."
    ),
    strict=True,
)
def test_per_tenant_knowledge_differentiation():
    agent = PhishIntelAgent()
    # Briefing takes no tenant_id at Phase 2 — knowledge is global (P2-D6).
    briefing_a = agent.brief(tenant_id="tenant_a")  # type: ignore[call-arg]
    briefing_b = agent.brief(tenant_id="tenant_b")  # type: ignore[call-arg]
    assert briefing_a != briefing_b
