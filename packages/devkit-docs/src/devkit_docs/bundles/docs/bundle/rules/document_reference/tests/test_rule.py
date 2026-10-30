"""``RULE-document-reference``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.rules import RulesRunError, Violation
from devkit_agt.features.rules.services.testing import check, load_rule

RULE = load_rule(__file__)


def _found(violations: list[Violation]) -> list[tuple[str, int, str]]:
    """``(file, line, message)`` of the violations that remain (not fixed)."""
    return [(v.file, v.line, v.message) for v in violations if not v.fixed]


def _doc(document_id: str, body: str = "", header: str = "", status: str = "active") -> str:
    return f"---\nid: {document_id}\nstatus: {status}\n{header}---\n{body}"


def test_resolvable_references_pass(tmp_path: Path) -> None:
    files = {
        "docs/a.md": _doc("CAP-A-a", "`UC-b`\n", "usecases:\n  - UC-b\n"),
        "docs/b.md": _doc("UC-b", "`CAP-A-a`\n", "capabilities: [CAP-A-a]\n"),
    }
    assert check(RULE, tmp_path, files) == []


def test_reference_problems(tmp_path: Path) -> None:
    files = {"docs/a.md": _doc("CAP-A-a", "`UC-none`\n", "usecases:\n  - CAP-A-a\n  - docs/b.md\nspec: [x]\n")}
    assert _found(check(RULE, tmp_path, files)) == [
        ("docs/a.md", 7, "spec must be one ID"),
        ("docs/a.md", 5, "usecases takes UC- IDs, got CAP-A-a"),
        ("docs/a.md", 6, "usecases must contain a full document ID, got 'docs/b.md'"),
        ("docs/a.md", 9, "no document has the ID UC-none"),
    ]


def test_duplicates_and_shared_proposal_slugs(tmp_path: Path) -> None:
    files = {
        "docs/a.md": _doc("UC-dup"),
        "docs/b.md": _doc("UC-dup"),
        "docs/proposals/x/proposal.md": _doc("PROP-x"),
        "specs/2026-10/20261001-x/spec.md": _doc("SPEC-x"),
    }
    messages = _found(check(RULE, tmp_path, files))
    assert ("docs/a.md", 1, "UC-dup is declared by 2 documents: docs/a.md, docs/b.md") in messages
    assert ("docs/b.md", 1, "UC-dup is declared by 2 documents: docs/a.md, docs/b.md") in messages
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
        "docs/b/two.md": _doc("UC-two"),
        "docs/b/README.md": "# readme\n",
    }
    assert _found(check(RULE, tmp_path, files)) == [
        ("docs/a/one.md", 5, "internal document link ../b/two.md must be the ID `UC-two`")
    ]


def test_history_and_materials_are_skipped_unless_targeted(tmp_path: Path) -> None:
    files = {
        "specs/2026-10/20261001-done/spec.md": _doc("SPEC-done", "`UC-gone` [UC-x]\n", status="completed"),
        "docs/materials/m.md": _doc("MAT-m", "`UC-gone`\n"),
    }
    assert check(RULE, tmp_path, files) == []
    targeted = _found(check(RULE, tmp_path, targets=["specs/2026-10/20261001-done/spec.md"]))
    assert [m for _, _, m in targeted] == ["no document has the ID UC-gone", "no document has the ID UC-x"]


def test_only_targets_are_reported(tmp_path: Path) -> None:
    files = {"docs/a.md": _doc("CAP-A-a", "`UC-none`\n"), "docs/b.md": _doc("CAP-A-b", "`UC-none`\n")}
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


def _owners(violations: list[Violation]) -> list[tuple[str, int, str]]:
    """The findings of the glossary Owner pass alone (the steering pass also reads other cited IDs)."""
    return _found([v for v in violations if "glossary Owner" in v.remediation])


def test_glossary_owner_resolution_without_indexing_or_autofix(tmp_path: Path) -> None:
    from devkit_docs.features.documents import DocumentIndex

    glossary = _GLOSSARY_HEADER + (
        "| one | definition | `CAP-A-valid`, [ADR-missing] | | |\n"
        "| two | definition | `UC-duplicate` | | |\n"
        "| three | definition | | | |\n"
    )
    files = {
        "docs/steering/glossary.md": glossary,
        "docs/a.md": _doc("CAP-A-valid"),
        "docs/b.md": _doc("UC-duplicate"),
        "docs/c.md": _doc("UC-duplicate"),
    }
    found = check(RULE, tmp_path, files, targets=["docs/steering/glossary.md"])
    assert _found(found) == [
        ("docs/steering/glossary.md", 3, "no document has the ID ADR-missing"),
        ("docs/steering/glossary.md", 4, "UC-duplicate is declared by 2 documents: docs/b.md, docs/c.md"),
    ]
    assert all(not v.fixable for v in found)
    assert all(d.path != "docs/steering/glossary.md" for d in DocumentIndex.load(tmp_path).documents)
    assert _found(check(RULE, tmp_path, targets=["docs/steering/glossary.md"], fix=True)) == _found(found)
    assert (tmp_path / "docs/steering/glossary.md").read_text() == glossary
    assert check(RULE, tmp_path, targets=["docs/a.md"]) == []
    assert check(RULE, tmp_path, targets=["docs/steering/glossary.md"], exclude=["docs/steering/glossary.md"]) == []


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
    found = check(
        RULE,
        tmp_path,
        {
            "docs/steering/glossary.md": text,
            "docs/a.md": _doc("CAP-A-valid"),
            "docs/other.md": _GLOSSARY_HEADER + ignored_row,
            "docs/packages/example/glossary.md": _GLOSSARY_HEADER + ignored_row,
        },
    )
    assert _owners(found) == []
    # Outside Owner cells, the steering pass reports each visible backticked ID once, in the steering glossary only.
    assert {(file, line) for file, line, _ in _found(found)} == {
        ("docs/steering/glossary.md", 3),
        ("docs/steering/glossary.md", 19),
        ("docs/steering/glossary.md", 26),
        ("docs/steering/glossary.md", 29),
    }


def test_glossary_table_state_ends_at_blank_or_fence(tmp_path: Path) -> None:
    row = "| term | definition | `ADR-missing` | | |\n"
    text = _GLOSSARY_HEADER + "\n" + row + "\n" + _GLOSSARY_HEADER + "```\nexample\n```\n" + row
    assert _owners(check(RULE, tmp_path, {"docs/steering/glossary.md": text})) == []
    assert _owners(check(RULE, tmp_path, {"docs/steering/glossary.md": text + "\n" + _GLOSSARY_HEADER + row})) == [
        ("docs/steering/glossary.md", 15, "no document has the ID ADR-missing")
    ]


def test_glossary_uses_staged_snapshot_contents(tmp_path: Path) -> None:
    import subprocess

    from devkit_agt.features.rules.repositories.workspace.snapshot import git_snapshot, materialize_snapshot

    root = tmp_path / "repo"
    root.mkdir()

    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

    git("init", "-q")
    git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-qm", "init")
    (root / "docs/steering").mkdir(parents=True)
    glossary = root / "docs/steering/glossary.md"
    glossary.write_text(_GLOSSARY_HEADER + "| term | definition | `ADR-missing` | | |\n")
    git("add", "docs/steering/glossary.md")
    glossary.write_text(_GLOSSARY_HEADER + "| term | definition | | | |\n")
    snapshot = git_snapshot(root, staged=True)
    materialized = tmp_path / "snapshot"
    materialize_snapshot(snapshot, materialized)
    assert check(RULE, root) == []
    assert _found(check(RULE, materialized, targets=list(snapshot.changed))) == [
        ("docs/steering/glossary.md", 3, "no document has the ID ADR-missing")
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
    assert _found(check(RULE, tmp_path, {"docs/steering/glossary.md": text})) == [
        ("docs/steering/glossary.md", 3, "no document has the ID ADR-missing"),
        ("docs/steering/glossary.md", 4, "no document has the ID ADR-next"),
        ("docs/steering/glossary.md", 5, "no document has the ID ADR-no-border"),
        ("docs/steering/glossary.md", 7, "no document has the ID ADR-extra"),
    ]


def _aliased(document_id: str, aliases: str, body: str = "", header: str = "", status: str = "active") -> str:
    return _doc(document_id, body, f"aliases: [{aliases}]\n{header}", status)


def test_alias_references_are_fixed_in_current_documents(tmp_path: Path) -> None:
    files = {
        "docs/new.md": _aliased("UC-new", "UC-old", "Formerly `UC-old`.\n"),
        "docs/adr-new.md": _aliased("ADR-new", "ADR-old"),
        "docs/cap.md": _doc("CAP-A-a", "See [UC-old] and `ADR-old`.\n", "usecases:\n  - 'UC-old'\n"),
    }
    violations = check(RULE, tmp_path, files)
    assert {(v.file, v.message, v.fixable) for v in violations} == {
        ("docs/cap.md", "UC-old is an alias of UC-new; reference `UC-new`", True),
        ("docs/cap.md", "prose reference UC-old must be written `UC-old`, not [UC-old]", True),
        ("docs/cap.md", "ADR-old is an alias of ADR-new; reference `ADR-new`", True),
    }
    assert sum(v.message.startswith("UC-old is an alias") for v in violations) == 2
    fixed = check(RULE, tmp_path, fix=True)
    assert _found(fixed) == []
    text = (tmp_path / "docs/cap.md").read_text()
    assert "usecases:\n  - 'UC-new'\n" in text and text.endswith("See `UC-new` and `ADR-new`.\n")
    # A self-mention of a retired ID is deliberate: neither reported nor rewritten.
    assert (tmp_path / "docs/new.md").read_text() == files["docs/new.md"]
    assert check(RULE, tmp_path) == []


def test_alias_references_in_history_stay(tmp_path: Path) -> None:
    files = {
        "docs/new.md": _aliased("UC-new", "UC-old"),
        "specs/2026-10/20261001-done/spec.md": _doc("SPEC-done", "`UC-old`\n", status="completed"),
        "docs/roadmap/MS-done.md": _doc("MS-done", "`UC-old`\n", status="done"),
    }
    assert check(RULE, tmp_path, files) == []
    check(RULE, tmp_path, fix=True)
    for name, text in files.items():
        assert (tmp_path / name).read_text() == text


def test_alias_references_in_decision_records_are_fixed(tmp_path: Path) -> None:
    files = {
        "docs/new.md": _aliased("UC-new", "UC-old"),
        "docs/decisions/2026-10/20261001-x.md": _doc("ADR-x", "`UC-old`\n", status="accepted"),
        "docs/proposals/PROP-p/decisions/PADR-p.md": _doc("PADR-p", "`UC-old`\n", status="draft"),
        "docs/proposals/PROP-p/proposal.md": _doc("PROP-p", status="draft"),
    }
    assert {(v.file, v.fixable) for v in check(RULE, tmp_path, files)} == {
        ("docs/decisions/2026-10/20261001-x.md", True),
        ("docs/proposals/PROP-p/decisions/PADR-p.md", True),
    }
    check(RULE, tmp_path, fix=True)
    assert (tmp_path / "docs/decisions/2026-10/20261001-x.md").read_text().endswith("`UC-new`\n")
    assert (tmp_path / "docs/proposals/PROP-p/decisions/PADR-p.md").read_text().endswith("`UC-new`\n")
    assert check(RULE, tmp_path) == []


def test_relation_field_typing_is_kept_for_aliases(tmp_path: Path) -> None:
    files = {
        "docs/new.md": _aliased("CAP-A-new", "CAP-A-old"),
        "docs/usecase.md": _doc("UC-s", header="usecases: [CAP-A-old]\n"),
    }
    assert _found(check(RULE, tmp_path, files)) == [("docs/usecase.md", 4, "usecases takes UC- IDs, got CAP-A-old")]


def test_alias_shape_and_collisions_are_identity_checks(tmp_path: Path) -> None:
    files = {
        "docs/materials/m.md": _aliased("MAT-m", "MAT-old, CAP-A-x", "`UC-gone` `MAT-old`\n"),
        "docs/materials/n.md": _aliased("MAT-n", "MAT-old"),
        "docs/a.md": _aliased("CAP-A-a", "CAP-A-b"),
        "docs/b.md": _doc("CAP-A-b"),
        "docs/ref.md": _doc("UC-r", "`MAT-old`\n"),
    }
    found = _found(check(RULE, tmp_path, files))
    assert ("docs/materials/m.md", 4, "alias CAP-A-x must have the document's own prefix MAT-") in found
    collision = "alias MAT-old collides: it is declared by docs/materials/m.md, docs/materials/n.md"
    assert ("docs/materials/m.md", 1, collision) in found and ("docs/materials/n.md", 1, collision) in found
    shadowed = "alias CAP-A-b collides: it is declared by docs/b.md, docs/a.md"
    assert ("docs/a.md", 1, shadowed) in found and ("docs/b.md", 1, shadowed) in found
    assert (
        "docs/ref.md",
        5,
        "MAT-old is an alias declared by 2 documents: docs/materials/m.md, docs/materials/n.md",
    ) in found
    # References written inside materials are not checked.
    assert not any(file.startswith("docs/materials/") and "UC-gone" in message for file, _, message in found)
    check(RULE, tmp_path, fix=True)
    assert (tmp_path / "docs/ref.md").read_text() == files["docs/ref.md"]


def test_reference_to_a_material_alias_is_fixed(tmp_path: Path) -> None:
    files = {"docs/materials/m.md": _aliased("MAT-m", "MAT-old"), "docs/ref.md": _doc("UC-r", "`MAT-old`\n")}
    assert [v.message for v in check(RULE, tmp_path, files)] == ["MAT-old is an alias of MAT-m; reference `MAT-m`"]
    check(RULE, tmp_path, fix=True)
    assert (tmp_path / "docs/ref.md").read_text().endswith("`MAT-m`\n")


def test_glossary_owner_naming_an_alias_is_reported_not_fixed(tmp_path: Path) -> None:
    glossary = _GLOSSARY_HEADER + "| one | definition | `CAP-A-old` | | |\n"
    files = {"docs/steering/glossary.md": glossary, "docs/a.md": _aliased("CAP-A-new", "CAP-A-old")}
    found = check(RULE, tmp_path, files, targets=["docs/steering/glossary.md"])
    assert _found(found) == [
        ("docs/steering/glossary.md", 3, "Owner CAP-A-old is an alias of CAP-A-new; name `CAP-A-new`")
    ]
    assert not found[0].fixable
    check(RULE, tmp_path, targets=["docs/steering/glossary.md"], fix=True)
    assert (tmp_path / "docs/steering/glossary.md").read_text() == glossary


def test_cycles_through_aliases(tmp_path: Path) -> None:
    files = {
        "docs/roadmap/MS-a.md": _doc("MS-a", header="depends_on: [MS-b-old]\n"),
        "docs/roadmap/MS-b.md": _aliased("MS-b", "MS-b-old", header="depends_on: [MS-a]\n"),
        "docs/proposals/PROP-x/proposal.md": _doc("PROP-x", header="depends_on: [PROP-y-old]\n", status="draft"),
        "docs/proposals/PROP-y/proposal.md": _aliased("PROP-y", "PROP-y-old", header="depends_on: [PROP-x]\n"),
    }
    messages = [v.message for v in check(RULE, tmp_path, files)]
    assert "milestone dependency cycle includes MS-a" in messages
    assert "unit dependency cycle includes PROP-x" in messages
    assert "PROP-y-old is an alias of PROP-y; reference `PROP-y`" in messages


def test_late_proposal_reference_is_fixed_to_the_canonical_spec(tmp_path: Path) -> None:
    files = {
        "specs/2026-10/20261001-new/spec.md": _aliased("SPEC-new", "SPEC-old"),
        "docs/a.md": _doc("CAP-A-a", "`PROP-old`\n"),
    }
    assert [v.message for v in check(RULE, tmp_path, files)] == ["PROP-old was handed off; reference `SPEC-new`"]
    check(RULE, tmp_path, fix=True)
    assert (tmp_path / "docs/a.md").read_text().endswith("`SPEC-new`\n")
    assert check(RULE, tmp_path) == []


def test_handed_off_proposal_in_targeted_history_is_accepted(tmp_path: Path) -> None:
    # Handoff rewrites live references only; history cited the proposal while it existed and is never rewritten.
    done = "specs/2026-10/20261001-done/spec.md"
    files = {
        "specs/2026-10/20261002-x/spec.md": _doc("SPEC-x", "", "proposal: PROP-x\n"),
        done: _doc("SPEC-done", "Integrates before `PROP-x`.\n", "depends_on: [PROP-x]\n", status="completed"),
        "docs/roadmap/MS-done.md": _doc("MS-done", "`PROP-x`\n", status="done"),
    }
    targets = [done, "docs/roadmap/MS-done.md"]
    assert check(RULE, tmp_path, files, targets=targets) == []
    check(RULE, tmp_path, targets=targets, fix=True)
    for name, text in files.items():
        assert (tmp_path / name).read_text() == text


def test_handed_off_proposal_in_a_current_document_stays_fixable(tmp_path: Path) -> None:
    files = {
        "specs/2026-10/20261002-x/spec.md": _doc("SPEC-x"),
        "docs/a.md": _doc("CAP-A-a", "`PROP-x`\n"),
        "specs/2026-10/20261001-done/spec.md": _doc("SPEC-done", "`PROP-x`\n", status="completed"),
    }
    violations = check(RULE, tmp_path, files)
    assert [(v.file, v.message, v.fixable) for v in violations] == [
        ("docs/a.md", "PROP-x was handed off; reference `SPEC-x`", True)
    ]


def test_unknown_proposal_in_targeted_history_stays_an_error(tmp_path: Path) -> None:
    done = "specs/2026-10/20261001-done/spec.md"
    files = {done: _doc("SPEC-done", "`PROP-gone`\n", "depends_on: [PROP-gone]\n", status="completed")}
    violations = check(RULE, tmp_path, files, targets=[done])
    assert sorted((v.message, v.fixable) for v in violations) == [
        ("depends_on target PROP-gone resolves to 0 documents; expected one anchor", False),
        ("no document has the ID PROP-gone", False),
    ]


def test_proposal_beside_a_spec_alias_shares_its_slug(tmp_path: Path) -> None:
    files = {
        "specs/2026-10/20261001-new/spec.md": _aliased("SPEC-new", "SPEC-old"),
        "docs/proposals/PROP-old/proposal.md": _doc("PROP-old", status="draft"),
    }
    messages = [m for _, _, m in _found(check(RULE, tmp_path, files))]
    assert any(m.startswith("PROP-old shares its slug with SPEC-old") for m in messages)


def test_the_old_glossary_path_is_no_longer_read(tmp_path: Path) -> None:
    files = {"docs/glossary.md": _GLOSSARY_HEADER + "| term | definition | `ADR-missing` | | |\n"}
    assert check(RULE, tmp_path, files) == []


def test_ids_cited_in_steering_files_resolve_without_fixes_or_edges(tmp_path: Path) -> None:
    from devkit_docs.features.documents import DocumentIndex

    product = (
        "---\ntitle: Product\nsummary: Read before naming a feature.\n---\n"
        "See `CAP-A-missing`, `CAP-A-old` and `CAP-A-new`.\n\n```\n`CAP-A-fenced`\n```\n"
    )
    glossary = _GLOSSARY_HEADER + "| one | definition | `CAP-A-gone` | | |\n\nProse `CAP-A-gone`.\n"
    files = {
        "docs/steering/product.md": product,
        "docs/steering/glossary.md": glossary,
        "docs/steering/README.md": "`CAP-A-readme`\n",
        "docs/steering/sub/a.md": "`CAP-A-nested`\n",
        "docs/a.md": _aliased("CAP-A-new", "CAP-A-old"),
    }
    found = check(RULE, tmp_path, files)
    assert sorted(_found(found)) == [
        ("docs/steering/glossary.md", 3, "no document has the ID CAP-A-gone"),
        ("docs/steering/glossary.md", 5, "no document has the ID CAP-A-gone"),
        ("docs/steering/product.md", 5, "CAP-A-old is an alias of CAP-A-new; name `CAP-A-new`"),
        ("docs/steering/product.md", 5, "no document has the ID CAP-A-missing"),
    ]
    assert all(not v.fixable for v in found)
    check(RULE, tmp_path, fix=True)
    assert (tmp_path / "docs/steering/product.md").read_text() == product
    index = DocumentIndex.load(tmp_path)
    assert all(not d.path.startswith("docs/steering/") for d in index.documents)
    assert check(RULE, tmp_path, targets=["docs/a.md"]) == []


_QUICK = ("docs/development/x.md", "guides/install/y.md", "packages/p/README.md", "tools/t/README.md")


def test_an_alias_cited_in_a_quick_reference_is_fixed(tmp_path: Path) -> None:
    files: dict[str, str] = {"docs/a.md": _aliased("ADR-new", "ADR-old")}
    files.update({path: "# Notes\n\nSee `ADR-old` and `ADR-new`; ADR-old in prose stays.\n" for path in _QUICK})
    violations = check(RULE, tmp_path, files)
    assert sorted((v.file, v.line, v.column, v.message, v.fixable) for v in violations) == [
        (path, 3, 5, "ADR-old is an alias of ADR-new; reference `ADR-new`", True) for path in sorted(_QUICK)
    ]
    fixed = check(RULE, tmp_path, fix=True)
    assert all(v.fixed for v in fixed)
    for path in _QUICK:
        assert (tmp_path / path).read_text() == "# Notes\n\nSee `ADR-new` and `ADR-new`; ADR-old in prose stays.\n"
    assert check(RULE, tmp_path) == []


def test_an_unresolved_id_cited_in_a_quick_reference_is_an_error(tmp_path: Path) -> None:
    quick = "guides/y.md"
    text = "`UC-none` `UC-dup` `UC-shared`\n"
    files = {
        "docs/a.md": _aliased("UC-a", "UC-shared"),
        "docs/b.md": _aliased("UC-b", "UC-shared"),
        "docs/c.md": _doc("UC-dup"),
        "docs/d.md": _doc("UC-dup"),
        quick: text,
    }
    found = [v for v in check(RULE, tmp_path, files) if v.file == quick]
    assert [(v.line, v.column, v.message, v.fixable) for v in found] == [
        (1, 1, "no document has the ID UC-none", False),
        (1, 11, "UC-dup is declared by 2 documents: docs/c.md, docs/d.md", False),
        (1, 20, "UC-shared is an alias declared by 2 documents: docs/a.md, docs/b.md", False),
    ]
    check(RULE, tmp_path, fix=True)
    assert (tmp_path / quick).read_text() == text


def test_only_visible_citations_of_unindexed_quick_references_are_checked(tmp_path: Path) -> None:
    masked = (
        "UC-plain in prose, `see UC-span` with more text, ~~`UC-struck`~~, \\`UC-escaped\\`.\n\n"
        "<!-- `UC-comment` -->\n\n```\n`UC-fenced`\n```\n\n    `UC-indented`\n"
    )
    files = {
        "docs/development/masked.md": masked,
        "README.md": "`UC-root`\n",
        "packages/p/docs/README.md": "`UC-nested`\n",
        "examples/README.md": "`UC-example`\n",
        "docs/development/indexed.md": _doc("CAP-A-indexed", "`UC-indexed`\n"),
    }
    # The ID-bearing file is checked once, as an indexed document.
    assert _found(check(RULE, tmp_path, files)) == [
        ("docs/development/indexed.md", 5, "no document has the ID UC-indexed")
    ]


def test_quick_references_follow_targets_and_exclusions(tmp_path: Path) -> None:
    files = {
        "docs/a.md": _aliased("UC-new", "UC-old"),
        "guides/a.md": "`UC-old`\n",
        "guides/b.md": "`UC-old`\n",
    }
    assert [v.file for v in check(RULE, tmp_path, files, targets=["guides/b.md"])] == ["guides/b.md"]
    assert [v.file for v in check(RULE, tmp_path, exclude=["guides/a.md"])] == ["guides/b.md"]
    check(RULE, tmp_path, targets=["guides/b.md"], fix=True)
    assert (tmp_path / "guides/a.md").read_text() == "`UC-old`\n"
    assert (tmp_path / "guides/b.md").read_text() == "`UC-new`\n"
    (tmp_path / "guides/b.md").write_text("`UC-old`\n")
    check(RULE, tmp_path, exclude=["guides/a.md"], fix=True)
    assert (tmp_path / "guides/a.md").read_text() == "`UC-old`\n"
    assert (tmp_path / "guides/b.md").read_text() == "`UC-new`\n"


def test_the_quick_reference_set_is_a_setting(tmp_path: Path) -> None:
    files = {"notes/n.md": "`UC-none`\n", "guides/y.md": "`UC-none`\n"}
    custom = check(RULE, tmp_path, files, settings={"quick_references": ["notes/**/*.md"]})
    assert [v.file for v in custom] == ["notes/n.md"]
    assert check(RULE, tmp_path, settings={"quick_references": []}) == []
    with pytest.raises(RulesRunError) as raised:
        check(RULE, tmp_path, settings={"quick_references": ["../x"]})
    assert [problem.code for problem in raised.value.problems] == ["RULES_SETTINGS_INVALID"]


def test_the_guide_documents_the_quick_references_and_the_decision_record_fix() -> None:
    guide = (Path(__file__).parents[1] / "guide.md").read_text()
    assert "never rewrites an alias reference in an ADR or PADR" not in guide
    assert "`quick_references`" in guide
    for default in ("docs/development/**/*.md", "guides/**/*.md", "packages/*/README.md", "tools/*/README.md"):
        assert f"`{default}`" in guide, default
