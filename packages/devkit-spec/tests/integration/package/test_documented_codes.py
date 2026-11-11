"""Every advisory code devkit-spec defines is documented under ``docs/``: agents branch on codes, people look them up."""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SRC = Path(__file__).resolve().parents[3] / "src"
CODE = re.compile(r"""\bcode\s*(?::\s*str\s*)?=\s*["']([A-Z][A-Z0-9_]+)["']""")


def test_every_code_is_documented() -> None:
    codes = {match.group(1) for path in SRC.rglob("*.py") for match in CODE.finditer(path.read_text())}
    assert "SPEC_CONFIG_INVALID" in codes  # the scan works
    documented = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "docs").rglob("*.md"))
    assert sorted(code for code in codes if f"`{code}`" not in documented) == []


def test_the_agent_invocation_matches_devkit_dist() -> None:
    """The package base repeats devkit_dist's agent-facing invocation (a base may not import a feature module)."""
    from devkit_dist.features.project.models.invocation import AGENT_INVOCATION

    from devkit_spec.base.errors import DEVKIT

    assert DEVKIT == AGENT_INVOCATION


# SPEC-consolidate-spec-scope-commands AC-06: the scope codes table and the scope fixes name only what exists.
SCOPE_SOURCES = [
    *sorted((SRC / "devkit_spec/features/scope").rglob("*.py")),
    SRC / "devkit_spec/features/delivery/usecases/cleanup.py",
]
RETIRED = re.compile(r"scope (register|query|compare|update)\b|--request-id|--mode\b")


def _scope_error_classes() -> list[type]:
    from devkit_spec.base import errors

    classes = [
        value
        for value in vars(errors).values()
        if isinstance(value, type) and issubclass(value, errors.ScopeError) and value is not errors.ScopeError
    ]
    return [*classes, errors.PostFinishCleanupNotice]


def _documented_scope_codes() -> set[str]:
    contract = (ROOT / "docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md").read_text(encoding="utf-8")
    section = contract.split("### 4.8 Codes", 1)[1].split("\n### ", 1)[0]
    return set(re.findall(r"^\| `([A-Z][A-Z0-9_]+)` \|", section, flags=re.MULTILINE))


def _text(node: ast.expr) -> str:
    """The literal text of a string or f-string expression, its placeholders as ``{}``."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(_text(part) if isinstance(part, ast.Constant) else "{}" for part in node.values)
    if isinstance(node, ast.BinOp):
        return _text(node.left) + _text(node.right)
    return ""


def _source_fixes(path: Path) -> list[str]:
    fixes: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call):
            fixes += [_text(keyword.value) for keyword in node.keywords if keyword.arg == "fix"]
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and "FIX" in target.id for target in node.targets
        ):
            fixes.append(_text(node.value))
    return [fix for fix in fixes if fix]


def test_the_scope_codes_table_matches_the_defined_codes_in_both_directions() -> None:
    defined = {cls.code for cls in _scope_error_classes()}
    assert "SPEC_SCOPE_TIMEOUT" in defined  # the scan works
    documented = _documented_scope_codes()
    assert sorted(defined - documented) == [], "defined but missing from CAP-COLL-work-scope-registry 4.8"
    assert sorted(documented - defined) == [], "documented in 4.8 but no longer defined"


def test_scope_fixes_name_only_existing_commands_and_options() -> None:
    fixes = [(cls.__name__, str(cls.fix)) for cls in _scope_error_classes() if getattr(cls, "fix", "")]
    fixes += [(path.name, fix) for path in SCOPE_SOURCES for fix in _source_fixes(path)]
    assert len(fixes) > 10  # the scan works
    stale = [(owner, fix) for owner, fix in fixes if RETIRED.search(fix)]
    stale += [(owner, fix) for owner, fix in fixes if "--task-id" in fix and "release --task-id" not in fix]
    assert stale == []
