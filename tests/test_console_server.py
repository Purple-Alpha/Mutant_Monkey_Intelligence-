from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

CHAOS = Path(__file__).resolve().parents[1] / "mmi" / "project_brain" / "chaos"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
for p in (CHAOS, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from console_ack_adapter import ConsoleAckAdapter  # noqa: E402
from console_evidence_gate import (
    BUNDLE_VERSION,
    GATE_B_SUITE,
    VALIDATE_TTL_MS,
    GateConfig,
    build_manifest,
    compute_bundle_id,
    manifest_bytes,
    manifest_hash,
    sign_bundle,
    validate_bundle,
    verify_audit_chain,
)
from console_fingerprint_ledger import append_known_good  # noqa: E402
from mmi_canonical_digest import canonical_object_digest, file_sha256_hex  # noqa: E402


@pytest.fixture
def gate_env(tmp_path: Path) -> tuple[GateConfig, Ed25519PrivateKey]:
    audit_root = tmp_path / "console"
    ledger_path = audit_root / "state" / "fingerprint_ledger.jsonl"
    pubkey_path = audit_root / "keys" / "operator_ed25519.pub"

    priv = Ed25519PrivateKey.generate()
    pubkey_path.parent.mkdir(parents=True, exist_ok=True)
    pubkey_path.write_bytes(priv.public_key().public_bytes_raw())

    genesis = "d" * 64
    append_known_good("GENESIS", genesis, "genesis_seed", 1_700_000_000_000, path=ledger_path)
    append_known_good("pg-fix1", genesis, "proof_gate", 1_700_000_000_050, path=ledger_path)

    cfg = GateConfig(
        audit_root=audit_root,
        operator_pubkey_path=pubkey_path,
        fingerprint_ledger_path=ledger_path,
        now_ms=1_700_000_000_100,
    )
    return cfg, priv


def _write_summary(evidence: Path, *, blocked: bool = False) -> Path:
    evidence.mkdir(parents=True, exist_ok=True)
    patch_path = evidence / "patch.diff"
    patch_path.write_text("patch-bytes", encoding="utf-8")
    patch_hash = file_sha256_hex(patch_path)
    proof_of_fix = {"verdict": "CONTAINED", "scenario_id": "s1"}
    proof_of_regression = {"verdict": "PASS", "runs": 1}
    summary = {
        "suite": GATE_B_SUITE,
        "fix_id": "fix1",
        "run_id": "pg-fix1-abc",
        "timestamp_ms": 1_700_000_000_000,
        "overall_gate_status": "BLOCKED" if blocked else "CLEAN",
        "authority_intact": True,
        "blockers": ["x"] if blocked else [],
        "authority_hash": "d" * 64,
        "patch": {
            "patch_path": patch_path.as_posix(),
            "patch_hash": patch_hash,
            "patch_context": evidence.parent.as_posix(),
        },
        "proof_of_fix": proof_of_fix,
        "proof_of_regression": proof_of_regression,
        "proof_of_fix_digest": canonical_object_digest(proof_of_fix),
        "proof_of_regression_digest": canonical_object_digest(proof_of_regression),
        "rollback": {
            "rollback_token_hash": "d" * 64,
            "prior_known_good_run_id": "GENESIS",
            "prior_known_good_digest": "d" * 64,
        },
        "budget_telemetry_snapshot": {
            "run_id": "pg-fix1-abc",
            "budget_spent": 0,
            "budget_cap_day": 8_000_000,
            "budget_cap_hour": 800_000,
            "deadman_armed": True,
            "captured_at_ms": 1_700_000_000_000,
        },
        "evidence_dir": evidence.as_posix(),
    }
    summary_path = evidence / "proof_gate_summary.json"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    return summary_path


def _build_bundle(summary_path: Path) -> dict:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    bundle = {
        "bundle_version": BUNDLE_VERSION,
        "created_at_ms": 1_700_000_000_100,
        "operator_action": "SIGN_PROMOTE",
        "fix_id": summary["fix_id"],
        "gate_b_summary_path": summary_path.as_posix(),
        "gate_b_summary_digest": file_sha256_hex(summary_path),
        "patch_hash": summary["patch"]["patch_hash"],
        "proof_of_fix_ref": {
            "exploit_id": "s1",
            "evidence_path": summary["evidence_dir"],
            "digest": summary["proof_of_fix_digest"],
        },
        "proof_of_regression_ref": {
            "suite": "proof_gate_v1",
            "verdict": "GREEN",
            "evidence_path": summary["evidence_dir"],
            "digest": summary["proof_of_regression_digest"],
        },
        "rollback_token_hash": summary["rollback"]["rollback_token_hash"],
        "budget_telemetry_snapshot": summary["budget_telemetry_snapshot"],
    }
    bundle["bundle_id"] = compute_bundle_id(bundle)
    return bundle


def _sign(priv: Ed25519PrivateKey, manifest: dict) -> str:
    sig = priv.sign(manifest_bytes(manifest))
    return base64.b64encode(sig).decode("ascii")


def test_console_server_no_signing_imports() -> None:
    source = (SCRIPTS / "console_server.py").read_text(encoding="utf-8")
    assert "Ed25519PrivateKey" not in source


def test_t1_clean_validate_and_sign(gate_env: tuple[GateConfig, Ed25519PrivateKey]) -> None:
    cfg, priv = gate_env
    summary_path = _write_summary(cfg.audit_root / "evidence")
    bundle = _build_bundle(summary_path)
    result = validate_bundle(bundle, cfg)
    assert result.verdict == "VALID"

    sign_req = {
        "bundle_id": bundle["bundle_id"],
        "sign_seq": 1,
        "signed_at_ms": cfg.now_ms,
        "manifest_hash": result.manifest_hash_preview,
        "signature_b64": _sign(priv, result.manifest_preview),
        "operator_key_id": "test-key",
    }
    verdict, reasons, record = sign_bundle(sign_req, cfg)
    assert verdict == "ACCEPTED"
    assert not reasons
    assert record is not None


def test_t2_blocked_summary_rejected(gate_env: tuple[GateConfig, Ed25519PrivateKey]) -> None:
    cfg, priv = gate_env
    summary_path = _write_summary(cfg.audit_root / "evidence2", blocked=True)
    bundle = _build_bundle(summary_path)
    result = validate_bundle(bundle, cfg)
    assert result.verdict == "REJECTED"
    assert "GATE_NOT_CLEAN" in result.reasons


def test_t3_replay_rejected(gate_env: tuple[GateConfig, Ed25519PrivateKey]) -> None:
    cfg, priv = gate_env
    summary_path = _write_summary(cfg.audit_root / "evidence3")
    bundle = _build_bundle(summary_path)
    validate_bundle(bundle, cfg)
    manifest = build_manifest(bundle, sign_seq=1, signed_at_ms=cfg.now_ms)
    sign_req = {
        "bundle_id": bundle["bundle_id"],
        "sign_seq": 1,
        "signed_at_ms": cfg.now_ms,
        "manifest_hash": manifest_hash(manifest),
        "signature_b64": _sign(priv, manifest),
        "operator_key_id": "test-key",
    }
    sign_bundle(sign_req, cfg)
    verdict, reasons, _ = sign_bundle(sign_req, cfg)
    assert verdict == "REJECTED"
    assert "ALREADY_SIGNED" in reasons or "SEQ_NON_MONOTONIC" in reasons


def test_adapter_consume_once(gate_env: tuple[GateConfig, Ed25519PrivateKey]) -> None:
    cfg, priv = gate_env
    summary_path = _write_summary(cfg.audit_root / "evidence4")
    bundle = _build_bundle(summary_path)
    result = validate_bundle(bundle, cfg)
    manifest = result.manifest_preview
    sign_req = {
        "bundle_id": bundle["bundle_id"],
        "sign_seq": 1,
        "signed_at_ms": cfg.now_ms,
        "manifest_hash": result.manifest_hash_preview,
        "signature_b64": _sign(priv, manifest),
        "operator_key_id": "test-key",
    }
    _, _, record = sign_bundle(sign_req, cfg)
    adapter = ConsoleAckAdapter(cfg)
    assert adapter.verify(record)
    assert adapter.consume(record)
    assert not adapter.consume(record)


def test_audit_chain(gate_env: tuple[GateConfig, Ed25519PrivateKey]) -> None:
    cfg, _ = gate_env
    summary_path = _write_summary(cfg.audit_root / "evidence5")
    validate_bundle(_build_bundle(summary_path), cfg)
    assert verify_audit_chain(cfg.audit_log_path)


def test_v15_rollback_token_must_be_in_ledger(gate_env: tuple[GateConfig, Ed25519PrivateKey]) -> None:
    cfg, _ = gate_env
    evidence = cfg.audit_root / "v15"
    summary_path = _write_summary(evidence)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["authority_hash"] = "a" * 64
    summary["rollback"]["rollback_token_hash"] = "a" * 64
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    bundle = _build_bundle(summary_path)
    result = validate_bundle(bundle, cfg)
    assert result.verdict == "REJECTED"
    assert "FINGERPRINT_UNKNOWN" in result.reasons


def test_sign_rejects_expired_validation_ttl(gate_env: tuple[GateConfig, Ed25519PrivateKey]) -> None:
    cfg, priv = gate_env
    summary_path = _write_summary(cfg.audit_root / "ttl")
    bundle = _build_bundle(summary_path)
    validate_bundle(bundle, cfg)
    cfg.now_ms = cfg.now_ms + VALIDATE_TTL_MS + 1
    sign_req = {
        "bundle_id": bundle["bundle_id"],
        "sign_seq": 1,
        "signed_at_ms": cfg.now_ms,
        "manifest_hash": "00" * 32,
        "signature_b64": "AA==",
        "operator_key_id": "test-key",
    }
    verdict, reasons, _ = sign_bundle(sign_req, cfg)
    assert verdict == "REJECTED"
    assert "VALIDATION_EXPIRED" in reasons


def test_console_server_validate_endpoint_accepts_json_body(tmp_path: Path) -> None:
    """HTTP Body wiring — httpx ASGI transport (avoids Starlette TestClient hang in Codex)."""
    from console_server import create_app  # noqa: E402
    from console_server_harness import asgi_http  # noqa: E402

    audit_root = tmp_path / "http_audit"
    cfg = GateConfig(audit_root=audit_root, authority_root=Path(__file__).resolve().parents[1])
    app = create_app(cfg)
    for path in ("/api/v1/evidence-bundle/validate", "/api/v1/evidence-bundle/sign"):
        route = next(r for r in app.routes if getattr(r, "path", None) == path)
        assert getattr(route, "body_field", None) is not None

    health = asgi_http(app, "GET", "/api/v1/health")
    assert health.status_code == 200
    assert health.json()["service"] == "mmi_console_evidence_gate"

    resp = asgi_http(app, "POST", "/api/v1/evidence-bundle/validate", {"bundle_version": "bad"})
    assert resp.status_code == 422
    data = resp.json()
    assert data.get("verdict") == "REJECTED"
    assert "reasons" in data


def test_console_server_rejects_non_loopback_host() -> None:
    import subprocess

    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "console_server.py"), "--host", "0.0.0.0", "--authority", str(SCRIPTS.parent)],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert "127.0.0.1" in result.stderr


def test_console_server_http_via_uvicorn_subprocess(tmp_path: Path) -> None:
    """Live loopback HTTP smoke — matches operator lab path; bounded shutdown."""
    import socket
    import subprocess
    import urllib.error
    import urllib.request

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    proc = subprocess.Popen(
        [
            sys.executable,
            str(SCRIPTS / "console_server.py"),
            "--port",
            str(port),
            "--authority",
            str(SCRIPTS.parent),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        health_url = f"http://127.0.0.1:{port}/api/v1/health"
        validate_url = f"http://127.0.0.1:{port}/api/v1/evidence-bundle/validate"
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(health_url, timeout=1) as resp:
                    if resp.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                if proc.poll() is not None:
                    raise AssertionError(f"console server exited early: {proc.stderr.read()}")
                time.sleep(0.1)
        else:
            raise AssertionError("console server did not become ready")

        with urllib.request.urlopen(health_url, timeout=2) as resp:
            assert json.loads(resp.read().decode())["service"] == "mmi_console_evidence_gate"

        req = urllib.request.Request(
            validate_url,
            data=json.dumps({"bundle_version": "bad"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=2)
            raise AssertionError("expected 422 from validate endpoint")
        except urllib.error.HTTPError as exc:
            assert exc.code == 422
            body = json.loads(exc.read().decode())
            assert body.get("verdict") == "REJECTED"
            assert "reasons" in body
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
