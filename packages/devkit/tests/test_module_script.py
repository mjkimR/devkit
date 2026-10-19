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


def pytest_paths(check: list[str]) -> list[str]:
    """The test paths of a recorded pytest call: after the xdist and coverage options, before the extra arguments."""
    rest = [arg for arg in check[check.index("worksteal") + 1 :] if not arg.startswith("--cov")]
    return rest[: next((i for i, arg in enumerate(rest) if arg.startswith("-")), len(rest))]


def run_module(script_env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    script_env["DEVKIT_RUN_MODE"] = "raw"
    return subprocess.run(
        ["bash", str(ROOT / "scripts/module.sh"), *args], env=script_env, capture_output=True, text=True
    )


@pytest.mark.parametrize(
    ("args", "paths", "extra"),
    [
        (["gate"], ["packages/devkit/tests/gate", "packages/devkit/src/devkit/gate"], []),
        (
            ["gate", "worktree", "-k", "foo"],
            [
                "packages/devkit/tests/gate",
                "packages/devkit/src/devkit/gate",
                "packages/devkit/tests/worktree",
                "packages/devkit/src/devkit/worktree",
            ],
            ["-k", "foo"],
        ),
        (
            ["packages/devkit/tests/gate/test_hooks.py::test_commits_run_built_in_gates"],
            ["packages/devkit/tests/gate/test_hooks.py::test_commits_run_built_in_gates"],
            [],
        ),
        ([], ["packages/devkit/tests", "packages/devkit/src"], []),
        (["-k", "foo"], ["packages/devkit/tests", "packages/devkit/src"], ["-k", "foo"]),
    ],
)
@pytest.mark.parametrize("action", ["test", "test-cov"])
def test_selectors_replace_the_module_paths(
    script_env: dict[str, str], action: str, args: list[str], paths: list[str], extra: list[str]
) -> None:
    result = run_module(script_env, action, "devkit", *args)
    assert result.returncode == 0, result.stderr
    preflight, check = calls(script_env)
    assert preflight[-len(args) - 3 :] == ["just", action, "devkit", *args]
    assert pytest_paths(check) == paths
    assert check[len(check) - len(extra) :] == extra


def test_an_area_of_another_module_includes_its_source_package(script_env: dict[str, str]) -> None:
    result = run_module(script_env, "test", "spec", "scope")
    assert result.returncode == 0, result.stderr
    assert pytest_paths(calls(script_env)[1]) == [
        "packages/devkit-spec/tests/scope",
        "packages/devkit-spec/src/devkit_spec/scope",
    ]


def test_an_unknown_area_runs_no_tool(script_env: dict[str, str]) -> None:
    result = run_module(script_env, "test", "devkit", "nosuch", "-k", "foo")
    assert result.returncode == 2
    assert "Unknown area for devkit-agt: nosuch" in result.stderr
    available = next(line for line in result.stderr.splitlines() if line.startswith("Available areas: "))
    assert {"gate", "worktree", "core"} <= set(available.split(": ", 1)[1].split())
    assert "__pycache__" not in available
    assert not Path(script_env["CALLS"]).exists()


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
