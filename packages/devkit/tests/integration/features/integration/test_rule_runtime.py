"""A synchronized rule that imports code this runtime lacks is named before the provider (SPEC-integration-readiness-branch-code).

The fixture provider loads no rule, so every refusal here comes from ``check_rule_runtime``; a case it leaves alone
reaches the provider and prepares.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import devkit_agt.features.integration.services.providers as providers
import pytest
from devkit.advisory import ActionMode, Actor, AdvisoryError
from devkit_agt.features.integration import IntegrationContext, IntegrationService, RuleRuntimeMismatchError, Task
from devkit_agt.features.worktree import locate, plan_finish
from devkit_dist.features.project.repositories.receipt import RECEIPT_PATH
from testsupport.rules import git, write

from .test_pull_request import FakeGitHub

TASK = Task("session", "fixture-task")
RULE = ".devkit/managed/spec/rules/new_rule/rule.py"
RULE_TEST = ".devkit/managed/spec/rules/new_rule/tests/test_rule.py"
MISSING = "devkit_agt.features.rules.not_in_this_runtime"
RECEIPT = {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": [], "files": {}}


def _receipt(paths: dict[str, str]) -> str:
    asset = {"bundle": "spec", "id": "new-rule", "kind": "rule", "paths": sorted(paths)}
    files = {path: {"mode": 420, "sha256": hashlib.sha256(text.encode()).hexdigest()} for path, text in paths.items()}
    return json.dumps({**RECEIPT, "assets": [asset], "files": files}, indent=2) + "\n"


def _commit_rule(root: Path, source: str, *, tracked: bool = True, extra: dict[str, str] | None = None) -> str:
    """Commit a receipt listing ``RULE``; untracked, the rule file is written to ``root`` but left out of the commit."""
    paths = {RULE: source, **(extra or {})}
    for path, text in paths.items():
        write(root, path, text)
    write(root, RECEIPT_PATH, _receipt(paths))
    if tracked:
        git(root, "add", "-A")
    else:
        write(root, ".gitignore", ".devkit/transient/\n.devkit/managed/\n")
        git(root, "add", RECEIPT_PATH, ".gitignore")
    git(root, "commit", "-qm", "add a synchronized rule")
    return git(root, "rev-parse", "HEAD")


def test_rule_importing_a_missing_module_is_refused_before_the_provider(repo, ready_provider):
    base, worktree = repo
    _commit_rule(worktree, f"from {MISSING} import Rule as _Implementation\n")
    service = IntegrationService(base)
    with pytest.raises(RuleRuntimeMismatchError) as raised:
        service.prepare("dev-demo", TASK)
    assert raised.value.code == "INTEGRATION_RULE_RUNTIME_MISMATCH"
    assert raised.value.actor is Actor.USER
    assert raised.value.mode is not ActionMode.BLOCKED
    assert f"{RULE} imports {MISSING}" in raised.value.message
    assert raised.value.target_files == (RULE,)
    assert "devkit integration integrate" in (raised.value.fix or "")
    assert ready_provider.calls == []
    assert service._records == {}


def test_rule_importing_a_missing_name_is_refused(repo, ready_provider):
    base, worktree = repo
    _commit_rule(worktree, "from devkit_agt.features.rules.services.builtins import BaseRule, NotInThisRuntime\n")
    with pytest.raises(RuleRuntimeMismatchError) as raised:
        IntegrationService(base).prepare("dev-demo", TASK)
    assert "imports devkit_agt.features.rules.services.builtins.NotInThisRuntime" in raised.value.message
    assert "BaseRule" not in raised.value.message


def test_ignored_rule_copy_is_read_only_when_it_matches_the_receipt(repo, ready_provider):
    base, worktree = repo
    source = f"import {MISSING}\n"
    _commit_rule(worktree, source, tracked=False)
    with pytest.raises(RuleRuntimeMismatchError):
        IntegrationService(base).prepare("dev-demo", TASK)
    write(worktree, RULE, f"{source}# edited after sync\n")
    assert IntegrationService(base).prepare("dev-demo", TASK).request.readiness.reasons == ()


@pytest.mark.parametrize(
    "source",
    [
        "from __future__ import annotations\n\nimport json\nfrom . import helpers\n"
        "from devkit_agt.features.rules.services.builtins import BaseRule\n",
        "import not_an_installed_distribution_xyz\n",
        "def broken(:\n",
        f"def later():\n    import {MISSING}\n",
    ],
    ids=["available", "uninstalled-top-level", "syntax-error", "function-level"],
)
def test_rules_the_check_cannot_attribute_reach_the_provider(repo, ready_provider, source):
    base, worktree = repo
    _commit_rule(worktree, source)
    IntegrationService(base).prepare("dev-demo", TASK)
    assert len(ready_provider.calls) == 1


def test_rule_tests_are_not_checked(repo, ready_provider):
    base, worktree = repo
    _commit_rule(worktree, "import json\n", extra={RULE_TEST: f"import {MISSING}\n"})
    IntegrationService(base).prepare("dev-demo", TASK)
    assert len(ready_provider.calls) == 1


def test_result_commit_is_checked_at_a_build(repo, ready_provider):
    base, _ = repo
    context = IntegrationContext(plan_finish(locate(base), "dev-demo"), TASK)
    git(base, "checkout", "-qb", "result")
    result = _commit_rule(base, f"import {MISSING}\n")
    git(base, "checkout", "-q", "main")
    with pytest.raises(RuleRuntimeMismatchError):
        providers.check(ready_provider, replace(context, result_sha=result))
    assert ready_provider.calls == []


def test_pull_request_route_is_refused(repo, ready_provider, tmp_path):
    base, worktree = repo
    _commit_rule(worktree, f"import {MISSING}\n")
    remote = tmp_path / "remote.git"
    git(base, "init", "--bare", str(remote))
    git(base, "remote", "add", "origin", str(remote))
    git(base, "push", "-u", "origin", "main")
    service = IntegrationService(base)
    service.github = FakeGitHub(base, remote)
    with pytest.raises(AdvisoryError) as raised:
        service.prepare("dev-demo", TASK, "pull-request")
    assert raised.value.code == "INTEGRATION_RULE_RUNTIME_MISMATCH"
    assert ready_provider.calls == []


def test_runtime_inside_the_worktree_keeps_its_refusal(repo, ready_provider, monkeypatch):
    from devkit_agt.features.integration import RuntimeLocationError

    base, worktree = repo
    _commit_rule(worktree, f"import {MISSING}\n")
    monkeypatch.setattr(sys, "executable", str(worktree / ".venv/bin/python"))
    with pytest.raises(RuntimeLocationError):
        IntegrationService(base).prepare("dev-demo", TASK)
