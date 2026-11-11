"""Help texts name every value and flag an agent may pass."""

from __future__ import annotations

from click.testing import CliRunner
from devkit_dist.cli import cli as devkit_cli


def _help(*args: str) -> str:
    result = CliRunner().invoke(devkit_cli, ["spec", *args, "--help"])
    assert result.exit_code == 0, result.output
    return " ".join(result.output.split())


def test_help_names_every_composed_flag() -> None:
    # SPEC-split-composed-proposal-accept AC-04, AC-06: one operation and one option set per acceptance command.
    composed = _help("proposal", "accept-plan")
    for text in ("accept_only", "accept_and_handoff", "Development activity-effort", "--by [user|policy]"):
        assert text in composed
    assert "devkit spec proposal report" in composed and "devkit workflow envelope check" in composed
    assert "--check" not in composed and "--direct" not in composed and "--note" not in composed
    accept = _help("proposal", "accept")
    assert "--direct" in accept and "--check" in accept and "--note" in accept
    for text in ("--mode", "--effort", "accept_only", "accept_and_handoff"):
        assert text not in accept
    assert "accept-plan" in _help("proposal")
    assert "Development activity-effort" in _help("proposal", "handoff")
    assert "--mode" not in _help("scope", "collect") and "--base" in _help("scope", "collect")


def test_proposal_help_names_planning() -> None:  # SPEC-rename-incubation-to-adaptive-dev AC-07
    assert "Plan proposals in docs/proposals/ and hand approved ones off to spec bundles." in _help("proposal")
