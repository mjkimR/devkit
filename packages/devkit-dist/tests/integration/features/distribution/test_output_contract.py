"""Agent output contract of the distribution commands: exact runnable fixes, file targets and one wording per
condition (``CAP-ADV-agent-advisory-protocol`` section 8)."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import ExitCode
from devkit_dist.features.distribution.models.errors import McpRegistrationPendingNotice
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.usecases.override_commands import create_override
from devkit_dist.features.distribution.usecases.sync import sync_project
from devkit_dist.features.project.repositories.receipt import CONFIG_PATH
from distsupport.distribution import cli, instruction, make_bundle, write_bundle

DEFAULTED = """schema = 1
name = "extra"
version = "0.1.0"
default_preset = "all"
[[assets]]
id = "note"
kind = "instruction"
source = "note.md"
"""


def _invoke(*args: str):
    return CliRunner().invoke(cli, list(args))


def _error(result) -> dict:
    payload = json.loads(result.stdout)
    assert set(payload) == {"error"}, payload
    return payload["error"]


@pytest.fixture
def team(tmp_path: Path) -> InstalledBundle:
    return make_bundle(tmp_path, "team")


@pytest.fixture
def installed(team: InstalledBundle, monkeypatch: pytest.MonkeyPatch) -> list[InstalledBundle]:
    items = [team]

    @contextmanager
    def found():
        yield items

    for module in ("commands", "context"):
        monkeypatch.setattr(
            f"devkit_dist.features.distribution.usecases.{module}.discover_bundles", found, raising=False
        )
    return items


@pytest.fixture
def root(tmp_path: Path) -> Path:
    target = tmp_path / "consumer"
    (target / ".devkit").mkdir(parents=True)
    return target


def _synced(root: Path, installed: list[InstalledBundle], presets: dict[str, list[str]] | None = None) -> None:
    update_config(root, presets=presets or {"team": ["all"]}, agents=[])
    sync_project(root, installed)


# Finding 1: an unknown preset names the caller's own command, one per preset, and targets the argument.


def test_bundle_plan_unknown_preset_names_each_plan_command(team: InstalledBundle) -> None:
    source = str(team.bundle.root)
    error = _error(_invoke("bundle", "plan", source, "--preset", "nosuch"))
    advisory = error["advisory"]
    assert error["code"] == "SELECTION_INVALID"
    assert advisory["target_files"] == ["--preset"]
    assert advisory["fix"] == f"uv run devkit bundle plan {source}"
    assert advisory["details"] == [
        f"uv run devkit bundle plan {source} --preset {name}" for name in ("all", "guidance", "recovery")
    ]


def test_add_unknown_preset_names_each_add_command(installed: list[InstalledBundle], root: Path) -> None:
    error = _error(_invoke("add", "team:nosuch", "--format", "json", "-w", str(root)))
    advisory = error["advisory"]
    assert error["code"] == "SELECTION_INVALID"
    assert advisory["target_files"] == ["SELECTIONS"]
    assert advisory["fix"] == "uv run devkit list"
    assert advisory["details"] == [f"uv run devkit add team:{name}" for name in ("all", "guidance", "recovery")]


def test_sync_preset_without_default_names_each_sync_command(installed: list[InstalledBundle], root: Path) -> None:
    error = _error(_invoke("sync", "--preset", "team", "--format", "json", "-w", str(root)))
    advisory = error["advisory"]
    assert advisory["target_files"] == ["--preset"]
    assert advisory["details"] == [
        f"uv run devkit sync --preset team:{name}" for name in ("all", "guidance", "recovery")
    ]


# Finding 2 and 11: known values are interpolated, never left as placeholders; the selector argument is the target.


def test_add_uninstalled_bundle_targets_the_selector(installed: list[InstalledBundle], root: Path) -> None:
    error = _error(_invoke("add", "ghost", "--format", "json", "-w", str(root)))
    assert error["message"] == "bundle is not installed: ghost"
    assert error["advisory"]["target_files"] == ["SELECTIONS"]
    assert error["advisory"]["fix"] == "uv run devkit list"


def test_selected_bundle_not_installed_names_it(installed: list[InstalledBundle], root: Path) -> None:
    update_config(root, presets={"ghost": ["all"]}, agents=[])
    error = _error(_invoke("sync", "--format", "json", "-w", str(root)))
    assert error["message"] == "selected bundle is not installed: ghost"
    assert error["advisory"]["fix"] == "uv run devkit remove ghost"
    assert error["advisory"]["target_files"] == [CONFIG_PATH]
    assert "<" not in json.dumps(error["advisory"])


def test_remove_unselected_bundle_lists_names_without_repr(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    error = _error(_invoke("remove", "nosuch", "other", "--format", "json", "-w", str(root)))
    assert error["message"] == "bundle is not selected: nosuch, other"
    assert error["advisory"]["target_files"] == ["BUNDLES"]


def test_override_retained_names_the_add_command(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed, {"team": ["guidance"]})
    create_override(root, installed, "team:guide")
    result = json.loads(_invoke("remove", "team", "--format", "json", "-w", str(root)).stdout)
    (notice,) = [item for item in result["notices"] if item["code"] == "OVERRIDE_RETAINED"]
    assert notice["advisory"]["fix"] == "uv run devkit add team:guidance"


def test_edited_managed_file_names_its_asset(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    edited = ".devkit/managed/team/guide.md"
    (root / edited).write_text("edited\n")
    error = _error(_invoke("sync", "--format", "json", "-w", str(root)))
    assert error["code"] == "SYNC_CONFLICT"
    assert error["message"] == f"managed files were edited: {edited}"
    assert "uv run devkit override create team:guide" in error["advisory"]["fix"]
    assert "<" not in json.dumps(error["advisory"])
    status = json.loads(_invoke("status", "-w", str(root)).stdout)
    (problem,) = [item for item in status["errors"] if item["code"] == "SYNC_CONFLICT"]
    assert problem["message"] == error["message"]
    assert problem["advisory"]["fix"] == error["advisory"]["fix"]


def test_playbook_get_malformed_selector_fix_is_runnable(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    error = _error(_invoke("playbook", "get", "Team", "-w", str(root)))
    assert error["code"] == "ARGUMENT_INVALID"
    assert error["advisory"]["fix"] == "uv run devkit list"


def test_playbook_get_unknown_targets_the_selector(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    error = _error(_invoke("playbook", "get", "team/nosuch", "-w", str(root)))
    assert error["code"] == "SELECTION_INVALID"
    assert error["advisory"]["target_files"] == ["PLAYBOOK_ID"]


def test_get_context_of_an_installed_unselected_bundle_names_add(
    installed: list[InstalledBundle], root: Path, tmp_path: Path
) -> None:
    _synced(root, installed)
    installed.append(write_bundle(tmp_path / "extra", DEFAULTED, {"note.md": instruction("note")}))
    error = _error(_invoke("get-context", "extra", "-w", str(root)))
    assert error["code"] == "SELECTION_INVALID"
    assert error["advisory"]["fix"] == "uv run devkit add extra"
    assert error["advisory"]["target_files"] == ["BUNDLE_NAME"]
    unknown = _error(_invoke("get-context", "nosuch", "-w", str(root)))
    assert unknown["advisory"]["fix"] == "uv run devkit list"
    assert unknown["advisory"]["target_files"] == ["BUNDLE_NAME"]


# Finding 3: override drift is one advisory with workspace-relative override targets and one fix command.


def _drifted(root: Path, installed: list[InstalledBundle], *assets: str) -> None:
    _synced(root, installed)
    for asset in assets:
        create_override(root, installed, f"team:{asset}")
    source = installed[0].bundle.root
    (source / "guide.md").write_text("---\nname: testing\ndescription: Testing constraints.\n---\nChanged.\n")
    (source / "recovery.md").write_text((source / "recovery.md").read_text() + "Changed.\n")


def test_override_drift_warning_targets_override_files(installed: list[InstalledBundle], root: Path) -> None:
    _drifted(root, installed, "guide")
    result = json.loads(_invoke("sync", "--format", "json", "-w", str(root)).stdout)
    (drift,) = [item for item in result["notices"] if item["code"] == "OVERRIDE_DRIFT"]
    advisory = drift["advisory"]
    assert advisory["target_files"] == [".devkit/overrides/team/guide.md"]
    assert advisory["fix"] == "uv run devkit override diff team:guide"
    assert advisory["details"] == ["uv run devkit override accept team:guide"]
    status = json.loads(_invoke("status", "-w", str(root)).stdout)
    (warning,) = [item for item in status["notices"] if item["code"] == "OVERRIDE_DRIFT"]
    assert warning == drift


def test_blocked_override_drift_is_an_interaction(installed: list[InstalledBundle], root: Path) -> None:
    _drifted(root, installed, "guide")
    (root / CONFIG_PATH).write_text('override_drift = "block"\n' + (root / CONFIG_PATH).read_text())
    refused = _error(_invoke("sync", "--format", "json", "-w", str(root)))
    status = json.loads(_invoke("status", "-w", str(root)).stdout)
    (problem,) = [item for item in status["errors"] if item["code"] == "OVERRIDE_DRIFT"]
    for advisory in (refused["advisory"], problem["advisory"]):
        assert advisory["mode"] == "INTERACTION" and advisory["actor"] == "USER" and not advisory["guardrail"]
        assert advisory["target_files"] == [".devkit/overrides/team/guide.md"]
        assert advisory["fix"] == "uv run devkit override diff team:guide"
    assert refused["message"] == problem["message"]


def test_deferred_accept_names_the_remaining_override(installed: list[InstalledBundle], root: Path) -> None:
    _drifted(root, installed, "guide", "recovery")
    (root / CONFIG_PATH).write_text('override_drift = "block"\n' + (root / CONFIG_PATH).read_text())
    result = json.loads(_invoke("override", "accept", "team:guide", "-w", str(root)).stdout)
    (notice,) = [item for item in result["notices"] if item["code"] == "OVERRIDE_SYNC_DEFERRED"]
    assert notice["advisory"]["fix"] == "uv run devkit override diff team:recovery"
    assert notice["advisory"]["details"] == ["uv run devkit override accept team:recovery"]


# Finding 4: sync --check reports why it exits 1.


def test_sync_check_reports_not_synchronized(installed: list[InstalledBundle], root: Path) -> None:
    update_config(root, presets={"team": ["all"]}, agents=[])
    text = _invoke("sync", "--check", "-w", str(root))
    assert text.exit_code == int(ExitCode.FINDINGS)
    assert text.stdout.startswith("[SYNC: ")
    assert text.stderr.startswith("[ERROR]  (NOT_SYNCHRONIZED)")
    assert "[FIX]    uv run devkit sync\n" in text.stderr
    as_json = _invoke("sync", "--check", "--format", "json", "-w", str(root))
    assert as_json.exit_code == int(ExitCode.FINDINGS) and not as_json.stderr
    (error,) = json.loads(as_json.stdout)["errors"]
    assert error["code"] == "NOT_SYNCHRONIZED" and error["exit_code"] == int(ExitCode.FINDINGS)
    assert error["advisory"]["fix"] == "uv run devkit sync"


# Finding 5: one command in the fix; alternatives and conditions elsewhere.


def test_receipt_stale_fix_is_one_command(installed: list[InstalledBundle], root: Path) -> None:
    update_config(root, presets={"team": ["all"]}, agents=[])
    error = _error(_invoke("sync", "--locked", "--format", "json", "-w", str(root)))
    assert error["code"] == "RECEIPT_STALE"
    assert error["advisory"]["fix"] == "uv run devkit sync"
    assert "uv run devkit sync" in error["advisory"]["what_to_report"]


def test_accept_without_override_fix_is_one_command(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    error = _error(_invoke("override", "accept", "team:guide", "-w", str(root)))
    assert error["message"] == "no override found for team:guide"
    assert error["advisory"]["fix"] == "uv run devkit override create team:guide"


def test_existing_override_fix_is_one_command(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    create_override(root, installed, "team:guide")
    error = _error(_invoke("override", "create", "team:guide", "-w", str(root)))
    assert error["advisory"]["fix"] == "uv run devkit override create team:guide --force"


# Finding 6: the context argv is the agent-facing invocation.


def test_playbook_get_context_argv_uses_the_agent_invocation(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    result = json.loads(_invoke("playbook", "get", "team/release", "-w", str(root)).stdout)
    assert result["context"]["argv"] == ["uv", "run", "devkit", "get-context", "team"]


# Finding 7 and 8: workspace-relative paths; config show needs no flag.


def test_configuration_paths_are_workspace_relative(installed: list[InstalledBundle], root: Path) -> None:
    update_config(root, presets={"team": ["all"]}, agents=[])
    (root / CONFIG_PATH).write_text((root / CONFIG_PATH).read_text() + '\n[presentation]\nlanguage = "fr"\n')
    shown = _invoke("config", "show", "-w", str(root))
    assert shown.exit_code == 0, shown.output
    assert str(root) not in shown.stdout
    report = json.loads(shown.stdout)
    assert report["sources"]["presentation.language"] == CONFIG_PATH
    (notice,) = report["notices"]
    assert notice["advisory"]["target_files"] == [CONFIG_PATH]
    assert _invoke("config", "show", "--effective", "-w", str(root)).stdout == shown.stdout
    (root / CONFIG_PATH).write_text("schema = [\n")
    broken = _invoke("sync", "--format", "json", "-w", str(root))
    assert _error(broken)["code"] == "CONFIG_INVALID" and str(root) not in broken.stdout


# Finding 9: a never-synced checkout's next step is a plain sync, not a registration step.


def test_status_without_receipt_omits_registration_pending(
    installed: list[InstalledBundle], root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    update_config(root, presets={"team": ["all"]}, agents=["claude-code"])
    pending = [McpRegistrationPendingNotice("local MCP registration is not set up in this checkout: claude")]
    monkeypatch.setattr(
        "devkit_dist.features.distribution.usecases.status.registration_pending_notices", lambda *_: pending
    )
    status = json.loads(_invoke("status", "-w", str(root)).stdout)
    assert "MCP_REGISTRATION_PENDING" not in {item["code"] for item in status["notices"]}
    sync_project(root, installed)
    status = json.loads(_invoke("status", "-w", str(root)).stdout)
    assert "MCP_REGISTRATION_PENDING" in {item["code"] for item in status["notices"]}


# Finding 10: one wording per condition.


def test_missing_override_has_one_wording(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    messages = {
        _error(_invoke("override", verb, "team:guide", "-w", str(root)))["message"]
        for verb in ("remove", "accept", "diff")
    }
    assert messages == {"no override found for team:guide"}


# Finding 12: no digests in the default override output; file modes in octal.


def test_override_output_carries_no_digests(installed: list[InstalledBundle], root: Path) -> None:
    _synced(root, installed)
    create_override(root, installed, "team:guide")
    (listed,) = json.loads(_invoke("override", "list", "-w", str(root)).stdout)["overrides"]
    assert not any(key.endswith("sha256") for key in listed)
    diff = json.loads(_invoke("override", "diff", "team:guide", "-w", str(root)).stdout)
    assert not any(key.endswith("sha256") for key in diff)


def test_bundle_plan_modes_are_octal(team: InstalledBundle) -> None:
    plan = json.loads(_invoke("bundle", "plan", str(team.bundle.root)).stdout)
    assert {item["mode"] for item in plan["files"]} == {"0644"}
