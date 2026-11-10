"""Real Git fixtures for assignment command contracts."""

import json
import subprocess

import pytest
from click.testing import CliRunner
from devkit_adaptive.cli import cli


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-qb", "main", str(root)], check=True)
    for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.test")):
        subprocess.run(["git", "-C", str(root), "config", key, value], check=True)
    (root / "src").mkdir()
    (root / "src/a").write_text("base\n")
    (root / "src/ab").write_text("base\n")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
    return root


@pytest.fixture
def call(repo):
    def invoke(*args, expected=0, root=repo, text=False):
        result = CliRunner().invoke(
            cli, ["assignment", *args, "-w", str(root), *([] if text else ["--format", "json"])]
        )
        assert result.exit_code == expected, result.output + repr(result.exception)
        if text:
            return result.stdout
        assert len(result.stdout.splitlines()) == 1
        return json.loads(result.stdout)

    return invoke
