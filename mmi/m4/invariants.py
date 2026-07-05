"""§5 formal invariant suite — static checks (Phase 1) and live stubs."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

from mmi.m4.import_ban import scan_m4_package

STAGE_ORDER = ("C-M4", "C2", "C3", "C4", "M4")

SECRET_PATTERNS = (
    r"sk-[a-zA-Z0-9]{20,}",
    r"api[_-]?key\s*=",
    r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY",
    r"password\s*=\s*['\"][^'\"]+['\"]",
)

AUTHORITY_WRITE_PATTERNS = (
    re.compile(r"open\s*\([^)]*['\"]w", re.IGNORECASE),
    re.compile(r"open\s*\([^)]*['\"]a", re.IGNORECASE),
    re.compile(r"open\s*\([^)]*['\"]w\+", re.IGNORECASE),
    re.compile(r"\.write_text\s*\(", re.IGNORECASE),
    re.compile(r"\.write_bytes\s*\(", re.IGNORECASE),
    re.compile(r"shutil\.copy", re.IGNORECASE),
    re.compile(r"os\.remove\s*\(", re.IGNORECASE),
    re.compile(r"unlink\s*\(", re.IGNORECASE),
)  # legacy line-scan patterns; INV-1 uses AST (_ast_inv1_violations)

PRODUCTION_ENDPOINT_HINTS = (
    "supabase.co",
    "production",
    "prod.db",
    "DATABASE_URL",
)

PROMOTION_BYPASS_PATTERNS = (
    re.compile(r"BUILD_AUTHORIZED\s*=\s*True", re.IGNORECASE),
    re.compile(r"BUILD_AUTHORIZED\s*=\s*['\"]true['\"]", re.IGNORECASE),
    re.compile(r"perfect_claim\s*:\s*true", re.IGNORECASE),
    re.compile(r"M4_MET.*without.*OPERATOR", re.IGNORECASE),
)

EVIDENCE_TMP_PATTERNS = (
    re.compile(r"EVIDENCE_ROOT.*['\"]/tmp", re.IGNORECASE),
    re.compile(r"['\"]/tmp/mmi.*evidence", re.IGNORECASE),
)

AUTHORITY_NAME_MARKERS = frozenset({"AUTHORITY_ROOT", "authority_root"})
WRITE_METHODS = frozenset({"write_text", "write_bytes", "write", "unlink", "touch"})
WRITE_FUNCTIONS = frozenset({"open", "remove", "unlink", "rmdir"})


@dataclass
class InvariantViolation:
    invariant_id: str
    path: str
    line_no: int
    detail: str


@dataclass
class InvariantCheckResult:
    invariant_id: str
    phase: str
    passed: bool
    violations: list[InvariantViolation] = field(default_factory=list)
    note: str = ""


def _is_checker_source(rel: str) -> bool:
    return rel.replace("\\", "/").endswith("mmi/m4/invariants.py")


def _is_sandbox_vector_fixture(rel: str) -> bool:
    """§7 adversarial escape vectors — not live endpoint config."""
    return rel.replace("\\", "/").endswith("mmi/m4/sandbox_escape.py")


def _iter_m4_sources(authority_root: Path) -> list[Path]:
    roots = [
        authority_root / "mmi" / "m4",
        authority_root / "scripts",
    ]
    files: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.py")):
            if path.name.startswith("m4_") or path.parent.name == "m4":
                files.append(path)
    return sorted(set(files), key=lambda p: p.as_posix())


def _scan_lines(
    files: list[Path],
    authority_root: Path,
    invariant_id: str,
    predicate,
) -> list[InvariantViolation]:
    hits: list[InvariantViolation] = []
    for path in files:
        rel = path.relative_to(authority_root).as_posix()
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            detail = predicate(line)
            if detail:
                hits.append(
                    InvariantViolation(
                        invariant_id=invariant_id,
                        path=rel,
                        line_no=idx,
                        detail=detail,
                    )
                )
    return hits


def _authority_path_expr(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return "architectapp_clean" in node.value.lower()
    if isinstance(node, ast.Name) and node.id in AUTHORITY_NAME_MARKERS:
        return True
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.value.id in AUTHORITY_NAME_MARKERS
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "Path":
            return bool(node.args) and _authority_path_expr(node.args[0])
    if isinstance(node, ast.BinOp):
        return _authority_path_expr(node.left) or _authority_path_expr(node.right)
    if isinstance(node, ast.JoinedStr):
        return any(
            isinstance(part, ast.FormattedValue) and _authority_path_expr(part.value)
            for part in node.values
        )
    return False


def _expr_tainted(node: ast.AST, tainted: set[str]) -> bool:
    if isinstance(node, ast.Name):
        return node.id in tainted or node.id in AUTHORITY_NAME_MARKERS
    return _authority_path_expr(node)


def _assign_taint(targets: list[ast.expr], value: ast.AST, tainted: set[str]) -> None:
    if not _expr_tainted(value, tainted):
        return
    for target in targets:
        if isinstance(target, ast.Name):
            tainted.add(target.id)


def _write_mode_is_mutating(node: ast.Call) -> bool:
    if len(node.args) < 2:
        return True
    mode = node.args[1]
    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
        return any(ch in mode.value for ch in "wa+")
    return True


def _inv1_write_violation(
    node: ast.Call,
    tainted: set[str],
    rel: str,
) -> InvariantViolation | None:
    if isinstance(node.func, ast.Attribute):
        if node.func.attr in WRITE_METHODS and _expr_tainted(node.func.value, tainted):
            return InvariantViolation(
                invariant_id="INV-1",
                path=rel,
                line_no=node.lineno,
                detail=f"write via tainted authority handle: .{node.func.attr}()",
            )
    if isinstance(node.func, ast.Name) and node.func.id in WRITE_FUNCTIONS:
        if node.args and _expr_tainted(node.args[0], tainted):
            if node.func.id == "open" and not _write_mode_is_mutating(node):
                return None
            return InvariantViolation(
                invariant_id="INV-1",
                path=rel,
                line_no=node.lineno,
                detail=f"mutating call on tainted authority path: {node.func.id}()",
            )
    if isinstance(node.func, ast.Attribute) and node.func.attr in {"copy", "copy2", "move", "rmtree"}:
        if node.args and _expr_tainted(node.args[0], tainted):
            return InvariantViolation(
                invariant_id="INV-1",
                path=rel,
                line_no=node.lineno,
                detail=f"mutating shutil/os call on tainted authority path: .{node.func.attr}()",
            )
    return None


def _seed_module_taint(body: list[ast.stmt]) -> set[str]:
    """Collect names assigned from authority paths at module scope."""
    tainted: set[str] = set()
    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(stmt, ast.Assign):
            _assign_taint(stmt.targets, stmt.value, tainted)
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            _assign_taint([stmt.target], stmt.value, tainted)
    return tainted


def _analyze_inv1_body(
    body: list[ast.stmt],
    tainted: set[str],
    rel: str,
    violations: list[InvariantViolation],
    module_taint: set[str] | None = None,
) -> None:
    for stmt in body:
        if isinstance(stmt, ast.Assign):
            _assign_taint(stmt.targets, stmt.value, tainted)
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            _assign_taint([stmt.target], stmt.value, tainted)
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            hit = _inv1_write_violation(stmt.value, tainted, rel)
            if hit:
                violations.append(hit)
        elif isinstance(stmt, ast.If):
            branch_taint = set(tainted)
            _analyze_inv1_body(stmt.body, branch_taint, rel, violations, module_taint)
            _analyze_inv1_body(stmt.orelse, set(tainted), rel, violations, module_taint)
        elif isinstance(stmt, (ast.For, ast.While, ast.With)):
            inner = set(tainted)
            _analyze_inv1_body(getattr(stmt, "body", []), inner, rel, violations, module_taint)
        elif isinstance(stmt, ast.Try):
            inner = set(tainted)
            _analyze_inv1_body(stmt.body, inner, rel, violations, module_taint)
            for handler in stmt.handlers:
                _analyze_inv1_body(handler.body, set(tainted), rel, violations, module_taint)
        elif isinstance(stmt, ast.FunctionDef):
            _analyze_inv1_function(stmt, rel, violations, module_taint or set())
        elif isinstance(stmt, ast.AsyncFunctionDef):
            _analyze_inv1_function(stmt, rel, violations, module_taint or set())


def _analyze_inv1_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    rel: str,
    violations: list[InvariantViolation],
    module_taint: set[str],
) -> None:
    tainted: set[str] = set(module_taint)
    _analyze_inv1_body(node.body, tainted, rel, violations, module_taint)


def _ast_inv1_violations(path: Path, rel: str, text: str) -> list[InvariantViolation]:
    if _is_checker_source(rel) or "test_" in rel:
        return []
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []

    violations: list[InvariantViolation] = []
    module_taint = _seed_module_taint(tree.body)
    tainted: set[str] = set(module_taint)
    _analyze_inv1_body(tree.body, tainted, rel, violations, module_taint)
    return violations


def check_inv1_authority_never_writable(authority_root: Path) -> InvariantCheckResult:
    files = _iter_m4_sources(authority_root)
    violations: list[InvariantViolation] = []
    for path in files:
        rel = path.relative_to(authority_root).as_posix()
        text = path.read_text(encoding="utf-8")
        violations.extend(_ast_inv1_violations(path, rel, text))
    return InvariantCheckResult("INV-1", "static", not violations, violations)


def check_inv2_production_unreachable(authority_root: Path) -> InvariantCheckResult:
    files = [
        p
        for p in _iter_m4_sources(authority_root)
        if not _is_checker_source(p.relative_to(authority_root).as_posix())
        and not _is_sandbox_vector_fixture(p.relative_to(authority_root).as_posix())
    ]
    violations = _scan_lines(
        files,
        authority_root,
        "INV-2",
        lambda line: (
            f"production endpoint hint in m4 source: {line.strip()[:120]}"
            if any(h.lower() in line.lower() for h in PRODUCTION_ENDPOINT_HINTS)
            and "test_" not in line
            and "# spec" not in line.lower()
            else ""
        ),
    )
    return InvariantCheckResult("INV-2", "static", not violations, violations)


def check_inv3_secrets_never_cross(authority_root: Path) -> InvariantCheckResult:
    files = _iter_m4_sources(authority_root)
    violations: list[InvariantViolation] = []
    for path in files:
        rel = path.relative_to(authority_root).as_posix()
        if "test_" in rel or _is_checker_source(rel):
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                line_no = text[: match.start()].count("\n") + 1
                violations.append(
                    InvariantViolation(
                        invariant_id="INV-3",
                        path=rel,
                        line_no=line_no,
                        detail=f"secret pattern matched: {match.group()[:40]}",
                    )
                )
    import_ban = scan_m4_package(authority_root)
    if not import_ban.passed:
        for v in import_ban.violations:
            violations.append(
                InvariantViolation(
                    invariant_id="INV-3",
                    path=v.path,
                    line_no=v.line_no,
                    detail=f"L8 coupling (H-L8-001): {v.line}",
                )
            )
    return InvariantCheckResult("INV-3", "static", not violations, violations)


def check_inv4_budget_monotonic(authority_root: Path) -> InvariantCheckResult:
    files = [
        p
        for p in _iter_m4_sources(authority_root)
        if not _is_checker_source(p.relative_to(authority_root).as_posix())
    ]
    violations = _scan_lines(
        files,
        authority_root,
        "INV-4",
        lambda line: (
            "unattributed budget bypass hint"
            if re.search(r"budget.*replenish|replenish.*budget", line, re.IGNORECASE)
            and "attribution" not in line.lower()
            and "attributed" not in line.lower()
            and "CANARY-017" not in line
            else ""
        ),
    )
    return InvariantCheckResult("INV-4", "static", not violations, violations)


def check_inv5_evidence_ordered(authority_root: Path) -> InvariantCheckResult:
    files = _iter_m4_sources(authority_root)
    violations: list[InvariantViolation] = []
    for path in files:
        rel = path.relative_to(authority_root).as_posix()
        if _is_checker_source(rel):
            continue
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for pattern in EVIDENCE_TMP_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        InvariantViolation(
                            invariant_id="INV-5",
                            path=rel,
                            line_no=idx,
                            detail=f"forbidden evidence path: {line.strip()[:120]}",
                        )
                    )
    return InvariantCheckResult("INV-5", "static", not violations, violations)


def check_inv6_no_autonomous_promotion(authority_root: Path) -> InvariantCheckResult:
    files = _iter_m4_sources(authority_root)
    violations: list[InvariantViolation] = []
    for path in files:
        rel = path.relative_to(authority_root).as_posix()
        if "test_" in rel or _is_checker_source(rel):
            continue
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for pattern in PROMOTION_BYPASS_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        InvariantViolation(
                            invariant_id="INV-6",
                            path=rel,
                            line_no=idx,
                            detail=f"promotion bypass pattern: {line.strip()[:120]}",
                        )
                    )
    return InvariantCheckResult("INV-6", "static", not violations, violations)


def check_inv7_ladder_monotonic(authority_root: Path) -> InvariantCheckResult:
    violations: list[InvariantViolation] = []
    runner = authority_root / "scripts" / "m4_endurance_runner.py"
    if runner.exists():
        text = runner.read_text(encoding="utf-8")
        if "STAGE_ORDER" not in text and "C-M4" not in text:
            violations.append(
                InvariantViolation(
                    invariant_id="INV-7",
                    path="scripts/m4_endurance_runner.py",
                    line_no=0,
                    detail="endurance runner missing staged ladder enforcement",
                )
            )
        if re.search(r"--stage\s+M4", text) and "verify_exit" not in text:
            violations.append(
                InvariantViolation(
                    invariant_id="INV-7",
                    path="scripts/m4_endurance_runner.py",
                    line_no=0,
                    detail="M4 entry without stage_attestation.verify_exit",
                )
            )
    import_ban = scan_m4_package(authority_root)
    if not import_ban.passed:
        violations.append(
            InvariantViolation(
                invariant_id="INV-7",
                path="mmi/m4",
                line_no=0,
                detail="H-L8-001 import ban failed (prerequisite for ladder build)",
            )
        )
    return InvariantCheckResult(
        "INV-7",
        "static",
        not violations,
        violations,
        note="structural; full verify_exit wiring lands with m4_endurance_runner (Phase 7)",
    )


STATIC_CHECKS = (
    check_inv1_authority_never_writable,
    check_inv2_production_unreachable,
    check_inv3_secrets_never_cross,
    check_inv4_budget_monotonic,
    check_inv5_evidence_ordered,
    check_inv6_no_autonomous_promotion,
    check_inv7_ladder_monotonic,
)

LIVE_CHECKS = (
    "INV-1",
    "INV-2",
    "INV-3",
    "INV-4",
    "INV-5",
    "INV-6",
    "INV-7",
)


def run_static_suite(authority_root: Path) -> list[InvariantCheckResult]:
    return [fn(authority_root) for fn in STATIC_CHECKS]


def run_live_suite(authority_root: Path) -> list[InvariantCheckResult]:
    return [
        InvariantCheckResult(
            inv,
            "live",
            False,
            note="live checks require boundary daemon + endurance harness (Phase 4+)",
        )
        for inv in LIVE_CHECKS
    ]


def suite_passed(results: list[InvariantCheckResult]) -> bool:
    return all(r.passed for r in results)
