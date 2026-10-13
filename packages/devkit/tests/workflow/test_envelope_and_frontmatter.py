from __future__ import annotations

from pathlib import Path

import pytest
from devkit.workflow import Binding, load_envelopes, read_binding, write_binding
from devkit.workflow.unit import frontmatter as fm
from devkit.workflow.unit.envelope import skeleton, write_envelope

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
    out = fm.update(text, {"workflow": "new", "workflow_hash": "sha256:abc"})
    assert (
        out == "---\nid: x\nmeta:\n  workflow: nested\n# comment\nworkflow: new\nworkflow_hash: sha256:abc\n---\nbody\n"
    )


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
    write_binding(anchor, Binding("wf", "sha256:1"))
    assert read_binding(anchor) == Binding("wf", "sha256:1")
    assert anchor.read_text().startswith(
        "---\nid: a\nstatus: planned\nworkflow: wf\nworkflow_hash: sha256:1\n---\n# a\n"
    )
    write_binding(anchor, Binding("wf", "sha256:2"))
    assert anchor.read_text().count("workflow_hash") == 1


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
