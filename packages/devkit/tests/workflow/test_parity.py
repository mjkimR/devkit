"""Role vocabulary, show --unit, list filters, plugin checks and shared-stage consistency."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit.advisory import ActionMode
from devkit.core.plugins import iter_plugin_files
from devkit.workflow import (
    BaseCheck,
    CheckClass,
    Options,
    Registry,
    WorkflowError,
    Workspace,
    compare_shared_stages,
    discover_roles,
    evaluate_definition,
    load_check_files,
    load_plugin_checks,
    parse_definition,
    validate_definition,
)
from devkit.workflow.cli import cli
from devkit.workflow.errors import CheckError
from testsupport.workflow import WORKFLOW, write_config, write_receipt, write_unit

CONFIG = """schema = 1
[workflow]
default = "direct-delivery"

[workflow.approvals]
direction = "auto"
"""

PLUGIN = """from devkit.workflow import BaseCheck, CheckContext, CheckResult


class HasWord(BaseCheck):
    name = "has-word"
    description = "the file contains the word"
    params = ("file", "word")

    def evaluate(self, ctx: CheckContext) -> CheckResult:
        text = ctx.read(ctx.args[0])
        if text is None:
            return ctx.failed(f"{ctx.args[0]} missing")
        return ctx.passed() if ctx.args[1] in text else ctx.failed(f"{ctx.args[1]!r} not in {ctx.args[0]}")


class Explodes(BaseCheck):
    name = "explodes"
    description = "always raises"

    def evaluate(self, ctx: CheckContext) -> CheckResult:
        raise RuntimeError("boom")
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
    assert skipped.exit_code == 0 and "[NOTICE: role check skipped: no installation receipt and no .devkit/roles]" in (
        skipped.output
    )
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


def test_show_unit_prints_binding_and_drift(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    assert _run("new", "-w", str(workspace), "login").exit_code == 0
    unit = ".devkit/transient/work/login"
    shown = _run("show", "-w", str(workspace), "--unit", unit)
    assert shown.exit_code == 0, shown.output
    assert "[WORKFLOW: direct-delivery" in shown.output
    assert "[BINDING: workflow=direct-delivery hash=sha256:" in shown.output and "drift=false]" in shown.output
    data = json.loads(_run("show", "-w", str(workspace), "--unit", unit, "--format", "json").stdout)
    assert data["binding"]["workflow"] == "direct-delivery" and data["binding"]["drift"] is False

    definition = workspace / ".devkit/workflows/direct-delivery.md"
    definition.write_text(definition.read_text().replace("skills: [wf-build]", "skills: [wf-implement]"))
    drifted = _run("show", "-w", str(workspace), "--unit", unit)
    assert drifted.exit_code == 0 and "drift=true]" in drifted.output

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
    assert none.exit_code == 0 and "[UNITS: none under" in none.output


# --- plugin checks --------------------------------------------------------------


def test_load_check_files_validates_and_reports(tmp_path: Path) -> None:
    good = tmp_path / "good.py"
    good.write_text(PLUGIN)
    bad_name = tmp_path / "bad_name.py"
    bad_name.write_text("from devkit.workflow import BaseCheck\n\nclass X(BaseCheck):\n    name = 'Bad Name'\n")
    broken = tmp_path / "broken.py"
    broken.write_text("raise RuntimeError('cannot import')\n")
    duplicate = tmp_path / "dup.py"
    duplicate.write_text(PLUGIN)
    (tmp_path / "_private.py").write_text("raise RuntimeError('never loaded')\n")
    loaded, errors = load_check_files(iter_plugin_files(tmp_path))  # the directory scan skips _private.py
    assert [c.name for c in loaded] == ["explodes", "has-word"] or [c.name for c in loaded] == ["has-word", "explodes"]
    assert len(errors) == 3 and {e.code for e in errors} == {"WORKFLOW_CHECK_LOAD_FAILED"}
    messages = [str(e) for e in errors]
    assert any("must match [a-z][a-z0-9-]*" in m for m in messages)
    assert any("cannot import" in m for m in messages)
    assert any("already defined" in m for m in messages)
    assert {e.target_files[0] for e in errors} == {
        bad_name.as_posix(),
        broken.as_posix(),
        good.as_posix(),
    }  # dup.py loads first


def test_registry_rejects_plugin_colliding_with_builtin() -> None:
    class Clash(BaseCheck):
        name = "file-exists"
        description = "clash"

    try:
        Registry.build("task.md", (), [Clash()])
    except CheckError as exc:
        assert "collides with a built-in" in str(exc)
    else:
        raise AssertionError("expected CheckError")


def test_plugin_checks_from_checks_dir_are_listed_validated_and_evaluated(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    checks_dir = workspace / ".devkit/workflow-checks"
    checks_dir.mkdir()
    (checks_dir / "words.py").write_text(PLUGIN)
    listed = _run("checks", "-w", str(workspace))
    assert "[CHECK: has-word(file word) class=plugin" in listed.output
    assert any(
        c["name"] == "explodes" and c["class"] == "plugin"
        for c in json.loads(_run("checks", "-w", str(workspace), "--format", "json").stdout)["checks"]
    )

    definition = workspace / ".devkit/workflows/direct-delivery.md"
    definition.write_text(
        definition.read_text().replace(
            "exit: [tasks-all-checked, lint-clean]", "exit: [has-word(tasks.md done), explodes]"
        )
    )
    assert _run("validate", "-w", str(workspace)).exit_code == 0
    unit = write_unit(workspace, ".devkit/transient/work/login")
    (unit / "tasks.md").write_text("- [x] pending\n")
    result = _run("next", "-w", str(workspace), "--unit", str(unit), "--no-lint")
    assert result.exit_code == 0, result.output
    assert "[STAGE: build-verify" in result.output
    assert "[CHECK: has-word(tasks.md done) class=plugin evaluated=true detail=\"'done' not in tasks.md\"]" in (
        result.output
    )
    assert '[CHECK: explodes class=plugin evaluated=true detail="check failed: boom"]' in result.output
    (unit / "tasks.md").write_text("- [x] done\n")
    data = json.loads(_run("next", "-w", str(workspace), "--unit", str(unit), "--no-lint", "--format", "json").stdout)
    assert [u["name"] for u in data["unmet"]] == ["explodes"]


def test_plugin_checks_from_receipt_and_load_failures(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    managed = workspace / ".devkit/managed/team/checks"
    managed.mkdir(parents=True)
    (managed / "words.py").write_text(PLUGIN)
    _receipt(workspace, [{"kind": "workflow-check", "id": "words", "paths": [".devkit/managed/team/checks/words.py"]}])
    (workspace / ".devkit/roles").mkdir()
    (workspace / ".devkit/roles/reviewer.md").write_text("# reviewer\n")
    assert "class=plugin" in _run("checks", "-w", str(workspace)).output

    (managed / "words.py").unlink()
    missing = _run("checks", "-w", str(workspace))
    assert missing.exit_code == 2 and "(WORKFLOW_CHECK_LOAD_FAILED)" in missing.stderr
    assert "synchronized check .devkit/managed/team/checks/words.py is missing" in missing.stderr
    assert "[ACTION]" in missing.stderr

    (managed / "words.py").write_text("raise RuntimeError('broken plugin')\n")
    broken = _run("validate", "-w", str(workspace))
    assert (
        broken.exit_code == 2 and "(WORKFLOW_CHECK_LOAD_FAILED)" in broken.stderr and "broken plugin" in broken.stderr
    )


def test_receipt_listed_plugin_checks_are_verified_like_rules_and_gates(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    (workspace / ".devkit/roles").mkdir()
    (workspace / ".devkit/roles/reviewer.md").write_text("# reviewer\n")
    managed = workspace / ".devkit/managed/team/checks/words.py"
    override = workspace / ".devkit/overrides/team/checks/extra.py"
    for path in (managed, override):
        path.parent.mkdir(parents=True)
    managed.write_text(PLUGIN)
    override.write_text(PLUGIN.replace("has-word", "extra-word").replace("explodes", "extra-explodes"))
    asset = {
        "kind": "workflow-check",
        "id": "words",
        "paths": [".devkit/managed/team/checks/words.py", ".devkit/overrides/team/checks/extra.py"],
    }
    write_receipt(workspace, [asset], hashed=(".devkit/managed/team/checks/words.py",))
    # A recorded file matching its hash and an override without a record both load.
    names = {c.name for c in Workspace(workspace).plugins()}
    assert {"has-word", "extra-word"} <= names

    managed.write_text(PLUGIN + "\n# edited by hand\n")
    with pytest.raises(WorkflowError) as info:
        Workspace(workspace).plugins()
    error = info.value
    assert error.code == "WORKFLOW_CHECK_LOAD_FAILED" and error.mode is ActionMode.MAINTENANCE
    assert "differs from the hash in the receipt" in error.render()
    assert error.fix is not None and "devkit sync" in error.fix and "devkit override create team:words" in error.fix
    assert error.target_files == (".devkit/managed/team/checks/words.py",)
    _, problems = load_plugin_checks(workspace, ".devkit/workflow-checks")
    assert [(p.code, p.target_files) for p in problems] == [
        ("WORKFLOW_CHECK_LOAD_FAILED", (".devkit/managed/team/checks/words.py",))
    ]
    cli = _run("checks", "-w", str(workspace))
    assert cli.exit_code == 2 and "(WORKFLOW_CHECK_LOAD_FAILED)" in cli.stderr


def test_receipt_listed_plugin_checks_load_whatever_their_name(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    private = workspace / ".devkit/managed/team/checks/_words.py"
    private.parent.mkdir(parents=True)
    private.write_text(PLUGIN)
    write_receipt(
        workspace,
        [{"kind": "workflow-check", "id": "words", "entrypoints": [".devkit/managed/team/checks/_words.py"]}],
        hashed=(".devkit/managed/team/checks/_words.py",),
    )
    loaded, problems = load_plugin_checks(workspace, ".devkit/workflow-checks")
    assert problems == [] and {c.name for c in loaded} == {"has-word", "explodes"}


def test_definition_declared_check_cannot_shadow_plugin(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    checks_dir = workspace / ".devkit/workflow-checks"
    checks_dir.mkdir()
    (checks_dir / "words.py").write_text(PLUGIN)
    definition = workspace / ".devkit/workflows/direct-delivery.md"
    definition.write_text(
        definition.read_text().replace("{ name: ci-passed, class: runner", "{ name: has-word, class: runner")
    )
    result = _run("validate", "-w", str(workspace))
    assert result.exit_code == 1 and "collides with a built-in or plugin check" in result.output


def test_plugin_result_class_is_normalized() -> None:
    class Weird(BaseCheck):
        name = "weird"
        description = "returns a foreign class"

        def evaluate(self, ctx):  # type: ignore[no-untyped-def]
            from devkit.workflow import CheckResult

            return CheckResult("other-name", CheckClass.HUMAN, True, False, "ok")

    doc = parse_definition(WORKFLOW.replace("exit: [tasks-all-checked, lint-clean]", "exit: [weird]"))
    assert validate_definition(doc, "task.md", plugins=[Weird()]) == []


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
