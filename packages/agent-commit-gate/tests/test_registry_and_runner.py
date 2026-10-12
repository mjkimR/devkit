from __future__ import annotations

from pathlib import Path

from agent_commit_gate import (
    BaseGate,
    GateContext,
    GateEntry,
    GateRegistry,
    GateResult,
    GatesConfig,
    Outcome,
    Stage,
    default_registry,
    deployed_gate_paths,
    project_registry,
    run_stage,
)
from conftest import deploy_gate, gate_source


def _ctx(root: Path, stage: Stage = Stage.PRE_COMMIT, *args: str) -> GateContext:
    return GateContext(repo_root=root, git_dir=root / ".git", stage=stage, args=args)


def test_deployed_gate_paths_reads_gate_assets_only(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source())
    deploy_gate(tmp_path, gate_source("other", cls="OtherGate"), ".devkit/overrides/team/gates/other.py")
    (tmp_path / ".devkit/installation.json").write_text(
        (tmp_path / ".devkit/installation.json")
        .read_text()
        .replace(
            '"assets": [',
            '"assets": [{"kind": "rule", "paths": [".devkit/managed/team/rules/r.py"]}, '
            '{"kind": "gate", "paths": ["gone.py", "README.md"]}, ',
        )
    )
    found, missing = deployed_gate_paths(tmp_path)
    assert [p.relative_to(tmp_path).as_posix() for p in found] == [
        ".devkit/managed/team/gates/block.py",
        ".devkit/overrides/team/gates/other.py",
    ]
    assert missing == ["gone.py"]


def test_project_registry_loads_gates_and_reports_problems(tmp_path: Path) -> None:
    assert deployed_gate_paths(tmp_path) == ([], [])
    deploy_gate(tmp_path, gate_source())
    deploy_gate(tmp_path, "raise RuntimeError('boom')\n", ".devkit/managed/team/gates/broken.py")
    deploy_gate(tmp_path, gate_source("message-nonempty", cls="Dup"), ".devkit/managed/team/gates/dup.py")
    registry = project_registry(tmp_path)
    assert [g.id for g in registry.get_all()] == ["team-block", "message-nonempty"]
    assert registry.sources["team-block"] == ".devkit/managed/team/gates/block.py"
    messages = [e.message for e in registry.errors]
    assert any("failed to load gate file .devkit/managed/team/gates/broken.py: boom" in m for m in messages)
    assert any("duplicate gate id 'message-nonempty'" in m for m in messages)


def test_unreadable_receipt_is_a_registry_error(tmp_path: Path) -> None:
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/installation.json").write_text("{nope")
    registry = project_registry(tmp_path)
    assert registry.errors and "unreadable receipt" in registry.errors[0].message


class Recorder(BaseGate):
    def __init__(self, gate_id: str, order: int, calls: list[str], result: GateResult | None = None) -> None:
        super().__init__(id=gate_id, description="", stage=Stage.PRE_COMMIT, order=order)
        self.calls = calls
        self.result = result

    def run(self, ctx: GateContext) -> GateResult | None:
        self.calls.append(self.id)
        return self.result


def test_run_stage_orders_gates_and_runs_past_failures(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source())
    registry = project_registry(tmp_path)
    calls: list[str] = []
    registry.register(Recorder("late", 500, calls))
    registry.register(Recorder("early", 10, calls, GateResult.skipped("nothing staged")))
    report = run_stage(_ctx(tmp_path), registry, GatesConfig())
    assert calls == ["early", "late"]
    assert [(r.gate_id, r.outcome) for r in report.runs] == [
        ("early", Outcome.SKIPPED),
        ("team-block", Outcome.FAILED),
        ("late", Outcome.PASSED),
    ]
    assert report.failed and report.runs[1].error is not None and report.runs[1].error.code == "TEST_REFUSED"


def test_run_stage_applies_enabled_and_settings(tmp_path: Path) -> None:
    deploy_gate(tmp_path, gate_source(enabled=False))
    registry = project_registry(tmp_path)
    report = run_stage(_ctx(tmp_path), registry, GatesConfig())
    assert [(r.gate_id, r.outcome, r.note) for r in report.runs] == [("team-block", Outcome.SKIPPED, "disabled")]

    config = GatesConfig({"team-block": GateEntry(True, {"allow": True})})
    report = run_stage(_ctx(tmp_path), registry, config)
    assert not report.failed and report.runs[0].note == "allowed"

    config = GatesConfig({"team-block": GateEntry(True, {"allow": "yes"})})
    report = run_stage(_ctx(tmp_path), registry, config)
    assert report.failed and report.runs[0].error is not None and "expected bool" in report.runs[0].error.message


def test_configured_gate_that_is_not_installed_fails_the_stage(tmp_path: Path) -> None:
    config = GatesConfig({"timeline": GateEntry(True)})
    report = run_stage(_ctx(tmp_path), default_registry(), config)
    assert report.failed and "not installed: ['timeline']" in report.errors[0].message


def test_message_gate(tmp_path: Path) -> None:
    message = tmp_path / "MSG"
    registry = default_registry()
    for text, failed in [
        ("feat: x\n", False),
        ("# comment\n\n   \n", True),
        ("\n# ------------------------ >8 ------------------------\ndiff\n", True),
    ]:
        message.write_text(text)
        report = run_stage(_ctx(tmp_path, Stage.COMMIT_MSG, "MSG"), registry, GatesConfig())
        assert report.failed is failed, text
    assert run_stage(_ctx(tmp_path, Stage.POST_COMMIT), GateRegistry(), GatesConfig()).runs == ()
