"""``RULE-file-length``: files above ``max_lines`` are reported, with settings per project and per path."""

from __future__ import annotations

from pathlib import Path

import pytest

from devkit.rules import RuleContext, RulesRunError, Severity
from devkit.rules.rules.file_length import FileLengthRule
from devkit.rules.testing import check, write_files

LONG = "\n".join(f"Line {i}" for i in range(50))


def test_a_file_above_max_lines_is_reported(tmp_path: Path) -> None:
    write_files(tmp_path, {"docs/long.md": LONG})
    violations = FileLengthRule(max_lines=30).check(RuleContext(workspace_root=tmp_path))
    assert len(violations) == 1
    assert "exceeds line length limit" in violations[0].message


def test_settings_and_path_overrides_apply(tmp_path: Path) -> None:
    files = {"docs/long.md": LONG, "research/long.md": LONG, "src/long.py": LONG}
    settings = {"max_lines": 30, "overrides": [{"path": "research/**", "max_lines": 100}]}
    found = check(FileLengthRule(), tmp_path, files, settings=settings)
    assert [(v.file, v.severity) for v in found] == [("docs/long.md", Severity.WARNING)]
    found = check(FileLengthRule(), tmp_path, settings={"max_lines": 30, "extensions": [".py"]})
    assert [v.file for v in found] == ["src/long.py"]


def test_explicit_targets_limit_the_run(tmp_path: Path) -> None:
    files = {"docs/a.md": LONG, "docs/b.md": LONG}
    assert [
        v.file for v in check(FileLengthRule(), tmp_path, files, targets=["docs/b.md"], settings={"max_lines": 30})
    ] == ["docs/b.md"]


def test_excluded_files_are_never_reported(tmp_path: Path) -> None:
    files = {"docs/a.md": LONG, "vendor/b.md": LONG}
    found = check(FileLengthRule(), tmp_path, files, settings={"max_lines": 30}, exclude=["vendor/**"])
    assert [v.file for v in found] == ["docs/a.md"]
    assert (
        check(FileLengthRule(), tmp_path, targets=["vendor/b.md"], settings={"max_lines": 30}, exclude=["vendor/**"])
        == []
    )


def test_invalid_settings_fail_the_run(tmp_path: Path) -> None:
    with pytest.raises(RulesRunError) as raised:
        check(FileLengthRule(), tmp_path, settings={"max_lines": 0})
    assert [problem.code for problem in raised.value.problems] == ["RULES_SETTINGS_INVALID"]
