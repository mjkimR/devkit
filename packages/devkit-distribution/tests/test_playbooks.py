from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from devkit_distribution.bundles import BundleError, load_bundle
from devkit_distribution.bundles.playbooks import read_playbook_header
from devkit_distribution.cli import cli
from devkit_distribution.installation.context import get_context
from devkit_distribution.installation.discovery import InstalledBundle
from devkit_distribution.installation.playbook_search import bm25_scores, search_playbooks
from devkit_distribution.installation.playbook_skill import MANAGED_ROOT
from devkit_distribution.installation.sync import sync_project
from devkit_distribution.installation.transaction import JOURNAL, RECEIPT


def make_bundle(tmp_path: Path, bundle: str, *, directory: bool = False) -> InstalledBundle:
    root = tmp_path / bundle
    root.mkdir()
    (root / "AGENTS.md").write_text("# Shared contracts\n")
    (root / "guide.md").write_text("---\nname: testing\ndescription: Testing constraints.\n---\nInstruction body.\n")
    source = "recovery/SKILL.md" if directory else "recovery.md"
    (root / source).parent.mkdir(exist_ok=True)
    (root / source).write_text(
        "---\nname: restore-replica\ndescription: Restore a PostgreSQL replica.\n"
        "aliases:\n  - postgres standby repair\n  - wal failure\n---\n\nBODY_ONLY_SECRET\n"
    )
    if directory:
        (root / "recovery/reference.md").write_text("Resource containing bodyonlytoken.\n")
    (root / "release.md").write_text(
        "---\nname: publish-release\ndescription: Publish a software release.\n---\nbodyonlytoken\n"
    )
    (root / "bundle.toml").write_text(f'''schema = 1
name = "{bundle}"
version = "0.1.0"
[[assets]]
id = "recovery"
kind = "playbook"
source = "{"recovery" if directory else source}"
[[assets]]
id = "release"
kind = "playbook"
source = "release.md"
[[assets]]
id = "guide"
kind = "instruction"
source = "guide.md"
[presets.guidance]
assets = ["guide"]
[presets.recovery]
assets = ["recovery", "guide"]
''')
    return InstalledBundle(f"{bundle}-content", "0.1.0", load_bundle(root))


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    return root


def test_search_aliases_across_bundles_without_body_disclosure(tmp_path: Path, target: Path) -> None:
    installed = [make_bundle(tmp_path, "team", directory=True), make_bundle(tmp_path, "ops")]
    sync_project(target, installed)
    nested = target / "nested"
    nested.mkdir()
    result = search_playbooks(nested, "POSTGRES standby repair")
    assert [entry["bundle"] for entry in result["results"]] == ["ops", "team"]
    assert all(entry["id"] == "recovery" for entry in result["results"])
    assert "BODY_ONLY_SECRET" not in json.dumps(result)
    assert "BODY_ONLY_SECRET" in Path(result["results"][0]["path"]).read_text()
    assert search_playbooks(target, "bodyonlytoken")["results"] == []
    assert search_playbooks(target, "unrelatednomatch")["results"] == []
    assert "restore-replica" not in str(get_context(target, "team"))
    assert get_context(target, "team")["constitution"] == "# Shared contracts\n"


def test_search_caps_threshold_and_cli_budget(tmp_path: Path, target: Path) -> None:
    sync_project(target, [make_bundle(tmp_path, "team"), make_bundle(tmp_path, "ops")])
    limited = search_playbooks(target, "replica", limit=1)
    assert len(limited["results"]) == 1
    assert limited["truncated"] is True
    assert search_playbooks(target, "replica", min_score=100)["results"] == []
    runner = CliRunner()
    result = runner.invoke(cli, ["playbook", "search", "replica", "--target", str(target), "--max-bytes", "1024"])
    assert result.exit_code == 0, result.output
    assert len(result.output.encode()) <= 1024
    assert "BODY_ONLY_SECRET" not in result.output
    for query in ["복제 복구", "!!!", "x" * 513]:
        assert runner.invoke(cli, ["playbook", "search", query, "--target", str(target)]).exit_code == 1
    for option, value in [("--limit", "0"), ("--min-score", "nan"), ("--max-bytes", "100")]:
        assert (
            runner.invoke(cli, ["playbook", "search", "replica", "--target", str(target), option, value]).exit_code != 0
        )


def test_generated_skill_policies_and_sync_lifecycle(tmp_path: Path, target: Path) -> None:
    installed = [make_bundle(tmp_path, "team"), make_bundle(tmp_path, "ops")]
    sync_project(target, installed, agents=["codex", "claude-code"])
    assert (target / MANAGED_ROOT / "SKILL.md").exists()
    codex = target / ".agents/skills/devkit-playbook"
    claude = target / ".claude/skills/devkit-playbook"
    policy = yaml.safe_load((codex / "agents/openai.yaml").read_text())
    assert policy["policy"]["allow_implicit_invocation"] is False
    frontmatter = (claude / "SKILL.md").read_text().split("---")[1]
    assert yaml.safe_load(frontmatter)["disable-model-invocation"] is True
    assert "restore-replica" not in (codex / "SKILL.md").read_text()
    assert not (target / ".agents/skills/recovery").exists()
    receipt = (target / RECEIPT).read_bytes()
    assert sync_project(target, installed)["actions"] == []
    assert (target / RECEIPT).read_bytes() == receipt
    sync_project(target, installed, presets={"team": "guidance"})
    assert [item["bundle"] for item in search_playbooks(target, "replica")["results"]] == ["ops"]
    sync_project(target, installed, presets={"ops": "guidance"})
    assert not (codex / "SKILL.md").exists()
    assert not (target / MANAGED_ROOT / "SKILL.md").exists()
    assert search_playbooks(target, "replica")["results"] == []
    sync_project(target, installed, all_assets=True, agents=[])
    assert (target / MANAGED_ROOT / "SKILL.md").exists()
    assert not (claude / "SKILL.md").exists()
    sync_project(target, [])
    assert not (target / MANAGED_ROOT / "SKILL.md").exists()


def test_generated_skill_collision_and_user_edits_are_protected(tmp_path: Path, target: Path) -> None:
    installed = [make_bundle(tmp_path, "team")]
    skill = target / ".agents/skills/devkit-playbook/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("user owned")
    with pytest.raises(BundleError, match="unowned"):
        sync_project(target, installed, agents=["codex"])
    assert skill.read_text() == "user owned"
    skill.unlink()
    sync_project(target, installed, agents=["codex"])
    skill.write_text("user edit")
    with pytest.raises(BundleError, match="user-modified"):
        sync_project(target, [])


def test_search_rejects_modified_files_and_pending_transactions(tmp_path: Path, target: Path) -> None:
    sync_project(target, [make_bundle(tmp_path, "team")])
    (target / JOURNAL).write_text("{}")
    with pytest.raises(BundleError, match="pending transaction"):
        search_playbooks(target, "replica")
    (target / JOURNAL).unlink()
    (target / ".devkit/managed/team/recovery.md").write_text("unowned changes")
    with pytest.raises(BundleError, match="modified context"):
        search_playbooks(target, "replica")


@pytest.mark.parametrize(
    "header",
    [
        "name: example\n",
        "name: 123\ndescription: Example\n",
        "name: example\ndescription: [Example]\n",
        "name: example\ndescription: Example\naliases: text\n",
        "name: example\ndescription: Example\naliases: [123]\n",
        "name: example\ndescription: Example\ntags: [recovery]\n",
        "name: example\nname: duplicate\ndescription: Example\n",
        "name: example\ndescription: 복구\n",
        "name: example\ndescription: Example\naliases: [복구]\n",
        "name: example\ndescription: [broken\n",
    ],
)
def test_invalid_metadata_is_rejected_at_bundle_validation(tmp_path: Path, header: str) -> None:
    item = make_bundle(tmp_path, "team")
    (item.bundle.root / "recovery.md").write_text(f"---\n{header}---\nBODY_ONLY_SECRET\n")
    with pytest.raises(BundleError):
        load_bundle(item.bundle.root)


def test_multiline_description_and_optional_aliases() -> None:
    header = read_playbook_header(
        b"---\nname: example\ndescription: >\n  Restore a replica\n  after failure.\n---\nBody", "test"
    )
    assert header.description == "Restore a replica after failure."
    assert header.aliases == ()


def test_bm25_length_normalization_and_term_frequency() -> None:
    short, verbose = bm25_scores(["recovery replica", "recovery replica " + "other " * 50], "recovery")
    assert short > verbose > 0
    scores = bm25_scores(["replica replica", "replica other", "unrelated words"], "replica")
    assert scores[0] > scores[1] > scores[2] == 0
    assert bm25_scores(["replica"], "replica replica") == bm25_scores(["replica"], "replica")
    assert bm25_scores([], "replica") == []
    assert bm25_scores([""], "replica") == [0]
    assert all(math.isfinite(score) for score in scores)
