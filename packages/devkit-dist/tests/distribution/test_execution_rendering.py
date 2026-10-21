"""Canonical execution rendering and its separation from runtime authorization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from devkit.core.errors import ReceiptError
from devkit.core.local_config import resolve_execution_environment
from devkit.core.receipt import parse_receipt
from devkit.distribution.bundles import load_bundle
from devkit.distribution.errors import BundleError, ReceiptStaleError
from devkit.distribution.installation.context import get_context
from devkit.distribution.installation.inventory import desired_inventory
from devkit.distribution.installation.local_render import LocalRenderStaleError
from devkit.distribution.installation.status import get_project_status
from devkit.distribution.installation.sync import sync_project
from distsupport.distribution import instruction, write_bundle


def setup(tmp_path: Path):
    item = write_bundle(
        tmp_path / "source",
        """schema=1
name="execution"
version="0.1.0"
[variables.language]
type="string"
default="en"
[[assets]]
id="guide"
kind="instruction"
source="guide.md.jinja"
""",
        {
            "AGENTS.md.jinja": "Constitution {{ execution.environment }}\n",
            "guide.md.jinja": instruction("guide", "{{ execution.environment }} {{ vars.language }}\n"),
        },
    )
    root = tmp_path / "project"
    (root / ".devkit").mkdir(parents=True)
    (root / ".devkit/config.toml").write_text('agents=[]\n[presets]\nexecution="all"\n')
    return root, item


def test_reversal_no_save_context_status_and_idempotence(tmp_path: Path):
    root, item = setup(tmp_path)
    receipt = root / ".devkit/installation.json"
    sync_project(root, [item])
    local = receipt.read_bytes()
    assert parse_receipt(local).execution_environment == "local"
    sync_project(root, [item], environment="cloud", save_environment=False)
    assert resolve_execution_environment(root).environment == "local"
    assert get_context(root, "execution").constitution == "Constitution cloud\n"
    assert parse_receipt(receipt.read_bytes()).execution_environment == "cloud"
    assert not get_project_status(root, [item]).ok
    assert sync_project(root, [item], dry_run=True).actions
    assert sync_project(root, [item], environment="cloud", save_environment=False).actions == []
    sync_project(root, [item])
    assert receipt.read_bytes() == local
    assert get_project_status(root, [item]).ok
    assert not sync_project(root, [item]).actions
    with pytest.raises(ReceiptStaleError):
        sync_project(root, [item], environment="cloud", locked=True)
    assert receipt.read_bytes() == local


def test_unrecorded_canonical_bootstrap_and_personal_evidence(tmp_path: Path):
    root, item = setup(tmp_path)
    sync_project(root, [item])
    path = root / ".devkit/installation.json"
    raw = json.loads(path.read_text())
    raw.pop("execution_environment")
    path.write_text(json.dumps(raw))
    assert parse_receipt(path.read_bytes()).execution_environment is None
    assert get_context(root, "execution").constitution == "Constitution local\n"
    assert not get_project_status(root, [item]).ok
    with pytest.raises(ReceiptStaleError):
        sync_project(root, [item], locked=True)
    sync_project(root, [item])
    assert parse_receipt(path.read_bytes()).execution_environment == "local"
    (root / ".devkit/config.local.toml").write_text('[bundles.execution.variables]\nlanguage="ko"\n')
    sync_project(root, [item], environment="cloud", save_environment=False)
    assert get_context(root, "execution").constitution == "Constitution cloud\n"
    raw = json.loads(path.read_text())
    raw.pop("execution_environment")
    path.write_text(json.dumps(raw))
    with pytest.raises(LocalRenderStaleError):
        get_context(root, "execution")
    sync_project(root, [item])
    assert get_context(root, "execution").constitution == "Constitution local\n"


@pytest.mark.parametrize("invalid", [None, True, 1, "", "CLOUD", [], {}])
def test_receipt_environment_is_closed_and_typed(tmp_path: Path, invalid):
    root, item = setup(tmp_path)
    sync_project(root, [item])
    raw = json.loads((root / ".devkit/installation.json").read_text())
    raw["execution_environment"] = invalid
    with pytest.raises(ReceiptError):
        parse_receipt(json.dumps(raw))


def test_constitution_collision_and_reserved_input(tmp_path: Path):
    _root, item = setup(tmp_path)
    inv = desired_inventory([item], {"execution": ["all"]}, [])
    assert inv.files[".devkit/managed/execution/AGENTS.md"].data == b"Constitution local\n"
    (item.bundle.root / "AGENTS.md").write_text("literal")
    with pytest.raises(BundleError, match="collide"):
        load_bundle(item.bundle.root)


@pytest.mark.parametrize("agents", [[], ["codex"], ["claude-code"], ["antigravity"]])
def test_common_subagent_template_validation_and_projection(tmp_path: Path, agents):
    from devkit.distribution.installation.override_commands import create_override

    contract = """---
role: reviewer
title: Reviewer
description: Checks changes.
hosts:
  codex:
    status: emulated
    sandbox_mode: read-only
  claude-code:
    status: native
    tools: [Read]
  antigravity: unsupported
---
Review {{ execution.environment }}.
"""
    item = write_bundle(
        tmp_path / "source",
        """schema=1
name="roles"
version="0.1.0"
[[assets]]
id="reviewer"
kind="subagent"
source="reviewer.md.jinja"
""",
        {"reviewer.md.jinja": contract},
    )
    root = tmp_path / "project"
    (root / ".devkit").mkdir(parents=True)
    (root / ".devkit/config.toml").write_text(f'agents={json.dumps(agents)}\n[presets]\nroles="all"\n')
    sync_project(root, [item], environment="cloud", save_environment=False)
    output = root / ".devkit/managed/roles/reviewer.md"
    assert "Review cloud." in output.read_text()
    create_override(root, [item], "roles:reviewer")
    raw = root / ".devkit/overrides/roles/reviewer.md.jinja"
    assert "{{ execution.environment }}" in raw.read_text()
    raw.write_text(contract.replace("Review", "Inspect"))
    sync_project(root, [item], environment="cloud", save_environment=False)
    assert "Inspect cloud." in output.read_text()
    before = output.read_bytes()
    raw.write_text(contract.replace("role: reviewer", "role: wrong"))
    with pytest.raises(BundleError):
        sync_project(root, [item], environment="cloud", save_environment=False)
    assert output.read_bytes() == before


def test_constitution_personal_variables_remain_forbidden(tmp_path: Path):
    from devkit.distribution.installation.local_render import LocalRenderForbiddenError

    root, item = setup(tmp_path)
    (item.bundle.root / "AGENTS.md.jinja").write_text("{{ execution.environment }} {{ vars.language }}")
    sync_project(root, [item], environment="cloud", save_environment=False)
    (root / ".devkit/config.local.toml").write_text('[bundles.execution.variables]\nlanguage="ko"\n')
    with pytest.raises(LocalRenderForbiddenError):
        sync_project(root, [item], environment="cloud", save_environment=False)
