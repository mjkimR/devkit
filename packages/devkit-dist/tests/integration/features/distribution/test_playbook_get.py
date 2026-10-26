from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.features.distribution import GetPlaybook
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.workspace import JOURNAL
from devkit_dist.features.distribution.usecases.override_commands import create_override
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.receipt import RECEIPT_PATH
from distsupport.distribution import cli, make_bundle


def invoke(root: Path, selector: str):
    return CliRunner().invoke(cli, ["playbook", "get", selector, "-w", str(root)])


def error(root: Path, selector: str, code: str):
    result = invoke(root, selector)
    assert result.exit_code == 2, result.output
    payload = json.loads(result.stdout)
    assert set(payload) == {"error"}
    assert payload["error"]["code"] == code
    return payload["error"]


@pytest.fixture
def deployed(tmp_path: Path):
    root = tmp_path / "consumer"
    root.mkdir()
    installed = [make_bundle(tmp_path, "team", directory=True)]
    update_config(root, presets={"team": ["all"]}, agents=[])
    sync_project(root, installed)
    return root, installed


@pytest.mark.parametrize("directory", [False, True])
def test_complete_body_identity_and_no_resource_reads(tmp_path: Path, directory: bool, monkeypatch):
    installed = make_bundle(tmp_path, "team", directory=directory)
    source = installed.bundle.root / ("recovery/SKILL.md" if directory else "recovery.md")
    body = "\r\n  [resource](reference.md)\r\n" + "large body \n" * 10000 + "  \n"
    source.write_bytes(
        b"---\r\nname: different-name\r\ndescription: Procedure.\r\nx-extra: ignored\r\n---\r\n" + body.encode()
    )
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"team": ["all"]}, agents=[])
    sync_project(root, [installed])
    path = root / ".devkit/managed/team" / source.relative_to(installed.bundle.root)
    receipt_before = (root / RECEIPT_PATH).read_bytes()
    config_before = (root / ".devkit/config.toml").read_bytes()
    original = Path.read_bytes

    def guarded(self):
        assert self.name != "reference.md", "linked resource was read"
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    monkeypatch.setattr(
        "devkit_dist.features.distribution.usecases.commands.discover_bundles",
        lambda: pytest.fail("package enumeration"),
    )
    nested = root / "nested"
    nested.mkdir()
    result = GetPlaybook().execute(nested, "team/recovery").to_dict()
    assert result == {
        "bundle": "team",
        "id": "recovery",
        "alias": None,
        "name": "different-name",
        "description": "Procedure.",
        "aliases": [],
        "body": body,
        "source": {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()},
        "context": {"bundle": "team", "argv": ["devkit", "get-context", "team"], "policy": "once-per-agent-context"},
    }
    assert json.loads(invoke(root, "team/recovery").stdout) == result
    assert (root / RECEIPT_PATH).read_bytes() == receipt_before
    assert (root / ".devkit/config.toml").read_bytes() == config_before


@pytest.mark.parametrize(
    "selector",
    [
        "",
        "team",
        "Team/recovery",
        " team/recovery",
        "team/recovery ",
        "team//recovery",
        "/team/recovery",
        "team/recovery.md",
        "team/../recovery",
        "team:recovery",
        "team/recovery\n",
    ],
)
def test_invalid_selector_precedes_project_access(tmp_path: Path, selector: str):
    problem = error(tmp_path, selector, "ARGUMENT_INVALID")
    assert problem["advisory"]["target_files"] == ["PLAYBOOK_ID"]
    assert not (tmp_path / ".devkit").exists()


@pytest.mark.parametrize("selector", ["missing/recovery", "team/missing", "team/guide", "team/restore-replica"])
def test_exact_selection_errors(deployed, selector):
    root, _ = deployed
    assert "devkit list" in str(error(root, selector, "SELECTION_INVALID"))


def test_snapshot_and_unselected_asset(deployed):
    root, installed = deployed
    update_config(root, presets={"team": ["guidance"]})
    assert GetPlaybook().execute(root, "team/recovery").id == "recovery"
    sync_project(root, installed)
    error(root, "team/recovery", "SELECTION_INVALID")


def test_live_override_and_missing_override(deployed):
    root, installed = deployed
    create_override(root, installed, "team:recovery")
    path = root / ".devkit/overrides/team/recovery/SKILL.md"
    path.write_text("---\nname: edited\ndescription: Live edit.\n---\n  keep spaces\n")
    result = GetPlaybook().execute(root, "team/recovery").to_dict()
    assert result["name"] == "edited" and result["id"] == "recovery"
    assert result["body"] == "  keep spaces\n"
    assert result["source"] == {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    path.unlink()
    assert "devkit sync" in str(error(root, "team/recovery", "NOT_SYNCHRONIZED"))


@pytest.mark.parametrize("data", [b"\xff", b"no frontmatter", b"---\nname: only\n---\n"])
def test_invalid_effective_override(deployed, data):
    root, installed = deployed
    create_override(root, installed, "team:recovery")
    (root / ".devkit/overrides/team/recovery/SKILL.md").write_bytes(data)
    assert "SKILL.md" in str(error(root, "team/recovery", "BUNDLE_INVALID"))


@pytest.mark.parametrize("mutation", ["missing", "modified", "journal", "symlink", "receipt"])
def test_shared_read_failures(deployed, mutation):
    root, _ = deployed
    path = root / ".devkit/managed/team/recovery/SKILL.md"
    code = "NOT_SYNCHRONIZED"
    if mutation == "missing":
        path.unlink()
    elif mutation == "modified":
        path.write_text("modified")
    elif mutation == "journal":
        (root / JOURNAL).write_text("{}")
        code = "TRANSACTION_PENDING"
    elif mutation == "receipt":
        (root / RECEIPT_PATH).write_text("{}")
        code = "RECEIPT_INVALID"
    else:
        path.unlink()
        path.symlink_to(root / ".devkit/managed/team/release.md")
        code = "WORKSPACE_UNSAFE"
    error(root, "team/recovery", code)


@pytest.mark.parametrize(
    "entries",
    [
        [],
        [".devkit/managed/team/recovery/SKILL.md", ".devkit/managed/team/release.md"],
        [".devkit/managed/team/release.md"],
        [".devkit/managed/other/recovery.md"],
    ],
)
def test_corrupt_entrypoints(deployed, entries):
    root, _ = deployed
    path = root / RECEIPT_PATH
    receipt = json.loads(path.read_text())
    asset = next(a for a in receipt["assets"] if a["id"] == "recovery")
    asset["entrypoints"] = entries
    if entries == [".devkit/managed/other/recovery.md"]:
        asset["paths"] = entries
    path.write_text(json.dumps(receipt))
    error(root, "team/recovery", "RECEIPT_INVALID")


@pytest.mark.parametrize(
    "args",
    [[], ["team/recovery", "extra"], ["team/recovery", "--format", "json"], ["team/recovery", "--format", "text"]],
)
def test_usage_errors(args):
    result = CliRunner().invoke(cli, ["playbook", "get", *args])
    assert result.exit_code == 2 and "Usage:" in result.output


def test_missing_receipt(tmp_path):
    assert "devkit sync" in str(error(tmp_path, "team/recovery", "NOT_SYNCHRONIZED"))


def test_writer_lock_failure(deployed, monkeypatch):
    from devkit_dist.features.distribution.services.installation import transaction

    root, _ = deployed
    monkeypatch.setattr(transaction, "READ_LOCK_TIMEOUT", 0.01)
    with transaction.project_lock(root):
        error(root, "team/recovery", "LOCK_HELD")


def test_empty_context(tmp_path):
    from devkit_dist.features.distribution.usecases.context import GetContext
    from distsupport.distribution import write_bundle

    item = write_bundle(
        tmp_path / "source",
        'schema = 1\nname = "empty"\nversion = "0.1.0"\n[[assets]]\nid = "run"\nkind = "playbook"\nsource = "run.md"\n',
        {"run.md": "---\nname: run\ndescription: Run it.\n---\nbody"},
    )
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets={"empty": ["all"]}, agents=[])
    sync_project(root, [item])
    assert GetContext().execute(root, "empty").to_dict() == {
        "bundle": "empty",
        "constitution": None,
        "instructions": [],
    }
    assert GetPlaybook().execute(root, "empty/run").to_dict()["context"]["policy"] == "once-per-agent-context"


def test_unrelated_stale_personal_evidence(tmp_path):
    import subprocess

    from devkit_dist.features.project.repositories.local_config import LOCAL_CONFIG_PATH
    from distsupport.distribution import instruction, write_bundle

    item = write_bundle(
        tmp_path / "style",
        'schema = 1\nname = "style"\nversion = "0.1.0"\n[variables.language]\ntype = "string"\ndefault = "en"\n[[assets]]\nid = "style"\nkind = "instruction"\nsource = "style.md.jinja"\n',
        {"style.md.jinja": instruction("style", "Language: {{ vars.language }}\n")},
    )
    playbooks = make_bundle(tmp_path, "team")
    root = tmp_path / "consumer"
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    update_config(root, presets={"team": ["all"], "style": ["all"]}, agents=[])
    sync_project(root, [item, playbooks])
    (root / LOCAL_CONFIG_PATH).write_text('[bundles.style.variables]\nlanguage="ko"\n')
    sync_project(root, [item, playbooks])
    assert GetPlaybook().execute(root, "team/recovery").id == "recovery"
    (root / LOCAL_CONFIG_PATH).write_text('[bundles.style.variables]\nlanguage="ja"\n')
    error(root, "team/recovery", "CONFIG_LOCAL_RENDER_STALE")


def test_generated_exact_invocation_guidance():
    from devkit_dist.features.distribution.services.installation.playbook_skill import BODY

    for phrase in [
        "playbook get <bundle>/<playbook>",
        "once per agent context",
        "source.path",
        "unavailable approval UI is not approval",
        "External systems own",
        # ADR-spec-intake-playbook-discovery: a confirmed offer is explicit invocation; the scope stays the task.
        "does not activate\nplaybook search for future tasks",
        "that confirmation is\nthe explicit invocation",
    ]:
        assert phrase in BODY


def test_invalid_selector_precedes_invalid_workspace(tmp_path):
    problem = error(tmp_path / "nonexistent", "INVALID", "ARGUMENT_INVALID")
    assert problem["advisory"]["target_files"] == ["PLAYBOOK_ID"]


def test_alias_resolves_to_the_canonical_playbook(deployed):
    root, _ = deployed
    result = json.loads(invoke(root, "team/wal-failure").stdout)
    assert (result["id"], result["alias"], result["name"]) == ("recovery", "wal-failure", "restore-replica")
    assert result["aliases"] == ["restore-standby", "wal-failure"]
    assert GetPlaybook().execute(root, "team/recovery").alias is None


def test_override_aliases_exact_shadowing_and_ambiguity(deployed):
    root, installed = deployed
    create_override(root, installed, "team:release")
    path = root / ".devkit/overrides/team/release.md"
    # The override declares the other playbook's ID and alias: retrieval checks the effective headers again.
    path.write_text("---\nname: publish-release\ndescription: Edited.\naliases: [recovery, restore-standby]\n---\nb\n")
    exact = GetPlaybook().execute(root, "team/recovery")
    assert (exact.id, exact.alias) == ("recovery", None)
    problem = error(root, "team/restore-standby", "PLAYBOOK_ALIAS_AMBIGUOUS")
    assert problem["advisory"]["target_files"] == ["team/recovery", "team/release"]
    assert GetPlaybook().execute(root, "team/wal-failure").id == "recovery"
