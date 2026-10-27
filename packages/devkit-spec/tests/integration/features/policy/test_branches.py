"""``_branch_unit``: the committed spec bundle of a slug on a local ``dev-<slug>`` branch, matched exactly."""

from __future__ import annotations

from pathlib import Path

from spec_support.scope import git, write

from devkit_spec.features.policy.repositories.branches import _branch_unit


def _repo(tmp_path: Path, bundles: tuple[str, ...]) -> Path:
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, "README.md", "x\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    git(root, "switch", "-q", "-c", "dev-cleanup")
    for bundle in bundles:
        write(root, f"{bundle}/spec.md", "---\nid: X\n---\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "units")
    git(root, "switch", "-q", "main")
    return root


def test_the_exact_bundle_of_the_slug_is_the_unit(tmp_path: Path) -> None:
    root = _repo(tmp_path, ("specs/2026-10/20261002-cleanup", "specs/2026-10/20261001-hook-cleanup"))
    assert _branch_unit(root, "dev-cleanup", "cleanup") == "specs/2026-10/20261002-cleanup"


def test_a_bundle_whose_slug_only_ends_with_the_slug_is_not_the_unit(tmp_path: Path) -> None:
    root = _repo(tmp_path, ("specs/2026-10/20261001-hook-cleanup",))
    assert _branch_unit(root, "dev-cleanup", "cleanup") is None


def test_a_missing_branch_has_no_unit(tmp_path: Path) -> None:
    root = _repo(tmp_path, ("specs/2026-10/20261002-cleanup",))
    assert _branch_unit(root, "dev-other", "other") is None
