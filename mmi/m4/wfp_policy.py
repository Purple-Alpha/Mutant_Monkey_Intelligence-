"""WFP egress policy engine — default-deny T7 (§8, §17 Phase 4E)."""

from __future__ import annotations
import re

import json
import os
import socket
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Mapping

from mmi.m4.authority_seal import SignedPolicyManifest, WfpPolicyConfig
from mmi.m4.boundary_daemon import load_policy_manifest

WFP_SCHEMA_V = "2026-07-05c"
WFP_ENGINE_NAME = "mmi_wfp"
WFP_EXPECTED_FILTER_COUNT = 4
RULE_T7_DENY = "M4-WFP-001-T7"
RULE_ALLOW_TELEMETRY = "M4-WFP-ALLOW-TELEMETRY"
RESIDUAL_RISK_LINK = "R-001"
WFP_ACCESS_DENIED_MARKERS = ("10013", "WSAEACCES", "Access is denied")


class EgressDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True)
class EgressEndpoint:
    host: str
    port: int
    protocol: str = "TCP"

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> EgressEndpoint:
        return cls(
            host=str(data["host"]),
            port=int(data["port"]),
            protocol=str(data.get("protocol", "TCP")).upper(),
        )

    def key(self) -> tuple[str, int, str]:
        return (self.host.lower(), self.port, self.protocol)


@dataclass(frozen=True)
class WfpPolicyVerdict:
    fixture_id: str | None
    destination: str
    protocol: str
    port: int
    decision: EgressDecision
    rule_id: str
    policy_hash: str
    expected_action: str
    observed_action: str
    observed_process: str = "policy_engine"
    observed_sid: str = "telemetry_only"

    def to_dict(self) -> dict[str, object]:
        return {
            "fixture_id": self.fixture_id,
            "destination": self.destination,
            "protocol": self.protocol,
            "port": self.port,
            "decision": self.decision.value,
            "rule_id": self.rule_id,
            "policy_hash": self.policy_hash,
            "expected_action": self.expected_action,
            "observed_action": self.observed_action,
            "observed_process": self.observed_process,
            "observed_sid": self.observed_sid,
        }


class WfpPolicyEngine:
    RULE_T7_DENY = RULE_T7_DENY
    RULE_ALLOW_TELEMETRY = RULE_ALLOW_TELEMETRY

    def __init__(self, policy: SignedPolicyManifest):
        self.policy = policy
        self.wfp_policy = policy.wfp_policy
        self._allowlist = tuple(
            EgressEndpoint.from_mapping(item) for item in self.wfp_policy.telemetry_egress_allowlist
        )

    @classmethod
    def from_manifest_file(cls, policy_manifest_path: Path) -> WfpPolicyEngine:
        return cls(load_policy_manifest(policy_manifest_path))

    @property
    def policy_hash(self) -> str:
        return self.policy.manifest_hash

    def is_allowlisted(self, host: str, port: int, protocol: str = "TCP") -> bool:
        endpoint = EgressEndpoint(host=host, port=port, protocol=protocol)
        return endpoint.key() in {item.key() for item in self._allowlist}

    def evaluate_egress(
        self,
        host: str,
        port: int,
        *,
        protocol: str = "TCP",
        fixture_id: str | None = None,
    ) -> WfpPolicyVerdict:
        decision = EgressDecision.ALLOW if self.is_allowlisted(host, port, protocol) else EgressDecision.DENY
        rule_id = self.RULE_ALLOW_TELEMETRY if decision is EgressDecision.ALLOW else self.RULE_T7_DENY
        expected = decision.value
        return WfpPolicyVerdict(
            fixture_id=fixture_id,
            destination=host,
            protocol=protocol.upper(),
            port=port,
            decision=decision,
            rule_id=rule_id,
            policy_hash=self.policy_hash,
            expected_action=expected,
            observed_action=expected,
        )


def _helper_path() -> Path:
    env = os.environ.get("MMI_WFP_HELPER_EXE")
    if env:
        path = Path(env)
        if path.exists():
            return path

    scratch_release = Path(r"C:\mmi_boundary_scratch\mmi_wfp_build\x64\Release\mmi_wfp_helper.exe")
    if scratch_release.exists():
        return scratch_release

    marker = Path(r"C:\mmi_boundary_scratch\mmi_wfp_build\helper_path.txt")
    if marker.exists():
        marked = Path(marker.read_text(encoding="utf-8").strip())
        if marked.exists():
            return marked

    repo = Path(__file__).resolve().parents[2]
    release = repo / "host_boundary" / "mmi_wfp" / "x64" / "Release" / "mmi_wfp_helper.exe"
    if release.exists():
        return release
    return scratch_release


def wfp_engine_state_path(evidence_dir: Path) -> Path:
    return evidence_dir / "wfp_engine_state.json"


def load_wfp_engine_state(evidence_dir: Path) -> dict[str, object] | None:
    path = wfp_engine_state_path(evidence_dir)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_live_source_context() -> dict[str, object]:
    if sys.platform != "win32":
        return {
            "platform": sys.platform,
            "process_name": Path(sys.executable).name,
            "sid": "non_windows",
            "app_container_name": None,
            "namespace_hint": "non_windows",
        }

    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                "$id=[System.Security.Principal.WindowsIdentity]::GetCurrent();"
                "$sid=$id.User.Value;"
                "$proc=(Get-Process -Id $PID).ProcessName;"
                "@{sid=$sid;process_name=$proc;app_container_name=$null;namespace_hint=($proc+'@'+$sid)} | ConvertTo-Json -Compress",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            payload = json.loads(result.stdout.strip())
            payload["platform"] = "win32"
            return payload
    except (OSError, json.JSONDecodeError):
        pass

    return {
        "platform": "win32",
        "process_name": Path(sys.executable).name,
        "sid": "unknown",
        "app_container_name": None,
        "namespace_hint": Path(sys.executable).name,
    }


def source_context_matches_policy(
    observed: Mapping[str, object],
    policy: SignedPolicyManifest,
) -> bool:
    """Match observed probe identity against signed manifest only (no mutable evidence override)."""
    wfp = policy.wfp_policy
    observed_sid = str(observed.get("sid", ""))
    observed_app = observed.get("app_container_name")

    if wfp.app_container_name:
        return str(observed_app or "") == wfp.app_container_name

    if not wfp.clone_sid:
        return False
    return observed_sid.upper() == wfp.clone_sid.upper()


def manifest_requires_clone_probe(policy: SignedPolicyManifest) -> bool:
    wfp = policy.wfp_policy
    return bool(wfp.clone_sid or wfp.app_container_name)


def _is_wfp_access_denied(error_message: str | None) -> bool:
    if not error_message:
        return False
    upper = error_message.upper()
    return any(marker.upper() in upper for marker in WFP_ACCESS_DENIED_MARKERS)


def wfp_loaded(engine_name: str = WFP_ENGINE_NAME, evidence_dir: Path | None = None) -> bool:
    del evidence_dir  # status must come from helper/BFE — not unsigned state files
    helper = _helper_path()
    if sys.platform == "win32" and helper.exists():
        try:
            result = subprocess.run(
                [str(helper), "status", "--json"],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                payload = json.loads(result.stdout)
                count = int(payload.get("filter_count") or 0)
                return (
                    payload.get("loaded") is True
                    and count >= WFP_EXPECTED_FILTER_COUNT
                    and str(payload.get("engine_name", engine_name)).lower() == engine_name.lower()
                )
        except (OSError, json.JSONDecodeError):
            return False
    return False


def run_clone_probe(
    host: str,
    port: int,
    *,
    expect: str,
    evidence_dir: Path,
    policy: SignedPolicyManifest,
    timeout_s: float = 3.0,
) -> dict[str, object]:
    """Run TCP probe under clone/probe identity via helper (not harness process)."""
    wfp = policy.wfp_policy
    if not wfp.clone_sid and not wfp.app_container_name:
        return {
            "ok": False,
            "reason": "manifest_missing_clone_target",
            "connect_succeeded": False,
            "wfp_deny_proven": False,
        }
    if not wfp.probe_account_name:
        return {
            "ok": False,
            "reason": "manifest_missing_probe_account",
            "connect_succeeded": False,
            "wfp_deny_proven": False,
        }

    config_path = evidence_dir / "wfp_install_config.json"
    helper = _helper_path()
    if sys.platform != "win32" or not helper.exists() or not config_path.exists():
        return {
            "ok": False,
            "reason": "helper_or_config_missing",
            "connect_succeeded": False,
            "wfp_deny_proven": False,
        }

    try:
        result = subprocess.run(
            [
                str(helper),
                "probe",
                "--config",
                str(config_path),
                "--host",
                host,
                "--port",
                str(port),
                "--expect",
                expect,
                "--timeout-ms",
                str(int(timeout_s * 1000)),
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0 and not result.stdout.strip():
            return {
                "ok": False,
                "reason": result.stderr.strip() or "probe_failed",
                "connect_succeeded": False,
                "wfp_deny_proven": False,
            }
        payload = json.loads(result.stdout.strip() or "{}")
        payload["ok"] = payload.get("ok", result.returncode == 0)
        return payload
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "reason": str(exc),
            "connect_succeeded": False,
            "wfp_deny_proven": False,
        }


def attempt_live_connect(
    host: str,
    port: int,
    *,
    timeout_s: float = 3.0,
    required_source_context: dict[str, object] | None = None,
) -> tuple[bool, str | None]:
    if required_source_context is not None:
        current = resolve_live_source_context()
        if current.get("sid") != required_source_context.get("sid"):
            return False, "source_context_mismatch"
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True, None
    except OSError as exc:
        return False, str(exc)


def append_wfp_deny_event(
    evidence_dir: Path,
    *,
    test_id: str,
    policy_hash: str,
    active_rule_snapshot: str,
    source_process: str,
    source_namespace_or_context: str,
    destination: str,
    protocol: str,
    expected_action: str,
    observed_action: str,
    rule_id: str,
    pass_fail: str,
    residual_risk_link: str = RESIDUAL_RISK_LINK,
    event_log_pointer: str | None = None,
    timestamp_source: str = "utc_system",
) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    seq_path = evidence_dir / "wfp_event_seq.txt"
    seq = 0
    if seq_path.exists():
        seq = int(seq_path.read_text(encoding="utf-8").strip() or "0")
    seq += 1
    seq_path.write_text(str(seq), encoding="utf-8")
    pointer = event_log_pointer or f"wfp_event_{seq}"
    event = {
        "test_id": test_id,
        "policy_hash": policy_hash,
        "active_rule_snapshot": active_rule_snapshot,
        "source_process": source_process,
        "source_namespace_or_context": source_namespace_or_context,
        "destination": destination,
        "protocol": protocol,
        "expected_action": expected_action,
        "observed_action": observed_action,
        "rule_id": rule_id,
        "event_log_pointer": pointer,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "timestamp_source": timestamp_source,
        "pass_fail": pass_fail,
        "residual_risk_link": residual_risk_link,
    }
    line = json.dumps(event, sort_keys=True, separators=(",", ":"))
    with (evidence_dir / "wfp_denies.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run_t7_contract_fixtures(engine: WfpPolicyEngine) -> dict[str, object]:
    t7_c1 = engine.evaluate_egress("127.0.0.1", 19998, fixture_id="T7-C1")
    allow = engine._allowlist[0]
    t7_c2 = engine.evaluate_egress(allow.host, allow.port, protocol=allow.protocol, fixture_id="T7-C2")
    t7_c3 = engine.evaluate_egress("127.0.0.1", 19999, fixture_id="T7-C3")
    return {
        "t7_c1_decision": t7_c1.decision.value,
        "t7_c2_decision": t7_c2.decision.value,
        "t7_c3_decision": t7_c3.decision.value,
        "verdicts": [t7_c1.to_dict(), t7_c2.to_dict(), t7_c3.to_dict()],
    }


def _start_telemetry_listener(host: str, port: int) -> tuple[threading.Thread, socket.socket, threading.Event]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)
    sock.settimeout(0.5)
    stop_event = threading.Event()

    def _serve() -> None:
        while not stop_event.is_set():
            try:
                conn, _addr = sock.accept()
                conn.close()
            except OSError:
                continue

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    return thread, sock, stop_event


def _stop_telemetry_listener(sock: socket.socket, stop_event: threading.Event) -> None:
    stop_event.set()
    sock.close()



def _wfp_5157_message_field(message: str, label: str) -> str | None:
    match = re.search(rf"(?im)^\s*{re.escape(label)}:\s*(.+?)\s*$", message)
    if not match:
        return None
    return match.group(1).strip()


def _find_security_5157_event(
    *,
    start_time: datetime,
    destination_address: str,
    destination_port: int,
    application_hint: str = "mmi_wfp_helper.exe",
) -> dict[str, object] | None:
    """Return matching Windows Security 5157 evidence for the deny probe, if available."""
    if os.name != "nt":
        return None

    start_literal = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    ps = f"""
$start = [datetime]::Parse('{start_literal}')
Get-WinEvent -FilterHashtable @{{LogName='Security'; Id=5157; StartTime=$start}} -MaxEvents 200 |
  ForEach-Object {{
    [pscustomobject]@{{
      TimeCreated = $_.TimeCreated.ToString('o')
      Id = $_.Id
      ProviderName = $_.ProviderName
      Message = $_.Message
    }}
  }} |
  ConvertTo-Json -Depth 4
"""

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    payload = result.stdout.strip()
    if result.returncode != 0 or not payload:
        return None

    try:
        events = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if isinstance(events, dict):
        events = [events]
    if not isinstance(events, list):
        return None

    for event in events:
        if not isinstance(event, dict):
            continue
        message = str(event.get("Message", ""))
        app_name = _wfp_5157_message_field(message, "Application Name") or ""
        direction = _wfp_5157_message_field(message, "Direction")
        dest_addr = _wfp_5157_message_field(message, "Destination Address")
        dest_port = _wfp_5157_message_field(message, "Destination Port")
        if application_hint.lower() not in app_name.lower():
            continue
        if direction != "Outbound":
            continue
        if dest_addr != destination_address:
            continue
        if dest_port != str(destination_port):
            continue

        return {
            "event_id": event.get("Id"),
            "event_time": event.get("TimeCreated"),
            "provider_name": event.get("ProviderName"),
            "application_name": app_name,
            "direction": direction,
            "source_address": _wfp_5157_message_field(message, "Source Address"),
            "source_port": _wfp_5157_message_field(message, "Source Port"),
            "destination_address": dest_addr,
            "destination_port": int(dest_port),
            "protocol": _wfp_5157_message_field(message, "Protocol"),
            "layer_name": _wfp_5157_message_field(message, "Layer Name"),
            "filter_run_time_id": _wfp_5157_message_field(message, "Filter Run-Time ID"),
            "is_loopback": (_wfp_5157_message_field(message, "Is Loopback") == "True"),
        }

    return None

def run_wfp_selftest(
    evidence_dir: Path,
    policy_manifest_path: Path,
    *,
    live: bool = False,
) -> dict[str, object]:
    engine = WfpPolicyEngine.from_manifest_file(policy_manifest_path)
    contract = run_t7_contract_fixtures(engine)
    contract_pass = (
        contract["t7_c1_decision"] == EgressDecision.DENY.value
        and contract["t7_c2_decision"] == EgressDecision.ALLOW.value
        and contract["t7_c3_decision"] == EgressDecision.DENY.value
    )

    loaded = wfp_loaded(evidence_dir=evidence_dir) if live else wfp_loaded(evidence_dir=evidence_dir)
    source_context_ok: bool | None = None
    live_t7_blocked: bool | None = None
    live_telemetry_ok: bool | None = None
    observed_source_context: dict[str, object] | None = None
    deny_probe: dict[str, object] | None = None
    allow_probe: dict[str, object] | None = None

    if live:
        if not manifest_requires_clone_probe(engine.policy):
            source_context_ok = False
            live_t7_blocked = False
            live_telemetry_ok = False
        elif not loaded:
            source_context_ok = False
            live_t7_blocked = False
            live_telemetry_ok = False
        else:
            allow = engine._allowlist[0]
            deny_host = "127.0.0.1"
            deny_port = 19999
            listener_sock: socket.socket | None = None
            listener_stop: threading.Event | None = None
            deny_listener_sock: socket.socket | None = None
            deny_listener_stop: threading.Event | None = None
            try:
                _thread, listener_sock, listener_stop = _start_telemetry_listener(allow.host, allow.port)
                _deny_thread, deny_listener_sock, deny_listener_stop = _start_telemetry_listener(
                    deny_host,
                    deny_port,
                )
                deny_probe_started_at = datetime.now().astimezone()
                deny_probe = run_clone_probe(
                    deny_host,
                    deny_port,
                    expect="deny",
                    evidence_dir=evidence_dir,
                    policy=engine.policy,
                )
                deny_security_event_5157 = _find_security_5157_event(
                    start_time=deny_probe_started_at,
                    destination_address=deny_host,
                    destination_port=deny_port,
                )
                deny_probe["windows_security_5157"] = deny_security_event_5157
                deny_probe["os_native_wfp_block_proven"] = deny_security_event_5157 is not None
                allow_probe = run_clone_probe(
                    allow.host,
                    allow.port,
                    expect="allow",
                    evidence_dir=evidence_dir,
                    policy=engine.policy,
                )
                observed_source_context = {
                    "sid": deny_probe.get("observed_sid"),
                    "process_name": deny_probe.get("observed_process"),
                    "app_container_name": deny_probe.get("observed_app_container"),
                    "namespace_hint": deny_probe.get("source_namespace_or_context"),
                    "probe_account": engine.policy.wfp_policy.probe_account_name,
                }
                source_context_ok = source_context_matches_policy(
                    observed_source_context,
                    engine.policy,
                )
                live_t7_blocked = (
                    source_context_ok
                    and deny_probe.get("wfp_deny_proven") is True
                    and deny_probe.get("connect_succeeded") is False
                )
                live_telemetry_ok = (
                    source_context_ok
                    and allow_probe.get("connect_succeeded") is True
                    and allow_probe.get("wfp_deny_proven") is False
                )
                if live_t7_blocked:
                    append_wfp_deny_event(
                        evidence_dir,
                        test_id="T7-L1",
                        policy_hash=engine.policy_hash,
                        active_rule_snapshot=str(
                            deny_probe.get("active_rule_snapshot", f"{RULE_T7_DENY}:default_deny")
                        ),
                        source_process=str(observed_source_context.get("process_name", "clone_probe")),
                        source_namespace_or_context=str(
                            observed_source_context.get("namespace_hint", "clone_probe")
                        ),
                        destination=f"{deny_host}:{deny_port}",
                        protocol="TCP",
                        expected_action="DENY",
                        observed_action="DENY",
                        rule_id=str(deny_probe.get("rule_id", RULE_T7_DENY)),
                        pass_fail="PASS",
                        event_log_pointer=str(deny_probe.get("event_log_pointer", "")),
                        timestamp_source=str(
                            deny_probe.get("timestamp_source", "wfp_audit_timestamp")
                        ),
                    )
                if source_context_ok and not live_telemetry_ok:
                    append_wfp_deny_event(
                        evidence_dir,
                        test_id="T7-L2",
                        policy_hash=engine.policy_hash,
                        active_rule_snapshot=str(
                            allow_probe.get(
                                "active_rule_snapshot",
                                f"{RULE_ALLOW_TELEMETRY}:{allow.host}:{allow.port}",
                            )
                        ),
                        source_process=str(observed_source_context.get("process_name", "clone_probe")),
                        source_namespace_or_context=str(
                            observed_source_context.get("namespace_hint", "clone_probe")
                        ),
                        destination=f"{allow.host}:{allow.port}",
                        protocol=allow.protocol,
                        expected_action="ALLOW",
                        observed_action="DENY",
                        rule_id=str(allow_probe.get("rule_id", RULE_ALLOW_TELEMETRY)),
                        pass_fail="FAIL",
                        event_log_pointer=str(allow_probe.get("event_log_pointer", "")),
                        timestamp_source=str(
                            allow_probe.get("timestamp_source", "wfp_audit_timestamp")
                        ),
                    )
            finally:
                if listener_sock is not None and listener_stop is not None:
                    _stop_telemetry_listener(listener_sock, listener_stop)
                if deny_listener_sock is not None and deny_listener_stop is not None:
                    _stop_telemetry_listener(deny_listener_sock, deny_listener_stop)

    min_viable_live_t7 = bool(
        live
        and loaded
        and source_context_ok is True
        and live_t7_blocked is True
        and live_telemetry_ok is True
        and contract_pass
    )

    return {
        "schema_v": WFP_SCHEMA_V,
        "mode": "live" if live else "contract",
        "wfp_loaded": loaded if live else False,
        "contract_pass": contract_pass,
        "source_context_ok": source_context_ok,
        "live_t7_blocked": live_t7_blocked,
        "live_telemetry_ok": live_telemetry_ok,
        "min_viable_live_t7": min_viable_live_t7,
        "contract": contract,
        "policy_hash": engine.policy_hash,
        "observed_source_context": observed_source_context,
        "deny_probe": deny_probe,
        "allow_probe": allow_probe,
    }
