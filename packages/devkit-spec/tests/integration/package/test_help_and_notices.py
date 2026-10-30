"""Help texts name every value and flag an agent may pass."""

from __future__ import annotations

from click.testing import CliRunner
from devkit_dist.cli import cli as devkit_cli


def _help(*args: str) -> str:
    result = CliRunner().invoke(devkit_cli, ["spec", *args, "--help"])
    assert result.exit_code == 0, result.output
    return " ".join(result.output.split())


def test_help_names_every_composed_flag() -> None:
    accept = _help("proposal", "accept")
    assert "accept_only" in accept and "Development activity-effort" in accept
    assert "Development activity-effort" in _help("proposal", "handoff")
    assert "update" not in _help("scope", "register")  # update is hidden


def test_proposal_help_names_planning() -> None:  # SPEC-rename-incubation-to-adaptive-dev AC-07
    assert "Plan proposals in docs/proposals/ and hand approved ones off to spec bundles." in _help("proposal")
