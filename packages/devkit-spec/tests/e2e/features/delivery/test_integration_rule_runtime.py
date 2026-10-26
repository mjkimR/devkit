"""A source whose synchronized rule needs code the running runtime lacks (SPEC-integration-readiness-branch-code).

The real ``spec`` readiness provider imports the source's receipt-listed rule packages with the base checkout's
installed code. A rule whose implementation module the source adds, as ``RULE-steering-documents`` did, is named
``INTEGRATION_RULE_RUNTIME_MISMATCH`` before the provider runs; a rule broken for another reason keeps the provider's
``INTEGRATION_NOT_READY`` with ``RULES_LOAD_FAILED``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from devkit.advisory import Actor, AdvisoryError
from devkit_agt.features.integration import IntegrationService, ReadinessError, Task
from spec_support.delivery import _make_synced_repo, _start_worktree
from spec_support.scope import git, write

RECEIPT = ".devkit/installation.json"
RULE = ".devkit/managed/spec/rules/needs_new_code/rule.py"
MISSING = "devkit_spec.features.governance.usecases.not_in_this_runtime"
SESSION = Task(
    kind="session",
    id="newrule",
    claims_json=json.dumps(
        {"task_kind": "feature", "effort": "low", "review": "passed", "tests": "PASS pytest", "lint": True}
    ),
)


def _add_rule(worktree: Path, source: str) -> None:
    """Commit a receipt listing a Git-ignored synchronized rule whose worktree copy matches the recorded hash."""
    path = write(worktree, RULE, source)
    receipt = json.loads((worktree / RECEIPT).read_text(encoding="utf-8"))
    receipt["assets"].append({"bundle": "spec", "id": "needs-new-code", "kind": "rule", "paths": [RULE]})
    receipt["files"][RULE] = {"mode": 420, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    write(worktree, RECEIPT, json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    git(worktree, "add", "-A")
    git(worktree, "commit", "-q", "-m", "add a synchronized rule")


def test_rule_needing_source_code_is_named_before_readiness(tmp_path: Path, synced_template: Path) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    worktree = _start_worktree(repo, "dev-newrule", tmp_path / "wt-newrule")
    _add_rule(
        worktree,
        f"from {MISSING} import NeedsNewCodeRule as _Implementation\n\n\nclass Rule(_Implementation):\n    pass\n",
    )

    with pytest.raises(AdvisoryError) as raised:
        IntegrationService(repo).prepare("dev-newrule", SESSION)

    assert raised.value.code == "INTEGRATION_RULE_RUNTIME_MISMATCH"
    assert raised.value.actor is Actor.USER
    assert MISSING in raised.value.message
    assert raised.value.target_files == (RULE,)
    assert "build a runtime from the source's code" in (raised.value.fix or "")


def test_rule_importing_an_uninstalled_package_keeps_rules_load_failed(tmp_path: Path, synced_template: Path) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    worktree = _start_worktree(repo, "dev-newrule", tmp_path / "wt-newrule")
    _add_rule(worktree, "import not_an_installed_distribution_xyz\n")

    with pytest.raises(ReadinessError) as raised:
        IntegrationService(repo).prepare("dev-newrule", SESSION)

    assert raised.value.code == "INTEGRATION_NOT_READY"
    assert any("RULES_LOAD_FAILED" in detail or "RULES_RUN_FAILED" in detail for detail in raised.value.details)
