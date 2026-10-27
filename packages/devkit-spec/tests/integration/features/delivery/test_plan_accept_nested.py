"""Proposal acceptance in a devkit project nested below the Git repository's top level."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from spec_support.scope import git, write

from devkit_spec.features.delivery.usecases import native_plan_accept
from devkit_spec.features.delivery.usecases.native_plan_accept import _Acceptance

UNIT = "docs/proposals/PROP-idea"
DECISION = f"{UNIT}/decisions/plan-accept.md"


def _accept(root: Path, slug: str, *, by: str) -> SimpleNamespace:
    """The two project-relative writes ``accept_proposal`` makes: the accepted anchor and its gate record."""
    anchor = root / UNIT / "proposal.md"
    anchor.write_text(anchor.read_text().replace("status: reviewing", "status: accepted"))
    write(root, DECISION, f"---\nrequest: gate:plan-accept\nby: {by}\n---\n")
    return SimpleNamespace(path=f"{UNIT}/proposal.md", decision=DECISION)


def test_acceptance_in_a_nested_project_commits_the_exact_delta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = (tmp_path / "repo").resolve()
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    project = repo / "apps" / "proj"
    write(project, f"{UNIT}/proposal.md", "---\nid: PROP-idea\nstatus: reviewing\n---\n# [PROP-idea] Idea\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    previous = git(repo, "rev-parse", "HEAD")
    monkeypatch.setattr(native_plan_accept, "accept_proposal", _accept)
    monkeypatch.setattr(_Acceptance, "validate", lambda self, request: None)
    lifecycle = _Acceptance(project, "idea", "accept_only")
    lifecycle.source, lifecycle.meta = project, {"status": "reviewing"}
    request = SimpleNamespace(context=SimpleNamespace(finish=SimpleNamespace(source_sha=previous)))

    head = lifecycle.accept(request)  # type: ignore[arg-type]

    assert git(repo, "rev-parse", "HEAD") == head
    assert set(git(repo, "diff", "--name-only", previous, head).splitlines()) == {
        f"apps/proj/{UNIT}/proposal.md",
        f"apps/proj/{DECISION}",
    }
    assert lifecycle.completed == ["acceptance_record", "acceptance_commit"]
