from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from click.testing import CliRunner, Result
from devkit_dist.cli import cli as devkit_cli
from spec_support.proposals import GATED, INCUBATED, accept, write_workflow
from spec_support.types import Write


def _proposal(workspace: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, ["spec", "proposal", *args, "-w", str(workspace)])


def test_new_and_padr(workspace: Path) -> None:
    result = _proposal(workspace, "new", "Fast Engine", "--title", "Fast: Engine", "--with-target-docs")
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "[PROPOSAL: PROP-fast-engine path=docs/proposals/PROP-fast-engine/proposal.md "
        "dir=docs/proposals/PROP-fast-engine target_docs=docs/proposals/PROP-fast-engine/target-docs.md "
        "workflow=- planning_effort=medium dev_effort=medium]"
    ]
    assert "(SPEC_PROPOSAL_UNBOUND)" in result.stderr
    result = _proposal(workspace, "padr", "fast-engine", "Use AST parser")
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "[PADR: PADR-use-ast-parser path=docs/proposals/PROP-fast-engine/decisions/PADR-use-ast-parser.md "
        "proposal=PROP-fast-engine]"
    ]
    result = _proposal(workspace, "padr", "fast-engine", "Use AST parser", "--format", "json")
    assert result.exit_code == 2 and result.stderr == ""
    assert json.loads(result.stdout)["error"]["code"] == "SPEC_PADR_EXISTS"


def test_padr_slug_option(workspace: Path) -> None:
    _proposal(workspace, "new", "plans")
    result = _proposal(workspace, "padr", "plans", "2024 roadmap", "--slug", "roadmap-2024")
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "[PADR: PADR-roadmap-2024 path=docs/proposals/PROP-plans/decisions/PADR-roadmap-2024.md proposal=PROP-plans]"
    ]


def test_new_json(workspace: Path) -> None:
    result = _proposal(workspace, "new", "lean", "--planning-effort", "low", "--dev-effort", "high", "--format", "json")
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert {
        key: payload[key]
        for key in (
            "id",
            "dir",
            "path",
            "target_docs",
            "workflow",
            "planning_effort",
            "dev_effort",
            "next_command",
        )
    } == {
        "id": "PROP-lean",
        "dir": "docs/proposals/PROP-lean",
        "path": "docs/proposals/PROP-lean/proposal.md",
        "target_docs": None,
        "workflow": None,
        "planning_effort": "low",
        "dev_effort": "high",
        "next_command": None,
    }
    assert [notice["code"] for notice in payload["notices"]] == ["SPEC_PROPOSAL_UNBOUND"]


def test_new_binds_the_proposal_and_workflow_next_runs(workspace: Path) -> None:
    write_workflow(workspace, "sdd-proposal", INCUBATED)
    result = _proposal(workspace, "new", "bound", "--task-kind", "bugfix")
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "[PROPOSAL: PROP-bound path=docs/proposals/PROP-bound/proposal.md dir=docs/proposals/PROP-bound "
        "target_docs=- workflow=sdd-proposal planning_effort=medium dev_effort=medium]",
        "[NEXT_CMD: uv run devkit workflow next --unit docs/proposals/PROP-bound]",
    ]
    assert result.stderr == ""
    result = CliRunner().invoke(
        devkit_cli,
        ["workflow", "next", "--unit", "docs/proposals/PROP-bound", "-w", str(workspace), "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["workflow"] == "sdd-proposal" and payload["bound"] is True, payload


def test_handoff_refuses_an_unapproved_proposal(workspace: Path) -> None:
    _proposal(workspace, "new", "draft-one")
    result = _proposal(workspace, "handoff", "draft-one")
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "(SPEC_PROPOSAL_NOT_APPROVED)" in result.stderr
    assert (workspace / "docs/proposals/PROP-draft-one/proposal.md").is_file()


def test_handoff_text(workspace: Path, write: Write) -> None:
    write_workflow(workspace, "sdd-spec-feature")
    _proposal(workspace, "new", "shipit")
    _proposal(workspace, "padr", "shipit", "Pick")
    write("docs/proposals/PROP-shipit/materials/m.md", "[up](../proposal.md)\n")
    write("docs/usecases/UC-a.md", "---\nid: UC-a\n---\n[PROP-shipit] [gone](../proposals/PROP-shipit/decisions/)\n")
    accept(workspace / "docs/proposals/PROP-shipit/proposal.md")

    result = _proposal(workspace, "handoff", "shipit")

    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    head = lines[0]
    assert head.startswith("[HANDOFF: PROP-shipit spec=SPEC-shipit dir=specs/") and head.endswith(
        " workflow=sdd-spec-feature dev_effort=medium]"
    )
    spec_dir = head.split(" dir=")[1].split(" ")[0]
    month, bundle = spec_dir.split("/")[1:]
    stamp = bundle.split("-")[0]
    assert lines[1] == f"[MATERIALS: docs/materials/{month}/{stamp}-shipit]"
    assert lines[2] == f"[PROMOTED_ADR: ADR-pick path=docs/decisions/{month}/{stamp}-pick.md padr=PADR-pick]"
    assert "[REWRITTEN: docs/usecases/UC-a.md:4 kind=id from=PROP-shipit to=SPEC-shipit]" in lines
    assert (
        f"[REWRITTEN: docs/materials/{month}/{stamp}-shipit/m.md:1 kind=link from=../proposal.md "
        f"to=../../../../{spec_dir}/spec.md]"
    ) in lines
    assert (
        "[UNRESOLVED_LINK: docs/usecases/UC-a.md:4 kind=link target=../proposals/PROP-shipit/decisions/ reason=unmapped]"
        in lines
    )
    assert lines[-1] == f"[NEXT_CMD: uv run devkit workflow next --unit {spec_dir}]"
    assert "(SPEC_PROPOSAL_LINK_UNRESOLVED)" in result.stderr
    assert "(SPEC_PROPOSAL_REFS_REWRITTEN)" in result.stderr
    assert not (workspace / "docs/proposals/PROP-shipit").exists()


def _accept(workspace: Path, slug: str) -> None:
    proposal = workspace / f"docs/proposals/PROP-{slug}/proposal.md"
    proposal.write_text(proposal.read_text(encoding="utf-8").replace("status: draft", "status: accepted", 1), "utf-8")


def test_handoff_strict_fails_on_the_unresolved_link_warning(workspace: Path, write: Write) -> None:
    _proposal(workspace, "new", "strict")
    _accept(workspace, "strict")
    write("docs/usecases/UC-a.md", "[gone](../proposals/PROP-strict/decisions/)\n")
    result = _proposal(workspace, "handoff", "strict", "--strict")
    assert result.exit_code == 1
    assert result.stdout.startswith("[HANDOFF: PROP-strict ")


def test_handoff_json(workspace: Path) -> None:
    _proposal(workspace, "new", "jsonic")
    _accept(workspace, "jsonic")
    result = _proposal(workspace, "handoff", "jsonic", "--format", "json")
    assert result.exit_code == 0 and result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["proposal"] == "PROP-jsonic" and payload["spec"] == "SPEC-jsonic"
    assert payload["workflow"] is None and payload["next_command"] is None
    assert [notice["code"] for notice in payload["notices"]] == ["SPEC_PROPOSAL_UNBOUND"]
    assert set(payload) >= {"decisions", "rewritten", "rewritten_files", "unresolved", "materials", "target_docs"}
    assert payload["dropped_records"] == [] and payload["carried_gates"] == []
    assert payload["materials_merged"] is False and payload["dropped_duplicates"] == []


def _merge_into_existing(workspace: Path, write: Write, slug: str) -> str:
    """An accepted proposal whose dated materials directory already holds a file and a duplicate; returns it."""
    _proposal(workspace, "new", slug)
    _accept(workspace, slug)
    today = date.today()
    dest = f"docs/materials/{today:%Y-%m}/{today:%Y%m%d}-{slug}"
    write(f"{dest}/bench.json", "{}\n")
    write(f"{dest}/same.md", "# Same\n")
    write(f"docs/proposals/PROP-{slug}/materials/design.md", "# Design\n")
    write(f"docs/proposals/PROP-{slug}/materials/same.md", "# Same\n")
    return dest


def test_handoff_text_reports_a_merge(workspace: Path, write: Write) -> None:
    dest = _merge_into_existing(workspace, write, "merged")
    result = _proposal(workspace, "handoff", "merged")
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert lines[1:3] == [f"[MATERIALS: {dest} merged=yes]", f"[DROPPED_DUPLICATE: {dest}/same.md]"]
    assert "(SPEC_PROPOSAL_UNBOUND)" in result.stderr and result.stderr.count("(SPEC_") == 1  # no merge notice


def test_handoff_json_reports_a_merge(workspace: Path, write: Write) -> None:
    dest = _merge_into_existing(workspace, write, "merged-json")
    result = _proposal(workspace, "handoff", "merged-json", "--format", "json")
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["materials"] == dest and payload["materials_merged"] is True
    assert payload["dropped_duplicates"] == [f"{dest}/same.md"]
    assert [notice["code"] for notice in payload["notices"]] == ["SPEC_PROPOSAL_UNBOUND"]


def test_handoff_refuses_a_merge_conflict(workspace: Path, write: Write) -> None:
    dest = _merge_into_existing(workspace, write, "conflict")
    write("docs/proposals/PROP-conflict/materials/bench.json", "[]\n")
    result = _proposal(workspace, "handoff", "conflict", "--format", "json")
    assert result.exit_code == 2
    error = json.loads(result.stdout)["error"]
    assert error["code"] == "SPEC_PROPOSAL_TARGET_EXISTS"
    assert error["advisory"]["fix"].startswith(
        f"Reconcile docs/proposals/PROP-conflict/materials/bench.json with the existing {dest}/bench.json"
        " (different-content):"
    )
    assert (workspace / "docs/proposals/PROP-conflict/proposal.md").is_file()


def test_handoff_reports_dropped_records_and_carried_gates(workspace: Path) -> None:
    write_workflow(workspace, "sdd-proposal", INCUBATED)
    write_workflow(workspace, "sdd-spec-feature", GATED.format(id="sdd-spec-feature", middle=""))
    _proposal(workspace, "new", "gated")
    unit = "docs/proposals/PROP-gated"
    (workspace / unit / "decisions").mkdir(exist_ok=True)
    (workspace / unit / "decisions/01-gate-plan-accept.yaml").write_text(
        "request: gate:plan-accept\nkind: approve\naction: accept\nworkflow: sdd-proposal\n"
        "stage: direction-handoff\nby: user\nat: '2026-10-13T00:00:00Z'\n",
        encoding="utf-8",
    )
    _accept(workspace, "gated")

    result = _proposal(workspace, "handoff", "gated")

    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    spec_dir = lines[0].split(" dir=")[1].split(" ")[0]
    assert lines[1:3] == [
        f"[DROPPED_RECORD: {unit}/decisions/01-gate-plan-accept.yaml]",
        f"[CARRIED_GATE: gate:plan-accept decision={spec_dir}/decisions/01-gate-plan-accept.yaml]",
    ]
    assert result.stderr == ""
