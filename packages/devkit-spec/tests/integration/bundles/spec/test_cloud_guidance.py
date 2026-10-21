"""Audit every selected maintained output, including references and native projections."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

import pytest
from devkit_dist.features.distribution.services.bundles.common import AGENT_NAMES
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import discover_bundles
from devkit_dist.features.distribution.services.installation.inventory import desired_inventory
from devkit_dist.features.distribution.usecases.context import GetContext
from devkit_dist.features.distribution.usecases.sync import sync_project

MAINTAINED = {"advisory", "authoring", "devkit", "harness", "response-style", "spec"}
OPERATIONAL = re.compile(
    r"\bMCP\b|\b(?:integration_(?:integrate|prepare|resume|status)|spec_(?:proposal_report|plan_accept|handoff)|shared_(?:put|get|list|sweep|sweep_apply))\b|native (?:approval|confirmation|form)",
    re.I,
)
# These two lines document configuration keys; they do not instruct setup or routing.
DESCRIPTIVE = {
    ".devkit/managed/advisory/instructions/agent-advisory.md": {
        "Every error, warning and notice an AI agent reads (CLI commands, rules, validation, MCP tools) follows this protocol, so agents act on explicit directives instead of guessing, improvising workarounds or retrying in loops.",
        "- **MCP tools**: a failed call returns the rendered error block as the error result text; a successful call appends its rendered warning and notice blocks after the result text.",
    },
    ".devkit/managed/advisory/instructions/agent-advisory-python.md": {
        "- `error.lines()` / `error.render()`: sentinel lines (`[ERROR]`, `[WARN]` or `[NOTICE]` headline by level) for stderr or an MCP tool result; multi-line values continue on lines indented under their sentinel.",
    },
    ".devkit/managed/devkit/instructions/consumption.md": {
        "| `.devkit/config.local.toml` | no | Optional checkout-local execution, MCP registration, playbook and bundle-variable preferences |",
        "`[mcp] register = true | false`, `[playbooks]` search preferences and scalar",
    },
}


@pytest.mark.parametrize("agent", AGENT_NAMES)
def test_complete_maintained_cloud_inventory(agent: str, tmp_path: Path):
    with discover_bundles() as installed:
        selected = [item for item in installed if item.bundle.name in MAINTAINED]
        assert {item.bundle.name for item in selected} == MAINTAINED
        inventory = desired_inventory(
            selected, {item.bundle.name: ["all"] for item in selected}, [agent], environment="cloud"
        )
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={item.bundle.name: ["all"] for item in selected}, agents=[agent])
    sync_project(root, selected, environment="cloud")
    assert not sync_project(root, selected).actions
    for name, content in inventory.files.items():
        assert (root / name).read_bytes() == content.data
    for item in selected:
        context = GetContext().execute(root, item.bundle.name)
        if context.constitution is not None:
            assert (
                context.constitution.encode() == inventory.files[f".devkit/managed/{item.bundle.name}/AGENTS.md"].data
            )
    kinds = {path: asset.kind for asset in inventory.assets for path in asset.paths}
    classified = set()
    for name, content in inventory.files.items():
        assert not name.endswith(".jinja"), name
        # Classification is per destination, including generated skills and native contract TOML.
        kind = kinds.get(name)
        if name.endswith("/bundle.toml"):
            assert name.startswith(".devkit/managed/")
            classified.add(name)
            continue  # Manifest source paths are provenance, not executable agent guidance.
        if kind in {"rule", "gate", "hook"} and not name.endswith(".md"):
            assert PurePosixPath(name).suffix in {".py", ".toml", ".yaml", ".json", ".txt"}, name
            classified.add(name)
            continue  # Typed executable/configuration payloads, not operational prose.
        text = content.data.decode()
        for line in text.splitlines():
            if OPERATIONAL.search(line):
                assert line in DESCRIPTIVE.get(name, set()), (name, line)
        classified.add(name)
    assert classified == set(inventory.files)
    combined = "\n".join(v.data.decode() for k, v in inventory.files.items() if k.endswith(".md"))
    for required in (
        "devkit shared put|get|list|sweep",
        "devkit spec proposal report",
        "separately authorized",
        "devkit playbook get",
        "devkit workflow next",
    ):
        assert required in combined
    local = desired_inventory(selected, {item.bundle.name: ["all"] for item in selected}, [agent], environment="local")
    assert b"spec_plan_accept" in local.files[".devkit/managed/spec/skills/spec-review-proposal/SKILL.md"].data
    assert (
        b"Do not automatically fall back to CLI"
        in local.files[".devkit/managed/spec/skills/spec-orchestrate/SKILL.md"].data
    )
