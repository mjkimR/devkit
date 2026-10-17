from __future__ import annotations

import json
from pathlib import Path

import pytest
from devkit.core.errors import ReceiptError
from devkit.core.receipt import load_receipt
from devkit.rules import count_tasks
from devkit.workflow import (
    CheckClass,
    CheckError,
    DefinitionError,
    Registry,
    WorkflowNotFoundError,
    load_definition,
    parse_check,
    parse_definition,
    resolve_definition,
    validate_definition,
)
from devkit.workflow.definition.discovery import discover_definitions, managed_definition_paths
from devkit.workflow.definition.validation import definition_warnings
from testsupport.workflow import SIMPLE_UNIT, WORKFLOW, run_cli, simple_workspace, write_config, write_receipt

# --- check syntax and registry ------------------------------------------------


def test_parse_check_forms() -> None:
    assert parse_check("anchor-exists").args == ()
    inv = parse_check("frontmatter(task.md status planned)")
    assert (inv.name, inv.args) == ("frontmatter", ("task.md", "status", "planned"))
    assert str(inv) == "frontmatter(task.md status planned)"


@pytest.mark.parametrize("text", ["", "a b", "x(", "x()", "x(a(b))", "(a)", "x )"])
def test_parse_check_malformed(text: str) -> None:
    with pytest.raises(CheckError, match="malformed"):
        parse_check(text)


def test_registry_resolves_aliases_against_anchor() -> None:
    reg = Registry.build("spec.md")
    inv, check = reg.resolve_name("anchor-status-completed")
    assert (inv.name, inv.args, check.class_) == ("frontmatter", ("spec.md", "status", "completed"), CheckClass.DISK)
    with pytest.raises(CheckError, match="takes no arguments"):
        reg.resolve_name("anchor-exists(spec.md)")
    with pytest.raises(CheckError, match="expects 3 argument"):
        reg.resolve_name("frontmatter(spec.md status)")
    with pytest.raises(CheckError, match="unregistered"):
        reg.resolve_name("nope")


def test_registry_declared_checks_must_be_runner_or_human() -> None:
    from devkit.workflow import Check

    reg = Registry.build("task.md", (Check("ci-passed", CheckClass.RUNNER, "ci"),))
    assert reg.lookup("ci-passed") is not None
    with pytest.raises(CheckError, match="runner or human"):
        Registry.build("task.md", (Check("x", CheckClass.DISK, ""),))
    with pytest.raises(CheckError, match="collides"):
        Registry.build("task.md", (Check("file-exists", CheckClass.HUMAN, ""),))
    with pytest.raises(CheckError, match="duplicate declared check 'ci-passed'"):
        Registry.build("task.md", (Check("ci-passed", CheckClass.RUNNER, ""), Check("ci-passed", CheckClass.HUMAN, "")))


def test_count_tasks() -> None:
    text = "- [ ] a\n- [x] b\n* [X] c\n  - [ ] nested\n- not a task\n"
    assert count_tasks(text) == (2, 4)
    # Shared with devkit.rules: frontmatter and fenced examples are not tasks.
    fenced = "---\nstatus: draft\n- [ ] in frontmatter\n---\n```\n- [ ] in a fence\n```\n- [x] real\n"
    assert count_tasks(fenced) == (1, 1)


# --- definitions --------------------------------------------------------------


def test_parse_normalizes_human_gate_and_defaults() -> None:
    doc = parse_definition(WORKFLOW)
    assert [s.id for s in doc.stages] == ["intent", "build-verify", "review", "integrate"]
    assert doc.stage("intent").gate == "direction"  # type: ignore[union-attr]
    assert doc.stage("build-verify").gate is None  # type: ignore[union-attr]
    assert doc.declared_checks[0].name == "ci-passed"
    assert validate_definition(doc, "task.md") == []


def test_human_gate_true_names_gate_after_stage() -> None:
    doc = parse_definition(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: g3\n    human_gate: true\n    exit: [anchor-exists]\n---\n"
    )
    assert doc.stages[0].gate == "g3"


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("no frontmatter", "no frontmatter"),
        ("---\nid: [bad\n---\n", "invalid YAML"),
        ("---\nstages: []\n---\n", "id: expected"),
        ("---\nid: w\nstages: []\n---\n", "stages: expected a nonempty list"),
        ("---\nid: w\nstages:\n  - name: x\n---\n", "id: expected a nonempty string"),
        ("---\nid: w\nstages:\n  - id: a\n    human_gate: 3\n---\n", "human_gate"),
        ("---\nid: w\nstages:\n  - id: a\n    exit: x\n---\n", "list of strings"),
        ("---\nid: w\nchecks:\n  - { name: c, class: disk }\nstages:\n  - id: a\n---\n", "runner or human"),
    ],
)
def test_parse_structural_errors(text: str, match: str) -> None:
    with pytest.raises(DefinitionError, match=match):
        parse_definition(text)


def test_validate_reports_every_problem() -> None:
    text = """---
id: Bad_ID
schema_version: 2
stages:
  - id: a
    isolation: sometimes
    exit: [nope, frontmatter(x)]
    bogus: 1
    returns:
      - { to: zzz, when: "" }
      - { when: reason }
  - id: a
---
"""
    problems = {str(p) for p in validate_definition(parse_definition(text), "task.md")}
    expected_fragments = [
        "id: 'Bad_ID' must match",
        "schema_version: unsupported schema_version 2",
        "a.isolation: 'sometimes' not in",
        "a.exit: unregistered check 'nope'",
        "a.exit: check 'frontmatter' expects 3 argument",
        "a.bogus: unknown stage key",
        "a.returns[0].to: unknown stage 'zzz'",
        "a.returns[0].when: missing reason",
        "a.returns[1].to: missing target stage",
        "a.id: duplicate stage id",
    ]
    for fragment in expected_fragments:
        assert any(fragment in p for p in problems), fragment


def test_validate_duplicate_declared_check_keeps_the_others() -> None:
    text = """---
id: dup
schema_version: 1
checks:
  - { name: ci-passed, class: runner, description: ci }
  - { name: ci-passed, class: runner, description: ci again }
  - { name: po-ok, class: human, description: po }
  - { name: file-exists, class: human, description: clash }
stages:
  - id: build
    exit: [ci-passed, po-ok]
---
"""
    problems = [str(p) for p in validate_definition(parse_definition(text), "task.md")]
    assert problems == [
        "checks: duplicate declared check 'ci-passed'",
        "checks: declared check 'file-exists' collides with a built-in check",
    ]


def test_validate_rejects_runner_and_human_checks_in_handoff_when() -> None:
    text = """---
id: a
schema_version: 1
checks:
  - { name: ci-passed, class: runner, description: ci }
  - { name: po-ok, class: human, description: po }
stages:
  - id: build
    exit: [anchor-exists]
next:
  - { workflow: b, when: [ci-passed] }
  - { workflow: c, when: [po-ok, file-exists(spec.md)] }
---
"""
    problems = validate_definition(parse_definition(text), "task.md")
    assert [(p.code, str(p)) for p in problems] == [
        (
            "WORKFLOW_CHECK_INVALID",
            "next[0].when: runner check 'ci-passed' cannot decide a handoff; `when` takes checks the engine evaluates",
        ),
        (
            "WORKFLOW_CHECK_INVALID",
            "next[1].when: human check 'po-ok' cannot decide a handoff; `when` takes checks the engine evaluates",
        ),
    ]


def test_find_and_resolve(workspace: Path) -> None:
    defs = workspace / ".devkit" / "workflows"
    assert resolve_definition(defs, "direct-delivery").id == "direct-delivery"
    assert resolve_definition(defs, str(defs / "direct-delivery.md")).id == "direct-delivery"
    with pytest.raises(WorkflowNotFoundError, match="no workflow with id"):
        resolve_definition(defs, "missing")
    with pytest.raises(WorkflowNotFoundError, match="no definition file"):
        resolve_definition(defs, "missing.md")
    (defs / "dup.md").write_text(WORKFLOW)
    with pytest.raises(DefinitionError, match="more than once") as dup:
        resolve_definition(defs, "direct-delivery")
    assert dup.value.code == "WORKFLOW_DEFINITION_INVALID"


def test_load_reports_path_in_errors(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("---\nstages: []\n---\n")
    with pytest.raises(DefinitionError, match=r"bad\.md"):
        load_definition(bad)


def test_managed_definition_paths_from_receipt(tmp_path: Path) -> None:
    assert managed_definition_paths(tmp_path, None) == ([], [])
    write_receipt(
        tmp_path,
        [
            {"kind": "workflow", "id": "a", "entrypoints": [".devkit/managed/team/flows/a.md"]},
            {"kind": "playbook", "id": "p", "entrypoints": [".devkit/managed/team/p.md"]},
            {"kind": "workflow", "id": "b", "paths": [".devkit/managed/team/b.md", ".devkit/managed/team/b.png"]},
        ],
    )
    for rel in (".devkit/managed/team/flows/a.md", ".devkit/managed/team/b.md"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(WORKFLOW)
    assert managed_definition_paths(tmp_path, load_receipt(tmp_path)) == (
        sorted([tmp_path / ".devkit/managed/team/flows/a.md", tmp_path / ".devkit/managed/team/b.md"]),
        [],
    )


def test_malformed_receipt_is_an_error_not_an_empty_source(workspace: Path) -> None:
    (workspace / ".devkit/installation.json").write_text("not json")
    with pytest.raises(ReceiptError):
        discover_definitions(workspace, workspace / ".devkit/workflows")


def test_discover_merges_receipt_and_local_with_local_shadowing(workspace: Path) -> None:
    managed = workspace / ".devkit/managed/team/flows"
    managed.mkdir(parents=True)
    (managed / "delivery.md").write_text(WORKFLOW.replace('title: "Direct delivery"', 'title: "Managed"'))
    (managed / "bugfix.md").write_text(WORKFLOW.replace("id: direct-delivery", "id: bugfix"))
    write_receipt(
        workspace,
        [
            {"kind": "workflow", "id": "delivery", "entrypoints": [".devkit/managed/team/flows/delivery.md"]},
            {"kind": "workflow", "id": "bugfix", "entrypoints": [".devkit/managed/team/flows/bugfix.md"]},
            {"kind": "workflow", "id": "gone", "entrypoints": [".devkit/managed/team/flows/missing.md"]},
        ],
    )
    defs = workspace / ".devkit/workflows"
    docs, errors = discover_definitions(workspace, defs)
    # A recorded definition missing from disk is reported, not silently skipped (R9).
    assert [(str(e), e.code, e.target_files, e.fix, e.mode.value) for e in errors] == [
        (
            "synchronized workflow .devkit/managed/team/flows/missing.md is missing from the working tree",
            "WORKFLOW_ASSET_MISSING",
            (".devkit/managed/team/flows/missing.md",),
            "devkit sync",
            "AUTO",
        )
    ]
    by_id = {d.id: d for d in docs}
    assert set(by_id) == {"direct-delivery", "bugfix"}
    assert by_id["direct-delivery"].title == "Direct delivery"  # local shadows managed
    assert resolve_definition(defs, "bugfix", workspace).path == managed / "bugfix.md"
    with pytest.raises(WorkflowNotFoundError, match="installation receipt"):
        resolve_definition(defs, "nope", workspace)


# --- optional stages --------------------------------------------------------------------------

OPTIONAL = """---
id: w
schema_version: 1
checks:
  - {{ name: signed-off, class: human, description: "a person signed off" }}
  - {{ name: ci, class: runner, description: "CI is green" }}
stages:
  - id: spike
    optional: true
    human_gate: {gate}
    exit: [{exit}]
  - id: build
    exit: [anchor-exists]
---
"""


def test_an_optional_stage_with_an_approval_is_valid_with_a_warning() -> None:
    gated = parse_definition(OPTIONAL.format(gate="spike-ok", exit="anchor-exists"))
    assert validate_definition(gated, "task.md") == []
    [warning] = definition_warnings(gated, "task.md")
    assert (warning.code, warning.level.value, warning.where) == (
        "WORKFLOW_OPTIONAL_STAGE_UNASKED",
        "WARNING",
        "spike.human_gate",
    )
    assert "approvals.spike-ok=auto, --given spike-ok or a decision record written by a host" in warning.message
    checked = parse_definition(OPTIONAL.format(gate="false", exit="signed-off"))
    assert validate_definition(checked, "task.md") == []
    [warning] = definition_warnings(checked, "task.md")
    assert warning.where == "spike.exit" and "human check 'signed-off'" in warning.message
    # Checks the engine evaluates, or a runner passes with --given, are no concern.
    for exit_ in ("anchor-exists", "ci"):
        assert definition_warnings(parse_definition(OPTIONAL.format(gate="false", exit=exit_)), "task.md") == []


def test_validate_warns_about_an_optional_gated_stage(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    (root / ".devkit/workflows/w.md").write_text(OPTIONAL.format(gate="spike-ok", exit="anchor-exists"))
    result = run_cli("validate", "-w", str(root), "--format", "json")
    assert result.exit_code == 0, result.output
    document = json.loads(result.stdout)
    assert document["ok"] is True and document["definitions"][0]["errors"] == []
    assert [n["code"] for n in document["notices"]] == ["WORKFLOW_OPTIONAL_STAGE_UNASKED", "WORKFLOW_ROLES_UNCHECKED"]
    text = run_cli("validate", "-w", str(root))
    assert text.exit_code == 0 and text.stdout.startswith("[VALID: .devkit/workflows/w.md id=w]")
    assert "[WARN]" in text.stderr and "(WORKFLOW_OPTIONAL_STAGE_UNASKED)" in text.stderr
    assert run_cli("validate", "-w", str(root), "--strict").exit_code == 1


def test_a_unit_of_an_optional_gated_stage_can_satisfy_it(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    (root / ".devkit/workflows/w.md").write_text(OPTIONAL.format(gate="spike-ok", exit="anchor-exists"))
    write_config(root, '[workflow]\ndefault = "w"\n[workflow.approvals]\nspike-ok = "auto"\n')
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    result = json.loads(run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint", "--format", "json").stdout)
    assert result["stage"] is None and result["done"] == ["spike", "build"]
