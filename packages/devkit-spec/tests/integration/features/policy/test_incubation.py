"""Incubation policy omits implicit lifecycle work, not document checks or retained Units."""

import pytest
from devkit_agt.features.rules import RuleContext, evaluate_rules

from devkit_spec.features.governance.usecases.spec_lifecycle import SpecLifecycleRule
from devkit_spec.features.governance.usecases.task_coverage import TaskCoverageRule
from devkit_spec.features.policy import LifecycleInactiveError
from devkit_spec.features.proposals.usecases.scaffold import create_proposal
from devkit_spec.features.proposals.usecases.specs import create_spec


def config(root):
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text('[development]\napproach="incubation"\n')


@pytest.mark.parametrize("operation", [create_spec, create_proposal])
def test_mutation_refuses_before_writes(tmp_path, operation):
    config(tmp_path)
    before = list(tmp_path.rglob("*"))
    with pytest.raises(LifecycleInactiveError):
        operation(tmp_path, "demo")
    assert list(tmp_path.rglob("*")) == before


def test_unbound_document_is_omitted_but_retained_unit_checked(tmp_path):
    config(tmp_path)
    bundle = tmp_path / "specs/2026-10/20261028-demo"
    bundle.mkdir(parents=True)
    spec = bundle / "spec.md"
    spec.write_text("---\nstatus: completed\n---\n# Product\n")
    result = evaluate_rules(RuleContext(tmp_path), [SpecLifecycleRule(), TaskCoverageRule()])
    assert result.ok and len(result.omissions) == 2
    assert all(o.code == "SDD_LIFECYCLE_INACTIVE" for o in result.omissions)
    spec.write_text("---\nworkflow: sdd-spec-feature\nstatus: completed\n---\n# Retained\n")
    result = evaluate_rules(RuleContext(tmp_path), [SpecLifecycleRule()])
    assert not result.ok and not result.omissions


def test_composed_and_direct_accept_handoff_refuse(tmp_path):
    from devkit_spec.features.delivery.usecases.native_handoff import HandoffUseCase
    from devkit_spec.features.delivery.usecases.native_plan_accept import PlanAcceptUseCase
    from devkit_spec.features.proposals.usecases.accept import accept_proposal
    from devkit_spec.features.proposals.usecases.handoff import handoff_proposal

    config(tmp_path)
    for operation in (
        lambda: PlanAcceptUseCase(tmp_path).execute("demo", effort="medium"),
        lambda: HandoffUseCase(tmp_path).execute("demo", "medium"),
        lambda: accept_proposal(tmp_path, "demo", by="user"),
        lambda: handoff_proposal(tmp_path, "demo"),
    ):
        with pytest.raises(LifecycleInactiveError):
            operation()
    assert not (tmp_path / "specs").exists()
    assert not (tmp_path / "docs").exists()


def test_installed_cli_reports_omissions_and_inactive_mutation(tmp_path, synced_template):
    import json

    from click.testing import CliRunner
    from devkit_dist.cli import cli
    from spec_support.delivery import _make_synced_repo

    repo = _make_synced_repo(tmp_path, synced_template, extra_config='[development]\napproach="incubation"')
    runner = CliRunner()
    result = runner.invoke(cli, ["rules", "check", "-w", str(repo), "--format", "json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert len(data["omissions"]) == 5 and not data["errors"]
    assert all(o["code"] == "SDD_LIFECYCLE_INACTIVE" for o in data["omissions"])
    result = runner.invoke(cli, ["spec", "new", "demo", "-w", str(repo), "--format", "json"])
    assert result.exit_code == 2, result.output
    assert json.loads(result.stdout)["error"]["code"] == "SPEC_LIFECYCLE_INACTIVE"
    policy = runner.invoke(cli, ["spec", "policy", "-w", str(repo), "--format", "json"])
    assert json.loads(policy.stdout)["development"] == {"approach": "incubation", "source": ".devkit/config.toml"}
