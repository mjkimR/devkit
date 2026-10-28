"""Terminal statuses are historical in browsing and search (``SPEC-list-terminal-statuses-historical``)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit_dist.cli import cli as devkit_cli
from docs_support.types import Write

from devkit_docs.features.documents import DocumentIndex

FEEDBACK = ("open", "resolved", "promoted", "dismissed", "forwarded")


def _doc(document_id: str, **fields: str) -> str:
    header = "".join(f"{key}: {value}\n" for key, value in fields.items())
    return f"---\nid: {document_id}\n{header}---\nThe slow sync observation.\n"


def _spec(*args: str, workspace: Path) -> Result:
    return CliRunner().invoke(devkit_cli, ["docs", *args, "-w", str(workspace)])


def _ids(result: Result) -> list[str]:
    return [line.split()[1] for line in result.stdout.splitlines() if line.startswith("[DOCUMENT: ")]


@pytest.fixture
def settled(workspace: Path, write: Write) -> Path:
    for status in FEEDBACK:
        write(f"specs/2026-10/feedback/20261026-{status}.md", _doc(f"FB-{status}", status=status, title="Slow sync"))
    write("docs/decisions/2026-10/20261026-kept.md", _doc("ADR-kept", status="accepted"))
    write("docs/decisions/2026-10/20261026-old.md", _doc("ADR-old", status="Superseded"))
    write("docs/proposals/PROP-live/proposal.md", _doc("PROP-live", status="draft"))
    write("docs/proposals/PROP-no/proposal.md", _doc("PROP-no", status="rejected"))
    write("specs/2026-10/20261001-done/spec.md", _doc("SPEC-done", status="completed"))
    return workspace


def test_terminal_statuses_are_hidden_by_default(settled: Path) -> None:
    result = _spec("list", "feedback", "decision", "proposal", workspace=settled)
    assert result.exit_code == 0
    assert _ids(result) == ["ADR-kept", "PROP-live", "FB-open"]
    assert result.stdout.splitlines()[-2:] == [
        "[PAGE: total=3 offset=0 limit=20 count=3 next=- hidden=6]",
        f"[HISTORY_CMD: uv run devkit docs list feedback decision proposal --history -w {settled}]",
    ]


def test_history_shows_them(settled: Path) -> None:
    result = _spec("list", "feedback", "decision", "proposal", "--history", workspace=settled)
    assert result.exit_code == 0
    assert sorted(_ids(result)) == sorted(
        ["ADR-kept", "ADR-old", "PROP-live", "PROP-no", *(f"FB-{status}" for status in FEEDBACK)]
    )
    assert result.stdout.splitlines()[-1] == "[PAGE: total=9 offset=0 limit=20 count=9 next=- hidden=0]"


def test_a_listed_status_shows_its_documents_whatever_their_history(settled: Path) -> None:
    resolved = _spec("list", "feedback", "--status", "resolved", workspace=settled)
    assert _ids(resolved) == ["FB-resolved"]
    assert resolved.stdout.splitlines()[-1].endswith(" hidden=0]")
    completed = _spec("list", "spec", "--status", "completed", workspace=settled)
    assert _ids(completed) == ["SPEC-done"]
    assert completed.stdout.splitlines()[-1].endswith(" hidden=0]")


def test_the_page_reports_what_it_hid(settled: Path) -> None:
    result = _spec("list", "feedback", "-n", "0", workspace=settled)
    assert result.stdout.splitlines()[-2:] == [
        "[PAGE: total=1 offset=0 limit=0 count=1 next=- hidden=4]",
        f"[HISTORY_CMD: uv run devkit docs list feedback --history -w {settled} --limit 0]",
    ]
    payload = json.loads(_spec("list", "feedback", "--format", "json", workspace=settled).stdout)
    assert payload["total"] == 1 and payload["hidden"] == 4
    assert [d["historical"] for d in payload["documents"]] == [False]


def test_no_hint_without_hidden_documents(workspace: Path, write: Write) -> None:
    write("specs/2026-10/feedback/20261026-open.md", _doc("FB-open", status="open"))
    result = _spec("list", "feedback", workspace=workspace)
    assert result.stdout.splitlines()[-1] == "[PAGE: total=1 offset=0 limit=20 count=1 next=- hidden=0]"
    assert "[HISTORY_CMD:" not in result.stdout


def test_every_kind_selection_and_search_follow_the_rule(settled: Path) -> None:
    listed = _spec("list", workspace=settled)
    assert sorted(_ids(listed)) == ["ADR-kept", "FB-open", "PROP-live"]
    assert listed.stdout.splitlines()[-2].endswith(" hidden=7]")
    found = _spec(
        "search", "slow", "sync", "--kind", "feedback", "--mode", "lexical", "--format", "json", workspace=settled
    )
    assert [hit["id"] for hit in json.loads(found.stdout)["hits"]] == ["FB-open"]
    every = _spec(
        "search",
        "slow",
        "sync",
        "--kind",
        "feedback",
        "--mode",
        "lexical",
        "--history",
        "--format",
        "json",
        workspace=settled,
    )
    assert sorted(hit["id"] for hit in json.loads(every.stdout)["hits"]) == sorted(f"FB-{s}" for s in FEEDBACK)


def test_historical_ids_stay_resolvable(settled: Path) -> None:
    result = _spec("resolve", "ADR-old", workspace=settled)
    assert result.exit_code == 0
    assert result.stdout.startswith("[DOCUMENT: ADR-old kind=decision status=Superseded ")


def test_terminal_documents_stay_out_of_the_rules_history(settled: Path) -> None:
    index = DocumentIndex.load(settled)
    old = index.resolve("ADR-old")
    assert index.is_terminal(old) and index.is_browsing_historical(old)
    assert not index.is_historical(old)
