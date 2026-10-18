"""Repository verification can bypass a broken runner without retrying commands."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def script_env(tmp_path: Path) -> dict[str, str]:
    uv = tmp_path / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "with open(os.environ['CALLS'], 'a') as log:\n"
        "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "sys.exit(int(os.environ.get('TOOL_EXIT', '0')))\n"
    )
    uv.chmod(0o755)
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}", "CALLS": str(tmp_path / "calls")}
    env.pop("DEVKIT_RUN_MODE", None)
    return env


def calls(env: dict[str, str]) -> list[list[str]]:
    return [json.loads(line) for line in Path(env["CALLS"]).read_text().splitlines()]


@pytest.mark.parametrize("mode", [None, "raw"])
@pytest.mark.parametrize("target", ["all", "devkit"])
def test_test_recipe_preserves_arguments_and_preflight(
    script_env: dict[str, str], mode: str | None, target: str
) -> None:
    if mode:
        script_env["DEVKIT_RUN_MODE"] = mode
    result = subprocess.run(
        ["bash", str(ROOT / "scripts/module.sh"), "test", target, "-k", "foo and bar", "-n0"],
        env=script_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    preflight, check = calls(script_env)
    assert preflight == [
        "run",
        "--no-active",
        "python",
        "scripts/check_test_environment.py",
        "--",
        "just",
        "test",
        target,
        "-k",
        "foo and bar",
        "-n0",
    ]
    prefix = ["run", "--no-active"]
    if mode != "raw":
        prefix += ["devkit", "run", "--", "uv", "run", "--no-active"]
    assert check[: len(prefix) + 1] == [*prefix, "pytest"]
    assert check[-3:] == ["-k", "foo and bar", "-n0"]


@pytest.mark.parametrize("mode", ["compact", "raw"])
def test_failure_stops_checks_without_retry(script_env: dict[str, str], mode: str) -> None:
    script_env.update(DEVKIT_RUN_MODE=mode, TOOL_EXIT="2")
    result = subprocess.run(["bash", str(ROOT / "scripts/module.sh"), "lint-check", "devkit"], env=script_env)
    assert result.returncode == 2
    assert len(calls(script_env)) == 1


def test_invalid_mode_runs_no_tool(script_env: dict[str, str]) -> None:
    script_env["DEVKIT_RUN_MODE"] = "typo"
    result = subprocess.run(
        ["bash", str(ROOT / "scripts/module.sh"), "check", "devkit"],
        env=script_env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "DEVKIT_RUN_MODE" in result.stderr
    assert not Path(script_env["CALLS"]).exists()
