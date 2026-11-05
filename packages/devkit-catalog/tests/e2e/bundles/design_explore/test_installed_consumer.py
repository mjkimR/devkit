"""Real dist/catalog wheels deploy design-explore without agt/docs/spec (SPEC-design-solution-exploration AC-06)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[6]
ROLES = ("solution-explorer", "reference-researcher", "design-critic")


def test_installed_design_exploration_without_delivery_packages(tmp_path: Path) -> None:
    env = {
        key: value for key, value in os.environ.items() if not key.startswith(("DEVKIT_", "PYTHONPATH", "VIRTUAL_ENV"))
    }

    def run(*args: str, cwd: Path = tmp_path) -> str:
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout

    wheels = tmp_path / "wheels"
    for package in ("devkit-advisory", "devkit-cli", "devkit-core", "devkit-dist", "devkit-catalog"):
        run("uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels), cwd=ROOT)
    venv = tmp_path / "venv"
    run("uv", "venv", str(venv))
    python = str(venv / "bin/python")
    run("uv", "pip", "install", "--python", python, *map(str, wheels.glob("*.whl")))
    run(
        python,
        "-c",
        "from importlib.metadata import distributions; "
        "assert not {'devkit-agt','devkit-docs','devkit-spec'} & {d.metadata['Name'] for d in distributions()}",
    )
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    run("git", "init", "-q", str(consumer))

    def cli(*args: str) -> str:
        return run(python, "-m", "devkit_dist", *args, "-w", str(consumer), cwd=consumer)

    cli("sync")
    skill = consumer / ".agents/skills/design-explore"
    assert not skill.exists()
    before = json.loads(cli("config", "show"))["configuration"]["development"]["approach"]
    cli("add", "design-explore")
    assert json.loads(cli("config", "show"))["configuration"]["development"]["approach"] == before
    assert yaml.safe_load((skill / "agents/openai.yaml").read_text())["policy"]["allow_implicit_invocation"] is False
    for role in ROLES:
        assert (skill / f"roles/{role}.md").is_file()
        assert not (consumer / f".codex/agents/{role}.toml").exists()
    for absent in ("docs", "specs", ".devkit/managed/spec", ".devkit/managed/deep-research", ".devkit/adaptive-dev.md"):
        assert not (consumer / absent).exists()
    for relative in ("references/exploration-methods.md", "references/orchestration.md"):
        assert (skill / relative).is_file()
    # The response procedure and local author assignment ship in the built wheel without a new role.
    orchestration = (skill / "references/orchestration.md").read_text()
    assert "Optional critique response" in orchestration
    assert "at most one author response per affected candidate" in orchestration
    assert "missing author coverage" in orchestration
    assert "reasoned disposition" in orchestration
    assert "Response assignment" in (skill / "roles/solution-explorer.md").read_text()
    assert "no automatic further critic reply" in (skill / "roles/design-critic.md").read_text()
    cli("add", "command-design")
    other = consumer / ".devkit/managed/command-design"
    assert other.is_dir()
    artifact = consumer / "design.md"
    artifact.write_text("User-owned design notes.\n")
    cli("remove", "design-explore")
    assert not skill.exists()
    assert other.is_dir()
    assert artifact.read_text() == "User-owned design notes.\n"
    cli("add", "design-explore")
    assert (skill / "SKILL.md").is_file()
    assert artifact.read_text() == "User-owned design notes.\n"
    cli("sync", "--check")
