"""Raw-byte hygiene budgets, targeting and rule-local consolidated selection."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import Phase, RuleContext, RulesRunError, Severity
from devkit_agt.features.rules.services.builtins.file_length import FileLengthRule
from devkit_agt.features.rules.services.builtins.file_length.rule import DEFAULT_MAX_BYTES, FileLengthSettings
from devkit_agt.features.rules.services.testing import check, write_files

LONG = "x" * 50


def test_default_budget_and_single_line_overflow(tmp_path: Path) -> None:
    assert DEFAULT_MAX_BYTES == 49152
    assert FileLengthSettings().max_bytes == 49152
    assert FileLengthSettings().consolidated_max_bytes is None
    write_files(tmp_path, {"docs/long.md": "x" * 49153})
    found = FileLengthRule().check(RuleContext(workspace_root=tmp_path))
    assert len(found) == 1
    assert found[0].message == "File exceeds byte budget (49153 > 49152 bytes)"
    assert (found[0].line, found[0].severity, found[0].phase, found[0].fixable) == (
        1,
        Severity.WARNING,
        Phase.HYGIENE,
        False,
    )


@pytest.mark.parametrize(
    "raw", [b"", b"abcd", b"abcde", "가".encode(), "가나".encode(), b"a\nb", b"a\r\nb", b"a\r\nb\n", b"\xff" * 5]
)
def test_raw_bytes_not_characters_or_normalized_newlines(tmp_path: Path, raw: bytes) -> None:
    (tmp_path / "doc.md").write_bytes(raw)
    found = check(FileLengthRule(), tmp_path, settings={"max_bytes": 4})
    assert len(found) == int(len(raw) > 4)
    if found:
        assert found[0].line == 1
        assert found[0].message == f"File exceeds byte budget ({len(raw)} > 4 bytes)"


def test_settings_and_path_overrides_apply(tmp_path: Path) -> None:
    files = {"docs/long.md": LONG, "research/long.md": LONG, "src/long.py": LONG}
    settings = {"max_bytes": 30, "overrides": [{"path": "research/**", "max_bytes": 100}]}
    found = check(FileLengthRule(), tmp_path, files, settings=settings)
    assert [(v.file, v.severity) for v in found] == [("docs/long.md", Severity.WARNING)]
    found = check(FileLengthRule(), tmp_path, settings={"max_bytes": 30, "extensions": [".py"]})
    assert [v.file for v in found] == ["src/long.py"]


def test_explicit_targets_limit_the_run(tmp_path: Path) -> None:
    files = {"docs/a.md": LONG, "docs/b.md": LONG}
    assert [
        v.file for v in check(FileLengthRule(), tmp_path, files, targets=["docs/b.md"], settings={"max_bytes": 30})
    ] == ["docs/b.md"]


def test_excluded_files_are_never_reported(tmp_path: Path) -> None:
    files = {"docs/a.md": LONG, "vendor/b.md": LONG}
    found = check(FileLengthRule(), tmp_path, files, settings={"max_bytes": 30}, exclude=["vendor/**"])
    assert [v.file for v in found] == ["docs/a.md"]
    assert (
        check(FileLengthRule(), tmp_path, targets=["vendor/b.md"], settings={"max_bytes": 30}, exclude=["vendor/**"])
        == []
    )


@pytest.mark.parametrize("field", ["max_bytes", "consolidated_max_bytes"])
@pytest.mark.parametrize("budget", [True, "600", 0, -1])
def test_invalid_byte_settings_fail_the_run(tmp_path: Path, field: str, budget: object) -> None:
    with pytest.raises(RulesRunError) as raised:
        check(FileLengthRule(), tmp_path, settings={field: budget})
    assert [problem.code for problem in raised.value.problems] == ["RULES_SETTINGS_INVALID"]
    assert "RULE-file-length" in str(raised.value.problems[0])


@pytest.mark.parametrize("field", ["max_lines", "consolidated_max_lines"])
@pytest.mark.parametrize("override", [False, True])
def test_obsolete_line_keys_are_errors_not_converted(tmp_path: Path, field: str, override: bool) -> None:
    settings = {"overrides": [{"path": "docs/**", field: 600}]} if override else {field: 600}
    with pytest.raises(RulesRunError) as raised:
        check(FileLengthRule(), tmp_path, settings=settings)
    assert [problem.code for problem in raised.value.problems] == ["RULES_SETTINGS_INVALID"]
    assert field in str(raised.value.problems[0])


def _record(header: str, size: int, *, final_newline: bool = True) -> str:
    prefix = f"---\n{header}\n---\n"
    body_size = size - len(prefix.encode()) - int(final_newline)
    assert body_size >= 0
    return prefix + "x" * body_size + ("\n" if final_newline else "")


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
@pytest.mark.parametrize("size", [500, 600, 601])
@pytest.mark.parametrize("final_newline", [True, False])
def test_consolidated_thresholds(tmp_path: Path, identity: str, aliases: str, size: int, final_newline: bool) -> None:
    text = _record(f"id: {identity}\naliases: {aliases}", size, final_newline=final_newline)
    assert len(text.encode()) == size
    found = check(
        FileLengthRule(), tmp_path, {"record.md": text}, settings={"max_bytes": 400, "consolidated_max_bytes": 600}
    )
    if size <= 600:
        assert found == []
    else:
        assert len(found) == 1 and found[0].line == 1
        assert found[0].message == "File exceeds byte budget (601 > 600 bytes)"
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
    ordinary = check(FileLengthRule(), tmp_path, files, settings={"max_bytes": 400})
    assert check(FileLengthRule(), tmp_path, settings={"max_bytes": 400, "consolidated_max_bytes": 600}) == ordinary
    assert ordinary[0].line == 1
    assert ordinary[0].remediation == "Consider modularizing or splitting the document into smaller sections"


@pytest.mark.parametrize("text", ["body\n" * 100, "---\nid: [unclosed\n" + "body\n" * 100])
def test_absent_or_unterminated_frontmatter_keeps_ordinary_limit(tmp_path: Path, text: str) -> None:
    found = check(
        FileLengthRule(), tmp_path, {"record.md": text}, settings={"max_bytes": 400, "consolidated_max_bytes": 600}
    )
    assert len(found) == 1 and found[0].line == 1


def test_omitted_option_and_higher_ordinary_override(tmp_path: Path) -> None:
    files = {"record.md": _record("id: ADR-example\naliases: [old, older]", 700)}
    ordinary = check(FileLengthRule(), tmp_path, files, settings={"max_bytes": 400})
    assert ordinary[0].line == 1
    settings = {"max_bytes": 400, "consolidated_max_bytes": 600, "overrides": [{"path": "record.md", "max_bytes": 900}]}
    assert check(FileLengthRule(), tmp_path, settings=settings) == []
    settings["overrides"] = [{"path": "record.md", "consolidated_max_bytes": 750}]
    assert check(FileLengthRule(), tmp_path, settings=settings) == []


@pytest.mark.parametrize("enabled,size,suffix", [(False, 500, ".md"), (True, 400, ".md"), (True, 500, ".txt")])
def test_unneeded_headers_are_not_parsed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, enabled: bool, size: int, suffix: str
) -> None:
    from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache

    def unexpected(*args: object) -> None:
        pytest.fail("frontmatter must not be read for this file")

    monkeypatch.setattr(WorkspaceCache, "get_frontmatter", unexpected)
    settings: dict[str, object] = {"max_bytes": 400, "extensions": [suffix]}
    if enabled:
        settings["consolidated_max_bytes"] = 600
    check(FileLengthRule(), tmp_path, {f"record{suffix}": "x" * size}, settings=settings)
