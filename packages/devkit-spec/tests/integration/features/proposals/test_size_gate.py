"""The XL size gate before Planning (``SPEC-backlog-subagent-roles``): one predicate, ``size`` absent or exactly S, M
or L, checked by the ``sdd-proposal`` exit, ``accept --direct`` and the ``plan-`` attach check."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner, Result
from devkit_agt.features.workflow import Workspace, load_decisions, record_answer
from devkit_dist.cli import cli as devkit_cli
from spec_support.proposals import TODAY, write_workflow
from spec_support.scope import git, write

import devkit_spec
from devkit_spec.features.proposals import create_proposal
from devkit_spec.features.proposals.models.axes import size_blocker

DEFINITION = (
    Path(devkit_spec.__file__).parent / "bundles" / "spec" / "bundle" / "workflows" / "sdd-proposal.md"
).read_text(encoding="utf-8")
UNIT = "docs/proposals/PROP-wide"
SCAFFOLDED = "size: M "


def _repo(tmp_path: Path, policy: str = "ask") -> Path:
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    write(root, ".devkit/config.toml", f'[workflow.approvals]\nplan-intent = "{policy}"\n')
    write_workflow(root, "sdd-proposal", DEFINITION)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "init")
    return root


def _draft(root: Path, size: str | None) -> Path:
    """A bound draft with ``size`` replaced (``None``: the line removed); returns proposal.md."""
    proposal = root / create_proposal(root, "wide", today=TODAY).path
    lines = proposal.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [line for line in lines if not line.startswith(SCAFFOLDED)]
    assert len(kept) == len(lines) - 1
    if size is not None:
        kept.insert(lines.index(next(line for line in lines if line.startswith(SCAFFOLDED))), f"size: {size}\n")
    proposal.write_text("".join(kept), encoding="utf-8")
    return proposal


def _run(root: Path, *args: str) -> Result:
    return CliRunner().invoke(devkit_cli, [*args, "-w", str(root)])


@pytest.mark.parametrize(
    ("meta", "blocked"),
    [
        ({}, None),
        ({"size": None}, None),
        ({"size": ""}, None),
        ({"size": "S"}, None),
        ({"size": "M"}, None),
        ({"size": "L"}, None),
        ({"size": "XL"}, "size: XL"),
        ({"size": "xl"}, "size: xl"),
        ({"size": "m"}, "size: m"),
        ({"size": 3}, "size: 3"),
    ],
)
def test_one_size_predicate(meta: dict[str, Any], blocked: str | None) -> None:
    assert size_blocker(meta) == blocked


@pytest.mark.parametrize("policy", ["ask", "auto"])
@pytest.mark.parametrize("size", ["XL", "xl"])
def test_an_xl_draft_leaves_plan_intent_unmet_at_next(tmp_path: Path, policy: str, size: str) -> None:
    root = _repo(tmp_path, policy)
    _draft(root, size)
    result = _run(root, "workflow", "next", "--unit", UNIT)
    assert result.exit_code == 0, result.output
    assert "[STAGE: intent-proposal " in result.stdout
    assert "[UNMET: frontmatter(proposal.md size S|M|L|)" in result.stdout
    assert f'detail="size={size}"' in result.stdout
    assert "[REQUEST: id=gate:plan-intent" not in result.stdout
    assert "[GATE_PASSED: plan-intent" not in result.stdout


@pytest.mark.parametrize("policy", ["ask", "auto"])
@pytest.mark.parametrize("size", [None, "L"])
def test_an_absent_or_l_size_opens_the_request(tmp_path: Path, policy: str, size: str | None) -> None:
    root = _repo(tmp_path, policy)
    _draft(root, size)
    result = _run(root, "workflow", "next", "--unit", UNIT)
    assert result.exit_code == 0, result.output
    assert "frontmatter(proposal.md size" not in result.stdout
    if policy == "ask":
        assert "[REQUEST: id=gate:plan-intent " in result.stdout
    else:
        assert "[GATE_PASSED: plan-intent stage=intent-proposal policy=auto" in result.stdout


def test_plan_intent_cannot_be_recorded_for_an_xl_draft(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _draft(root, "XL")
    result = _run(
        root, "workflow", "answer", "--unit", UNIT, "--request", "gate:plan-intent", "--action", "accept",
        "--by", "user", "--format", "json",
    )  # fmt: skip
    assert result.exit_code == 2, result.output
    assert json.loads(result.stdout)["error"]["code"] == "REQUEST_UNKNOWN"
    assert not load_decisions(root / UNIT).records


def _accept_check(root: Path) -> Result:
    return _run(root, "spec", "proposal", "accept", "wide", "--by", "user", "--direct", "--check", "--note", "x",
                "--format", "json")  # fmt: skip


def test_a_direct_acceptance_check_names_the_size_blocker(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    proposal = _draft(root, "L")
    ws = Workspace(root, lint=None, ancestor=None)
    record_answer(ws, ws.resolve_unit(UNIT), "gate:plan-intent", "accept", by="user", lint=False)
    assert "size:" not in _accept_check(root).stdout
    proposal.write_text(proposal.read_text(encoding="utf-8").replace("size: L\n", "size: XL\n"), encoding="utf-8")
    result = _accept_check(root)
    assert result.exit_code == 2, result.output
    error = json.loads(result.stdout)["error"]
    assert error["code"] == "SPEC_PROPOSAL_NOT_ELIGIBLE"
    details = error["advisory"]["details"]
    assert (
        "blocking: size: XL (decompose first: split with --decomposed-from or promote to a milestone;"
        " allowed: S, M, L or absent)"
    ) in details, details
