"""Regression tests for unit layout containment, anchor disambiguation, ``show --unit`` and anchor writes."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit.workflow import LayoutError, TemplateLayout, Workspace, parse_layout_spec, read_binding, validate_template
from devkit.workflow.cli import cli
from devkit.workflow.unit import binding as binding_module
from devkit.workflow.unit.binding import Binding, write_binding
from testsupport.workflow import WORKFLOW, write_config, write_unit

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
        ("requests", "--no-lint"),
        ("answer", "--no-lint", "--request", "feedback:draft", "--action", "accept", "--value", "x"),
        ("return", "--no-lint", "--to", "draft"),
        ("show",),
    ],
)
def test_every_unit_command_resolves_an_ambiguous_unit_with_anchor(ambiguous: Path, command: tuple[str, ...]) -> None:
    base = [command[0], "-w", str(ambiguous), "--unit", "docs/proposals/dup", *command[1:]]
    refused = _run(*base)
    assert refused.exit_code == 2 and "(ANCHOR_AMBIGUOUS)" in refused.stderr
    assert "[FIX]    Pass --anchor <file> with one of spec.md, proposal.md" in refused.stderr
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
    assert done.output.startswith("[HANDOFF: from=incubate to=direct-delivery")


def test_anchor_must_be_a_present_candidate_and_agree_with_workflow(ambiguous: Path) -> None:
    unit = ["-w", str(ambiguous), "--unit", "docs/proposals/dup", "--no-lint"]
    unknown = _run("next", *unit, "--anchor", "other.md")
    assert unknown.exit_code == 2 and "(UNIT_NOT_FOUND)" in unknown.stderr
    assert "Pass --anchor with one of: spec.md, proposal.md" in unknown.stderr
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
    refused = _run("envelope", "new", *unit, "--kind", "review")
    assert refused.exit_code == 2 and "(ANCHOR_AMBIGUOUS)" in refused.stderr
    assert _run("envelope", "new", *unit, "--anchor", "proposal.md", "--kind", "review").exit_code == 0
    missing = _run("envelope", "check", "-w", str(ambiguous), "--unit", "docs/proposals")
    assert missing.exit_code == 2 and "(UNIT_NOT_FOUND)" in missing.stderr


def test_anchor_mismatch_fix_names_a_command_every_caller_has(ambiguous: Path) -> None:
    write_unit(ambiguous, "specs/x", anchor="spec.md", extra="workflow: incubate\n")
    for command in (("requests",), ("next",), ("handoff",)):
        result = _run(*command, "-w", str(ambiguous), "--unit", "specs/x", "--no-lint")
        assert result.exit_code == 2 and "(ANCHOR_MISMATCH)" in result.stderr
        assert "`devkit workflow bind --unit specs/x --workflow <id>`" in result.stderr
    assert _run("bind", "-w", str(ambiguous), "--unit", "specs/x", "--workflow", "direct-delivery").exit_code == 0


# --- show --unit -------------------------------------------------------------------------------


def test_show_unit_reports_an_invalid_bound_definition(workspace: Path) -> None:
    (workspace / ".devkit/roles").mkdir()
    (workspace / ".devkit/roles/other.md").write_text("x")
    write_unit(workspace, ".devkit/transient/work/u", extra="workflow: direct-delivery\n")
    by_ref = _run("show", "direct-delivery", "-w", str(workspace))
    by_unit = _run("show", "--unit", ".devkit/transient/work/u", "-w", str(workspace))
    assert by_ref.exit_code == by_unit.exit_code == 1
    assert "[BINDING: workflow=direct-delivery hash=- drift=false]" in by_unit.output
    assert "[PROBLEM: review.role: unknown role 'reviewer'" in by_unit.output
    assert Workspace(workspace).describe_unit(".devkit/transient/work/u").errors


# --- anchor writes --------------------------------------------------------------------------


def test_binding_is_written_into_an_anchor_without_frontmatter(tmp_path: Path) -> None:
    anchor = tmp_path / "task.md"
    anchor.write_text("# plain\n\nbody\n")
    write_binding(anchor, Binding("wf", "sha256:1"))
    assert anchor.read_text() == "---\nworkflow: wf\nworkflow_hash: sha256:1\n---\n# plain\n\nbody\n"
    assert read_binding(anchor) == Binding("wf", "sha256:1")


def test_binding_write_keeps_mode_and_original_on_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    anchor = tmp_path / "task.md"
    original = "---\nid: a\n---\n# a\n"
    anchor.write_text(original)
    anchor.chmod(0o640)
    write_binding(anchor, Binding("wf", "sha256:1"))
    assert anchor.stat().st_mode & 0o777 == 0o640 and "workflow: wf" in anchor.read_text()

    anchor.write_text(original)

    def disk_full(*_: object) -> None:
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(binding_module.os, "replace", disk_full)
    with pytest.raises(OSError):
        write_binding(anchor, Binding("wf", "sha256:2"))
    assert anchor.read_text() == original
    assert sorted(os.listdir(tmp_path)) == ["task.md"]


def test_binding_write_through_a_link_replaces_the_target(tmp_path: Path) -> None:
    real = tmp_path / "real.md"
    real.write_text("---\nid: a\n---\n")
    link = tmp_path / "task.md"
    link.symlink_to(real)
    write_binding(link, Binding("wf", "sha256:1"))
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
        ("requests", "--no-lint"),
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
    assert "`devkit workflow bind --unit .devkit/transient/work/u --workflow <id>`" in result.stderr
    bound = _run("bind", "-w", str(workspace), "--unit", ".devkit/transient/work/u", "--workflow", "direct-delivery")
    assert bound.exit_code == 0


def test_new_without_default_names_workflow_option(workspace: Path) -> None:
    result = _run("new", "-w", str(workspace), "login")
    assert result.exit_code == 2 and "(WORKFLOW_NOT_SELECTED)" in result.stderr
    assert "[FIX]    Pass --workflow <id>, or set [workflow].default" in result.stderr
