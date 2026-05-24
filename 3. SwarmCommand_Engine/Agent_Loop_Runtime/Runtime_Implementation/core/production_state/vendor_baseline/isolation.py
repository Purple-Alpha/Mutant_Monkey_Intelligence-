"""Tenant-isolated SQLite connection management for the Vendor Baseline Store."""

from __future__ import annotations

import os
import re
import sqlite3
import stat
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from core.blackboard import GovernanceError


DATABASE_FILENAME = "vendor_baseline.sqlite"
_TENANT_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def validate_tenant_id(tenant_id: str) -> str:
    """Return a verified tenant id safe for use as a physical path segment."""

    if not isinstance(tenant_id, str) or not tenant_id:
        raise GovernanceError("tenant_id must be a non-empty string")
    if tenant_id != tenant_id.strip():
        raise GovernanceError("tenant_id must not contain leading or trailing whitespace")
    if ".." in tenant_id or "/" in tenant_id or "\\" in tenant_id:
        raise GovernanceError("tenant_id must not contain path traversal characters")
    if tenant_id.startswith(".") or tenant_id.endswith("."):
        raise GovernanceError("tenant_id must not start or end with a dot")
    if any(not char.isprintable() for char in tenant_id):
        raise GovernanceError("tenant_id must not contain non-printable characters")
    if not _TENANT_ID_RE.fullmatch(tenant_id):
        raise GovernanceError("tenant_id contains unsupported characters")
    return tenant_id


def tenant_directory_path(tenant_id: str, *, blackboard_root: Path | None = None) -> Path:
    root = Path(".") if blackboard_root is None else Path(blackboard_root)
    return root / "production_state" / validate_tenant_id(tenant_id)


def tenant_database_path(tenant_id: str, *, blackboard_root: Path | None = None) -> Path:
    return tenant_directory_path(tenant_id, blackboard_root=blackboard_root) / DATABASE_FILENAME


@contextmanager
def leased_connection(
    tenant_id: str,
    *,
    blackboard_root: Path | None = None,
) -> Iterator[sqlite3.Connection]:
    """Lease one SQLite connection bound exclusively to a verified tenant path."""

    path = tenant_database_path(tenant_id, blackboard_root=blackboard_root)
    existed = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    harden_path(path.parent, is_directory=True)
    if existed:
        harden_path(path, is_directory=False)

    conn = sqlite3.connect(path)
    try:
        harden_path(path, is_directory=False)
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    finally:
        conn.close()


def harden_path(path: Path, *, is_directory: bool) -> None:
    if sys.platform == "win32":
        _harden_path_windows(path)
        return
    mode = stat.S_IRWXU if is_directory else stat.S_IRUSR | stat.S_IWUSR
    os.chmod(path, mode)


def _harden_path_windows(path: Path) -> None:
    try:
        import ntsecuritycon as con  # type: ignore[import-not-found]
        import win32api  # type: ignore[import-not-found]
        import win32security  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised only on misconfigured Windows
        raise GovernanceError("pywin32 is required for Windows ACL hardening") from exc

    user_name = win32api.GetUserName()
    user_sid, _, _ = win32security.LookupAccountName(None, user_name)

    dacl = win32security.ACL()
    dacl.AddAccessAllowedAce(
        win32security.ACL_REVISION,
        con.GENERIC_READ | con.GENERIC_WRITE,
        user_sid,
    )

    security_info = (
        win32security.DACL_SECURITY_INFORMATION
        | win32security.PROTECTED_DACL_SECURITY_INFORMATION
    )
    win32security.SetNamedSecurityInfo(
        str(path),
        win32security.SE_FILE_OBJECT,
        security_info,
        None,
        None,
        dacl,
        None,
    )

