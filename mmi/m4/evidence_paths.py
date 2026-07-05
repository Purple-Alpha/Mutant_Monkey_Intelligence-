"""EVIDENCE_ROOT resolution — must stay outside AUTHORITY_ROOT (§2, §13, H-EVID-001)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

DEFAULT_EVIDENCE_ROOT_WIN = Path("C:/mmi_m4_evidence")
DEFAULT_EVIDENCE_ROOT_POSIX = Path("/var/mmi_m4_evidence")
REVIEW_FALLBACK_DIRNAME = "m4_evidence_root"


class EvidencePathError(ValueError):
    """EVIDENCE_ROOT violates authority boundary or is not writable."""


def default_evidence_root() -> Path:
    return evidence_root_candidates()[0]


def evidence_root_candidates() -> list[Path]:
    env = os.environ.get("MMI_EVIDENCE_ROOT")
    if env:
        return [Path(env).expanduser()]

    roots: list[Path] = []

    def add(path: Path) -> None:
        expanded = path.expanduser()
        if expanded not in roots:
            roots.append(expanded)

    if sys.platform == "win32":
        add(DEFAULT_EVIDENCE_ROOT_WIN)
        if local := os.environ.get("LOCALAPPDATA"):
            add(Path(local) / "mmi_m4_evidence")
        if temp := os.environ.get("TEMP"):
            add(Path(temp) / REVIEW_FALLBACK_DIRNAME)
        add(Path.home() / "AppData" / "Local" / REVIEW_FALLBACK_DIRNAME)
    else:
        add(DEFAULT_EVIDENCE_ROOT_POSIX)
        # WSL/Linux host with Windows evidence volume (PC1 dual-path)
        add(Path("/mnt/c/mmi_m4_evidence"))
        if xdg_state := os.environ.get("XDG_STATE_HOME"):
            add(Path(xdg_state) / "mmi_m4_evidence")
        add(Path.home() / ".local" / "state" / "mmi_m4_evidence")
        add(Path.home() / ".cache" / "mmi_m4_evidence")
        if tmpdir := os.environ.get("TMPDIR"):
            add(Path(tmpdir) / REVIEW_FALLBACK_DIRNAME)
        add(Path(tempfile.gettempdir()) / REVIEW_FALLBACK_DIRNAME)

    return roots


def is_under_authority(path: Path, authority_root: Path) -> bool:
    path = path.resolve()
    authority = authority_root.resolve()
    if path == authority:
        return True
    try:
        path.relative_to(authority)
        return True
    except ValueError:
        return False


def forbidden_tmp_evidence_path(path: Path) -> bool:
    posix = path.as_posix().lower()
    return "/tmp" in posix and "mmi" in posix


def validate_evidence_dir(evidence_dir: Path, authority_root: Path) -> None:
    if is_under_authority(evidence_dir, authority_root):
        raise EvidencePathError(
            f"EVIDENCE_ROOT must be outside AUTHORITY_ROOT; got {evidence_dir} under {authority_root}"
        )
    if forbidden_tmp_evidence_path(evidence_dir):
        raise EvidencePathError("EVIDENCE_ROOT must not use forbidden /tmp evidence paths (H-EVID-001)")


def validate_fuzz_dir(fuzz_dir: Path, authority_root: Path) -> None:
    validate_evidence_dir(fuzz_dir, authority_root)


def is_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".mmi_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def resolve_evidence_subdir(
    subdir: str,
    evidence_arg: Path | None,
    authority_root: Path,
) -> Path:
    authority = authority_root.resolve()

    if evidence_arg is not None:
        target = evidence_arg.expanduser().resolve()
        validate_evidence_dir(target, authority)
        if not is_writable_dir(target):
            raise EvidencePathError(f"EVIDENCE_ROOT/{subdir} is not writable: {target}")
        return target

    candidates: list[Path] = []
    for root in evidence_root_candidates():
        target = root.expanduser().resolve() / subdir
        if is_under_authority(target, authority):
            continue
        if forbidden_tmp_evidence_path(target):
            continue
        if target.exists() and (target / "policy_manifest.json").exists():
            return target
        if is_writable_dir(target):
            candidates.append(target)

    if candidates:
        return candidates[0]

    raise EvidencePathError(
        f"no writable EVIDENCE_ROOT/{subdir} outside AUTHORITY_ROOT; "
        "set MMI_EVIDENCE_ROOT or pass --evidence <path>"
    )


def resolve_fuzz_evidence_dir(evidence_arg: Path | None, authority_root: Path) -> Path:
    return resolve_evidence_subdir("fuzz", evidence_arg, authority_root)


def resolve_sandbox_evidence_dir(evidence_arg: Path | None, authority_root: Path) -> Path:
    return resolve_evidence_subdir("sandbox", evidence_arg, authority_root)


def resolve_boundary_evidence_dir(evidence_arg: Path | None, authority_root: Path) -> Path:
    return resolve_evidence_subdir("boundary", evidence_arg, authority_root)
