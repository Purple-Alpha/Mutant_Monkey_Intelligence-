from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.evidence_package import gates

BOUNDARY_FIXTURE = "Exact package boundary fixture text."


def test_broken_link_gate_requires_source_artifact_path_to_resolve(tmp_path):
    artifact = tmp_path / "audit_outputs" / "record.md"
    artifact.parent.mkdir()
    artifact.write_text("evidence\n", encoding="utf-8")

    passing = gates.run_broken_link_gate(
        [{"record_id": "r1", "source_artifact_path": "audit_outputs/record.md"}],
        workspace_root=tmp_path,
    )
    failing = gates.run_broken_link_gate(
        [{"record_id": "r2", "source_artifact_path": "audit_outputs/missing.md"}],
        workspace_root=tmp_path,
    )

    assert passing.passed
    assert not failing.passed
    assert failing.findings[0].code == "source_artifact_missing"


def test_signed_provenance_gate_requires_policy_and_override_signatures(tmp_path):
    signed = tmp_path / "4. Product_Roadmap" / "Signed_Spec.md"
    signed.parent.mkdir()
    signed.write_text("signed\n", encoding="utf-8")

    passing = gates.run_signed_provenance_gate(
        [{"record_type": "tenant_override", "signed_by": "4. Product_Roadmap/Signed_Spec.md"}],
        workspace_root=tmp_path,
    )
    failing = gates.run_signed_provenance_gate(
        [{"record_type": "policy_state", "record_id": "policy-1"}],
        workspace_root=tmp_path,
    )

    assert passing.passed
    assert not failing.passed
    assert failing.findings[0].code == "missing_signed_by"


def test_stale_evidence_gate_enforces_thresholds_and_signed_exemption(tmp_path):
    signed = tmp_path / "signed.md"
    signed.write_text("signed\n", encoding="utf-8")
    now = datetime(2026, 6, 3, tzinfo=timezone.utc)

    result = gates.run_stale_evidence_gate(
        [
            {
                "record_id": "fresh",
                "evidence_category": "detection_evidence",
                "last_verified_at": "2026-05-15T00:00:00+00:00",
            },
            {
                "record_id": "stale",
                "evidence_category": "policy_change_control",
                "last_verified_at": "2026-04-01T00:00:00+00:00",
            },
            {
                "record_id": "signed-old",
                "evidence_category": "policy_change_control",
                "last_verified_at": "2025-01-01T00:00:00+00:00",
                "signed_by": "signed.md",
            },
        ],
        now=now,
        workspace_root=tmp_path,
    )

    assert not result.passed
    assert [finding.path for finding in result.findings] == ["stale"]
    assert result.findings[0].code == "stale_evidence"


def test_stale_evidence_gate_requires_superseded_signed_annotation(tmp_path):
    signed = tmp_path / "signed.md"
    signed.write_text("signed\n", encoding="utf-8")

    result = gates.run_stale_evidence_gate(
        [
            {
                "record_id": "old-spec",
                "evidence_category": "policy_change_control",
                "last_verified_at": "2025-01-01T00:00:00+00:00",
                "signed_by": "signed.md",
                "superseded_by": "new-spec",
            }
        ],
        now=datetime(2026, 6, 3, tzinfo=timezone.utc),
        workspace_root=tmp_path,
    )

    assert not result.passed
    assert result.findings[0].code == "missing_superseded_annotation"


def test_claim_validation_gate_requires_each_claim_to_trace_to_sourced_record():
    records = [
        {"record_id": "r1", "source_artifact_path": "audit_outputs/r1.md"},
        {"record_id": "r2"},
    ]

    passing = gates.run_claim_validation_gate([{"claim_id": "c1", "record_refs": ["r1"]}], records)
    failing = gates.run_claim_validation_gate(
        [
            {"claim_id": "missing-source"},
            {"claim_id": "bad-ref", "record_refs": ["nope"]},
            {"claim_id": "unsourced-ref", "record_refs": ["r2"]},
        ],
        records,
    )

    assert passing.passed
    assert not failing.passed
    assert {finding.code for finding in failing.findings} == {
        "claim_has_no_source",
        "claim_record_ref_missing",
        "claim_record_has_no_source",
    }


def test_redaction_gate_blocks_secrets_raw_bodies_and_cross_tenant_identifiers():
    result = gates.run_redaction_gate(
        [
            {"record_id": "secret", "notes": "XAI_API_KEY=xai-" + "a" * 24},
            {"record_id": "raw", "raw_email_body": "full message content"},
        ],
        rendered_texts=["tenant-b appears in tenant-a package"],
        tenant_id="tenant-a",
        known_tenant_ids=["tenant-a", "tenant-b"],
    )

    assert not result.passed
    assert {finding.code for finding in result.findings} >= {
        "secret_or_credential_present",
        "raw_body_field_present",
        "cross_tenant_identifier",
    }


def test_forbidden_language_gate_allows_only_explicit_allowed_contexts():
    result = gates.run_forbidden_language_gate(
        [
            {"path": "scope", "text": "This context may name compliance.", "allowed_context": True},
            {"path": "claim", "text": "NorthStar is compliant and guaranteed."},
        ]
    )

    assert not result.passed
    assert [finding.path for finding in result.findings] == ["claim", "claim"]


def test_vocabulary_translation_gate_blocks_untranslated_carrier_jargon():
    passing = gates.run_vocabulary_translation_gate(
        ["This shows how well this control works in practice."]
    )
    failing = gates.run_vocabulary_translation_gate(
        [{"path": "render.md", "text": "Control efficacy is documented."}]
    )

    assert passing.passed
    assert not failing.passed
    assert failing.findings[0].code == "untranslated_jargon"


def test_scope_boundary_gate_requires_exact_statement():
    assert gates.run_scope_boundary_gate(
        f"# Package\n\n{BOUNDARY_FIXTURE}\n",
        boundary_statement=BOUNDARY_FIXTURE,
    ).passed

    result = gates.run_scope_boundary_gate(
        "This package mostly covers the same thing.",
        boundary_statement=BOUNDARY_FIXTURE,
    )

    assert not result.passed
    assert result.findings[0].code == "scope_boundary_missing_or_edited"


def test_audit_packet_coverage_gate_blocks_touched_files_outside_packet():
    passing = gates.run_audit_packet_coverage_gate(
        ["core/evidence_package/gates.py"],
        ["core/evidence_package/gates.py", "tests/test_gates.py"],
    )
    failing = gates.run_audit_packet_coverage_gate(
        ["core/evidence_package/gates.py", "PROJECT_ACTIVITY_LOG.md"],
        ["core/evidence_package/gates.py"],
    )

    assert passing.passed
    assert not failing.passed
    assert failing.findings[0].path == "PROJECT_ACTIVITY_LOG.md"


def test_canonical_lists_match_signed_gate_sources():
    assert "compliant" in gates.FORBIDDEN_LANGUAGE_PHRASES
    assert "SOC 2" in gates.FORBIDDEN_LANGUAGE_PHRASES
    assert (
        gates.VOCABULARY_TRANSLATIONS["control attestation framework"]
        == "the way we record what each control does"
    )
    assert gates.FRESHNESS_THRESHOLDS_DAYS["policy_change_control"] == 30
    assert gates.FRESHNESS_THRESHOLDS_DAYS["detection_evidence"] == 90
