"""Regression tests for the review findings (B1-B13, R1-R10 and nits), one or more per finding."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit.workflow import (
    AnchorInvalidError,
    DefinitionError,
    DriftError,
    Options,
    TemplateLayout,
    Workspace,
    evaluate_definition,
    load_check_files,
    load_decisions,
    load_envelopes,
    parse_definition,
    render_evaluation,
    schema_hash,
    validate_definition,
    write_envelope,
)
from devkit.workflow.cli import cli
from devkit.workflow.errors import AuthoringError
from devkit.workflow.unit import frontmatter as fm
from devkit.workflow.unit.envelope import compose_envelope
from testsupport.workflow import WORKFLOW, write_config, write_record, write_unit

A = """---
id: a
schema_version: 1
stages:
  - id: build
    human_gate: integration
    exit: [file-exists(done.txt)]
next:
  - { workflow: b }
---
"""
B = """---
id: b
schema_version: 1
stages:
  - id: ship
    human_gate: integration
    exit: [file-exists(shipped.txt)]
next:
  - { workflow: c }
---
"""
C = """---
id: c
schema_version: 1
stages:
  - id: close
    exit: [anchor-exists]
next:
  - { workflow: b }
  - { workflow: d }
---
"""
D = """---
id: d
schema_version: 1
stages:
  - id: done
    exit: [anchor-exists]
---
"""
LOOP = """---
id: loop
schema_version: 1
stages:
  - id: build
    exit: [tasks-all-checked]
  - id: integrate
    human_gate: integration
    exit: [file-exists(ready.txt)]
---
"""
UNIT = ".devkit/transient/work/u"


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def _workspace(root: Path, docs: dict[str, str], default: str, approvals: str = "") -> Path:
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True, exist_ok=True)
    for name, text in docs.items():
        (defs / f"{name}.md").write_text(text)
    write_config(root, f'[workflow]\ndefault = "{default}"\n[workflow.approvals]\n{approvals}')
    return root


def _answer(root: Path, request: str, *extra: str) -> Result:
    result = _run("answer", "-w", str(root), "--unit", UNIT, "--no-lint", "--request", request, *extra)
    assert result.exit_code == 0, result.output + result.stderr
    return result


def _next(root: Path, *extra: str) -> Result:
    return _run("next", "-w", str(root), "--unit", UNIT, "--no-lint", *extra)


# --- B1: approvals are scoped to the workflow segment ------------------------------------


def test_b1_gate_approval_does_not_carry_across_a_handoff(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"a": A, "b": B, "c": C, "d": D}, "a", 'handoff = "auto"\n')
    assert _run("new", "-w", str(root), "u").exit_code == 0
    (root / UNIT / "done.txt").write_text("x")
    assert "[REQUEST: id=gate:integration" in _next(root).output
    _answer(root, "gate:integration", "--action", "accept")
    assert "[STAGE: - complete=true]" in _next(root).output
    handed = _run("handoff", "-w", str(root), "--unit", UNIT, "--no-lint")
    assert handed.exit_code == 0, handed.stderr
    (root / UNIT / "shipped.txt").write_text("x")
    nxt = _next(root)
    assert "[STAGE: ship" in nxt.output and "[REQUEST: id=gate:integration" in nxt.output


def test_b1_return_loop_requires_the_gate_again(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"loop": LOOP}, "loop")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    unit = root / UNIT
    (unit / "tasks.md").write_text("- [x] a\n")
    (unit / "ready.txt").write_text("x")
    _answer(root, "gate:integration", "--action", "accept")
    assert "[STAGE: - complete=true]" in _next(root).output

    # The unit goes back to build: `next` reports the integration approval as stale but writes nothing.
    (unit / "tasks.md").write_text("- [ ] a\n")
    before = sorted(p.relative_to(unit).as_posix() for p in unit.rglob("*"))
    back = _next(root)
    assert back.exit_code == 0 and "[STAGE: build" in back.output
    assert (
        "[STALE_APPROVAL: decisions/01-gate-integration.yaml request=gate:integration stage=integrate counts=yes "
        f'void_with="devkit workflow return --unit {UNIT} --to build"]' in back.output
    )
    as_json = json.loads(_next(root, "--format", "json").output)
    assert as_json["stale_approvals"] == ["decisions/01-gate-integration.yaml"]
    assert sorted(p.relative_to(unit).as_posix() for p in unit.rglob("*")) == before
    assert [r.request for r in load_decisions(unit).records] == ["gate:integration"]

    # Until an explicit return, the stale approval still counts: redoing build completes the unit again.
    (unit / "tasks.md").write_text("- [x] a\n")
    assert "[STAGE: - complete=true]" in _next(root).output

    # After `devkit workflow return`, the approval no longer counts and must be given again.
    (unit / "tasks.md").write_text("- [ ] a\n")
    returned = _run("return", "-w", str(root), "--unit", UNIT, "--no-lint", "--to", "build")
    assert returned.exit_code == 0, returned.stderr
    assert [r.request for r in load_decisions(unit).records] == ["gate:integration", "return:build"]
    (unit / "tasks.md").write_text("- [x] a\n")
    again = _next(root)
    assert "[STAGE: integrate" in again.output and "[REQUEST: id=gate:integration" in again.output
    assert "[STALE_APPROVAL" not in again.output


def test_b1_explicit_return_command(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"direct-delivery": WORKFLOW}, "direct-delivery")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    _answer(root, "gate:direction", "--action", "accept")
    assert "[DONE: intent]" in _next(root).output
    later = _run("return", "-w", str(root), "--unit", UNIT, "--no-lint", "--to", "review")
    assert later.exit_code == 2 and "(RETURN_INVALID)" in later.stderr
    unknown = _run("return", "-w", str(root), "--unit", UNIT, "--no-lint", "--to", "nope")
    assert unknown.exit_code == 2 and "(RETURN_INVALID)" in unknown.stderr
    back = _run("return", "-w", str(root), "--unit", UNIT, "--no-lint", "--to", "intent", "--note", "new scope")
    assert back.exit_code == 0 and back.output.strip() == "[RETURNED: decisions/02-return-intent.yaml to=intent]"
    nxt = _next(root)
    assert "[STAGE: intent" in nxt.output and "[REQUEST: id=gate:direction" in nxt.output


# --- B2: a recorded handoff choice belongs to its segment ---------------------------------


def test_b2_stale_handoff_choice_is_not_reused(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"a": A, "b": B, "c": C, "d": D}, "a", 'integration = "auto"\n')
    assert _run("new", "-w", str(root), "u").exit_code == 0
    unit = root / UNIT
    (unit / "done.txt").write_text("x")
    _answer(root, "handoff", "--action", "accept", "--value", "b")
    assert _run("handoff", "-w", str(root), "--unit", UNIT, "--no-lint").exit_code == 0
    (unit / "shipped.txt").write_text("x")
    to_c = _run("handoff", "-w", str(root), "--unit", UNIT, "--no-lint", "--workflow", "c")
    assert to_c.exit_code == 0 and "decision=decisions/02-handoff.yaml" in to_c.output
    # c lists b again; the old "b" choice was made in segment a and must not decide here.
    nxt = _next(root)
    assert "[WORKFLOW: c" in nxt.output and "chosen=-" in nxt.output and "[REQUEST: id=handoff" in nxt.output
    history = Workspace(root).resolve_unit(UNIT).binding.history
    assert [(h.workflow, h.last_decision) for h in history] == [("a", 1), ("b", 2)]


# --- B3: gates are asked once the stage's work is done -------------------------------------


def test_b3_no_gate_request_or_human_wait_while_exit_checks_are_unmet(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/u")
    opts = Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md", skip_lint=True)
    res = evaluate_definition(parse_definition(A), opts)
    assert [u.name for u in res.unmet] == ["file-exists(done.txt)"]
    assert res.requests == [] and res.waiting is None
    assert res.gate is not None and not res.gate.satisfied
    (unit / "done.txt").write_text("x")
    res = evaluate_definition(parse_definition(A), opts)
    assert [u.name for u in res.unmet] == ["gate:integration"] and [r.id for r in res.requests] == ["gate:integration"]
    assert res.waiting is not None and res.waiting.checks == ("gate:integration",)


# --- B4 / R1: drift ----------------------------------------------------------------------------


def test_b4_evaluating_another_workflow_is_not_drift(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"a": A, "b": B, "c": C, "d": D}, "a")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    result = _next(root, "--workflow", "d")
    assert result.exit_code == 0, result.stderr
    assert "[BOUND_ELSEWHERE: workflow=a]" in result.output and "[DRIFT" not in result.output
    data = json.loads(_next(root, "--workflow", "d", "--format", "json").stdout)
    assert data["bound_elsewhere"] == "a" and data["drift"] is None


def test_r1_drift_policy_lives_in_the_library(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"d": D}, "d")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    definition = root / ".devkit/workflows/d.md"
    definition.write_text(definition.read_text().replace("exit: [anchor-exists]", "exit: [file-exists(x)]"))
    ws = Workspace(root)
    with pytest.raises(DriftError) as raised:
        ws.evaluate_unit(ws.resolve_unit(UNIT), lint=False)
    assert raised.value.code == "WORKFLOW_DRIFT"
    assert ws.evaluate_unit(ws.resolve_unit(UNIT), lint=False, enforce_drift=False).blocked_by_drift
    # A unit with no current stage reports drift without blocking.
    (root / UNIT / "x").write_text("x")
    result = ws.evaluate_unit(ws.resolve_unit(UNIT), lint=False)
    assert result.complete and result.drift is not None


# --- B5 / B6: frontmatter rewriting ---------------------------------------------------------------


def test_b5_update_drops_the_whole_block_value_of_a_replaced_key() -> None:
    text = (
        "---\nid: x\nworkflow: a\nworkflow_history:\n  - workflow: z\n    hash: h0\n\n    completed: '2026-01-01'\n"
        "list:\n- one\n- two\nowner: me\n---\n# x\n"
    )
    out = fm.update(text, {"workflow": "b", "workflow_history": "[{workflow: z}]", "list": "[three]"})
    assert out == "---\nid: x\nowner: me\nworkflow: b\nworkflow_history: [{workflow: z}]\nlist: [three]\n---\n# x\n"
    assert fm.parse(out)["owner"] == "me"


def test_b6_update_and_parse_agree_on_the_block() -> None:
    assert fm.update("---\n---\nbody\n", {"k": "v"}) == "---\nk: v\n---\nbody\n"
    spaced = "---\na: 1\n--- \nbody\n"
    assert fm.parse(spaced) == {"a": 1}
    assert fm.parse(fm.update(spaced, {"k": "v"})) == {"a": 1, "k": "v"}
    with pytest.raises(fm.FrontmatterError):
        fm.update("---\na: 1\n", {"k": "v"})


# --- B7 / B8: decision records ------------------------------------------------------------------


def test_b7_sequence_continues_after_a_malformed_last_record(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"direct-delivery": WORKFLOW}, "direct-delivery")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    write_record(root / UNIT, "01-gate-direction.yaml", request="gate:direction", kind="approve", action="maybe")
    accepted = _answer(root, "gate:direction", "--action", "accept")
    assert "decisions/02-gate-direction.yaml" in accepted.output


def test_b8_records_are_validated_against_their_request(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/u")
    common = {"workflow": "a", "action": "accept"}
    write_record(unit, "01-gate-integration.yaml", request="gate:integration", kind="choose", value="x", **common)
    write_record(unit, "02-handoff.yaml", request="gate:integration", kind="approve", stage="build", **common)
    write_record(unit, "03-gate-integration.yaml", request="gate:integration", kind="approve", **common)
    write_record(
        unit, "04-gate-integration.yaml", request="gate:integration", kind="approve", stage="build", value="v", **common
    )
    decisions = load_decisions(unit)
    reasons = {e.file: e.message for e in decisions.errors}
    assert "does not match request" in reasons["decisions/01-gate-integration.yaml"]
    assert "file name must be NN-gate-integration.yaml" in reasons["decisions/02-handoff.yaml"]
    assert "needs the stage" in reasons["decisions/03-gate-integration.yaml"]
    assert "takes no value" in reasons["decisions/04-gate-integration.yaml"]
    assert decisions.records == [] and decisions.next_sequence() == 5
    res = evaluate_definition(parse_definition(A), Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md"))
    assert len(res.decision_errors) == 4


def test_b8_unquoted_timestamps_are_accepted(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/u")
    (unit / "decisions").mkdir()
    (unit / "decisions/01-gate-integration.yaml").write_text(
        "request: gate:integration\nkind: approve\naction: accept\nworkflow: a\nstage: build\nat: 2026-10-12T09:30:00Z\n"
    )
    (unit / "decisions/02-feedback-build.yaml").write_text(
        "request: feedback:build\nkind: feedback\naction: accept\nworkflow: a\nvalue: note\nat: 2026-10-12\n"
    )
    decisions = load_decisions(unit)
    assert decisions.errors == []
    assert [r.at for r in decisions.records] == ["2026-10-12T09:30:00Z", "2026-10-12"]


# --- B9: one JSON document --------------------------------------------------------------------


def test_b9_json_output_is_a_single_document_when_lint_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import devkit.rules

    def broken(*_: object, **__: object) -> None:
        raise RuntimeError("rule exploded")

    root = _workspace(
        tmp_path, {"w": "---\nid: w\nschema_version: 1\nstages:\n  - id: s\n    exit: [lint-clean]\n---\n"}, "w"
    )
    assert _run("new", "-w", str(root), "u").exit_code == 0
    monkeypatch.setattr(devkit.rules, "run_project_rules", broken)
    result = _run("next", "-w", str(root), "--unit", UNIT, "--format", "json")
    assert result.exit_code == 2 and "(UNEXPECTED_ERROR) rule exploded" in result.stderr
    [error] = json.loads(result.stdout)["errors"]
    assert (error["code"], error["message"]) == ("UNEXPECTED_ERROR", "rule exploded")
    text = _run("next", "-w", str(root), "--unit", UNIT)
    assert '[LINT_ERROR: "rule exploded"]' in text.output


def test_b9_envelope_check_json_is_a_single_document(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"direct-delivery": WORKFLOW}, "direct-delivery")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    (root / UNIT / "envelopes/review-01.yaml").write_text("status: completed\n")
    result = _run("envelope", "check", "-w", str(root), "--unit", UNIT, "--format", "json")
    assert result.exit_code == 1 and "(ENVELOPE_INVALID)" in result.stderr
    assert json.loads(result.stdout)["errors"][0]["file"] == "envelopes/review-01.yaml"


# --- B10 - B13 -------------------------------------------------------------------------------------


def test_b10_discovery_follows_slashes_in_date_specs(tmp_path: Path) -> None:
    layout = TemplateLayout("specs", "{date:%Y/%m}/{slug}", "spec.md")
    rel = layout.new_unit("login", date(2026, 10, 12))
    assert rel.as_posix() == "specs/2026/10/login" and layout.discovery_glob() == "*/*/*"
    (tmp_path / rel).mkdir(parents=True)
    (tmp_path / rel / "spec.md").write_text("---\nid: x\n---\n")
    assert [p.as_posix() for p in layout.discover(tmp_path)] == ["specs/2026/10/login"]


@pytest.mark.parametrize("key", ["optional", "exception"])
def test_b11_stage_flags_must_be_booleans(key: str) -> None:
    with pytest.raises(DefinitionError, match=rf"s\.{key}: expected true or false"):
        parse_definition(f"---\nid: c\nschema_version: 1\nstages:\n  - id: s\n    {key}: 'false'\n---\n")
    with pytest.raises(DefinitionError, match=r"s\.role: expected a string"):
        parse_definition("---\nid: c\nschema_version: 1\nstages:\n  - id: s\n    role: 3\n---\n")


def test_b12_envelope_status_is_validated_on_load(tmp_path: Path) -> None:
    (tmp_path / "envelopes").mkdir()
    (tmp_path / "envelopes/review-01.yaml").write_text("kind: review\nstatus: complete\n")
    envelopes = load_envelopes(tmp_path)
    assert envelopes.by_kind == {} and "status 'complete' not in" in envelopes.errors[0].message


def test_b13_envelope_sequences_past_99(tmp_path: Path) -> None:
    (tmp_path / "envelopes").mkdir()
    (tmp_path / "envelopes/review-99.yaml").write_text("kind: review\nstatus: completed\n")
    (tmp_path / "envelopes/review-07.yaml").write_text("not: [valid\n")  # malformed files still count
    path, seq = write_envelope(tmp_path, "review", "kind: review\nstatus: completed\n")
    assert (path.name, seq) == ("review-100.yaml", 100)
    envelopes = load_envelopes(tmp_path)
    latest = envelopes.latest("review")
    assert latest is not None and latest.seq == 100
    assert [e.file for e in envelopes.errors] == ["envelopes/review-07.yaml"]


# --- R2 - R8 ------------------------------------------------------------------------------------------


def test_r2_workflow_paths_resolve_against_the_workspace_root(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"a": A, "b": B, "c": C, "d": D}, "a")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    result = _next(root, "--workflow", ".devkit/workflows/d.md")
    assert result.exit_code == 0, result.stderr
    assert "[WORKFLOW: d " in result.output


def test_r3_invalid_anchor_is_an_error_in_the_library(tmp_path: Path) -> None:
    unit = tmp_path / "work/u"
    unit.mkdir(parents=True)
    (unit / "task.md").write_text("---\nstatus: [broken\n---\n")
    with pytest.raises(AnchorInvalidError) as raised:
        evaluate_definition(parse_definition(A), Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md"))
    assert raised.value.code == "ANCHOR_INVALID"


def test_r4_display_names_do_not_change_the_hash() -> None:
    renamed = WORKFLOW.replace("name: Intent", "name: Clarify intent")
    assert schema_hash(parse_definition(renamed)) == schema_hash(parse_definition(WORKFLOW))
    assert schema_hash(
        parse_definition(WORKFLOW.replace("isolation: preferred", "isolation: required"))
    ) != schema_hash(parse_definition(WORKFLOW))


def test_r5_unknown_keys_gate_names_and_schema_version() -> None:
    doc = parse_definition(WORKFLOW.replace("status: active", "status: active\nnxt: []"))
    assert "nxt: unknown document key" in {str(p) for p in validate_definition(doc, "task.md")}
    bad_gate = parse_definition(
        "---\nid: c\nschema_version: true\nstages:\n  - id: s\n    human_gate: Integration\n---\n"
    )
    problems = {str(p) for p in validate_definition(bad_gate, "task.md")}
    assert "s.human_gate: gate name 'Integration' must match [a-z][a-z0-9-]*" in problems
    assert any(p.startswith("schema_version: unsupported schema_version 0") for p in problems)
    with pytest.raises(DefinitionError, match=r"returns\[0\]: unknown keys \['why'\]"):
        parse_definition("---\nid: c\nstages:\n  - id: s\n    returns: [{to: s, why: x}]\n---\n")
    with pytest.raises(DefinitionError, match=r"checks\[0\]: unknown keys \['kind'\]"):
        parse_definition("---\nid: c\nchecks: [{name: x, class: human, kind: y}]\nstages:\n  - id: s\n---\n")
    clash = parse_definition(
        "---\nid: c\nschema_version: 1\nchecks: [{name: review, class: human}]\n"
        "stages:\n  - id: s\n    human_gate: review\n---\n"
    )
    assert any("has the name of a gate" in str(p) for p in validate_definition(clash, "task.md"))


def test_r5_check_file_arguments_stay_inside_the_unit() -> None:
    doc = parse_definition(
        "---\nid: c\nschema_version: 1\nstages:\n  - id: s\n    exit: [file-exists(../x), file-exists(/etc/passwd)]\n---\n"
    )
    problems = [str(p) for p in validate_definition(doc, "task.md")]
    assert len(problems) == 2 and all("must be a path inside the unit directory" in p for p in problems)


def test_r6_git_failure_is_not_a_definite_answer(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/u")
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text("kind: review\nstatus: completed\ndiff_scope: {head: abc1234}\n")
    (unit / "envelopes/final-report-01.yaml").write_text(
        "kind: final-report\nstatus: completed\ndiff_scope: {head: def5678}\n"
    )
    doc = parse_definition(
        "---\nid: c\nschema_version: 1\nstages:\n  - id: s\n    exit: [revision-ancestor(review final-report)]\n---\n"
    )

    def unknown_revision(*_: object) -> bool:
        raise RuntimeError("bad object abc1234")

    res = evaluate_definition(
        doc, Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md", ancestor=unknown_revision)
    )
    assert (res.unmet[0].evaluated, res.unmet[0].detail) == (False, "git: bad object abc1234")
    res = evaluate_definition(doc, Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md"))
    assert (res.unmet[0].evaluated, res.unmet[0].detail) == (False, "no git function configured")
    with pytest.raises(AuthoringError, match="hexadecimal commit id"):
        compose_envelope(unit_dir=unit, envelopes=load_envelopes(unit), kind="review", head="HEAD")


def test_r7_free_text_stays_on_one_line(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/u")
    (unit / "done.txt").write_text("x")
    write_record(
        unit,
        "01-gate-integration.yaml",
        request="gate:integration",
        kind="approve",
        action="decline",
        workflow="a",
        stage="build",
        note='say "no"\n] [FAKE: x',
    )
    text = render_evaluation(
        evaluate_definition(parse_definition(A), Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md"))
    )
    assert (
        '[DECLINED: id=gate:integration file=decisions/01-gate-integration.yaml note="say \\"no\\"\\n] [FAKE: x"]'
        in text
    )
    assert all(not line.startswith("[FAKE") for line in text.splitlines())


def test_r8_gate_reports_what_satisfied_it(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/u")
    doc = parse_definition(A)
    base = {"workspace_root": tmp_path, "unit_dir": unit, "anchor": "task.md"}
    res = evaluate_definition(doc, Options(**base, given=("integration",)))  # type: ignore[arg-type]
    assert res.gate is not None and (res.gate.satisfied, res.gate.source) == (True, "given")
    res = evaluate_definition(doc, Options(**base, approvals={"integration": "auto"}))  # type: ignore[arg-type]
    assert res.gate is not None and (res.gate.satisfied, res.gate.source) == (True, "policy")
    write_record(
        unit,
        "01-gate-integration.yaml",
        request="gate:integration",
        kind="approve",
        action="accept",
        workflow="a",
        stage="build",
    )
    res = evaluate_definition(doc, Options(**base))  # type: ignore[arg-type]
    assert res.gate is not None
    assert res.gate.to_dict() == {
        "name": "integration",
        "policy": "ask",
        "satisfied": True,
        "source": "decision",
        "decision": "decisions/01-gate-integration.yaml",
    }
    assert (
        "[GATE: integration policy=ask satisfied=yes source=decision:decisions/01-gate-integration.yaml]"
        in render_evaluation(res)
    )


# --- R10 and nits ----------------------------------------------------------------------------------


GOOD_AND_BAD = """
from devkit.workflow import BaseCheck


class Good(BaseCheck):
    name = "good"

    def evaluate(self, ctx):
        return ctx.passed()


class Bad(BaseCheck):
    name = "Bad Name"
"""


def test_r10_plugin_files_load_atomically(tmp_path: Path) -> None:
    (tmp_path / "mixed.py").write_text(GOOD_AND_BAD)
    (tmp_path / "first.py").write_text(GOOD_AND_BAD.split("class Bad")[0])
    (tmp_path / "second.py").write_text(GOOD_AND_BAD.split("class Bad")[0])
    loaded, errors = load_check_files([tmp_path / "mixed.py", tmp_path / "first.py", tmp_path / "second.py"])
    assert [c.name for c in loaded] == ["good"]  # only first.py
    assert len(errors) == 2
    assert "mixed.py" in str(errors[0]) and "must match" in str(errors[0])
    assert "second.py" in str(errors[1]) and "already defined" in str(errors[1])


def test_nit_feedback_value_requires_accept_and_list_reports_unreadable_anchors(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"direct-delivery": WORKFLOW}, "direct-delivery")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    declined = _run(
        "answer", "-w", str(root), "--unit", UNIT, "--request", "feedback:x", "--action", "decline", "--value", "t"
    )
    assert declined.exit_code == 2 and "(DECISION_INVALID)" in declined.stderr
    broken = root / ".devkit/transient/work/broken"
    broken.mkdir()
    (broken / "task.md").write_text("---\nid: [x\n---\n")
    rows = json.loads(_run("list", "-w", str(root), "--format", "json").stdout)["units"]
    assert [(r["unit"], r["error"] is not None) for r in rows] == [
        (".devkit/transient/work/broken", True),
        (UNIT, False),
    ]


def test_nit_new_refuses_a_directory_that_already_is_a_unit(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"direct-delivery": WORKFLOW}, "direct-delivery")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    again = _run("new", "-w", str(root), "u")
    assert again.exit_code == 2 and "(UNIT_EXISTS)" in again.stderr


def test_workspace_root_defaults_to_the_enclosing_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _workspace(tmp_path, {"direct-delivery": WORKFLOW}, "direct-delivery")
    assert _run("new", "-w", str(root), "u").exit_code == 0
    monkeypatch.chdir(root / UNIT)
    result = _run("next", "--unit", str(root / UNIT), "--no-lint")
    assert result.exit_code == 0 and "[WORKFLOW: direct-delivery unit=.devkit/transient/work/u " in result.output
