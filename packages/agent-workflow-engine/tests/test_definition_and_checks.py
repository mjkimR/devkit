from __future__ import annotations

from pathlib import Path

import pytest
from agent_workflow_engine import (
    CheckClass,
    CheckError,
    DefinitionError,
    Registry,
    load,
    parse,
    parse_check,
    resolve,
    schema_hash,
    validate,
)
from agent_workflow_engine.checks import count_tasks
from agent_workflow_engine.definition import find
from conftest import WORKFLOW

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
    from agent_workflow_engine import Check

    reg = Registry.build("task.md", (Check("ci-passed", CheckClass.RUNNER, "ci"),))
    assert reg.lookup("ci-passed") is not None
    with pytest.raises(CheckError, match="runner or human"):
        Registry.build("task.md", (Check("x", CheckClass.DISK, ""),))
    with pytest.raises(CheckError, match="collides"):
        Registry.build("task.md", (Check("file-exists", CheckClass.HUMAN, ""),))


def test_count_tasks() -> None:
    text = "- [ ] a\n- [x] b\n* [X] c\n  - [ ] nested\n- not a task\n"
    assert count_tasks(text) == (2, 4)


# --- definitions --------------------------------------------------------------


def test_parse_normalizes_human_gate_and_defaults() -> None:
    doc = parse(WORKFLOW)
    assert [s.id for s in doc.stages] == ["intent", "build-verify", "review", "integrate"]
    assert doc.stage("intent").gate == "direction"  # type: ignore[union-attr]
    assert doc.stage("build-verify").gate is None  # type: ignore[union-attr]
    assert doc.declared_checks[0].name == "ci-passed"
    assert validate(doc, "task.md") == []


def test_human_gate_true_names_gate_after_stage() -> None:
    doc = parse(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: g3\n    human_gate: true\n    exit: [anchor-exists]\n---\n"
    )
    assert doc.stages[0].gate == "g3"


def test_schema_hash_ignores_title_and_body() -> None:
    a = parse(WORKFLOW)
    b = parse(WORKFLOW.replace('title: "Direct delivery"', 'title: "Other"') + "\nmore prose\n")
    c = parse(WORKFLOW.replace("skills: [wf-intent]", "skills: [wf-start]"))
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
        parse(text)


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
    problems = {str(p) for p in validate(parse(text), "task.md")}
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
    assert find(defs, "direct-delivery").id == "direct-delivery"
    assert resolve(defs, str(defs / "direct-delivery.md")).id == "direct-delivery"
    with pytest.raises(DefinitionError, match="no workflow with id"):
        find(defs, "missing")
    (defs / "dup.md").write_text(WORKFLOW)
    with pytest.raises(DefinitionError, match="more than once"):
        find(defs, "direct-delivery")


def test_load_reports_path_in_errors(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("---\nstages: []\n---\n")
    with pytest.raises(DefinitionError, match=r"bad\.md"):
        load(bad)
