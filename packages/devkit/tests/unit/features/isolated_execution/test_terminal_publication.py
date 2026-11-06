"""Observation rechecks terminal evidence published during supervisor inspection."""

import json
from typing import Any

import pytest
from devkit.advisory import AdvisoryError
from devkit_agt.features.isolated_execution.repositories import runtime
from devkit_agt.features.isolated_execution.repositories.runs import Runs
from devkit_agt.features.isolated_execution.services import lifecycle


@pytest.mark.parametrize("supervisor_reused", [False, True])
@pytest.mark.parametrize("publication", ["passed", "missing", "mismatched", "nonterminal"])
def test_wait_rechecks_terminal_publication(tmp_path, monkeypatch, supervisor_reused, publication):
    run_id = "a" * 32
    runs = object.__new__(Runs)
    runs.base = tmp_path / "consumer"
    runs.common = runs.base / ".git"
    runs.directory = tmp_path / "evidence"
    directory = runs.path(run_id)
    directory.mkdir(parents=True)
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "repository": str(runs.common),
        "checkout": str(runs.base.parent / f"{runs.base.name}-exec-{run_id}"),
        "sha": "b" * 40,
        "argv": ["native"],
        "outcome": None,
        "phase": "running",
        "supervisor": {"pid": 100, "birth": "original"},
    }
    for name in ("manifest.json", "state.json"):
        (directory / name).write_text(json.dumps(manifest))
    terminal = dict(manifest, phase="passed", outcome="passed", exit_code=0)
    terminal["ownership"] = {"groups": [], "quiescent": True, "verified_at": 1.0}
    if publication == "mismatched":
        terminal["sha"] = "c" * 40
    elif publication == "nonterminal":
        terminal.update(phase="running", outcome=None)
    cleanup = {"outcome": "refused", "code": "EXECUTION_CLEAN_REFUSED"}
    runtime.atomic(directory / "cleanup.json", cleanup)

    def finishes_during_inspection():
        if publication != "missing":
            runtime.atomic(directory / "result.json", terminal)
            runtime.atomic(directory / "state.json", terminal)
        return {100: {"pid": 100, "birth": "unrelated"}} if supervisor_reused else {}

    monkeypatch.setattr(runtime, "processes", finishes_during_inspection)
    if publication == "mismatched":
        with pytest.raises(AdvisoryError):
            lifecycle.wait(runs, run_id, 1, False)
    else:
        observed = lifecycle.wait(runs, run_id, 1, False)
        assert observed["outcome"] == ("passed" if publication == "passed" else "unknown")
        assert observed["cleanup"] == cleanup
