"""Execute known dynamic FIX builders; the AST scan cannot evaluate these expressions."""

from pathlib import Path
from types import SimpleNamespace

import click
import pytest
from devkit.advisory import Actor, AdvisoryError, Retry
from devkit_agt.features.gate.models.contracts import GateContext, Stage
from devkit_agt.features.workflow.models.decision_records import Decision
from devkit_agt.features.workflow.models.definition import Candidate, WorkflowDocument
from devkit_agt.features.workflow.usecases.handoff import evaluate_handoff
from devkit_dist.cli import cli
from testsupport.advisory_contract import assert_advisory_contract


@pytest.fixture
def commands() -> set[str]:
    return set(cli.list_commands(click.Context(cli)))


def test_commit_message_fix_uses_the_actual_quoted_git_path(tmp_path: Path, commands: set[str]) -> None:
    git_dir = tmp_path / "git with spaces"
    context = GateContext(tmp_path, git_dir, git_dir, Stage.COMMIT_MSG)
    with pytest.raises(AdvisoryError) as caught:
        _ = context.message_file
    assert str(git_dir / "COMMIT_EDITMSG") in (caught.value.fix or "")
    assert_advisory_contract(caught.value, commands)


@pytest.mark.parametrize("unit", ["", "specs/2026-10/20261028-example"])
@pytest.mark.parametrize("eligible", [("next-one",), ("next-one", "next-two")])
def test_handoff_conditional_fixes_and_candidate_details(
    unit: str, eligible: tuple[str, ...], commands: set[str]
) -> None:
    document = WorkflowDocument("example", next=tuple(Candidate(name) for name in eligible))
    recorded = Decision(
        "decisions/01-handoff.yaml", 1, "handoff", "choose", "accept", "example", "2026-10-28", value="old"
    )
    _, ignored = evaluate_handoff(
        document, lambda _: pytest.fail("no candidate checks expected"), recorded, "ask", unit=unit
    )
    assert ignored is not None
    assert_advisory_contract(ignored, commands)
    if unit:
        assert all(name in " ".join(ignored.details) for name in eligible)


def test_proposal_acceptance_fix_uses_the_actual_slug(commands: set[str]) -> None:
    errors = pytest.importorskip("devkit_spec.base.errors")
    error = errors.ProposalAcceptanceUnrecordedError(
        "missing acceptance", fix=errors.acceptance_unrecorded_fix("example")
    )
    assert "proposal accept example" in error.fix
    assert_advisory_contract(error, commands)


@pytest.mark.parametrize("workflows", [(), ("one",), ("one", "two")])
def test_unbound_guidance_helpers_for_zero_one_or_several_workflows(
    workflows: tuple[str, ...], monkeypatch: pytest.MonkeyPatch, tmp_path: Path, commands: set[str]
) -> None:
    binding = pytest.importorskip("devkit_spec.features.proposals.usecases.binding")
    errors = pytest.importorskip("devkit_spec.base.errors")

    class Workspace:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def definitions(self) -> list[SimpleNamespace]:
            return [SimpleNamespace(id=name) for name in workflows]

    monkeypatch.setattr(binding, "Workspace", Workspace)
    fix, details = binding.unbound_guidance(tmp_path, "specs/2026-10/20261028-example", "sdd-spec-feature")
    assert_advisory_contract(errors.ProposalUnboundNotice("unbound", *details, fix=fix), commands)


@pytest.mark.parametrize(
    ("field", "value", "mode", "expected"),
    [
        ("fix", "uv run devkit gate run commit-msg <file>", "input", "placeholder"),
        ("fix", "Choose <low|medium|high>", "input", "placeholder"),
        ("fix", "Record <the user's reason>", "input", "placeholder"),
        ("fix", "devkit sync", "input", "lacks uv run"),
        ("fix", "Retry uv run devkit sync", "maintenance", "contradicts"),
        ("what_to_report", "Run `devkit sync`", "input", "REPORT lacks uv run"),
        ("details", "Run `devkit sync`", "input", "DETAIL lacks uv run"),
    ],
)
def test_constructed_contract_rejects_bad_dynamic_fields(
    field: str, value: str, mode: str, expected: str, commands: set[str]
) -> None:
    # Injection verifies the checker sees computed instance values, rather than just scanning this literal.
    text = "".join(value)
    error = AdvisoryError(
        "dynamic fixture",
        *([text] if field == "details" else []),
        actor=Actor.DEVELOPER,
        retry=Retry.AFTER_FIX,
        input_error=mode == "input",
        fix=text if field == "fix" else None,
        what_to_report=text if field == "what_to_report" else None,
    )
    with pytest.raises(AssertionError, match=expected):
        assert_advisory_contract(error, commands)
