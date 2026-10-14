"""Whole, uniquely numbered record files, exclusive unit creation, optional stages without approvals
and envelopes scoped to the workflow segment they were written in."""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import devkit.workflow.unit.records as records
import pytest
import yaml
from click.testing import CliRunner, Result
from devkit.workflow import (
    Binding,
    HistoryEntry,
    Options,
    UnitDirNotEmptyError,
    UnitExistsError,
    Workspace,
    create_unit,
    evaluate_definition,
    load_decisions,
    load_envelopes,
    parse_definition,
    validate_definition,
    write_binding,
)
from devkit.workflow.cli import cli
from devkit.workflow.unit.decisions import new_decision, write_decision
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


def _leftovers(directory: Path) -> list[str]:
    return sorted(p.name for p in directory.iterdir() if records.is_temporary(p.name))


# --- numbered records ---------------------------------------------------------------------------


def test_a_sequence_is_unique_across_requests(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)
    first = write_decision(unit, new_decision(stale, "gate:a", "accept", workflow="w", stage="s"))
    # A concurrent writer computed the same next sequence for another request.
    second = write_decision(unit, new_decision(stale, "return:s", "accept", workflow="w"))
    assert (first.seq, second.seq) == (1, 2)
    assert second.file == "decisions/02-return-s.yaml"
    assert [r.seq for r in load_decisions(unit).records] == [1, 2]


def test_a_sequence_is_never_below_a_taken_one(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)
    write_record(unit, "05-gate-a.yaml", request="gate:a", kind="approve", action="accept", workflow="w", stage="s")
    # Sequence 1 is free, but a record written now must order after record 5.
    assert write_decision(unit, new_decision(stale, "gate:b", "accept", workflow="w", stage="s")).seq == 6


def test_concurrent_writers_get_distinct_sequences(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)

    def write(i: int) -> int:
        return write_decision(unit, new_decision(stale, f"gate:g{i}", "accept", workflow="w", stage="s")).seq

    with ThreadPoolExecutor(max_workers=8) as pool:
        seqs = list(pool.map(write, range(24)))
    assert sorted(seqs) == list(range(1, 25))
    assert len(load_decisions(unit).records) == 24 and _leftovers(unit / "decisions") == []


def test_an_interrupted_write_leaves_no_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    unit = write_unit(tmp_path, "u")

    def interrupted(*_: object) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(records.os, "link", interrupted)
    with pytest.raises(KeyboardInterrupt):
        write_decision(unit, new_decision(load_decisions(unit), "gate:a", "accept", workflow="w", stage="s"))
    assert list((unit / "decisions").iterdir()) == []
    monkeypatch.undo()
    assert (
        write_decision(unit, new_decision(load_decisions(unit), "gate:a", "accept", workflow="w", stage="s")).seq == 1
    )


def test_a_concurrent_return_voids_an_approval_given_from_the_same_state(tmp_path: Path) -> None:
    doc = parse_definition(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: s\n    human_gate: g\n    exit: [anchor-exists]\n---\n"
    )
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)
    write_decision(unit, new_decision(stale, "gate:g", "accept", workflow="w", stage="s"))
    write_decision(unit, new_decision(stale, "return:s", "accept", workflow="w"))
    res = evaluate_definition(doc, Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md", skip_lint=True))
    assert res.stage is not None and [u.name for u in res.unmet] == ["gate:g"]


def test_a_failed_explicit_handoff_leaves_no_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    defs = tmp_path / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "a.md").write_text(SIMPLE.format(id="a", check="anchor-exists")[:-4] + "next:\n  - { workflow: b }\n---\n")
    (defs / "b.md").write_text(SIMPLE.format(id="b", check="anchor-exists"))
    write_config(tmp_path, '[workflow]\ndefault = "a"\n')
    assert _run("new", "-w", str(tmp_path), "u").exit_code == 0
    anchor = (tmp_path / UNIT / "task.md").read_text()

    def broken(*_: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(records.os, "link", broken)
    result = _run("handoff", "-w", str(tmp_path), "--unit", UNIT, "--workflow", "b", "--no-lint")
    assert result.exit_code != 0
    assert (tmp_path / UNIT / "task.md").read_text() == anchor
    assert list((tmp_path / UNIT / "decisions").iterdir()) == []


# --- creating a unit ----------------------------------------------------------------------------


def test_new_refuses_a_non_empty_directory_without_an_anchor(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    leftover = root / UNIT / "decisions"
    leftover.mkdir(parents=True)
    write_record(
        root / UNIT, "01-gate-g.yaml", request="gate:g", kind="approve", action="accept", workflow="w", stage="s"
    )
    with pytest.raises(UnitDirNotEmptyError) as raised:
        create_unit(Workspace(root), "u")
    assert raised.value.code == "UNIT_DIR_NOT_EMPTY"
    assert not (root / UNIT / "task.md").exists()
    result = _run("new", "-w", str(root), "u")
    assert result.exit_code == 2 and "(UNIT_DIR_NOT_EMPTY)" in result.stderr and "[FIX]" in result.stderr


def test_new_uses_an_empty_existing_directory(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    (root / UNIT).mkdir(parents=True)
    unit = create_unit(Workspace(root), "u")
    assert unit.anchor_path.is_file() and (unit.dir / "envelopes").is_dir()


def test_concurrent_new_calls_create_one_unit(tmp_path: Path) -> None:
    root = _workspace(tmp_path)

    def create(_: int) -> str:
        try:
            create_unit(Workspace(root), "u")
        except (UnitExistsError, UnitDirNotEmptyError) as exc:
            return exc.code
        return "created"

    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(create, range(16)))
    assert outcomes.count("created") == 1
    assert set(outcomes) == {"created", "UNIT_EXISTS"}
    assert _leftovers(root / UNIT) == []


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


# --- optional stages ------------------------------------------------------------------------------

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


def test_an_optional_stage_cannot_ask_for_an_approval() -> None:
    gated = parse_definition(OPTIONAL.format(gate="spike-ok", exit="anchor-exists"))
    assert [str(p) for p in validate_definition(gated, "task.md")] == [
        "spike.human_gate: an optional stage cannot have a gate 'spike-ok': it is never current, so its request is "
        "never asked; drop optional or move the approval to a stage that is not optional"
    ]
    checked = parse_definition(OPTIONAL.format(gate="false", exit="signed-off"))
    [problem] = validate_definition(checked, "task.md")
    assert problem.code == "WORKFLOW_DEFINITION_INVALID" and str(problem).startswith(
        "spike.exit: an optional stage cannot have a human check 'signed-off'"
    )
    # Checks the engine evaluates, or a runner passes with --given, stay allowed.
    for exit_ in ("anchor-exists", "ci"):
        assert validate_definition(parse_definition(OPTIONAL.format(gate="false", exit=exit_)), "task.md") == []


def test_validate_reports_an_optional_gated_stage(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    (root / ".devkit/workflows/w.md").write_text(OPTIONAL.format(gate="true", exit="anchor-exists"))
    result = _run("validate", "-w", str(root), "--format", "json")
    assert result.exit_code == 1
    [definition] = json.loads(result.stdout)["definitions"]
    assert [e["code"] for e in definition["errors"]] == ["WORKFLOW_DEFINITION_INVALID"]


# --- envelopes scoped to the segment ----------------------------------------------------------------

REVIEWED = """---
id: {id}
schema_version: 1
stages:
  - id: review
    exit: [envelope-review-passed]
next:
  - {{ workflow: {other} }}
---
"""


def _chain(root: Path) -> Path:
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "a.md").write_text(REVIEWED.format(id="a", other="b"))
    (defs / "b.md").write_text(REVIEWED.format(id="b", other="a"))
    write_config(root, '[workflow]\ndefault = "a"\n[workflow.approvals]\nhandoff = "auto"\n')
    return root


def _review(root: Path) -> Result:
    return _run(
        "envelope", "new", "-w", str(root), "--unit", UNIT, "--kind", "review", "--stage", "review", "--summary", "ok"
    )


def _stage(root: Path) -> str | None:
    result = json.loads(_run("next", "-w", str(root), "--unit", UNIT, "--no-lint", "--format", "json").stdout)
    return result["stage"]["id"] if result["stage"] else None


def test_envelope_new_records_the_workflow_and_segment(tmp_path: Path) -> None:
    root = _chain(tmp_path)
    assert _run("new", "-w", str(root), "u").exit_code == 0
    assert _review(root).exit_code == 0
    data = yaml.safe_load((root / UNIT / "envelopes/review-01.yaml").read_text())
    assert list(data)[:4] == ["kind", "stage", "workflow", "segment"]
    assert (data["workflow"], data["segment"]) == ("a", 0)
    skeleton = _run("envelope", "new", "-w", str(root), "--unit", UNIT, "--kind", "report")
    assert skeleton.exit_code == 0
    assert "workflow: a\nsegment: 0\n" in (root / UNIT / "envelopes/report-01.yaml").read_text()
    listed = json.loads(_run("envelope", "check", "-w", str(root), "--unit", UNIT, "--format", "json").stdout)
    assert [(e["workflow"], e["segment"]) for e in listed["envelopes"]] == [("a", 0), ("a", 0)]


def test_an_envelope_counts_only_in_its_segment(tmp_path: Path) -> None:
    root = _chain(tmp_path)
    assert _run("new", "-w", str(root), "u").exit_code == 0
    assert _stage(root) == "review"
    assert _review(root).exit_code == 0
    assert _stage(root) is None
    assert _run("handoff", "-w", str(root), "--unit", UNIT, "--no-lint").exit_code == 0  # a -> b
    # a's review does not satisfy b's review stage.
    assert _stage(root) == "review"
    assert _review(root).exit_code == 0
    assert _stage(root) is None
    assert _run("handoff", "-w", str(root), "--unit", UNIT, "--no-lint").exit_code == 0  # b -> a again
    # Re-entering a: the review of its first segment does not count either.
    assert _stage(root) == "review"
    assert _review(root).exit_code == 0
    assert _stage(root) is None
    data = yaml.safe_load((root / UNIT / "envelopes/review-03.yaml").read_text())
    assert (data["workflow"], data["segment"]) == ("a", 2)


def test_reverify_from_latest_reads_only_the_current_segment(tmp_path: Path) -> None:
    root = _chain(tmp_path)
    assert _run("new", "-w", str(root), "u").exit_code == 0
    assert _review(root).exit_code == 0
    assert _run("handoff", "-w", str(root), "--unit", UNIT, "--no-lint").exit_code == 0
    carried = _run("envelope", "new", "-w", str(root), "--unit", UNIT, "--kind", "reverify", "--from", "latest")
    assert carried.exit_code == 2 and "(ENVELOPE_FROM_INVALID)" in carried.stderr


def test_unscoped_envelopes_count_in_every_segment(tmp_path: Path) -> None:
    doc = parse_definition(REVIEWED.format(id="b", other="a"))
    unit = write_unit(tmp_path, "u")
    write_binding(unit / "task.md", Binding("b", "h", (HistoryEntry("a", "h", "2026-10-12", 0),)))
    (unit / "envelopes").mkdir()
    opts = Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md", skip_lint=True)

    def review(**scope: object) -> None:
        (unit / "envelopes/review-01.yaml").write_text(
            yaml.safe_dump({"kind": "review", "stage": "review", "status": "completed", **scope})
        )

    for scope, counts in (
        ({}, True),
        ({"workflow": "b"}, True),
        ({"workflow": "b", "segment": 1}, True),
        ({"workflow": "b", "segment": 0}, False),
        ({"workflow": "a", "segment": 1}, False),
        ({"segment": 0}, True),
    ):
        review(**scope)
        assert evaluate_definition(doc, opts).complete is counts, scope


@pytest.mark.parametrize(
    ("scope", "reason"),
    [
        ({"workflow": "Not An Id"}, "workflow 'Not An Id' must be a workflow id"),
        ({"segment": -1}, "segment: expected a non-negative integer"),
        ({"segment": "1"}, "segment: expected a non-negative integer"),
        ({"segment": True}, "segment: expected a non-negative integer"),
    ],
)
def test_a_malformed_scope_is_an_envelope_error(tmp_path: Path, scope: dict[str, object], reason: str) -> None:
    unit = write_unit(tmp_path, "u")
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text(yaml.safe_dump({"kind": "review", "status": "completed", **scope}))
    [error] = load_envelopes(unit).errors
    assert error.code == "ENVELOPE_INVALID" and error.message.startswith(reason)
