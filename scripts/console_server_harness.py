#!/usr/bin/env python3
"""Console server harness — T1/T2/T3 + H4/H6/H8/H10 scenarios."""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_AUTHORITY = Path("/mnt/c/Architectapp_clean")
HARNESS_EVIDENCE_DIR = Path("/tmp/mmi_console_server/harness")


def _ensure_paths(authority: Path) -> None:
    for p in (authority / "mmi/project_brain/chaos", authority / "scripts"):
        if p.exists() and str(p) not in sys.path:
            sys.path.insert(0, str(p))


def _reset_harness_audit_root(audit_root: Path) -> None:
    """Hermetic reset — same --evidence-dir must be re-runnable (Codex R2)."""
    audit_root.mkdir(parents=True, exist_ok=True)
    for child in list(audit_root.iterdir()):
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink(missing_ok=True)


def _route_body_field(app, path: str, method: str):
    for route in app.routes:
        if getattr(route, "path", None) != path:
            continue
        if method.upper() not in getattr(route, "methods", set()):
            continue
        return getattr(route, "body_field", None)
    return None


def asgi_http(app, method: str, path: str, json_body: dict[str, Any] | None = None):
    """In-process HTTP against a FastAPI app without Starlette TestClient."""
    import asyncio

    import httpx
    from httpx import ASGITransport

    async def _run():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            if method.upper() == "GET":
                return await client.get(path)
            return await client.post(path, json=json_body)

    return asyncio.run(_run())


def _http_smoke(cfg, authority: Path) -> tuple[str, str]:
    """Verify FastAPI routes accept JSON bodies via httpx ASGI transport."""
    try:
        import httpx  # noqa: F401
    except ImportError:
        return "FAIL", "FAIL"

    from console_server import create_app

    app = create_app(cfg)
    if _route_body_field(app, "/api/v1/evidence-bundle/validate", "POST") is None:
        return "FAIL", "FAIL"
    if _route_body_field(app, "/api/v1/evidence-bundle/sign", "POST") is None:
        return "FAIL", "FAIL"

    health = asgi_http(app, "GET", "/api/v1/health")
    validate = asgi_http(app, "POST", "/api/v1/evidence-bundle/validate", {"bundle_version": "bad"})
    health_ok = health.status_code == 200 and health.json().get("service") == "mmi_console_evidence_gate"
    validate_ok = validate.status_code == 422 and validate.json().get("verdict") == "REJECTED"
    return ("PASS" if health_ok else "FAIL", "PASS" if validate_ok else "FAIL")


def _keypair():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    priv = Ed25519PrivateKey.generate()
    return priv, priv.public_key().public_bytes_raw()


def _setup_env(evidence_dir: Path):
    from console_evidence_gate import GateConfig, build_manifest, manifest_hash, manifest_bytes, sign_bundle, validate_bundle
    from console_fingerprint_ledger import append_known_good
    from console_ack_adapter import ConsoleAckAdapter
    from mmi_canonical_digest import canonical_object_digest, file_sha256_hex

    audit_root = evidence_dir
    ledger_path = audit_root / "state" / "fingerprint_ledger.jsonl"
    pubkey_path = audit_root / "keys" / "operator_ed25519.pub"
    priv, pub_raw = _keypair()
    pubkey_path.parent.mkdir(parents=True, exist_ok=True)
    pubkey_path.write_bytes(pub_raw)

    genesis = "e" * 64
    append_known_good("GENESIS", genesis, "genesis_seed", 1_700_000_000_000, path=ledger_path)

    cfg = GateConfig(
        audit_root=audit_root,
        operator_pubkey_path=pubkey_path,
        fingerprint_ledger_path=ledger_path,
        now_ms=1_700_000_000_200,
    )
    return cfg, priv, validate_bundle, sign_bundle, build_manifest, manifest_hash, ConsoleAckAdapter, canonical_object_digest, file_sha256_hex


def _write_summary(
    evidence: Path,
    *,
    blocked: bool = False,
    tamper_patch: bool = False,
    run_id: str = "pg-harness-001",
    authority_hash: str = "e" * 64,
    fix_id: str = "harness_fix",
) -> Path:
    evidence.mkdir(parents=True, exist_ok=True)
    patch_path = evidence / "patch.diff"
    patch_path.write_text("harness-patch", encoding="utf-8")
    from mmi_canonical_digest import canonical_object_digest, file_sha256_hex

    patch_hash = file_sha256_hex(patch_path)
    if tamper_patch:
        patch_path.write_text("tampered", encoding="utf-8")

    proof_of_fix = {"verdict": "CONTAINED", "scenario_id": "h1"}
    proof_of_regression = {"verdict": "PASS", "runs": 1}
    summary = {
        "suite": "proof_gate_v2_console_bindings",
        "fix_id": fix_id,
        "run_id": run_id,
        "timestamp_ms": 1_700_000_000_000,
        "overall_gate_status": "BLOCKED" if blocked else "CLEAN",
        "authority_intact": True,
        "blockers": ["blocked"] if blocked else [],
        "authority_hash": authority_hash,
        "patch": {"patch_path": patch_path.as_posix(), "patch_hash": patch_hash, "patch_context": evidence.parent.as_posix()},
        "proof_of_fix": proof_of_fix,
        "proof_of_regression": proof_of_regression,
        "proof_of_fix_digest": canonical_object_digest(proof_of_fix),
        "proof_of_regression_digest": canonical_object_digest(proof_of_regression),
        "rollback": {
            "rollback_token_hash": authority_hash,
            "prior_known_good_run_id": "GENESIS",
            "prior_known_good_digest": "e" * 64,
        },
        "budget_telemetry_snapshot": {
            "run_id": run_id,
            "budget_spent": 0,
            "budget_cap_day": 8_000_000,
            "budget_cap_hour": 800_000,
            "deadman_armed": True,
            "captured_at_ms": 1_700_000_000_000,
        },
        "evidence_dir": evidence.as_posix(),
    }
    path = evidence / "proof_gate_summary.json"
    path.write_text(json.dumps(summary), encoding="utf-8")
    return path


def _bundle(summary_path: Path, file_sha256_hex, compute_bundle_id) -> dict:
    from console_evidence_gate import BUNDLE_VERSION, compute_bundle_id as cbi

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    bundle = {
        "bundle_version": BUNDLE_VERSION,
        "created_at_ms": 1_700_000_000_200,
        "operator_action": "SIGN_PROMOTE",
        "fix_id": summary["fix_id"],
        "gate_b_summary_path": summary_path.as_posix(),
        "gate_b_summary_digest": file_sha256_hex(summary_path),
        "patch_hash": summary["patch"]["patch_hash"],
        "proof_of_fix_ref": {
            "exploit_id": "h1",
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
    bundle["bundle_id"] = cbi(bundle)
    return bundle


def run_harness(authority: Path, evidence_dir: Path) -> dict[str, Any]:
    _ensure_paths(authority)
    _reset_harness_audit_root(evidence_dir)
    from console_evidence_gate import compute_bundle_id, manifest_bytes, verify_audit_chain
    from console_fingerprint_ledger import append_known_good
    from mmi_canonical_digest import file_sha256_hex

    cfg, priv, validate_bundle, sign_bundle, build_manifest, manifest_hash, ConsoleAckAdapter, _, fsha = _setup_env(
        evidence_dir
    )

    scenarios: dict[str, str] = {}

    # T1 — append current rollback token to ledger (V15) before validate
    t1_ev = evidence_dir / "t1"
    sp = _write_summary(t1_ev)
    summary_t1 = json.loads(sp.read_text(encoding="utf-8"))
    append_known_good(
        summary_t1["run_id"],
        summary_t1["authority_hash"],
        "proof_gate",
        1_700_000_000_001,
        path=cfg.fingerprint_ledger_path,
    )
    b = _bundle(sp, fsha, compute_bundle_id)
    vr = validate_bundle(b, cfg)
    manifest = vr.manifest_preview
    sig = base64.b64encode(priv.sign(manifest_bytes(manifest))).decode()
    sr = sign_bundle(
        {
            "bundle_id": b["bundle_id"],
            "sign_seq": 1,
            "signed_at_ms": cfg.now_ms,
            "manifest_hash": vr.manifest_hash_preview,
            "signature_b64": sig,
            "operator_key_id": "harness",
        },
        cfg,
    )
    scenarios["T1"] = "PASS" if vr.verdict == "VALID" and sr[0] == "ACCEPTED" else "FAIL"

    # T2a blocked
    sp2 = _write_summary(evidence_dir / "t2a", blocked=True)
    vr2 = validate_bundle(_bundle(sp2, fsha, compute_bundle_id), cfg)
    scenarios["T2a"] = "PASS" if vr2.verdict == "REJECTED" else "FAIL"

    # T2b tampered patch hash in bundle
    sp3 = _write_summary(evidence_dir / "t2b")
    b3 = _bundle(sp3, fsha, compute_bundle_id)
    b3["patch_hash"] = "f" * 64
    b3["bundle_id"] = compute_bundle_id({k: v for k, v in b3.items() if k != "bundle_id"})
    vr3 = validate_bundle(b3, cfg)
    scenarios["T2b"] = "PASS" if vr3.verdict == "REJECTED" else "FAIL"

    # T2c summary substitution — bundle cites stale summary path/digest
    sp2c = _write_summary(evidence_dir / "t2c_stale", run_id="pg-stale")
    b2c = _bundle(sp2c, fsha, compute_bundle_id)
    sp2c_current = _write_summary(evidence_dir / "t2c_current", run_id="pg-current")
    b2c["gate_b_summary_path"] = sp2c_current.as_posix()
    b2c["gate_b_summary_digest"] = fsha(sp2c_current)
    b2c["bundle_id"] = compute_bundle_id({k: v for k, v in b2c.items() if k != "bundle_id"})
    vr2c = validate_bundle(b2c, cfg)
    scenarios["T2c"] = "PASS" if vr2c.verdict == "REJECTED" and "CROSS_BIND_FAIL" in vr2c.reasons else "FAIL"

    # T2d older-green regression digest not in current summary
    sp2d = _write_summary(evidence_dir / "t2d")
    append_known_good("pg-t2d", summary_t1["authority_hash"], "proof_gate", 1_700_000_000_002, path=cfg.fingerprint_ledger_path)
    b2d = _bundle(sp2d, fsha, compute_bundle_id)
    b2d["proof_of_regression_ref"]["digest"] = "f" * 64
    b2d["bundle_id"] = compute_bundle_id({k: v for k, v in b2d.items() if k != "bundle_id"})
    vr2d = validate_bundle(b2d, cfg)
    scenarios["T2d"] = "PASS" if vr2d.verdict == "REJECTED" else "FAIL"

    # T2e/T2f HTTP smoke — httpx ASGI transport (Codex-safe; no Starlette TestClient)
    scenarios["T2e"], scenarios["T2f"] = _http_smoke(cfg, authority)

    # T3a replay sign
    sr_replay = sign_bundle(
        {
            "bundle_id": b["bundle_id"],
            "sign_seq": 1,
            "signed_at_ms": cfg.now_ms,
            "manifest_hash": vr.manifest_hash_preview,
            "signature_b64": sig,
            "operator_key_id": "harness",
        },
        cfg,
    )
    scenarios["T3a"] = "PASS" if sr_replay[0] == "REJECTED" else "FAIL"

    # T3b stale signed_at_ms
    sp3b = _write_summary(evidence_dir / "t3b", run_id="pg-t3b")
    append_known_good("pg-t3b", "e" * 64, "proof_gate", 1_700_000_000_003, path=cfg.fingerprint_ledger_path)
    b3b = _bundle(sp3b, fsha, compute_bundle_id)
    vr3b = validate_bundle(b3b, cfg)
    stale_ms = cfg.now_ms - 400_000
    manifest3b = vr3b.manifest_preview
    sig3b = base64.b64encode(priv.sign(manifest_bytes(manifest3b))).decode()
    sr3b = sign_bundle(
        {
            "bundle_id": b3b["bundle_id"],
            "sign_seq": 2,
            "signed_at_ms": stale_ms,
            "manifest_hash": vr3b.manifest_hash_preview,
            "signature_b64": sig3b,
            "operator_key_id": "harness",
        },
        cfg,
    )
    scenarios["T3b"] = "PASS" if sr3b[0] == "REJECTED" and "REPLAY_STALE" in sr3b[1] else "FAIL"

    # T3c manifest field swap — sign over SIGN_ACK manifest but request uses wrong hash
    sp3c = _write_summary(evidence_dir / "t3c", run_id="pg-t3c")
    append_known_good("pg-t3c", "e" * 64, "proof_gate", 1_700_000_000_004, path=cfg.fingerprint_ledger_path)
    b3c = _bundle(sp3c, fsha, compute_bundle_id)
    b3c["operator_action"] = "SIGN_ACK"
    b3c["bundle_id"] = compute_bundle_id({k: v for k, v in b3c.items() if k != "bundle_id"})
    vr3c = validate_bundle(b3c, cfg)
    manifest_promote = build_manifest(b3c, sign_seq=2, signed_at_ms=cfg.now_ms)
    manifest_promote["operator_action"] = "SIGN_PROMOTE"
    wrong_hash = manifest_hash(manifest_promote)
    sig3c = base64.b64encode(priv.sign(manifest_bytes(vr3c.manifest_preview))).decode()
    sr3c = sign_bundle(
        {
            "bundle_id": b3c["bundle_id"],
            "sign_seq": 2,
            "signed_at_ms": cfg.now_ms,
            "manifest_hash": wrong_hash,
            "signature_b64": sig3c,
            "operator_key_id": "harness",
        },
        cfg,
    )
    scenarios["T3c"] = "PASS" if sr3c[0] == "REJECTED" else "FAIL"

    # T3d bundle mutation under same bundle_id
    sp3d = _write_summary(evidence_dir / "t3d", run_id="pg-t3d")
    append_known_good("pg-t3d", "e" * 64, "proof_gate", 1_700_000_000_005, path=cfg.fingerprint_ledger_path)
    b3d = _bundle(sp3d, fsha, compute_bundle_id)
    validate_bundle(b3d, cfg)
    b3d_mut = dict(b3d)
    b3d_mut["patch_hash"] = "a" * 64
    vr3d = validate_bundle(b3d_mut, cfg)
    scenarios["T3d"] = "PASS" if vr3d.verdict == "REJECTED" and (
        "BUNDLE_ID_CONFLICT" in vr3d.reasons or "BUNDLE_ID_MISMATCH" in vr3d.reasons
    ) else "FAIL"

    # T3e adapter consume twice
    adapter = ConsoleAckAdapter(cfg)
    record_path = cfg.signoff_dir / f"console_signoff_record_{b['bundle_id']}.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    scenarios["T3e"] = "PASS" if adapter.consume(record) and not adapter.consume(record) else "FAIL"

    # H4 authority write refused
    from console_evidence_gate import _assert_audit_write

    try:
        _assert_audit_write(authority / "write_attempt.json", cfg)
        scenarios["H4"] = "FAIL"
    except PermissionError:
        scenarios["H4"] = "PASS"

    # H6 no private key under audit root
    scenarios["H6"] = "PASS"
    for p in evidence_dir.rglob("*"):
        if p.is_file() and p.suffix in {".key", ".pem"}:
            scenarios["H6"] = "FAIL"

    scenarios["H8"] = "PASS" if verify_audit_chain(cfg.audit_log_path) else "FAIL"

    source = (authority / "scripts/console_server.py").read_text(encoding="utf-8")
    scenarios["H10"] = "PASS" if "Ed25519PrivateKey" not in source else "FAIL"

    blockers = [k for k, v in scenarios.items() if v != "PASS"]
    overall = "CLEAN" if not blockers else "BLOCKED"
    summary = {
        "suite": "console_gate_v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenarios": scenarios,
        "overall_gate_status": overall,
        "blockers": blockers,
        "evidence_dir": evidence_dir.as_posix(),
    }
    (evidence_dir / "console_gate_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="MMI Console Server Harness")
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument("--evidence-dir", type=Path, default=HARNESS_EVIDENCE_DIR)
    args = parser.parse_args()
    if not args.authority.exists():
        print(json.dumps({"error": "authority not found"}), file=sys.stderr)
        return 2
    summary = run_harness(args.authority, args.evidence_dir)
    print(json.dumps(summary, indent=2))
    return 0 if summary["overall_gate_status"] == "CLEAN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
