"""Handoff validates a projected graph before mutation and preserves direct edges."""

import subprocess
from pathlib import Path

import pytest
from devkit.core.frontmatter import parse
from proposals.support import TODAY, accept

from devkit_spec.errors import ProposalInvalidError, ProposalSlugConflictError
from devkit_spec.proposals import create_proposal, handoff_proposal


def snapshot(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def setup(root: Path, edges: str) -> None:
    anchor = root / create_proposal(root, "child").path
    accept(anchor, "\n" + edges)
    subprocess.run(["git", "-C", str(root), "init", "-q", "-b", "dev-child"], check=True)


@pytest.mark.parametrize(
    "edges",
    [
        "depends_on: [PROP-child]",
        "depends_on: [PROP-missing]",
        "depends_on: bad",
        "depends_on: [1]",
        "depends_on: [MS-theme]",
    ],
)
def test_invalid_graph_refuses_without_writes(workspace: Path, edges: str) -> None:
    setup(workspace, edges)
    before = snapshot(workspace)
    with pytest.raises(ProposalInvalidError):
        handoff_proposal(workspace, "child", today=TODAY)
    assert snapshot(workspace) == before


def test_carry_rewrite_namespaced_and_preserve_history(workspace: Path, write) -> None:
    setup(workspace, "depends_on: [SPEC-done]")
    write("specs/2026-10/done/spec.md", "---\nid: SPEC-done\nstatus: completed\ndepends_on: [PROP-child]\n---\n")
    incoming = write(
        "docs/packages/pkg/proposals/PROP-next/proposal.md",
        "---\nid: PROP-next\nstatus: draft\ndepends_on: [PROP-child]\n---\n",
    )
    result = handoff_proposal(workspace, "child", today=TODAY)
    data = parse((workspace / result.dir / "spec.md").read_text()).data
    assert data is not None and data["depends_on"] == ["SPEC-done"]
    assert "depends_on: [SPEC-child]" in incoming.read_text()
    assert "depends_on: [PROP-child]" in (workspace / "specs/2026-10/done/spec.md").read_text()


def test_projected_mixed_cycle_and_collision(workspace: Path, write) -> None:
    setup(workspace, "depends_on: [SPEC-live]")
    write("specs/2026-10/live/spec.md", "---\nid: SPEC-live\nstatus: in-progress\ndepends_on: [PROP-child]\n---\n")
    before = snapshot(workspace)
    with pytest.raises(ProposalInvalidError):
        handoff_proposal(workspace, "child", today=TODAY)
    assert snapshot(workspace) == before
    write("specs/2026-10/child/spec.md", "---\nid: SPEC-child\nstatus: planned\n---\n")
    before = snapshot(workspace)
    with pytest.raises(ProposalSlugConflictError):
        handoff_proposal(workspace, "child", today=TODAY)
    assert snapshot(workspace) == before
