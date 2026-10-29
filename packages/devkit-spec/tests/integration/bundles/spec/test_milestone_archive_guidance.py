"""Rendered archive guidance with explicit simulated user decisions and real Git file states.

These fixtures execute the described file operations, not an automatic lifecycle evaluator.
Semantic approval remains a review judgment; token checks alone are not transition evidence.
"""

import subprocess
from pathlib import Path

import pytest
from devkit_core.core.frontmatter import parse
from devkit_docs.features.documents import DocumentIndex
from devkit_docs.features.documents.models.milestones import milestone_path_valid
from distsupport.guidance import assert_rule
from spec_support.bundle_text import raw


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def commit(root: Path, message: str) -> str:
    git(root, "add", "docs")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def milestone(root: Path, slug: str, status: str) -> Path:
    path = root / f"docs/roadmap/{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nid: {slug}\ntitle: Example\nstatus: {status}\n---\n# [{slug}] Example\n\n## Completion review\n\nDecomposition: pending\nDirect proposal work: pending\n"
    )
    return path


@pytest.mark.parametrize("environment", ["local", "cloud"])
def test_archive_transition_instructions(environment: str) -> None:
    procedure = raw("skills/spec/references/milestone-completion.md", environment)
    for rule in (
        ("`status: done`", "move the file", "`docs/roadmap/_archive/`", "same commit"),
        ("drop", "move into `_archive/`", "one backlog commit", "does not create or confirm", "completion assertion"),
        ("unchanged archived drop", "writes nothing"),
        ("file movement", "no extra archive-only gate", "destination collision", "without overwriting"),
        ("relocation batch", "exact unchanged batch", "only those files", "comparing bytes before/after"),
        ("keep absent historical assertions absent",),
        ("merge", "either supported location"),
    ):
        assert_rule(procedure, *rule)
    backlog = raw("skills/spec/references/backlog.md", environment)
    assert "docs/roadmap/_archive/MS-<slug>.md" in backlog
    assert_rule(backlog, "reopen", "move back to the root", "reset both assertions to pending", "one approved commit")


def test_simulated_close_reopen_drop_and_history_merge(tmp_path: Path) -> None:
    # Scenario authority: a simulated user has confirmed decomposition and direct work for this candidate.
    git(tmp_path, "init", "-q")
    root = milestone(tmp_path, "MS-example", "active")
    initial = commit(tmp_path, "initial active candidate")
    archived = root.parent / "_archive" / root.name
    archived.parent.mkdir()
    root.write_text(root.read_text().replace("status: active", "status: done").replace(": pending", ": confirmed"))
    root.rename(archived)
    closed = commit(tmp_path, "simulated approved close and move")
    assert not root.exists()
    assert milestone_path_valid(archived.relative_to(tmp_path).as_posix(), "done")
    assert "Decomposition: confirmed" in archived.read_text()
    assert "Direct proposal work: confirmed" in archived.read_text()
    assert set(git(tmp_path, "diff", "--no-renames", "--name-only", initial, closed).splitlines()) == {
        "docs/roadmap/MS-example.md",
        "docs/roadmap/_archive/MS-example.md",
    }
    # Repeating the unchanged closed candidate performs no operation and creates no commit.
    assert not git(tmp_path, "status", "--porcelain")
    assert git(tmp_path, "rev-parse", "HEAD") == closed
    # Simulated decision to reopen scope: reset and relocate together.
    archived.write_text(
        archived.read_text().replace("status: done", "status: active").replace(": confirmed", ": pending")
    )
    archived.rename(root)
    reopened = commit(tmp_path, "simulated approved reopen and move")
    assert milestone_path_valid(root.relative_to(tmp_path).as_posix(), "active")
    assert "confirmed" not in root.read_text() and not archived.exists()
    assert len(git(tmp_path, "diff", "--no-renames", "--name-only", closed, reopened).splitlines()) == 2
    # Simulated drop decision includes explicit remaining-scope disposition; it never confirms completion.
    root.write_text(
        root.read_text().replace("status: active", "status: dropped")
        + "\nRemaining scope: explicitly excluded by the simulated user decision.\n"
    )
    root.rename(archived)
    dropped = commit(tmp_path, "simulated approved drop disposition and move")
    data = parse(archived.read_text()).data
    assert data is not None and data["status"] == "dropped"
    assert "confirmed" not in archived.read_text()
    assert "Remaining scope: explicitly excluded" in archived.read_text()
    assert not git(tmp_path, "status", "--porcelain")
    assert git(tmp_path, "rev-parse", "HEAD") == dropped  # Repeated unchanged drop is no-op.
    # Simulated merge decision preserves the archived ID as a theme alias with pending assertions.
    theme = milestone(tmp_path, "MS-theme", "active")
    theme.write_text(theme.read_text().replace("title: Example", "title: Theme\naliases: [MS-example]"))
    archived.unlink()
    commit(tmp_path, "simulated approved historical merge")
    index = DocumentIndex.load(tmp_path)
    assert index.resolve("MS-example").id == "MS-theme"
    assert "confirmed" not in theme.read_text()
