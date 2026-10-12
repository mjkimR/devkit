from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from devkit_distribution.bundles import BundleError, load_bundle
from devkit_distribution.bundles.workflows import read_workflow_header
from devkit_distribution.installation.config import update_config
from devkit_distribution.installation.discovery import InstalledBundle
from devkit_distribution.installation.sync import sync_project
from devkit_distribution.installation.transaction import RECEIPT
from devkit_distribution.installation.workflow_skill import MANAGED_ROOT, NAME

WORKFLOW = """---
id: direct-delivery
title: "Direct delivery"
schema_version: 1
stages:
  - id: intent
    exit: [anchor-exists]
---
Gate rules.
"""


def make_bundle(tmp_path: Path, bundle: str, workflow: str = WORKFLOW) -> InstalledBundle:
    root = tmp_path / bundle
    (root / "flows").mkdir(parents=True)
    (root / "flows/delivery.md").write_text(workflow)
    (root / "guide.md").write_text("---\nname: testing\ndescription: Testing constraints.\n---\nBody.\n")
    (root / "bundle.toml").write_text(f'''schema = 1
name = "{bundle}"
version = "0.1.0"
[[assets]]
id = "delivery"
kind = "workflow"
source = "flows/delivery.md"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[presets.guidance]
assets = ["guide"]
[presets.delivery]
assets = ["delivery", "guide"]
''')
    return InstalledBundle(f"{bundle}-content", "0.1.0", load_bundle(root))


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    return root


def test_header_validation() -> None:
    header = read_workflow_header(WORKFLOW.encode(), "x")
    assert (header.id, header.title, header.stages) == ("direct-delivery", "Direct delivery", 1)
    for body, match in [
        ("no frontmatter", "requires YAML frontmatter"),
        ("---\nid: x\n", "unclosed"),
        ("---\nid: [\n---\n", "invalid YAML"),
        ("---\n- a\n---\n", "must be a mapping"),
        ("---\nid: Bad_ID\nstages: [a]\n---\n", "lowercase slug"),
        ("---\nid: ok\nstages: []\n---\n", "nonempty list"),
    ]:
        with pytest.raises(BundleError, match=match):
            read_workflow_header(body.encode(), "x")


def test_manifest_rejects_bad_workflow_sources(tmp_path: Path) -> None:
    root = tmp_path / "bad"
    (root / "flows").mkdir(parents=True)
    (root / "flows/a.md").write_text("plain\n")
    (root / "bundle.toml").write_text(
        'schema = 1\nname = "bad"\nversion = "0.1.0"\n[[assets]]\nid = "a"\nkind = "workflow"\nsource = "flows"\n'
    )
    with pytest.raises(BundleError, match="single Markdown file"):
        load_bundle(root)
    (root / "bundle.toml").write_text(
        'schema = 1\nname = "bad"\nversion = "0.1.0"\n[[assets]]\nid = "a"\nkind = "workflow"\nsource = "flows/a.md"\n'
    )
    with pytest.raises(BundleError, match="requires YAML frontmatter"):
        load_bundle(root)


def test_sync_deploys_workflow_and_generated_entry_skill(tmp_path: Path, target: Path) -> None:
    installed = [make_bundle(tmp_path, "team")]
    update_config(target, presets={"team": ["delivery"]}, agents=["codex", "claude-code"])
    sync_project(target, installed)

    deployed = target / ".devkit/managed/team/flows/delivery.md"
    assert deployed.read_text() == WORKFLOW
    receipt = json.loads((target / RECEIPT).read_text())
    record = next(a for a in receipt["assets"] if a["kind"] == "workflow")
    assert record["id"] == "delivery" and record["entrypoints"] == [".devkit/managed/team/flows/delivery.md"]

    assert (target / MANAGED_ROOT / "SKILL.md").exists()
    codex = target / f".agents/skills/{NAME}"
    claude = target / f".claude/skills/{NAME}"
    assert "agent-workflow next" in (codex / "SKILL.md").read_text()
    policy = yaml.safe_load((codex / "agents/openai.yaml").read_text())
    assert policy["policy"]["allow_implicit_invocation"] is True
    frontmatter = yaml.safe_load((claude / "SKILL.md").read_text().split("---")[1])
    assert frontmatter["name"] == NAME and "disable-model-invocation" not in frontmatter
    assert not (claude / "agents").exists()

    # Deselecting the only workflow removes the definition and the entry skill.
    sync_project(target, installed, presets={"team": ["guidance"]})
    assert not deployed.exists()
    assert not (target / MANAGED_ROOT / "SKILL.md").exists()
    assert not (codex / "SKILL.md").exists()
    assert not any(a["kind"] == "workflow" for a in json.loads((target / RECEIPT).read_text())["assets"])


def test_workflow_and_playbook_skills_coexist(tmp_path: Path, target: Path) -> None:
    from test_playbooks import make_bundle as make_playbook_bundle

    installed = [make_bundle(tmp_path, "team"), make_playbook_bundle(tmp_path, "ops")]
    update_config(target, presets={"team": ["all"], "ops": ["all"]}, agents=["codex"])
    sync_project(target, installed)
    assert (target / ".agents/skills/devkit-workflow/SKILL.md").exists()
    assert (target / ".agents/skills/devkit-playbook/SKILL.md").exists()
