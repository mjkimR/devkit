"""The deployed ADR checker, evaluated through the real rule engine and snapshot cache."""

from pathlib import Path

import pytest
from devkit_agt.features.rules import match_path
from devkit_agt.features.rules.services.testing import check, evaluate, load_rule, opened_files

RULE = load_rule(__file__)
OLD = "docs/decisions/old.md"
NEW = "docs/decisions/new.md"


def _doc(name: str, header: str = "", body: str = "", status: str = "accepted") -> str:
    return f"---\nid: {name}\nstatus: {status}\n{header}---\n# {name}\n\n{body}"


def test_valid_whole_and_partial_replacements(tmp_path: Path) -> None:
    files = {
        OLD: _doc("ADR-old", "superseded_by: ADR-new\n", status="superseded"),
        NEW: _doc("ADR-new", "supersedes: [ADR-old, ADR-partial]\n"),
        "docs/decisions/partial.md": _doc("ADR-partial", body="Superseded in part by `ADR-new`: retries.\n"),
    }
    assert check(RULE, tmp_path, files) == []


@pytest.mark.parametrize(
    "header,status",
    [
        ("superseded_by: ADR-new\n", "accepted"),
        ("", "superseded"),
        ("superseded_by: [ADR-new]\n", "superseded"),
        ("superseded_by: ADR-missing\n", "superseded"),
        ("superseded_by: null\n", "superseded"),
    ],
)
def test_invalid_whole_replacements_report_source(tmp_path: Path, header: str, status: str) -> None:
    found = check(RULE, tmp_path, {OLD: _doc("ADR-old", header, status=status), NEW: _doc("ADR-new")})
    assert found and all(v.rule_id == RULE.id and v.file == OLD and not v.fixable for v in found)
    assert all(v.remediation and v.line >= 1 for v in found)


def test_whole_successor_requires_reciprocal_supersedes(tmp_path: Path) -> None:
    found = check(
        RULE,
        tmp_path,
        {
            OLD: _doc("ADR-old", "superseded_by: ADR-new\n", status="superseded"),
            NEW: _doc("ADR-new"),
        },
    )
    assert [(v.file, v.line) for v in found] == [(OLD, 4)]


@pytest.mark.parametrize("value", ["ADR-missing", "CAP-A-x", "[ADR-old, 3]", "{x: ADR-old}", "null"])
def test_invalid_supersedes_metadata(tmp_path: Path, value: str) -> None:
    files = {NEW: _doc("ADR-new", f"supersedes: {value}\n"), "docs/cap.md": _doc("CAP-A-x")}
    found = check(RULE, tmp_path, files)
    assert found and all(v.file == NEW and v.line == 4 for v in found)


def test_missing_partial_counterparts_are_reported_on_both_sides(tmp_path: Path) -> None:
    files = {OLD: _doc("ADR-old"), NEW: _doc("ADR-new", "supersedes: ADR-old\n")}
    assert [v.file for v in check(RULE, tmp_path, files)] == [NEW]
    files[OLD] = _doc("ADR-old", body="Superseded in part by `ADR-new`: retries.\n")
    files[NEW] = _doc("ADR-new")
    assert [v.file for v in check(RULE, tmp_path, files)] == [OLD]


def test_partial_pointer_must_resolve_and_target_stays_accepted(tmp_path: Path) -> None:
    files = {OLD: _doc("ADR-old", body="Superseded in part by `ADR-missing`: retries.\n", status="deprecated")}
    found = check(RULE, tmp_path, files)
    assert len(found) == 2 and {v.file for v in found} == {OLD}


def test_aliases_on_both_sides_resolve_canonically(tmp_path: Path) -> None:
    files = {
        OLD: _doc("ADR-old", "aliases: [ADR-old-alias]\n", "Superseded in part by `ADR-new-alias`: retries.\n"),
        NEW: _doc("ADR-new", "aliases: [ADR-new-alias]\nsupersedes: ADR-old-alias\n"),
    }
    assert check(RULE, tmp_path, files) == []
    files[OLD] = _doc("ADR-old", "aliases: [ADR-old-alias]\nsuperseded_by: ADR-new-alias\n", status="superseded")
    assert check(RULE, tmp_path, files) == []


def test_ambiguous_aliases_are_not_guessed(tmp_path: Path) -> None:
    files = {
        OLD: _doc("ADR-old", "aliases: [ADR-retired]\n"),
        "docs/decisions/other.md": _doc("ADR-other", "aliases: [ADR-retired]\n"),
        NEW: _doc("ADR-new", "supersedes: ADR-retired\n"),
    }
    assert [v.file for v in check(RULE, tmp_path, files)] == [NEW]


def test_masked_examples_and_padrs_are_outside_scope(tmp_path: Path) -> None:
    pointer = "Superseded in part by `ADR-missing`: retries."
    body = f"```markdown\n{pointer}\n```\n\n    {pointer}\n\n<!-- {pointer} -->\n\n~~{pointer}~~\n"
    files = {
        OLD: _doc("ADR-old", body=body),
        "docs/proposals/p/decision.md": _doc("PADR-draft", "supersedes: ADR-missing\n"),
    }
    assert check(RULE, tmp_path, files) == []


def test_targeting_exclusions_and_fix_immutability(tmp_path: Path) -> None:
    files = {OLD: _doc("ADR-old", status="superseded"), NEW: _doc("ADR-new", "supersedes: ADR-missing\n")}
    found = check(RULE, tmp_path, files, targets=[OLD], fix=True)
    assert [v.file for v in found] == [OLD]
    assert (tmp_path / OLD).read_text() == files[OLD]
    assert [v.file for v in check(RULE, tmp_path, exclude=[OLD])] == [NEW]
    assert [v.file for v in check(RULE, tmp_path, targets=[OLD], fix=True)] == [OLD]


def test_declared_inputs_cover_snapshot_reads(tmp_path: Path) -> None:
    files = {
        OLD: _doc("ADR-old"),
        NEW: _doc("ADR-new", "supersedes: ADR-old\n"),
        "specs/x/spec.md": _doc("SPEC-x"),
        "src/a.py": "x = 1\n",
    }
    check(RULE, tmp_path, files)
    assert evaluate(RULE, tmp_path, targets=["src/a.py"]).skipped == [RULE.id]
    for target in [OLD, "specs/x/spec.md"]:
        # Either declared input activates this cross-document checker.
        assert RULE.id not in evaluate(RULE, tmp_path, targets=[target]).skipped
    with opened_files(tmp_path) as opened:
        check(RULE, tmp_path)
    assert all(any(match_path(pattern, name) for pattern in (getattr(RULE, "inputs", None) or ())) for name in opened)


def test_historical_partial_pointer_survives_later_whole_replacement(tmp_path: Path) -> None:
    files = {
        OLD: _doc(
            "ADR-old", "superseded_by: ADR-final\n", "Superseded in part by `ADR-new`: retries.\n", status="superseded"
        ),
        NEW: _doc("ADR-new", "supersedes: ADR-old\n"),
        "docs/decisions/final.md": _doc("ADR-final", "supersedes: ADR-old\n"),
    }
    assert check(RULE, tmp_path, files) == []
    files[NEW] = _doc("ADR-new")
    assert [v.file for v in check(RULE, tmp_path, files)] == [OLD]


def test_root_and_nested_materials_are_free_form(tmp_path: Path) -> None:
    files = {
        "docs/materials/example.md": _doc("ADR-example", status="superseded"),
        "specs/x/materials/example.md": _doc("ADR-nested", "supersedes: ADR-missing\n"),
    }
    assert check(RULE, tmp_path, files) == []
