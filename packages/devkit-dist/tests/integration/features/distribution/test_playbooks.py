from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner
from devkit_dist.features.distribution.models.errors import (
    BundleError,
    ConflictError,
    NotSynchronizedError,
    PendingTransactionError,
)
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.bundles.playbooks import read_playbook_header
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.guidance_block import ENTRY_SKILLS
from devkit_dist.features.distribution.services.installation.playbook_skill import MANAGED_ROOT, skill_files
from devkit_dist.features.distribution.services.installation.workspace import JOURNAL
from devkit_dist.features.distribution.usecases.context import GetContext
from devkit_dist.features.distribution.usecases.playbook_search import SearchPlaybooks
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH, RECEIPT_PATH
from devkit_dist.features.search import Embedder
from distsupport.distribution import cli, make_bundle, write_bundle
from distsupport.guidance import assert_rule
from distsupport.search import write_model


def select(target: Path, *bundles: str) -> None:
    update_config(target, presets={name: ["all"] for name in bundles})


@pytest.fixture
def target(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    return root


def test_search_metadata_across_bundles_without_body_disclosure(tmp_path: Path, target: Path) -> None:
    installed = [make_bundle(tmp_path, "team", directory=True), make_bundle(tmp_path, "ops")]
    select(target, "team", "ops")
    sync_project(target, installed)
    nested = target / "nested"
    nested.mkdir()
    result = SearchPlaybooks().execute(nested, "POSTGRESQL replica").to_dict()
    assert [entry["bundle"] for entry in result["results"]] == ["ops", "team"]
    assert all(entry["id"] == "recovery" for entry in result["results"])
    # Aliases are identity metadata: returned with the candidate, never ranked.
    assert all(entry["aliases"] == ["restore-standby", "wal-failure"] for entry in result["results"])
    assert SearchPlaybooks().execute(target, "wal failure standby").to_dict()["results"] == []
    assert "BODY_ONLY_SECRET" not in json.dumps(result)
    assert "BODY_ONLY_SECRET" in Path(result["results"][0]["path"]).read_text()
    assert SearchPlaybooks().execute(target, "bodyonlytoken").to_dict()["results"] == []
    assert SearchPlaybooks().execute(target, "unrelatednomatch").to_dict()["results"] == []
    assert "restore-replica" not in str(GetContext().execute(target, "team"))
    assert GetContext().execute(target, "team").to_dict()["constitution"] == "# Shared contracts\n"


def test_search_caps_threshold_and_cli_budget(tmp_path: Path, target: Path) -> None:
    select(target, "team", "ops")
    sync_project(target, [make_bundle(tmp_path, "team"), make_bundle(tmp_path, "ops")])
    limited = SearchPlaybooks().execute(target, "replica", limit=1).to_dict()
    assert len(limited["results"]) == 1
    assert limited["truncated"] is True
    assert SearchPlaybooks().execute(target, "replica", min_score=100).to_dict()["results"] == []
    runner = CliRunner()
    result = runner.invoke(
        cli, ["playbook", "search", "replica", "--workspace-root", str(target), "--max-bytes", "1024"]
    )
    assert result.exit_code == 0, result.output
    assert len(result.output.encode()) <= 1024
    assert "BODY_ONLY_SECRET" not in result.output
    for query in ["복제 복구", "!!!", "x" * 513]:
        assert runner.invoke(cli, ["playbook", "search", query, "--workspace-root", str(target)]).exit_code == 2
    for option, value in [("--limit", "0"), ("--min-score", "nan"), ("--max-bytes", "100")]:
        bad = runner.invoke(cli, ["playbook", "search", "replica", "--workspace-root", str(target), option, value])
        # A bound is a semantic check: one JSON error naming the option, not a click usage error.
        assert bad.exit_code == 2
        error = json.loads(bad.stdout)["error"]
        assert error["code"] == "ARGUMENT_INVALID" and error["advisory"]["target_files"] == [option]


def test_generated_skill_policies_and_sync_lifecycle(tmp_path: Path, target: Path) -> None:
    installed = [make_bundle(tmp_path, "team"), make_bundle(tmp_path, "ops")]
    select(target, "team", "ops")
    update_config(target, agents=["codex", "claude-code"])
    sync_project(target, installed)
    assert (target / MANAGED_ROOT / "SKILL.md").exists()
    codex = target / ".agents/skills/devkit-playbook"
    claude = target / ".claude/skills/devkit-playbook"
    policy = yaml.safe_load((codex / "agents/openai.yaml").read_text())
    assert policy["policy"]["allow_implicit_invocation"] is False
    frontmatter = (claude / "SKILL.md").read_text().split("---")[1]
    assert yaml.safe_load(frontmatter)["disable-model-invocation"] is True
    assert "restore-replica" not in (codex / "SKILL.md").read_text()
    assert not (target / ".agents/skills/recovery").exists()
    receipt = (target / RECEIPT_PATH).read_bytes()
    assert sync_project(target, installed).to_dict()["actions"] == []
    assert (target / RECEIPT_PATH).read_bytes() == receipt
    sync_project(target, installed, presets={"team": ["guidance"]})
    assert [item["bundle"] for item in SearchPlaybooks().execute(target, "replica").to_dict()["results"]] == ["ops"]
    sync_project(target, installed, presets={"team": ["guidance"], "ops": ["guidance"]})
    assert not (codex / "SKILL.md").exists()
    assert not (target / MANAGED_ROOT / "SKILL.md").exists()
    assert SearchPlaybooks().execute(target, "replica").to_dict()["results"] == []
    sync_project(target, installed, agents=[])
    assert (target / MANAGED_ROOT / "SKILL.md").exists()
    assert not (claude / "SKILL.md").exists()
    sync_project(target, [], deselect=["team", "ops"])
    assert not (target / MANAGED_ROOT / "SKILL.md").exists()


# SPEC-spec-playbook-discovery AC-06: the generic entry stays spec-neutral and keeps its explicit invocation.
SPEC_ASSET_TERMS = ("spec-playbook", "/spec", "references/playbooks.md", "devkit-spec")
REMOVED_PHRASES = ("do not authorize playbook discovery", "references from other skills", "invocation only")


@pytest.mark.parametrize("agent", [None, "codex", "claude-code"])
def test_generated_skill_is_spec_neutral(agent: str | None) -> None:
    files = skill_files(agent)
    raw = files["SKILL.md"].decode()
    body = " ".join(raw.split())
    for term in (*SPEC_ASSET_TERMS, *REMOVED_PHRASES):
        assert term not in body, term
    assert_rule(raw, "only when", "explicitly invokes", "devkit-playbook", "current task")
    assert_rule(
        raw, "description:", "only when", "explicitly invokes", "devkit-playbook", "confirms", "offered playbook"
    )
    assert_rule(raw, "entry skill", "offers a playbook", "confirms", "confirmation", "explicit invocation")
    assert_rule(raw, "only in", "explicitly requested discovery", "no suitable playbook", "ask")
    assert_rule(raw, "retrieval", "no execution authority")


def test_guidance_line_and_cli_help_are_spec_neutral() -> None:
    line = ENTRY_SKILLS["playbook"]
    assert line == "`devkit-playbook`: find and run an operational playbook the user invokes or confirms"
    result = CliRunner().invoke(cli, ["playbook", "--help"])
    assert result.exit_code == 0
    assert "after explicit devkit-playbook invocation" not in result.output
    assert "retrieval grants no execution authority" in " ".join(result.output.split())
    for term in SPEC_ASSET_TERMS:
        assert term not in line and term not in result.output, term


def test_generated_skill_collision_and_user_edits_are_protected(tmp_path: Path, target: Path) -> None:
    installed = [make_bundle(tmp_path, "team")]
    select(target, "team")
    skill = target / ".agents/skills/devkit-playbook/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("user owned")
    with pytest.raises(ConflictError, match="unowned"):
        sync_project(target, installed, agents=["codex"])
    assert skill.read_text() == "user owned"
    skill.unlink()
    sync_project(target, installed, agents=["codex"])
    skill.write_text("user edit")
    with pytest.raises(ConflictError, match="managed files were edited"):
        sync_project(target, installed, agents=["codex"])
    # Deselecting leaves the edited generated file behind as an orphan instead of aborting.
    result = sync_project(target, [], deselect=["team"])
    orphans = [name for notice in result.notices if notice.code == "ORPHAN_LEFT" for name in notice.target_files]
    assert ".agents/skills/devkit-playbook/SKILL.md" in orphans
    assert skill.read_text() == "user edit"


def test_search_rejects_modified_files_and_pending_transactions(tmp_path: Path, target: Path) -> None:
    select(target, "team")
    sync_project(target, [make_bundle(tmp_path, "team")])
    (target / JOURNAL).write_text("{}")
    with pytest.raises(PendingTransactionError, match="interrupted synchronization"):
        SearchPlaybooks().execute(target, "replica")
    (target / JOURNAL).unlink()
    (target / ".devkit/managed/team/recovery.md").write_text("unowned changes")
    with pytest.raises(NotSynchronizedError, match="modified context"):
        SearchPlaybooks().execute(target, "replica")


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
        "name: example\ndescription: Example\naliases: [postgres standby repair]\n",
        "name: example\ndescription: Example\naliases: [Old-id]\n",
        "name: example\ndescription: Example\naliases: [old-id, old-id]\n",
        "name: example\ndescription: Example\naliases: [release]\n",
        "name: example\ndescription: Example\naliases: [recovery]\n",
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


def test_cli_budget_counts_the_printed_bytes_of_accented_headers(tmp_path: Path, target: Path) -> None:
    # Accented Latin text is several bytes per character; the budget must hold for the bytes printed.
    # The query term is in half of the headers, so it has a positive IDF.
    accented = "Récupérer la réplique après échec, étape par étape. " * 4
    files = {
        f"playbooks/p{n:02d}.md": f"---\nname: playbook-{n:02d}\ndescription: {accented if n % 2 else 'Other.'}\n---\nBody.\n"
        for n in range(20)
    }
    assets = "".join(
        f'[[assets]]\nid = "p{n:02d}"\nkind = "playbook"\nsource = "playbooks/p{n:02d}.md"\n' for n in range(20)
    )
    installed = write_bundle(tmp_path / "accents", f'schema = 1\nname = "accents"\nversion = "0.1.0"\n{assets}', files)
    select(target, "accents")
    sync_project(target, [installed])
    for max_bytes in ("1024", "2048", "4096"):
        result = CliRunner().invoke(
            cli,
            [
                "playbook",
                "search",
                "replique",
                "--workspace-root",
                str(target),
                "--limit",
                "20",
                "--max-bytes",
                max_bytes,
            ],
        )
        assert result.exit_code == 0, result.output
        assert json.loads(result.stdout)["truncated"] is True
        assert len(result.stdout_bytes) <= int(max_bytes)


def test_search_adopts_playbooks_config_defaults(tmp_path: Path, target: Path) -> None:
    select(target, "team", "ops")
    sync_project(target, [make_bundle(tmp_path, "team"), make_bundle(tmp_path, "ops")])
    config_file = target / CONFIG_PATH
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""schema = 1

[playbooks]
min_score = 0.5
limit = 1
max_bytes = 4096
""")
    # With limit=1 from config, only 1 result is returned
    res = SearchPlaybooks().execute(target, "replica").to_dict()
    assert len(res["results"]) == 1
    assert res["truncated"] is True

    # With higher min_score in config, matching below 50.0 works, but if min_score is high it filters
    config_file.write_text("""schema = 1

[playbooks]
min_score = 50.0
""")
    assert SearchPlaybooks().execute(target, "replica").to_dict()["results"] == []


def test_cli_overrides_playbooks_config(tmp_path: Path, target: Path) -> None:
    select(target, "team", "ops")
    sync_project(target, [make_bundle(tmp_path, "team"), make_bundle(tmp_path, "ops")])
    config_file = target / CONFIG_PATH
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("""schema = 1

[playbooks]
min_score = 50.0
limit = 1
""")
    runner = CliRunner()
    # Default CLI run uses config min_score=50.0 -> 0 results
    res_default = runner.invoke(cli, ["playbook", "search", "replica", "--workspace-root", str(target)])
    assert res_default.exit_code == 0
    data_default = json.loads(res_default.output)
    assert len(data_default["results"]) == 0

    # Explicit CLI override --min-score 0.1 -> returns results
    res_override = runner.invoke(
        cli, ["playbook", "search", "replica", "--workspace-root", str(target), "--min-score", "0.1"]
    )
    assert res_override.exit_code == 0
    data_override = json.loads(res_override.output)
    # limit was 1 from config, so 1 result
    assert len(data_override["results"]) == 1

    # Overriding limit as well
    res_override2 = runner.invoke(
        cli, ["playbook", "search", "replica", "--workspace-root", str(target), "--min-score", "0.1", "--limit", "2"]
    )
    assert res_override2.exit_code == 0
    data_override2 = json.loads(res_override2.output)
    assert len(data_override2["results"]) == 2


def test_playbook_extension_keys_are_accepted_but_not_indexed(tmp_path: Path, target: Path) -> None:
    header = read_playbook_header(
        b"---\nname: restore-replica\ndescription: Restore a replica.\nx-trigger: [replica down, zebra]\nx-scope: repo\n---\n",
        "x",
    )
    assert header.extensions == (("x-trigger", ["replica down", "zebra"]), ("x-scope", "repo"))
    with pytest.raises(BundleError, match="supported frontmatter fields are name, description, aliases and x-<name>"):
        read_playbook_header(b"---\nname: a\ndescription: b\ntrigger: c\n---\n", "x")
    with pytest.raises(BundleError, match="supported frontmatter fields"):
        read_playbook_header(b"---\nname: a\ndescription: b\nx-Trigger: c\n---\n", "x")
    item = make_bundle(tmp_path, "team")
    (item.bundle.root / "recovery.md").write_text(
        "---\nname: restore-replica\ndescription: Restore a PostgreSQL replica.\nx-trigger: [zebra]\n---\nbody\n"
    )
    select(target, "team")
    sync_project(target, [item], agents=["codex"])
    assert "x-trigger" in (target / ".devkit/managed/team/recovery.md").read_text()
    assert SearchPlaybooks().execute(target, "zebra").to_dict()["results"] == []
    hit = SearchPlaybooks().execute(target, "replica").to_dict()["results"][0]
    assert hit["name"] == "restore-replica" and "x-trigger" not in json.dumps(hit)


# "database" and "broken" never occur in the playbook headers, so only the dense ranking can find recovery.
VECTORS = {
    "database": [1.0, 0.0],
    "broken": [1.0, 0.1],
    "postgresql": [1.0, 0.0],
    "replica": [0.9, 0.1],
    "publish": [0.0, 1.0],
    "software": [0.1, 0.9],
}


@pytest.fixture
def model(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Install a tiny embedding model; the returned list records each model load."""
    embedder = Embedder.from_directory(write_model(tmp_path / "model", VECTORS))
    loads: list[str] = []
    monkeypatch.setattr(
        "devkit_dist.features.search.services.index.load_embedder", lambda name: loads.append(name) or embedder
    )
    return loads


def test_auto_search_is_hybrid_with_a_model_and_finds_other_wording(
    tmp_path: Path, target: Path, model: list[str]
) -> None:
    select(target, "team", "ops")
    sync_project(target, [make_bundle(tmp_path, "team"), make_bundle(tmp_path, "ops")])
    hybrid = SearchPlaybooks().execute(target, "database broken").to_dict()
    assert hybrid["mode"] == "hybrid" and model == ["potion-base-8m"]
    assert [(entry["bundle"], entry["id"]) for entry in hybrid["results"]] == [
        ("ops", "recovery"),
        ("team", "recovery"),
    ]
    assert hybrid["results"][0]["score"] == pytest.approx(1 / 61, abs=1e-6)  # fused: ranked first by dense alone
    lexical = SearchPlaybooks().execute(target, "database broken", mode="lexical").to_dict()
    assert lexical == {"query": "database broken", "mode": "lexical", "results": [], "truncated": False}
    # The dense floor applies before fusion: nothing is similar enough, and nothing matches lexically.
    assert SearchPlaybooks().execute(target, "database broken", min_similarity=1.0).to_dict()["results"] == []
    dense = SearchPlaybooks().execute(target, "publish software", mode="DENSE").to_dict()
    assert dense["mode"] == "dense" and {entry["id"] for entry in dense["results"]} == {"release"}


def test_auto_search_is_lexical_without_a_model(tmp_path: Path, target: Path) -> None:
    select(target, "team")
    sync_project(target, [make_bundle(tmp_path, "team")])
    result = SearchPlaybooks().execute(target, "replica").to_dict()
    assert result["mode"] == "lexical" and [entry["id"] for entry in result["results"]] == ["recovery"]
    runner = CliRunner()
    for mode in ("hybrid", "dense"):
        # An explicit dense ranking is an error without the model, never a silent lexical result.
        explicit = runner.invoke(cli, ["playbook", "search", "replica", "-w", str(target), "--mode", mode])
        assert explicit.exit_code == 2
        assert json.loads(explicit.stdout)["error"]["code"] == "SEARCH_MODEL_NOT_FOUND"


def test_search_without_playbooks_never_loads_the_model(tmp_path: Path, target: Path, model: list[str]) -> None:
    update_config(target, presets={"team": ["guidance"]})
    sync_project(target, [make_bundle(tmp_path, "team")])
    assert SearchPlaybooks().execute(target, "replica").to_dict()["mode"] == "lexical" and model == []


def test_mode_and_min_similarity_come_from_config_and_options(tmp_path: Path, target: Path, model: list[str]) -> None:
    select(target, "team")
    sync_project(target, [make_bundle(tmp_path, "team")])
    (target / CONFIG_PATH).write_text((target / CONFIG_PATH).read_text() + '\n[playbooks]\nmode = "lexical"\n')
    assert SearchPlaybooks().execute(target, "database broken").to_dict()["mode"] == "lexical"
    runner = CliRunner()
    hybrid = runner.invoke(cli, ["playbook", "search", "database broken", "-w", str(target), "--mode", "HYBRID"])
    assert hybrid.exit_code == 0 and json.loads(hybrid.stdout)["mode"] == "hybrid"
    bad = runner.invoke(cli, ["playbook", "search", "replica", "-w", str(target), "--min-similarity", "1.5"])
    assert bad.exit_code == 2
    error = json.loads(bad.stdout)["error"]
    assert error["code"] == "ARGUMENT_INVALID" and error["advisory"]["target_files"] == ["--min-similarity"]
    assert runner.invoke(cli, ["playbook", "search", "replica", "-w", str(target), "--mode", "semantic"]).exit_code == 2


def test_identifier_aliases_are_accepted_and_unique_in_the_bundle(tmp_path: Path) -> None:
    item = make_bundle(tmp_path, "team")
    assert load_bundle(item.bundle.root).name == "team"
    (item.bundle.root / "release.md").write_text(
        "---\nname: publish-release\ndescription: Publish a software release.\naliases: [wal-failure]\n---\nbody\n"
    )
    with pytest.raises(BundleError, match="already declared by recovery"):
        load_bundle(item.bundle.root)
