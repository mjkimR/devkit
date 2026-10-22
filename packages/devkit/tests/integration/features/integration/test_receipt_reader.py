"""A source that changes the receipt reader is diagnosed before the readiness provider (SPEC-retained-runtime-receipt).

The fixture provider reads the source's committed receipt with the running reader, as the ``devkit-spec`` provider
reads the source tree, so without the diagnosis prepare reports the receipt's own ``RECEIPT_INVALID``.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest
from devkit.advisory import ActionMode, AdvisoryError
from devkit_agt.features.integration import IntegrationService, Task
from devkit_dist.features.project.repositories.receipt import RECEIPT_PATH, parse_receipt
from testsupport.rules import git, write

from .test_pull_request import FakeGitHub

TASK = Task("session", "fixture-task")
READER = "packages/devkit-dist/src/devkit_dist/features/project/repositories/receipt.py"
RECEIPT = {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": [], "files": {}}


def _receipt(**extra: object) -> str:
    return json.dumps({**RECEIPT, **extra}, indent=2) + "\n"


@pytest.fixture
def reading_provider(ready_provider, monkeypatch):
    """The fixture provider, reading the source's committed receipt first."""
    original = ready_provider.check

    def check(context):
        parse_receipt(git(context.finish.base, "show", f"{context.finish.source_sha}:{RECEIPT_PATH}"))
        return replace(original(context), landed_check="devkit rules check")

    monkeypatch.setattr(ready_provider, "check", check)
    return ready_provider


def _source(repo, *, reader_changed: bool):
    """The target accepts its receipt; the source adds an unknown key and changes the reader only when asked."""
    base, worktree = repo
    write(base, RECEIPT_PATH, _receipt())
    write(base, READER, "# the target's reader\n")
    git(base, "add", ".")
    git(base, "commit", "-qm", "record the receipt")
    git(worktree, "merge", "-q", "main")
    write(worktree, RECEIPT_PATH, _receipt(future_key="value"))
    if reader_changed:
        write(worktree, READER, "# the source's reader accepts future_key\n")
    git(worktree, "add", ".")
    git(worktree, "commit", "-qm", "add a receipt key")
    return base, worktree


def test_reader_changing_source_is_refused_before_the_provider(repo, reading_provider):
    base, _ = _source(repo, reader_changed=True)
    service = IntegrationService(base)
    with pytest.raises(AdvisoryError) as raised:
        service.prepare("dev-demo", TASK)
    assert raised.value.code == "INTEGRATION_RECEIPT_READER_CHANGED"
    assert raised.value.mode is ActionMode.INTERACTION
    assert "restarting" in (raised.value.fix or "")
    assert "devkit worktree finish" in (raised.value.fix or "")
    assert raised.value.target_files == (RECEIPT_PATH,)
    assert reading_provider.calls == []
    assert service._records == {}


def test_reader_changing_source_is_refused_on_the_pull_request_route(repo, reading_provider, tmp_path):
    base, _ = _source(repo, reader_changed=True)
    remote = tmp_path / "remote.git"
    git(base, "init", "--bare", str(remote))
    git(base, "remote", "add", "origin", str(remote))
    git(base, "push", "-u", "origin", "main")
    service = IntegrationService(base)
    service.github = FakeGitHub(base, remote)
    with pytest.raises(AdvisoryError) as raised:
        service.prepare("dev-demo", TASK, "pull-request")
    assert raised.value.code == "INTEGRATION_RECEIPT_READER_CHANGED"
    assert reading_provider.calls == []


def test_corrupted_receipt_without_reader_change_keeps_receipt_invalid(repo, reading_provider):
    base, _ = _source(repo, reader_changed=False)
    with pytest.raises(AdvisoryError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert raised.value.code == "RECEIPT_INVALID"


def test_unreadable_target_receipt_is_not_diagnosed(repo, reading_provider):
    base, worktree = _source(repo, reader_changed=True)
    write(base, RECEIPT_PATH, _receipt(other_key="value"))
    git(base, "commit", "-qam", "corrupt the target receipt")
    git(worktree, "merge", "-q", "-X", "theirs", "main")
    write(worktree, RECEIPT_PATH, _receipt(future_key="value"))
    git(worktree, "commit", "-qam", "keep the source receipt")
    with pytest.raises(AdvisoryError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert raised.value.code == "RECEIPT_INVALID"
