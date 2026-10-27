"""Role vocabulary, show --unit, list filters and shared-stage consistency."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner, Result
from devkit_agt.features.workflow import (
    Options,
    compare_shared_stages,
    discover_roles,
    evaluate_definition,
    parse_definition,
    validate_definition,
)
from devkit_agt.features.workflow.cli import cli
from testsupport.workflow import WORKFLOW, write_config, write_receipt, write_unit

CONFIG = """schema = 1
[workflow]
default = "direct-delivery"

[workflow.approvals]
direction = "auto"
"""


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def _receipt(root: Path, assets: list[dict]) -> None:
    write_receipt(root, assets)


# --- roles ----------------------------------------------------------------------


def test_discover_roles_sources(tmp_path: Path) -> None:
    assert discover_roles(tmp_path, ".devkit/roles") is None
    _receipt(
        tmp_path,
        [
            {
                "kind": "subagent",
                "id": "reviewer",
                "paths": [".claude/agents/reviewer.md", ".devkit/managed/team/subagents/reviewer.md"],
            },
            {"kind": "subagent", "id": "scout", "paths": [".codex/agents/scout.toml"]},
            {"kind": "skill", "id": "review", "paths": [".agents/skills/review/SKILL.md"]},
        ],
    )
    contract = tmp_path / ".devkit/managed/team/subagents/reviewer.md"
    contract.parent.mkdir(parents=True)
    contract.write_text("---\nrole: code-reviewer\ntitle: R\n---\nbody\n")
    roles = discover_roles(tmp_path, ".devkit/roles")
    assert roles == {
        "reviewer": ".devkit/managed/team/subagents/reviewer.md",
        "code-reviewer": ".devkit/managed/team/subagents/reviewer.md",
        "scout": ".codex/agents/scout.toml",
    }
    local = tmp_path / ".devkit/roles"
    local.mkdir()
    (local / "scout.md").write_text("# local scout\n")
    (local / "Bad Name.md").write_text("ignored\n")
    roles = discover_roles(tmp_path, ".devkit/roles")
    assert roles is not None and roles["scout"] == ".devkit/roles/scout.md" and "Bad Name" not in roles


def test_validate_reports_unknown_role_only_when_vocabulary_is_known() -> None:
    doc = parse_definition(WORKFLOW)
    assert validate_definition(doc, "task.md", roles=None) == []
    problems = validate_definition(doc, "task.md", roles={})
    assert [str(p) for p in problems] == ["review.role: unknown role 'reviewer' (no subagent contract found)"]
    assert validate_definition(doc, "task.md", roles={"reviewer": ".devkit/roles/reviewer.md"}) == []


def test_validate_cli_skips_or_enforces_roles(workspace: Path) -> None:
    skipped = _run("validate", "-w", str(workspace))
    assert skipped.exit_code == 0
    assert skipped.stderr == (
        "[NOTICE] (WORKFLOW_ROLES_UNCHECKED) stage roles were not checked: no installation receipt and no .devkit/roles\n"
    )  # brief: no [ACTION] line
    as_json = json.loads(_run("validate", "-w", str(workspace), "--format", "json").stdout)
    assert as_json["roles_checked"] is False and [n["code"] for n in as_json["notices"]] == ["WORKFLOW_ROLES_UNCHECKED"]
    (workspace / ".devkit/roles").mkdir()
    enforced = _run("validate", "-w", str(workspace))
    assert enforced.exit_code == 1 and "review.role: unknown role 'reviewer'" in enforced.output
    (workspace / ".devkit/roles/reviewer.md").write_text("# reviewer\n")
    assert _run("validate", "-w", str(workspace)).exit_code == 0


def test_delegate_cites_the_contract(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    (workspace / ".devkit/roles").mkdir()
    (workspace / ".devkit/roles/reviewer.md").write_text("# reviewer\n")
    unit = write_unit(workspace, ".devkit/transient/work/login")
    (unit / "tasks.md").write_text("- [x] done\n")
    result = _run("next", "-w", str(workspace), "--unit", str(unit), "--no-lint")
    assert result.exit_code == 0, result.output
    assert "[DELEGATE: role=reviewer isolation=preferred contract=.devkit/roles/reviewer.md]" in result.output
    data = json.loads(_run("next", "-w", str(workspace), "--unit", str(unit), "--no-lint", "--format", "json").stdout)
    assert data["delegate"] == {"role": "reviewer", "isolation": "preferred", "contract": ".devkit/roles/reviewer.md"}


def test_delegate_without_vocabulary_has_no_contract(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "tasks.md").write_text("- [x] done\n")
    opts = Options(
        workspace_root=tmp_path, unit_dir=unit, anchor="task.md", skip_lint=True, approvals={"direction": "auto"}
    )
    res = evaluate_definition(parse_definition(WORKFLOW), opts)
    assert res.delegate is not None and res.delegate.contract is None
    assert res.delegate.to_dict() == {"role": "reviewer", "isolation": "preferred", "contract": None}


# --- show --unit ----------------------------------------------------------------


def test_show_unit_prints_binding_and_current_definition(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    assert _run("new", "-w", str(workspace), "login").exit_code == 0
    unit = ".devkit/transient/work/login"
    shown = _run("show", "-w", str(workspace), "--unit", unit)
    assert shown.exit_code == 0, shown.output
    assert "[WORKFLOW: direct-delivery" in shown.output
    assert "[BINDING: workflow=direct-delivery]" in shown.output
    data = json.loads(_run("show", "-w", str(workspace), "--unit", unit, "--format", "json").stdout)
    assert data["binding"] == {"workflow": "direct-delivery", "workflow_history": []}

    definition = workspace / ".devkit/workflows/direct-delivery.md"
    definition.write_text(definition.read_text().replace("skills: [wf-build]", "skills: [wf-implement]"))
    updated = _run("show", "-w", str(workspace), "--unit", unit)
    assert updated.exit_code == 0 and "wf-implement" in updated.output

    both = _run("show", "-w", str(workspace), "direct-delivery", "--unit", unit)
    assert both.exit_code == 2 and "(ARGUMENT_INVALID)" in both.stderr
    neither = _run("show", "-w", str(workspace), "--format", "json")
    assert neither.exit_code == 2 and json.loads(neither.stdout)["error"]["code"] == "ARGUMENT_INVALID"


# --- list filters ---------------------------------------------------------------


def test_list_status_filters(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    write_unit(workspace, ".devkit/transient/work/a", status="planned")
    write_unit(workspace, ".devkit/transient/work/b", status="completed")
    write_unit(workspace, ".devkit/transient/work/c", status="in-progress")
    everything = json.loads(_run("list", "-w", str(workspace), "--format", "json").stdout)["units"]
    assert [row["status"] for row in everything] == ["planned", "completed", "in-progress"]
    active = json.loads(_run("list", "-w", str(workspace), "--exclude-status", "completed", "--format", "json").stdout)[
        "units"
    ]
    assert [row["unit"] for row in active] == [".devkit/transient/work/a", ".devkit/transient/work/c"]
    planned = _run("list", "-w", str(workspace), "--status", "planned")
    assert planned.output.strip() == "[UNIT: .devkit/transient/work/a status=planned workflow=- anchor=task.md]"
    several = json.loads(
        _run("list", "-w", str(workspace), "--status", "planned", "--status", "completed", "--format", "json").stdout
    )["units"]
    assert [row["unit"] for row in several] == [".devkit/transient/work/a", ".devkit/transient/work/b"]
    none = _run("list", "-w", str(workspace), "--status", "nope")
    assert none.exit_code == 0 and "[OK: no units dirs=" in none.output


# --- shared stages --------------------------------------------------------------


def test_shared_stage_problems() -> None:
    a = parse_definition(WORKFLOW)
    same = parse_definition(WORKFLOW.replace("id: direct-delivery", "id: bugfix"))
    assert compare_shared_stages([a, same]) == []
    different = parse_definition(
        WORKFLOW.replace("id: direct-delivery", "id: bugfix")
        .replace("exit: [envelope-review-passed]", "exit: [envelope-review-passed, ci-passed]")
        .replace("role: reviewer", "role: developer")
    )
    problems = compare_shared_stages([a, different])
    assert [str(p) for p in problems] == [
        "shared stage 'review' differs between direct-delivery and bugfix: exit",
        "shared stage 'review' differs between direct-delivery and bugfix: role",
    ]
    assert {p.code for p in problems} == {"SHARED_STAGE_MISMATCH"}


def test_validate_cli_reports_shared_stage_drift_only_for_the_whole_workspace(workspace: Path) -> None:
    other = workspace / ".devkit/workflows/bugfix.md"
    other.write_text(
        WORKFLOW.replace("id: direct-delivery", "id: bugfix").replace("skills: [wf-build]", "skills: [wf-fix]")
    )
    whole = _run("validate", "-w", str(workspace))
    assert whole.exit_code == 1
    assert "[INVALID: shared stage 'build-verify' differs between bugfix and direct-delivery: skills]" in whole.output
    single = _run("validate", "-w", str(workspace), str(other))
    assert single.exit_code == 0, single.output
    other.write_text(WORKFLOW.replace("id: direct-delivery", "id: bugfix"))
    assert _run("validate", "-w", str(workspace)).exit_code == 0


def test_validation_problems_and_load_errors_are_coded_entries(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    (workspace / ".devkit/roles").mkdir()
    (workspace / ".devkit/roles/other.md").write_text("# other\n")  # `reviewer` is not in the vocabulary
    (workspace / ".devkit/workflows/broken.md").write_text("---\nid: [\n---\n")
    result = _run("validate", "-w", str(workspace), "--format", "json")
    assert result.exit_code == 2  # a definition that cannot be loaded is a load problem, not a finding
    data = json.loads(result.stdout)
    [definition] = data["definitions"]
    assert {"code": "ROLE_UNKNOWN", "where": "review.role"} in [
        {k: p[k] for k in ("code", "where")} for p in definition["errors"]
    ]
    assert definition["ok"] is False and data["ok"] is False
    [load_error] = data["errors"]
    assert load_error["code"] == "WORKFLOW_DEFINITION_INVALID" and load_error["exit_code"] == 2
    assert load_error["advisory"]["target_files"][0].endswith("broken.md") and load_error["message"]
    text = _run("validate", "-w", str(workspace))
    assert "[INVALID: " in text.output and "review.role: unknown role 'reviewer'" in text.output

    shown = _run("show", "-w", str(workspace), "direct-delivery", "--format", "json")
    assert shown.exit_code == 1
    shown_data = json.loads(shown.stdout)
    assert shown_data["ok"] is False and any(p["code"] == "ROLE_UNKNOWN" for p in shown_data["errors"])
    assert (
        "[PROBLEM: review.role: unknown role 'reviewer'" in _run("show", "-w", str(workspace), "direct-delivery").output
    )
