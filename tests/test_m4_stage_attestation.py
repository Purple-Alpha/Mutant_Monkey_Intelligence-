from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from mmi.m4.key_custody import (
    KeyCustodyNonExportable,
    SoftwareStubCustodian,
    TpmHsmCustodian,
    create_custodian,
    custody_selftest,
)
from mmi.m4.stage_attestation import (
    GENESIS_PARENT_HASH,
    STAGE_ORDER,
    StageAttestationError,
    exit_artifact_hash,
    load_exit,
    run_attestation_selftest,
    save_exit,
    sign_exit,
    verify_exit,
    verify_exit_for_entry,
)


def test_custody_selftest_sign_verify_and_export_blocked():
    result = custody_selftest(SoftwareStubCustodian())
    assert result["sign_verify_ok"] is True
    assert result["export_blocked"] is True
    assert result["satisfies_min_viable_exit"] is False


def test_custody_export_raises():
    custodian = SoftwareStubCustodian()
    with pytest.raises(KeyCustodyNonExportable):
        custodian.export_private_material()


def test_tpm_custodian_not_configured_for_sign():
    custodian = TpmHsmCustodian()
    with pytest.raises(Exception):
        custodian.sign(b"probe")


def test_create_custodian_defaults_to_software_stub():
    custodian = create_custodian()
    assert custodian.custody_mode == "SOFTWARE_STUB_DEV_ONLY"


def test_attestation_selftest_passes():
    result = run_attestation_selftest(SoftwareStubCustodian())
    assert result["cm4_sign_verify_ok"] is True
    assert result["c2_lineage_ok"] is True
    assert result["stale_h0_rejected"] is True
    assert result["mixed_lineage_rejected"] is True
    assert result["forgery_rejected"] is True
    assert result["non_promoting_emit_none"] is True


def test_sign_exit_round_trip_and_save_load(tmp_path: Path):
    custodian = SoftwareStubCustodian()
    artifact = sign_exit(
        stage_id="C-M4",
        run_mode="C-M4",
        run_nonce="nonce-001",
        d_mode_s=900,
        chain_tip="tip-001",
        authority_h0="sha256:h0",
        parent_exit_hash=GENESIS_PARENT_HASH,
        status="HARNESS_READY",
        custodian=custodian,
    )
    assert artifact is not None
    path = save_exit(tmp_path / "cm4_exit.json", artifact)
    loaded = load_exit(path)
    index = {exit_artifact_hash(loaded): loaded}
    verify_exit(loaded, custodian, exit_index=index, current_authority_h0="sha256:h0")


def test_stale_h0_rejected_at_entry():
    custodian = SoftwareStubCustodian()
    cm4 = sign_exit(
        stage_id="C-M4",
        run_mode="C-M4",
        run_nonce="nonce-001",
        d_mode_s=900,
        chain_tip="tip-001",
        authority_h0="sha256:h0-old",
        parent_exit_hash=GENESIS_PARENT_HASH,
        status="HARNESS_READY",
        custodian=custodian,
    )
    assert cm4 is not None
    index = {exit_artifact_hash(cm4): cm4}
    with pytest.raises(StageAttestationError):
        verify_exit_for_entry(cm4, "C-M4", custodian, "sha256:h0-new", index)


def test_non_promoting_status_emits_none():
    custodian = SoftwareStubCustodian()
    blocked = sign_exit(
        stage_id="C-M4",
        run_mode="C-M4",
        run_nonce="nonce-001",
        d_mode_s=900,
        chain_tip="tip-001",
        authority_h0="sha256:h0",
        parent_exit_hash=GENESIS_PARENT_HASH,
        status="BLOCKED",
        custodian=custodian,
    )
    assert blocked is None


def test_stage_order_matches_spec():
    assert STAGE_ORDER == ("C-M4", "C2", "C3", "C4", "M4")
