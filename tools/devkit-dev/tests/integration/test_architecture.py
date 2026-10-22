"""Run the bundled structure rule against the repository's single declaration."""

import ast
from pathlib import Path

from devkit_dev.bundle.rules.architecture.rule import inspect_architecture


def test_repository_architecture() -> None:
    root = Path(__file__).resolve().parents[4]
    findings = inspect_architecture(root)
    assert not findings, "\n".join(f"{path}:{line}: {message}" for path, line, message in findings)


def test_repository_usecase_boundaries() -> None:
    from importlib import import_module

    rule = import_module("devkit_dev.bundle.rules.usecase-boundaries.rule")
    root = Path(__file__).resolve().parents[4]
    findings = rule.inspect_usecases(root)
    assert not findings, "\n".join(f"{path}:{line}: {message}" for path, line, message in findings)


def test_workspace_modules_use_shared_logger() -> None:
    root = Path(__file__).resolve().parents[4]
    violations: list[str] = []
    for py_file in root.glob("packages/*/src/**/*.py"):
        if py_file.name == "logs.py" or "devkit_cli" in py_file.parts:
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "getLogger"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "logging"
                and node.args
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "__name__"
            ):
                violations.append(f"{py_file.relative_to(root)}:{node.lineno}")
    assert not violations, f"Workspace modules must use devkit_core.core.logs.get_logger(__name__): {violations}"
