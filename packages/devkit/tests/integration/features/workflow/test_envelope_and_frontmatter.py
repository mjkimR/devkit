from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import devkit_agt.features.workflow.repositories.unit.frontmatter as fm
import pytest
import yaml
from click.testing import Result
from devkit_agt.features.workflow import (
    Binding,
    HistoryEntry,
    Options,
    envelope_timestamp,
    evaluate_definition,
    load_envelopes,
    parse_definition,
    read_binding,
    write_binding,
)
from devkit_agt.features.workflow.services.envelope import skeleton, write_envelope
from testsupport.workflow import SIMPLE_UNIT, run_cli, simple_workspace, write_config, write_record, write_unit

# --- frontmatter ------------------------------------------------------------------


def test_parse_uses_the_core_grammar() -> None:
    assert fm.parse("no block") == {}
    assert fm.parse("---\na: 1\nb: true\n---\n") == {"a": 1, "b": True}
    assert fm.parse("---\na: 1\n---") == {"a": 1}
    for broken in ("---\na: [\n---\n", "---\n- list\n---\n", "---\na: 1\na: 2\n---\n", "---\na: 1\n"):
        with pytest.raises(fm.FrontmatterError):
            fm.parse(broken)


def test_field_stringifies_scalars() -> None:
    data = {"s": "x", "n": 3, "b": False, "none": None}
    assert [fm.field(data, k) for k in ("s", "n", "b", "none", "missing")] == ["x", "3", "false", "", ""]


def test_update_preserves_other_lines_and_nested_keys() -> None:
    text = "---\nid: x\nworkflow: old\nmeta:\n  workflow: nested\n# comment\n---\nbody\n"
    out = fm.update(text, {"workflow": "new", "owner": "agent"})
    assert out == "---\nid: x\nmeta:\n  workflow: nested\n# comment\nworkflow: new\nowner: agent\n---\nbody\n"


def test_update_handles_crlf_and_missing_block() -> None:
    out = fm.update("---\r\nid: x\r\n---\r\nbody", {"k": "v"})
    assert out == "---\r\nid: x\r\nk: v\r\n---\r\nbody"
    assert fm.update("plain", {"k": "v"}) == "---\nk: v\n---\nplain"
    assert fm.update("# t\r\nbody", {"k": "v"}) == "---\r\nk: v\r\n---\r\n# t\r\nbody"


def test_render_roundtrip() -> None:
    text = fm.render({"id": "a", "status": "planned"}, "# a\n")
    assert text.startswith("---\nid: a\nstatus: planned\n---\n# a\n")
    assert fm.parse(text) == {"id": "a", "status": "planned"}


# --- binding -------------------------------------------------------------------------


def test_binding_read_write(tmp_path: Path) -> None:
    anchor = tmp_path / "task.md"
    anchor.write_text("---\nid: a\nstatus: planned\n---\n# a\n")
    assert read_binding(anchor) == Binding()
    assert not read_binding(anchor).bound
    write_binding(anchor, Binding("wf"))
    assert read_binding(anchor) == Binding("wf")
    assert anchor.read_text().startswith("---\nid: a\nstatus: planned\nworkflow: wf\n---\n# a\n")
    write_binding(anchor, Binding("wf"))
    assert "workflow_hash" not in anchor.read_text()


# --- envelopes --------------------------------------------------------------------------


def _write(unit: Path, name: str, body: str) -> None:
    (unit / "envelopes").mkdir(exist_ok=True)
    (unit / "envelopes" / name).write_text(body)


def test_missing_envelopes_dir(tmp_path: Path) -> None:
    env = load_envelopes(tmp_path)
    assert env.by_kind == {} and env.errors == [] and env.latest("review") is None
    assert write_envelope(tmp_path, "review", "kind: review\n") == (tmp_path / "envelopes/review-01.yaml", 1)


def test_load_sorts_by_sequence_and_computes_review_state(tmp_path: Path) -> None:
    _write(tmp_path, "review-02.yaml", "kind: review\nstatus: completed\nfindings:\n  - issue: a\n")
    _write(tmp_path, "review-01.yaml", "kind: review\nstatus: completed\n")
    _write(tmp_path, "reverify-01.yaml", "kind: reverify\nstatus: completed\nreview: review-02.yaml\n")
    env = load_envelopes(tmp_path)
    assert [e.seq for e in env.by_kind["review"]] == [1, 2]
    assert env.latest("review").open_findings() == 1  # type: ignore[union-attr]
    decider = env.review_state()
    assert decider is not None and decider.kind == "reverify" and decider.open_findings() == 0
    assert env.deciding("review") is decider
    assert env.errors == []
    assert write_envelope(tmp_path, "review", "x")[1] == 3


def test_reverify_for_older_round_does_not_decide(tmp_path: Path) -> None:
    _write(tmp_path, "review-01.yaml", "kind: review\nstatus: completed\n")
    _write(tmp_path, "review-02.yaml", "kind: review\nstatus: completed\nfindings:\n  - {issue: a, resolution: open}\n")
    _write(tmp_path, "reverify-01.yaml", "kind: reverify\nstatus: completed\nreview: review-01.yaml\n")
    decider = load_envelopes(tmp_path).review_state()
    assert decider is not None and decider.file == "envelopes/review-02.yaml"


@pytest.mark.parametrize(
    ("name", "body", "reason"),
    [
        ("review-1.yaml", "kind: review\nstatus: completed\n", "file name must be"),
        ("review-01.yaml", "status: completed\n", "missing required key kind"),
        ("review-01.yaml", "kind: scout\nstatus: completed\n", "does not match file name"),
        ("review-01.yaml", "kind: review\n", "missing required key status"),
        ("reverify-01.yaml", "kind: reverify\nstatus: completed\n", "reverify needs"),
        ("review-01.yaml", "kind: review\nstatus: completed\nfindings:\n  - {resolution: maybe}\n", "resolution"),
        ("review-01.yaml", "kind: review\nstatus: completed\nchecks: [a]\n", "checks: expected a mapping"),
        ("review-01.yaml", "kind: [\n", "yaml:"),
        ("review-01.yaml", "- list\n", "expected a mapping"),
    ],
)
def test_envelope_errors(tmp_path: Path, name: str, body: str, reason: str) -> None:
    _write(tmp_path, name, body)
    env = load_envelopes(tmp_path)
    assert env.by_kind == {}
    assert len(env.errors) == 1 and reason in env.errors[0].message


def test_checks_and_diff_scope(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "final-report-01.yaml",
        'kind: final-report\nstatus: completed\nchecks:\n  tests: "PASS 3/3"\n  lint: FAIL\ndiff_scope: {base: main, head: abc1234}\n',
    )
    env = load_envelopes(tmp_path).latest("final-report")
    assert env is not None
    assert env.check_pass("tests") and not env.check_pass("lint") and not env.check_pass("missing")
    assert (env.diff_base, env.diff_head) == ("main", "abc1234")
    assert env.to_dict()["diff_scope"] == {"base": "main", "head": "abc1234"}


def test_skeleton_is_never_accepted() -> None:
    text = skeleton("reverify", "review", "2026-10-12T00:00:00Z")
    assert "status: needs_input" in text and "review: review-NN.yaml" in text and "diff_scope" in text
    assert "diff_scope" not in skeleton("scout", "", "t")


# --- envelopes scoped to the segment ----------------------------------------------------------

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


def _review(root: Path, *extra: str) -> Result:
    return run_cli(
        "envelope", "review", "-w", str(root), "--unit", SIMPLE_UNIT, "--stage", "review",
        "--summary", "ok", *extra,
    )  # fmt: skip


def _stage(root: Path) -> str | None:
    result = json.loads(run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint", "--format", "json").stdout)
    return result["stage"]["id"] if result["stage"] else None


def test_envelope_new_records_the_workflow_and_segment(tmp_path: Path) -> None:
    root = _chain(tmp_path)
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    assert _review(root).exit_code == 0
    data = yaml.safe_load((root / SIMPLE_UNIT / "envelopes/review-01.yaml").read_text())
    assert list(data)[:4] == ["kind", "stage", "workflow", "segment"]
    assert (data["workflow"], data["segment"]) == ("a", 0)
    skeleton = run_cli("envelope", "new", "-w", str(root), "--unit", SIMPLE_UNIT, "--kind", "report")
    assert skeleton.exit_code == 0
    assert "workflow: a\nsegment: 0\n" in (root / SIMPLE_UNIT / "envelopes/report-01.yaml").read_text()
    listed = json.loads(run_cli("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT, "--format", "json").stdout)
    assert [(e["workflow"], e["segment"]) for e in listed["envelopes"]] == [("a", 0), ("a", 0)]


def test_an_envelope_counts_only_in_its_segment(tmp_path: Path) -> None:
    root = _chain(tmp_path)
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    assert _stage(root) == "review"
    assert _review(root).exit_code == 0
    assert _stage(root) is None
    assert run_cli("handoff", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint").exit_code == 0  # a -> b
    # a's review does not satisfy b's review stage.
    assert _stage(root) == "review"
    assert _review(root).exit_code == 0
    assert _stage(root) is None
    assert run_cli("handoff", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint").exit_code == 0  # b -> a again
    # Re-entering a: the review of its first segment does not count either.
    assert _stage(root) == "review"
    assert _review(root).exit_code == 0
    assert _stage(root) is None
    data = yaml.safe_load((root / SIMPLE_UNIT / "envelopes/review-03.yaml").read_text())
    assert (data["workflow"], data["segment"]) == ("a", 2)


def test_reverify_from_latest_reads_only_the_current_segment(tmp_path: Path) -> None:
    root = _chain(tmp_path)
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    assert _review(root).exit_code == 0
    assert run_cli("handoff", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint").exit_code == 0
    carried = run_cli("envelope", "reverify", "-w", str(root), "--unit", SIMPLE_UNIT, "--from", "latest")
    assert carried.exit_code == 2 and "(ENVELOPE_FROM_INVALID)" in carried.stderr


def test_unscoped_envelopes_count_in_every_segment(tmp_path: Path) -> None:
    doc = parse_definition(REVIEWED.format(id="b", other="a"))
    unit = write_unit(tmp_path, "u")
    write_binding(unit / "task.md", Binding("b", (HistoryEntry("a", "2026-10-12", 0),)))
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


# --- envelope new after a return, and without the definition -----------------------------------


def test_an_envelope_written_right_after_a_return_counts(tmp_path: Path) -> None:
    root = _chain(tmp_path)
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    assert _review(root).exit_code == 0 and _stage(root) is None
    returned = run_cli("return", "-w", str(root), "--unit", SIMPLE_UNIT, "--to", "review", "--no-lint")
    assert returned.exit_code == 0, returned.output
    assert _stage(root) == "review"  # the return voided the first review
    assert _review(root).exit_code == 0
    assert _stage(root) is None  # the review written within the same second counts


def test_an_envelope_is_stamped_after_the_latest_return(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    returned = {"kind": "return", "action": "accept", "workflow": "a", "stage": "review"}
    write_record(unit, "01-return-review.yaml", request="return:review", at="2026-10-12T09:30:00Z", **returned)
    early = datetime(2026, 10, 12, 9, 30, 0, 300000, tzinfo=UTC)  # a clock behind the record's second
    assert envelope_timestamp(unit, "a", 0, early) == "2026-10-12T09:30:01Z"
    assert envelope_timestamp(unit, "a", 0, datetime(2026, 10, 12, 10, 0, tzinfo=UTC)) == "2026-10-12T10:00:00Z"
    # Returns of another workflow or a finished segment do not hold the stamp back.
    assert envelope_timestamp(unit, "b", 0, early) == "2026-10-12T09:30:00.300000Z"
    assert envelope_timestamp(unit, "a", 1, early) == "2026-10-12T09:30:00.300000Z"


@pytest.mark.parametrize(
    "definition",
    [
        "---\nid: w\nschema_version: 1\nstages:\n  - id: s\n    exit: [no-such-check]\n---\n",  # invalid
        None,  # removed
    ],
)
def test_envelope_new_does_not_need_the_definition(tmp_path: Path, definition: str | None) -> None:
    root = simple_workspace(tmp_path)
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    path = root / ".devkit/workflows/w.md"
    if definition is None:
        path.unlink()
    else:
        path.write_text(definition)
    assert run_cli("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint").exit_code == 2
    result = run_cli(
        "envelope", "review", "-w", str(root), "--unit", SIMPLE_UNIT, "--summary", "ok",
        "--format", "json",
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["file"] == "envelopes/review-01.yaml"
    data = yaml.safe_load((root / SIMPLE_UNIT / "envelopes/review-01.yaml").read_text())
    assert (data["workflow"], data["segment"]) == ("w", 0)


def test_envelope_new_still_needs_one_anchor(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    (root / ".devkit/workflows/p.md").write_text(
        "---\nid: p\nschema_version: 1\nlayout:\n  anchor: proposal.md\nstages:\n  - id: s\n    exit: [anchor-exists]\n---\n"
    )
    assert run_cli("new", "-w", str(root), "u").exit_code == 0
    (root / SIMPLE_UNIT / "proposal.md").write_text("---\nid: u\nworkflow: p\n---\n")
    args = ("envelope", "new", "-w", str(root), "--unit", SIMPLE_UNIT, "--kind", "report")
    ambiguous = run_cli(*args)
    assert ambiguous.exit_code == 2 and "(ANCHOR_AMBIGUOUS)" in ambiguous.stderr
    chosen = run_cli(*args, "--anchor", "proposal.md")
    assert chosen.exit_code == 0, chosen.output
    assert "workflow: p\n" in (root / SIMPLE_UNIT / "envelopes/report-01.yaml").read_text()
