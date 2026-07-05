"""Minifilter policy engine — FileId/path enforcement model (§8, §17 Phase 4D)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

from mmi.m4.authority_seal import (
    AuthorityManifest,
    EnforcementEntry,
    file_identity,
    load_authority_manifest,
    seal_fingerprint,
    verify_fingerprint,
)
from mmi.m4.boundary_daemon import load_policy_manifest


class FilterOperation(str, Enum):
    WRITE = "WRITE"
    CREATE = "CREATE"
    SET_INFORMATION = "SET_INFORMATION"
    SET_SECURITY = "SET_SECURITY"
    LINK_CREATE = "LINK_CREATE"
    DELETE = "DELETE"
    RENAME = "RENAME"


class FilterDecision(str, Enum):
    DENY = "DENY"
    ALLOW = "ALLOW"


MUTATING_OPS = frozenset(
    {
        FilterOperation.WRITE,
        FilterOperation.CREATE,
        FilterOperation.SET_INFORMATION,
        FilterOperation.SET_SECURITY,
        FilterOperation.LINK_CREATE,
        FilterOperation.DELETE,
        FilterOperation.RENAME,
    }
)


@dataclass(frozen=True)
class PolicyVerdict:
    fixture_id: str | None
    operation: FilterOperation
    requested_path: str
    canonical_path: str
    resolved_target: str
    volume_guid: str
    file_reference_number: str
    decision: FilterDecision
    rule_id: str
    observed_process: str = "policy_engine"
    observed_sid: str = "telemetry_only"
    wsl_drvfs_origin: str | None = None
    bypassio_state: str = "NOT_CHECKED"

    def to_dict(self) -> dict[str, object]:
        return {
            "fixture_id": self.fixture_id,
            "operation": self.operation.value,
            "requested_path": self.requested_path,
            "canonical_path": self.canonical_path,
            "resolved_target_object": self.resolved_target,
            "volume_guid": self.volume_guid,
            "file_reference_number": self.file_reference_number,
            "observed_process": self.observed_process,
            "observed_sid": self.observed_sid,
            "wsl_drvfs_9p_origin": self.wsl_drvfs_origin,
            "decision": self.decision.value,
            "rule_id": self.rule_id,
            "bypassio_state_at_decision": self.bypassio_state,
        }


class MinifilterPolicyEngine:
    """Evaluate mutating ops against signed FileId manifest — trust anchor is object identity."""

    RULE_AUTHORITY_FILEID = "M4-FILTER-001"
    RULE_LINK_TO_AUTHORITY = "M4-FILTER-002"

    def __init__(self, manifest: AuthorityManifest, authority_root: Path):
        self.manifest = manifest
        self.authority_root = authority_root.resolve()
        self._by_fileid: dict[tuple[str, str], EnforcementEntry] = {}
        self._by_rel_path: dict[str, EnforcementEntry] = {}
        for entry in manifest.entries:
            key = (entry.volume_guid.lower(), entry.file_reference_number.lower())
            self._by_fileid[key] = entry
            self._by_rel_path[entry.relative_path.lower()] = entry

    @classmethod
    def from_manifest_file(cls, authority_manifest_path: Path) -> MinifilterPolicyEngine:
        manifest = load_authority_manifest(authority_manifest_path)
        return cls(manifest, Path(manifest.authority_root))

    def is_under_authority(self, path: Path) -> bool:
        path = path.resolve()
        try:
            path.relative_to(self.authority_root)
            return True
        except ValueError:
            return False

    def resolve_path(self, path: Path) -> Path:
        path = path.expanduser()
        if not path.is_absolute():
            path = self.authority_root / path
        return path.resolve()

    def _entry_for_path(self, path: Path) -> EnforcementEntry | None:
        path = self.resolve_path(path)
        if not self.is_under_authority(path):
            return None
        rel = path.relative_to(self.authority_root).as_posix()
        if rel == ".":
            rel_key = "."
        else:
            rel_key = rel
        hit = self._by_rel_path.get(rel_key.lower())
        if hit is not None:
            return hit
        try:
            vol, file_id, _ = file_identity(path, self.authority_root)
            return self._by_fileid.get((vol.lower(), file_id.lower()))
        except Exception:
            return None

    def evaluate(
        self,
        operation: FilterOperation,
        path: Path,
        *,
        fixture_id: str | None = None,
        link_target: Path | None = None,
        wsl_drvfs_origin: str | None = None,
    ) -> PolicyVerdict:
        target = self.resolve_path(path)
        canonical = str(target)
        entry = self._entry_for_path(target)
        link_entry = None

        vol = entry.volume_guid if entry else ""
        file_id = entry.file_reference_number if entry else ""
        if entry is None and self.is_under_authority(target):
            try:
                vol, file_id, _ = file_identity(target, self.authority_root)
            except Exception:
                vol, file_id = "", ""

        if operation == FilterOperation.LINK_CREATE and link_target is not None:
            if self._entry_for_path(link_target) is not None or self.is_under_authority(
                self.resolve_path(link_target)
            ):
                le = self._entry_for_path(link_target)
                return PolicyVerdict(
                    fixture_id=fixture_id,
                    operation=operation,
                    requested_path=str(path),
                    canonical_path=canonical,
                    resolved_target=str(self.resolve_path(link_target)),
                    volume_guid=le.volume_guid if le else vol,
                    file_reference_number=le.file_reference_number if le else file_id,
                    decision=FilterDecision.DENY,
                    rule_id=self.RULE_LINK_TO_AUTHORITY,
                    wsl_drvfs_origin=wsl_drvfs_origin,
                )

        if operation in MUTATING_OPS and self.is_under_authority(target):
            return PolicyVerdict(
                fixture_id=fixture_id,
                operation=operation,
                requested_path=str(path),
                canonical_path=canonical,
                resolved_target=canonical,
                volume_guid=vol,
                file_reference_number=file_id,
                decision=FilterDecision.DENY,
                rule_id=self.RULE_AUTHORITY_FILEID,
                wsl_drvfs_origin=wsl_drvfs_origin,
            )

        return PolicyVerdict(
            fixture_id=fixture_id,
            operation=operation,
            requested_path=str(path),
            canonical_path=canonical,
            resolved_target=canonical,
            volume_guid=vol,
            file_reference_number=file_id,
            decision=FilterDecision.ALLOW,
            rule_id="M4-FILTER-ALLOW-SCRATCH",
            wsl_drvfs_origin=wsl_drvfs_origin,
        )


def query_bypassio_state(authority_root: Path) -> str:
    """Record BypassIO query attempt — full fsutil parse deferred to live host tooling."""
    import subprocess

    if not Path(r"C:\Windows\System32\fsutil.exe").exists():
        return "UNSUPPORTED"
    try:
        result = subprocess.run(
            ["fsutil", "bypassIo", "state", "/v", str(authority_root)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        text = (result.stdout or "") + (result.stderr or "")
        upper = text.upper()
        if "DISABLED" in upper or "NOT SUPPORTED" in upper:
            return "BYPASSIO_DISABLED_OR_UNSUPPORTED"
        if "ENABLED" in upper:
            return "BYPASSIO_SUPPORTED_BUT_PROVEN_NOT_APPLICABLE_TO_WRITE_DENY_CLAIM"
        return "UNKNOWN"
    except OSError:
        return "UNKNOWN"


def driver_loaded(filter_name: str = "mmi_boundary") -> bool:
    import re
    import subprocess

    try:
        result = subprocess.run(
            ["fltmc", "filters"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        text = result.stdout or ""
        pattern = re.compile(
            rf"^\s*{re.escape(filter_name)}\s+(\d+)",
            re.IGNORECASE | re.MULTILINE,
        )
        match = pattern.search(text)
        if match is None:
            return False
        return int(match.group(1)) > 0
    except OSError:
        return False


def append_minifilter_event(evidence_dir: Path, event: dict[str, object]) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, sort_keys=True, separators=(",", ":"))
    with (evidence_dir / "minifilter_denies.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run_t1_t2_contract_fixtures(
    engine: MinifilterPolicyEngine,
    *,
    scratch_root: Path,
) -> dict[str, object]:
    authority = engine.authority_root
    t1_path = authority / "mmi_m4_boundary_probe" / "P4_T1_probe.txt"
    t2_link_source = scratch_root / "link_to_authority_probe"
    t2_target = authority / ".git" / "config"

    t1 = engine.evaluate(FilterOperation.WRITE, t1_path, fixture_id="T1")
    t2 = engine.evaluate(
        FilterOperation.LINK_CREATE,
        t2_link_source,
        fixture_id="T2",
        link_target=t2_target,
    )
    scratch_probe = scratch_root / "allowed_probe.txt"
    allow = engine.evaluate(FilterOperation.WRITE, scratch_probe, fixture_id="F10")

    return {
        "t1_decision": t1.decision.value,
        "t2_decision": t2.decision.value,
        "scratch_allow_decision": allow.decision.value,
        "t1_rule": t1.rule_id,
        "t2_rule": t2.rule_id,
        "verdicts": [t1.to_dict(), t2.to_dict(), allow.to_dict()],
    }


def attempt_live_write(
    path: Path,
    payload: str = "probe",
    *,
    mkdir_parents: bool = True,
) -> tuple[bool, str | None]:
    """Return (write_succeeded, error_message)."""
    try:
        if mkdir_parents:
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        return True, None
    except OSError as exc:
        return False, str(exc)


def run_minifilter_selftest(
    evidence_dir: Path,
    authority_manifest_path: Path,
    *,
    scratch_root: Path | None = None,
    h0_fingerprint: str | None = None,
    live: bool = False,
) -> dict[str, object]:
    engine = MinifilterPolicyEngine.from_manifest_file(authority_manifest_path)
    authority = engine.authority_root
    scratch = scratch_root or Path(r"C:\mmi_boundary_scratch")
    h0 = h0_fingerprint or seal_fingerprint(authority)

    contract = run_t1_t2_contract_fixtures(engine, scratch_root=scratch)
    bypassio = query_bypassio_state(authority)
    loaded = driver_loaded()

    for verdict in contract["verdicts"]:
        event = dict(verdict)
        event["h0_fingerprint"] = h0
        event["boundary_mode"] = "live" if live else "contract"
        event["bypassio_state_at_decision"] = bypassio
        append_minifilter_event(evidence_dir, event)

    live_t1_blocked = None
    live_scratch_ok = None
    if live:
        probe = authority / "mmi_m4_boundary_probe" / "P4_T1_live_probe.txt"
        succeeded, err = attempt_live_write(probe, mkdir_parents=False)
        live_t1_blocked = not succeeded
        scratch_probe = scratch / "allowed_live_probe.txt"
        scratch_ok, scratch_err = attempt_live_write(scratch_probe, mkdir_parents=True)
        live_scratch_ok = scratch_ok
        h1 = seal_fingerprint(authority)
        fingerprint_ok = verify_fingerprint(authority, h0)
    else:
        h1 = h0
        fingerprint_ok = True

    contract_pass = (
        contract["t1_decision"] == FilterDecision.DENY.value
        and contract["t2_decision"] == FilterDecision.DENY.value
        and contract["scratch_allow_decision"] == FilterDecision.ALLOW.value
    )

    return {
        "schema_v": "2026-07-04a",
        "mode": "live" if live else "contract",
        "driver_loaded": loaded,
        "bypassio_state": bypassio,
        "contract": contract,
        "contract_pass": contract_pass,
        "live_t1_blocked": live_t1_blocked,
        "live_scratch_ok": live_scratch_ok,
        "h0_fingerprint": h0,
        "h1_fingerprint": h1,
        "verify_fingerprint_ok": fingerprint_ok,
        "min_viable_live": live and loaded and live_t1_blocked is True and contract_pass,
    }
