"""Bindings by definition path, units outside the workspace root, lint errors from ``requests``,
feedback actions and same-second envelope voiding."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit.workflow import (
    DecisionInvalidError,
    Options,
    WorkflowNotBindableError,
    Workspace,
    create_unit,
    evaluate_definition,
    parse_definition,
    record_answer,
)
from devkit.workflow.cli import cli
from testsupport.workflow import write_config, write_record, write_unit

UNIT = ".devkit/transient/work/u"
SIMPLE = "---\nid: {id}\nschema_version: 1\nstages:\n  - id: s\n    exit: [{check}]\n---\n"


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def _workspace(root: Path, check: str = "anchor-exists") -> Path:
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True, exist_ok=True)
    (defs / "w.md").write_text(SIMPLE.format(id="w", check=check))
    write_config(root, '[workflow]\ndefault = "w"\n')
    return root


# --- binding by definition path -----------------------------------------------------------------


def test_bind_and_new_refuse_a_definition_path_outside_discovery(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    (root / "elsewhere").mkdir()
    (root / "elsewhere/x.md").write_text(SIMPLE.format(id="x", check="anchor-exists"))
    assert _run("new", "-w", str(root), "u").exit_code == 0
    anchor = (root / UNIT / "task.md").read_text()

    bound = _run("bind", "-w", str(root), "--unit", UNIT, "--workflow", "elsewhere/x.md")
    assert bound.exit_code == 2 and "(WORKFLOW_NOT_BINDABLE)" in bound.stderr and bound.stdout == ""
    assert (root / UNIT / "task.md").read_text() == anchor  # nothing written

    created = _run("new", "-w", str(root), "v", "--workflow", "elsewhere/x.md")
    assert created.exit_code == 2 and "(WORKFLOW_NOT_BINDABLE)" in created.stderr
    assert not (root / ".devkit/transient/work/v").exists()
    with pytest.raises(WorkflowNotBindableError):
        create_unit(Workspace(root), "v", workflow="elsewhere/x.md")

    # Evaluating against the file without binding stays possible.
    assert _run("next", "-w", str(root), "--unit", UNIT, "--workflow", "elsewhere/x.md").exit_code == 0


def test_a_path_whose_id_resolves_to_another_file_is_refused(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    (root / "elsewhere").mkdir()
    (root / "elsewhere/w.md").write_text(SIMPLE.format(id="w", check="file-exists(other.txt)"))
    assert _run("new", "-w", str(root), "u").exit_code == 0
    result = _run("bind", "-w", str(root), "--unit", UNIT, "--workflow", "elsewhere/w.md")
    assert result.exit_code == 2 and "(WORKFLOW_NOT_BINDABLE)" in result.stderr
    assert "that id resolves to .devkit/workflows/w.md" in result.stderr


def test_a_path_to_the_discovered_definition_binds_and_resolves_later(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    assert _run("new", "-w", str(root), "u", "--workflow", ".devkit/workflows/w.md").exit_code == 0
    bound = _run("bind", "-w", str(root), "--unit", UNIT, "--workflow", str(root / ".devkit/workflows/w.md"))
    assert bound.exit_code == 0 and bound.stdout.startswith("[BOUND: w ")
    for args in (("next",), ("requests",), ("show",)):
        result = _run(*args, "-w", str(root), "--unit", UNIT)
        assert result.exit_code == 0, (args, result.stderr)


# --- units outside the workspace root -----------------------------------------------------------


def test_lint_clean_on_a_unit_outside_the_root_is_a_reported_error(tmp_path: Path) -> None:
    root = _workspace(tmp_path / "project", check="lint-clean")
    outside = write_unit(tmp_path, "outside/u")
    result = _run("next", "-w", str(root), "--unit", str(outside), "--format", "json")
    assert result.exit_code == 2, result.output
    [error] = json.loads(result.stdout)["errors"]
    assert error["code"] == "PATH_UNSAFE" and "outside the workspace root" in error["message"]

    # A unit reached through a symbolic link that leaves the root is the same unit.
    (root / "linked").symlink_to(outside, target_is_directory=True)
    text = _run("next", "-w", str(root), "--unit", "linked")
    assert text.exit_code == 2 and "[LINT_ERROR: " in text.stdout and "(PATH_UNSAFE)" in text.stderr


def test_the_lint_detail_names_a_unit_outside_the_root_as_given(tmp_path: Path) -> None:
    doc = parse_definition(SIMPLE.format(id="w", check="lint-clean"))
    unit = write_unit(tmp_path, "outside/u")

    def lint(_root: Path, _files: list[str]) -> list[str]:
        return [f"v{i}" for i in range(5)]

    res = evaluate_definition(
        doc, Options(workspace_root=tmp_path / "work", unit_dir=unit, anchor="task.md", lint=lint)
    )
    assert res.unit == unit.as_posix() and res.lint_error is not None
    assert res.lint_error.code == "PATH_UNSAFE"
    # Inside the root, the detail names the unit relative to it.
    res = evaluate_definition(doc, Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md", lint=lint))
    assert "2 more (devkit rules check outside/u)" in res.unmet[0].detail


# --- requests reports the lint error ------------------------------------------------------------


def test_requests_reports_a_lint_error_like_next(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import devkit.rules

    def broken(*_: object, **__: object) -> None:
        raise RuntimeError("rule exploded")

    root = _workspace(tmp_path, check="lint-clean")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    monkeypatch.setattr(devkit.rules, "run_project_rules", broken)
    result = _run("requests", "-w", str(root), "--unit", UNIT, "--format", "json")
    assert result.exit_code == 2 and result.stderr == ""
    document = json.loads(result.stdout)
    assert document["requests"] == [] and [e["code"] for e in document["errors"]] == ["UNEXPECTED_ERROR"]
    text = _run("requests", "-w", str(root), "--unit", UNIT)
    assert text.stdout.splitlines() == ["[REQUESTS: none]", '[LINT_ERROR: "RuntimeError: rule exploded"]']
    assert text.exit_code == 2 and "(UNEXPECTED_ERROR) RuntimeError: rule exploded" in text.stderr

    clean = json.loads(_run("requests", "-w", str(root), "--unit", UNIT, "--no-lint", "--format", "json").stdout)
    assert clean == {"requests": [], "errors": []}


# --- feedback actions -----------------------------------------------------------------------------


def test_feedback_answers_validate_the_action(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    ws = Workspace(root)
    unit = create_unit(ws, "u")
    with pytest.raises(DecisionInvalidError):
        record_answer(ws, unit, "feedback:x", "approve", ["text"])
    assert not (unit.dir / "decisions").exists()


# --- same-second envelope voiding ----------------------------------------------------------------

REVIEWED = parse_definition("""---
id: reviewed
schema_version: 1
stages:
  - id: build
    exit: [file-exists(built.txt)]
  - id: review
    exit: [envelope-review-passed]
---
""")


@pytest.mark.parametrize("written", ["2026-10-12T09:30:00Z", "2026-10-12T09:30:00.900000+00:00"])
def test_a_return_voids_an_envelope_from_the_same_second(tmp_path: Path, written: str) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "built.txt").write_text("x")
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text(
        f"kind: review\nstatus: completed\nstage: review\ncreated_at: '{written}'\n"
    )
    opts = Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md", skip_lint=True)
    assert evaluate_definition(REVIEWED, opts).complete
    returned = {"kind": "return", "action": "accept", "workflow": "reviewed", "stage": "build"}
    write_record(unit, "01-return-build.yaml", request="return:build", at="2026-10-12T09:30:00Z", **returned)
    res = evaluate_definition(REVIEWED, opts)
    assert res.stage is not None and res.stage.id == "review"
    assert [u.name for u in res.unmet] == ["envelope-review-passed"]
