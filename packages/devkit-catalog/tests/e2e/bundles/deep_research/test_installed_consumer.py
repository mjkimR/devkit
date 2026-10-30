"""Real docs/catalog wheels run the deep-research assets in an SDD consumer without devkit-spec (SPEC-deep-research-bundle AC-08)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[6]
ROLES = ("direction-explorer", "discovery-critic", "discovery-planner", "research-investigator")
MATERIAL = """---
id: MAT-reading-tools
created_at: 2026-10-30
---

# [MAT-reading-tools] Reading tools

Status: partial
"""


def test_installed_deep_research_without_spec(tmp_path: Path) -> None:
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
    assert not (consumer / ".devkit/managed/deep-research").exists()
    cli("add", "deep-research")
    assert json.loads(cli("config", "show"))["configuration"]["development"]["approach"] == "sdd"
    assert not (consumer / ".devkit/incubation.md").exists()
    assert not (consumer / ".devkit/managed/spec").exists()
    assert not (consumer / ".devkit/managed/incubation").exists()
    research = consumer / ".agents/skills/deep-research"
    assert (research / "SKILL.md").is_file()
    assert yaml.safe_load((research / "agents/openai.yaml").read_text())["policy"]["allow_implicit_invocation"] is False
    for role in ROLES:
        assert (consumer / f".codex/agents/{role}.toml").is_file()

    workspace_example = (research / "references/workspace.md").read_text().split("```sh\n", 1)[1].split("```", 1)[0]
    workspace_script = tmp_path / "research-workspace.sh"
    workspace_script.write_text(workspace_example + '\nprintf \'%s\\n\' "$research_run" "$research_task"\n')
    run("bash", "-n", str(workspace_script), cwd=consumer)
    allocations = [run("bash", "-eu", str(workspace_script), cwd=consumer).splitlines() for _ in range(2)]
    assert allocations[0][0] != allocations[1][0]
    for run_path, task_path in allocations:
        assert run_path.startswith(".devkit/transient/deep-research/run-")
        assert (consumer / run_path).is_dir()
        assert (consumer / task_path).resolve().is_relative_to((consumer / run_path).resolve())
        assert run("git", "check-ignore", "--", run_path, task_path, cwd=consumer).splitlines() == [run_path, task_path]
        assert not run("git", "ls-files", "--", run_path, task_path, cwd=consumer).strip()

    material = consumer / "docs/materials/2026-10/20261030-reading-tools/20261030-reading-tools.md"
    material.parent.mkdir(parents=True)
    material.write_text(MATERIAL)
    expected = material.read_bytes()
    cli("rules", "check")
    cli("remove", "deep-research")
    assert not research.exists()
    assert not (consumer / ".codex/agents/research-investigator.toml").exists()
    assert material.read_bytes() == expected
    cli("add", "deep-research")
    assert material.read_bytes() == expected
    assert (research / "SKILL.md").is_file()
    cli("sync", "--check")
