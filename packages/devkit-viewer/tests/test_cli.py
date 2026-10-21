from __future__ import annotations

import json
import os
import re
import signal
import socket
import subprocess
import sys
import urllib.request
from importlib.metadata import entry_points, version
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit_dist.cli import cli as devkit_cli
from viewer_fixtures import MakeRepo

SENTINEL = re.compile(r"^\[VIEWER: url=http://127\.0\.0\.1:(\d+)/ repos=(\d+)\]$")


def _serve(cwd: Path, *args: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, "-P", "-m", "devkit_dist", "viewer", "serve", *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def test_serve_prints_one_line_and_stops_cleanly(make_repo: MakeRepo, tmp_path: Path) -> None:
    alpha, beta = make_repo("alpha"), make_repo("beta")
    process = _serve(tmp_path, "--repo", str(alpha), "--repo", str(beta), "--port", "0")
    try:
        assert process.stdout is not None
        match = SENTINEL.match(process.stdout.readline().rstrip("\n"))
        assert match, "the first stdout line is the [VIEWER] sentinel"
        port, count = int(match[1]), int(match[2])
        assert count == 2
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/repos", timeout=10) as response:
            assert [repo["id"] for repo in json.load(response)["repos"]] == ["alpha", "beta"]
        process.send_signal(signal.SIGINT)
        stdout, _stderr = process.communicate(timeout=10)
    finally:
        process.kill()
    assert process.returncode == 0
    assert stdout == ""


def test_sigterm_stops_cleanly(make_repo: MakeRepo) -> None:
    alpha = make_repo("alpha")
    process = _serve(alpha, "--port", "0")
    try:
        assert process.stdout is not None
        assert SENTINEL.match(process.stdout.readline().rstrip("\n"))
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=10)
    finally:
        process.kill()
    assert process.returncode == 0


def _invoke(cwd: Path, *args: str) -> Result:
    previous = Path.cwd()
    os.chdir(cwd)
    try:
        return CliRunner().invoke(devkit_cli, ["viewer", "serve", *args])
    finally:
        os.chdir(previous)


def test_refusals(make_repo: MakeRepo, tmp_path: Path) -> None:
    first = make_repo("same", parent=tmp_path / "a")
    second = make_repo("same", parent=tmp_path / "b")
    empty = tmp_path / "empty"
    empty.mkdir()
    cases = {
        "VIEWER_REPO_DUPLICATE": ["--repo", str(first), "--repo", str(second)],
        "VIEWER_REPO_INVALID": ["--repo", str(empty)],
        "VIEWER_NO_REPOSITORY": ["--scan", str(empty)],
    }
    for code, args in cases.items():
        result = _invoke(tmp_path, *args, "--port", "0")
        assert result.exit_code == 2, code
        assert result.stdout == ""
        assert f"({code})" in result.stderr
    outside = _invoke(empty, "--port", "0")
    assert outside.exit_code == 2
    assert "(VIEWER_NO_REPOSITORY)" in outside.stderr


def test_port_in_use(make_repo: MakeRepo) -> None:
    alpha = make_repo("alpha")
    with socket.socket() as taken:
        taken.bind(("127.0.0.1", 0))
        taken.listen()
        result = _invoke(alpha, "--port", str(taken.getsockname()[1]))
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "(VIEWER_PORT_IN_USE)" in result.stderr


def test_version_and_mount() -> None:
    result = CliRunner().invoke(devkit_cli, ["viewer", "--version"])
    assert result.exit_code == 0
    assert result.stdout == f"[VERSION: devkit-viewer {version('devkit-viewer')}]\n"
    assert CliRunner().invoke(devkit_cli, ["viewer", "serve", "--help"]).exit_code == 0
    (mount,) = [ep for ep in entry_points(group="devkit.commands") if ep.name == "viewer"]
    assert mount.value == "devkit_viewer.features.browse.cli:cli"


@pytest.mark.parametrize("args", [["--port", "-1"], ["--port", "70000"]])
def test_port_range(args: list[str]) -> None:
    assert CliRunner().invoke(devkit_cli, ["viewer", "serve", *args]).exit_code == 2
