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
from devkit_agt.features.integration import IntegrationService
from spec_support.delivery import _make_synced_repo, _start_worktree
from spec_support.scope import git, write

RECEIPT = ".devkit/installation.json"
RULE = ".devkit/managed/spec/rules/needs_new_code/rule.py"
MISSING = "devkit_spec.features.governance.usecases.not_in_this_runtime"


def _add_rule(worktree: Path, source: str) -> None:
    """Commit a receipt listing a Git-ignored synchronized rule whose worktree copy matches the recorded hash."""
    path = write(worktree, RULE, source)
    receipt = json.loads((worktree / RECEIPT).read_text(encoding="utf-8"))
    receipt["assets"].append({"bundle": "spec", "id": "needs-new-code", "kind": "rule", "paths": [RULE]})
    receipt["files"][RULE] = {"mode": 420, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    write(worktree, RECEIPT, json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    git(worktree, "add", "-A")
    git(worktree, "commit", "-q", "-m", "add a synchronized rule")


@pytest.mark.parametrize(
    "source",
    [
        f"from {MISSING} import NeedsNewCodeRule\n",
        "import not_an_installed_distribution_xyz\n",
    ],
)
def test_upgrade_merges_without_importing_source_rules(tmp_path: Path, synced_template: Path, source: str) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    worktree = _start_worktree(repo, "dev-newrule", tmp_path / "wt-newrule")
    _add_rule(worktree, source)
    service = IntegrationService(repo)
    request = service.prepare("dev-newrule").request
    result = service.execute_cli("dev-newrule", expected_digest=request.digest)
    assert result.status == "completed" and result.verification == "pending"
    assert not worktree.exists()


def test_future_receipt_schema_does_not_require_old_reader(tmp_path: Path, synced_template: Path) -> None:
    repo = _make_synced_repo(tmp_path, synced_template)
    worktree = _start_worktree(repo, "dev-future", tmp_path / "wt-future")
    write(worktree, RECEIPT, '{"schema": "future", "unsupported": true}\n')
    git(worktree, "add", "-A")
    git(worktree, "commit", "-qm", "upgrade receipt")
    service = IntegrationService(repo)
    result = service.execute_cli("dev-future", expected_digest=service.prepare("dev-future").request.digest)
    assert result.status == "completed" and result.verification == "pending"
    assert json.loads((repo / RECEIPT).read_text())["schema"] == "future"
