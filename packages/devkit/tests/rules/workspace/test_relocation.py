"""``relocate_links``: the link outcomes of a proposal handoff (a bundle moved to a spec, decisions and materials)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from devkit.rules import (
    LinkRelocation,
    RelocatedLink,
    UnresolvedLink,
    UnresolvedReason,
    relocate_links,
)

BUNDLE = "docs/proposals/PROP-linked"
SPEC = "specs/2026-10/20261014-linked"
ADR = "docs/decisions/2026-10/20261014-pick-engine.md"
MATERIALS = "docs/materials/2026-10/20261014-linked"


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return path


def _bundle_relocation(root: Path) -> LinkRelocation:
    bundle = root / BUNDLE
    return LinkRelocation(
        files={
            bundle: root / SPEC,
            bundle / "proposal.md": root / SPEC / "spec.md",
            bundle / "target-docs.md": root / SPEC / "target-docs.md",
            bundle / "decisions/PADR-pick-engine.md": root / ADR,
        },
        directories={bundle / "materials": root / MATERIALS},
        removed=[bundle],
        file_origins={root / ADR: bundle / "decisions/PADR-pick-engine.md"},
        directory_origins={root / SPEC: bundle, root / MATERIALS: bundle / "materials"},
    )


def test_links_into_a_moved_bundle_follow_it(tmp_path: Path) -> None:
    other = _write(
        tmp_path,
        "docs/proposals/PROP-other/proposal.md",
        "# Other\n"
        "See [prop](../PROP-linked/proposal.md), [blueprint](../PROP-linked/target-docs.md), "
        "[padr](../PROP-linked/decisions/PADR-pick-engine.md), [mat](../PROP-linked/materials/survey.md), "
        "[dir](../PROP-linked/).\n"
        "Ambiguous: [decisions](../PROP-linked/decisions/) and [missing](../PROP-linked/materials/absent/x.md).\n"
        "Keep: [ext](https://example.com/PROP-linked/proposal.md) [anchor](#top) "
        "[abs](/docs/proposals/PROP-linked/proposal.md) [query](?x)\n"
        "```md\n[code](../PROP-linked/proposal.md)\n```\n",
    )
    note = _write(tmp_path, "specs/note.md", "[p](../docs/proposals/PROP-linked/proposal.md)\n")
    untouched = _write(tmp_path, "docs/untouched.md", "[cap](capabilities/CAP-X.md)\n")

    report = relocate_links(tmp_path, [other, note, untouched], _bundle_relocation(tmp_path))

    assert report.files == ["docs/proposals/PROP-other/proposal.md", "specs/note.md"]
    assert report.unresolved == [
        UnresolvedLink(
            "docs/proposals/PROP-other/proposal.md", 3, "../PROP-linked/decisions/", UnresolvedReason.UNMAPPED
        )
    ]
    assert report.unresolved[0].to_dict() == {
        "path": "docs/proposals/PROP-other/proposal.md",
        "line": 3,
        "target": "../PROP-linked/decisions/",
        "reason": "unmapped",
    }
    got = other.read_text(encoding="utf-8")
    assert f"[prop](../../../{SPEC}/spec.md)" in got
    assert f"[blueprint](../../../{SPEC}/target-docs.md)" in got
    assert "[padr](../../decisions/2026-10/20261014-pick-engine.md)" in got
    assert "[mat](../../materials/2026-10/20261014-linked/survey.md)" in got
    assert f"[dir](../../../{SPEC})" in got
    assert "[decisions](../PROP-linked/decisions/)" in got
    # A link beneath a moved directory follows it, whether or not the file exists.
    assert "[missing](../../materials/2026-10/20261014-linked/absent/x.md)" in got
    assert (
        "Keep: [ext](https://example.com/PROP-linked/proposal.md) [anchor](#top) "
        "[abs](/docs/proposals/PROP-linked/proposal.md) [query](?x)\n" in got
    )
    assert "```md\n[code](../PROP-linked/proposal.md)\n```" in got
    assert note.read_text(encoding="utf-8") == "[p](2026-10/20261014-linked/spec.md)\n"
    assert untouched.read_text(encoding="utf-8") == "[cap](capabilities/CAP-X.md)\n"
    rewritten = {(r.path, r.line, r.old): r.new for r in report.rewritten}
    assert (
        rewritten[("specs/note.md", 1, "../docs/proposals/PROP-linked/proposal.md")]
        == "2026-10/20261014-linked/spec.md"
    )
    assert len(rewritten) == 7
    assert RelocatedLink("specs/note.md", 1, "a", "b").to_dict() == {
        "path": "specs/note.md",
        "line": 1,
        "from": "a",
        "to": "b",
    }


def test_moved_files_keep_their_targets_from_the_new_location(tmp_path: Path) -> None:
    _write(tmp_path, "docs/capabilities/lifecycle/CAP-X.md", "# cap\n")
    survey = _write(
        tmp_path,
        f"{MATERIALS}/survey.md",
        "# Survey\n"
        "[back](../proposal.md) [padr](../decisions/PADR-pick-engine.md#sec) "
        "[cap](../../../capabilities/lifecycle/CAP-X.md)\n"
        "[dirlink](../) [sibling](./notes.md)\n",
    )
    spec = _write(
        tmp_path,
        f"{SPEC}/spec.md",
        "Intro [CAP-X](../../capabilities/lifecycle/CAP-X.md). See [notes](materials/notes.md) "
        "and [self](proposal.md?plain).\n",
    )

    report = relocate_links(tmp_path, [survey, spec], _bundle_relocation(tmp_path))

    material = survey.read_text(encoding="utf-8")
    assert f"[back](../../../../{SPEC}/spec.md)" in material
    assert "[padr](../../../decisions/2026-10/20261014-pick-engine.md#sec)" in material
    assert "[cap](../../../capabilities/lifecycle/CAP-X.md)" in material  # the same target, the same spelling
    assert f"[dirlink](../../../../{SPEC})" in material
    assert "[sibling](./notes.md)" in material  # the author's spelling is kept
    assert spec.read_text(encoding="utf-8") == (
        "Intro [CAP-X](../../../docs/capabilities/lifecycle/CAP-X.md). "
        "See [notes](../../../docs/materials/2026-10/20261014-linked/notes.md) and [self](spec.md?plain).\n"
    )
    assert report.files == [f"{MATERIALS}/survey.md", f"{SPEC}/spec.md"] and report.unresolved == []


def test_a_file_written_as_another_file_resolves_from_it(tmp_path: Path) -> None:
    bundle = tmp_path / "docs/proposals/PROP-adr-links"
    adr_a = tmp_path / "docs/decisions/2026-10/20261014-pick-a.md"
    adr_b = tmp_path / "docs/decisions/2026-10/20261014-pick-b.md"
    spec = tmp_path / "specs/2026-10/20261014-adr-links/spec.md"
    _write(tmp_path, "docs/capabilities/x/CAP-X.md", "# cap\n")
    _write(
        tmp_path,
        adr_a.relative_to(tmp_path).as_posix(),
        "[cap](../../../capabilities/x/CAP-X.md) [b](PADR-pick-b.md) [p](../proposal.md)\n",
    )
    relocation = LinkRelocation(
        files={
            bundle / "proposal.md": spec,
            bundle / "decisions/PADR-pick-a.md": adr_a,
            bundle / "decisions/PADR-pick-b.md": adr_b,
        },
        removed=[bundle],
        file_origins={adr_a: bundle / "decisions/PADR-pick-a.md", adr_b: bundle / "decisions/PADR-pick-b.md"},
    )

    report = relocate_links(tmp_path, [adr_a], relocation)

    assert adr_a.read_text(encoding="utf-8") == (
        "[cap](../../capabilities/x/CAP-X.md) [b](20261014-pick-b.md) [p](../../../specs/2026-10/20261014-adr-links/spec.md)\n"
    )
    assert [(r.old, r.new) for r in report.rewritten] == [
        ("../../../capabilities/x/CAP-X.md", "../../capabilities/x/CAP-X.md"),
        ("PADR-pick-b.md", "20261014-pick-b.md"),
        ("../proposal.md", "../../../specs/2026-10/20261014-adr-links/spec.md"),
    ]


def test_carried_files_and_links_to_them(tmp_path: Path) -> None:
    bundle = tmp_path / "docs/proposals/PROP-relative"
    materials = tmp_path / "docs/materials/2026-10/20261014-relative"
    spec = tmp_path / "specs/2026-10/20261014-relative/spec.md"
    notes = _write(
        tmp_path,
        "docs/materials/2026-10/20261014-relative/notes.md",
        "# Notes\n[back](proposal.md) [mat](materials/a.md)\n",
    )
    readme = _write(tmp_path, "docs/README.md", "[notes](proposals/PROP-relative/notes.md)\n")
    relocation = LinkRelocation(
        files={bundle / "proposal.md": spec, bundle / "notes.md": materials / "notes.md"},
        directories={bundle / "materials": materials},
        removed=[bundle],
        file_origins={materials / "notes.md": bundle / "notes.md"},
        directory_origins={materials: bundle / "materials"},
    )

    report = relocate_links(tmp_path, [notes, readme], relocation)

    assert (
        notes.read_text(encoding="utf-8")
        == "# Notes\n[back](../../../../specs/2026-10/20261014-relative/spec.md) [mat](a.md)\n"
    )
    assert readme.read_text(encoding="utf-8") == "[notes](materials/2026-10/20261014-relative/notes.md)\n"
    assert report.unresolved == []


def test_a_moved_single_file(tmp_path: Path) -> None:
    single = tmp_path / "docs/proposals/PROP-single.md"
    story = _write(tmp_path, "docs/stories/US-a.md", "---\nid: US-a\n---\n[s](../proposals/PROP-single.md#why)\n")
    relocation = LinkRelocation(files={single: tmp_path / "specs/2026-10/20261014-single/spec.md"}, removed=[single])
    report = relocate_links(tmp_path, [story], relocation)
    assert (
        story.read_text(encoding="utf-8")
        == "---\nid: US-a\n---\n[s](../../specs/2026-10/20261014-single/spec.md#why)\n"
    )
    assert [(r.path, r.line) for r in report.rewritten] == [("docs/stories/US-a.md", 4)]


def test_relative_paths_resolve_against_the_root_and_the_deepest_directory_wins(tmp_path: Path) -> None:
    page = _write(tmp_path, "page.md", "[a](old/a.md) [b](old/sub/b.md) [c](old/sub/deep/c.md) [gone](removed/x.md)\n")
    relocation = LinkRelocation(
        directories={"old": "new", "old/sub": "elsewhere/sub"},
        removed=["removed"],
    )
    report = relocate_links(tmp_path, ["page.md"], relocation)
    assert page.read_text(encoding="utf-8") == (
        "[a](new/a.md) [b](elsewhere/sub/b.md) [c](elsewhere/sub/deep/c.md) [gone](removed/x.md)\n"
    )
    assert [(u.target, u.reason) for u in report.unresolved] == [("removed/x.md", UnresolvedReason.UNMAPPED)]


def test_a_link_to_a_moved_directory_itself_needs_an_exact_entry(tmp_path: Path) -> None:
    page = _write(tmp_path, "page.md", "[dir](old/) [file](old/a.md)\n")
    report = relocate_links(tmp_path, [page], LinkRelocation(directories={"old": "new"}))
    assert page.read_text(encoding="utf-8") == "[dir](old/) [file](new/a.md)\n"
    assert [(u.target, u.reason) for u in report.unresolved] == [("old/", UnresolvedReason.UNMAPPED)]
    report = relocate_links(tmp_path, [page], LinkRelocation(files={"old": "new"}, directories={"old": "new"}))
    assert page.read_text(encoding="utf-8") == "[dir](new) [file](new/a.md)\n" and report.unresolved == []


def test_bytes_line_endings_and_link_syntax_are_kept(tmp_path: Path) -> None:
    page = _write(tmp_path, "page.md", 'a\r\n[x](<old/a b.md> "title") ![img](old/i.png)\r\nend')
    page.chmod(0o640)
    relocate_links(tmp_path, [page], LinkRelocation(directories={"old": "new"}))
    assert page.read_bytes() == b'a\r\n[x](<new/a b.md> "title") ![img](new/i.png)\r\nend'
    assert page.stat().st_mode & 0o777 == 0o640


def test_a_symlinked_file_is_written_through(tmp_path: Path) -> None:
    real = _write(tmp_path, "real.md", "[a](old/a.md)\n")
    link = tmp_path / "link.md"
    link.symlink_to(real)
    report = relocate_links(tmp_path, [link], LinkRelocation(directories={"old": "new"}))
    assert link.is_symlink() and real.read_text(encoding="utf-8") == "[a](new/a.md)\n"
    assert report.files == ["link.md"]


def test_unreadable_and_unwritable_files_are_reported(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root ignores file permissions")
    binary = tmp_path / "binary.md"
    binary.write_bytes(b"\xff[a](old/a.md)\n")
    locked = _write(tmp_path, "locked/page.md", "[a](../old/a.md)\n")
    (tmp_path / "locked").chmod(0o555)
    try:
        report = relocate_links(
            tmp_path, [tmp_path / "missing.md", binary, locked], LinkRelocation(directories={"old": "new"})
        )
    finally:
        (tmp_path / "locked").chmod(0o755)
    assert report.unresolved == [
        UnresolvedLink("missing.md", 0, "", UnresolvedReason.UNREADABLE),
        UnresolvedLink("binary.md", 0, "", UnresolvedReason.UNREADABLE),
        UnresolvedLink("locked/page.md", 0, "", UnresolvedReason.UNWRITABLE),
    ]
    assert report.files == [] and report.rewritten == []
    assert locked.read_text(encoding="utf-8") == "[a](../old/a.md)\n"


def test_string_maps_need_no_conversion(tmp_path: Path) -> None:
    # Mapping keys are invariant: a plain dict[str, str] must type-check as LinkRelocation's maps.
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/a.md").write_text("[x](old.md)\n", encoding="utf-8")
    moved: dict[str, str] = {"docs/old.md": "docs/new.md"}
    report = relocate_links(tmp_path, ["docs/a.md"], LinkRelocation(files=moved, directories=moved))
    assert (tmp_path / "docs/a.md").read_text(encoding="utf-8") == "[x](new.md)\n"
    assert [(item.old, item.new) for item in report.rewritten] == [("old.md", "new.md")]
