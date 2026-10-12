from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
import yaml
from devkit_distribution.bundles import BundleError, load_bundle
from devkit_distribution.bundles.subagents import projection_path, read_contract, render
from devkit_distribution.installation.config import update_config
from devkit_distribution.installation.discovery import InstalledBundle
from devkit_distribution.installation.sync import sync_project
from devkit_distribution.installation.transaction import RECEIPT

CONTRACT = """---
role: reviewer
title: Reviewer
description: Reviews a change against its specification and returns findings with evidence.
skill: review
hosts:
  claude-code:
    status: native
    tools: [Read, Grep, Glob]
    maxTurns: 20
    background: false
  codex:
    status: emulated
    sandbox_mode: read-only
---
# Reviewer

## Purpose

Compare the diff with the spec. Return "findings" with evidence.
"""


def make_bundle(tmp_path: Path, bundle: str, contract: str = CONTRACT) -> InstalledBundle:
    root = tmp_path / bundle
    (root / "subagents").mkdir(parents=True)
    (root / "subagents/reviewer.md").write_text(contract)
    (root / "bundle.toml").write_text(f'''schema = 1
name = "{bundle}"
version = "0.1.0"
[[assets]]
id = "reviewer"
kind = "subagent"
source = "subagents/reviewer.md"
''')
    return InstalledBundle(f"{bundle}-content", "0.1.0", load_bundle(root))


def test_read_contract() -> None:
    contract = read_contract(CONTRACT.encode(), "x", "reviewer")
    assert (contract.role, contract.title, contract.skill) == ("reviewer", "Reviewer", "review")
    assert contract.hosts["claude-code"].status == "native"
    assert contract.hosts["claude-code"].settings == (
        ("tools", ["Read", "Grep", "Glob"]),
        ("maxTurns", 20),
        ("background", False),
    )
    assert contract.hosts["codex"].settings == (("sandbox_mode", "read-only"),)
    assert contract.body.startswith("# Reviewer")


@pytest.mark.parametrize(
    ("replacement", "match"),
    [
        (("role: reviewer", "role: Reviewer_X"), "lowercase slug"),
        (("role: reviewer", "role: other"), "must equal the asset id"),
        (("title: Reviewer", "title: ''"), "title is required"),
        (("skill: review", "skill: Bad Skill"), "skill must be a lowercase slug"),
        (("  codex:", "  gemini:"), "unknown host"),
        (("status: native", "status: maybe"), "status must be one of"),
        (("    tools: [Read, Grep, Glob]", "    rocket: true"), "not allowed"),
        (("    maxTurns: 20", "    maxTurns: [1, 2]"), "must be a string, integer, boolean or list"),
        (("hosts:", "extra: 1\nhosts:"), "unknown frontmatter keys"),
    ],
)
def test_read_contract_rejects(replacement: tuple[str, str], match: str) -> None:
    body = CONTRACT.replace(*replacement)
    assert body != CONTRACT
    with pytest.raises(BundleError, match=match):
        read_contract(body.encode(), "x", "reviewer")


def test_read_contract_rejects_missing_hosts_and_empty_body() -> None:
    with pytest.raises(BundleError, match="hosts must be a nonempty mapping"):
        read_contract(b"---\nrole: r\ntitle: T\ndescription: D\n---\nbody\n", "x")
    with pytest.raises(BundleError, match=r"body .* is empty"):
        read_contract(b"---\nrole: r\ntitle: T\ndescription: D\nhosts:\n  codex: native\n---\n", "x")
    with pytest.raises(BundleError, match="requires YAML frontmatter"):
        read_contract(b"plain\n", "x")


def test_render_claude_and_codex_projections() -> None:
    contract = read_contract(CONTRACT.encode(), "x")
    claude = render("claude-code", contract, ".devkit/managed/team/subagents/reviewer.md")
    assert claude is not None
    head, body = claude.decode().split("---\n")[1:]
    assert yaml.safe_load(head) == {
        "name": "reviewer",
        "description": "Reviewer. Reviews a change against its specification and returns findings with evidence.",
        "tools": ["Read", "Grep", "Glob"],
        "maxTurns": 20,
        "background": False,
    }
    assert body.startswith("Role contract: `.devkit/managed/team/subagents/reviewer.md`. Procedure: skill `review`.")
    assert "Host projection: native." in body and "# Reviewer" in body

    codex = render("codex", contract, ".devkit/managed/team/subagents/reviewer.md")
    assert codex is not None
    data = tomllib.loads(codex.decode())
    assert data["name"] == "reviewer" and data["sandbox_mode"] == "read-only"
    assert "Host projection: emulated." in data["developer_instructions"]
    assert "does not enforce" in data["developer_instructions"]
    assert 'Return "findings" with evidence.' in data["developer_instructions"]


def test_render_antigravity_projection_carries_fixed_keys() -> None:
    body = CONTRACT.replace(
        "  codex:\n",
        '  antigravity:\n    status: native\n    tools: [view_file, grep_search]\n    commandExecutionPolicy: "off"\n  codex:\n',
    )
    contract = read_contract(body.encode(), "x")
    rendered = render("antigravity", contract, ".devkit/managed/team/subagents/reviewer.md")
    assert rendered is not None
    head = rendered.decode().split("---\n")[1]
    assert yaml.safe_load(head) == {
        "name": "reviewer",
        "description": "Reviewer. Reviews a change against its specification and returns findings with evidence.",
        "subagent": True,
        "mainAgent": False,
        "tools": ["view_file", "grep_search"],
        "commandExecutionPolicy": "off",
    }
    assert projection_path("antigravity", "reviewer") == ".agents/agents/reviewer.md"


def test_render_unsupported_host_yields_no_file_and_missing_host_fails() -> None:
    contract = read_contract(CONTRACT.replace("status: emulated", "status: unsupported").encode(), "x")
    assert render("codex", contract, "p") is None
    only_codex = CONTRACT.replace(
        "  claude-code:\n    status: native\n    tools: [Read, Grep, Glob]\n    maxTurns: 20\n    background: false\n",
        "",
    )
    contract = read_contract(only_codex.encode(), "x")
    with pytest.raises(BundleError, match="no projection for claude-code"):
        render("claude-code", contract, "p")


def test_manifest_validates_contract_source(tmp_path: Path) -> None:
    with pytest.raises(BundleError, match="must equal the asset id"):
        make_bundle(tmp_path, "bad", CONTRACT.replace("role: reviewer", "role: critic"))
    root = tmp_path / "dir"
    (root / "subagents/reviewer").mkdir(parents=True)
    (root / "subagents/reviewer/x.md").write_text("x")
    (root / "bundle.toml").write_text(
        'schema = 1\nname = "dir"\nversion = "0.1.0"\n[[assets]]\nid = "reviewer"\nkind = "subagent"\nsource = "subagents/reviewer"\n'
    )
    with pytest.raises(BundleError, match="single Markdown file"):
        load_bundle(root)


def test_sync_projects_contract_per_agent(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    installed = [make_bundle(tmp_path, "team")]
    update_config(target, presets={"team": ["all"]})
    with pytest.raises(BundleError, match="no projection for antigravity"):
        sync_project(target, installed)  # every host is a target by default; the contract must name each
    update_config(target, agents=["codex", "claude-code"])
    sync_project(target, installed)

    assert (target / ".devkit/managed/team/subagents/reviewer.md").read_text() == CONTRACT
    claude = target / projection_path("claude-code", "reviewer")
    codex = target / projection_path("codex", "reviewer")
    assert claude.read_bytes() == render(
        "claude-code", read_contract(CONTRACT.encode(), "x"), ".devkit/managed/team/subagents/reviewer.md"
    )
    assert tomllib.loads(codex.read_text())["name"] == "reviewer"
    receipt = json.loads((target / RECEIPT).read_text())
    record = next(a for a in receipt["assets"] if a["id"] == "reviewer")
    assert record["paths"] == sorted(
        [".devkit/managed/team/subagents/reviewer.md", ".claude/agents/reviewer.md", ".codex/agents/reviewer.toml"]
    )

    # Unsupported host: the projection disappears while the contract stays managed.
    root = installed[0].bundle.root
    (root / "subagents/reviewer.md").write_text(CONTRACT.replace("status: emulated", "status: unsupported"))
    sync_project(target, [InstalledBundle("team-content", "0.1.1", load_bundle(root))])
    assert not codex.exists() and claude.exists()

    # A host the contract does not mention is an explicit error, never a silent skip.
    (root / "subagents/reviewer.md").write_text(
        CONTRACT.replace("  codex:\n    status: emulated\n    sandbox_mode: read-only\n", "")
    )
    with pytest.raises(BundleError, match="no projection for codex"):
        sync_project(target, [InstalledBundle("team-content", "0.1.2", load_bundle(root))])


def test_override_of_contract_is_rendered_and_cited(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    installed = [make_bundle(tmp_path, "team")]
    update_config(target, presets={"team": ["all"]}, agents=["claude-code"])
    sync_project(target, installed)
    override = target / ".devkit/overrides/team/subagents/reviewer.md"
    override.parent.mkdir(parents=True)
    override.write_text(CONTRACT.replace("maxTurns: 20", "maxTurns: 5"))
    sync_project(target, installed)
    projected = (target / ".claude/agents/reviewer.md").read_text()
    assert "maxTurns: 5" in projected
    assert "Role contract: `.devkit/overrides/team/subagents/reviewer.md`." in projected
    receipt = json.loads((target / RECEIPT).read_text())
    assert receipt["overrides"]["team"]["reviewer"]["kind"] == "subagent"


def test_contract_extension_keys_are_kept_but_never_rendered(tmp_path: Path) -> None:
    contract = CONTRACT.replace(
        "skill: review\n", "skill: review\nx-model-profile: {tier: strong, temperature: 0}\nx-git-actions: [commit]\n"
    )
    parsed = read_contract(contract.encode(), "x", "reviewer")
    assert parsed.extensions == (
        ("x-model-profile", {"tier": "strong", "temperature": 0}),
        ("x-git-actions", ["commit"]),
    )
    for agent in ("claude-code", "codex"):
        rendered = render(agent, parsed, ".devkit/managed/team/subagents/reviewer.md")
        assert rendered is not None and b"x-" not in rendered and b"strong" not in rendered
    with pytest.raises(BundleError, match=r"unknown frontmatter keys \['model_profile'\] \(extensions use x-<name>\)"):
        read_contract(CONTRACT.replace("skill: review\n", "skill: review\nmodel_profile: strong\n").encode(), "x")
    with pytest.raises(BundleError, match="unknown frontmatter keys"):
        read_contract(CONTRACT.replace("skill: review\n", "skill: review\nx-Bad: 1\n").encode(), "x")
    # The managed copy is the contract verbatim, so the keys stay readable to other tools.
    item = make_bundle(tmp_path, "team", contract)
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"team": ["all"]}, agents=["claude-code"])
    sync_project(target, [item])
    assert "x-model-profile" in (target / ".devkit/managed/team/subagents/reviewer.md").read_text()
    assert "x-model-profile" not in (target / ".claude/agents/reviewer.md").read_text()
