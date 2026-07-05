"""
Metadata Ingress Gate — Three-Stream Security Policy Envelope (Ed25519).

STATUS: BUILD v1 — wire behind ChaosOrchestrator ingress before LLM parse.
Authority: Matt (Super). Date: 2026-07-01.

Turns metadata from passive documentation into an immutable, cryptographically
bound execution boundary. Every agent-to-agent packet is wrapped in an envelope
carrying three enforced streams:

  1. PROVENANCE  — per-agent Ed25519 signature + monotonic nonce + ms timestamp
                   (proves WHICH agent sent it; kills replay / MITM).
  2. LINEAGE     — origin lane + clearance + target capability, checked against
                   a policy table (READ_ONLY input CANNOT reach a WRITE action).
  3. VOLUMETRIC  — true UTF-8 byte size, key count, whitespace ratio, entropy,
                   with HARD caps that reject oversized / padded payloads.

Design rules that fix the common broken version of this gate:
  * Ed25519 (asymmetric), NOT HMAC. A verifier cannot forge a sender.
  * Signature covers a canonical manifest that BINDS the payload via sha256,
    so tampering the payload breaks the signature.
  * Volumetric caps are ENFORCED (reject), not merely recorded.
  * Lane policy is ENFORCED — the "READ_ONLY blocks delete DB" claim is real.
  * Anti-replay nonce is MONOTONIC and PERSISTED to disk (survives restart).
  * Send-side and verify-side state are separate objects (no nonce collision).
  * No broad `except Exception:` swallowing — failures return typed reasons.

Not a substitute for `action_integrity_gate.py` (business-action authority) or
`mmi_control_envelope.py` (agent-output invariants). This gate runs FIRST, at
ingress, and drops bad packets before any of those ever see the text.
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from math import log2
from pathlib import Path
from time import time_ns
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from canary_metadata_layer import CanaryMetadataLayer
from behavioral_fingerprint_layer import BehavioralFingerprintLayer
from cross_packet_correlation_layer import CrossPacketCorrelationLayer
from graph_topology_layer import LaneTransitionGraphLayer
from provenance_chain_depth_layer import ProvenanceChainDepthLayer
from temporal_rhythm_layer import TemporalRhythmLayer

try:
    from cryptolalia_lab_bridge import mirror_router_for_lab, route_gate_divert_to_mirror
except ImportError:
    mirror_router_for_lab = None  # type: ignore
    route_gate_divert_to_mirror = None  # type: ignore

# --------------------------------------------------------------------------- #
# Canonicalization + metrics (deterministic)                                   #
# --------------------------------------------------------------------------- #


def _canonical(obj: Any) -> bytes:
    """Deterministic, compact JSON bytes. Same input -> identical bytes."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha256_b64(data: bytes) -> str:
    import hashlib

    return base64.b64encode(hashlib.sha256(data).digest()).decode("ascii")


def _shannon_entropy(data: bytes) -> float:
    """Bits/byte. High => encrypted/obfuscated blob; low => padding."""
    if not data:
        return 0.0
    n = len(data)
    return -sum((c / n) * log2(c / n) for c in Counter(data).values())


def _whitespace_ratio(text: str) -> float:
    if not text:
        return 0.0
    return sum(1 for ch in text if ch.isspace()) / len(text)


# --------------------------------------------------------------------------- #
# Policy + limits                                                              #
# --------------------------------------------------------------------------- #

# origin_lane -> clearance_level -> {allowed target capabilities}
# A packet may only request a capability its lane+clearance is granted.
DEFAULT_LANE_POLICY: dict[str, dict[str, set[str]]] = {
    "USER_INPUT": {"RESTRICTED": {"READ_ONLY"}},
    "AGENT_TRUSTED": {"STANDARD": {"READ_ONLY", "WRITE"}},
    "SYSTEM_CORE": {"PRIVILEGED": {"READ_ONLY", "WRITE", "EXECUTE", "ADMIN"}},
}


@dataclass(frozen=True)
class VolumetricLimits:
    max_payload_bytes: int = 16_384        # hard cap: kills whitespace/markdown bombs
    max_key_count: int = 64                # structural fan-out cap
    max_whitespace_ratio: float = 0.40     # padding-attack cap
    max_entropy: float | None = None       # None = record only; set e.g. 7.5 to reject blobs
    max_envelope_bytes: int = 65_536       # raw string DoS guard (checked pre-parse)


@dataclass(frozen=True)
class TimeWindow:
    max_transit_ms: int = 5_000            # packet older than this is expired
    max_future_skew_ms: int = 2_000        # tolerate small clock skew ahead of us


class EnvelopeRejected(Exception):
    """Raised internally with a machine-readable reason code."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


class MirrorDimensionDivert(Exception):
    """Depth-layer anomaly — route to Mirror Dimension, not a hard signature failure."""

    def __init__(
        self,
        detail: str,
        payload: dict[str, Any],
        layer_result: dict[str, Any],
        *,
        error: str = "FINGERPRINT_ANOMALY",
        sender_id: str = "",
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.payload = payload
        self.layer_result = layer_result
        self.error = error
        self.sender_id = sender_id

    @property
    def fingerprint(self) -> dict[str, Any]:
        """Backward-compatible alias for layer_result."""
        return self.layer_result


# --------------------------------------------------------------------------- #
# Keyring                                                                      #
# --------------------------------------------------------------------------- #


class AgentKeyring:
    """Maps sender_id -> Ed25519 public key. The gate trusts only these."""

    def __init__(self) -> None:
        self._pub: dict[str, Ed25519PublicKey] = {}

    def register(self, sender_id: str, public_key_b64: str) -> None:
        raw = base64.b64decode(public_key_b64)
        self._pub[sender_id] = Ed25519PublicKey.from_public_bytes(raw)

    def register_key(self, sender_id: str, key: Ed25519PublicKey) -> None:
        self._pub[sender_id] = key

    def public_key(self, sender_id: str) -> Ed25519PublicKey | None:
        return self._pub.get(sender_id)

    def known(self, sender_id: str) -> bool:
        return sender_id in self._pub


def generate_agent_keypair() -> tuple[Ed25519PrivateKey, str]:
    """Return (private_key, public_key_b64) for registration in a keyring."""
    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(
        priv.public_key().public_bytes_raw()
    ).decode("ascii")
    return priv, pub_b64


# --------------------------------------------------------------------------- #
# Persistent monotonic nonce state                                            #
# --------------------------------------------------------------------------- #


class _NonceStore:
    """Per-sender last-accepted nonce, persisted atomically. Survives restart."""

    def __init__(self, path: Path | None) -> None:
        self.path = Path(path) if path else None
        self._state: dict[str, int] = {}
        if self.path and self.path.exists():
            try:
                self._state = {
                    str(k): int(v)
                    for k, v in json.loads(self.path.read_text()).items()
                }
            except (json.JSONDecodeError, ValueError, OSError):
                self._state = {}

    def last(self, sender_id: str) -> int:
        return self._state.get(sender_id, 0)

    def commit(self, sender_id: str, nonce: int) -> None:
        self._state[sender_id] = nonce
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(self._state, fh, sort_keys=True)
            os.replace(tmp, self.path)  # atomic
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)


# --------------------------------------------------------------------------- #
# Send side                                                                   #
# --------------------------------------------------------------------------- #


class AgentSigner:
    """Held by a sending agent. Seals payloads into signed envelopes."""

    def __init__(
        self,
        sender_id: str,
        private_key: Ed25519PrivateKey,
        nonce_state_path: Path | None = None,
    ) -> None:
        self.sender_id = sender_id
        self._priv = private_key
        self._nonces = _NonceStore(nonce_state_path)

    def public_key_b64(self) -> str:
        return base64.b64encode(
            self._priv.public_key().public_bytes_raw()
        ).decode("ascii")

    def seal(
        self,
        payload: dict[str, Any],
        *,
        origin_lane: str,
        clearance_level: str,
        target_capability: str,
        target_lane: str = "",
    ) -> str:
        canon_payload = _canonical(payload)
        nonce = self._nonces.last(self.sender_id) + 1

        metadata = {
            "provenance": {
                "sender_id": self.sender_id,
                "nonce": nonce,
                "timestamp_ms": time_ns() // 1_000_000,
            },
            "lineage": {
                "origin_lane": origin_lane,
                "target_lane": target_lane,
                "clearance_level": clearance_level,
                "target_capability": target_capability,
            },
            "volumetric": {
                "payload_byte_size": len(canon_payload),
                "payload_key_count": len(payload),
                "payload_sha256_b64": _sha256_b64(canon_payload),
                "whitespace_ratio": round(
                    _whitespace_ratio(canon_payload.decode("utf-8")), 4
                ),
                "entropy": round(_shannon_entropy(canon_payload), 4),
            },
        }

        # Signature covers the canonical metadata, which binds the payload via
        # its sha256. Alter either and verification fails.
        signature = self._priv.sign(_canonical(metadata))
        self._nonces.commit(self.sender_id, nonce)

        return json.dumps(
            {
                "metadata": metadata,
                "payload": payload,
                "envelope_signature": base64.b64encode(signature).decode("ascii"),
            }
        )


# --------------------------------------------------------------------------- #
# Verify side                                                                  #
# --------------------------------------------------------------------------- #


@dataclass
class MetadataIngressGate:
    keyring: AgentKeyring
    lane_policy: dict[str, dict[str, set[str]]] = field(
        default_factory=lambda: DEFAULT_LANE_POLICY
    )
    limits: VolumetricLimits = field(default_factory=VolumetricLimits)
    window: TimeWindow = field(default_factory=TimeWindow)
    nonce_state_path: Path | None = None
    fingerprint_state_path: Path | None = None
    correlation_state_path: Path | None = None
    rhythm_state_path: Path | None = None
    chain_depth_state_path: Path | None = None
    depth_layers_enabled: bool = True
    canary_layer: CanaryMetadataLayer | None = None
    graph_layer: LaneTransitionGraphLayer | None = None
    fingerprint_layer: BehavioralFingerprintLayer | None = None
    correlation_layer: CrossPacketCorrelationLayer | None = None
    rhythm_layer: TemporalRhythmLayer | None = None
    chain_depth_layer: ProvenanceChainDepthLayer | None = None
    mirror_lab_root: Path | None = None

    def __post_init__(self) -> None:
        self._nonces = _NonceStore(self.nonce_state_path)
        if self.depth_layers_enabled:
            if self.canary_layer is None:
                self.canary_layer = CanaryMetadataLayer()
            if self.graph_layer is None:
                self.graph_layer = LaneTransitionGraphLayer()
            if self.fingerprint_layer is None:
                self.fingerprint_layer = BehavioralFingerprintLayer(
                    state_path=self.fingerprint_state_path
                )
            if self.correlation_layer is None:
                self.correlation_layer = CrossPacketCorrelationLayer(
                    state_path=self.correlation_state_path
                )
            if self.rhythm_layer is None:
                self.rhythm_layer = TemporalRhythmLayer(
                    state_path=self.rhythm_state_path
                )
            if self.chain_depth_layer is None:
                self.chain_depth_layer = ProvenanceChainDepthLayer(
                    state_path=self.chain_depth_state_path
                )
        self._mirror_router = None
        if self.mirror_lab_root is not None and mirror_router_for_lab is not None:
            self._mirror_router = mirror_router_for_lab(self.mirror_lab_root)

    def _route_mirror_lab(self, sender_id: str, divert: MirrorDimensionDivert) -> dict[str, Any] | None:
        if self._mirror_router is None or route_gate_divert_to_mirror is None:
            return None
        detail = divert.detail
        if isinstance(divert.layer_result.get("detail"), dict):
            detail = divert.layer_result["detail"].get("reason", detail)
        return route_gate_divert_to_mirror(
            self._mirror_router,
            sender_id,
            error=divert.error,
            detail=detail,
            payload=divert.payload,
            layer_result=divert.layer_result,
        )

    # -- public API -------------------------------------------------------- #

    def admit(self, raw_envelope: str) -> tuple[bool, dict[str, Any]]:
        """
        Evaluate the metadata boundary FIRST. On any mismatch, drop the packet
        and return (False, {"error": CODE, ...}) before the payload is trusted.
        On success return (True, payload).
        """
        try:
            payload = self._admit_or_raise(raw_envelope)
            return True, payload
        except MirrorDimensionDivert as divert:
            detail = divert.detail
            if isinstance(divert.layer_result.get("detail"), dict):
                detail = divert.layer_result["detail"].get("reason", detail)
            mirror_route = None
            if self.mirror_lab_root is not None:
                mirror_route = self._route_mirror_lab(
                    divert.sender_id or "unknown_sender", divert
                )
            result: dict[str, Any] = {
                "error": divert.error,
                "route": "MIRROR_DIMENSION",
                "detail": detail,
                "verdict": divert.layer_result.get("verdict", "ANOMALY"),
                "payload": divert.payload,
            }
            if mirror_route is not None:
                result["cryptolalia"] = {
                    "routed": mirror_route.get("routed"),
                    "cryptolalia_bytes": mirror_route.get("cryptolalia_bytes", 0),
                    "mirror_cell": mirror_route.get("mirror_cell"),
                }
            return False, result
        except EnvelopeRejected as rej:
            return False, {"error": rej.code, "detail": rej.detail}

    # -- pipeline (fail-fast, cheapest-and-untrusted first) ---------------- #

    def _admit_or_raise(self, raw_envelope: str) -> dict[str, Any]:
        # 0. Raw DoS guard — before any parse, no trust required.
        if len(raw_envelope.encode("utf-8")) > self.limits.max_envelope_bytes:
            raise EnvelopeRejected("ENVELOPE_TOO_LARGE")

        # 0b. Layer 8 — honeytoken canary (pre-signature recon tripwire).
        if self.depth_layers_enabled and self.canary_layer is not None:
            canary_ok, canary_err = self.canary_layer.inspect_canaries(raw_envelope)
            if not canary_ok:
                raise EnvelopeRejected(
                    canary_err.get("error", "CANARY_TRIPPED"),
                    canary_err.get("detail", ""),
                )

        # 1. Parse structure.
        try:
            env = json.loads(raw_envelope)
            metadata = env["metadata"]
            payload = env["payload"]
            sig_b64 = env["envelope_signature"]
            prov = metadata["provenance"]
            lineage = metadata["lineage"]
            vol = metadata["volumetric"]
            sender_id = prov["sender_id"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise EnvelopeRejected("MALFORMED_ENVELOPE", str(exc)) from exc

        # 2. Known sender?
        pub = self.keyring.public_key(sender_id)
        if pub is None:
            raise EnvelopeRejected("UNKNOWN_SENDER", sender_id)

        # 3. Bind payload to signed metadata via hash (detects tampering).
        canon_payload = _canonical(payload)
        if _sha256_b64(canon_payload) != vol.get("payload_sha256_b64"):
            raise EnvelopeRejected("PAYLOAD_HASH_MISMATCH")

        # 4. Verify signature over canonical metadata. Metadata is trusted only
        #    after this line.
        try:
            pub.verify(base64.b64decode(sig_b64), _canonical(metadata))
        except (InvalidSignature, ValueError, TypeError) as exc:
            raise EnvelopeRejected("SIGNATURE_MISMATCH", str(exc)) from exc

        # 5. Chronology (metadata now trusted).
        now_ms = time_ns() // 1_000_000
        ts = int(prov["timestamp_ms"])
        if now_ms - ts > self.window.max_transit_ms:
            raise EnvelopeRejected("METADATA_EXPIRED", f"age={now_ms - ts}ms")
        if ts - now_ms > self.window.max_future_skew_ms:
            raise EnvelopeRejected("TIMESTAMP_IN_FUTURE", f"ahead={ts - now_ms}ms")

        # 6. Anti-replay: strictly increasing per sender, persisted.
        nonce = int(prov["nonce"])
        if nonce <= self._nonces.last(sender_id):
            raise EnvelopeRejected(
                "NONCE_REPLAY", f"nonce={nonce} last={self._nonces.last(sender_id)}"
            )

        # 7. Volumetric caps — ENFORCED, not just recorded.
        if len(canon_payload) > self.limits.max_payload_bytes:
            raise EnvelopeRejected("PAYLOAD_TOO_LARGE", f"{len(canon_payload)}B")
        if len(payload) > self.limits.max_key_count:
            raise EnvelopeRejected("TOO_MANY_KEYS", str(len(payload)))
        ws = _whitespace_ratio(canon_payload.decode("utf-8"))
        if ws > self.limits.max_whitespace_ratio:
            raise EnvelopeRejected("WHITESPACE_PADDING", f"ratio={ws:.3f}")
        if self.limits.max_entropy is not None:
            ent = _shannon_entropy(canon_payload)
            if ent > self.limits.max_entropy:
                raise EnvelopeRejected("ENTROPY_ANOMALY", f"entropy={ent:.3f}")

        # 8. Lineage lane-lock — the READ_ONLY-blocks-write guarantee.
        origin = lineage.get("origin_lane")
        clearance = lineage.get("clearance_level")
        capability = lineage.get("target_capability")
        allowed = self.lane_policy.get(origin, {}).get(clearance, set())
        if capability not in allowed:
            raise EnvelopeRejected(
                "LANE_VIOLATION",
                f"{origin}/{clearance} may not {capability}",
            )

        # 8b. Layer 6 — lane-transition graph (post-signature topology).
        if self.depth_layers_enabled and self.graph_layer is not None:
            graph_ok, graph_err = self.graph_layer.verify_transition_edge(metadata)
            if not graph_ok:
                raise EnvelopeRejected(
                    graph_err.get("error", "TOPOLOGY_VIOLATION"),
                    graph_err.get("detail", ""),
                )

        # 8c. Layer 4 — behavioral fingerprint (post-signature, after L6).
        if self.depth_layers_enabled and self.fingerprint_layer is not None:
            fp_ok, fp = self.fingerprint_layer.analyze_fingerprint(
                sender_id, metadata, payload
            )
            if not fp_ok:
                raise EnvelopeRejected(
                    fp.get("error", "FINGERPRINT_REJECTED"),
                    fp.get("detail", ""),
                )
            if fp.get("route") == "MIRROR_DIMENSION":
                raise MirrorDimensionDivert(
                    str(fp.get("detail", "")),
                    payload,
                    fp,
                    error="FINGERPRINT_ANOMALY",
                    sender_id=sender_id,
                )

        # 8d. Layer 5 — cross-packet correlation (post-L4, before nonce commit).
        if self.depth_layers_enabled and self.correlation_layer is not None:
            stream_ok, stream = self.correlation_layer.analyze_stream(
                sender_id, metadata, payload, int(prov["timestamp_ms"])
            )
            if not stream_ok:
                raise EnvelopeRejected(
                    stream.get("error", "STREAM_CORRELATION_REJECTED"),
                    str(stream.get("detail", "")),
                )
            if stream.get("route") == "MIRROR_DIMENSION":
                detail = stream.get("detail", {})
                reason = detail.get("reason", "") if isinstance(detail, dict) else str(detail)
                raise MirrorDimensionDivert(
                    reason,
                    payload,
                    stream,
                    error="STREAM_CORRELATION_ANOMALY",
                    sender_id=sender_id,
                )

        arrival_ts_ms = int(prov["timestamp_ms"])

        # 8e. Layer 7 — temporal rhythm (post-L5, before nonce commit).
        if self.depth_layers_enabled and self.rhythm_layer is not None:
            rhythm_ok, rhythm = self.rhythm_layer.analyze_rhythm(
                sender_id, metadata, payload, arrival_ts_ms
            )
            if not rhythm_ok:
                raise EnvelopeRejected(
                    rhythm.get("error", "RHYTHM_REJECTED"),
                    str(rhythm.get("detail", "")),
                )
            if rhythm.get("route") == "MIRROR_DIMENSION":
                detail = rhythm.get("detail", {})
                reason = detail.get("reason", "") if isinstance(detail, dict) else str(detail)
                raise MirrorDimensionDivert(
                    reason,
                    payload,
                    rhythm,
                    error="RHYTHM_ANOMALY",
                    sender_id=sender_id,
                )

        # 8f. Layer 9 - provenance chain depth (after L7, before nonce commit).
        if self.depth_layers_enabled and self.chain_depth_layer is not None:
            chain_ok, chain = self.chain_depth_layer.analyze_chain(
                sender_id,
                metadata,
                payload,
                ingress_lane=str(origin),
                routing_capability=str(capability),
                routing_target_lane=str(lineage.get("target_lane", "")),
                arrival_ts_ms=arrival_ts_ms,
            )
            if not chain_ok:
                raise EnvelopeRejected(
                    chain.get("error", "CHAIN_DEPTH_REJECTED"),
                    str(chain.get("detail", "")),
                )
            if chain.get("route") == "MIRROR_DIMENSION":
                detail = chain.get("detail", {})
                reason = detail.get("reason", "") if isinstance(detail, dict) else str(detail)
                raise MirrorDimensionDivert(
                    reason,
                    payload,
                    chain,
                    error="CHAIN_DEPTH_ANOMALY",
                    sender_id=sender_id,
                )

        # 9. Accept — commit nonce only after every check passes.
        self._nonces.commit(sender_id, nonce)
        return payload


__all__ = [
    "AgentKeyring",
    "AgentSigner",
    "MetadataIngressGate",
    "VolumetricLimits",
    "TimeWindow",
    "EnvelopeRejected",
    "MirrorDimensionDivert",
    "DEFAULT_LANE_POLICY",
    "generate_agent_keypair",
]
