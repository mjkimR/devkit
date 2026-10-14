from __future__ import annotations

import unicodedata
from pathlib import Path

import pytest
from devkit.advisory import ActionMode
from devkit.core import FrontmatterError, UnsafePathError
from devkit.rules import PinnedWriteError, WorkspaceCache
from testsupport.rules import init_repo, write


def test_cache_read_text_and_invalidation(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "sample.md"
    doc_path.write_text("initial content", encoding="utf-8")

    # First read
    assert workspace_cache.read_text("sample.md") == "initial content"

    # Modify underlying file directly
    doc_path.write_text("updated content", encoding="utf-8")
    # Cached value should still be returned
    assert workspace_cache.read_text("sample.md") == "initial content"

    # Invalidate cache
    workspace_cache.invalidate("sample.md")
    assert workspace_cache.read_text("sample.md") == "updated content"


def test_cache_frontmatter_parsing(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "doc.md"
    content = "---\nid: US-test\ntitle: Test Story\nstatus: active\n---\n\n# Body here"
    doc_path.write_text(content, encoding="utf-8")

    fm = workspace_cache.get_frontmatter("doc.md")
    assert fm is not None
    assert fm["id"] == "US-test"
    assert fm["title"] == "Test Story"


def test_cache_markdown_links(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "doc.md"
    content = "Check [Auth guide](./guides/auth.md) and [External](https://example.com)."
    doc_path.write_text(content, encoding="utf-8")

    links = workspace_cache.get_links("doc.md")
    assert len(links) == 2
    assert links[0].text == "Auth guide"
    assert links[0].target == "./guides/auth.md"
    assert links[1].text == "External"
    assert links[1].target == "https://example.com"


def test_frontmatter_delimiters_inside_values(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    (temp_workspace / "doc.md").write_text('---\ntitle: "before---after"\n---\n# Body\n')
    assert workspace_cache.get_frontmatter("doc.md") == {"title": "before---after"}


def test_file_listing_cached_and_invalidated(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    (temp_workspace / "b.md").touch()
    ignored = temp_workspace / ".venv"
    ignored.mkdir()
    (ignored / "ignored.md").touch()
    assert workspace_cache.find_files(temp_workspace) == [temp_workspace / "b.md"]
    (temp_workspace / "a.md").touch()
    assert workspace_cache.find_files(temp_workspace) == [temp_workspace / "b.md"]
    workspace_cache.invalidate("a.md")
    assert workspace_cache.find_files(temp_workspace) == [temp_workspace / "a.md", temp_workspace / "b.md"]


def test_frontmatter_uses_the_core_grammar(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    write(temp_workspace, "indented.md", " ---\ntitle: x\n---\n")
    write(temp_workspace, "unclosed.md", "---\njust a thematic break\n")
    write(temp_workspace, "scalar.md", "---\nIntro text\n---\nbody\n")
    write(temp_workspace, "dup.md", "---\na:\n  b: 1\n  b: 2\n---\n")
    assert workspace_cache.get_frontmatter("indented.md") is None
    assert workspace_cache.get_frontmatter("missing.md") is None
    for name in ("unclosed.md", "scalar.md", "dup.md"):
        with pytest.raises(FrontmatterError):
            workspace_cache.get_frontmatter(name)


def test_scans_skip_devkit_and_git_ignored_files(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    write(root, ".gitignore", "venv/\nbuild/\n")
    write(root, "docs/a.md", "x\n")
    write(root, "untracked.md", "x\n")
    write(root, "venv/lib/site.md", "x\n")
    write(root, "build/out.md", "x\n")
    write(root, ".devkit/managed/b/guide.md", "x\n")
    cache = WorkspaceCache(root)
    assert [p.relative_to(root).as_posix() for p in cache.find_files(root)] == [
        "README.md",
        "docs/a.md",
        "untracked.md",
    ]
    unfiltered = WorkspaceCache(root, git_filter=False)
    assert "venv/lib/site.md" in [p.relative_to(root).as_posix() for p in unfiltered.find_files(root)]


def test_scans_skip_symlinks_resolving_outside(tmp_path: Path) -> None:
    root = tmp_path / "ws"
    write(tmp_path, "outside.md", "x\n")
    write(root, "docs/real.md", "x\n")
    (root / "docs/out.md").symlink_to(tmp_path / "outside.md")
    (root / "docs/in.md").symlink_to("real.md")
    cache = WorkspaceCache(root)
    assert [p.name for p in cache.find_files(root)] == ["in.md", "real.md"]
    (root / "linkdir").symlink_to(tmp_path)
    assert cache.find_files(root / "linkdir") == []
    git_cache = WorkspaceCache(init_repo(tmp_path / "repo"))
    assert git_cache.find_files(tmp_path / "repo" / ".." / "ws") == []


def test_scans_match_git_names_in_any_unicode_normalization(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    nfd = unicodedata.normalize("NFD", "café.md")
    write(root, nfd, "x\n")
    cache = WorkspaceCache(root)
    assert [unicodedata.normalize("NFC", p.name) for p in cache.find_files(root)] == ["README.md", "café.md"]


def test_write_text_is_exact_and_never_under_devkit(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    workspace_cache.write_text("a.md", "one\r\ntwo\n")
    assert (temp_workspace / "a.md").read_bytes() == b"one\r\ntwo\n"
    with pytest.raises(PinnedWriteError, match=r"under \.devkit/") as refused:
        workspace_cache.write_text(".devkit/managed/x.md", "x")
    assert refused.value.code == "RULES_PINNED_WRITE_REFUSED" and refused.value.mode is ActionMode.BLOCKED
    assert not (temp_workspace / ".devkit").exists()


def test_write_text_replaces_atomically_and_keeps_the_mode(
    temp_workspace: Path, workspace_cache: WorkspaceCache, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os
    import stat

    target = temp_workspace / "doc.md"
    target.write_bytes(b"old\n")
    target.chmod(0o640)
    workspace_cache.write_text("doc.md", "new\n")
    assert target.read_bytes() == b"new\n" and stat.S_IMODE(target.stat().st_mode) == 0o640

    def fail(src: object, dst: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError):
        workspace_cache.write_text("doc.md", "partial\n")
    assert target.read_bytes() == b"new\n"
    assert sorted(p.name for p in temp_workspace.iterdir() if p.name.startswith(".doc.md")) == []


def test_write_text_refuses_a_path_that_resolves_outside_the_workspace(tmp_path: Path) -> None:
    root = tmp_path / "ws"
    outside = tmp_path / "outside.md"
    outside.write_text("keep\n", encoding="utf-8")
    write(root, "x.md", "x\n")
    (root / "link.md").symlink_to(outside)
    (root / "out").symlink_to(tmp_path)
    cache = WorkspaceCache(root)
    for path in ("link.md", "out/new.md", "../escape.md", outside):
        with pytest.raises(UnsafePathError) as refused:
            cache.write_text(path, "changed\n")
        assert refused.value.code == "PATH_UNSAFE"
    assert outside.read_text(encoding="utf-8") == "keep\n"
    assert not (tmp_path / "new.md").exists() and not (tmp_path / "escape.md").exists()


def test_read_text_strict(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    write(temp_workspace, "bad.md", b"caf\xe9\n")
    assert workspace_cache.read_text("bad.md") == "caf�\n"
    assert workspace_cache.read_text_strict("bad.md") is None


def test_transient_devkit_files_and_explicit_ignored_targets_are_scanned(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    write(root, ".gitignore", ".devkit/transient/\n")
    write(root, ".devkit/transient/work/unit/tasks.md", "x\n")
    write(root, ".devkit/overrides/b/rule.md", "x\n")
    cache = WorkspaceCache(root)
    assert ".devkit/transient/work/unit/tasks.md" not in [
        p.relative_to(root).as_posix() for p in cache.find_files(root)
    ]
    cache.add_explicit([".devkit/transient/work/unit/tasks.md", ".devkit/overrides/b/rule.md"])
    assert [p.relative_to(root).as_posix() for p in cache.find_files(root)] == [
        ".devkit/transient/work/unit/tasks.md",
        "README.md",
    ]
    with pytest.raises(PinnedWriteError):
        cache.write_text(".devkit/overrides/b/rule.md", "y")
