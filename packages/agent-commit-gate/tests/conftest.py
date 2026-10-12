from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

# A deployed gate file: refuses every commit unless its ``allow`` setting is on.
GATE = """from dataclasses import dataclass

from agent_commit_gate import BaseGate, GateContext, GateError, GateResult, Stage


@dataclass(frozen=True)
class Settings:
    allow: bool = False


class {cls}(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="{gate_id}",
            description="test gate",
            stage=Stage.PRE_COMMIT,
            enabled_by_default={enabled},
            settings=Settings(),
        )

    def run(self, ctx: GateContext) -> GateResult:
        if ctx.settings.allow:
            return GateResult.passed("allowed")
        raise GateError.blocked("{gate_id} refused", code="TEST_REFUSED")
"""


def gate_source(gate_id: str = "team-block", *, enabled: bool = True, cls: str = "BlockGate") -> str:
    return GATE.format(gate_id=gate_id, enabled=enabled, cls=cls)


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check, env=env)


def deploy_gate(repo: Path, source: str, rel: str = ".devkit/managed/team/gates/block.py") -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)
    receipt = repo / ".devkit/installation.json"
    data = json.loads(receipt.read_text()) if receipt.is_file() else {"schema": 1, "assets": []}
    data["assets"].append({"bundle": "team", "id": path.stem, "kind": "gate", "paths": [rel]})
    receipt.write_text(json.dumps(data))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "dev@example.com")
    git(root, "config", "user.name", "Dev")
    git(root, "config", "commit.gpgsign", "false")
    return root
