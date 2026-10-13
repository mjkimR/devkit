"""The commented settings template in ``<common-git-dir>/devkit.config``."""

from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from click.testing import CliRunner
from devkit.gate import BaseGate, GateContext, GateResult, Stage, load_gate_project
from devkit.gate.cli import cli
from devkit.gate.hooks import local_config
from testsupport.gate import deploy_gate, gate_source


def _install(repo: Path) -> str:
    result = CliRunner().invoke(cli, ["install", "-w", str(repo), "--python", sys.executable])
    assert result.exit_code == 0, result.output
    return result.output


def _config(repo: Path) -> Path:
    return repo / ".git/devkit.config"


def test_install_writes_a_commented_table_per_gate(repo: Path) -> None:
    deploy_gate(repo, gate_source())
    output = _install(repo)
    assert f"[CONFIG: template=created path={_config(repo)}]" in output
    text = _config(repo).read_text()
    assert tomllib.loads(text) == {}  # every line is a comment until the developer uncomments one
    assert local_config.mentioned_gates(text) == {"rules-staged", "message-nonempty", "team-block"}
    assert "# [gates.settings.team-block]\n# pre-commit gate, on by default: test gate\n" in text
    assert "# enabled = true\n# allow = false  # boolean\n" in text
    assert "# [gates.settings.message-nonempty]\n# commit-msg gate, on by default:" in text

    assert "[CONFIG: template=unchanged" in _install(repo)


def test_uncommented_lines_are_kept_and_take_effect(repo: Path) -> None:
    deploy_gate(repo, gate_source())
    _install(repo)
    path = _config(repo)
    edited = path.read_text().replace("# [gates.settings.team-block]", "[gates.settings.team-block]")
    edited = edited.replace("# allow = false", "allow = true")
    path.write_text(edited)

    assert "[CONFIG: template=unchanged" in _install(repo)
    assert path.read_text() == edited
    project = load_gate_project(repo)
    assert project.validation.errors == ()
    assert project.config.gates["team-block"].values == {"allow": True}


def test_post_sync_appends_only_new_gates(repo: Path) -> None:
    _install(repo)
    path = _config(repo)
    before = path.read_text().rstrip("\n")  # a file without a final newline still gets a separated table
    path.write_text(before)
    deploy_gate(repo, gate_source("second-gate", enabled=False, cls="SecondGate"), ".devkit/managed/team/gates/two.py")

    assert local_config.post_sync(repo, {}) is None
    text = path.read_text()
    assert text.startswith(before + "\n\n# [gates.settings.second-gate]\n")
    assert "# pre-commit gate, off by default: test gate\n# enabled = false\n" in text
    assert text.count("[gates.settings.rules-staged]") == 1


def test_post_sync_leaves_repositories_without_managed_hooks_alone(repo: Path, tmp_path: Path) -> None:
    assert local_config.post_sync(repo, {}) is None
    assert not _config(repo).exists()
    outside = tmp_path / "outside"
    outside.mkdir()
    assert local_config.post_sync(outside, {}) is None


def test_a_symlinked_config_is_skipped_with_a_warning(repo: Path, tmp_path: Path) -> None:
    target = tmp_path / "elsewhere.toml"
    target.write_text("# mine\n")
    _config(repo).symlink_to(target)
    result = CliRunner().invoke(cli, ["install", "-w", str(repo), "--python", sys.executable])
    assert result.exit_code == 0, result.output
    assert "[CONFIG: template=skipped" in result.stdout
    assert "GATE_CONFIG_TEMPLATE_SKIPPED" in result.stderr
    assert target.read_text() == "# mine\n"

    notices = local_config.post_sync(repo, {})
    assert notices is not None and [notice.code for notice in notices] == ["GATE_CONFIG_TEMPLATE_SKIPPED"]


@dataclass(frozen=True)
class _Settings:
    limit: int | None = None
    paths: list[str] = field(default_factory=lambda: ["src"], metadata={"help": "Directories to check."})
    label: str | None = field(default=None, metadata={"help": "  Shown   in the\nrefusal.  "})


class _Gate(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="sample",
            description="Checks things.",
            stage=Stage.COMMIT_MSG,
            enabled_by_default=False,
            settings=_Settings(),
        )

    def run(self, ctx: GateContext) -> GateResult:
        return GateResult.passed()


def test_render_table_shows_types_defaults_and_help() -> None:
    assert local_config.render_table(_Gate()) == (
        "# [gates.settings.sample]\n"
        "# commit-msg gate, off by default: Checks things.\n"
        "# enabled = false\n"
        "# limit = 0  # integer or null; unset by default\n"
        '# paths = ["src"]  # array of strings; Directories to check.\n'
        '# label = ""  # string or null; unset by default; Shown in the refusal.\n'
    )
