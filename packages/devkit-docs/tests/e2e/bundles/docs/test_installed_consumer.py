"""Built-wheel consumer has no SDD package or lifecycle asset."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]


def test_document_only_built_wheels(tmp_path: Path) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("DEVKIT_", "PYTHONPATH", "VIRTUAL_ENV"))}

    def run(*args: str, cwd: Path = tmp_path) -> str:
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout

    wheels = tmp_path / "wheels"
    for package in ["devkit-advisory", "devkit-cli", "devkit-core", "devkit-dist", "devkit-agt", "devkit-docs"]:
        run("uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels), cwd=ROOT)
    venv = tmp_path / "venv"
    run("uv", "venv", str(venv))
    python = str(venv / "bin/python")
    run("uv", "pip", "install", "--python", python, *map(str, wheels.glob("*.whl")))
    run(
        python,
        "-c",
        "from importlib.metadata import distributions; assert 'devkit-spec' not in {d.metadata['Name'] for d in distributions()}",
    )
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    run("git", "init", "-q", str(consumer))

    def cli(*args: str) -> str:
        return run(python, "-m", "devkit_dist", *args, "-w", str(consumer), cwd=consumer)

    cli("sync")
    context = json.loads(cli("get-context", "docs"))
    assert len(context["instructions"]) == 8
    assert not (consumer / ".devkit/managed/spec").exists()
    assert not (consumer / ".agents/skills/spec").exists()
    assert not (consumer / ".devkit/managed/docs/workflows").exists()
    assert len(list((consumer / ".devkit/managed/docs/rules").glob("*/rule.py"))) == 9
    receipt = json.loads((consumer / ".devkit/installation.json").read_text())
    assert '"spec"' not in json.dumps(receipt)
    cli("add", "docs:docs-skeleton")
    for args in [
        ("docs", "list"),
        ("docs", "resolve", "ARCH-01-introduction-and-goals"),
        ("docs", "refs", "ARCH-01-introduction-and-goals"),
        ("docs", "search", "architecture"),
        ("rules", "check"),
        ("sync", "--check"),
    ]:
        cli(*args)
    explain = cli("rules", "explain", "RULE-document-reference")
    assert "docs:living-spec-writing" in explain and ".devkit/managed/docs/instructions/" in explain

    assert json.loads(cli("config", "show"))["configuration"]["development"]["approach"] == "sdd"
    config = consumer / ".devkit/config.toml"
    config.write_text(
        config.read_text() + '\n[development]\napproach = "incubation"\n[integration]\nprovider = "project"\n'
    )
    inspected = json.loads(cli("config", "show"))
    assert inspected["configuration"]["development"]["approach"] == "incubation"
    assert inspected["sources"]["development.approach"] == ".devkit/config.toml"
    cli("rules", "check")
    run("git", "config", "user.email", "test@example.com", cwd=consumer)
    run("git", "config", "user.name", "Test", cwd=consumer)
    run("git", "branch", "-M", "main", cwd=consumer)
    run("git", "add", ".", cwd=consumer)
    run("git", "commit", "-qm", "configure document-only incubation", cwd=consumer)
    started = json.loads(cli("worktree", "start", "dev-demo", "--format", "json"))
    # The retained CLI's result exposes the worktree path; it is a real installed project provider consumer.
    worktree = consumer.parent / "consumer-wt-dev-demo"
    assert worktree.is_dir(), started
    (worktree / "app.py").write_text("value = 1\n")
    run("git", "add", "app.py", cwd=worktree)
    run("git", "commit", "-qm", "implement incubation flow", cwd=worktree)
    prepared = json.loads(
        cli(
            "integration",
            "prepare",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "docs-consumer",
            "--claims",
            json.dumps({"review": "PASS source review", "tests": "PASS project tests", "lint": "PASS lint"}),
            "--format",
            "json",
        )
    )
    assert prepared["status"] == "prepared"
