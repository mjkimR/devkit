"""Per-definition layouts, the [workflow.stages] table and envelope authoring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner, Result
from devkit_agt.features.workflow import (
    LayoutError,
    LayoutSpec,
    WorkflowConfigError,
    load_workflow_config,
    parse_definition,
    parse_layout_spec,
)
from devkit_agt.features.workflow.cli import cli
from devkit_agt.features.workflow.models.errors import AuthoringError, DefinitionError
from devkit_agt.features.workflow.services.definition.validation import validate_definition
from devkit_agt.features.workflow.services.envelope import compose_envelope, load_envelopes, render_envelope
from testsupport.workflow import WORKFLOW, write_config, write_unit

PROPOSAL = """---
id: incubate
schema_version: 1
layout:
  work_dir: docs/proposals
  unit_path: "{slug}"
  anchor: proposal.md
stages:
  - id: draft
    exit: [anchor-exists, frontmatter(proposal.md status accepted)]
    skills: [wf-draft]
next:
  - { workflow: direct-delivery, recommended: true }
---
"""


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


@pytest.fixture
def two_layouts(workspace: Path) -> Path:
    (workspace / ".devkit/workflows/incubate.md").write_text(PROPOSAL, encoding="utf-8")
    write_config(
        workspace,
        """[workflow]
work_dir = "specs"
unit_path = "{date:%Y-%m}/{date:%Y%m%d}-{slug}"
anchor = "spec.md"
default = "direct-delivery"

[workflow.approvals]
direction = "auto"
""",
    )
    return workspace


# --- layout spec ------------------------------------------------------------------


def test_parse_layout_spec_partial_and_errors() -> None:
    assert parse_layout_spec({"anchor": "spec.md"}) == LayoutSpec(anchor="spec.md")
    assert parse_layout_spec({"work_dir": "docs/proposals/", "unit_path": "{slug}"}) == LayoutSpec(
        "docs/proposals", "{slug}", None
    )
    for raw, match in [
        ([], "expected a mapping"),
        ({"bogus": 1}, "unknown keys"),
        ({"work_dir": "/abs"}, "layout.work_dir"),
        ({"unit_path": "{ticket}"}, "layout.unit_path"),
        ({"anchor": "a/b.md"}, "layout.anchor"),
    ]:
        with pytest.raises(LayoutError, match=match):
            parse_layout_spec(raw)


def test_definition_layout_is_parsed_and_validated() -> None:
    doc = parse_definition(PROPOSAL)
    assert doc.layout == LayoutSpec("docs/proposals", "{slug}", "proposal.md")
    assert doc.anchor("task.md") == "proposal.md" and parse_definition(WORKFLOW).anchor("task.md") == "task.md"
    assert doc.to_dict()["layout"] == {"work_dir": "docs/proposals", "unit_path": "{slug}", "anchor": "proposal.md"}
    # aliases resolve against the declared anchor, so anchor-exists is valid without the project anchor
    assert validate_definition(doc, "task.md", known_ids={"incubate", "direct-delivery"}) == []
    same = parse_definition(PROPOSAL.replace("anchor: proposal.md", "anchor: other.md"))
    assert same.anchor("task.md") == "other.md"
    with pytest.raises(DefinitionError, match=r"layout\.unit_path"):
        parse_definition(PROPOSAL.replace('unit_path: "{slug}"', 'unit_path: "{nope}"'))


def test_stage_id_grammar_is_validated() -> None:
    doc = parse_definition(WORKFLOW.replace("id: build-verify", "id: Build_Verify"))
    assert any("must match" in str(p) and p.where == "Build_Verify.id" for p in validate_definition(doc, "task.md"))
    newline = parse_definition(WORKFLOW.replace("human_gate: integration", 'human_gate: "integration\\n"'))
    assert any(p.where == "integrate.human_gate" for p in validate_definition(newline, "task.md"))


# --- CLI across two layouts ------------------------------------------------------------


def test_new_list_next_bind_across_layouts(two_layouts: Path) -> None:
    root = two_layouts
    spec = _run("new", "-w", str(root), "login", "--date", "2026-10-12")
    assert spec.output.strip() == "[UNIT: specs/2026-10/20261012-login workflow=direct-delivery anchor=spec.md]"
    prop = _run("new", "-w", str(root), "search", "--workflow", "incubate")
    assert prop.output.strip() == "[UNIT: docs/proposals/search workflow=incubate anchor=proposal.md]"
    assert (root / "docs/proposals/search/proposal.md").is_file()

    listed = json.loads(_run("list", "-w", str(root), "--format", "json").stdout)["units"]
    assert [(r["unit"], r["anchor"], r["workflow"]) for r in listed] == [
        ("docs/proposals/search", "proposal.md", "incubate"),
        ("specs/2026-10/20261012-login", "spec.md", "direct-delivery"),
    ]
    text = _run("list", "-w", str(root)).output
    assert "[UNIT: docs/proposals/search status=planned workflow=incubate anchor=proposal.md]" in text

    nxt = _run("next", "-w", str(root), "--unit", "docs/proposals/search", "--no-lint")
    assert nxt.exit_code == 0, nxt.output
    assert "[WORKFLOW: incubate unit=docs/proposals/search status=planned bound=yes]" in nxt.output
    assert "[STAGE: draft" in nxt.output and "frontmatter(proposal.md status accepted)" in nxt.output

    bound = _run("bind", "-w", str(root), "--unit", "docs/proposals/search")
    assert bound.exit_code == 0 and bound.output.startswith("[BOUND: incubate]")

    show = _run("show", "-w", str(root), "incubate")
    assert "[LAYOUT: work_dir=docs/proposals unit_path={slug} anchor=proposal.md]" in show.output
    assert json.loads(_run("show", "-w", str(root), "incubate", "--format", "json").stdout)["anchor"] == "proposal.md"

    empty = _run("list", "-w", str(root / ".devkit"))
    assert "[UNITS: none under" in empty.output


def test_anchor_ambiguous_and_mismatch(two_layouts: Path) -> None:
    root = two_layouts
    unit = write_unit(root, "docs/proposals/dup", anchor="proposal.md", extra="workflow: incubate\n")
    (unit / "spec.md").write_text("---\nid: dup\nstatus: planned\n---\n")
    ambiguous = _run("next", "-w", str(root), "--unit", "docs/proposals/dup", "--no-lint")
    assert ambiguous.exit_code == 2 and "(ANCHOR_AMBIGUOUS)" in ambiguous.stderr and "--anchor" in ambiguous.stderr
    explicit = _run("next", "-w", str(root), "--unit", "docs/proposals/dup", "--no-lint", "--workflow", "incubate")
    assert explicit.exit_code == 0 and "[WORKFLOW: incubate" in explicit.output

    # bound to a workflow whose anchor is not the file that identifies the unit
    write_unit(root, "specs/2026-10/20261012-x", anchor="spec.md", extra="workflow: incubate\n")
    mismatch = _run("next", "-w", str(root), "--unit", "specs/2026-10/20261012-x", "--no-lint")
    assert mismatch.exit_code == 2 and "(ANCHOR_MISMATCH)" in mismatch.stderr and "proposal.md" in mismatch.stderr
    missing = _run("next", "-w", str(root), "--unit", "specs/2026-10/20261012-x", "--workflow", "incubate")
    assert missing.exit_code == 2 and "(UNIT_NOT_FOUND) proposal.md not found" in missing.stderr


def test_handoff_refuses_a_candidate_with_another_anchor(two_layouts: Path) -> None:
    root = two_layouts
    _run("new", "-w", str(root), "search", "--workflow", "incubate")
    unit = root / "docs/proposals/search"
    (unit / "proposal.md").write_text((unit / "proposal.md").read_text().replace("status: planned", "status: accepted"))
    result = _run(
        "handoff", "-w", str(root), "--unit", "docs/proposals/search", "--no-lint", "--workflow", "direct-delivery"
    )
    assert result.exit_code == 2 and "(HANDOFF_LAYOUT_MISMATCH)" in result.stderr and "spec.md" in result.stderr
    assert "workflow: incubate" in (unit / "proposal.md").read_text()


# --- [workflow.stages] -------------------------------------------------------------------


def test_stages_table_parses_and_rejects_bad_entries(tmp_path: Path) -> None:
    write_config(tmp_path, '[workflow.stages]\ncollect-feedback = "off"\nreview = "on"\n')
    cfg = load_workflow_config(tmp_path)
    assert cfg.stages == {"collect-feedback": "off", "review": "on"}
    assert cfg.stage_policy("collect-feedback") == "off" and cfg.stage_policy("other") == "on"
    for body, match in [
        ('[workflow.stages]\nreview = "maybe"\n', "not one of on|off"),
        ('[workflow.stages]\n"Bad Id" = "off"\n', "stage ids match"),
        ("[workflow]\nstages = 1\n", "expected a table"),
    ]:
        write_config(tmp_path, body)
        with pytest.raises(WorkflowConfigError, match=match):
            load_workflow_config(tmp_path)


def test_cli_skips_off_stage_and_completes(workspace: Path) -> None:
    write_config(
        workspace,
        'schema = 1\n[workflow]\ndefault = "direct-delivery"\n[workflow.approvals]\ndirection = "auto"\n'
        'integration = "auto"\n[workflow.stages]\nbuild-verify = "off"\nreview = "off"\nunknown-stage = "off"\n',
    )
    _run("new", "-w", str(workspace), "login", "--status", "completed")
    unit = ".devkit/transient/work/login"
    nxt = _run("next", "-w", str(workspace), "--unit", unit, "--no-lint", "--given", "ci-passed")
    assert nxt.exit_code == 0, nxt.output
    assert "[SKIPPED: build-verify reason=stages.build-verify=off]" in nxt.output
    assert "[SKIPPED: review reason=stages.review=off]" in nxt.output
    assert "[STAGE: - complete=true]" in nxt.output
    show = _run("show", "-w", str(workspace), "direct-delivery")
    assert "[SKIP: review reason=stages.review=off]" in show.output
    data = json.loads(_run("show", "-w", str(workspace), "direct-delivery", "--format", "json").stdout)
    assert data["stages_off"] == ["build-verify", "review"]


# --- envelope authoring -------------------------------------------------------------------


def _draft(unit: Path, **kw: object) -> str:
    draft = compose_envelope(unit_dir=unit, envelopes=load_envelopes(unit), **kw)  # type: ignore[arg-type]
    return render_envelope(draft, "2026-10-12T00:00:00Z")


def test_compose_review_and_reverify_round_trip(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    findings = (
        "- issue: Null deref\n  evidence: a.py:3\n- issue: Slow path\n  evidence: b.py:9\n  suggested_action: cache\n"
    )
    body = _draft(
        unit,
        kind="review",
        stage="review",
        summary="two findings",
        findings_yaml=findings,
        checks=["tests=PASS 3/3", "lint=FAIL"],
        base="main",
        head="abc1234",
        assumptions=["CI is green"],
        unverified=["perf"],
    )
    data = yaml.safe_load(body)
    assert list(data) == [
        "kind",
        "stage",
        "created_at",
        "status",
        "summary",
        "findings",
        "assumptions",
        "unverified_areas",
        "checks",
        "diff_scope",
    ]
    assert data["status"] == "completed" and [f["resolution"] for f in data["findings"]] == ["open", "open"]
    assert data["checks"] == {"tests": "PASS 3/3", "lint": "FAIL"} and data["diff_scope"] == {
        "base": "main",
        "head": "abc1234",
    }
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text(body)
    loaded = load_envelopes(unit).latest("review")
    assert loaded is not None and loaded.open_findings() == 2 and loaded.assumptions == ("CI is green",)
    assert loaded.unverified_areas == ("perf",) and loaded.to_dict()["findings"][1]["suggested_action"] == "cache"

    reverify = yaml.safe_load(_draft(unit, kind="reverify", source="latest", resolve=["1"], waive=["2=accepted cost"]))
    assert reverify["review"] == "review-01.yaml"
    assert [f["resolution"] for f in reverify["findings"]] == ["resolved", "waived"]
    # The waiver reason has its own key; the finding's suggested action is kept.
    assert reverify["findings"][1]["waiver"] == "accepted cost"
    assert reverify["findings"][1]["suggested_action"] == "cache"
    (unit / "envelopes/reverify-01.yaml").write_text(yaml.safe_dump(reverify, sort_keys=False))
    decider = load_envelopes(unit).review_state()
    assert decider is not None and decider.kind == "reverify" and decider.open_findings() == 0

    # a later reverify carries from the deciding reverify, keeping the review round; `all` resolves every open one
    (unit / "envelopes/review-02.yaml").write_text(
        "kind: review\nstatus: completed\nfindings:\n  - {issue: c, evidence: d}\n"
    )
    again = yaml.safe_load(_draft(unit, kind="reverify", source="latest", resolve=["all"]))
    assert again["review"] == "review-02.yaml" and again["findings"][0]["resolution"] == "resolved"
    from_file = yaml.safe_load(_draft(unit, kind="reverify", source="envelopes/review-01.yaml"))
    assert from_file["review"] == "review-01.yaml" and len(from_file["findings"]) == 2


@pytest.mark.parametrize(
    ("kw", "code", "match"),
    [
        ({"kind": "review", "status": "maybe"}, "ENVELOPE_STATUS_INVALID", "not in"),
        ({"kind": "review", "resolve": ["1"]}, "ENVELOPE_FROM_INVALID", "need --from"),
        ({"kind": "review", "source": "latest"}, "ENVELOPE_FLAG_INVALID", "a reverify carries findings"),
        ({"kind": "reverify"}, "ENVELOPE_FROM_INVALID", "reverify needs --from"),
        ({"kind": "reverify", "source": "latest"}, "ENVELOPE_FROM_INVALID", "no review envelope"),
        ({"kind": "final-report", "checks": ["tests"]}, "ENVELOPE_FLAG_INVALID", "name=PASS|FAIL|SKIP"),
        ({"kind": "final-report", "checks": ["tests=ok"]}, "ENVELOPE_FLAG_INVALID", "must start with"),
        ({"kind": "reverify", "source": "latest", "waive": ["x"]}, "ENVELOPE_FLAG_INVALID", "finding-number"),
        ({"kind": "reverify", "source": "latest", "resolve": ["0"]}, "ENVELOPE_FLAG_INVALID", "finding number"),
        ({"kind": "review", "findings_yaml": "- issue: a\n"}, "ENVELOPE_FINDINGS_INVALID", "needs issue and evidence"),
        (
            {"kind": "review", "findings_yaml": "- {issue: a, evidence: b, resolution: resolved}\n"},
            "ENVELOPE_FLAG_INVALID",
            "close them in a reverify",
        ),
        (
            {"kind": "review", "findings_yaml": "- {issue: a, evidence: b, extra: 1}\n"},
            "ENVELOPE_FINDINGS_INVALID",
            "unknown keys",
        ),
        ({"kind": "review", "findings_yaml": "issue: [\n"}, "ENVELOPE_FINDINGS_INVALID", "yaml"),
        ({"kind": "review", "findings_yaml": "a: b\n"}, "ENVELOPE_FINDINGS_INVALID", "expected a YAML list"),
    ],
)
def test_compose_rejections(tmp_path: Path, kw: dict[str, object], code: str, match: str) -> None:
    unit = write_unit(tmp_path, "work/a")
    with pytest.raises(AuthoringError, match=match) as info:
        compose_envelope(unit_dir=unit, envelopes=load_envelopes(unit), **kw)  # type: ignore[arg-type]
    assert info.value.code == code


def test_compose_out_of_range_numbers(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "envelopes").mkdir()
    (unit / "envelopes/review-01.yaml").write_text(
        "kind: review\nstatus: completed\nfindings:\n  - {issue: a, evidence: b}\n"
    )
    for resolve, waive in ((["2"], []), ([], ["3=x"])):
        with pytest.raises(AuthoringError, match=r"1\.\.1") as caught:
            compose_envelope(
                unit_dir=unit,
                envelopes=load_envelopes(unit),
                kind="reverify",
                source="latest",
                resolve=resolve,
                waive=waive,
            )
        assert caught.value.code == "ENVELOPE_FLAG_INVALID"
    with pytest.raises(AuthoringError, match="file name must be") as caught:
        compose_envelope(unit_dir=unit, envelopes=load_envelopes(unit), kind="reverify", source="notes.yaml")
    assert caught.value.code == "ENVELOPE_FROM_INVALID"


def test_cli_envelope_new_authoring_and_check(workspace: Path, tmp_path: Path) -> None:
    write_config(workspace, 'schema = 1\n[workflow]\ndefault = "direct-delivery"\n')
    _run("new", "-w", str(workspace), "login")
    unit = ".devkit/transient/work/login"
    findings = tmp_path / "findings.yaml"
    findings.write_text("- issue: Null deref\n  evidence: a.py:3\n")
    review = _run(
        "envelope",
        "review",
        "-w",
        str(workspace),
        "--unit",
        unit,
        "--stage",
        "review",
        "--summary",
        "one finding",
        "--findings-file",
        str(findings),
        "--check",
        "tests=PASS 3/3",
    )
    assert review.exit_code == 0, review.output
    assert (
        review.output.strip()
        == f"[ENVELOPE: {unit}/envelopes/review-01.yaml kind=review seq=01 status=completed open_findings=1]"
    )
    stdin = CliRunner().invoke(
        cli,
        ["envelope", "new", "-w", str(workspace), "--unit", unit, "--kind", "scout", "--findings-file", "-"],
        input="- {issue: x, evidence: y}\n",
    )
    assert stdin.exit_code == 0 and "scout-01.yaml kind=scout seq=01 status=completed open_findings=1" in stdin.output

    reverify = _run(
        "envelope",
        "reverify",
        "-w",
        str(workspace),
        "--unit",
        unit,
        "--from",
        "latest",
        "--resolve",
        "1",
    )
    assert (
        reverify.exit_code == 0
        and "reverify-01.yaml kind=reverify seq=01 status=completed open_findings=0" in reverify.output
    )
    data = yaml.safe_load((workspace / unit / "envelopes/reverify-01.yaml").read_text())
    assert data["review"] == "review-01.yaml" and data["findings"][0]["resolution"] == "resolved"

    bad = _run("envelope", "review", "-w", str(workspace), "--unit", unit, "--status", "nope")
    assert bad.exit_code == 2 and "(ENVELOPE_STATUS_INVALID)" in bad.stderr
    unreadable = _run("envelope", "review", "-w", str(workspace), "--unit", unit, "--findings-file", "/nope.yaml")
    assert unreadable.exit_code == 2 and "(ENVELOPE_FLAG_INVALID)" in unreadable.stderr

    ok = _run("envelope", "check", "-w", str(workspace), "--unit", unit)
    assert ok.exit_code == 0, ok.output
    assert "[ENVELOPE: envelopes/review-01.yaml kind=review seq=01 status=completed open_findings=1]" in ok.output
    assert "[OK: 3 envelopes]" in ok.output
    as_json = json.loads(_run("envelope", "check", "-w", str(workspace), "--unit", unit, "--format", "json").stdout)
    assert [e["file"] for e in as_json["envelopes"]] == [
        "envelopes/reverify-01.yaml",
        "envelopes/review-01.yaml",
        "envelopes/scout-01.yaml",
    ]
    assert as_json["errors"] == []

    (workspace / unit / "envelopes/review-02.yaml").write_text("status: completed\n")
    broken = _run("envelope", "check", "-w", str(workspace), "--unit", unit)
    assert broken.exit_code == 1
    assert '[ENVELOPE_ERROR: envelopes/review-02.yaml "missing required key kind"]' in broken.output
    assert "(ENVELOPE_INVALID)" in broken.stderr and f"[TARGET] {unit}/envelopes/review-02.yaml" in broken.stderr
    assert "[OK:" not in broken.output
