"""Real docs/catalog wheels expose incubation assets and shared policy without SDD."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]


def test_installed_incubation_without_spec(tmp_path: Path) -> None:
    env = {
        key: value for key, value in os.environ.items() if not key.startswith(("DEVKIT_", "PYTHONPATH", "VIRTUAL_ENV"))
    }

    def run(*args: str, cwd: Path = tmp_path, expected: int = 0) -> str:
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)
        assert result.returncode == expected, result.stdout + result.stderr
        return result.stdout

    wheels = tmp_path / "wheels"
    for package in [
        "devkit-advisory",
        "devkit-cli",
        "devkit-core",
        "devkit-dist",
        "devkit-agt",
        "devkit-docs",
        "devkit-catalog",
    ]:
        run("uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels), cwd=ROOT)
    venv = tmp_path / "venv"
    run("uv", "venv", str(venv))
    python = str(venv / "bin/python")
    run("uv", "pip", "install", "--python", python, *map(str, wheels.glob("*.whl")))
    run(
        python,
        "-c",
        "from importlib.metadata import distributions; assert 'devkit-spec' not in {item.metadata['Name'] for item in distributions()}",
    )
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    run("git", "init", "-q", str(consumer))

    def cli(*args: str, expected: int = 0) -> str:
        return run(python, "-m", "devkit_dist", *args, "-w", str(consumer), cwd=consumer, expected=expected)

    cli("sync")
    assert not (consumer / ".devkit/managed/incubation").exists()
    cli("add", "incubation")
    assert not (consumer / ".devkit/incubation.md").exists()
    context = json.loads(cli("get-context", "incubation"))
    assert "Idea Incubation" in context["constitution"]
    assert json.loads(cli("config", "show"))["configuration"]["development"]["approach"] == "sdd"
    config = consumer / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[development]\napproach = "incubation"\n')
    inspected = json.loads(cli("config", "show"))
    assert inspected["configuration"]["development"]["approach"] == "incubation"
    assert inspected["sources"]["development.approach"] == ".devkit/config.toml"
    assert len(json.loads(cli("get-context", "docs"))["instructions"]) == 8
    assert not (consumer / ".devkit/managed/spec").exists()
    assert not (consumer / ".agents/skills/spec").exists()
    assert (consumer / ".agents/skills/incubate/SKILL.md").is_file()
    assert not (consumer / ".agents/skills/incubate-research").exists()
    for role in ("product-clarifier", "incubation-researcher", "usage-reviewer"):
        assert (consumer / f".codex/agents/{role}.toml").is_file()
    assert not (consumer / ".codex/agents/direction-explorer.toml").exists()
    current = consumer / ".devkit/incubation.md"
    current.write_bytes(b"# Current facts\nGoal: household list\nUnverified: offline merge\n")
    expected_context = current.read_bytes()
    roadmap = consumer / "docs/materials/discovery-roadmap.md"
    roadmap.parent.mkdir(parents=True, exist_ok=True)
    roadmap.write_text("# Proposed roadmap\nInvestigate offline collaboration before implementation.\n")
    expected_roadmap = roadmap.read_bytes()
    cli("rules", "check")
    cli("remove", "incubation")
    assert not (consumer / ".agents/skills/incubate/SKILL.md").exists()
    assert current.read_bytes() == expected_context
    assert roadmap.read_bytes() == expected_roadmap
    cli("add", "incubation")
    assert current.read_bytes() == expected_context
    assert roadmap.read_bytes() == expected_roadmap
    assert (consumer / ".agents/skills/incubate/SKILL.md").is_file()
    cli("sync", "--check")
    config.write_text(config.read_text().replace('approach = "incubation"', 'approach = "invalid"'))
    error = json.loads(cli("config", "show", "--format", "json", expected=2))
    assert error["error"]["code"] == "DEVELOPMENT_CONFIG_INVALID"
    assert current.read_bytes() == expected_context
