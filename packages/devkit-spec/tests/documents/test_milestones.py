"""Milestones remain discoverable history and provenance survives source deletion."""

from pathlib import Path

from click.testing import CliRunner
from devkit.cli import cli

from devkit_spec.documents import DocumentIndex, parse_document
from devkit_spec.documents.ids import Kind


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
    listed = runner.invoke(cli, ["spec", "list", "milestone", "-w", str(workspace)])
    assert listed.exit_code == 0 and "[DOCUMENT: MS-next" in listed.stdout and "[DOCUMENT: MS-old" not in listed.stdout
    history = runner.invoke(cli, ["spec", "list", "milestone", "--history", "-w", str(workspace)])
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
