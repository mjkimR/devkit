from __future__ import annotations

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
    schema_hash,
    validate_definition,
)
from devkit.workflow.definition.discovery import discover_definitions, managed_definition_paths
from testsupport.workflow import WORKFLOW, write_receipt

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


def test_schema_hash_ignores_title_and_body() -> None:
    a = parse_definition(WORKFLOW)
    b = parse_definition(WORKFLOW.replace('title: "Direct delivery"', 'title: "Other"') + "\nmore prose\n")
    c = parse_definition(WORKFLOW.replace("skills: [wf-intent]", "skills: [wf-start]"))
    assert schema_hash(a) == schema_hash(b)
    assert schema_hash(a) != schema_hash(c)
    assert schema_hash(a).startswith("sha256:")


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
