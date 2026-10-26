"""Proposal handoff into a materials directory that already exists (``SPEC-merge-proposal-materials-at-handoff``)."""

from __future__ import annotations

import errno
import os
import stat
from collections.abc import Callable
from pathlib import Path

import pytest
from spec_support.proposals import MONTH, STAMP, TODAY, accept
from spec_support.types import Write

from devkit_spec.base.errors import ProposalHandoffError, ProposalInvalidError, ProposalTargetExistsError
from devkit_spec.features.proposals import create_padr, create_proposal, handoff_proposal
from devkit_spec.features.proposals.usecases import handoff as handoff_module

Snapshot = dict[str, tuple[str, bytes, int]]


def _dest(slug: str) -> str:
    return f"docs/materials/{MONTH}/{STAMP}-{slug}"


def _new(root: Path, slug: str) -> Path:
    """A scaffolded, accepted bundle with one PADR; returns its directory."""
    created = create_proposal(root, slug, today=TODAY)
    create_padr(root, slug, f"Pick {slug}")
    accept(root / created.path)
    return (root / created.path).parent


def _snapshot(top: Path) -> Snapshot:
    """Every path under ``top`` (``top`` included) by ``lstat``: its type, bytes or link text, and inode."""
    found: Snapshot = {}
    if not os.path.lexists(top):
        return found
    paths = [top, *top.rglob("*")]
    for path in paths:
        info = path.lstat()
        rel = path.relative_to(top).as_posix()
        if stat.S_ISLNK(info.st_mode):
            found[rel] = ("link", os.readlink(path).encode(), info.st_ino)
        elif stat.S_ISDIR(info.st_mode):
            found[rel] = ("dir", b"", info.st_ino)
        elif stat.S_ISREG(info.st_mode):
            found[rel] = ("file", path.read_bytes(), info.st_ino)
        else:
            found[rel] = ("other", b"", info.st_ino)
    return found


def _kept(before: Snapshot, after: Snapshot) -> bool:
    """Whether every path of ``before`` is in ``after`` unchanged, inode included."""
    return all(after.get(rel) == entry for rel, entry in before.items())


def test_merges_disjoint_materials_into_an_existing_directory(workspace: Path, write: Write) -> None:
    bundle = _new(workspace, "disjoint")
    dest = workspace / _dest("disjoint")
    write(f"{_dest('disjoint')}/bench.json", '{"ms": 12}\n')
    write(f"{_dest('disjoint')}/nested/run-1.txt", "run 1\n")
    write("docs/proposals/PROP-disjoint/materials/design.md", "# Design\n")
    write("docs/proposals/PROP-disjoint/materials/nested/run-2.txt", "run 2\n")
    write("docs/proposals/PROP-disjoint/materials/fresh/deep/d.txt", "deep\n")
    write("docs/proposals/PROP-disjoint/notes.md", "# Notes\n")
    before = _snapshot(dest)

    result = handoff_proposal(workspace, "disjoint", today=TODAY)

    assert result.materials == _dest("disjoint")
    assert result.materials_merged is True and result.dropped_duplicates == []
    assert result.to_dict()["materials_merged"] is True and result.to_dict()["dropped_duplicates"] == []
    assert _kept(before, _snapshot(dest))
    assert (dest / "design.md").read_text(encoding="utf-8") == "# Design\n"
    assert (dest / "nested/run-2.txt").read_text(encoding="utf-8") == "run 2\n"
    assert (dest / "fresh/deep/d.txt").read_text(encoding="utf-8") == "deep\n"
    assert (dest / "notes.md").read_text(encoding="utf-8") == "# Notes\n"
    assert not bundle.exists()
    assert (workspace / f"docs/decisions/{MONTH}/{STAMP}-pick-disjoint.md").is_file()


def test_without_an_existing_directory_nothing_is_merged(workspace: Path, write: Write) -> None:
    _new(workspace, "fresh")
    write("docs/proposals/PROP-fresh/materials/a.md", "# a\n")
    result = handoff_proposal(workspace, "fresh", today=TODAY)
    assert result.materials == _dest("fresh")
    assert result.materials_merged is False and result.dropped_duplicates == []


def test_drops_byte_identical_duplicates_and_keeps_the_destination_copy(workspace: Path, write: Write) -> None:
    _new(workspace, "dups")
    write(f"{_dest('dups')}/same.md", "# Same\n")
    write(f"{_dest('dups')}/notes.md", "# Notes\n")
    write("docs/proposals/PROP-dups/materials/same.md", "# Same\n")
    write("docs/proposals/PROP-dups/materials/other.md", "# Other\n")
    write("docs/proposals/PROP-dups/notes.md", "# Notes\n")  # a carried extra identical to a pre-existing file
    write("docs/usecases/UC-a.md", "---\nid: UC-a\n---\n[same](../proposals/PROP-dups/materials/same.md)\n")
    dest = workspace / _dest("dups")
    before = _snapshot(dest)

    result = handoff_proposal(workspace, "dups", today=TODAY)

    assert result.materials_merged is True
    assert result.dropped_duplicates == [f"{_dest('dups')}/notes.md", f"{_dest('dups')}/same.md"]
    assert _kept(before, _snapshot(dest))
    assert (dest / "other.md").is_file()
    # A link to the dropped copy reaches the kept one.
    use_case = (workspace / "docs/usecases/UC-a.md").read_text(encoding="utf-8")
    assert f"[same](../materials/{MONTH}/{STAMP}-dups/same.md)" in use_case


def _different_content(root: Path, write: Write) -> tuple[str, str]:
    write(f"{_dest('clash')}/a.md", "theirs\n")
    write("docs/proposals/PROP-clash/materials/a.md", "ours\n")
    return "materials/a.md", "a.md"


def _directory_onto_file(root: Path, write: Write) -> tuple[str, str]:
    write(f"{_dest('clash')}/sub", "a file\n")
    write("docs/proposals/PROP-clash/materials/sub/x.md", "# x\n")
    return "materials/sub", "sub"


def _file_onto_directory(root: Path, write: Write) -> tuple[str, str]:
    write(f"{_dest('clash')}/a.md/inner.txt", "inner\n")
    write("docs/proposals/PROP-clash/materials/a.md", "ours\n")
    return "materials/a.md", "a.md"


def _equal_links(root: Path, write: Write) -> tuple[str, str]:
    write(f"{_dest('clash')}/target.md", "t\n")
    write("docs/proposals/PROP-clash/materials/target-copy.md", "t\n")
    (root / _dest("clash") / "a.md").symlink_to("target.md")
    (root / "docs/proposals/PROP-clash/materials/a.md").symlink_to("target.md")
    return "materials/a.md", "a.md"


def _source_link(root: Path, write: Write) -> tuple[str, str]:
    write(f"{_dest('clash')}/a.md", "t\n")
    write("docs/proposals/PROP-clash/materials/t.md", "t\n")
    (root / "docs/proposals/PROP-clash/materials/a.md").symlink_to("t.md")
    return "materials/a.md", "a.md"


def _link_above_a_planned_path(root: Path, write: Write) -> tuple[str, str]:
    write("docs/elsewhere/keep.md", "keep\n")
    (root / _dest("clash")).mkdir(parents=True)
    (root / _dest("clash") / "sub").symlink_to(root / "docs/elsewhere", target_is_directory=True)
    write("docs/proposals/PROP-clash/materials/sub/x.md", "# x\n")
    return "materials/sub", "sub"


def _destination_is_a_link(root: Path, write: Write) -> tuple[str, str]:
    write("docs/elsewhere/keep.md", "keep\n")
    (root / f"docs/materials/{MONTH}").mkdir(parents=True)
    (root / _dest("clash")).symlink_to(root / "docs/elsewhere", target_is_directory=True)
    write("docs/proposals/PROP-clash/materials/x.md", "# x\n")
    return "materials", ""


def _destination_is_a_file(root: Path, write: Write) -> tuple[str, str]:
    write(_dest("clash"), "a file\n")
    write("docs/proposals/PROP-clash/materials/x.md", "# x\n")
    return "materials", ""


def _extra_with_different_content(root: Path, write: Write) -> tuple[str, str]:
    write(f"{_dest('clash')}/notes.md", "theirs\n")
    write("docs/proposals/PROP-clash/notes.md", "ours\n")
    return "notes.md", "notes.md"


def _extra_below_a_file(root: Path, write: Write) -> tuple[str, str]:
    write(f"{_dest('clash')}/decisions", "a file\n")
    write("docs/proposals/PROP-clash/decisions/sketch.txt", "sketch\n")
    return "decisions/sketch.txt", "decisions"


def _extra_below_a_link(root: Path, write: Write) -> tuple[str, str]:
    write("docs/elsewhere/keep.md", "keep\n")
    (root / _dest("clash")).mkdir(parents=True)
    (root / _dest("clash") / "decisions").symlink_to(root / "docs/elsewhere", target_is_directory=True)
    write("docs/proposals/PROP-clash/decisions/sketch.txt", "sketch\n")
    return "decisions/sketch.txt", "decisions"


def _non_regular(root: Path, write: Write) -> tuple[str, str]:
    (root / _dest("clash")).mkdir(parents=True)
    os.mkfifo(root / _dest("clash") / "a.md")
    write("docs/proposals/PROP-clash/materials/a.md", "ours\n")
    return "materials/a.md", "a.md"


@pytest.mark.parametrize(
    ("arrange", "kind"),
    [
        (_different_content, "different-content"),
        (_directory_onto_file, "file-directory"),
        (_file_onto_directory, "file-directory"),
        (_equal_links, "symbolic-link"),
        (_source_link, "symbolic-link"),
        (_link_above_a_planned_path, "symbolic-link"),
        (_destination_is_a_link, "symbolic-link"),
        (_destination_is_a_file, "file-directory"),
        (_extra_with_different_content, "different-content"),
        (_extra_below_a_file, "file-directory"),
        (_extra_below_a_link, "symbolic-link"),
        pytest.param(
            _non_regular,
            "non-regular",
            marks=pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="needs named pipes"),
        ),
    ],
)
def test_refuses_a_conflict_before_writing_anything(
    workspace: Path, write: Write, arrange: Callable[[Path, Write], tuple[str, str]], kind: str
) -> None:
    bundle = _new(workspace, "clash")
    source, destination = arrange(workspace, write)
    dest = workspace / _dest("clash")
    trees = [bundle, workspace / f"docs/materials/{MONTH}", workspace / "docs/elsewhere"]
    before = [_snapshot(tree) for tree in trees]

    with pytest.raises(ProposalTargetExistsError) as raised:
        handoff_proposal(workspace, "clash", today=TODAY)

    error = raised.value
    source_rel = f"docs/proposals/PROP-clash/{source}"
    destination_rel = (dest / destination).relative_to(workspace).as_posix() if destination else _dest("clash")
    assert error.code == "SPEC_PROPOSAL_TARGET_EXISTS"
    # A merge conflict is a data collision the user resolves: INTERACTION, not the BLOCKED guardrail.
    advisory = error.to_dict()["advisory"]
    assert (advisory["mode"], advisory["guardrail"], advisory["actor"]) == ("INTERACTION", False, "USER")
    assert advisory["action"].startswith("INTERACTION — Stop and ask the user.")
    assert error.target_files == (destination_rel,)
    assert f"{source_rel} -> {destination_rel}: {kind}" in error.details
    assert error.fix is not None and "remove" not in error.fix
    if destination:
        assert error.fix.startswith(f"Reconcile {source_rel} with the existing {destination_rel} ({kind}):")
        assert f"keeping {_dest('clash')} and its other files" in error.fix
    else:  # the dated path itself is no directory: the fix renames it aside, keeping its content
        assert error.fix.startswith(f"Rename {destination_rel} aside ({kind}: it is not a real directory)")
    assert [_snapshot(tree) for tree in trees] == before
    assert not (workspace / "specs").exists() and not (workspace / "docs/decisions").exists()


def test_an_unreadable_file_is_refused_before_writing(
    workspace: Path, write: Write, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _new(workspace, "unreadable")
    write(f"{_dest('unreadable')}/a.md", "same\n")
    write("docs/proposals/PROP-unreadable/materials/a.md", "same\n")

    def cmp(*_: object, **__: object) -> bool:
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(handoff_module.filecmp, "cmp", cmp)
    with pytest.raises(ProposalInvalidError) as raised:
        handoff_proposal(workspace, "unreadable", today=TODAY)
    assert raised.value.target_files == (
        "docs/proposals/PROP-unreadable/materials/a.md",
        f"{_dest('unreadable')}/a.md",
    )
    assert raised.value.fix == "Make both files in [TARGET] readable, then rerun the handoff"
    assert (bundle / "materials/a.md").is_file() and not (workspace / "specs").exists()


def test_reports_every_conflict_and_names_the_first_in_the_fix(workspace: Path, write: Write) -> None:
    _new(workspace, "many")
    write(f"{_dest('many')}/b.md", "theirs\n")
    write(f"{_dest('many')}/a.md", "theirs\n")
    write("docs/proposals/PROP-many/materials/a.md", "ours\n")
    write("docs/proposals/PROP-many/materials/b.md", "ours\n")
    with pytest.raises(ProposalTargetExistsError) as raised:
        handoff_proposal(workspace, "many", today=TODAY)
    error = raised.value
    assert error.target_files == (f"{_dest('many')}/a.md", f"{_dest('many')}/b.md")
    assert error.details == (
        f"docs/proposals/PROP-many/materials/a.md -> {_dest('many')}/a.md: different-content",
        f"docs/proposals/PROP-many/materials/b.md -> {_dest('many')}/b.md: different-content",
    )
    assert error.fix is not None
    assert f"Reconcile docs/proposals/PROP-many/materials/a.md with the existing {_dest('many')}/a.md" in error.fix
    assert "reconcile each other conflict in [DETAIL] the same way" in error.fix


def test_a_reconciled_conflict_hands_off_on_the_rerun(workspace: Path, write: Write) -> None:
    bundle = _new(workspace, "again")
    write(f"{_dest('again')}/a.md", "theirs\n")
    write("docs/proposals/PROP-again/materials/a.md", "ours\n")
    with pytest.raises(ProposalTargetExistsError):
        handoff_proposal(workspace, "again", today=TODAY)
    (bundle / "materials/a.md").rename(bundle / "materials/a-proposal.md")
    result = handoff_proposal(workspace, "again", today=TODAY)
    assert result.materials_merged is True
    dest = workspace / _dest("again")
    assert (dest / "a.md").read_text(encoding="utf-8") == "theirs\n"
    assert (dest / "a-proposal.md").read_text(encoding="utf-8") == "ours\n"


def test_ignores_junk_on_both_sides(workspace: Path, write: Write) -> None:
    _new(workspace, "junk")
    for name in (".DS_Store", "sub/Thumbs.db", "desktop.ini"):
        write(f"{_dest('junk')}/{name}", "theirs\n")
        write(f"docs/proposals/PROP-junk/materials/{name}", "ours\n")
    write("docs/proposals/PROP-junk/materials/real.md", "# real\n")
    write("docs/proposals/PROP-junk/materials/only-junk/.DS_Store", "ours\n")
    write("docs/proposals/PROP-junk/.DS_Store", "ours\n")
    dest = workspace / _dest("junk")
    before = _snapshot(dest)

    result = handoff_proposal(workspace, "junk", today=TODAY)

    assert result.materials_merged is True and result.dropped_duplicates == []
    after = _snapshot(dest)
    assert _kept(before, after)
    assert set(after) - set(before) == {"real.md"}
    assert not (workspace / "docs/proposals/PROP-junk").exists()


def _fail_on_call(number: int, real: Callable[..., None]) -> Callable[..., None]:
    """``move_path`` that raises on its ``number``-th call and runs ``real`` otherwise."""
    calls = {"n": 0}

    def move_path(*args: object) -> None:
        calls["n"] += 1
        if calls["n"] == number:
            raise OSError("No space left on device")
        real(*args)

    return move_path


def _merge_bundle(workspace: Path, write: Write, slug: str) -> tuple[Path, Path]:
    bundle = _new(workspace, slug)
    write(f"{_dest(slug)}/bench.json", "{}\n")
    write(f"{_dest(slug)}/nested/run-1.txt", "run 1\n")
    write(f"docs/proposals/PROP-{slug}/materials/design.md", "# Design\n")
    write(f"docs/proposals/PROP-{slug}/materials/nested/run-2.txt", "run 2\n")
    write(f"docs/proposals/PROP-{slug}/materials/fresh/f.txt", "f\n")
    write(f"docs/proposals/PROP-{slug}/notes.md", "# Notes\n")
    return bundle, workspace / _dest(slug)


@pytest.mark.parametrize("failing", [2, 4])
def test_a_failed_merge_never_touches_pre_existing_paths(
    workspace: Path, write: Write, monkeypatch: pytest.MonkeyPatch, failing: int
) -> None:
    # Moves: design.md, fresh/ (whole), nested/run-2.txt, then the carried notes.md (the 4th, after every material).
    bundle, dest = _merge_bundle(workspace, write, f"fails{failing}")
    before, proposal_before = _snapshot(dest), _snapshot(bundle)
    with monkeypatch.context() as patch:
        patch.setattr(handoff_module, "move_path", _fail_on_call(failing, handoff_module.move_path))
        with pytest.raises(ProposalHandoffError):
            handoff_proposal(workspace, f"fails{failing}", today=TODAY)
    assert _snapshot(dest) == before
    assert {rel: entry[:2] for rel, entry in _snapshot(bundle).items()} == {
        rel: entry[:2] for rel, entry in proposal_before.items()
    }
    assert not (workspace / "specs" / MONTH).exists()
    assert handoff_proposal(workspace, f"fails{failing}", today=TODAY).materials_merged is True
    assert _kept(before, _snapshot(dest))


def test_a_failed_merge_across_file_systems_never_touches_pre_existing_paths(
    workspace: Path, write: Write, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle, dest = _merge_bundle(workspace, write, "far")
    before = _snapshot(dest)
    rename = os.rename

    def cross_device(source: object, destination: object) -> None:
        if Path(str(source)).is_relative_to(bundle):
            raise OSError(errno.EXDEV, "Invalid cross-device link")
        rename(source, destination)  # type: ignore[arg-type]

    copy2 = handoff_module.shutil.copy2
    copies = {"n": 0}

    def failing_copy(source: object, destination: object, **kwargs: object) -> object:
        copies["n"] += 1
        if copies["n"] == 2:  # the second leaf file: design.md was copied, nested/run-2.txt fails
            Path(str(destination)).write_text("partial", encoding="utf-8")
            raise OSError("No space left on device")
        return copy2(source, destination, **kwargs)  # type: ignore[arg-type]

    with monkeypatch.context() as patch:
        patch.setattr("devkit_spec.features.proposals.usecases.specs.os.rename", cross_device)
        patch.setattr("devkit_spec.features.proposals.usecases.specs.shutil.copy2", failing_copy)
        with pytest.raises(ProposalHandoffError):
            handoff_proposal(workspace, "far", today=TODAY)
    assert _snapshot(dest) == before
    assert (bundle / "materials/nested/run-2.txt").read_text(encoding="utf-8") == "run 2\n"
    assert (bundle / "materials/design.md").read_text(encoding="utf-8") == "# Design\n"

    monkeypatch.setattr("devkit_spec.features.proposals.usecases.specs.os.rename", cross_device)
    result = handoff_proposal(workspace, "far", today=TODAY)
    assert result.materials_merged is True and _kept(before, _snapshot(dest))
    assert (dest / "nested/run-2.txt").read_text(encoding="utf-8") == "run 2\n"
    assert not bundle.exists()


def test_links_of_pre_existing_files_resolve_from_where_they_are(workspace: Path, write: Write) -> None:
    _new(workspace, "links")
    dest = _dest("links")
    write(f"{dest}/bench.json", "{}\n")
    write(f"docs/materials/{MONTH}/month.md", "# Month\n")
    # From the proposal's materials/ (the same depth), ../month.md would point into the proposal.
    write(
        f"{dest}/index.md",
        "# Index\n[bench](bench.json) [month](../month.md) [proposal](../../../proposals/PROP-links/proposal.md)\n",
    )
    write(f"{dest}/nested/keep.md", "# Keep\n")
    write("docs/proposals/PROP-links/materials/design.md", "# Design\n[up](../proposal.md) [notes](../notes.md)\n")
    write("docs/proposals/PROP-links/materials/nested/n.md", "[up](../../proposal.md)\n")
    write("docs/proposals/PROP-links/materials/deep/d.md", "[up](../../proposal.md)\n")
    write("docs/proposals/PROP-links/notes.md", "# Notes\n")

    result = handoff_proposal(workspace, "links", today=TODAY)

    spec = f"specs/{MONTH}/{STAMP}-links/spec.md"
    index = (workspace / dest / "index.md").read_text(encoding="utf-8")
    assert index == f"# Index\n[bench](bench.json) [month](../month.md) [proposal](../../../../{spec})\n"
    design = (workspace / dest / "design.md").read_text(encoding="utf-8")
    assert design == f"# Design\n[up](../../../../{spec}) [notes](notes.md)\n"
    assert (workspace / dest / "nested/n.md").read_text(encoding="utf-8") == f"[up](../../../../../{spec})\n"
    assert (workspace / dest / "deep/d.md").read_text(encoding="utf-8") == f"[up](../../../../../{spec})\n"
    assert result.unresolved == []
