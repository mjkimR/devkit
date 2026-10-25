from __future__ import annotations

import json
import tomllib
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.bundles.subagents import (
    projection_path,
    read_contract,
    render_projection,
)
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.receipt import RECEIPT_PATH

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
  antigravity: unsupported
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
        (("  antigravity: unsupported\n", ""), r"hosts must name every agent; missing \['antigravity'\]"),
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
        read_contract(CONTRACT.split("# Reviewer")[0].encode(), "x")
    with pytest.raises(BundleError, match="requires YAML frontmatter"):
        read_contract(b"plain\n", "x")


def test_render_claude_and_codex_projections() -> None:
    contract = read_contract(CONTRACT.encode(), "x")
    claude = render_projection("claude-code", contract, ".devkit/managed/team/subagents/reviewer.md")
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

    codex = render_projection("codex", contract, ".devkit/managed/team/subagents/reviewer.md")
    assert codex is not None
    data = tomllib.loads(codex.decode())
    assert data["name"] == "reviewer" and data["sandbox_mode"] == "read-only"
    assert "Host projection: emulated." in data["developer_instructions"]
    assert "does not enforce" in data["developer_instructions"]
    assert 'Return "findings" with evidence.' in data["developer_instructions"]


def test_render_antigravity_projection_carries_fixed_keys() -> None:
    body = CONTRACT.replace(
        "  antigravity: unsupported\n",
        '  antigravity:\n    status: native\n    tools: [view_file, grep_search]\n    commandExecutionPolicy: "off"\n',
    )
    contract = read_contract(body.encode(), "x")
    rendered = render_projection("antigravity", contract, ".devkit/managed/team/subagents/reviewer.md")
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
    assert render_projection("codex", contract, "p") is None
    # A parsed contract names every host; one built in code may not.
    only_codex = replace(contract, hosts={"codex": contract.hosts["codex"]})
    with pytest.raises(BundleError, match="no projection for claude-code"):
        render_projection("claude-code", only_codex, "p")


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
    sync_project(target, installed)  # every host is a target by default; antigravity is unsupported
    assert not (target / projection_path("antigravity", "reviewer")).exists()

    assert (target / ".devkit/managed/team/subagents/reviewer.md").read_text() == CONTRACT
    claude = target / projection_path("claude-code", "reviewer")
    codex = target / projection_path("codex", "reviewer")
    assert claude.read_bytes() == render_projection(
        "claude-code", read_contract(CONTRACT.encode(), "x"), ".devkit/managed/team/subagents/reviewer.md"
    )
    assert tomllib.loads(codex.read_text())["name"] == "reviewer"
    receipt = json.loads((target / RECEIPT_PATH).read_text())
    record = next(a for a in receipt["assets"] if a["id"] == "reviewer")
    assert record["paths"] == sorted(
        [".devkit/managed/team/subagents/reviewer.md", ".claude/agents/reviewer.md", ".codex/agents/reviewer.toml"]
    )

    # Unsupported host: the projection disappears while the contract stays managed.
    root = installed[0].bundle.root
    (root / "subagents/reviewer.md").write_text(CONTRACT.replace("status: emulated", "status: unsupported"))
    sync_project(target, [InstalledBundle("team-content", "0.1.1", load_bundle(root))])
    assert not codex.exists() and claude.exists()

    # A host the contract does not mention is an invalid bundle, never a silent skip.
    (root / "subagents/reviewer.md").write_text(
        CONTRACT.replace("  codex:\n    status: emulated\n    sandbox_mode: read-only\n", "")
    )
    with pytest.raises(BundleError, match=r"hosts must name every agent; missing \['codex'\]"):
        load_bundle(root)


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
    receipt = json.loads((target / RECEIPT_PATH).read_text())
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
        rendered = render_projection(agent, parsed, ".devkit/managed/team/subagents/reviewer.md")
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


@pytest.mark.parametrize("level", ["inherit", "light", "standard", "deep"])
def test_source_level_projects_all_hosts(level: str) -> None:
    body = CONTRACT.replace("skill: review", f"level: {level}\nskill: review").replace(
        "  antigravity: unsupported", "  antigravity: native"
    )
    contract = read_contract(body.encode(), "x")
    for host in ("claude-code", "codex", "antigravity"):
        rendered = render_projection(host, contract, "contract.md")
        assert rendered is not None
        data = (
            tomllib.loads(rendered.decode()) if host == "codex" else yaml.safe_load(rendered.decode().split("---\n")[1])
        )
        assert "level" not in data
        assert ("model" in data) == (level != "inherit")
        assert "maxTurns" in data if host == "claude-code" else True
        if host == "antigravity":
            assert "effort" not in data


@pytest.mark.parametrize("native", ["    model: custom\n", "    model_reasoning_effort: high\n"])
def test_source_level_conflicts_with_native_fields(native: str) -> None:
    body = CONTRACT.replace("skill: review", "level: inherit\nskill: review").replace(
        "    sandbox_mode: read-only\n", "    sandbox_mode: read-only\n" + native
    )
    with pytest.raises(BundleError, match="conflicts"):
        read_contract(body.encode(), "x")


def test_policy_sync_reset_digests_dry_run_and_foreign_files(tmp_path: Path) -> None:
    from devkit_dist.features.distribution.usecases.status import get_project_status

    target = tmp_path / "consumer"
    target.mkdir()
    item = make_bundle(tmp_path, "team")
    update_config(target, presets={"team": ["all"]}, agents=["codex"])
    config = target / ".devkit/config.toml"
    initial_config = config.read_text()
    config.write_text(initial_config + '\n[subagents]\ndefault_level = "deep"\n')
    sync_project(target, [item])
    projection = target / ".codex/agents/reviewer.toml"
    deep = projection.read_bytes()
    assert tomllib.loads(deep.decode())["model"] == "gpt-6-astra"
    receipt = (target / RECEIPT_PATH).read_bytes()
    foreign = target / ".codex/agents/foreign.toml"
    foreign.write_text("foreign")
    config.write_text(initial_config + '\n[subagents]\ndefault_level = "inherit"\n')
    dry = sync_project(target, [item], dry_run=True)
    assert any(action.path == ".codex/agents/reviewer.toml" for action in dry.actions)
    assert projection.read_bytes() == deep and (target / RECEIPT_PATH).read_bytes() == receipt
    # Status uses the same preflight; it reports drift without modifying the deployment.
    assert any(error.code == "NOT_SYNCHRONIZED" for error in get_project_status(target, [item]).errors)
    sync_project(target, [item])
    assert "model" not in tomllib.loads(projection.read_text())
    assert (target / RECEIPT_PATH).read_bytes() != receipt
    assert foreign.read_text() == "foreign"
    assert sync_project(target, [item]).actions == []
    assert config.read_text().startswith(initial_config)


@pytest.mark.parametrize(
    "tail",
    [
        '[subagents.roles."missing:reviewer"]\nlevel="deep"\n',
        '[subagents.roles."team:missing"]\nlevel="deep"\n',
        '[subagents.levels.deep.antigravity]\nmodel="por"\n',
    ],
)
def test_invalid_policy_leaves_owned_files_unchanged(tmp_path: Path, tail: str) -> None:
    from devkit_dist.base.errors import ConfigError

    target = tmp_path / "consumer"
    target.mkdir()
    item = make_bundle(tmp_path, "team")
    update_config(target, presets={"team": ["all"]}, agents=["codex"])
    sync_project(target, [item])
    before = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
    config = target / ".devkit/config.toml"
    config.write_text(config.read_text() + "\n" + tail)
    before[config.relative_to(target)] = config.read_bytes()
    with pytest.raises(ConfigError):
        sync_project(target, [item])
    assert {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()} == before


def test_explicit_project_inherit_clears_native_escape_hatch(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    body = CONTRACT.replace(
        "    sandbox_mode: read-only", "    sandbox_mode: read-only\n    model: custom\n    model_reasoning_effort: max"
    )
    item = make_bundle(tmp_path, "team", body)
    update_config(target, presets={"team": ["all"]}, agents=["codex"])
    sync_project(target, [item])
    projection = target / ".codex/agents/reviewer.toml"
    assert tomllib.loads(projection.read_text())["model"] == "custom"
    config = target / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[subagents.roles."team:reviewer"]\nlevel="inherit"\n')
    sync_project(target, [item])
    data = tomllib.loads(projection.read_text())
    assert not {"model", "model_reasoning_effort"} & data.keys()
    assert data["sandbox_mode"] == "read-only"


def test_native_variants_stay_verbatim_and_reject_role_overrides(tmp_path: Path) -> None:
    from devkit_dist.base.errors import ConfigError

    native = 'name = "reviewer"\ndescription = "Native"\nmodel = "custom"\ndeveloper_instructions = "body"\n'
    root = tmp_path / "native"
    root.mkdir()
    (root / "reviewer.toml").write_text(native)
    (root / "bundle.toml").write_text(
        'schema=1\nname="native"\nversion="0.1.0"\n[[assets]]\nid="reviewer"\nkind="subagent"\n[assets.variants]\ncodex="reviewer.toml"\n'
    )
    item = InstalledBundle("native", "0.1.0", load_bundle(root))
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"native": ["all"]}, agents=["codex"])
    config = target / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[subagents]\ndefault_level="deep"\n')
    sync_project(target, [item])
    assert (target / ".codex/agents/reviewer.toml").read_text() == native
    config.write_text(config.read_text() + '\n[subagents.roles."native:reviewer"]\nlevel="inherit"\n')
    with pytest.raises(ConfigError, match="common subagent"):
        sync_project(target, [item])


def test_installed_unselected_role_override_is_dormant(tmp_path: Path) -> None:
    item = make_bundle(tmp_path, "team")
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"team": ["all"]}, agents=["codex"])
    config = target / ".devkit/config.toml"
    config.write_text(
        'schema=1\nagents=["codex"]\n[presets]\nteam=false\n[subagents.roles."team:missing"]\nlevel="deep"\n'
    )
    sync_project(target, [item])
    assert not (target / ".codex/agents/reviewer.toml").exists()


def test_templated_source_level_and_bundle_plan(tmp_path: Path) -> None:
    from devkit_dist.features.distribution.services.installation.plan import plan_bundle

    item = make_bundle(tmp_path, "team", CONTRACT.replace("skill: review", "level: deep\nskill: review"))
    source = item.bundle.root / "subagents/reviewer.md"
    source.rename(source.with_suffix(".md.jinja"))
    manifest = item.bundle.root / "bundle.toml"
    manifest.write_text(manifest.read_text().replace("reviewer.md", "reviewer.md.jinja"))
    item = InstalledBundle("team-content", "0.1.0", load_bundle(item.bundle.root))
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"team": ["all"]}, agents=["codex"])
    sync_project(target, [item])
    projection = target / ".codex/agents/reviewer.toml"
    data = tomllib.loads(projection.read_text())
    assert data["model"] == "gpt-6-astra" and data["model_reasoning_effort"] == "high"
    planned = plan_bundle(item.bundle, agents=["codex"])
    assert (
        next(file.sha256 for file in planned.files if file.destination == ".codex/agents/reviewer.toml")
        == json.loads((target / RECEIPT_PATH).read_text())["files"][".codex/agents/reviewer.toml"]["sha256"]
    )


@pytest.mark.parametrize("common", [True, False])
def test_preset_excluded_common_is_dormant_but_variant_override_is_invalid(tmp_path: Path, common: bool) -> None:
    from devkit_dist.base.errors import ConfigError

    item = make_bundle(tmp_path, "team")
    root = item.bundle.root
    manifest = root / "bundle.toml"
    text = manifest.read_text()
    if not common:
        (root / "native.toml").write_text('name="reviewer"\ndescription="native"\ndeveloper_instructions="body"\n')
        text = text.replace('source = "subagents/reviewer.md"', '[assets.variants]\ncodex="native.toml"')
    (root / "note.md").write_text("Retained document")
    manifest.write_text(
        text + '\n[[assets]]\nid="note"\nkind="document"\nsource="note.md"\n[presets.empty]\nassets=["note"]\n'
    )
    item = InstalledBundle("team-content", "0.1.0", load_bundle(root))
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"team": ["empty"]}, agents=["codex"])
    config = target / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[subagents.roles."team:reviewer"]\nlevel="deep"\n')
    if common:
        sync_project(target, [item])
        assert not (target / ".codex/agents/reviewer.toml").exists()
    else:
        with pytest.raises(ConfigError, match="common subagent"):
            sync_project(target, [item])
