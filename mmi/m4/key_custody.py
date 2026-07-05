"""KEY_CUSTODY adapter — TPM/HSM target; software stub for dev/unit only (§2, §17 Phase 4A)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class KeyCustodyError(RuntimeError):
    """Custody operation failed."""


class KeyCustodyNonExportable(KeyCustodyError):
    """Private signing material must not leave the custodian."""


class TpmHsmCustodianUnavailable(KeyCustodyError):
    """TPM/HSM custodian required for min-viable exit but not available."""


CUSTODY_MODE_SOFTWARE_STUB = "SOFTWARE_STUB_DEV_ONLY"
CUSTODY_MODE_TPM_HSM = "TPM_HSM"
DEV_STUB_KEY_FILENAME = ".mmi_dev_custody_stub.key"


class KeyCustodian(Protocol):
    custody_mode: str
    key_id: str

    def sign(self, message: bytes) -> str: ...
    def verify(self, message: bytes, signature: str) -> bool: ...
    def export_private_material(self) -> bytes: ...
    def satisfies_min_viable_exit(self) -> bool: ...
    def selftest(self) -> dict[str, object]: ...


@dataclass
class SoftwareStubCustodian:
    """In-memory HMAC custodian for unit/dev tests only — not min-viable exit."""

    custody_mode: str = CUSTODY_MODE_SOFTWARE_STUB
    key_id: str = ""
    _key: bytes = b""

    def __post_init__(self) -> None:
        if not self._key:
            object.__setattr__(self, "_key", secrets.token_bytes(32))
        if not self.key_id:
            object.__setattr__(
                self,
                "key_id",
                hashlib.sha256(self._key).hexdigest()[:16],
            )

    @classmethod
    def from_key_file(cls, path: os.PathLike[str] | str) -> SoftwareStubCustodian:
        key = Path(path).read_bytes()
        if len(key) < 16:
            raise KeyCustodyError("dev stub key file too short")
        return cls(_key=key, key_id=hashlib.sha256(key).hexdigest()[:16])

    def sign(self, message: bytes) -> str:
        digest = hmac.new(self._key, message, hashlib.sha256).digest()
        return digest.hex()

    def verify(self, message: bytes, signature: str) -> bool:
        expected = self.sign(message)
        return hmac.compare_digest(expected, signature.lower())

    def export_private_material(self) -> bytes:
        raise KeyCustodyNonExportable(
            "KEY_CUSTODY private material is non-exportable (stub enforces for tests)"
        )

    def satisfies_min_viable_exit(self) -> bool:
        return False

    def selftest(self) -> dict[str, object]:
        message = b"mmi-key-custody-selftest"
        signature = self.sign(message)
        export_blocked = False
        try:
            self.export_private_material()
        except KeyCustodyNonExportable:
            export_blocked = True
        return {
            "custody_mode": self.custody_mode,
            "key_id": self.key_id,
            "sign_verify_ok": self.verify(message, signature),
            "export_blocked": export_blocked,
            "satisfies_min_viable_exit": self.satisfies_min_viable_exit(),
        }


@dataclass
class TpmHsmCustodian:
    """Placeholder for PC1 TPM/HSM — required for Phase 4 min-viable exit (4G)."""

    custody_mode: str = CUSTODY_MODE_TPM_HSM
    key_id: str = "tpm-hsm-unconfigured"

    def sign(self, message: bytes) -> str:
        raise TpmHsmCustodianUnavailable(
            "TPM/HSM KEY_CUSTODY not configured; use SOFTWARE_STUB for dev/unit only"
        )

    def verify(self, message: bytes, signature: str) -> bool:
        raise TpmHsmCustodianUnavailable("TPM/HSM KEY_CUSTODY not configured")

    def export_private_material(self) -> bytes:
        raise KeyCustodyNonExportable("TPM/HSM private material is non-exportable")

    def satisfies_min_viable_exit(self) -> bool:
        return False

    def selftest(self) -> dict[str, object]:
        return {
            "custody_mode": self.custody_mode,
            "key_id": self.key_id,
            "configured": False,
            "export_blocked": True,
            "satisfies_min_viable_exit": False,
            "note": "Configure TPM/HSM adapter before 4G min-viable exit",
        }


def dev_stub_key_path(evidence_boundary_dir: os.PathLike[str] | Path | None = None) -> Path | None:
    if env := os.environ.get("MMI_KEY_CUSTODY_STUB_FILE"):
        return Path(env).expanduser()
    if evidence_boundary_dir is not None:
        candidate = Path(evidence_boundary_dir) / DEV_STUB_KEY_FILENAME
        if candidate.exists():
            return candidate
    return None


def persist_dev_stub_key(custodian: KeyCustodian, evidence_boundary_dir: os.PathLike[str] | Path) -> Path | None:
    if not isinstance(custodian, SoftwareStubCustodian):
        return None
    path = Path(evidence_boundary_dir) / DEV_STUB_KEY_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(custodian._key)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path


def create_custodian(
    mode: str | None = None,
    *,
    evidence_boundary_dir: os.PathLike[str] | Path | None = None,
) -> KeyCustodian:
    selected = mode or os.environ.get("MMI_KEY_CUSTODY_MODE", CUSTODY_MODE_SOFTWARE_STUB)
    if selected == CUSTODY_MODE_TPM_HSM:
        return TpmHsmCustodian()
    if selected == CUSTODY_MODE_SOFTWARE_STUB:
        stub_path = dev_stub_key_path(evidence_boundary_dir)
        if stub_path is not None:
            return SoftwareStubCustodian.from_key_file(stub_path)
        return SoftwareStubCustodian()
    raise KeyCustodyError(f"unknown KEY_CUSTODY mode: {selected}")


def custody_selftest(custodian: KeyCustodian | None = None) -> dict[str, object]:
    custodian = custodian or create_custodian()
    return custodian.selftest()


def write_custody_selftest(path: str | os.PathLike[str], custodian: KeyCustodian | None = None) -> dict[str, object]:
    result = custody_selftest(custodian)
    target = os.fspath(path)
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return result
