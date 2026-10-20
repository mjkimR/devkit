"""``RULE-document-reference``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

from devkit.rules import Violation
from devkit.rules.testing import check, load_rule

RULE = load_rule(__file__)


def _found(violations: list[Violation]) -> list[tuple[str, int, str]]:
    """``(file, line, message)`` of the violations that remain (not fixed)."""
    return [(v.file, v.line, v.message) for v in violations if not v.fixed]


def _doc(document_id: str, body: str = "", header: str = "", status: str = "active") -> str:
    return f"---\nid: {document_id}\nstatus: {status}\n{header}---\n{body}"


def test_resolvable_references_pass(tmp_path: Path) -> None:
    files = {
        "docs/a.md": _doc("CAP-A-a", "`US-b`\n", "stories:\n  - US-b\n"),
        "docs/b.md": _doc("US-b", "`CAP-A-a`\n", "capabilities: [CAP-A-a]\n"),
    }
    assert check(RULE, tmp_path, files) == []


def test_reference_problems(tmp_path: Path) -> None:
    files = {"docs/a.md": _doc("CAP-A-a", "`US-none`\n", "stories:\n  - CAP-A-a\n  - docs/b.md\nspec: [x]\n")}
    assert _found(check(RULE, tmp_path, files)) == [
        ("docs/a.md", 7, "spec must be one ID"),
        ("docs/a.md", 5, "stories takes US- IDs, got CAP-A-a"),
        ("docs/a.md", 6, "stories must contain a full document ID, got 'docs/b.md'"),
        ("docs/a.md", 9, "no document has the ID US-none"),
    ]


def test_duplicates_and_shared_proposal_slugs(tmp_path: Path) -> None:
    files = {
        "docs/a.md": _doc("US-dup"),
        "docs/b.md": _doc("US-dup"),
        "docs/proposals/x/proposal.md": _doc("PROP-x"),
        "specs/2026-10/20261001-x/spec.md": _doc("SPEC-x"),
    }
    messages = _found(check(RULE, tmp_path, files))
    assert ("docs/a.md", 1, "US-dup is declared by 2 documents: docs/a.md, docs/b.md") in messages
    assert ("docs/b.md", 1, "US-dup is declared by 2 documents: docs/a.md, docs/b.md") in messages
    assert any(path == "docs/proposals/x/proposal.md" and "shares its slug" in m for path, _, m in messages)


def test_brackets_and_handed_off_proposals_are_fixed(tmp_path: Path) -> None:
    files = {
        "specs/2026-10/20261001-x/spec.md": _doc("SPEC-x", "", "proposal: PROP-x\n"),
        "docs/a.md": _doc("CAP-A-a", "See [SPEC-x] and `PROP-x`, [link](https://x).\n"),
    }
    violations = check(RULE, tmp_path, files)
    assert {(v.message, v.fixable) for v in violations} == {
        ("prose reference SPEC-x must be written `SPEC-x`, not [SPEC-x]", True),
        ("PROP-x was handed off; reference `SPEC-x`", True),
    }
    fixed = check(RULE, tmp_path, fix=True)
    assert _found(fixed) == [] and all(v.fixed for v in fixed)
    assert (tmp_path / "docs/a.md").read_text().endswith("See `SPEC-x` and `SPEC-x`, [link](https://x).\n")
    assert "proposal: PROP-x" in (tmp_path / "specs/2026-10/20261001-x/spec.md").read_text()


def test_internal_path_links_must_be_ids(tmp_path: Path) -> None:
    files = {
        "docs/a/one.md": _doc(
            "CAP-A-one", "[two](../b/two.md) [readme](../b/README.md) [x](../b/two.md#h) ![i](../b/two.md)\n"
        ),
        "docs/b/two.md": _doc("US-two"),
        "docs/b/README.md": "# readme\n",
    }
    assert _found(check(RULE, tmp_path, files)) == [
        ("docs/a/one.md", 5, "internal document link ../b/two.md must be the ID `US-two`")
    ]


def test_history_and_materials_are_skipped_unless_targeted(tmp_path: Path) -> None:
    files = {
        "specs/2026-10/20261001-done/spec.md": _doc("SPEC-done", "`US-gone` [US-x]\n", status="completed"),
        "docs/materials/m.md": _doc("MAT-m", "`US-gone`\n"),
    }
    assert check(RULE, tmp_path, files) == []
    targeted = _found(check(RULE, tmp_path, targets=["specs/2026-10/20261001-done/spec.md"]))
    assert [m for _, _, m in targeted] == ["no document has the ID US-gone", "no document has the ID US-x"]


def test_only_targets_are_reported(tmp_path: Path) -> None:
    files = {"docs/a.md": _doc("CAP-A-a", "`US-none`\n"), "docs/b.md": _doc("CAP-A-b", "`US-none`\n")}
    assert [file for file, _, _ in _found(check(RULE, tmp_path, files, targets=["docs/b.md"]))] == ["docs/b.md"]


def test_milestone_cycles_are_seen_through_untargeted_nodes(tmp_path: Path) -> None:
    files = {
        "docs/roadmap/MS-a.md": _doc("MS-a", header="depends_on: [MS-b]\n"),
        "docs/roadmap/MS-b.md": _doc("MS-b", header="depends_on: [MS-a]\n"),
        "docs/proposals/PROP-x/proposal.md": _doc("PROP-x", header="milestone: MS-a\n"),
    }
    found = check(RULE, tmp_path, files, targets=["docs/roadmap/MS-a.md"])
    assert len(found) == 1 and "dependency cycle includes MS-a" in found[0].message


def test_milestone_wrong_kind_and_historical_origins(tmp_path: Path) -> None:
    files = {
        "docs/roadmap/MS-a.md": _doc("MS-a", header="depends_on: [PROP-x]\n"),
        "docs/proposals/PROP-x/proposal.md": _doc(
            "PROP-x", header="milestone: PROP-x\ndecomposed_from: PROP-deleted\n"
        ),
    }
    messages = [v.message for v in check(RULE, tmp_path, files)]
    assert any("depends_on takes MS- IDs" in message for message in messages)
    assert any("milestone takes MS- IDs" in message for message in messages)
    assert not any("PROP-deleted" in message for message in messages)


def test_self_cycle_and_wrong_provenance_shape(tmp_path: Path) -> None:
    files = {
        "docs/roadmap/MS-a.md": _doc("MS-a", header="depends_on: [MS-a]\n"),
        "docs/proposals/PROP-x/proposal.md": _doc("PROP-x", header="supersedes: MS-a\n"),
    }
    messages = [v.message for v in check(RULE, tmp_path, files)]
    assert any("dependency cycle" in message for message in messages)
    assert any("supersedes takes PROP- IDs" in message for message in messages)


_GLOSSARY_HEADER = "| Term | Definition | Owner | Avoid | Code identifiers |\n| :--- | :--- | :--- | :--- | :--- |\n"


def test_glossary_owner_resolution_without_indexing_or_autofix(tmp_path: Path) -> None:
    from devkit_spec.documents import DocumentIndex

    glossary = _GLOSSARY_HEADER + (
        "| one | definition | `CAP-A-valid`, [ADR-missing] | | |\n"
        "| two | definition | `US-duplicate` | | |\n"
        "| three | definition | | | |\n"
    )
    files = {
        "docs/glossary.md": glossary,
        "docs/a.md": _doc("CAP-A-valid"),
        "docs/b.md": _doc("US-duplicate"),
        "docs/c.md": _doc("US-duplicate"),
    }
    found = check(RULE, tmp_path, files, targets=["docs/glossary.md"])
    assert _found(found) == [
        ("docs/glossary.md", 3, "no document has the ID ADR-missing"),
        ("docs/glossary.md", 4, "US-duplicate is declared by 2 documents: docs/b.md, docs/c.md"),
    ]
    assert all(not v.fixable for v in found)
    assert all(d.path != "docs/glossary.md" for d in DocumentIndex.load(tmp_path).documents)
    assert _found(check(RULE, tmp_path, targets=["docs/glossary.md"], fix=True)) == _found(found)
    assert (tmp_path / "docs/glossary.md").read_text() == glossary
    assert check(RULE, tmp_path, targets=["docs/a.md"]) == []
    assert check(RULE, tmp_path, targets=["docs/glossary.md"], exclude=["docs/glossary.md"]) == []


def test_glossary_only_visible_owner_cells_in_recognized_tables(tmp_path: Path) -> None:
    ignored_row = "| term | definition | `ADR-ignored` | | |\n"
    text = (
        "# Glossary\n\nProse `ADR-ignored`.\n\n"
        "```markdown\n" + _GLOSSARY_HEADER + ignored_row + "```\n\n"
        "<!--\n"
        + _GLOSSARY_HEADER
        + ignored_row
        + "-->\n\n"
        + _GLOSSARY_HEADER
        + "| `ADR-ignored` | `ADR-ignored` and a `pipe|code` and escaped \\| | `CAP-A-valid` | [ADR-ignored] | `ADR-ignored` |\n"
        + "| term | definition | <!-- `ADR-ignored` --> ~~`ADR-ignored`~~ \\`ADR-ignored\\` | | |\n"
        + "| term | definition | `[ADR-ignored]` [label](ADR-ignored) | | |\n"
        + "| term | definition | | | |\n\n"
        + "| Term | Definition | Notes |\n| --- | --- | --- |\n| x | y | `ADR-ignored` |\n\n"
        + "| Term | Definition | Owner | Avoid | Code identifiers |\n"
        + ignored_row
        + "\n"
        + _GLOSSARY_HEADER
        + "| last | definition | [CAP-A-valid] | | |\n"
    )
    assert (
        check(
            RULE,
            tmp_path,
            {
                "docs/glossary.md": text,
                "docs/a.md": _doc("CAP-A-valid"),
                "docs/other.md": _GLOSSARY_HEADER + ignored_row,
                "docs/packages/example/glossary.md": _GLOSSARY_HEADER + ignored_row,
            },
        )
        == []
    )


def test_glossary_table_state_ends_at_blank_or_fence(tmp_path: Path) -> None:
    row = "| term | definition | `ADR-missing` | | |\n"
    text = _GLOSSARY_HEADER + "\n" + row + "\n" + _GLOSSARY_HEADER + "```\nexample\n```\n" + row
    assert check(RULE, tmp_path, {"docs/glossary.md": text}) == []
    assert _found(check(RULE, tmp_path, {"docs/glossary.md": text + "\n" + _GLOSSARY_HEADER + row})) == [
        ("docs/glossary.md", 15, "no document has the ID ADR-missing")
    ]


def test_glossary_uses_staged_snapshot_contents(tmp_path: Path) -> None:
    import subprocess

    from devkit.rules.workspace.snapshot import git_snapshot, materialize_snapshot

    root = tmp_path / "repo"
    root.mkdir()

    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

    git("init", "-q")
    git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-qm", "init")
    (root / "docs").mkdir()
    glossary = root / "docs/glossary.md"
    glossary.write_text(_GLOSSARY_HEADER + "| term | definition | `ADR-missing` | | |\n")
    git("add", "docs/glossary.md")
    glossary.write_text(_GLOSSARY_HEADER + "| term | definition | | | |\n")
    snapshot = git_snapshot(root, staged=True)
    materialized = tmp_path / "snapshot"
    materialize_snapshot(snapshot, materialized)
    assert check(RULE, root) == []
    assert _found(check(RULE, materialized, targets=list(snapshot.changed))) == [
        ("docs/glossary.md", 3, "no document has the ID ADR-missing")
    ]


def test_glossary_compact_empty_cells_keep_owner_and_following_rows(tmp_path: Path) -> None:
    text = (
        _GLOSSARY_HEADER
        + "|term|definition|`ADR-missing`|||\n"
        + "| term | definition | `ADR-next` | | |\n"
        + "term|definition|`ADR-no-border`||\n"
        + "| term | definition |\n"
        + "| term | definition | `ADR-extra` | | | ignored surplus |\n"
    )
    assert _found(check(RULE, tmp_path, {"docs/glossary.md": text})) == [
        ("docs/glossary.md", 3, "no document has the ID ADR-missing"),
        ("docs/glossary.md", 4, "no document has the ID ADR-next"),
        ("docs/glossary.md", 5, "no document has the ID ADR-no-border"),
        ("docs/glossary.md", 7, "no document has the ID ADR-extra"),
    ]
