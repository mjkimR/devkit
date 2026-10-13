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
    assert local_config.mentioned_gates(text) == {"verify-commands", "message-nonempty", "team-block"}
    assert "## pre-commit gate, on by default: test gate\n# [gates.settings.team-block]\n" in text
    assert "#   enabled = true\n#   allow = false  # boolean\n" in text
    assert "## commit-msg gate, on by default: Refuse" in text

    assert "[CONFIG: template=unchanged" in _install(repo)


def test_uncommented_lines_are_kept_and_take_effect(repo: Path) -> None:
    deploy_gate(repo, gate_source())
    _install(repo)
    path = _config(repo)
    edited = path.read_text().replace("# [gates.settings.team-block]", "[gates.settings.team-block]")
    edited = edited.replace("#   allow = false", "  allow = true")
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
    deploy_gate(
        repo, gate_source("second-gate", enabled=False, cls="SecondGate"), ".devkit/managed/team/gates/two/gate.py"
    )

    assert local_config.post_sync(repo, {}) is None
    text = path.read_text()
    assert text.startswith(
        before + "\n\n## pre-commit gate, off by default: test gate\n# [gates.settings.second-gate]\n"
    )
    assert "# [gates.settings.second-gate]\n#   enabled = false\n" in text
    assert text.count("[gates.settings.verify-commands]") == 1


def test_post_sync_installs_hooks_and_skips_non_repositories(repo: Path, tmp_path: Path) -> None:
    assert local_config.post_sync(repo, {}) is None
    assert _config(repo).exists()
    assert (repo / ".git/hooks/pre-commit.d/20-devkit").is_file()
    assert (repo / ".git/hooks/post-commit.d").is_dir()
    assert not (repo / ".git/hooks/post-commit.d/20-devkit").exists()
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
        "## commit-msg gate, off by default: Checks things.\n"
        "# [gates.settings.sample]\n"
        "#   enabled = false\n"
        "#   limit = 0  # integer or null; unset by default\n"
        '#   paths = ["src"]  # array of strings; Directories to check.\n'
        '#   label = ""  # string or null; unset by default; Shown in the refusal.\n'
    )


def _uncomment_once(block: str) -> str:
    """What an editor's toggle-comment does to a selection: drop one ``#`` and the space after it."""
    return "".join(
        line[2:] if line.startswith("# ") else line[1:] if line.startswith("#") else line
        for line in block.splitlines(keepends=True)
    )


def test_uncommenting_a_whole_table_keeps_prose_commented_and_yields_valid_toml(repo: Path) -> None:
    deploy_gate(repo, gate_source())
    _install(repo)
    path = _config(repo)
    text = path.read_text()
    table = local_config.render_table(
        next(g for g in load_gate_project(repo).registry.get_all() if g.id == "team-block")
    )
    assert table in text
    path.write_text(text.replace(table, _uncomment_once(table)))

    assert tomllib.loads(path.read_text()) == {"gates": {"settings": {"team-block": {"enabled": True, "allow": False}}}}
    project = load_gate_project(repo)
    assert project.validation.errors == ()
    assert project.config.gates["team-block"].values == {"allow": False}
    assert tomllib.loads(_uncomment_once(local_config.HEADER)) == {}  # the file header stays prose too


def test_uncommenting_a_table_keeps_the_settings_of_the_project_config(repo: Path) -> None:
    deploy_gate(repo, gate_source())
    (repo / ".devkit/config.toml").write_text(
        '[gates.settings.verify-commands]\ncommands = ["just check"]\n\n[gates.settings.team-block]\nenabled = false\n'
    )
    _install(repo)
    path = _config(repo)
    text = path.read_text()
    assert (
        "# [gates.settings.verify-commands]\n"
        "#   enabled = true\n"
        "##   commands: set in .devkit/config.toml; adding commands = <value> here replaces it  # array of strings; "
    ) in text
    assert "# [gates.settings.team-block]\n##   enabled: set in .devkit/config.toml;" in text
    assert "#   allow = false  # boolean\n" in text

    # As the header says: the table header and only the key that changes; the whole table is just as safe.
    edited = text.replace(
        "# [gates.settings.verify-commands]\n#   enabled = true", "[gates.settings.verify-commands]\n  enabled = false"
    )
    table = next(block for block in edited.split("\n\n") if "[gates.settings.team-block]" in block)
    path.write_text(edited.replace(table, _uncomment_once(table)))

    project = load_gate_project(repo)
    assert project.validation.errors == ()
    assert project.config.gates["verify-commands"].enabled is False
    assert project.validation.settings["verify-commands"].commands == ["just check"]
    assert project.config.gates["team-block"].enabled is False
    assert project.config.gates["team-block"].values == {"allow": False}


def test_an_unreadable_project_gates_table_skips_the_template(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    (repo / ".devkit/config.toml").write_text("[gates]\nsettings = 1\n")
    result = local_config.refresh_project_template(repo)
    assert result.state is local_config.TemplateState.SKIPPED and not _config(repo).exists()
    assert result.notice is not None and result.notice.code == "GATE_CONFIG_TEMPLATE_SKIPPED"
    assert result.notice.target_files == (".devkit/config.toml",)


def test_post_sync_preserves_hooks_and_reports_the_move_once(repo: Path) -> None:
    hook = repo / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\nexit 0\n")
    hook.chmod(0o755)
    notices = local_config.post_sync(repo, {})
    assert notices is not None and [notice.code for notice in notices] == ["GATE_HOOK_PRESERVED"]
    assert local_config.post_sync(repo, {}) is None
    assert (repo / ".git/hooks/pre-commit.legacy").read_text() == "#!/bin/sh\nexit 0\n"


def test_post_sync_skips_custom_hooks_path_with_a_coded_warning(repo: Path) -> None:
    from testsupport.gate import git

    git(repo, "config", "core.hooksPath", ".husky")
    notices = local_config.post_sync(repo, {})
    assert notices is not None and [notice.code for notice in notices] == ["GATE_HOOK_INSTALL_SKIPPED"]
    assert "GATE_HOOKS_PATH_SET" in notices[0].details[0]
    assert git(repo, "config", "core.hooksPath").stdout.strip() == ".husky"
    assert not (repo / ".git/hooks/pre-commit").exists()


def test_post_sync_leaves_symbolic_hooks_and_reserved_entries_untouched(repo: Path) -> None:
    hook = repo / ".git/hooks/pre-commit"
    hook.symlink_to("missing-hook")
    notices = local_config.post_sync(repo, {})
    assert notices is not None and notices[0].code == "GATE_HOOK_INSTALL_SKIPPED"
    assert "GATE_FOREIGN_HOOK" in notices[0].details[0] and hook.is_symlink()
    hook.unlink()
    entry = repo / ".git/hooks/pre-commit.d/20-devkit"
    entry.parent.mkdir()
    entry.write_text("mine\n")
    notices = local_config.post_sync(repo, {})
    assert notices is not None and "GATE_HOOK_LAYOUT_INVALID" in notices[0].details[0]
    assert entry.read_text() == "mine\n" and not hook.exists()
