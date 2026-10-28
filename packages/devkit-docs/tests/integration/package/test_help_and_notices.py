"""Help texts name every value an agent may pass, and a failed lookup keeps the warnings it collected."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from devkit_dist.cli import cli as devkit_cli
from docs_support.types import Write


def _help(*args: str) -> str:
    result = CliRunner().invoke(devkit_cli, ["docs", *args, "--help"])
    assert result.exit_code == 0, result.output
    return " ".join(result.output.split())


def test_help_names_every_kind() -> None:
    assert "usecase, ux, architecture" in _help("list")


def test_a_failed_refs_lookup_keeps_the_collected_warnings(workspace: Path, write: Write) -> None:
    write("docs/capabilities/core/CAP-CORE-bad.md", "---\nid: [unclosed\n---\n")
    result = CliRunner().invoke(devkit_cli, ["docs", "refs", "NOPE", "-w", str(workspace), "--format", "json"])
    assert result.exit_code == 2
    document = json.loads(result.stdout)
    assert document["error"]["code"] == "DOCS_ID_UNRESOLVED"
    assert [notice["code"] for notice in document["notices"]] == ["DOCS_DOCUMENT_INVALID"]
    text = CliRunner().invoke(devkit_cli, ["docs", "refs", "NOPE", "-w", str(workspace)])
    assert text.stderr.index("DOCS_DOCUMENT_INVALID") < text.stderr.index("DOCS_ID_UNRESOLVED")
