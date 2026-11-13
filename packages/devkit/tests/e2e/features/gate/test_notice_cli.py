"""Installed CLI and real commit-gate handling of a nonblocking consideration."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from testsupport.gate import git
from testsupport.rules import digests, write_receipt

SOURCE = """from devkit_agt.features.rules import Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule
class Consider(BaseRule):
    def __init__(self):
        super().__init__('RULE-consider', 'consider', 'fixture', severity=Severity.NOTICE, change_scope=True)
    def check(self, ctx):
        return [Violation(self.id, name, 1, 'Consider the changed document', change_span=c.span('after', 1, len(c.after.splitlines())+1))
                for name,c in ctx.changes.items() if name.endswith('.md') and c.after and c.hunks]
"""


def test_notice_passes_strict_installed_cli_and_real_commit(repo: Path) -> None:
    rel = ".devkit/managed/team/rules/consider/rule.py"
    source = repo / rel
    source.parent.mkdir(parents=True)
    source.write_text(SOURCE)
    write_receipt(repo, [{"bundle": "team", "id": "consider", "kind": "rule", "paths": [rel]}], digests(repo, rel))
    (repo / "README.md").write_text("# Initial\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "baseline")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

    def invoke(*args: str):
        return subprocess.run(
            [sys.executable, "-m", "devkit_dist", *args], cwd=repo, env=env, capture_output=True, text=True
        )

    installed = invoke("gate", "install", "--python", sys.executable)
    assert installed.returncode == 0, installed.stderr
    (repo / "README.md").write_text("# Changed\n")
    checked = invoke("rules", "check", "--strict", "README.md")
    assert checked.returncode == 0 and "severity=notice" in checked.stdout and "status=consider" in checked.stdout
    context = invoke("rules", "context", "README.md", "--format", "json")
    assert context.returncode == 0 and '"hunks":[' in context.stdout
    git(repo, "add", "README.md")
    env["DEVKIT_STRICT"] = "1"
    committed = subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "update"], env=env, capture_output=True, text=True
    )
    assert committed.returncode == 0, committed.stdout + committed.stderr
    assert "GATE_RULES_NOTICES" in committed.stderr
