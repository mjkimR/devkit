"""Milestones remain discoverable history and provenance survives source deletion."""

from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.cli import cli

from devkit_docs.features.documents import DocumentIndex, parse_document
from devkit_docs.features.documents.models.ids import Kind


def test_milestone_history_and_current_incoming_members(workspace: Path, write) -> None:
    write("docs/roadmap/MS-old.md", "---\nid: MS-old\nstatus: done\n---\n")
    write("docs/roadmap/MS-next.md", "---\nid: MS-next\nstatus: planned\ndepends_on: [MS-old]\n---\n")
    write("docs/proposals/PROP-x/proposal.md", "---\nid: PROP-x\nstatus: draft\nmilestone: MS-old\n---\n")
    index = DocumentIndex.load(workspace)
    old = index.resolve("MS-old")
    assert old.kind is Kind.MILESTONE and index.is_historical(old)
    assert not index.is_historical(index.resolve("MS-next"))
    assert set(index.incoming("MS-old")) == {"MS-next", "PROP-x"}
    runner = CliRunner()
    listed = runner.invoke(cli, ["docs", "list", "milestone", "-w", str(workspace)])
    assert listed.exit_code == 0 and "[DOCUMENT: MS-next" in listed.stdout and "[DOCUMENT: MS-old" not in listed.stdout
    history = runner.invoke(cli, ["docs", "list", "milestone", "--history", "-w", str(workspace)])
    assert history.exit_code == 0 and "[DOCUMENT: MS-old" in history.stdout


def test_kind_scoped_fields_and_unresolved_provenance() -> None:
    document = parse_document("docs/a.md", "---\nid: CAP-A-a\nmilestone: MS-a\ndepends_on: []\n---\n")
    assert document is not None and len(document.issues) == 2 and document.references == []
    spec = parse_document(
        "specs/2026-10/20261018-a/spec.md", "---\nid: SPEC-a\ndecomposed_from: PROP-gone\nsupersedes: PROP-old\n---\n"
    )
    assert spec is not None and spec.references == []
    assert [(ref.field, ref.target) for ref in spec.provenance] == [
        ("decomposed_from", "PROP-gone"),
        ("supersedes", "PROP-old"),
    ]


@pytest.mark.parametrize("status", ["done", "dropped"])
def test_archived_identity_refs_and_cli_history(workspace: Path, write, status: str) -> None:
    path = f"docs/roadmap/_archive/MS-old-{status}.md"
    identifier = f"MS-old-{status}"
    write(
        path,
        f"---\nid: {identifier}\naliases: [MS-alias]\ntitle: Archived history\nsummary: Archived history searchable marker.\nstatus: {status}\n---\n# [{identifier}] History\n",
    )
    write("docs/roadmap/MS-live.md", f"---\nid: MS-live\nstatus: active\ndepends_on: [{identifier}]\n---\n")
    write("docs/roadmap/_archive/MS-invalid.md", "---\nid: MS-invalid\nstatus: active\n---\n")
    index = DocumentIndex.load(workspace)
    assert index.resolve("MS-alias").path == path
    assert set(index.incoming(identifier)) == {"MS-live"}
    assert index.resolve("MS-invalid").path.endswith("_archive/MS-invalid.md")
    assert not index.is_historical(index.resolve("MS-invalid"))
    runner = CliRunner()

    def invoke(*args: str):
        result = runner.invoke(cli, ["docs", *args, "-w", str(workspace)])
        assert result.exit_code == 0, result.output
        return result.stdout

    assert path in invoke("resolve", "MS-alias")
    assert "MS-live" in invoke("refs", identifier, "--direction", "in")
    assert identifier not in invoke("list", "milestone")
    assert identifier in invoke("list", "milestone", "--status", status)
    assert identifier in invoke("list", "milestone", "--history")
    assert f"[HIT: {identifier} " not in invoke("search", identifier, "--mode", "lexical")
    assert f"[HIT: {identifier} " in invoke("search", identifier, "--mode", "lexical", "--history")
