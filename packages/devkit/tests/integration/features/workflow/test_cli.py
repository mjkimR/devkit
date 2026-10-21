from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit.advisory import AdvisoryError
from devkit_agt.features.workflow.cli import cli
from testsupport.workflow import SIMPLE_UNIT, WORKFLOW, simple_workspace, write_config, write_receipt

CONFIG = """schema = 1
[workflow]
default = "direct-delivery"

[workflow.approvals]
direction = "auto"
"""


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def test_help() -> None:
    result = _run("--help")
    assert result.exit_code == 0 and "workflow engine" in result.output


def test_checks_text_and_json(tmp_path: Path) -> None:
    text = _run("checks", "-w", str(tmp_path))
    assert text.exit_code == 0 and "[CHECK: anchor-exists class=disk alias=file-exists(task.md)" in text.output
    data = json.loads(_run("checks", "-w", str(tmp_path), "--format", "json").stdout)["checks"]
    assert {c["name"] for c in data} >= {"file-exists", "lint-clean", "envelope-review-passed"}


def test_validate_and_show(workspace: Path) -> None:
    result = _run("validate", "-w", str(workspace))
    assert result.exit_code == 0 and "[VALID:" in result.output and "id=direct-delivery" in result.output

    (workspace / ".devkit/workflows/broken.md").write_text(
        WORKFLOW.replace("id: direct-delivery", "id: broken").replace("anchor-exists", "nope")
    )
    result = _run("validate", "-w", str(workspace))
    assert result.exit_code == 1 and "[INVALID:" in result.output and "unregistered check 'nope'" in result.output

    show = _run("show", "-w", str(workspace), "direct-delivery")
    assert (
        show.exit_code == 0
        and "[WORKFLOW: direct-delivery" in show.output
        and "[GATE: direction policy=ask]" in show.output
    )
    data = json.loads(_run("show", "-w", str(workspace), "direct-delivery", "--format", "json").stdout)
    assert "hash" not in data and data["approvals"] == {"direction": "ask", "integration": "ask"}
    missing = _run("show", "-w", str(workspace), "missing")
    assert missing.exit_code == 2 and "(WORKFLOW_NOT_FOUND)" in missing.stderr


def test_validate_with_no_definitions(tmp_path: Path) -> None:
    result = _run("validate", "-w", str(tmp_path))
    assert result.exit_code == 0 and "no definitions" in result.output


def test_new_requires_a_workflow_selection(workspace: Path) -> None:
    result = _run("new", "-w", str(workspace), "login")
    assert result.exit_code == 2 and "(WORKFLOW_NOT_SELECTED)" in result.stderr and "[ACTION]" in result.stderr


def test_end_to_end_new_next_bind_envelope_list(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    created = _run("new", "-w", str(workspace), "login", "--date", "2026-10-12")
    assert created.exit_code == 0, created.output
    assert created.output.strip() == "[UNIT: .devkit/transient/work/login workflow=direct-delivery anchor=task.md]"
    unit = workspace / ".devkit/transient/work/login"
    anchor = (unit / "task.md").read_text()
    assert "workflow: direct-delivery" in anchor and "workflow_hash" not in anchor and "created: 2026-10-12" in anchor
    assert (unit / "envelopes").is_dir()
    dup = _run("new", "-w", str(workspace), "login")
    assert dup.exit_code == 2 and "(UNIT_EXISTS)" in dup.stderr

    nxt = _run("next", "-w", str(workspace), "--unit", ".devkit/transient/work/login", "--no-lint")
    assert nxt.exit_code == 0, nxt.output
    assert "[WORKFLOW: direct-delivery unit=.devkit/transient/work/login status=planned bound=yes]" in nxt.output
    assert "[DONE: intent]" in nxt.output and "[STAGE: build-verify" in nxt.output
    assert "[NEXT_SKILL: wf-build]" in nxt.output

    listed = json.loads(_run("list", "-w", str(workspace), "--format", "json").stdout)["units"]
    assert listed[0]["unit"] == ".devkit/transient/work/login" and listed[0]["workflow"] == "direct-delivery"

    env = _run("envelope", "review", "-w", str(workspace), "--unit", str(unit), "--stage", "review")
    assert (
        env.exit_code == 0
        and env.output.strip()
        == "[ENVELOPE: .devkit/transient/work/login/envelopes/review-01.yaml kind=review seq=01 status=needs_input open_findings=0]"
    )
    env = _run(
        "envelope",
        "review",
        "-w",
        str(workspace),
        "--unit",
        str(unit),
    )
    assert "seq=02" in env.output
    bad_kind = _run("envelope", "new", "-w", str(workspace), "--unit", str(unit), "--kind", "Bad")
    assert bad_kind.exit_code == 2 and "(ENVELOPE_KIND_INVALID)" in bad_kind.stderr
    for kind in ("worker", "answer", "resolution", "review", "reverify"):  # each has its own command
        own = _run("envelope", "new", "-w", str(workspace), "--unit", str(unit), "--kind", kind)
        assert own.exit_code == 2 and "(ENVELOPE_FLAG_INVALID)" in own.stderr
        assert f"devkit workflow envelope {kind}" in own.stderr

    as_json = json.loads(
        _run("next", "-w", str(workspace), "--unit", str(unit), "--no-lint", "--format", "json").stdout
    )
    assert as_json["stage"]["id"] == "build-verify" and as_json["bound"] is True and as_json["complete"] is False


def test_next_applies_definition_changes_without_rebinding(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    _run("new", "-w", str(workspace), "login")
    unit = ".devkit/transient/work/login"
    anchor = workspace / unit / "task.md"
    original = anchor.read_bytes()
    definition = workspace / ".devkit/workflows/direct-delivery.md"
    definition.write_text(definition.read_text().replace("skills: [wf-build]", "skills: [wf-scope]"))
    result = _run("next", "-w", str(workspace), "--unit", unit, "--no-lint")
    assert result.exit_code == 0, result.stderr
    assert "wf-scope" in result.stdout
    data = json.loads(_run("next", "-w", str(workspace), "--unit", unit, "--no-lint", "--format", "json").stdout)
    assert data["bound"] is True and data["next_skill"] == "wf-scope"
    assert "drift" not in data
    assert anchor.read_bytes() == original


def test_given_validation_and_gate_flow(workspace: Path) -> None:
    write_config(workspace, 'schema = 1\n[workflow]\ndefault = "direct-delivery"\n')
    _run("new", "-w", str(workspace), "login")
    unit = ".devkit/transient/work/login"
    waiting = _run("next", "-w", str(workspace), "--unit", unit, "--no-lint")
    assert (
        "[STAGE: intent human_gate=direction" in waiting.output and "[WAITING: human gate:direction]" in waiting.output
    )
    passed = _run("next", "-w", str(workspace), "--unit", unit, "--no-lint", "--given", "direction")
    assert "[DONE: intent]" in passed.output
    bad = _run("next", "-w", str(workspace), "--unit", unit, "--no-lint", "--given", "anchor-exists")
    assert bad.exit_code == 2 and "(GIVEN_INVALID)" in bad.stderr


def test_next_unknown_unit_is_unit_not_found(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    result = _run("next", "-w", str(workspace), "--unit", "nowhere")
    assert result.exit_code == 2 and "(UNIT_NOT_FOUND) no anchor file (task.md) found in nowhere" in result.stderr


def test_specrig_style_layout_from_config(workspace: Path) -> None:
    write_config(
        workspace,
        """[workflow]
work_dir = "specs"
unit_path = "{date:%Y-%m}/{date:%Y%m%d}-{slug}"
anchor = "spec.md"
default = "direct-delivery"
""",
    )
    created = _run("new", "-w", str(workspace), "login", "--date", "2026-10-12")
    assert created.output.strip() == "[UNIT: specs/2026-10/20261012-login workflow=direct-delivery anchor=spec.md]"
    listed = _run("list", "-w", str(workspace))
    assert (
        "[UNIT: specs/2026-10/20261012-login status=planned workflow=direct-delivery anchor=spec.md]" in listed.output
    )


def test_lint_check_runs_rule_engine(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    _run("new", "-w", str(workspace), "login")
    unit = workspace / ".devkit/transient/work/login"
    (unit / "tasks.md").write_text("- [x] done\n\n[broken](missing.md)\n")
    result = _run("next", "-w", str(workspace), "--unit", str(unit))
    assert result.exit_code == 0, result.output
    assert "[STAGE: build-verify" in result.output and "RULE-markdown-link" in result.output
    (unit / "tasks.md").write_text("- [x] done\n")
    result = _run("next", "-w", str(workspace), "--unit", str(unit))
    assert "[STAGE: review" in result.output


def test_lint_check_honors_rules_exclude(workspace: Path) -> None:
    # Same policy as `devkit rules check`: files under [rules] exclude are not linted.
    write_config(workspace, CONFIG + '\n[rules]\nexclude = [".devkit/transient/work/**"]\n')
    _run("new", "-w", str(workspace), "login")
    unit = workspace / ".devkit/transient/work/login"
    (unit / "tasks.md").write_text("- [x] done\n\n[broken](missing.md)\n")
    result = _run("next", "-w", str(workspace), "--unit", str(unit))
    assert result.exit_code == 0, result.output
    assert "[STAGE: review" in result.output and "RULE-markdown-link" not in result.output


def test_lint_function_reports_a_malformed_receipt(tmp_path: Path) -> None:
    from devkit_agt.features.workflow.usecases.lint import lint_with_rules

    (tmp_path / "a.md").write_text("fine\n")
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/installation.json").write_text("{not json")
    with pytest.raises(AdvisoryError, match="installation"):
        lint_with_rules(tmp_path, ["a.md"])
    assert lint_with_rules(tmp_path, []) == []


def test_invalid_config_is_a_clean_error(tmp_path: Path) -> None:
    write_config(tmp_path, '[workflow.approvals]\nx = "maybe"\n')
    result = _run("checks", "-w", str(tmp_path))
    assert result.exit_code == 2 and "(WORKFLOW_CONFIG_INVALID)" in result.stderr and "not one of" in result.stderr
    assert "[TARGET] .devkit/config.toml" in result.stderr


def test_invalid_bound_workflow_reports_problems_as_details(workspace: Path) -> None:
    write_config(workspace, CONFIG)
    _run("new", "-w", str(workspace), "login")
    definition = workspace / ".devkit/workflows/direct-delivery.md"
    definition.write_text(definition.read_text().replace("anchor-exists", "nope"))
    result = _run("next", "-w", str(workspace), "--unit", ".devkit/transient/work/login", "--no-lint")
    assert result.exit_code == 2 and "(WORKFLOW_INVALID)" in result.stderr
    assert "[DETAIL] intent.exit: unregistered check 'nope'" in result.stderr
    assert "[TARGET] .devkit/workflows/direct-delivery.md" in result.stderr


def test_cli_uses_synchronized_workflow_from_receipt(tmp_path: Path) -> None:
    managed = tmp_path / ".devkit/managed/team/flows"
    managed.mkdir(parents=True)
    (managed / "delivery.md").write_text(WORKFLOW)
    write_receipt(
        tmp_path,
        [
            {"kind": "workflow", "id": "delivery", "entrypoints": [".devkit/managed/team/flows/delivery.md"]},
            {"kind": "subagent", "id": "reviewer", "paths": [".claude/agents/reviewer.md"]},
        ],
    )
    write_config(tmp_path, CONFIG)
    validated = _run("validate", "-w", str(tmp_path))
    assert validated.exit_code == 0 and ".devkit/managed/team/flows/delivery.md id=direct-delivery" in validated.output
    assert "[NOTICE: role check skipped" not in validated.output
    created = _run("new", "-w", str(tmp_path), "login")
    assert created.exit_code == 0, created.output
    nxt = _run("next", "-w", str(tmp_path), "--unit", ".devkit/transient/work/login", "--no-lint")
    assert nxt.exit_code == 0 and "[WORKFLOW: direct-delivery" in nxt.output


def test_requests_reports_a_lint_error_like_next(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import devkit_agt.features.rules

    def broken(*_: object, **__: object) -> None:
        raise RuntimeError("rule exploded")

    root = simple_workspace(tmp_path, check="lint-clean")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    monkeypatch.setattr(devkit_agt.features.rules, "run_project_rules", broken)
    result = _run("requests", "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json")
    assert result.exit_code == 2 and result.stderr == ""
    document = json.loads(result.stdout)
    assert document["requests"] == [] and [e["code"] for e in document["errors"]] == ["UNEXPECTED_ERROR"]
    text = _run("requests", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert text.stdout.splitlines() == ["[REQUESTS: none]", '[LINT_ERROR: "RuntimeError: rule exploded"]']
    assert text.exit_code == 2 and "(UNEXPECTED_ERROR) RuntimeError: rule exploded" in text.stderr

    clean = json.loads(_run("requests", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint", "--format", "json").stdout)
    assert clean == {"requests": [], "errors": []}
