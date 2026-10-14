from __future__ import annotations

import json
import signal
from pathlib import Path

import pytest
from devkit.advisory import ActionMode, AdvisoryError, ExitCode, Level
from devkit.compact import CommandInterrupted, run_command
from devkit.gate import (
    BaseGate,
    GateConfigError,
    GateContext,
    GateEntry,
    GateError,
    GateLoadError,
    GateRefusedError,
    GateRegistry,
    GateResult,
    GateResultError,
    GatesConfig,
    Outcome,
    Stage,
    default_gate_registry,
    deployed_gate_packages,
    project_registry,
    run_stage,
    validate_gates,
)
from testsupport.gate import deploy_gate, gate_ctx, gate_source

_DEFAULTS = GatesConfig()


def _receipt(root: Path) -> dict:
    return json.loads((root / ".devkit/installation.json").read_text())


def _save_receipt(root: Path, data: dict) -> None:
    (root / ".devkit/installation.json").write_text(json.dumps(data))


def test_deployed_gate_packages_reads_gate_assets_only(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source())
    deploy_gate(tmp_path, gate_source("other", cls="OtherGate"), ".devkit/overrides/team/gates/other/gate.py")
    data = _receipt(tmp_path)
    data["assets"][:0] = [
        {"bundle": "team", "id": "r", "kind": "rule", "paths": [".devkit/managed/team/rules/r.py"]},
        {"bundle": "team", "id": "gone", "kind": "gate", "paths": ["gone.py", "README.md"]},
    ]
    _save_receipt(tmp_path, data)
    deployed = deployed_gate_packages(tmp_path)
    assert [{n: p.relative_to(tmp_path).as_posix() for n, p in pkg.modules.items()} for pkg in deployed.packages] == [
        {"gate": ".devkit/managed/team/gates/block/gate.py"},
        {"gate": ".devkit/overrides/team/gates/other/gate.py"},
    ]
    assert [(e.code, e.message) for e in deployed.errors] == [("ASSET_FILE_INVALID", "gone.py is missing")]
    # A missing file is restored by a sync (a fresh clone or worktree lacks the ignored managed copies): AUTO.
    assert deployed.errors[0].target_files == ("gone.py",) and deployed.errors[0].fix == "devkit sync"
    assert deployed.errors[0].mode is ActionMode.AUTO


def test_receipt_listed_gate_files_load_whatever_their_name(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source("private-gate"), ".devkit/managed/team/gates/private/_private.py")
    deployed = deployed_gate_packages(tmp_path)
    assert [list(p.modules) for p in deployed.packages] == [["_private"]] and deployed.errors == ()
    assert project_registry(tmp_path).get("private-gate") is not None


def test_a_gate_package_imports_its_own_modules_relatively(tmp_path: Path) -> None:
    deploy_gate(tmp_path, "GATE_ID = 'split-gate'\n", ".devkit/managed/team/gates/split/ids.py")
    source = gate_source("placeholder").replace('id="placeholder"', "id=GATE_ID")
    deploy_gate(tmp_path, "from .ids import GATE_ID\n" + source, ".devkit/managed/team/gates/split/gate.py")
    data = _receipt(tmp_path)  # deploy_gate records one asset per call: merge them into the package's one asset
    first, second = data["assets"]
    data["assets"] = [{**first, "paths": first["paths"] + second["paths"]}]
    _save_receipt(tmp_path, data)
    deployed = deployed_gate_packages(tmp_path)
    assert [sorted(p.modules) for p in deployed.packages] == [["gate", "ids"]]
    registry = project_registry(tmp_path)
    assert registry.get("split-gate") is not None and registry.errors == []
    assert registry.sources["split-gate"] == ".devkit/managed/team/gates/split/gate.py"


def test_gate_files_are_checked_against_the_receipt_hash(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source())
    assert len(deployed_gate_packages(tmp_path).packages) == 1

    path = tmp_path / ".devkit/managed/team/gates/block/gate.py"
    path.write_text(gate_source() + "\n# edited by hand\n")
    deployed = deployed_gate_packages(tmp_path)
    assert deployed.packages == () and "differs from the hash in the receipt" in deployed.errors[0].message
    assert deployed.errors[0].fix is not None and "devkit override create team:block" in deployed.errors[0].fix
    registry = project_registry(tmp_path)
    assert registry.get("team-block") is None and registry.errors


@pytest.mark.parametrize("unsafe", ["../outside.py", "/abs/gate.py", "a/../b.py"])
def test_unsafe_receipt_paths_are_rejected(tmp_path: Path, unsafe: str) -> None:
    deploy_gate(tmp_path, gate_source())
    data = _receipt(tmp_path)
    data["assets"][0]["paths"] = [unsafe]
    _save_receipt(tmp_path, data)
    deployed = deployed_gate_packages(tmp_path)
    assert deployed.packages == () and deployed.errors[0].code == "RECEIPT_INVALID"


def test_gate_file_symlinked_outside_the_project_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path / "outside.py"
    outside.write_text(gate_source())
    root = tmp_path / "project"
    deploy_gate(root, gate_source())
    link = root / ".devkit/managed/team/gates/block/gate.py"
    link.unlink()
    link.symlink_to(outside)
    deployed = deployed_gate_packages(root)
    assert deployed.packages == () and "unsafe" in deployed.errors[0].message


def test_project_registry_loads_gates_and_reports_problems(tmp_path: Path) -> None:
    assert deployed_gate_packages(tmp_path).packages == ()
    deploy_gate(tmp_path, gate_source())
    deploy_gate(tmp_path, "raise RuntimeError('boom')\n", ".devkit/managed/team/gates/broken/gate.py")
    deploy_gate(tmp_path, gate_source("message-nonempty", cls="Dup"), ".devkit/managed/team/gates/dup/gate.py")
    registry = project_registry(tmp_path)
    assert [g.id for g in registry.get_all()] == ["team-block", "verify-commands", "message-nonempty"]
    assert registry.sources["team-block"] == ".devkit/managed/team/gates/block/gate.py"
    messages = [e.message for e in registry.errors]
    assert any("failed to load gate package .devkit/managed/team/gates/broken: boom" in m for m in messages)
    assert any("duplicate gate id 'message-nonempty'" in m for m in messages)
    assert all(isinstance(e, GateLoadError) and e.code == "GATE_LOAD_FAILED" for e in registry.errors)


def test_a_gate_file_loads_atomically(tmp_path: Path) -> None:
    source = gate_source("first", cls="First") + (
        "\n\nclass Second(BaseGate):\n"
        "    def __init__(self) -> None:\n"
        "        raise RuntimeError('second cannot start')\n"
        "\n"
        "    def run(self, ctx):\n"
        "        return None\n"
    )
    deploy_gate(tmp_path, source)
    registry = project_registry(tmp_path)
    assert registry.get("first") is None
    assert any("second cannot start" in e.message for e in registry.errors)


def test_abstract_shared_bases_are_not_gates(tmp_path: Path) -> None:
    source = (
        "from devkit.gate import BaseGate, Stage\n\n\n"
        "class Shared(BaseGate):\n"
        "    def __init__(self, gate_id: str) -> None:\n"
        "        super().__init__(id=gate_id, description='', stage=Stage.PRE_COMMIT)\n\n\n"
        "class Concrete(Shared):\n"
        "    def __init__(self) -> None:\n"
        "        super().__init__('concrete')\n\n"
        "    def run(self, ctx):\n"
        "        return None\n"
    )
    deploy_gate(tmp_path, source)
    registry = project_registry(tmp_path)
    assert registry.errors == [] and registry.get("concrete") is not None


def test_gates_with_invalid_metadata_are_rejected(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source().replace("stage=Stage.PRE_COMMIT", 'stage="pre-commit"'))
    registry = project_registry(tmp_path)
    assert registry.get("team-block") is None
    assert any("stage must be a devkit.gate.Stage" in e.message for e in registry.errors)


def test_unreadable_receipt_is_a_registry_error(tmp_path: Path) -> None:
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/installation.json").write_text("{nope")
    registry = project_registry(tmp_path)
    assert registry.errors and registry.errors[0].code == "RECEIPT_INVALID"
    assert registry.errors[0].target_files == (".devkit/installation.json",)


class Recorder(BaseGate):
    def __init__(self, gate_id: str, order: int, calls: list[str], result: object = None) -> None:
        super().__init__(id=gate_id, description="", stage=Stage.PRE_COMMIT, order=order)
        self.calls = calls
        self.result = result

    def run(self, ctx: GateContext) -> GateResult | None:
        self.calls.append(self.id)
        return self.result  # type: ignore[return-value]  # some tests return invalid values on purpose


def test_run_stage_orders_gates_and_runs_past_failures(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source())
    registry = project_registry(tmp_path)
    calls: list[str] = []
    registry.register(Recorder("late", 500, calls))
    registry.register(Recorder("early", 10, calls, GateResult.skipped("nothing staged")))
    report = run_stage(gate_ctx(tmp_path), registry, _DEFAULTS)
    assert calls == ["early", "late"]
    assert [(r.gate_id, r.outcome) for r in report.runs] == [
        ("early", Outcome.SKIPPED),
        ("team-block", Outcome.FAILED),
        ("verify-commands", Outcome.SKIPPED),
        ("late", Outcome.PASSED),
    ]
    assert not report.ok and report.runs[1].error is not None and report.runs[1].error.code == "TEST_REFUSED"
    assert report.problems == (report.runs[1].error,) and report.exit_code is ExitCode.FINDINGS


def test_gate_result_cannot_report_failure() -> None:
    with pytest.raises(GateResultError, match="refuse by raising GateRefusedError") as info:
        GateResult(Outcome.FAILED, "why")
    assert (info.value.code, info.value.mode) == ("GATE_RESULT_INVALID", ActionMode.MAINTENANCE)


def test_gate_refusals_exit_findings_and_config_errors_exit_error() -> None:
    refused = GateRefusedError("refused", fix="Do it differently")
    assert (refused.code, refused.exit_code, refused.mode) == ("GATE_FAILED", ExitCode.FINDINGS, ActionMode.BLOCKED)
    config = GateConfigError("bad")
    assert (config.code, config.exit_code, config.mode) == (
        "GATE_CONFIG_INVALID",
        ExitCode.ERROR,
        ActionMode.INPUT_ERROR,
    )
    assert all(isinstance(error, GateError) for error in (refused, config))


def test_stage_report_exits_with_the_highest_problem_exit_code(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source())
    config = GatesConfig({**_DEFAULTS.gates, "typo": GateEntry(True)})
    report = run_stage(gate_ctx(tmp_path), project_registry(tmp_path), config)
    assert [e.code for e in report.problems] == ["GATE_CONFIG_INVALID", "TEST_REFUSED"]
    assert report.exit_code is ExitCode.ERROR


def test_every_failed_run_carries_an_error(tmp_path: Path) -> None:
    class SilentFailure(BaseGate):
        def __init__(self) -> None:
            super().__init__(id="silent", description="", stage=Stage.PRE_COMMIT)

        def run(self, ctx: GateContext) -> GateResult:
            return GateResult(Outcome.FAILED, "why")

    registry = GateRegistry()
    registry.register(SilentFailure())
    registry.register(Recorder("wrong-type", 200, [], True))
    report = run_stage(gate_ctx(tmp_path), registry, GatesConfig())
    assert [r.outcome for r in report.runs] == [Outcome.FAILED, Outcome.FAILED]
    assert all(r.error is not None for r in report.runs)
    assert report.runs[0].error is not None and "refuse by raising GateRefusedError" in report.runs[0].error.message
    assert report.runs[1].error is not None and report.runs[1].error.code == "GATE_RESULT_INVALID"


class Raises(BaseGate):
    def __init__(self, gate_id: str, order: int, exc: BaseException) -> None:
        super().__init__(id=gate_id, description="", stage=Stage.PRE_COMMIT, order=order)
        self.exc = exc

    def run(self, ctx: GateContext) -> GateResult:
        raise self.exc


@pytest.mark.parametrize("code", [0, 1, None])
def test_a_gate_calling_sys_exit_fails_and_later_gates_still_run(tmp_path: Path, code: int | None) -> None:
    calls: list[str] = []
    registry = GateRegistry()
    registry.register(Raises("exits", 10, SystemExit(code)))
    registry.register(Raises("refuses", 20, GateRefusedError("no", code="TEST_REFUSED")))
    registry.register(Recorder("late", 100, calls))
    report = run_stage(gate_ctx(tmp_path), registry, GatesConfig())
    assert [(r.gate_id, r.outcome) for r in report.runs] == [
        ("exits", Outcome.FAILED),
        ("refuses", Outcome.FAILED),
        ("late", Outcome.PASSED),
    ]
    assert calls == ["late"] and report.runs[0].error is not None
    assert report.runs[0].error.code == "UNEXPECTED_ERROR" and "SystemExit" in report.runs[0].error.message
    assert report.exit_code is ExitCode.ERROR


def test_keyboard_interrupt_aborts_the_stage(tmp_path: Path) -> None:
    calls: list[str] = []
    registry = GateRegistry()
    registry.register(Raises("interrupted", 10, KeyboardInterrupt()))
    registry.register(Recorder("late", 100, calls))
    with pytest.raises(KeyboardInterrupt):
        run_stage(gate_ctx(tmp_path), registry, GatesConfig())
    assert calls == []


class RunsCommand(BaseGate):
    def __init__(self, gate_id: str, order: int, command: str) -> None:
        super().__init__(id=gate_id, description="", stage=Stage.PRE_COMMIT, order=order)
        self.command = command

    def run(self, ctx: GateContext) -> GateResult:
        run_command(["sh", "-c", self.command], cwd=ctx.repo_root, log_dir=ctx.repo_root / "logs")
        return GateResult.passed()


def test_an_interrupted_run_command_aborts_the_stage(tmp_path: Path) -> None:
    # CommandInterrupted is a SystemExit, which a gate calling sys.exit() turns into a failure: not this one.
    calls: list[str] = []
    registry = GateRegistry()
    registry.register(RunsCommand("interrupted", 10, "kill -INT $PPID; sleep 30"))  # Ctrl-C while it runs
    registry.register(Recorder("late", 100, calls))
    with pytest.raises(CommandInterrupted) as caught:
        run_stage(gate_ctx(tmp_path), registry, GatesConfig())
    assert caught.value.code == 128 + signal.SIGINT and caught.value.run.interrupted == signal.SIGINT
    assert calls == []


def test_gate_notices_never_fail_the_stage_and_errors_are_lowered(tmp_path: Path) -> None:
    warning = AdvisoryError("hook-like problem", code="TEAM_ERROR")
    notice = AdvisoryError("fyi", code="TEAM_NOTICE", level=Level.NOTICE)
    registry = GateRegistry()
    registry.register(Recorder("noisy", 100, [], GateResult.passed("ok", notices=[warning, notice])))
    report = run_stage(gate_ctx(tmp_path), registry, GatesConfig())
    assert report.ok and report.exit_code is ExitCode.OK
    assert [(n.code, n.level, n.exit_code) for n in report.notices] == [
        ("TEAM_ERROR", Level.WARNING, ExitCode.OK),
        ("TEAM_NOTICE", Level.NOTICE, ExitCode.OK),
    ]
    assert warning.level is Level.ERROR  # the gate's own object is not changed


class BadNotices(BaseGate):
    def __init__(self, gate_id: str, order: int, *, bypass: bool = False) -> None:
        super().__init__(id=gate_id, description="", stage=Stage.PRE_COMMIT, order=order)
        self.bypass = bypass

    def run(self, ctx: GateContext) -> GateResult:
        if self.bypass:  # past __post_init__, as a subclass or object.__setattr__ could be
            result = GateResult.passed()
            object.__setattr__(result, "notices", ("plain text",))
            return result
        return GateResult.passed(notices=["plain text"])  # type: ignore[list-item]


@pytest.mark.parametrize("bypass", [False, True])
def test_a_notice_that_is_not_an_advisory_fails_only_its_gate(tmp_path: Path, bypass: bool) -> None:
    calls: list[str] = []
    registry = GateRegistry()
    registry.register(BadNotices("bad-notices", 10, bypass=bypass))
    registry.register(Recorder("late", 100, calls))
    report = run_stage(gate_ctx(tmp_path), registry, GatesConfig())
    assert [(r.gate_id, r.outcome) for r in report.runs] == [("bad-notices", Outcome.FAILED), ("late", Outcome.PASSED)]
    error = report.runs[0].error
    assert error is not None and (error.code, error.mode) == ("GATE_RESULT_INVALID", ActionMode.MAINTENANCE)
    assert "a GateResult notice is a str, not an AdvisoryError" in error.message
    assert calls == ["late"] and report.exit_code is ExitCode.ERROR


def test_gate_result_notices_are_checked_and_kept_as_a_tuple() -> None:
    warning = AdvisoryError("w", level=Level.WARNING)
    assert GateResult(notices=[warning]).notices == (warning,)  # type: ignore[arg-type]
    with pytest.raises(GateResultError, match="not a sequence of AdvisoryError"):
        GateResult(notices=1)  # type: ignore[arg-type]


def test_run_stage_applies_enabled_and_settings(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source(enabled=False))
    registry = project_registry(tmp_path)
    report = run_stage(gate_ctx(tmp_path), registry, _DEFAULTS)
    assert [(r.gate_id, r.outcome, r.note) for r in report.runs] == [
        ("team-block", Outcome.SKIPPED, "disabled"),
        ("verify-commands", Outcome.SKIPPED, "no commands configured"),
    ]

    config = GatesConfig({**_DEFAULTS.gates, "team-block": GateEntry(True, {"allow": True})})
    report = run_stage(gate_ctx(tmp_path), registry, config)
    assert report.ok and report.runs[0].note == "allowed"

    config = GatesConfig({**_DEFAULTS.gates, "team-block": GateEntry(True, {"allow": "yes"})})
    report = run_stage(gate_ctx(tmp_path), registry, config)
    assert not report.ok and report.runs[0].outcome is Outcome.SKIPPED and report.runs[0].note == "invalid settings"
    assert any("expected bool" in e.message for e in report.errors)


def test_invalid_settings_of_a_disabled_gate_or_another_stage_are_reported(tmp_path: Path) -> None:
    registry = default_gate_registry()
    config = GatesConfig(
        {
            "verify-commands": GateEntry(False, {"bogus": 1}),
            "message-nonempty": GateEntry(True, {"bogus": 1}),
        }
    )
    validation = validate_gates(registry, config)
    assert len(validation.errors) == 2
    assert "unknown settings ['bogus']" in validation.errors[0].message  # verify-commands, disabled
    assert "gate has no settings" in validation.errors[1].message  # message-nonempty, another stage
    report = run_stage(gate_ctx(tmp_path), registry, config)
    assert not report.ok and [r.note for r in report.runs] == ["disabled"]


def test_configured_gate_that_is_not_installed_fails_the_stage(tmp_path: Path) -> None:
    config = GatesConfig({"timeline": GateEntry(True)})
    report = run_stage(gate_ctx(tmp_path), default_gate_registry(), config)
    assert not report.ok and "not installed: ['timeline']" in report.errors[0].message
    assert report.errors[0].fix is not None and "`devkit sync`" in report.errors[0].fix


@pytest.mark.parametrize(
    ("text", "failed"),
    [
        ("feat: x\n", False),
        ("#123 fix the parser\n", False),  # `git commit -m` keeps a leading '#'
        ("# Heading\n\nbody\n", False),
        ("; with core.commentChar=';'\n", False),
        ("", True),
        ("  \n\n\t\n", True),
        ("\n# ------------------------ >8 ------------------------\ndiff\n", True),
        ("\n; ------------------------ >8 ------------------------\ndiff\n", True),
        ("fix: y\n# ------------------------ >8 ------------------------\n", False),
    ],
)
def test_message_gate(tmp_path: Path, text: str, failed: bool) -> None:
    (tmp_path / "MSG").write_text(text)
    report = run_stage(gate_ctx(tmp_path, Stage.COMMIT_MSG, "MSG"), default_gate_registry(), GatesConfig())
    assert report.ok is not failed
    if failed:
        assert report.exit_code is ExitCode.FINDINGS and report.problems[0].fix


def test_post_commit_without_gates(tmp_path: Path) -> None:
    assert run_stage(gate_ctx(tmp_path, Stage.POST_COMMIT), GateRegistry(), GatesConfig()).runs == ()
