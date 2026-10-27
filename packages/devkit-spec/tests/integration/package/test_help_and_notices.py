"""Help texts name every value and flag an agent may pass, and a failed lookup keeps the warnings it collected."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from devkit_dist.cli import cli as devkit_cli
from spec_support.types import Write


def _help(*args: str) -> str:
    result = CliRunner().invoke(devkit_cli, ["spec", *args, "--help"])
    assert result.exit_code == 0, result.output
    return " ".join(result.output.split())


def test_help_names_every_kind_and_composed_flag() -> None:
    assert "usecase, ux, architecture" in _help("list")
    accept = _help("proposal", "accept")
    assert "accept_only" in accept and "Development activity-effort" in accept
    assert "Development activity-effort" in _help("proposal", "handoff")
    assert "update" not in _help("scope", "register")  # update is hidden


def test_a_failed_refs_lookup_keeps_the_collected_warnings(workspace: Path, write: Write) -> None:
    write("docs/capabilities/core/CAP-CORE-bad.md", "---\nid: [unclosed\n---\n")
    result = CliRunner().invoke(devkit_cli, ["spec", "refs", "NOPE", "-w", str(workspace), "--format", "json"])
    assert result.exit_code == 2
    document = json.loads(result.stdout)
    assert document["error"]["code"] == "SPEC_ID_UNRESOLVED"
    assert [notice["code"] for notice in document["notices"]] == ["SPEC_DOCUMENT_INVALID"]
    text = CliRunner().invoke(devkit_cli, ["spec", "refs", "NOPE", "-w", str(workspace)])
    assert text.stderr.index("SPEC_DOCUMENT_INVALID") < text.stderr.index("SPEC_ID_UNRESOLVED")
