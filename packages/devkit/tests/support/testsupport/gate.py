"""Gate test helpers: deployed gate sources, Git and receipt fixtures."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from devkit_agt.features.gate import GateContext, Stage

# A deployed gate package's module: refuses every commit unless its ``allow`` setting is on.
GATE = """from dataclasses import dataclass

from devkit_agt.features.gate import BaseGate, GateContext, GateRefusedError, GateResult, Stage


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
        raise GateRefusedError("{gate_id} refused", code="TEST_REFUSED")
"""


def gate_source(gate_id: str = "team-block", *, enabled: bool = True, cls: str = "BlockGate") -> str:
    return GATE.format(gate_id=gate_id, enabled=enabled, cls=cls)


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check, env=env)


def deploy_gate(repo: Path, source: str, rel: str = ".devkit/managed/team/gates/block/gate.py") -> None:
    """Write a gate package's one module and list it in the receipt as an asset named after its directory.

    The file's hash is recorded under ``files`` unless it is a project override.
    """
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)
    receipt = repo / ".devkit/installation.json"
    data = (
        json.loads(receipt.read_text())
        if receipt.is_file()
        else {"schema": 1, "packages": [], "selection": {"agents": [], "presets": {}}, "assets": [], "files": {}}
    )
    data["assets"].append(
        {"bundle": "team", "id": path.parent.name.strip("_").replace("_", "-"), "kind": "gate", "paths": [rel]}
    )
    if not rel.startswith(".devkit/overrides/"):
        data["files"][rel] = {"sha256": hashlib.sha256(source.encode()).hexdigest(), "mode": 420}
    receipt.write_text(json.dumps(data))


def gate_ctx(root: Path, stage: Stage = Stage.PRE_COMMIT, *args: str) -> GateContext:
    """A context for a repository whose git dir is ``root/.git`` (no linked worktree)."""
    return GateContext(repo_root=root, git_dir=root / ".git", common_git_dir=root / ".git", stage=stage, args=args)
