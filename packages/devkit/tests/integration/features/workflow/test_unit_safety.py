"""Regression tests for unit layout containment, anchor disambiguation, ``show --unit`` and anchor writes."""

from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import devkit_agt.features.workflow.repositories.unit.binding as binding_module
import devkit_agt.features.workflow.repositories.unit.records as records
import devkit_agt.features.workflow.usecases.units as units_module
import pytest
from click.testing import CliRunner, Result
from devkit_agt.features.workflow import (
    CreateUnitUseCase,
    LayoutError,
    TemplateLayout,
    UnitDirNotEmptyError,
    UnitExistsError,
    WorkflowNotBindableError,
    Workspace,
    parse_layout_spec,
    read_binding,
    validate_template,
)
from devkit_agt.features.workflow.cli import cli
from devkit_agt.features.workflow.models.binding import Binding
from devkit_agt.features.workflow.repositories.unit.binding import write_binding
from testsupport.workflow import (
    SIMPLE,
    SIMPLE_UNIT,
    WORKFLOW,
    run_cli,
    simple_workspace,
    write_config,
    write_record,
    write_unit,
)

PROPOSAL = """---
id: incubate
schema_version: 1
layout:
  work_dir: docs/proposals
  unit_path: "{slug}"
  anchor: proposal.md
stages:
  - id: draft
    exit: [anchor-exists]
    skills: [wf-draft]
next:
  - { workflow: direct-delivery }
---
"""
TRIAGE = """---
id: triage
schema_version: 1
stages:
  - id: decide
    exit: [anchor-exists]
    skills: [wf-decide]
next:
  - { workflow: direct-delivery }
---
"""


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


# --- layout containment ---------------------------------------------------------------


@pytest.mark.parametrize(
    "template",
    ["{date:/abs/outside-%Y}/{slug}", ".{date:.}/{slug}", "{date:%Y/..}/{slug}", "{date:..}/{slug}"],
)
def test_template_whose_date_spec_escapes_is_refused(template: str) -> None:
    with pytest.raises(LayoutError):
        validate_template(template)
    with pytest.raises(LayoutError):
        parse_layout_spec({"unit_path": template})


def test_new_refuses_a_layout_that_renders_outside_the_workspace(workspace: Path, tmp_path_factory) -> None:
    outside = tmp_path_factory.mktemp("outside")
    write_config(
        workspace, f'[workflow]\ndefault = "direct-delivery"\nunit_path = "{{date:{outside}/x-%Y}}/{{slug}}"\n'
    )
    result = _run("new", "-w", str(workspace), "esc", "--date", "2026-10-12")
    assert result.exit_code == 2 and "(WORKFLOW_CONFIG_INVALID)" in result.stderr
    assert not any(outside.iterdir())


def test_new_unit_refuses_a_rendering_that_leaves_work_dir() -> None:
    layout = TemplateLayout("specs", "{date:%Y}/{slug}", "task.md")
    object.__setattr__(layout, "unit_path", "{date:/abs/%Y}/{slug}")  # bypass construction-time validation
    with pytest.raises(LayoutError, match="escapes the work directory"):
        layout.new_unit("esc", date(2026, 10, 12))


def test_new_refuses_a_unit_directory_linked_outside_work_dir(workspace: Path, tmp_path_factory) -> None:
    outside = tmp_path_factory.mktemp("outside")
    write_config(workspace, '[workflow]\ndefault = "direct-delivery"\nunit_path = "{date:%Y}/{slug}"\n')
    work = workspace / ".devkit/transient/work"
    work.mkdir(parents=True)
    (work / "2026").symlink_to(outside, target_is_directory=True)
    result = _run("new", "-w", str(workspace), "esc", "--date", "2026-10-12")
    assert result.exit_code == 2 and "(LAYOUT_INVALID)" in result.stderr
    assert not any(outside.iterdir())


# --- anchor disambiguation --------------------------------------------------------------


@pytest.fixture
def ambiguous(workspace: Path) -> Path:
    (workspace / ".devkit/workflows/incubate.md").write_text(PROPOSAL, encoding="utf-8")
    write_config(workspace, '[workflow]\nwork_dir = "specs"\nanchor = "spec.md"\ndefault = "direct-delivery"\n')
    unit = write_unit(workspace, "docs/proposals/dup", anchor="proposal.md", extra="workflow: incubate\n")
    (unit / "spec.md").write_text("---\nid: dup\nstatus: planned\n---\n")
    return workspace


@pytest.mark.parametrize(
    "command",
    [
        ("next", "--no-lint"),
        ("bind",),
        ("next", "--view", "requests", "--no-lint"),
        ("answer", "--no-lint", "--request", "feedback:draft", "--action", "accept", "--value", "x"),
        ("return", "--no-lint", "--to", "draft"),
        ("show",),
    ],
)
def test_every_unit_command_resolves_an_ambiguous_unit_with_anchor(ambiguous: Path, command: tuple[str, ...]) -> None:
    base = [command[0], "-w", str(ambiguous), "--unit", "docs/proposals/dup", *command[1:]]
    refused = _run(*base)
    assert refused.exit_code == 2 and "(ANCHOR_AMBIGUOUS)" in refused.stderr
    for anchor in ("spec.md", "proposal.md"):
        assert f"[DETAIL] uv run devkit workflow {' '.join(base)} --anchor {anchor}" in refused.stderr
    resolved = _run(*base, "--anchor", "proposal.md")
    assert resolved.exit_code == 0, resolved.output + resolved.stderr


def test_handoff_resolves_an_ambiguous_unit_with_anchor(ambiguous: Path) -> None:
    write_config(
        ambiguous,
        '[workflow]\nwork_dir = "specs"\nanchor = "spec.md"\ndefault = "direct-delivery"\n'
        '[workflow.approvals]\nhandoff = "auto"\n',
    )
    (ambiguous / ".devkit/workflows/direct-delivery.md").write_text(
        WORKFLOW.replace("id: direct-delivery", "id: direct-delivery\nlayout: { anchor: proposal.md }", 1)
    )
    base = ["handoff", "-w", str(ambiguous), "--unit", "docs/proposals/dup", "--no-lint"]
    assert "(ANCHOR_AMBIGUOUS)" in _run(*base).stderr
    done = _run(*base, "--anchor", "proposal.md")
    assert done.exit_code == 0, done.stderr
    assert done.output.startswith("[HANDED_OFF: from=incubate to=direct-delivery")


def test_anchor_must_be_a_present_candidate_and_agree_with_workflow(ambiguous: Path) -> None:
    unit = ["-w", str(ambiguous), "--unit", "docs/proposals/dup", "--no-lint"]
    unknown = _run("next", *unit, "--anchor", "other.md")
    assert unknown.exit_code == 2 and "(UNIT_NOT_FOUND)" in unknown.stderr
    assert "Pass --anchor one of: spec.md, proposal.md" in unknown.stderr
    conflict = _run("next", *unit, "--workflow", "incubate", "--anchor", "spec.md")
    assert conflict.exit_code == 2 and "(ANCHOR_MISMATCH)" in conflict.stderr
    agreed = _run("next", *unit, "--workflow", "incubate", "--anchor", "proposal.md")
    assert agreed.exit_code == 0 and "[WORKFLOW: incubate" in agreed.output
    show = _run("show", "incubate", "-w", str(ambiguous), "--anchor", "proposal.md")
    assert show.exit_code == 2 and "(ARGUMENT_INVALID)" in show.stderr


def test_envelope_check_needs_only_some_anchor_and_new_resolves_the_unit(ambiguous: Path) -> None:
    unit = ["-w", str(ambiguous), "--unit", "docs/proposals/dup"]
    assert _run("envelope", "check", *unit).exit_code == 0
    # `new` records the bound workflow and segment, so it resolves the unit like every unit command.
    refused = _run(
        "envelope",
        "review",
        *unit,
    )
    assert refused.exit_code == 2 and "(ANCHOR_AMBIGUOUS)" in refused.stderr
    assert (
        _run(
            "envelope",
            "review",
            *unit,
            "--anchor",
            "proposal.md",
        ).exit_code
        == 0
    )
    missing = _run("envelope", "check", "-w", str(ambiguous), "--unit", "docs/proposals")
    assert missing.exit_code == 2 and "(UNIT_NOT_FOUND)" in missing.stderr


def test_anchor_mismatch_fix_names_a_command_every_caller_has(ambiguous: Path) -> None:
    write_unit(ambiguous, "specs/x", anchor="spec.md", extra="workflow: incubate\n")
    for command in (
        ("next", "--view", "requests"),
        ("next",),
        ("handoff",),
    ):
        result = _run(*command, "-w", str(ambiguous), "--unit", "specs/x", "--no-lint")
        assert result.exit_code == 2 and "(ANCHOR_MISMATCH)" in result.stderr
        assert "[DETAIL] uv run devkit workflow bind --unit specs/x --workflow direct-delivery" in result.stderr
    assert _run("bind", "-w", str(ambiguous), "--unit", "specs/x", "--workflow", "direct-delivery").exit_code == 0


# --- show --unit -------------------------------------------------------------------------------


def test_show_unit_reports_an_invalid_bound_definition(workspace: Path) -> None:
    (workspace / ".devkit/roles").mkdir()
    (workspace / ".devkit/roles/other.md").write_text("x")
    write_unit(workspace, ".devkit/transient/work/u", extra="workflow: direct-delivery\n")
    by_ref = _run("show", "direct-delivery", "-w", str(workspace))
    by_unit = _run("show", "--unit", ".devkit/transient/work/u", "-w", str(workspace))
    assert by_ref.exit_code == by_unit.exit_code == 1
    assert "[BINDING: workflow=direct-delivery]" in by_unit.output
    assert "[PROBLEM: review.role: unknown role 'reviewer'" in by_unit.output
    assert Workspace(workspace).describe_unit(".devkit/transient/work/u").errors


# --- anchor writes --------------------------------------------------------------------------


def test_binding_is_written_into_an_anchor_without_frontmatter(tmp_path: Path) -> None:
    anchor = tmp_path / "task.md"
    anchor.write_text("# plain\n\nbody\n")
    write_binding(anchor, Binding("wf"))
    assert anchor.read_text() == "---\nworkflow: wf\n---\n# plain\n\nbody\n"
    assert read_binding(anchor) == Binding("wf")


def test_binding_write_keeps_mode_and_original_on_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    anchor = tmp_path / "task.md"
    original = "---\nid: a\n---\n# a\n"
    anchor.write_text(original)
    anchor.chmod(0o640)
    write_binding(anchor, Binding("wf"))
    assert anchor.stat().st_mode & 0o777 == 0o640 and "workflow: wf" in anchor.read_text()

    anchor.write_text(original)

    def disk_full(*_: object) -> None:
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(binding_module.os, "replace", disk_full)
    with pytest.raises(OSError):
        write_binding(anchor, Binding("wf"))
    assert anchor.read_text() == original
    assert sorted(os.listdir(tmp_path)) == ["task.md"]


def test_binding_write_through_a_link_replaces_the_target(tmp_path: Path) -> None:
    real = tmp_path / "real.md"
    real.write_text("---\nid: a\n---\n")
    link = tmp_path / "task.md"
    link.symlink_to(real)
    write_binding(link, Binding("wf"))
    assert link.is_symlink() and "workflow: wf" in real.read_text()


@pytest.fixture
def chain(workspace: Path) -> Path:
    (workspace / ".devkit/workflows/triage.md").write_text(TRIAGE, encoding="utf-8")
    write_config(workspace, '[workflow]\ndefault = "triage"\n')
    unit = workspace / ".devkit/transient/work/plain"
    unit.mkdir(parents=True)
    (unit / "task.md").write_text("# plain\n")
    return workspace


def test_handoff_binds_an_anchor_without_frontmatter(chain: Path) -> None:
    unit = ".devkit/transient/work/plain"
    done = _run("handoff", "-w", str(chain), "--unit", unit, "--no-lint", "--workflow", "direct-delivery")
    assert done.exit_code == 0, done.stderr
    text = (chain / unit / "task.md").read_text()
    assert text.startswith("---\nworkflow: direct-delivery\n") and text.endswith("---\n# plain\n")
    assert (chain / unit / "decisions/01-handoff.yaml").is_file()


def test_failed_handoff_leaves_no_decision_record(chain: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    unit = chain / ".devkit/transient/work/plain"

    def disk_full(*_: object) -> None:
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(binding_module.os, "replace", disk_full)
    failed = _run("handoff", "-w", str(chain), "--unit", str(unit), "--no-lint", "--workflow", "direct-delivery")
    assert failed.exit_code != 0
    assert (unit / "task.md").read_text() == "# plain\n"
    assert not list((unit / "decisions").glob("*.yaml"))


# --- workflow selection -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        ("next", "--no-lint"),
        ("bind",),
        ("next", "--view", "requests", "--no-lint"),
        ("answer", "--no-lint", "--request", "gate:x", "--action", "accept"),
        ("return", "--no-lint", "--to", "plan"),
        ("handoff", "--no-lint"),
        ("show",),
    ],
)
def test_unbound_unit_without_default_names_bind(workspace: Path, command: tuple[str, ...]) -> None:
    write_unit(workspace, ".devkit/transient/work/u")
    result = _run(command[0], "-w", str(workspace), "--unit", ".devkit/transient/work/u", *command[1:])
    assert result.exit_code == 2 and "(WORKFLOW_NOT_SELECTED)" in result.stderr
    assert (
        "[FIX]    uv run devkit workflow bind --unit .devkit/transient/work/u --workflow direct-delivery"
        in result.stderr
    )
    bound = _run("bind", "-w", str(workspace), "--unit", ".devkit/transient/work/u", "--workflow", "direct-delivery")
    assert bound.exit_code == 0


def test_new_without_default_names_workflow_option(workspace: Path) -> None:
    result = _run("new", "-w", str(workspace), "login")
    assert result.exit_code == 2 and "(WORKFLOW_NOT_SELECTED)" in result.stderr
    assert "[FIX]    Pass --workflow with a workflow id `uv run devkit workflow validate` lists" in result.stderr


# --- binding by definition path ---------------------------------------------------------------


def test_bind_and_new_refuse_a_definition_path_outside_discovery(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    (root / "elsewhere").mkdir()
    (root / "elsewhere/x.md").write_text(SIMPLE.format(id="x", check="anchor-exists"))
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    anchor = (root / SIMPLE_UNIT / "task.md").read_text()

    bound = run_cli("bind", "-w", str(root), "--unit", SIMPLE_UNIT, "--workflow", "elsewhere/x.md")
    assert bound.exit_code == 2 and "(WORKFLOW_NOT_BINDABLE)" in bound.stderr and bound.stdout == ""
    assert (root / SIMPLE_UNIT / "task.md").read_text() == anchor  # nothing written

    created = run_cli("new", "-w", str(root), "v", "--workflow", "elsewhere/x.md")
    assert created.exit_code == 2 and "(WORKFLOW_NOT_BINDABLE)" in created.stderr
    assert not (root / ".devkit/transient/work/v").exists()
    with pytest.raises(WorkflowNotBindableError):
        CreateUnitUseCase().execute(Workspace(root), "v", workflow="elsewhere/x.md")

    # Evaluating against the file without binding stays possible.
    assert run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--workflow", "elsewhere/x.md").exit_code == 0


def test_a_path_whose_id_resolves_to_another_file_is_refused(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    (root / "elsewhere").mkdir()
    (root / "elsewhere/w.md").write_text(SIMPLE.format(id="w", check="file-exists(other.txt)"))
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    result = run_cli("bind", "-w", str(root), "--unit", SIMPLE_UNIT, "--workflow", "elsewhere/w.md")
    assert result.exit_code == 2 and "(WORKFLOW_NOT_BINDABLE)" in result.stderr
    assert "that id resolves to .devkit/workflows/w.md" in result.stderr


def test_a_path_to_the_discovered_definition_binds_and_resolves_later(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    assert run_cli("new", "-w", str(root), "u", "--workflow", ".devkit/workflows/w.md").exit_code == 0
    bound = run_cli("bind", "-w", str(root), "--unit", SIMPLE_UNIT, "--workflow", str(root / ".devkit/workflows/w.md"))
    assert bound.exit_code == 0 and bound.stdout.startswith("[BOUND: w]")
    for args in (
        ("next",),
        ("next", "--view", "requests"),
        ("show",),
    ):
        result = run_cli(*args, "-w", str(root), "--unit", SIMPLE_UNIT)
        assert result.exit_code == 0, (args, result.stderr)


# --- creating a unit --------------------------------------------------------------------------


def _leftovers(directory: Path) -> list[str]:
    return sorted(p.name for p in directory.iterdir() if records.is_temporary(p.name))


def test_new_refuses_a_directory_without_an_anchor_holding_records(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    (root / SIMPLE_UNIT / "decisions").mkdir(parents=True)
    write_record(
        root / SIMPLE_UNIT, "01-gate-g.yaml", request="gate:g", kind="approve", action="accept", workflow="w", stage="s"
    )
    with pytest.raises(UnitDirNotEmptyError) as raised:
        CreateUnitUseCase().execute(Workspace(root), "u")
    assert raised.value.code == "UNIT_DIR_NOT_EMPTY"
    assert raised.value.target_files == (f"{SIMPLE_UNIT}/decisions/01-gate-g.yaml",)
    assert not (root / SIMPLE_UNIT / "task.md").exists()
    result = run_cli("new", "-w", str(root), "u")
    assert result.exit_code == 2 and "(UNIT_DIR_NOT_EMPTY)" in result.stderr and "[FIX]" in result.stderr

    (root / SIMPLE_UNIT / "decisions/01-gate-g.yaml").unlink()
    (root / SIMPLE_UNIT / "envelopes").mkdir()
    (root / SIMPLE_UNIT / "envelopes/review-01.yml").write_text("kind: review\nstatus: completed\n")
    with pytest.raises(UnitDirNotEmptyError) as raised:
        CreateUnitUseCase().execute(Workspace(root), "u")
    assert raised.value.target_files == (f"{SIMPLE_UNIT}/envelopes/review-01.yml",)


def test_new_uses_an_existing_directory_without_records(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    unit_dir = root / SIMPLE_UNIT
    (unit_dir / "decisions").mkdir(parents=True)
    (unit_dir / "envelopes").mkdir()
    for name in (".DS_Store", ".gitkeep", "notes.md", "decisions/README.md", "decisions/.01-x.yaml.0123456789ab.tmp"):
        (unit_dir / name).write_text("kept")
    unit = CreateUnitUseCase().execute(Workspace(root), "u")
    assert unit.anchor_path.is_file() and (unit.dir / "envelopes").is_dir()
    assert (unit_dir / "notes.md").read_text() == "kept" and (unit_dir / ".gitkeep").is_file()


def test_concurrent_new_calls_create_one_unit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = simple_workspace(tmp_path)
    calls = 8
    # Every call passes the existence checks before any of them writes: only the exclusive write tells them apart.
    barrier = threading.Barrier(calls, timeout=10)
    write = units_module.write_new_file

    def write_together(path: Path, body: str) -> bool:
        barrier.wait()
        return write(path, body)

    monkeypatch.setattr(units_module, "write_new_file", write_together)

    def create(_: int) -> str:
        try:
            CreateUnitUseCase().execute(Workspace(root), "u")
        except (UnitExistsError, UnitDirNotEmptyError) as exc:
            return exc.code
        return "created"

    with ThreadPoolExecutor(max_workers=calls) as pool:
        outcomes = list(pool.map(create, range(calls)))
    assert outcomes.count("created") == 1
    assert set(outcomes) == {"created", "UNIT_EXISTS"}
    assert _leftovers(root / SIMPLE_UNIT) == []


def test_new_never_overwrites_an_anchor_that_appears_meanwhile(tmp_path: Path) -> None:
    anchor = tmp_path / "task.md"
    anchor.write_text("first")
    assert records.write_new_file(anchor, "second") is False
    assert anchor.read_text() == "first" and _leftovers(tmp_path) == []
    assert records.write_new_file(tmp_path / "other.md", "x") is True
    assert os.stat(tmp_path / "other.md").st_mode & 0o777 == 0o666 & ~_umask()


def _umask() -> int:
    current = os.umask(0)
    os.umask(current)
    return current
