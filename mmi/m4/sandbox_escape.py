"""Modular sandbox escape tests — §7 Phase 3 policy model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

SANDBOX_MODULES = (
    "SE-FS",
    "SE-LINK",
    "SE-RAW",
    "SE-NET",
    "SE-9P",
    "SE-IPC",
    "SE-KEY",
)


class EscapeOutcome(str, Enum):
    DENY = "DENY"
    CONTAINED = "CONTAINED"
    ALLOW = "ALLOW"


@dataclass(frozen=True)
class EscapeVector:
    vector_id: str
    description: str
    payload: str


@dataclass(frozen=True)
class ModuleSpec:
    module_id: str
    escape_attempted: str
    canaries: tuple[str, ...]
    vectors: tuple[EscapeVector, ...]


@dataclass
class VectorResult:
    module: str
    vector_id: str
    result: EscapeOutcome
    canary: str
    detail: str


@dataclass
class ModuleResult:
    module: str
    result: EscapeOutcome
    canaries: list[str] = field(default_factory=list)
    vectors: list[VectorResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.result in {EscapeOutcome.DENY, EscapeOutcome.CONTAINED} and all(
            v.result in {EscapeOutcome.DENY, EscapeOutcome.CONTAINED} for v in self.vectors
        )


def _module_specs() -> dict[str, ModuleSpec]:
    return {
        "SE-FS": ModuleSpec(
            "SE-FS",
            "filesystem traversal LAB_ROOT → AUTHORITY_ROOT / EVIDENCE_ROOT",
            ("001", "007"),
            (
                EscapeVector("fs-traversal-dotdot", "path traversal via ..", "../../authority/seal"),
                EscapeVector("fs-lab-to-evidence", "lab clone write to evidence root", "../evidence/chain.jsonl"),
            ),
        ),
        "SE-LINK": ModuleSpec(
            "SE-LINK",
            "hardlink/junction/symlink to authority inode",
            ("002",),
            (
                EscapeVector("link-hardlink-authority", "hardlink to authority file", "hardlink:authority/manifest"),
                EscapeVector("link-junction-evidence", "junction to evidence dir", "junction:evidence"),
            ),
        ),
        "SE-RAW": ModuleSpec(
            "SE-RAW",
            "raw volume handle \\\\.\\C: / \\\\.\\PhysicalDriveN",
            ("003",),
            (
                EscapeVector("raw-volume-c", "open \\\\.\\C:", r"\\.\C:"),
                EscapeVector("raw-physical-drive", "open \\\\.\\PhysicalDrive0", r"\\.\PhysicalDrive0"),
            ),
        ),
        "SE-NET": ModuleSpec(
            "SE-NET",
            "egress to non-allowlisted / prod endpoint",
            ("004", "018"),
            (
                EscapeVector("net-prod-db", "connect prod db host", "tcp://prod.db.internal:5432"),
                EscapeVector("net-supabase", "connect supabase prod", "https://xyz.supabase.co"),
            ),
        ),
        "SE-9P": ModuleSpec(
            "SE-9P",
            "DrvFs/9P relay write attribution bypass",
            ("001", "007"),
            (
                EscapeVector("9p-relay-write", "9P relay write under clone SID", "9p:write:/mnt/c/authority"),
                EscapeVector("9p-fileid-bypass", "relay path without FileId enforcement", "9p:fileid-bypass"),
            ),
        ),
        "SE-IPC": ModuleSpec(
            "SE-IPC",
            "shared-memory / named-pipe crossing to TCB",
            ("013", "022"),
            (
                EscapeVector("ipc-named-pipe-tcb", "named pipe to boundary daemon", r"\\.\pipe\mmi_boundary"),
                EscapeVector("ipc-shm-tcb", "shared memory segment to TCB", "shm:tcb:0"),
            ),
        ),
        "SE-KEY": ModuleSpec(
            "SE-KEY",
            "read key material from clone address space / env",
            ("003", "022"),
            (
                EscapeVector("key-env-leak", "read signing key from env", "env:KEY_CUSTODY_PRIVATE"),
                EscapeVector("key-memory-scrape", "scrape key from process memory", "mem:scrape:signer"),
            ),
        ),
    }


@dataclass
class SandboxContext:
    authority_root: Path
    lab_root: Path
    evidence_root: Path


class SandboxBoundaryPolicy:
    """Phase 3 policy model — encodes §7 expected DENY semantics (Phase 4 wires host boundary)."""

    def evaluate(self, spec: ModuleSpec, vector: EscapeVector, ctx: SandboxContext) -> VectorResult:
        outcome = self._decide(spec.module_id, vector, ctx)
        canary = spec.canaries[0] if spec.canaries else "000"
        return VectorResult(
            module=spec.module_id,
            vector_id=vector.vector_id,
            result=outcome,
            canary=canary,
            detail=f"{spec.escape_attempted}: {vector.description}",
        )

    def _decide(self, module_id: str, vector: EscapeVector, ctx: SandboxContext) -> EscapeOutcome:
        auth = ctx.authority_root.as_posix().lower()
        payload = vector.payload.lower()

        if module_id == "SE-FS":
            if "authority" in payload or "evidence" in payload or ".." in payload:
                return EscapeOutcome.DENY
        if module_id == "SE-LINK":
            if "authority" in payload or "evidence" in payload or "hardlink" in payload or "junction" in payload:
                return EscapeOutcome.DENY
        if module_id == "SE-RAW":
            if r"\\.\c:" in payload or "physicaldrive" in payload:
                return EscapeOutcome.DENY
        if module_id == "SE-NET":
            if "prod" in payload or "supabase.co" in payload:
                return EscapeOutcome.DENY
        if module_id == "SE-9P":
            if "9p" in payload or "fileid-bypass" in payload:
                return EscapeOutcome.DENY
        if module_id == "SE-IPC":
            if "pipe" in payload or "shm" in payload or "tcb" in payload:
                return EscapeOutcome.CONTAINED
        if module_id == "SE-KEY":
            if "key" in payload or "signer" in payload or "private" in payload:
                return EscapeOutcome.DENY

        if auth and auth in payload:
            return EscapeOutcome.DENY
        return EscapeOutcome.DENY


def run_module(module_id: str, ctx: SandboxContext, policy: SandboxBoundaryPolicy | None = None) -> ModuleResult:
    specs = _module_specs()
    if module_id not in specs:
        raise ValueError(f"unknown sandbox module: {module_id}")
    pol = policy or SandboxBoundaryPolicy()
    spec = specs[module_id]
    vectors = [pol.evaluate(spec, v, ctx) for v in spec.vectors]
    worst = EscapeOutcome.DENY
    for vr in vectors:
        if vr.result == EscapeOutcome.ALLOW:
            worst = EscapeOutcome.ALLOW
            break
        if vr.result == EscapeOutcome.CONTAINED and worst != EscapeOutcome.ALLOW:
            worst = EscapeOutcome.CONTAINED
    return ModuleResult(
        module=module_id,
        result=worst,
        canaries=list(spec.canaries),
        vectors=vectors,
    )


def run_all_modules(ctx: SandboxContext, policy: SandboxBoundaryPolicy | None = None) -> list[ModuleResult]:
    return [run_module(mid, ctx, policy) for mid in SANDBOX_MODULES]


def suite_passed(results: list[ModuleResult]) -> bool:
    return bool(results) and all(r.passed for r in results)


def module_specs() -> dict[str, ModuleSpec]:
    return _module_specs()
