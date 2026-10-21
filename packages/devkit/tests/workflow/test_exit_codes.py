"""Exit codes of ``devkit workflow`` (0 ok, 1 findings, 2 error) and the codes of library errors."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit.advisory import ActionMode, ExitCode
from devkit_agt.features.workflow import (
    CheckError,
    DecisionRecordError,
    Decisions,
    DefinitionError,
    LayoutError,
    WorkflowConfigError,
    WorkflowError,
    Workspace,
    is_ancestor,
    load_decisions,
    load_envelopes,
    new_decision,
    parse_check,
    parse_definition,
    parse_layout_spec,
    write_envelope,
)
from devkit_agt.features.workflow.cli import cli
from devkit_core.base.errors import GitError
from devkit_dist.base.errors import ConfigError as CoreConfigError
from devkit_dist.base.errors import ReceiptError
from testsupport.workflow import WORKFLOW, write_config

UNIT = ".devkit/transient/work/login"


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


@pytest.fixture
def unit_ws(workspace: Path) -> Path:
    write_config(workspace, 'schema = 1\n[workflow]\ndefault = "direct-delivery"\n')
    assert _run("new", "-w", str(workspace), "login").exit_code == 0
    return workspace


# --- 0: success, including states that wait for a person -----------------------------------------


def test_waiting_for_a_human_gate_is_success(unit_ws: Path) -> None:
    result = _run("next", "-w", str(unit_ws), "--unit", UNIT, "--no-lint")
    assert result.exit_code == ExitCode.OK and "[GATE: direction" in result.output


def test_a_valid_workspace_validates_with_zero(unit_ws: Path) -> None:
    assert _run("validate", "-w", str(unit_ws)).exit_code == ExitCode.OK


# --- 1: the command ran and reports a negative result ----------------------------------------------


def test_validate_and_show_with_problems_exit_one(unit_ws: Path) -> None:
    definition = unit_ws / ".devkit/workflows/direct-delivery.md"
    definition.write_text(WORKFLOW.replace("anchor-exists", "nope"))
    assert _run("validate", "-w", str(unit_ws)).exit_code == ExitCode.FINDINGS
    assert _run("show", "-w", str(unit_ws), "direct-delivery").exit_code == ExitCode.FINDINGS


def test_envelope_check_with_malformed_files_exits_one(unit_ws: Path) -> None:
    (unit_ws / UNIT / "envelopes/review-01.yaml").write_text("status: completed\n")
    result = _run("envelope", "check", "-w", str(unit_ws), "--unit", UNIT)
    assert result.exit_code == ExitCode.FINDINGS and "(ENVELOPE_INVALID)" in result.stderr


# --- 2: the command could not do its job ------------------------------------------------------------


def test_usage_error_exits_two(unit_ws: Path) -> None:
    assert _run("next", "-w", str(unit_ws)).exit_code == ExitCode.ERROR  # --unit is required


def test_unknown_unit_exits_two_with_a_json_error(unit_ws: Path) -> None:
    result = _run("next", "-w", str(unit_ws), "--unit", "nowhere", "--format", "json")
    assert result.exit_code == ExitCode.ERROR and result.stderr == ""
    assert json.loads(result.stdout)["error"]["code"] == "UNIT_NOT_FOUND"


def test_invalid_config_exits_two(tmp_path: Path) -> None:
    write_config(tmp_path, "[workflow\n")
    result = _run("list", "-w", str(tmp_path))
    assert result.exit_code == ExitCode.ERROR and "(CONFIG_INVALID)" in result.stderr


def test_malformed_receipt_exits_two_with_the_core_fix(unit_ws: Path) -> None:
    (unit_ws / ".devkit/installation.json").write_text("{not json")
    result = _run("validate", "-w", str(unit_ws))
    assert result.exit_code == ExitCode.ERROR and "(RECEIPT_INVALID)" in result.stderr
    assert "git checkout -- .devkit/installation.json" in result.stderr


def test_unloadable_definition_makes_validate_exit_two(unit_ws: Path) -> None:
    (unit_ws / ".devkit/workflows/broken.md").write_text("---\nid: [\n---\n")
    result = _run("validate", "-w", str(unit_ws), "--format", "json")
    assert result.exit_code == ExitCode.ERROR
    assert [e["code"] for e in json.loads(result.stdout)["errors"]] == ["WORKFLOW_DEFINITION_INVALID"]


@pytest.mark.parametrize(
    "args",
    [
        ("validate", "{root}/missing.md"),
        ("list", "-w", "{root}/missing"),
        ("next", "-w", "{root}/missing", "--unit", UNIT),
    ],
)
def test_argument_errors_in_json_mode_print_one_document(unit_ws: Path, args: tuple[str, ...]) -> None:
    argv = [arg.format(root=unit_ws) for arg in args]
    if "-w" not in argv:
        argv[1:1] = ["-w", str(unit_ws)]
    result = _run(*argv, "--format", "json")
    assert result.exit_code == ExitCode.ERROR, result.output
    assert json.loads(result.stdout)["error"]["code"] == "ARGUMENT_INVALID"


def test_every_json_command_prints_one_object(unit_ws: Path) -> None:
    for args in (
        ("list",),
        ("checks",),
        ("validate",),
        ("requests", "--unit", UNIT, "--no-lint"),
        ("next", "--unit", UNIT, "--no-lint"),
        ("show", "direct-delivery"),
        ("envelope", "check", "--unit", UNIT),
    ):
        result = _run(*args, "-w", str(unit_ws), "--format", "json")
        assert result.exit_code == ExitCode.OK, (args, result.output)
        assert isinstance(json.loads(result.stdout), dict), args
    assert set(json.loads(_run("list", "-w", str(unit_ws), "--format", "json").stdout)) == {"units"}
    assert set(json.loads(_run("checks", "-w", str(unit_ws), "--format", "json").stdout)) == {"checks"}


def test_unexpected_exception_exits_two(unit_ws: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_: object, **__: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(Workspace, "evaluate_unit", boom)
    result = _run("next", "-w", str(unit_ws), "--unit", UNIT, "--no-lint")
    assert result.exit_code == ExitCode.ERROR and "(UNEXPECTED_ERROR) RuntimeError: boom" in result.stderr


# --- library errors carry codes -------------------------------------------------------------------


def test_library_errors_are_workflow_errors_with_codes(tmp_path: Path) -> None:
    with pytest.raises(LayoutError) as layout:
        parse_layout_spec({"anchor": "a/b.md"})
    with pytest.raises(DefinitionError) as definition:
        parse_definition("no frontmatter")
    with pytest.raises(CheckError) as check:
        parse_check("bad(")
    with pytest.raises(WorkflowError) as request:
        new_decision(Decisions(), "nope", "accept", workflow="w")
    with pytest.raises(WorkflowError) as kind:
        write_envelope(tmp_path, "Bad", "x")
    codes = [e.value.code for e in (layout, definition, check, request, kind)]
    assert codes == [
        "LAYOUT_INVALID",
        "WORKFLOW_DEFINITION_INVALID",
        "WORKFLOW_CHECK_INVALID",
        "REQUEST_UNKNOWN",
        "ENVELOPE_KIND_INVALID",
    ]
    assert all(e.value.mode is ActionMode.INPUT_ERROR for e in (layout, definition, check, request, kind))
    assert issubclass(DecisionRecordError, WorkflowError)


def test_config_error_is_both_a_workflow_and_a_core_config_error(tmp_path: Path) -> None:
    write_config(tmp_path, '[workflow]\nanchor = "a/b"\n')
    with pytest.raises(WorkflowConfigError) as info:
        Workspace(tmp_path)
    assert isinstance(info.value, WorkflowError) and isinstance(info.value, CoreConfigError)
    assert info.value.code == "WORKFLOW_CONFIG_INVALID" and info.value.target_files == (".devkit/config.toml",)


def test_core_errors_pass_through(tmp_path: Path) -> None:
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/installation.json").write_text("{")
    with pytest.raises(ReceiptError):
        _ = Workspace(tmp_path).receipt
    with pytest.raises(GitError) as git:
        is_ancestor(tmp_path, "not-hex", "abc1234")
    assert git.value.mode is ActionMode.INPUT_ERROR


def test_collected_entries_carry_codes(tmp_path: Path) -> None:
    (tmp_path / "envelopes").mkdir()
    (tmp_path / "envelopes/review-01.yaml").write_text("status: completed\n")
    (tmp_path / "decisions").mkdir()
    (tmp_path / "decisions/01-gate-x.yaml").write_text("request: gate:x\n")
    assert load_envelopes(tmp_path).errors[0].to_dict()["code"] == "ENVELOPE_INVALID"
    assert load_decisions(tmp_path).errors[0].to_dict()["code"] == "DECISION_RECORD_INVALID"


@pytest.mark.parametrize("output_format", ["text", "json"])
def test_show_exits_one_even_when_a_problem_carries_exit_code_two(
    unit_ws: Path, monkeypatch: pytest.MonkeyPatch, output_format: str
) -> None:
    # ``show`` produced its report, so it exits 1; 2 is only for a show that cannot run.
    from devkit_agt.features.workflow import DefinitionProblem

    problem = DefinitionProblem("serious", where="review.role", exit_code=ExitCode.ERROR)
    monkeypatch.setattr(Workspace, "validate_definition", lambda self, doc, known=None: [problem])
    result = _run("show", "-w", str(unit_ws), "direct-delivery", "--format", output_format)
    assert result.exit_code == ExitCode.FINDINGS
    if output_format == "json":
        assert json.loads(result.stdout)["errors"][0]["exit_code"] == int(ExitCode.ERROR)
