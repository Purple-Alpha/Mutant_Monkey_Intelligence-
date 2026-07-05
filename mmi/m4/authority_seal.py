"""Authority H0 seal + signed policy manifest (§8 ENFORCEMENT_KEY, §17 Phase 4B)."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from mmi.m4.key_custody import KeyCustodian, persist_dev_stub_key
from mmi.m4.stage_attestation import canonical_payload_bytes, sign_bytes

MANIFEST_SCHEMA_V = "2026-07-04a"
H0_SEAL_SCHEMA_V = "2026-07-04a"
POLICY_MANIFEST_SCHEMA_V = "2026-07-05b"
ENFORCEMENT_KEY_KIND = "volume+FileId"
DEFAULT_TELEMETRY_EGRESS_ALLOWLIST: tuple[dict[str, object], ...] = (
    {"host": "127.0.0.1", "port": 9443, "protocol": "TCP"},
)

DEFAULT_EXCLUDE_DIR_NAMES = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        ".venv_kinetic",
        "node_modules",
    }
)


class AuthoritySealError(ValueError):
    """Manifest/seal invalid — fail-closed."""


@dataclass(frozen=True)
class EnforcementEntry:
    volume_guid: str
    file_reference_number: str
    relative_path: str
    is_directory: bool
    size: int
    mtime_ns: int
    identity_source: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> EnforcementEntry:
        return cls(
            volume_guid=str(data["volume_guid"]),
            file_reference_number=str(data["file_reference_number"]),
            relative_path=str(data["relative_path"]),
            is_directory=bool(data["is_directory"]),
            size=int(data["size"]),
            mtime_ns=int(data["mtime_ns"]),
            identity_source=str(data["identity_source"]),
        )


@dataclass(frozen=True)
class AuthorityManifest:
    schema_v: str
    authority_root: str
    enforcement_key: str
    entries: tuple[EnforcementEntry, ...]

    @property
    def manifest_hash(self) -> str:
        return compute_manifest_hash(self)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_v": self.schema_v,
            "authority_root": self.authority_root,
            "enforcement_key": self.enforcement_key,
            "manifest_hash": self.manifest_hash,
            "entry_count": len(self.entries),
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass(frozen=True)
class WfpPolicyConfig:
    telemetry_egress_allowlist: tuple[dict[str, object], ...]
    clone_sid: str | None = None
    app_container_name: str | None = None
    probe_account_name: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "telemetry_egress_allowlist": list(self.telemetry_egress_allowlist),
        }
        if self.clone_sid is not None:
            payload["clone_sid"] = self.clone_sid
        if self.app_container_name is not None:
            payload["app_container_name"] = self.app_container_name
        if self.probe_account_name is not None:
            payload["probe_account_name"] = self.probe_account_name
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, object] | None) -> WfpPolicyConfig:
        if not data:
            return cls.default_dev()
        allowlist_raw = data.get("telemetry_egress_allowlist")
        if not isinstance(allowlist_raw, list) or not allowlist_raw:
            return cls.default_dev()
        allowlist = tuple(dict(item) for item in allowlist_raw)  # type: ignore[arg-type]
        clone_sid = data.get("clone_sid")
        app_container_name = data.get("app_container_name")
        probe_account_name = data.get("probe_account_name")
        return cls(
            telemetry_egress_allowlist=allowlist,
            clone_sid=str(clone_sid) if clone_sid else None,
            app_container_name=str(app_container_name) if app_container_name else None,
            probe_account_name=str(probe_account_name) if probe_account_name else None,
        )

    @classmethod
    def default_dev(cls) -> WfpPolicyConfig:
        return cls(telemetry_egress_allowlist=DEFAULT_TELEMETRY_EGRESS_ALLOWLIST)


@dataclass(frozen=True)
class SignedH0Seal:
    schema_v: str
    authority_root: str
    h0_fingerprint: str
    manifest_hash: str
    h0_signature: str
    custody_key_id: str
    h0_signed_before_provision: bool
    sealed_at_utc: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SignedPolicyManifest:
    schema_v: str
    authority_root: str
    enforcement_key: str
    manifest_hash: str
    entry_count: int
    entries: tuple[EnforcementEntry, ...]
    custody_key_id: str
    policy_signature: str
    wfp_policy: WfpPolicyConfig = WfpPolicyConfig.default_dev()

    def unsigned_dict(self) -> dict[str, object]:
        return {
            "schema_v": self.schema_v,
            "authority_root": self.authority_root,
            "enforcement_key": self.enforcement_key,
            "manifest_hash": self.manifest_hash,
            "entry_count": self.entry_count,
            "entries": [entry.to_dict() for entry in self.entries],
            "custody_key_id": self.custody_key_id,
            "wfp_policy": self.wfp_policy.to_dict(),
        }

    def to_dict(self) -> dict[str, object]:
        payload = self.unsigned_dict()
        payload["policy_signature"] = self.policy_signature
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> SignedPolicyManifest:
        entries = tuple(EnforcementEntry.from_dict(item) for item in data["entries"])  # type: ignore[index]
        wfp_raw = data.get("wfp_policy")
        wfp_policy = WfpPolicyConfig.from_dict(wfp_raw if isinstance(wfp_raw, Mapping) else None)
        return cls(
            schema_v=str(data["schema_v"]),
            authority_root=str(data["authority_root"]),
            enforcement_key=str(data["enforcement_key"]),
            manifest_hash=str(data["manifest_hash"]),
            entry_count=int(data["entry_count"]),
            entries=entries,
            custody_key_id=str(data["custody_key_id"]),
            policy_signature=str(data["policy_signature"]),
            wfp_policy=wfp_policy,
        )


def _canonical_manifest_body(manifest: AuthorityManifest) -> dict[str, object]:
    return {
        "schema_v": manifest.schema_v,
        "authority_root": manifest.authority_root,
        "enforcement_key": manifest.enforcement_key,
        "entries": [entry.to_dict() for entry in manifest.entries],
    }


def compute_manifest_hash(manifest: AuthorityManifest) -> str:
    digest = hashlib.sha256(canonical_payload_bytes(_canonical_manifest_body(manifest))).hexdigest()
    return f"sha256:{digest}"


def seal_fingerprint(authority_root: os.PathLike[str] | str) -> str:
    """Return H0 authority baseline fingerprint (manifest hash)."""
    manifest = build_enforcement_manifest(authority_root)
    return manifest.manifest_hash


def _win_file_identity(path: Path) -> tuple[str, str, str]:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class FILE_ID_INFO(ctypes.Structure):
        _fields_ = [
            ("VolumeSerialNumber", wintypes.DWORD),
            ("FileId", wintypes.BYTE * 16),
        ]

    FileIdInfo = 18
    handle = kernel32.CreateFileW(
        str(path),
        0,
        7,  # FILE_SHARE_READ | WRITE | DELETE
        None,
        3,  # OPEN_EXISTING
        0x02000000,  # FILE_FLAG_BACKUP_SEMANTICS for directories
        None,
    )
    if handle == wintypes.HANDLE(-1).value:
        raise AuthoritySealError(f"CreateFileW failed for {path}")

    try:
        info = FILE_ID_INFO()
        ok = kernel32.GetFileInformationByHandleEx(
            handle,
            FileIdInfo,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if not ok:
            raise AuthoritySealError(f"GetFileInformationByHandleEx failed for {path}")
        volume_guid = f"vol-{info.VolumeSerialNumber:08x}"
        file_reference_number = info.FileId.hex()
        return volume_guid, file_reference_number, "win32_file_id"
    finally:
        kernel32.CloseHandle(handle)


def _dev_fallback_identity(path: Path, authority_root: Path) -> tuple[str, str, str]:
    stat = path.stat()
    rel = path.relative_to(authority_root).as_posix()
    body = f"{rel}|{stat.st_size}|{int(stat.st_mtime_ns)}|{'dir' if path.is_dir() else 'file'}"
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return "dev-volume", digest[:32], "dev_content_identity"


def file_identity(path: Path, authority_root: Path) -> tuple[str, str, str]:
    if sys.platform == "win32":
        try:
            return _win_file_identity(path)
        except (AuthoritySealError, OSError):
            pass
    return _dev_fallback_identity(path, authority_root)


def iter_authority_paths(
    authority_root: Path,
    *,
    exclude_dir_names: frozenset[str] = DEFAULT_EXCLUDE_DIR_NAMES,
) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(authority_root):
        current = Path(dirpath)
        dirnames[:] = sorted(name for name in dirnames if name not in exclude_dir_names)
        yield current
        for name in sorted(filenames):
            yield current / name


def build_enforcement_manifest(
    authority_root: os.PathLike[str] | str,
    *,
    exclude_dir_names: frozenset[str] = DEFAULT_EXCLUDE_DIR_NAMES,
    max_entries: int | None = None,
) -> AuthorityManifest:
    root = Path(authority_root).resolve()
    if not root.exists():
        raise AuthoritySealError(f"authority root missing: {root}")

    entries: list[EnforcementEntry] = []
    seen_paths: set[str] = set()
    for path in iter_authority_paths(root, exclude_dir_names=exclude_dir_names):
        rel = path.relative_to(root).as_posix()
        if rel == ".":
            rel_key = "."
        else:
            rel_key = rel
        if rel_key in seen_paths:
            continue
        seen_paths.add(rel_key)

        if path.is_symlink():
            continue

        stat = path.stat()
        volume_guid, file_reference_number, identity_source = file_identity(path, root)
        entries.append(
            EnforcementEntry(
                volume_guid=volume_guid,
                file_reference_number=file_reference_number,
                relative_path=rel_key,
                is_directory=path.is_dir(),
                size=0 if path.is_dir() else stat.st_size,
                mtime_ns=int(stat.st_mtime_ns),
                identity_source=identity_source,
            )
        )
        if max_entries is not None and len(entries) >= max_entries:
            break

    if not entries:
        raise AuthoritySealError("authority manifest empty")

    entries.sort(key=lambda item: item.relative_path)
    return AuthorityManifest(
        schema_v=MANIFEST_SCHEMA_V,
        authority_root=str(root),
        enforcement_key=ENFORCEMENT_KEY_KIND,
        entries=tuple(entries),
    )


def load_authority_manifest(path: Path) -> AuthorityManifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = tuple(EnforcementEntry.from_dict(item) for item in data["entries"])
    return AuthorityManifest(
        schema_v=str(data["schema_v"]),
        authority_root=str(data["authority_root"]),
        enforcement_key=str(data["enforcement_key"]),
        entries=entries,
    )


def sign_h0_seal(manifest: AuthorityManifest, custodian: KeyCustodian) -> SignedH0Seal:
    h0 = manifest.manifest_hash
    signature = custodian.sign(h0.encode("utf-8"))
    return SignedH0Seal(
        schema_v=H0_SEAL_SCHEMA_V,
        authority_root=manifest.authority_root,
        h0_fingerprint=h0,
        manifest_hash=h0,
        h0_signature=signature,
        custody_key_id=custodian.key_id,
        h0_signed_before_provision=True,
        sealed_at_utc=datetime.now(timezone.utc).isoformat(),
    )


def verify_h0_seal(seal: SignedH0Seal, custodian: KeyCustodian) -> None:
    if not seal.h0_signed_before_provision:
        raise AuthoritySealError("h0_signed_before_provision must be true for pre-provision seal")
    if seal.h0_fingerprint != seal.manifest_hash:
        raise AuthoritySealError("h0_fingerprint/manifest_hash mismatch in seal record")
    if not custodian.verify(seal.h0_fingerprint.encode("utf-8"), seal.h0_signature):
        raise AuthoritySealError("h0_signature invalid")


def sign_policy_manifest(
    manifest: AuthorityManifest,
    custodian: KeyCustodian,
    *,
    wfp_policy: WfpPolicyConfig | None = None,
) -> SignedPolicyManifest:
    wfp = wfp_policy or WfpPolicyConfig.default_dev()
    unsigned = {
        "schema_v": POLICY_MANIFEST_SCHEMA_V,
        "authority_root": manifest.authority_root,
        "enforcement_key": manifest.enforcement_key,
        "manifest_hash": manifest.manifest_hash,
        "entry_count": len(manifest.entries),
        "entries": [entry.to_dict() for entry in manifest.entries],
        "custody_key_id": custodian.key_id,
        "wfp_policy": wfp.to_dict(),
    }
    signature = sign_bytes(custodian, unsigned)
    return SignedPolicyManifest(
        schema_v=POLICY_MANIFEST_SCHEMA_V,
        authority_root=manifest.authority_root,
        enforcement_key=manifest.enforcement_key,
        manifest_hash=manifest.manifest_hash,
        entry_count=len(manifest.entries),
        entries=manifest.entries,
        custody_key_id=custodian.key_id,
        policy_signature=signature,
        wfp_policy=wfp,
    )


def verify_policy_manifest(
    signed: SignedPolicyManifest,
    custodian: KeyCustodian,
    *,
    current_manifest: AuthorityManifest | None = None,
) -> None:
    if signed.schema_v != POLICY_MANIFEST_SCHEMA_V:
        raise AuthoritySealError(f"unsupported policy schema: {signed.schema_v}")
    if not custodian.verify(
        canonical_payload_bytes(signed.unsigned_dict()),
        signed.policy_signature,
    ):
        raise AuthoritySealError("policy_signature invalid")
    if current_manifest is not None:
        if signed.manifest_hash != current_manifest.manifest_hash:
            raise AuthoritySealError("policy manifest_hash mismatch vs current authority state")
        if len(signed.entries) != len(current_manifest.entries):
            raise AuthoritySealError("policy entry_count mismatch vs current authority state")


def daemon_may_arm(
    signed: SignedPolicyManifest,
    custodian: KeyCustodian,
    current_manifest: AuthorityManifest,
) -> tuple[bool, str]:
    """Daemon arm gate — refuse on hash/signature mismatch (§8, 4C hook)."""
    try:
        verify_policy_manifest(signed, custodian, current_manifest=current_manifest)
    except AuthoritySealError as exc:
        return False, str(exc)
    return True, "policy_manifest_ok"


def verify_fingerprint(authority_root: os.PathLike[str] | str, expected_h0: str) -> bool:
    """VERIFY_FINGERPRINT helper — Hn == H0 (§14)."""
    return seal_fingerprint(authority_root) == expected_h0


def store_pre_provision_seal(
    evidence_dir: os.PathLike[str] | Path,
    authority_root: os.PathLike[str] | Path,
    custodian: KeyCustodian,
    *,
    wfp_policy: WfpPolicyConfig | None = None,
) -> dict[str, object]:
    manifest = build_enforcement_manifest(authority_root)
    h0_seal = sign_h0_seal(manifest, custodian)
    policy = sign_policy_manifest(manifest, custodian, wfp_policy=wfp_policy)

    verify_h0_seal(h0_seal, custodian)
    verify_policy_manifest(policy, custodian, current_manifest=manifest)

    boundary = Path(evidence_dir)
    boundary.mkdir(parents=True, exist_ok=True)

    manifest_path = boundary / "authority_manifest.json"
    h0_path = boundary / "h0_pre_provision_seal.json"
    policy_path = boundary / "policy_manifest.json"

    manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    h0_path.write_text(json.dumps(h0_seal.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    policy_path.write_text(json.dumps(policy.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    stub_key_path = persist_dev_stub_key(custodian, boundary)

    return {
        "manifest_hash": manifest.manifest_hash,
        "entry_count": len(manifest.entries),
        "h0_signed_before_provision": h0_seal.h0_signed_before_provision,
        "manifest_path": str(manifest_path),
        "h0_path": str(h0_path),
        "policy_path": str(policy_path),
        "dev_stub_key_path": str(stub_key_path) if stub_key_path else None,
    }


def run_authority_seal_selftest(
    authority_root: os.PathLike[str] | Path,
    custodian: KeyCustodian,
    *,
    max_entries: int | None = 200,
) -> dict[str, object]:
    manifest = build_enforcement_manifest(authority_root, max_entries=max_entries)
    h0 = manifest.manifest_hash
    policy = sign_policy_manifest(manifest, custodian)
    verify_policy_manifest(policy, custodian, current_manifest=manifest)

    mismatch_refused = False
    tampered = SignedPolicyManifest(
        schema_v=policy.schema_v,
        authority_root=policy.authority_root,
        enforcement_key=policy.enforcement_key,
        manifest_hash="sha256:deadbeef",
        entry_count=policy.entry_count,
        entries=policy.entries,
        custody_key_id=policy.custody_key_id,
        policy_signature=policy.policy_signature,
        wfp_policy=policy.wfp_policy,
    )
    try:
        verify_policy_manifest(tampered, custodian, current_manifest=manifest)
    except AuthoritySealError:
        mismatch_refused = True

    arm_ok, _ = daemon_may_arm(policy, custodian, manifest)
    arm_bad, _ = daemon_may_arm(tampered, custodian, manifest)

    h0_seal = sign_h0_seal(manifest, custodian)
    verify_h0_seal(h0_seal, custodian)

    rebuilt = build_enforcement_manifest(authority_root, max_entries=max_entries)
    fingerprint_stable = rebuilt.manifest_hash == h0
    full_fingerprint_ok: bool | None = None
    if max_entries is None:
        full_fingerprint_ok = verify_fingerprint(authority_root, h0)

    return {
        "schema_v": MANIFEST_SCHEMA_V,
        "entry_count": len(manifest.entries),
        "manifest_lists_fileids": all(
            entry.volume_guid and entry.file_reference_number for entry in manifest.entries
        ),
        "h0_fingerprint": h0,
        "h0_signed_before_provision": h0_seal.h0_signed_before_provision,
        "policy_sign_verify_ok": True,
        "hash_mismatch_refused": mismatch_refused,
        "daemon_arm_ok": arm_ok,
        "daemon_arm_refused_on_tamper": not arm_bad,
        "verify_fingerprint_ok": fingerprint_stable if max_entries is not None else bool(full_fingerprint_ok),
        "selftest_max_entries": max_entries,
    }
