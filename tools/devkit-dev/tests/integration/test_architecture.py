"""Run the bundled structure rule against the repository's single declaration."""

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
