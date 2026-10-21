"""Run the bundled structure rule against the repository's single declaration."""

from pathlib import Path

from devkit_dev.bundle.rules.architecture.rule import inspect_architecture


def test_repository_architecture() -> None:
    root = Path(__file__).resolve().parents[3]
    findings = inspect_architecture(root)
    assert not findings, "\n".join(f"{path}:{line}: {message}" for path, line, message in findings)
