"""``envelope worker`` refuses a stage the unit's workflow does not declare (``SPEC-lifecycle-feedback-fixes``)."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import Result
from testsupport.workflow import SIMPLE_UNIT, run_cli, simple_workspace

# ``w`` with an ordinary stage and an exception stage.
RECOVERING = (
    "---\nid: w\nschema_version: 1\nchecks:\n"
    "  - { name: exception-raised, class: human, description: raised }\n"
    "  - { name: exception-handled, class: human, description: handled }\n"
    "stages:\n  - id: s\n    exit: [anchor-exists]\n"
    "  - id: recover\n    exception: true\n    entry: [exception-raised]\n    exit: [exception-handled]\n---\n"
)


@pytest.fixture
def root(tmp_path: Path) -> Path:
    simple_workspace(tmp_path)
    (tmp_path / ".devkit/workflows/w.md").write_text(RECOVERING, encoding="utf-8")
    created = run_cli("new", "-w", str(tmp_path), "u")
    assert created.exit_code == 0, created.output
    return tmp_path


def _worker(root: Path, *args: str) -> Result:
    return run_cli("envelope", "worker", "-w", str(root), "--unit", SIMPLE_UNIT, *args)


def _written(root: Path) -> list[str]:
    directory = root / SIMPLE_UNIT / "envelopes"
    return sorted(p.name for p in directory.iterdir()) if directory.is_dir() else []


# AC-03
@pytest.mark.parametrize("authoring", [("--summary", "ran", "--effort", "medium"), ()], ids=["authoring", "skeleton"])
def test_an_undeclared_stage_is_refused_before_writing(root: Path, authoring: tuple[str, ...]) -> None:
    result = _worker(root, "--stage", "no-such-stage", *authoring)
    assert result.exit_code == 2, result.output
    assert "ENVELOPE_FLAG_INVALID" in result.stderr
    assert "[TARGET] --stage" in result.stderr
    assert f"uv run devkit workflow next --unit {SIMPLE_UNIT}" in result.stderr
    assert "declares: s, recover" in result.stderr
    assert _written(root) == []


# AC-03
def test_a_dash_stage_is_still_refused_on_the_stage_flag(root: Path) -> None:
    result = _worker(root, "--stage", "-", "--summary", "ran")
    assert result.exit_code == 2, result.output
    assert "ENVELOPE_FLAG_INVALID" in result.stderr and "[TARGET] --stage" in result.stderr
    assert _written(root) == []


# AC-04
@pytest.mark.parametrize("stage", ["s", "recover"])
def test_a_declared_stage_writes(root: Path, stage: str) -> None:
    result = _worker(root, "--stage", stage, "--summary", "ran")
    assert result.exit_code == 0, result.output
    assert _written(root) == ["worker-01.yaml"]


# AC-04
@pytest.mark.parametrize("definition", [None, "---\nid: [unclosed\n---\n"], ids=["missing", "unreadable"])
def test_an_unloadable_definition_keeps_the_lenient_path(root: Path, definition: str | None) -> None:
    path = root / ".devkit/workflows/w.md"
    if definition is None:
        path.unlink()
    else:
        path.write_text(definition, encoding="utf-8")
    result = _worker(root, "--stage", "no-such-stage", "--summary", "ran")
    assert result.exit_code == 0, result.output
    assert _written(root) == ["worker-01.yaml"]
