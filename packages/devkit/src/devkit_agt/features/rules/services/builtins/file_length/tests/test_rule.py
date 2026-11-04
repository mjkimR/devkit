"""``RULE-file-length``: files above ``max_lines`` are reported, with settings per project and per path."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import RuleContext, RulesRunError, Severity
from devkit_agt.features.rules.services.builtins.file_length import FileLengthRule
from devkit_agt.features.rules.services.testing import check, write_files

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


def _record(header: str, lines: int, *, final_newline: bool = True) -> str:
    prefix = f"---\n{header}\n---\n"
    text = prefix + "body\n" * (lines - prefix.count("\n"))
    return text if final_newline else text.rstrip("\n")


@pytest.mark.parametrize(
    "identity,aliases",
    [
        ("ADR-example", "[ADR-first, ADR-second]"),
        ("FB-consolidated-governance-promoted", "[FB-one]"),
        ("FB-consolidated-docs-search-forwarded", "[FB-one]"),
        ("FB-consolidated-other-dismissed", "[FB-one]"),
        ("FB-consolidated-other-resolved", "[FB-one]"),
    ],
)
@pytest.mark.parametrize("lines", [500, 600, 601])
@pytest.mark.parametrize("final_newline", [True, False])
def test_consolidated_thresholds(tmp_path: Path, identity: str, aliases: str, lines: int, final_newline: bool) -> None:
    found = check(
        FileLengthRule(),
        tmp_path,
        {"record.md": _record(f"id: {identity}\naliases: {aliases}", lines, final_newline=final_newline)},
        settings={"consolidated_max_lines": 600},
    )
    if lines <= 600:
        assert found == []
    else:
        assert len(found) == 1
        assert found[0].line == 601
        assert found[0].message == "File exceeds line length limit (601 > 600 lines)"
        assert found[0].remediation == (
            "Review the consolidation group by topic while preserving every retained decision or outcome"
        )
        assert not found[0].fixable


@pytest.mark.parametrize(
    "header",
    [
        "id: PADR-example\naliases: [one, two]",
        "id: CAP-example\naliases: [one, two]",
        "id: ADR-example\naliases: [one]",
        "id: ADR-example\naliases: [one, one]",
        "id: ADR-example\naliases: [one, 2]",
        "id: ADR-example\naliases: [one, null]",
        "id: ADR-example\naliases: [one, '   ']",
        "id: ADR-example\naliases: one",
        "id: ADR-example\naliases: {one: two}",
        "id: ADR-example",
        "id: ''\naliases: [one, two]",
        "id: 42\naliases: [one, two]",
        "id: FB-consolidated-other-open\naliases: [one]",
        "id: FB-consolidated--promoted\naliases: [one]",
        "id: FB-consolidated-other-promoted-extra\naliases: [one]",
        "id: FB-consolidated-other-promoted\naliases: []",
        "id: [invalid",
        "- a non-mapping header",
    ],
)
def test_nonqualifying_or_invalid_headers_keep_ordinary_findings(tmp_path: Path, header: str) -> None:
    files = {"record.md": _record(header, 500)}
    ordinary = check(FileLengthRule(), tmp_path, files)
    assert check(FileLengthRule(), tmp_path, settings={"consolidated_max_lines": 600}) == ordinary
    assert ordinary[0].line == 401
    assert ordinary[0].remediation == "Consider modularizing or splitting the document into smaller sections"


@pytest.mark.parametrize("text", ["body\n" * 500, "---\nid: [unclosed\n" + "body\n" * 498])
def test_absent_or_unterminated_frontmatter_keeps_ordinary_limit(tmp_path: Path, text: str) -> None:
    found = check(FileLengthRule(), tmp_path, {"record.md": text}, settings={"consolidated_max_lines": 600})
    assert len(found) == 1 and found[0].line == 401


def test_omitted_option_preserves_alias_record_and_higher_override(tmp_path: Path) -> None:
    files = {"record.md": _record("id: ADR-example\naliases: [old, older]", 700)}
    ordinary = check(FileLengthRule(), tmp_path, files)
    assert ordinary[0].line == 401
    settings = {"consolidated_max_lines": 600, "overrides": [{"path": "record.md", "max_lines": 900}]}
    assert check(FileLengthRule(), tmp_path, settings=settings) == []
    settings["overrides"] = [{"path": "record.md", "consolidated_max_lines": 750}]
    assert check(FileLengthRule(), tmp_path, settings=settings) == []


@pytest.mark.parametrize("budget", [True, "600", 0, -1])
def test_invalid_consolidated_budget(tmp_path: Path, budget: object) -> None:
    with pytest.raises(RulesRunError) as raised:
        check(FileLengthRule(), tmp_path, settings={"consolidated_max_lines": budget})
    assert [problem.code for problem in raised.value.problems] == ["RULES_SETTINGS_INVALID"]
    assert "RULE-file-length" in str(raised.value.problems[0])


@pytest.mark.parametrize("enabled,lines,suffix", [(False, 500, ".md"), (True, 400, ".md"), (True, 500, ".txt")])
def test_unneeded_headers_are_not_parsed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, enabled: bool, lines: int, suffix: str
) -> None:
    from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache

    def unexpected(*args: object) -> None:
        pytest.fail("frontmatter must not be read for this file")

    monkeypatch.setattr(WorkspaceCache, "get_frontmatter", unexpected)
    settings: dict[str, object] = {"extensions": [suffix]}
    if enabled:
        settings["consolidated_max_lines"] = 600
    check(FileLengthRule(), tmp_path, {f"record{suffix}": "body\n" * lines}, settings=settings)
