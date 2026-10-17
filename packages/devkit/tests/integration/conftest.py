from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from devkit.integration import Evidence, Readiness, providers
from devkit.worktree import locate, start
from testsupport.rules import git, init_repo, write


@dataclass
class Entry:
    name: str
    value: str
    target: Any
    dist: Any = None

    def load(self):
        return self.target


class Provider:
    allowed = True

    def check(self, context):
        plan = context.finish
        ready = git(Path(plan.base), "show", f"{plan.source_sha}:ready.txt") == "ready"
        return Readiness(
            plan.source_sha,
            plan.target_sha,
            (Evidence("FIXTURE_CHECK_PASSED", plan.source_sha),),
            () if ready and self.allowed else ("finish the fixture checks",),
        )


@pytest.fixture
def ready_provider(monkeypatch: pytest.MonkeyPatch):
    provider = Provider()
    original = providers.metadata.entry_points

    def entries(**kw):
        if kw.get("group") == "devkit.integration.readiness":
            return [Entry("fixture", "fixture:provider", provider)] if kw.get("name") == "fixture" else []
        if kw.get("group") == "devkit.post_finish":
            return []
        return original(**kw)

    monkeypatch.setattr(providers.metadata, "entry_points", entries)
    return provider


@pytest.fixture
def repo(tmp_path: Path, ready_provider) -> tuple[Path, Path]:
    base = init_repo(tmp_path / "repo")
    write(base, ".devkit/config.toml", '[integration]\nprovider = "fixture"\n')
    write(base, ".gitignore", ".devkit/transient/\n")
    git(base, "add", ".")
    git(base, "commit", "-qm", "configure integration")
    created = start(locate(base), "dev-demo")
    write(created.path, "ready.txt", "ready\n")
    git(created.path, "add", ".")
    git(created.path, "commit", "-qm", "implement fixture")
    return base, created.path
