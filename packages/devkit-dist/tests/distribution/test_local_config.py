from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.core.local_config import LOCAL_CONFIG_PATH, resolve_execution_environment
from devkit.core.receipt import load_receipt
from devkit.distribution.errors import ConflictError, ReceiptStaleError
from devkit.distribution.installation import sync, transaction
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.context import get_context
from devkit.distribution.installation.local_render import (
    LOCAL_RENDER,
    LocalChangedError,
    LocalNotIgnoredError,
    LocalRenderForbiddenError,
    LocalRenderStaleError,
)
from devkit.distribution.installation.status import get_project_status
from distsupport.distribution import cli, instruction, write_bundle


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


@pytest.fixture
def fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    item = write_bundle(
        tmp_path / "source",
        """schema = 1
name = "style"
version = "0.1.0"
[variables.language]
type = "string"
default = "en"
[[assets]]
id = "style"
kind = "instruction"
source = "style.md.jinja"
""",
        {"style.md.jinja": instruction("style", "Language: {{ vars.language }}\n")},
    )
    root = tmp_path / "project"
    root.mkdir()
    git(root, "init", "-q")
    update_config(root, presets={"style": ["all"]}, agents=[])
    sync.sync_project(root, [item])

    @contextmanager
    def found():
        yield [item]

    monkeypatch.setattr("devkit.distribution.cli.discover_bundles", found)
    return root, item


def local(root: Path, text: str = '[bundles.style.variables]\nlanguage="ko"\n') -> None:
    (root / LOCAL_CONFIG_PATH).write_text(text)


def tracked_state(root: Path) -> dict[str, bytes]:
    return {p: (root / p).read_bytes() for p in (".devkit/config.toml", ".devkit/installation.json", "AGENTS.md")}


def test_personal_render_locked_restore_stale_and_removal(fixture) -> None:
    root, item = fixture
    canonical = tracked_state(root)
    canonical_receipt = load_receipt(root)
    local(root)
    sync.sync_project(root, [item], locked=True)
    output = root / ".devkit/managed/style/style.md"
    assert "Language: ko" in output.read_text()
    assert tracked_state(root) == canonical
    assert load_receipt(root) == canonical_receipt
    assert get_context(root, "style").instructions
    assert get_project_status(root, [item]).ok
    ledger = json.loads((root / LOCAL_RENDER).read_text())
    assert list(ledger["files"]) == [".devkit/managed/style/style.md"]
    output.unlink()
    sync.sync_project(root, [item], locked=True)
    assert "Language: ko" in output.read_text()
    local(root, '[bundles.style.variables]\nlanguage="ja"\n')
    with pytest.raises(LocalRenderStaleError):
        get_context(root, "style")
    with pytest.raises(LocalRenderStaleError):
        get_project_status(root, [item])
    sync.sync_project(root, [item])
    output.write_text("hand edit")
    with pytest.raises(ConflictError):
        sync.sync_project(root, [item])
    output.unlink()
    sync.sync_project(root, [item])
    (root / LOCAL_CONFIG_PATH).unlink()
    sync.sync_project(root, [item])
    assert "Language: en" in output.read_text()
    assert not (root / LOCAL_RENDER).exists()
    assert tracked_state(root) == canonical


@pytest.mark.parametrize("case", ["tracked-local", "negated-local", "tracked-output", "unignored-output"])
def test_ignore_and_index_refusal_preserve_state(fixture, case: str) -> None:
    root, item = fixture
    local(root)
    if case == "tracked-local":
        git(root, "add", "-f", LOCAL_CONFIG_PATH)
    elif case == "negated-local":
        with (root / ".devkit/.gitignore").open("a") as f:
            f.write("!/config.local.toml\n")
    elif case == "tracked-output":
        git(root, "add", "-f", ".devkit/managed/style/style.md")
    else:
        (root / ".devkit/.gitignore").write_text("/config.local.toml\n/transient/\n")
    before = tracked_state(root)
    with pytest.raises(LocalNotIgnoredError):
        sync.sync_project(root, [item])
    assert tracked_state(root) == before
    assert not (root / LOCAL_RENDER).exists()


@pytest.mark.parametrize(
    "flags,persist,exit_code",
    [
        (["--cloud"], True, 0),
        (["--cloud", "--dry-run"], False, 0),
        (["--cloud", "--check"], False, 1),
        (["--cloud", "--no-save"], False, 0),
        (["--cloud", "--locked"], True, 0),
    ],
)
def test_environment_cli_matrix(fixture, flags: list[str], persist: bool, exit_code: int) -> None:
    root, _ = fixture
    before = tracked_state(root)
    result = CliRunner().invoke(cli, ["sync", "-w", str(root), "--format", "json", *flags])
    assert result.exit_code == exit_code, result.output
    assert json.loads(result.stdout)["execution_environment"] == "cloud"
    assert resolve_execution_environment(root).environment == ("cloud" if persist else "local")
    assert tracked_state(root) == before
    if persist:
        assert CliRunner().invoke(cli, ["sync", "-w", str(root)]).exit_code == 0
        assert resolve_execution_environment(root).environment == "cloud"
        assert CliRunner().invoke(cli, ["sync", "--local", "-w", str(root)]).exit_code == 0
        assert resolve_execution_environment(root).environment == "local"


def test_shared_writer_inspection_and_mutually_exclusive_flags(fixture) -> None:
    root, _ = fixture
    local(root, '# personal\n[execution]\nenvironment="cloud"\n')
    before = (root / LOCAL_CONFIG_PATH).read_bytes()
    update_config(root, agents=[])
    assert (root / LOCAL_CONFIG_PATH).read_bytes() == before
    result = CliRunner().invoke(cli, ["config", "show", "--effective", "-w", str(root), "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["sources"]["execution.environment"] == str(root / LOCAL_CONFIG_PATH)
    assert CliRunner().invoke(cli, ["sync", "--cloud", "--local", "-w", str(root)]).exit_code == 2


def test_ignore_append_and_locked_refusal(fixture) -> None:
    root, item = fixture
    text = "# custom\n/managed/\n/transient/\n/custom/\n"
    (root / ".devkit/.gitignore").write_text(text)
    preview = sync.sync_project(root, [item], environment="cloud", dry_run=True)
    assert any(a.path == LOCAL_CONFIG_PATH for a in preview.actions)
    assert (root / ".devkit/.gitignore").read_text() == text
    with pytest.raises(ReceiptStaleError):
        sync.sync_project(root, [item], environment="cloud", locked=True)
    assert not (root / LOCAL_CONFIG_PATH).exists()
    sync.sync_project(root, [item], environment="cloud")
    assert (root / ".devkit/.gitignore").read_text() == text + "/config.local.toml\n"


def test_input_race_aborts_before_writes(fixture, monkeypatch: pytest.MonkeyPatch) -> None:
    root, item = fixture
    before = tracked_state(root)
    original = sync._build_receipt

    def race(*args, **kwargs):
        result = original(*args, **kwargs)
        local(root, '[execution]\nenvironment="cloud"\n')
        return result

    monkeypatch.setattr(sync, "_build_receipt", race)
    with pytest.raises(LocalChangedError):
        sync.sync_project(root, [item], environment="local")
    assert tracked_state(root) == before
    assert resolve_execution_environment(root).environment == "cloud"


def test_transaction_failure_rolls_back_local_and_shared(fixture, monkeypatch: pytest.MonkeyPatch) -> None:
    root, _ = fixture
    before = tracked_state(root)
    original = transaction.atomic_write

    def fail(root, name, content):
        if name == LOCAL_CONFIG_PATH and content is not None:
            raise OSError("injected transaction failure")
        return original(root, name, content)

    monkeypatch.setattr(transaction, "atomic_write", fail)
    result = CliRunner().invoke(cli, ["sync", "--cloud", "--no-agents", "-w", str(root)])
    assert result.exit_code != 0
    assert not (root / LOCAL_CONFIG_PATH).exists()
    assert tracked_state(root) == before


def test_guidance_personalization_refused(fixture) -> None:
    root, item = fixture
    source = item.bundle.root
    with (source / "bundle.toml").open("a") as f:
        f.write('\n[[assets]]\nid="pointer"\nkind="guidance"\nsource="pointer.md.jinja"\n')
    (source / "pointer.md.jinja").write_text("- Language {{ vars.language }}\n")
    from dataclasses import replace

    from devkit.distribution.bundles import load_bundle

    item = replace(item, bundle=load_bundle(source))
    sync.sync_project(root, [item])
    before = tracked_state(root)
    local(root)
    with pytest.raises(LocalRenderForbiddenError):
        sync.sync_project(root, [item])
    assert tracked_state(root) == before


def test_missing_ledger_and_post_sync_warning(fixture, monkeypatch: pytest.MonkeyPatch) -> None:
    root, item = fixture
    local(root)
    sync.sync_project(root, [item])
    (root / LOCAL_RENDER).unlink()
    with pytest.raises(LocalRenderStaleError):
        get_context(root, "style")
    from devkit.distribution.errors import OrphanLeftNotice

    monkeypatch.setattr(sync, "run_post_sync", lambda *args: [OrphanLeftNotice("post-sync warning")])
    result = sync.sync_project(root, [item], environment="cloud")
    assert result.notices
    assert resolve_execution_environment(root).environment == "cloud"


def test_executable_asset_personalization_refused(fixture) -> None:
    root, item = fixture
    source = item.bundle.root
    with (source / "bundle.toml").open("a") as stream:
        stream.write('\n[[assets]]\nid="policy"\nkind="workflow"\nsource="policy.md.jinja"\n')
    (source / "policy.md.jinja").write_text(
        '---\nid: policy\ntitle: "{{ vars.language }}"\nschema_version: 1\nstages:\n  - id: check\n    exit: [anchor-exists]\n---\n'
    )
    from dataclasses import replace

    from devkit.distribution.bundles import load_bundle
    from devkit.distribution.errors import BundleError

    before = tracked_state(root)
    local(root)
    with pytest.raises(BundleError, match="templates require"):
        replace(item, bundle=load_bundle(source))
    assert tracked_state(root) == before


def test_skill_native_projection_and_initial_sync(tmp_path: Path) -> None:
    item = write_bundle(
        tmp_path / "source",
        """schema = 1
name = "response-style"
version = "0.1.0"
[variables.language]
type = "string"
default = "en"
[[assets]]
id = "response-style"
kind = "skill"
source = "skills/response-style"
""",
        {"skills/response-style/SKILL.md.jinja": instruction("response-style", "Language: {{ vars.language }}\n")},
    )
    root = tmp_path / "consumer"
    root.mkdir()
    git(root, "init", "-q")
    (root / ".gitignore").write_text(".agents/\n")
    update_config(root, presets={"response-style": ["all"]}, agents=["codex"])
    local(root, '[bundles.response-style.variables]\nlanguage="ko"\n')
    sync.sync_project(root, [item])
    native = root / ".agents/skills/response-style/SKILL.md"
    assert "Language: ko" in native.read_text()
    canonical = tracked_state(root)
    git(root, "add", "-f", str(native.relative_to(root)))
    local(root, '[bundles.response-style.variables]\nlanguage="ja"\n')
    with pytest.raises(LocalNotIgnoredError):
        sync.sync_project(root, [item])
    assert tracked_state(root) == canonical


@pytest.mark.parametrize("locked", [False, True])
@pytest.mark.parametrize("case", ["equal-tracked", "equal-unignored", "removed-tracked", "removed-unignored"])
def test_every_ledger_mutation_requires_ignored_untracked_state(fixture, locked: bool, case: str) -> None:
    root, item = fixture
    local(root)
    sync.sync_project(root, [item])
    if case.startswith("removed"):
        (root / LOCAL_CONFIG_PATH).unlink()
    else:
        local(root, '[bundles.style.variables]\nlanguage="en"\n')
    if case.endswith("-tracked"):
        git(root, "add", "-f", LOCAL_RENDER)
    else:
        (root / ".devkit/.gitignore").write_text("/managed/\n/config.local.toml\n")
    before = (root / LOCAL_RENDER).read_bytes()
    output = (root / ".devkit/managed/style/style.md").read_bytes()
    with pytest.raises(LocalNotIgnoredError):
        sync.sync_project(root, [item], locked=locked)
    assert (root / LOCAL_RENDER).read_bytes() == before
    assert (root / ".devkit/managed/style/style.md").read_bytes() == output


@pytest.mark.parametrize("tracked", [False, True])
def test_canonical_restoration_checks_prior_personal_outputs(fixture, tracked: bool) -> None:
    root, item = fixture
    local(root)
    sync.sync_project(root, [item])
    path = ".devkit/managed/style/style.md"
    if tracked:
        git(root, "add", "-f", path)
    else:
        (root / ".devkit/.gitignore").write_text("/transient/\n/config.local.toml\n")
    (root / LOCAL_CONFIG_PATH).unlink()
    before = (root / path).read_bytes()
    with pytest.raises(LocalNotIgnoredError):
        sync.sync_project(root, [item])
    assert (root / path).read_bytes() == before


def test_input_snapshot_precedes_selection_save(fixture) -> None:
    from devkit.distribution.installation.config import prepare_config_update

    root, item = fixture
    before = (root / ".devkit/installation.json").read_bytes()
    changed = (root / ".devkit/config.toml").read_text() + '\n[execution]\nenvironment="cloud"\n'

    def save():
        update = prepare_config_update(root, agents=[])
        (root / ".devkit/config.toml").write_text(changed)
        return update

    with pytest.raises(LocalChangedError):
        sync.sync_project(root, [item], save=save, environment="local")
    assert (root / ".devkit/config.toml").read_text() == changed
    assert (root / ".devkit/installation.json").read_bytes() == before
    assert not (root / LOCAL_CONFIG_PATH).exists()


@pytest.mark.parametrize("evidence", ["missing", "malformed"])
@pytest.mark.parametrize("tracked", [False, True])
def test_restoration_keeps_personal_ownership_when_render_evidence_is_lost(
    fixture, evidence: str, tracked: bool
) -> None:
    root, item = fixture
    local(root)
    sync.sync_project(root, [item])
    path = ".devkit/managed/style/style.md"
    if tracked:
        git(root, "add", "-f", path)
    else:
        (root / ".devkit/.gitignore").write_text("/transient/\n/config.local.toml\n")
    (root / LOCAL_CONFIG_PATH).unlink()
    ledger = root / LOCAL_RENDER
    if evidence == "missing":
        ledger.unlink()
    else:
        ledger.write_text("broken")
    before = (root / path).read_bytes()
    with pytest.raises(LocalNotIgnoredError):
        sync.sync_project(root, [item])
    assert (root / path).read_bytes() == before


def test_shared_render_changes_do_not_acquire_personal_provenance(fixture) -> None:
    root, item = fixture
    path = ".devkit/managed/style/style.md"
    git(root, "add", "-f", path)
    config = root / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[bundles.style.variables]\nlanguage="ja"\n')
    sync.sync_project(root, [item])
    assert "Language: ja" in (root / path).read_text()
    assert json.loads((root / ".devkit/transient/deployed.json").read_text())["personal"] == []
