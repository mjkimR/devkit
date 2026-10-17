"""The shared devkit conventions as the workflow engine applies them.

One class per error code, collected problems as advisory errors, full-match
grammars, the cached workspace sources and the library entry points.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import devkit.workflow.errors as workflow_errors
import devkit.workflow.workspace as workspace_module
import pytest
from click.testing import CliRunner, Result
from devkit.advisory import ActionMode, AdvisoryError
from devkit.workflow import (
    AnchorInvalidError,
    DecisionRecordError,
    DefinitionProblem,
    EnvelopeFormatError,
    HistoryEntry,
    WorkflowConfigError,
    WorkflowError,
    Workspace,
    create_unit,
    list_units,
    load_decisions,
    load_envelopes,
    read_binding,
    write_binding,
)
from devkit.workflow.cli import cli
from devkit.workflow.definition.ids import is_ident
from devkit.workflow.evaluation.git import is_revision
from devkit.workflow.project.config import parse_workflow_config
from devkit.workflow.project.layout import validate_relative_dir
from devkit.workflow.unit.decisions import is_request_id
from devkit.workflow.unit.envelope import FILE
from testsupport.workflow import WORKFLOW, write_config

UNIT = ".devkit/transient/work/u"


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def _workspace(root: Path) -> Path:
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "direct-delivery.md").write_text(WORKFLOW)
    write_config(root, '[workflow]\ndefault = "direct-delivery"\n')
    return root


# --- error classes ------------------------------------------------------------------------------


def _error_classes() -> list[type[WorkflowError]]:
    return [
        cls
        for _, cls in inspect.getmembers(workflow_errors, inspect.isclass)
        if issubclass(cls, WorkflowError)
        and cls.__module__ == workflow_errors.__name__
        and not cls.__name__.startswith("_")
    ]


def test_every_code_has_exactly_one_class() -> None:
    """A collected form (``DefinitionProblem``, ``CheckReferenceProblem``) inherits its code; nothing redeclares one."""
    by_code: dict[str, list[str]] = {}
    for cls in _error_classes():
        if "code" in vars(cls):
            by_code.setdefault(cls.code, []).append(cls.__name__)
    shared = {code: names for code, names in by_code.items() if len(names) > 1}
    assert shared == {}
    assert workflow_errors.CheckReferenceProblem("x").code == "WORKFLOW_CHECK_INVALID"
    assert int(workflow_errors.CheckReferenceProblem("x").exit_code) == 1
    assert {"WORKFLOW_DEFINITION_INVALID", "WORKFLOW_CHECK_INVALID"} <= set(by_code)


def test_the_base_class_sets_actor_and_retry_once() -> None:
    error = WorkflowError("x")
    assert error.mode is ActionMode.MAINTENANCE
    assert WorkflowConfigError("x").code == "WORKFLOW_CONFIG_INVALID"
    assert workflow_errors.HandoffChoiceRequiredError("x").mode is ActionMode.INTERACTION
    assert workflow_errors.WorkflowAssetMissingError("x").mode is ActionMode.AUTO


# --- full-match grammars --------------------------------------------------------------------------


def test_grammars_match_in_full() -> None:
    assert is_ident("gate") and not is_ident("gate\n") and not is_ident("Gate")
    assert is_request_id("gate:x") and not is_request_id("gate:x\n")
    assert is_revision("abcdef0") and not is_revision("abcdef0\n")
    assert FILE.fullmatch("review-01.yaml") and not FILE.fullmatch("review-01.yaml\n")
    with pytest.raises(WorkflowConfigError, match="gate names"):
        parse_workflow_config({"workflow": {"approvals": {"gate\n": "ask"}}})


def test_relative_dirs_use_the_core_path_rules() -> None:
    assert validate_relative_dir("docs//./proposals/") == "docs/proposals"
    for bad in ("/abs", "a/../b", "a\\b", "C:x", "."):
        with pytest.raises(workflow_errors.LayoutError):
            validate_relative_dir(bad)


# --- collected problems -----------------------------------------------------------------------------


def test_collected_problems_are_advisory_errors(tmp_path: Path) -> None:
    unit = tmp_path / "u"
    (unit / "decisions").mkdir(parents=True)
    (unit / "decisions/01-gate-x.yaml").write_text("- not a mapping\n")
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text("status: completed\n")
    [decision] = load_decisions(unit).errors
    [envelope] = load_envelopes(unit).errors
    assert isinstance(decision, DecisionRecordError) and isinstance(envelope, EnvelopeFormatError)
    assert decision.to_dict()["file"] == "decisions/01-gate-x.yaml"
    assert envelope.to_dict()["file"] == "envelopes/review-01.yaml"
    assert envelope.advisory.target_files == ("envelopes/review-01.yaml",)
    problem = DefinitionProblem("bad", where="build.exit")
    assert str(problem) == "build.exit: bad" and problem.to_dict()["where"] == "build.exit"
    assert int(problem.exit_code) == 1


def test_unit_info_error_is_coded(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    broken = root / ".devkit/transient/work/broken"
    broken.mkdir(parents=True)
    (broken / "task.md").write_text("---\nid: [x\n---\n")
    [row] = list_units(Workspace(root))
    assert isinstance(row.error, AnchorInvalidError)
    assert row.error.to_dict()["code"] == "ANCHOR_INVALID" and row.to_dict()["error"] is not None
    listed = _run("list", "-w", str(root))
    assert "[UNIT: .devkit/transient/work/broken status=- workflow=- anchor=task.md error=" in listed.output


# --- argument checks ------------------------------------------------------------------------------------


def test_semantic_argument_checks_are_argument_invalid(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    bad_date = _run("new", "-w", str(root), "u", "--date", "tomorrow")
    assert bad_date.exit_code == 2 and "(ARGUMENT_INVALID)" in bad_date.stderr
    both = _run("show", "-w", str(root), "direct-delivery", "--unit", UNIT, "--format", "json")
    assert both.exit_code == 2 and json.loads(both.stdout)["error"]["code"] == "ARGUMENT_INVALID"


# --- library entry points ------------------------------------------------------------------------------


def test_bind_unit_rebinds_and_keeps_history(tmp_path: Path) -> None:
    ws = Workspace(_workspace(tmp_path))
    unit = create_unit(ws, "u")
    old = read_binding(unit.anchor_path)
    write_binding(unit.anchor_path, type(old)("direct-delivery", (HistoryEntry("triage", "2026-10-12", 2),)))
    rebound = ws.bind_unit(unit.rel)
    assert rebound.binding.workflow == "direct-delivery"
    assert rebound.binding.history == (HistoryEntry("triage", "2026-10-12", 2),)
    assert read_binding(unit.anchor_path) == rebound.binding


def test_workspace_loads_each_source_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _workspace(tmp_path)
    calls = {"receipt": 0, "discover": 0}
    real_receipt, real_discover = workspace_module.load_receipt, workspace_module.discover_definitions

    def count_receipt(*args: object) -> object:
        calls["receipt"] += 1
        return real_receipt(*args)  # type: ignore[arg-type]

    def count_discover(*args: object) -> object:
        calls["discover"] += 1
        return real_discover(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(workspace_module, "load_receipt", count_receipt)
    monkeypatch.setattr(workspace_module, "discover_definitions", count_discover)
    ws = Workspace(root)
    for _ in range(2):
        ws.load_definition("direct-delivery")
        ws.definition()
        ws.validate_definitions()
    unit = create_unit(ws, "u")
    ws.evaluate_unit(ws.resolve_unit(unit.rel), lint=False)
    assert calls == {"receipt": 1, "discover": 1}
    assert ws.config.layout is ws.config.layout


def test_lint_errors_pass_through(tmp_path: Path) -> None:
    refusal = AdvisoryError("rules could not run", code="RULES_RUN_FAILED")

    def lint(root: Path, files: list[str]) -> list[str]:
        raise refusal

    root = _workspace(tmp_path)
    (root / ".devkit/workflows/direct-delivery.md").write_text(
        "---\nid: direct-delivery\nschema_version: 1\nstages:\n  - id: s\n    exit: [lint-clean]\n---\n"
    )
    ws = Workspace(root, lint=lint)
    unit = create_unit(ws, "u")
    assert ws.evaluate_unit(unit).lint_error is refusal
