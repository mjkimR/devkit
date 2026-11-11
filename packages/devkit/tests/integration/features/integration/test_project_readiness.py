"""Integration delegates source workflow validation to the Host's branch runtime."""

from pathlib import Path

import pytest
from devkit_agt.features.integration import IntegrationService
from devkit_agt.features.worktree import locate, start
from testsupport.rules import git, init_repo, write


@pytest.mark.parametrize("approach", ["adaptive-dev", "sdd"])
@pytest.mark.parametrize("table", ["", "[integration]\n"], ids=["absent", "empty"])
def test_merge_needs_no_readiness_provider_or_claims(tmp_path: Path, approach, table):
    base = init_repo(tmp_path / "base")
    write(base, ".devkit/config.toml", f'[development]\napproach="{approach}"\n' + table)
    git(base, "add", ".")
    git(base, "commit", "-qm", "configure")
    worktree = start(locate(base), "dev-demo").path
    write(worktree, "app.py", "value = 1\n")
    git(worktree, "add", ".")
    git(worktree, "commit", "-qm", "implement")
    service = IntegrationService(base)
    request = service.prepare("dev-demo").request
    assert "task" not in request.approval_scope() and "readiness" not in request.approval_scope()
    result = service.execute_cli("dev-demo", expected_digest=request.digest)
    assert result.status == "completed" and result.verification == "pending"
