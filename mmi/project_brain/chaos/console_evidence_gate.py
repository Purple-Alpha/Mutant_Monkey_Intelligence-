"""Console evidence gate core — validate/sign logic (AGI §5 step 4)."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from console_fingerprint_ledger import DEFAULT_LEDGER_PATH, ledger_contains
from mmi_canonical_digest import canonical_json_bytes, canonical_object_digest, file_sha256_hex

CONSOLE_BIND = "127.0.0.1"
CONSOLE_PORT = 8767
BUNDLE_VERSION = "console_evidence_v1"
GATE_B_SUITE = "proof_gate_v2_console_bindings"
MANIFEST_DOMAIN = "mmi_console_signoff_v1"
REPLAY_WINDOW_MS = 300_000
MAX_CLOCK_SKEW_MS = 30_000
MAX_BUNDLE_BYTES = 1_048_576
MAX_SIG_B64_BYTES = 128
VALIDATE_TTL_MS = 900_000
GATE_B_MAX_AGE_MS = 86_400_000
AUDIT_ROOT = Path("/tmp/mmi_console_server")
SIGNOFF_DIR = AUDIT_ROOT / "signoff"
AUDIT_LOG_PATH = AUDIT_ROOT / "audit" / "console_audit.jsonl"
SIGN_SEQ_PATH = AUDIT_ROOT / "state" / "sign_seq.json"
CONSUMED_SET_PATH = AUDIT_ROOT / "state" / "consumed.jsonl"
OPERATOR_PUBKEY_PATH = AUDIT_ROOT / "keys" / "operator_ed25519.pub"
STAGING_DIR = AUDIT_ROOT / "staging"
VALIDATION_CACHE_PATH = AUDIT_ROOT / "state" / "validation_cache.json"

OPERATOR_ACTIONS = frozenset({"SIGN_PROMOTE", "SIGN_RESUME", "SIGN_ACK"})
TELEMETRY_DENYLIST = frozenset(
    {
        "afe_score",
        "axis_a_tier",
        "axis_b_tier",
        "overall_weapon_tier",
        "telemetry",
        "websocket_feed",
        "dashboard_health",
    }
)


@dataclass
class GateConfig:
    audit_root: Path = AUDIT_ROOT
    operator_pubkey_path: Path = OPERATOR_PUBKEY_PATH
    fingerprint_ledger_path: Path = DEFAULT_LEDGER_PATH
    authority_root: Path | None = None
    now_ms: int | None = None

    @property
    def signoff_dir(self) -> Path:
        return self.audit_root / "signoff"

    @property
    def staging_dir(self) -> Path:
        return self.audit_root / "staging"

    @property
    def audit_log_path(self) -> Path:
        return self.audit_root / "audit" / "console_audit.jsonl"

    @property
    def sign_seq_path(self) -> Path:
        return self.audit_root / "state" / "sign_seq.json"

    @property
    def consumed_set_path(self) -> Path:
        return self.audit_root / "state" / "consumed.jsonl"

    @property
    def validation_cache_path(self) -> Path:
        return self.audit_root / "state" / "validation_cache.json"


@dataclass
class ValidationResult:
    verdict: str
    reasons: list[str] = field(default_factory=list)
    bundle_id: str | None = None
    manifest_preview: dict[str, Any] | None = None
    manifest_hash_preview: str | None = None


def _now_ms(config: GateConfig) -> int:
    return config.now_ms if config.now_ms is not None else int(time.time() * 1000)


def _assert_audit_write(path: Path, config: GateConfig) -> Path:
    resolved = path.resolve()
    root = config.audit_root.resolve()
    if resolved != root and root not in resolved.parents:
        raise PermissionError(f"write outside audit root: {resolved}")
    return resolved


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _audit_prev_hash(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "0" * 64
    lines = path.read_text(encoding="utf-8").splitlines()
    last = lines[-1].encode("utf-8") if lines else b""
    return hashlib.sha256(last).hexdigest() if last else "0" * 64


def append_audit_line(config: GateConfig, event: str, payload: dict[str, Any]) -> None:
    path = _assert_audit_write(config.audit_log_path, config)
    path.parent.mkdir(parents=True, exist_ok=True)
    line_obj = {
        "ts_ms": _now_ms(config),
        "event": event,
        **payload,
        "prev_line_hash": _audit_prev_hash(path),
    }
    line = json.dumps(line_obj, sort_keys=True, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def verify_audit_chain(path: Path) -> bool:
    if not path.exists():
        return True
    prev = "0" * 64
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get("prev_line_hash") != prev:
            return False
        prev = hashlib.sha256(line.encode("utf-8")).hexdigest()
    return True


def compute_bundle_id(bundle: dict[str, Any]) -> str:
    copy = {k: v for k, v in bundle.items() if k != "bundle_id"}
    digest = canonical_object_digest(copy)
    return f"ceb-{digest[:16]}"


def _integers_only(obj: Any, path: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            errors.extend(_integers_only(val, f"{path}.{key}" if path else key))
    elif isinstance(obj, list):
        for idx, val in enumerate(obj):
            errors.extend(_integers_only(val, f"{path}[{idx}]"))
    elif isinstance(obj, float):
        errors.append(path or "root")
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, int):
        pass
    elif isinstance(obj, str):
        pass
    elif obj is None:
        errors.append(path or "root")
    return errors


def _load_gate_b_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _parse_timestamp_ms(summary: dict[str, Any]) -> int | None:
    if "timestamp_ms" in summary and isinstance(summary["timestamp_ms"], int):
        return summary["timestamp_ms"]
    return None


def build_manifest(
    bundle: dict[str, Any],
    *,
    sign_seq: int,
    signed_at_ms: int,
) -> dict[str, Any]:
    budget = bundle["budget_telemetry_snapshot"]
    return {
        "domain": MANIFEST_DOMAIN,
        "bundle_id": bundle["bundle_id"],
        "bundle_version": bundle["bundle_version"],
        "operator_action": bundle["operator_action"],
        "fix_id": bundle["fix_id"],
        "patch_hash": bundle["patch_hash"],
        "proof_of_fix_digest": bundle["proof_of_fix_ref"]["digest"],
        "proof_of_regression_digest": bundle["proof_of_regression_ref"]["digest"],
        "rollback_token_hash": bundle["rollback_token_hash"],
        "budget_snapshot_digest": canonical_object_digest(budget),
        "gate_b_summary_digest": bundle["gate_b_summary_digest"],
        "sign_seq": sign_seq,
        "signed_at_ms": signed_at_ms,
    }


def manifest_bytes(manifest: dict[str, Any]) -> bytes:
    deny = TELEMETRY_DENYLIST & set(manifest.keys())
    if deny:
        raise ValueError(f"telemetry fields in manifest: {sorted(deny)}")
    return canonical_json_bytes(manifest)


def manifest_hash(manifest: dict[str, Any]) -> str:
    return hashlib.sha256(manifest_bytes(manifest)).hexdigest()


def load_operator_pubkey(path: Path) -> Ed25519PublicKey:
    raw = path.read_bytes()
    if len(raw) != 32:
        raise ValueError("operator pubkey must be 32 raw bytes")
    return Ed25519PublicKey.from_public_bytes(raw)


def verify_signature(manifest: dict[str, Any], signature_b64: str, pubkey: Ed25519PublicKey) -> bool:
    try:
        sig = base64.b64decode(signature_b64)
        if len(sig) != 64:
            return False
        pubkey.verify(sig, manifest_bytes(manifest))
        return True
    except (InvalidSignature, ValueError):
        return False


def _get_sign_seq(config: GateConfig) -> int:
    data = _read_json(config.sign_seq_path)
    if not data:
        return 0
    return int(data.get("sign_seq", 0))


def _set_sign_seq(config: GateConfig, value: int) -> None:
    path = _assert_audit_write(config.sign_seq_path, config)
    _atomic_write_json(path, {"sign_seq": value})


def _stage_bundle(config: GateConfig, bundle_id: str, bundle: dict[str, Any]) -> None:
    path = _assert_audit_write(config.staging_dir / f"{bundle_id}.json", config)
    _atomic_write_json(path, bundle)


def _load_staged_bundle(config: GateConfig, bundle_id: str) -> dict[str, Any] | None:
    return _read_json(config.staging_dir / f"{bundle_id}.json")


def _save_validation_cache(config: GateConfig, bundle_id: str, checked_at_ms: int) -> None:
    cache = _read_json(config.validation_cache_path) or {}
    cache[bundle_id] = {"checked_at_ms": checked_at_ms, "verdict": "VALID"}
    path = _assert_audit_write(config.validation_cache_path, config)
    _atomic_write_json(path, cache)


def _validation_age_ok(config: GateConfig, bundle_id: str, now: int) -> bool:
    cache = _read_json(config.validation_cache_path) or {}
    entry = cache.get(bundle_id)
    if not entry:
        return False
    return now - int(entry.get("checked_at_ms", 0)) <= VALIDATE_TTL_MS


def validate_bundle(
    bundle: dict[str, Any],
    config: GateConfig,
    *,
    update_cache: bool = True,
) -> ValidationResult:
    reasons: list[str] = []
    now = _now_ms(config)

    try:
        raw = json.dumps(bundle, sort_keys=True).encode("utf-8")
        if len(raw) > MAX_BUNDLE_BYTES:
            reasons.append("BUNDLE_TOO_LARGE")
    except (TypeError, ValueError):
        reasons.append("MISSING_FIELD")
        return ValidationResult("REJECTED", reasons)

    if bundle.get("bundle_version") != BUNDLE_VERSION:
        reasons.append("BAD_VERSION")

    float_paths = _integers_only(bundle)
    if float_paths:
        reasons.append("MISSING_FIELD")

    summary_path = Path(bundle.get("gate_b_summary_path", ""))
    summary = _load_gate_b_summary(summary_path) if bundle.get("gate_b_summary_path") else None
    if summary is None:
        reasons.append("MISSING_FIELD")
        return ValidationResult("REJECTED", reasons)

    if summary.get("suite") != GATE_B_SUITE:
        reasons.append("BAD_GATE_B_SUITE")

    if summary.get("overall_gate_status") != "CLEAN":
        reasons.append("GATE_NOT_CLEAN")
    if not summary.get("authority_intact"):
        reasons.append("AUTHORITY_COMPROMISED")
    if summary.get("blockers"):
        reasons.append("GATE_NOT_CLEAN")

    expected_id = compute_bundle_id(bundle)
    if bundle.get("bundle_id") != expected_id:
        reasons.append("BUNDLE_ID_MISMATCH")

    staged = _load_staged_bundle(config, expected_id)
    if staged is not None and staged != bundle:
        reasons.append("BUNDLE_ID_CONFLICT")

    summary_digest = file_sha256_hex(summary_path)
    if bundle.get("gate_b_summary_digest") != summary_digest:
        reasons.append("CROSS_BIND_FAIL")

    ts_ms = _parse_timestamp_ms(summary)
    if ts_ms is None:
        reasons.append("MISSING_FIELD")
    elif now - ts_ms > GATE_B_MAX_AGE_MS or ts_ms > now + MAX_CLOCK_SKEW_MS:
        reasons.append("GATE_B_STALE")

    if bundle.get("fix_id") != summary.get("fix_id"):
        reasons.append("CROSS_BIND_FAIL")

    patch = summary.get("patch") or {}
    patch_path = Path(patch.get("patch_path", ""))
    patch_hash = patch.get("patch_hash")
    if not patch_path.exists() or not patch_hash:
        reasons.append("HASH_MISMATCH")
    else:
        recomputed = file_sha256_hex(patch_path)
        if recomputed != patch_hash or bundle.get("patch_hash") != patch_hash:
            reasons.append("HASH_MISMATCH")

    pof_digest = summary.get("proof_of_fix_digest")
    por_digest = summary.get("proof_of_regression_digest")
    if bundle.get("proof_of_fix_ref", {}).get("digest") != pof_digest:
        reasons.append("CROSS_BIND_FAIL")
    if bundle.get("proof_of_regression_ref", {}).get("digest") != por_digest:
        reasons.append("CROSS_BIND_FAIL")

    rollback = summary.get("rollback") or {}
    rollback_token = bundle.get("rollback_token_hash")
    if rollback_token != summary.get("authority_hash"):
        reasons.append("HASH_MISMATCH")
    if rollback_token != rollback.get("rollback_token_hash"):
        reasons.append("HASH_MISMATCH")

    prior_digest = rollback.get("prior_known_good_digest")
    if not prior_digest or not ledger_contains(prior_digest, config.fingerprint_ledger_path):
        reasons.append("FINGERPRINT_UNKNOWN")
    if not rollback_token or not ledger_contains(rollback_token, config.fingerprint_ledger_path):
        reasons.append("FINGERPRINT_UNKNOWN")

    summary_budget = summary.get("budget_telemetry_snapshot")
    bundle_budget = bundle.get("budget_telemetry_snapshot")
    if not summary_budget or bundle_budget != summary_budget:
        reasons.append("CROSS_BIND_FAIL")
    if bundle_budget and bundle_budget.get("run_id") != summary.get("run_id"):
        reasons.append("MISSING_FIELD")

    if bundle.get("operator_action") not in OPERATOR_ACTIONS:
        reasons.append("UNKNOWN_OPERATOR_ACTION")

    if reasons:
        return ValidationResult("REJECTED", sorted(set(reasons)), expected_id)

    _stage_bundle(config, expected_id, bundle)
    if update_cache:
        _save_validation_cache(config, expected_id, now)
    preview = build_manifest(bundle, sign_seq=_get_sign_seq(config) + 1, signed_at_ms=now)
    return ValidationResult(
        "VALID",
        [],
        expected_id,
        preview,
        manifest_hash(preview),
    )


def sign_bundle(
    sign_request: dict[str, Any],
    config: GateConfig,
    *,
    client: str = "127.0.0.1",
) -> tuple[str, list[str], dict[str, Any] | None]:
    reasons: list[str] = []
    now = _now_ms(config)
    bundle_id = sign_request.get("bundle_id")
    if not bundle_id:
        return "REJECTED", ["MISSING_FIELD"], None

    bundle = _load_staged_bundle(config, bundle_id)
    if bundle is None:
        return "REJECTED", ["MISSING_FIELD"], None

    if not _validation_age_ok(config, bundle_id, now):
        return "REJECTED", ["VALIDATION_EXPIRED"], None

    validation = validate_bundle(bundle, config, update_cache=False)
    if validation.verdict != "VALID":
        return "REJECTED", validation.reasons or ["MISSING_FIELD"], None

    sign_seq = int(sign_request.get("sign_seq", -1))
    expected_seq = _get_sign_seq(config) + 1
    if sign_seq != expected_seq:
        return "REJECTED", ["SEQ_NON_MONOTONIC"], None

    signed_at_ms = sign_request.get("signed_at_ms")
    if not isinstance(signed_at_ms, int):
        return "REJECTED", ["MISSING_FIELD"], None
    if signed_at_ms < now - REPLAY_WINDOW_MS or signed_at_ms > now + MAX_CLOCK_SKEW_MS:
        return "REJECTED", ["REPLAY_STALE"], None

    signoff_path = config.signoff_dir / f"console_signoff_record_{bundle_id}.json"
    if signoff_path.exists():
        return "REJECTED", ["ALREADY_SIGNED"], None

    sig_b64 = sign_request.get("signature_b64", "")
    if len(sig_b64) > MAX_SIG_B64_BYTES:
        return "REJECTED", ["SIG_INVALID"], None

    manifest = build_manifest(bundle, sign_seq=sign_seq, signed_at_ms=signed_at_ms)
    mh = manifest_hash(manifest)
    if sign_request.get("manifest_hash") != mh:
        return "REJECTED", ["MANIFEST_MISMATCH"], None

    if not config.operator_pubkey_path.exists():
        return "REJECTED", ["SIG_INVALID"], None

    pubkey = load_operator_pubkey(config.operator_pubkey_path)
    if not verify_signature(manifest, sig_b64, pubkey):
        return "REJECTED", ["SIG_INVALID"], None

    record = {
        "record_version": "console_signoff_v1",
        "bundle_id": bundle_id,
        "fix_id": bundle["fix_id"],
        "manifest": manifest,
        "manifest_hash": mh,
        "signature_b64": sig_b64,
        "operator_key_id": sign_request.get("operator_key_id", "matt-ed25519-01"),
        "sign_seq": sign_seq,
        "signed_at_ms": signed_at_ms,
        "verified_at_ms": now,
        "verdict": "ACCEPTED",
        "patch_hash": bundle["patch_hash"],
        "rollback_token_hash": bundle["rollback_token_hash"],
    }

    path = _assert_audit_write(signoff_path, config)
    _atomic_write_json(path, record)
    _set_sign_seq(config, sign_seq)

    append_audit_line(
        config,
        "SIGN",
        {
            "bundle_id": bundle_id,
            "verdict": "ACCEPTED",
            "reasons": [],
            "client": client,
            "sign_seq": sign_seq,
            "manifest_hash": mh,
        },
    )
    return "ACCEPTED", [], record


def review_bundle(bundle_id: str, config: GateConfig) -> dict[str, Any] | None:
    bundle = _load_staged_bundle(config, bundle_id)
    if bundle is None:
        return None
    summary = _load_gate_b_summary(Path(bundle["gate_b_summary_path"]))
    validation = validate_bundle(bundle, config)
    next_seq = _get_sign_seq(config) + 1
    now = _now_ms(config)
    manifest_fields = build_manifest(bundle, sign_seq=next_seq, signed_at_ms=now)
    return {
        "bundle": bundle,
        "gate_b_summary": summary,
        "diff_view": {
            "patch_path": (summary or {}).get("patch", {}).get("patch_path"),
            "pre_hash": (summary or {}).get("rollback", {}).get("prior_known_good_digest"),
            "post_hash": bundle.get("patch_hash"),
        },
        "validation": {
            "verdict": validation.verdict,
            "checked_at_ms": now,
            "reasons": validation.reasons,
        },
        "manifest_fields": manifest_fields,
        "next_sign_seq": next_seq,
        "manifest_hash": manifest_hash(manifest_fields),
    }
