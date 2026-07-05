from __future__ import annotations

import sys
from pathlib import Path

import pytest

CHAOS = Path(__file__).resolve().parents[1] / "mmi" / "project_brain" / "chaos"
for p in (CHAOS,):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from genomic_constraint_synth import (  # noqa: E402
    synthesize_constraint_v1,
    validate_breach_descriptor,
)
from genomic_constraint_validator import (  # noqa: E402
    compute_constraint_id,
    validate_genomic_constraint,
)


def _breach() -> dict:
    return {
        "descriptor_version": "breach_descriptor_v1",
        "incident_id": "inc-test-001",
        "critic_node": "critic-alpha",
        "exploit_id": "purple_exfil_proc_environ",
        "mirror_agent_id": "attacker_sim_01",
        "payload": "exfil /proc/self/environ",
    }


def _harvest() -> dict:
    return {"harvested_at_ms": 1_782_200_000_000, "exploit_class": "exfil"}


def test_breach_descriptor_valid() -> None:
    verdict, reasons = validate_breach_descriptor(_breach())
    assert verdict == "VALID"
    assert not reasons


def test_synth_deterministic() -> None:
    a = synthesize_constraint_v1(_harvest(), _breach(), episode_id="gre-test-001")
    b = synthesize_constraint_v1(_harvest(), _breach(), episode_id="gre-test-001")
    assert a["constraint_id"] == b["constraint_id"]
    assert a["constraint_id"] == compute_constraint_id(a)


def test_validate_accepts_synth_output() -> None:
    artifact = synthesize_constraint_v1(_harvest(), _breach(), episode_id="gre-test-001")
    verdict, reasons = validate_genomic_constraint(artifact)
    assert verdict == "VALID", reasons


def test_validate_rejects_bad_type() -> None:
    artifact = synthesize_constraint_v1(_harvest(), _breach(), episode_id="gre-test-001")
    artifact["constraint_type"] = "run_arbitrary_code"
    verdict, reasons = validate_genomic_constraint(artifact)
    assert verdict == "REJECTED"
    assert "ARTIFACT_SCHEMA_FAIL" in reasons


def test_validate_rejects_unregistered_capability() -> None:
    artifact = synthesize_constraint_v1(_harvest(), _breach(), episode_id="gre-test-001")
    artifact["constraint_body"]["target"] = "agent.unregistered.foo"
    verdict, reasons = validate_genomic_constraint(artifact)
    assert verdict == "REJECTED"
    assert "CAPABILITY_UNREGISTERED" in reasons


def test_validate_rejects_fragment() -> None:
    artifact = synthesize_constraint_v1(_harvest(), _breach(), episode_id="gre-test-001")
    artifact["constraint_completeness"] = "partial_fragment"
    verdict, reasons = validate_genomic_constraint(artifact)
    assert verdict == "REJECTED"
    assert "INCOMPLETE_BUNDLE" in reasons


def test_validate_rejects_executable_field() -> None:
    artifact = synthesize_constraint_v1(_harvest(), _breach(), episode_id="gre-test-001")
    artifact["constraint_body"]["code"] = "import os; os.system('x')"
    verdict, reasons = validate_genomic_constraint(artifact)
    assert verdict == "REJECTED"
    assert "EXECUTABLE_FIELD_DENIED" in reasons
