"""Real project provider accepts independent incubation work and preserves Unit ownership."""

from pathlib import Path

import pytest
from devkit_agt.features.integration import IntegrationService, Task
from devkit_agt.features.integration.models.errors import (
    ApproachMismatchError,
    LifecycleValidationRequiredError,
    ReadinessError,
)
from devkit_agt.features.worktree import locate, start
from testsupport.rules import git, init_repo, write

CLAIMS = '{"review":"PASS source review","tests":"PASS project tests","lint":"PASS lint"}'


def project(tmp_path: Path, approach="incubation", retained=False):
    base = init_repo(tmp_path / "base")
    write(base, ".devkit/config.toml", f'[development]\napproach="{approach}"\n[integration]\nprovider="project"\n')
    if retained:
        write(base, "docs/unit/anchor.md", "---\nworkflow: sdd-spec-feature\n---\n# Retained\n")
        write(base, "docs/unit/tasks.md", "Retained companion\n")
    git(base, "add", ".")
    git(base, "commit", "-qm", "configure")
    worktree = start(locate(base), "dev-demo").path
    write(worktree, "app.py", "value = 1\n")
    git(worktree, "add", ".")
    git(worktree, "commit", "-qm", "implement")
    return base, worktree


def test_real_project_readiness_without_sdd_records(tmp_path):
    base, _ = project(tmp_path, retained=True)
    result = IntegrationService(base).prepare("dev-demo", Task("session", "demo", claims_json=CLAIMS))
    evidence = {e.code: e.value for e in result.request.readiness.evidence}
    assert evidence["LIFECYCLE"] == "omitted:incubation"
    assert evidence["CI_RULES"] == "pass"
    assert "VERIFICATION_CLAIMS" in evidence
    landed = IntegrationService(base).execute_cli(
        "dev-demo", Task("session", "demo", claims_json=CLAIMS), expected_digest=result.request.digest
    )
    assert landed.status == "completed"


def test_missing_claims_refuse(tmp_path):
    base, _ = project(tmp_path)
    with pytest.raises(ReadinessError):
        IntegrationService(base).prepare("dev-demo", Task("session", "demo"))


def test_sdd_target_cannot_use_project_provider(tmp_path):
    base, worktree = project(tmp_path, approach="sdd")
    write(worktree, ".devkit/config.toml", '[development]\napproach="incubation"\n[integration]\nprovider="project"\n')
    git(worktree, "add", ".")
    git(worktree, "commit", "-qm", "propose approach")
    with pytest.raises(ApproachMismatchError):
        IntegrationService(base).prepare("dev-demo", Task("session", "demo", claims_json=CLAIMS))


@pytest.mark.parametrize("change", ["companion", "remove_binding", "delete_anchor"])
def test_retained_unit_requires_lifecycle_validator_even_session(tmp_path, change):
    base, worktree = project(tmp_path, retained=True)
    if change == "companion":
        write(worktree, "docs/unit/tasks.md", "Changed companion\n")
    elif change == "remove_binding":
        write(worktree, "docs/unit/anchor.md", "# Unbound now\n")
    else:
        (worktree / "docs/unit/anchor.md").unlink()
    git(worktree, "add", ".")
    git(worktree, "commit", "-qm", "change retained artifact")
    with pytest.raises(LifecycleValidationRequiredError):
        IntegrationService(base).prepare("dev-demo", Task("session", "demo", claims_json=CLAIMS))
