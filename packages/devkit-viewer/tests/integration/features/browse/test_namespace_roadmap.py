from __future__ import annotations

from pathlib import Path

import pytest

from devkit_viewer.features.browse.models.errors import path_not_found
from devkit_viewer.features.browse.repositories.worktree import WorkingTreeReader

PATHS = [
    "docs/roadmap/MS-global.md",
    "docs/roadmap/_archive/MS-base.md",
    "docs/packages/api/roadmap/_archive/MS-api.md",
    "docs/packages/web/roadmap/MS-web.md",
]


def write(root: Path, path: str, value: bytes = b"---\nid: MS-example\n---\n\xff") -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(value)


@pytest.mark.parametrize("config", [None, "not valid [toml", "", '[[tool.docs.namespaces]]\nname="api"\npath="api"'])
def test_namespace_headers_follow_structure_and_leave_bodies_unread(tmp_path: Path, config: str | None) -> None:
    for path in PATHS:
        write(tmp_path, path)
    for path in [
        "docs/packages/api/roadmap/_archive/deep/MS-ignore.md",
        "docs/packages/api/roadmap/deep/MS-ignore.md",
        "docs/packages/api/roadmap/README.md",
        "docs/packages/api/ux/MS-ignore.md",
    ]:
        write(tmp_path, path)
    if config is not None:
        write(tmp_path, ".devkit/config.toml", config.encode())
    result = WorkingTreeReader(tmp_path).dashboard_headers("milestones")
    assert sorted(item["path"] for item in result["items"]) == sorted(PATHS)  # type: ignore[index]
    assert result["errors"] == []
    assert "\\xff" not in str(result)


def test_namespace_discovery_excludes_local_symlink_roots_and_files(tmp_path: Path) -> None:
    for path in PATHS:
        write(tmp_path, path)
    (tmp_path / "docs/packages/alias").symlink_to(tmp_path / "docs/packages/api", target_is_directory=True)
    (tmp_path / "docs/packages/api/roadmap/MS-alias.md").symlink_to(tmp_path / PATHS[0])
    (tmp_path / "docs/packages/link").mkdir()
    (tmp_path / "docs/packages/link/roadmap").symlink_to(tmp_path / "docs/roadmap", target_is_directory=True)
    result = WorkingTreeReader(tmp_path).dashboard_headers("milestones")
    assert sorted(item["path"] for item in result["items"]) == sorted(PATHS)  # type: ignore[index]
    assert result["errors"] == []


def test_namespace_listing_failure_keeps_other_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for path in PATHS:
        write(tmp_path, path)
    original = WorkingTreeReader.tree

    def fail(self: WorkingTreeReader, path: str, *, recursive: bool = False):
        if path == "docs/packages/api/roadmap":
            raise path_not_found(path, "directory")
        return original(self, path, recursive=recursive)

    monkeypatch.setattr(WorkingTreeReader, "tree", fail)
    result = WorkingTreeReader(tmp_path).dashboard_headers("milestones")
    assert sorted(item["path"] for item in result["items"]) == sorted(p for p in PATHS if "/api/" not in p)  # type: ignore[index]
    assert len(result["errors"]) == 1  # type: ignore[arg-type]
    assert "docs/packages/api/roadmap:" in str(result["errors"])


def test_missing_roots_and_bad_namespace_header(tmp_path: Path) -> None:
    reader = WorkingTreeReader(tmp_path)
    assert reader.dashboard_headers("milestones") == {"items": [], "errors": []}
    write(tmp_path, PATHS[0])
    write(tmp_path, PATHS[2], b"---\nid: broken\n")
    result = reader.dashboard_headers("milestones")
    assert len(result["items"]) == 1  # type: ignore[arg-type]
    assert PATHS[2] in str(result["errors"])
