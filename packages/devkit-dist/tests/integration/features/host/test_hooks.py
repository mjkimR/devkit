"""Hook deployment and service dispatch against real project files and native protocol input."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from importlib.metadata import EntryPoint
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_dist.base.errors import ReceiptError
from devkit_dist.cli import cli
from devkit_dist.features.distribution.models.errors import BundleError, ReceiptStaleError, UnsafeWorkspaceError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.plan import plan_bundle
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.usecases.status import get_project_status
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.host import (
    DispatchHostHook,
    HookConflictError,
    HookDefinitionError,
    HookDispatchError,
    HookResponse,
    HostConfigError,
    InspectHost,
    read_hook,
)
from devkit_dist.features.project.repositories.receipt import RECEIPT_PATH, parse_receipt
from distsupport.distribution import write_bundle

SOURCE = 'host = "codex"\nevent = "PreToolUse"\nhandler = "observe"\nmatcher = "^Bash$"\ntimeout = 3\n'
MANIFEST = """schema = 1
name = "sample"
version = "0.1.0"
[[assets]]
id = "trace"
kind = "hook"
source = "hooks/trace.toml"
"""
CONFIG = ".codex/hooks.json"
KEY = "sample:trace"


@pytest.fixture
def bundle(tmp_path: Path) -> InstalledBundle:
    return write_bundle(tmp_path / "source", MANIFEST, {"hooks/trace.toml": SOURCE})


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / ".devkit").mkdir(parents=True)
    (root / ".devkit/config.toml").write_text('agents = ["codex"]\n[presets]\nsample = ["all"]\n')
    return root


@pytest.fixture(autouse=True)
def observer_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    # Match installed wheel metadata without depending on when the editable checkout was last installed.
    monkeypatch.setattr(
        "devkit_dist.features.host.usecases.runner.metadata.entry_points",
        lambda **kw: (
            [
                EntryPoint(
                    name="observe",
                    value="devkit_dist.features.host.services.observation:observe",
                    group="devkit.host.handlers",
                )
            ]
            if kw.get("group") == "devkit.host.handlers" and kw.get("name") == "observe"
            else []
        ),
    )


def event(project: Path, **extra: object) -> dict:
    return {"hook_event_name": "PreToolUse", "cwd": str(project), "tool_name": "Bash", **extra}


def deploy(project: Path, bundle: InstalledBundle) -> None:
    sync_project(project, [bundle], agents=["codex"])


def test_plan_sync_update_remove_preserve_user_hooks(project: Path, bundle: InstalledBundle) -> None:
    foreign = {"matcher": "Read", "hooks": [{"type": "command", "command": "user-scanner"}]}
    path = project / CONFIG
    path.parent.mkdir()
    path.write_text(json.dumps({"description": "My hooks", "hooks": {"PreToolUse": [foreign]}}))
    path.chmod(0o600)
    plan = plan_bundle(bundle.bundle, agents=["codex"])
    assert plan.to_dict()["host_hooks"][0]["asset"] == KEY
    original = path.read_bytes()
    sync_project(project, [bundle], agents=["codex"], dry_run=True)
    assert path.read_bytes() == original and not (project / RECEIPT_PATH).exists()
    deploy(project, bundle)
    data = json.loads(path.read_bytes())
    assert data["description"] == "My hooks" and data["hooks"]["PreToolUse"][0] == foreign
    assert path.stat().st_mode & 0o777 == 0o600
    receipt = read_receipt(project)
    assert receipt is not None and CONFIG not in receipt.file_records
    saved = path.read_bytes()
    assert not sync_project(project, [bundle]).actions
    assert path.read_bytes() == saved
    assert get_project_status(project, [bundle]).ok
    (bundle.bundle.root / "hooks/trace.toml").write_text(SOURCE.replace("^Bash$", "^apply_patch$"))
    newer = InstalledBundle(bundle.package, "0.1.0", load_bundle(bundle.bundle.root))
    sync_project(project, [newer])
    assert json.loads(path.read_bytes())["hooks"]["PreToolUse"][1]["matcher"] == "^apply_patch$"
    sync_project(project, [], deselect=["sample"])
    assert json.loads(path.read_bytes()) == {"description": "My hooks", "hooks": {"PreToolUse": [foreign]}}
    receipt = read_receipt(project)
    assert receipt is not None and not receipt.host_hooks


@pytest.mark.parametrize("change", ["edit", "remove", "duplicate"])
def test_modified_registration_refuses_all_writes(project: Path, bundle: InstalledBundle, change: str) -> None:
    deploy(project, bundle)
    path = project / CONFIG
    data = json.loads(path.read_bytes())
    groups = data["hooks"]["PreToolUse"]
    if change == "edit":
        groups[0]["hooks"][0]["command"] += " --changed"
    elif change == "remove":
        groups.clear()
    else:
        groups.append(groups[0].copy())
    path.write_text(json.dumps(data))
    receipt_before = (project / RECEIPT_PATH).read_bytes()
    source_before = (project / ".devkit/managed/sample/hooks/trace.toml").read_bytes()
    (bundle.bundle.root / "hooks/trace.toml").write_text(SOURCE.replace("timeout = 3", "timeout = 2"))
    with pytest.raises(HookConflictError):
        sync_project(project, [bundle])
    assert (project / RECEIPT_PATH).read_bytes() == receipt_before
    assert (project / ".devkit/managed/sample/hooks/trace.toml").read_bytes() == source_before
    report = get_project_status(project, [bundle])
    assert not report.ok and any(error.code == "HOST_HOOK_CONFLICT" for error in report.errors)


def test_existing_identical_unowned_group_is_not_adopted(project: Path, bundle: InstalledBundle) -> None:
    deploy(project, bundle)
    (project / RECEIPT_PATH).unlink()
    with pytest.raises(HookConflictError):
        deploy(project, bundle)


def test_locked_clone_restore_and_stale_scope(project: Path, bundle: InstalledBundle) -> None:
    deploy(project, bundle)
    receipt = (project / RECEIPT_PATH).read_bytes()
    (project / CONFIG).unlink()
    report = get_project_status(project, [bundle])
    assert not report.ok and report.errors[-1].code == "HOST_HOOK_MISSING"
    sync_project(project, [bundle], locked=True)
    assert (project / CONFIG).exists() and (project / RECEIPT_PATH).read_bytes() == receipt
    with pytest.raises(ReceiptStaleError):
        sync_project(project, [bundle], agents=["claude-code"], locked=True)
    sync_project(project, [bundle], agents=["claude-code"])
    assert json.loads((project / CONFIG).read_bytes())["hooks"] == {}
    receipt = read_receipt(project)
    assert receipt is not None and not receipt.host_hooks


def test_receipt_is_strict_and_rejects_forged_commands(project: Path, bundle: InstalledBundle) -> None:
    deploy(project, bundle)
    path = project / RECEIPT_PATH
    data = json.loads(path.read_bytes())
    data["host_hooks"][0]["command"] = "user-command"
    path.write_text(json.dumps(data))
    with pytest.raises(ReceiptError):
        read_receipt(project)
    data["host_hooks"][0]["timeout"] = True
    with pytest.raises(ReceiptError):
        parse_receipt(json.dumps(data))


@pytest.mark.parametrize("raw", [b"[]", b'{"hooks": {"Stop": {}}}', b'{"hooks": {}, "hooks": {}}'])
def test_invalid_shared_file_is_preserved(project: Path, bundle: InstalledBundle, raw: bytes) -> None:
    path = project / CONFIG
    path.parent.mkdir()
    path.write_bytes(raw)
    with pytest.raises(HostConfigError):
        deploy(project, bundle)
    assert path.read_bytes() == raw and not (project / RECEIPT_PATH).exists()


def test_symlinked_host_directory_is_refused(project: Path, bundle: InstalledBundle, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (project / ".codex").symlink_to(outside, target_is_directory=True)
    with pytest.raises(UnsafeWorkspaceError):
        deploy(project, bundle)
    assert list(outside.iterdir()) == []


def test_dispatch_observes_only_metadata_and_status_distinguishes_delivery(
    project: Path, bundle: InstalledBundle
) -> None:
    deploy(project, bundle)
    assert InspectHost().execute(project).hooks[0]["last_received"] is None
    assert (
        DispatchHostHook().execute(
            project, "codex", KEY, event(project, prompt="SECRET", tool_input={"command": "PRIVATE"})
        )
        == {}
    )
    status = InspectHost().execute(project).to_dict()
    assert status["ok"] and status["trust"] == "unknown" and status["execution_permissions"] == "unknown"
    assert status["hooks"][0]["last_received"]["event"] == "PreToolUse"
    stored = (project / ".devkit/transient/host/codex/sample/trace.json").read_text()
    assert "SECRET" not in stored and "PRIVATE" not in stored and "cwd" not in stored


def test_dispatch_rejects_stale_definition_wrong_event_and_unknown_asset(
    project: Path, bundle: InstalledBundle
) -> None:
    deploy(project, bundle)
    for key, payload in [("sample:missing", event(project)), (KEY, event(project, hook_event_name="Stop"))]:
        with pytest.raises(HookDispatchError):
            DispatchHostHook().execute(project, "codex", key, payload)
    path = project / ".devkit/overrides/sample/hooks/trace.toml"
    path.parent.mkdir(parents=True)
    path.write_text(SOURCE.replace("PreToolUse", "PostToolUse"))
    sync_project(project, [bundle])
    with pytest.raises(HookDispatchError):
        DispatchHostHook().execute(project, "codex", KEY, event(project))


def test_handler_context_and_failures_do_not_corrupt_protocol(
    project: Path, bundle: InstalledBundle, monkeypatch: pytest.MonkeyPatch
) -> None:
    deploy(project, bundle)

    def handler(_event):
        print("accidental print")
        return HookResponse("Read the repository contract first.")

    monkeypatch.setattr("devkit_dist.features.host.usecases.runner.load_handler", lambda name: handler)
    result = CliRunner().invoke(
        cli, ["host", "hook", "--host", "codex", "--asset", KEY], input=json.dumps(event(project))
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "Read the repository contract first.",
        }
    }

    def broken(_event):
        raise RuntimeError("SECRET prompt")

    monkeypatch.setattr("devkit_dist.features.host.usecases.runner.load_handler", lambda name: broken)
    result = CliRunner().invoke(
        cli, ["host", "hook", "--host", "codex", "--asset", KEY], input=json.dumps(event(project))
    )
    assert result.exit_code == 0 and json.loads(result.stdout) == {}
    assert "HOST_HOOK_DISPATCH_FAILED" in result.stderr and "SECRET" not in result.output


@pytest.mark.parametrize(
    "raw",
    ["[]", "invalid", "{}", '{"cwd":"relative"}', "x" * (1024 * 1024 + 1)],
    ids=["array", "invalid", "empty", "relative", "oversized"],
)
def test_hook_cli_failures_are_advisory_native_json(raw: str) -> None:
    result = CliRunner().invoke(cli, ["host", "hook", "--host", "codex", "--asset", KEY], input=raw)
    assert result.exit_code == 0 and json.loads(result.stdout) == {}
    assert "HOST_HOOK_DISPATCH_FAILED" in result.stderr


def test_cli_status_and_missing_handler(
    project: Path, bundle: InstalledBundle, monkeypatch: pytest.MonkeyPatch
) -> None:
    deploy(project, bundle)
    args = ["host", "status", "-w", str(project), "--format", "json"]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0 and json.loads(result.stdout)["ok"]
    monkeypatch.setattr("devkit_dist.features.host.usecases.runner.metadata.entry_points", lambda **kw: [])
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 1
    assert json.loads(result.stdout)["errors"][0]["code"] == "HOST_HOOK_DISPATCH_FAILED"


@pytest.mark.parametrize(
    "source",
    [
        SOURCE.replace('"codex"', '"other"'),
        SOURCE.replace('"PreToolUse"', '"Unknown"'),
        SOURCE.replace('"PreToolUse"', '"Stop"'),
        SOURCE.replace("timeout = 3", "timeout = true"),
        SOURCE + 'extra = "no"\n',
        SOURCE.replace('"observe"', '"mod:unsafe"'),
        SOURCE.replace('"PreToolUse"', '"SessionEnd"').replace("timeout = 3", "timeout = 10"),
    ],
)
def test_invalid_hook_definitions_rejected_at_authoring(source: str, tmp_path: Path) -> None:
    with pytest.raises(HookDefinitionError):
        read_hook(source.encode(), "hook.toml")
    with pytest.raises(BundleError):
        write_bundle(tmp_path / "bad", MANIFEST, {"hooks/trace.toml": source})


def test_generated_command_runs_from_subdirectory(project: Path, bundle: InstalledBundle) -> None:
    deploy(project, bundle)
    subdir = project / "src"
    subdir.mkdir()
    # A maintained package entry point is used by installed-wheel smoke; here make the source observer available
    # in a separate interpreter without changing the test process's metadata.
    code = """
import json
from importlib.metadata import EntryPoint
from unittest.mock import patch
from devkit_dist.cli import cli
entry = EntryPoint(name="observe", value="devkit_dist.features.host.services.observation:observe", group="devkit.host.handlers")
with patch("devkit_dist.features.host.usecases.runner.metadata.entry_points", return_value=[entry]):
    cli()
"""
    result = subprocess.run(
        [sys.executable, "-c", code, "host", "hook", "--host", "codex", "--asset", KEY],
        input=json.dumps(event(subdir)),
        capture_output=True,
        text=True,
        cwd=subdir,
        env=os.environ,
    )
    assert result.returncode == 0 and result.stderr == "" and json.loads(result.stdout) == {}
    assert InspectHost().execute(project).hooks[0]["last_received"] is not None


def test_changed_override_handler_requires_sync(project: Path, bundle: InstalledBundle) -> None:
    deploy(project, bundle)
    override = project / ".devkit/overrides/sample/hooks/trace.toml"
    override.parent.mkdir(parents=True)
    override.write_text(SOURCE)
    sync_project(project, [bundle])
    override.write_text(SOURCE.replace('handler = "observe"', 'handler = "other-service"'))
    with pytest.raises(HookDispatchError) as caught:
        DispatchHostHook().execute(project, "codex", KEY, event(project))
    assert caught.value.code == "HOST_HOOK_DISPATCH_FAILED"
    assert not (project / ".devkit/transient/host/codex/sample/trace.json").exists()


def test_import_output_is_discarded_before_status_json(
    project: Path, bundle: InstalledBundle, monkeypatch: pytest.MonkeyPatch
) -> None:
    deploy(project, bundle)

    def noisy_load(_entry):
        print("accidental import output")
        return lambda _event: HookResponse()

    monkeypatch.setattr(EntryPoint, "load", noisy_load)
    result = CliRunner().invoke(cli, ["host", "status", "-w", str(project), "--format", "json"])
    assert result.exit_code == 0 and json.loads(result.stdout)["ok"]
