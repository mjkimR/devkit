"""The ``devkit`` guide bundle shipped inside devkit-dist: distribution guidance and shared general subagents.

The harness guidance (rules, gates, workflows, ``devkit run``) ships with devkit-agt in the ``harness`` bundle
(``ADR-dist-bundles-compatibility``), so a standalone installation deploys no directive it cannot follow. The
``role-worker`` subagent is the tool-limited child other bundles' skills delegate role files to
(``ADR-role-worker-subagent``).
"""

from __future__ import annotations

import re
import tomllib
from importlib import resources
from pathlib import Path

import pytest
import yaml
from devkit_dist.features.distribution.models.errors import SelectionError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.bundles.subagents import projection_path, read_contract
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.context import GetContext
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.guidance import assert_rule

INSTRUCTIONS = ["consumption", "in-repo-bundle", "resource-kinds"]
SUBAGENTS = ["role-worker"]
CLAUDE_TOOLS = ["Read", "Grep", "Glob", "Bash", "Edit", "Write", "WebSearch", "WebFetch", "Agent"]
ANTIGRAVITY_TOOLS = ["view_file", "grep_search", "replace_file_content", "run_command"]
# Commands of devkit-agt: never a directive of this bundle.
HARNESS_COMMANDS = ("devkit rules", "devkit gate", "devkit workflow", "devkit run", "devkit worktree")


def _root() -> Path:
    path = resources.files("devkit_dist.bundles.devkit").joinpath("bundle")
    assert isinstance(path, Path)
    return path


def test_guide_bundle_is_valid_and_its_default_holds_instructions_and_shared_subagents() -> None:  # AC-02
    bundle = load_bundle(_root())
    assert bundle.name == "devkit"
    assert bundle.default_preset == "core" and bundle.auto_select
    assert bundle.preset_names == ["all", "core"]
    assert bundle.select(["core"]) == set(INSTRUCTIONS + SUBAGENTS) == {asset.id for asset in bundle.assets}
    kinds = {asset.id: asset.kind for asset in bundle.assets}
    assert kinds == {**dict.fromkeys(INSTRUCTIONS, "instruction"), **dict.fromkeys(SUBAGENTS, "subagent")}
    assert bundle.constitution is not None
    constitution = bundle.constitution.read_text("utf-8")
    assert len(constitution.splitlines()) <= 100
    # get-context returns the instruction catalog next to the constitution; the constitution does not repeat it.
    assert not any(f"`{name}`:" in constitution for name in INSTRUCTIONS)


def test_the_bundle_names_no_harness_command() -> None:
    files = [
        _root() / "AGENTS.md",
        *sorted((_root() / "instructions").glob("*.md")),
        *sorted((_root() / "subagents").glob("*.md")),
    ]
    found = {path.name: [cmd for cmd in HARNESS_COMMANDS if cmd in path.read_text("utf-8")] for path in files}
    assert {name: commands for name, commands in found.items() if commands} == {}


def test_role_worker_projects_for_every_host_with_inherited_model(tmp_path: Path) -> None:  # AC-01, AC-02
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": ["core"]}, agents=["claude-code", "codex", "antigravity"])
    sync_project(target, [InstalledBundle("devkit-dist", "0.1.0", load_bundle(_root()))])
    assert (target / ".devkit/managed/devkit/subagents/role-worker.md").is_file()
    projections = {
        path.relative_to(target).as_posix()
        for directory in (".claude/agents", ".codex/agents", ".agents/agents")
        for path in (target / directory).glob("*")
    }
    assert projections == {projection_path(host, "role-worker") for host in ("claude-code", "codex", "antigravity")}

    claude_head, claude_prompt = (target / ".claude/agents/role-worker.md").read_text().split("---\n")[1:]
    claude = yaml.safe_load(claude_head)
    assert claude["name"] == "role-worker" and claude["tools"] == CLAUDE_TOOLS
    assert not {"model", "effort"} & claude.keys()
    assert "Host projection: native." in claude_prompt

    codex = tomllib.loads((target / ".codex/agents/role-worker.toml").read_text())
    assert codex["sandbox_mode"] == "workspace-write"
    assert not {"model", "model_reasoning_effort"} & codex.keys()
    assert "Host projection: emulated." in codex["developer_instructions"]

    antigravity_head, antigravity_prompt = (target / ".agents/agents/role-worker.md").read_text().split("---\n")[1:]
    antigravity = yaml.safe_load(antigravity_head)
    assert antigravity["tools"] == ANTIGRAVITY_TOOLS and antigravity["subagent"] is True
    assert antigravity["commandExecutionPolicy"] == "sandbox"
    assert "model" not in antigravity
    assert "Host projection: unverified." in antigravity_prompt

    # The subagent adds nothing to the root guidance block.
    assert "role-worker" not in (target / "AGENTS.md").read_text()


def test_role_worker_is_neutral_and_follows_the_named_role_file() -> None:  # AC-03
    contract = read_contract((_root() / "subagents/role-worker.md").read_bytes(), "devkit", "role-worker")
    assert contract.level is None and contract.skill is None
    listing = f"{contract.role} {contract.title} {contract.description}".lower()
    for name in ("research", "uiux", "design", "explore", "critic", "investigator", "devkit", "skill", "bundle"):
        assert name not in listing, name
    body = contract.body
    assert_rule(body, "prompt names a role file", "read it before any other action", "assignment contract")
    assert_rule(body, "missing or unreadable", "stop")
    assert_rule(body, "names no role file", "treat the prompt as the assignment")
    assert_rule(body, "delegate only work that is independent")
    assert_rule(body, "prefer", "`role-worker`", "fitting dedicated subagent", "over `general-purpose`")


def test_the_constitution_keeps_the_distribution_contracts() -> None:
    constitution = (_root() / "AGENTS.md").read_text("utf-8")
    for directive in (
        "`devkit-playbook`",  # playbooks are explicit
        "`devkit add <bundle>[:<preset>]`",  # selection
        "`devkit remove <bundle>`",
    ):
        assert directive in constitution, directive
    assert_rule(constitution, "instruction body", "only when", "header", "matches")  # instruction bodies on demand
    assert_rule(constitution, "commit", "`.devkit/installation.json`")  # the receipt travels with the change
    assert "Snapshot gates" not in constitution  # the snapshot-gate contract is the harness's


def test_the_in_repo_example_never_declares_both_devkit_requirements() -> None:
    text = (_root() / "instructions/in-repo-bundle.md").read_text("utf-8")
    blocks = [block for block in re.findall(r"```toml\n(.*?)```", text, re.DOTALL) if "[dependency-groups]" in block]
    groups = [
        dependencies
        for block in blocks
        for table in [tomllib.loads(block)]
        for dependencies in table.get("dependency-groups", {}).values()
    ]
    assert groups, "the example declares a dependency group"
    for dependencies in groups:
        names = {re.split(r"[\s\[@=<>]", dependency, maxsplit=1)[0] for dependency in dependencies}
        assert not {"devkit-dist", "devkit-agt"} <= names
    assert_rule(text, "`devkit-agt`", "instead of", "`devkit-dist`")


@pytest.mark.parametrize("presets", [["core", "run"], ["run"]])
def test_the_run_preset_left_the_bundle(tmp_path: Path, presets: list[str]) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": presets}, agents=[])
    with pytest.raises(SelectionError) as raised:
        sync_project(target, [InstalledBundle("devkit-dist", "0.1.0", load_bundle(_root()))])
    assert raised.value.code == "SELECTION_INVALID"
    assert raised.value.fix == "uv run devkit list"
    assert raised.value.target_files == (".devkit/config.toml",)
    assert raised.value.details == (
        "uv run devkit sync --preset devkit:all",
        "uv run devkit sync --preset devkit:core",
    )


def test_the_all_preset_deploys_no_run_guidance(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": ["all"]}, agents=[])
    sync_project(target, [InstalledBundle("devkit-dist", "0.1.0", load_bundle(_root()))])
    assert not (target / ".devkit/managed/devkit/instructions/devkit-run.md").exists()
    assert "devkit run" not in (target / "AGENTS.md").read_text()


def test_guide_bundle_context_delivers_constitution_and_headers(tmp_path: Path) -> None:
    bundle = load_bundle(_root())
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": ["core"]}, agents=[])
    sync_project(target, [InstalledBundle("devkit", "0.1.0", bundle)])
    context = GetContext().execute(target, "devkit").to_dict()
    assert context["constitution"] and "`devkit-playbook`" in context["constitution"]
    headers = {entry["header"].split("\n", 1)[0] for entry in context["instructions"]}
    assert headers == {f"name: {name}" for name in INSTRUCTIONS}
    for entry in context["instructions"]:
        header = entry["header"]
        assert "description: Read before" in header
        assert header.isascii(), header
        assert Path(entry["path"]).is_file()


def test_an_unsynchronized_bundle_names_a_runnable_fix_and_the_synchronized_bundles(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"devkit": ["core"]}, agents=[])
    sync_project(target, [InstalledBundle("devkit", "0.1.0", load_bundle(_root()))])
    with pytest.raises(SelectionError) as raised:
        GetContext().execute(target, "nope")
    # One exact command, never a guess such as `devkit add nope` for a name that may not exist.
    assert raised.value.fix == "uv run devkit list"
    assert raised.value.details == ("synchronized bundles: devkit",)
