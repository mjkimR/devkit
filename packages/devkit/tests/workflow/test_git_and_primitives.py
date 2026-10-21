"""``git.is_ancestor`` against a real repository, and the disk primitives' edge cases."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from devkit.workflow import (
    Options,
    evaluate_definition,
    is_ancestor,
    parse_definition,
)
from devkit_core.base.errors import GitError
from testsupport.workflow import write_unit


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)
    return done.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    _git(root, "config", "commit.gpgsign", "false")
    (root / "a.txt").write_text("1")
    _git(root, "add", "a.txt")
    _git(root, "commit", "-q", "-m", "one")
    first = _git(root, "rev-parse", "HEAD")
    (root / "a.txt").write_text("2")
    _git(root, "commit", "-q", "-am", "two")
    return root, first, _git(root, "rev-parse", "HEAD")


def test_is_ancestor_answers_from_git(repo: tuple[Path, str, str]) -> None:
    root, first, second = repo
    assert is_ancestor(root, first, second) is True
    assert is_ancestor(root, second, first) is False
    assert is_ancestor(root, first, first) is True
    assert is_ancestor(root, first[:7], second[:12]) is True


def test_is_ancestor_raises_when_git_cannot_answer(repo: tuple[Path, str, str], tmp_path: Path) -> None:
    root, first, _ = repo
    with pytest.raises(GitError):
        is_ancestor(root, "0" * 40, first)  # unknown revision, as in a shallow clone
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()
    with pytest.raises(GitError):
        is_ancestor(not_a_repo, first, first)
    with pytest.raises(GitError, match="not a hexadecimal revision"):
        is_ancestor(root, "--output=x", first)


def test_revision_ancestor_check_end_to_end(repo: tuple[Path, str, str]) -> None:
    root, first, second = repo
    unit = write_unit(root, "work/u")
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text(f"kind: review\nstatus: completed\ndiff_scope: {{head: {first}}}\n")
    (unit / "envelopes/final-report-01.yaml").write_text(
        f"kind: final-report\nstatus: completed\ndiff_scope: {{head: {second}}}\n"
    )
    doc = parse_definition(
        "---\nid: c\nschema_version: 1\nstages:\n  - id: s\n    exit: [revision-ancestor(review final-report)]\n---\n"
    )
    res = evaluate_definition(doc, Options(workspace_root=root, unit_dir=unit, anchor="task.md", ancestor=is_ancestor))
    assert res.complete
    reversed_doc = parse_definition(
        "---\nid: c\nschema_version: 1\nstages:\n  - id: s\n    exit: [revision-ancestor(final-report review)]\n---\n"
    )
    res = evaluate_definition(
        reversed_doc, Options(workspace_root=root, unit_dir=unit, anchor="task.md", ancestor=is_ancestor)
    )
    assert res.unmet[0].evaluated and "ancestor=false" in res.unmet[0].detail


def _stage(*exits: str) -> str:
    return f"---\nid: c\nschema_version: 1\nstages:\n  - id: s\n    exit: [{', '.join(exits)}]\n---\n"


def test_disk_primitive_edge_cases(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/u")
    opts = Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md")
    (unit / "broken.md").write_text("---\nstatus: [x\n---\n")
    (unit / "empty.md").write_text("no tasks here\n")
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text("kind: review\nstatus: completed\n")
    (unit / "envelopes/final-report-01.yaml").write_text(
        "kind: final-report\nstatus: completed\ndiff_scope: {head: HEAD}\n"
    )
    doc = parse_definition(
        _stage(
            "frontmatter(broken.md status done)",
            "frontmatter(missing.md status done)",
            "tasks-checked(empty.md)",
            "tasks-checked(missing.md)",
            "not-skeleton(missing.md)",
            "envelope-check-pass(review tests)",
            "revision-ancestor(review final-report)",
            "revision-ancestor(final-report review)",
            "revision-ancestor(nothing review)",
        )
    )
    details = {u.name: u.detail for u in evaluate_definition(doc, opts).unmet}
    assert "invalid YAML frontmatter" in details["frontmatter(broken.md status done)"]
    assert details["frontmatter(missing.md status done)"] == "missing.md missing"
    assert details["tasks-checked(empty.md)"] == "no tasks"
    assert details["tasks-checked(missing.md)"] == "missing.md missing"
    assert "not-skeleton(missing.md)" not in details  # a missing file is not a skeleton
    assert details["envelope-check-pass(review tests)"] == "envelopes/review-01.yaml status=completed tests=''"
    assert details["revision-ancestor(review final-report)"] == "envelopes/review-01.yaml has no diff_scope.head"
    assert (
        details["revision-ancestor(final-report review)"]
        == "envelopes/final-report-01.yaml head 'HEAD' is not a revision"
    )
    assert details["revision-ancestor(nothing review)"] == "no nothing envelope"
