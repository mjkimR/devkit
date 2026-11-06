"""Terminal ownership guards for reused leaders and retained legacy evidence."""

import contextlib
import json
import os
from typing import cast

import pytest
from devkit_agt.features.isolated_execution.repositories import runtime
from devkit_agt.features.isolated_execution.repositories.runs import Runs as RunRepository
from devkit_agt.features.isolated_execution.services import lifecycle


def test_reused_unobserved_leader_is_never_adopted_or_signalled(tmp_path, monkeypatch):
    directory = tmp_path / "run"
    directory.mkdir()
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    (directory / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": "a" * 32,
                "checkout": str(checkout),
                "base": str(tmp_path),
                "sha": "b" * 40,
                "setup": None,
                "argv": ["native"],
            }
        )
    )
    state = {"child": None, "prep": 0, "native": 0}
    signalled = []

    def row(pid, group, birth):
        return {"pid": pid, "ppid": 1, "pgid": group, "birth": birth, "argv": "fixture"}

    class Child:
        def __init__(self, argv, **kwargs):
            self.pid = 100 if len(argv) > 1 else 200
            self.returncode = None
            state["child"] = self

        def poll(self):
            self.returncode = 0
            return 0

    def snapshot():
        child = state["child"]
        if child is None:
            return {os.getpid(): row(os.getpid(), os.getpid(), "supervisor")}
        if child.pid == 100:
            state["prep"] += 1
            return {100: row(100, 100, "preparation")} if state["prep"] == 1 else {}
        state["native"] += 1
        if state["native"] == 1:
            return {}  # Direct leader exited before the first scan; identity not observed.
        if state["native"] == 2:
            return {201: row(201, 200, "owned-orphan")}
        if state["native"] in (3, 4):
            # The orphan and its group have now exited; before an empty scan,
            # an unrelated process receives reused PID/PGID 200.
            (directory / "cancel").touch()
            return {200: row(200, 200, "unrelated-reused-leader")}
        return {}

    monkeypatch.setattr(runtime.subprocess, "Popen", Child)
    monkeypatch.setattr(runtime, "processes", snapshot)
    monkeypatch.setattr(runtime.signal, "signal", lambda *args: None)
    monkeypatch.setattr(runtime.os, "kill", lambda pid, sig: signalled.append(pid))
    monkeypatch.setattr(runtime.time, "sleep", lambda duration: None)
    runtime.supervise(directory)
    assert 200 not in signalled, f"unrelated reused leader was signalled: {signalled}"
    state_record = json.loads((directory / "state.json").read_text())
    assert state_record["outcome"] == "unknown"
    assert not (directory / "result.json").exists()


def test_clean_requires_positive_quiescence_proof(tmp_path, monkeypatch):
    (tmp_path / "result.json").write_text("{}")
    record = {
        "run_id": "a" * 32,
        "outcome": "passed",
        "checkout": "/owned/checkout",
        "sha": "b" * 40,
        "managed": [{"pid": 100, "birth": "retired-preparation", "pgid": 100}],
    }

    class Runs:
        base = tmp_path

        def path(self, run_id):
            return tmp_path

        def read(self, run_id):
            return dict(record)

        def cleanup_lock(self, run_id):
            return contextlib.nullcontext()

    removed = []
    # A retained terminal from the preceding captured runtime missed this writer.
    monkeypatch.setattr(
        runtime, "processes", lambda: {201: {"pid": 201, "ppid": 1, "pgid": 200, "birth": "surviving-owned-writer"}}
    )
    monkeypatch.setattr(lifecycle, "remove", lambda *args: removed.append(args) or "cleaned")
    observed = lifecycle.clean(cast(RunRepository, Runs()), "a" * 32)
    assert not removed, "terminal evidence without post-exit ownership proof authorized cleanup"
    assert observed["cleanup"]["outcome"] == "refused"


@pytest.mark.parametrize(
    "proof",
    [
        None,
        {},
        {"quiescent": True},
        {"quiescent": False, "groups": [], "verified_at": 1.0},
        {"quiescent": True, "groups": [200], "verified_at": 1.0},
        {"quiescent": True, "groups": [], "verified_at": "1"},
        {"quiescent": True, "groups": [], "verified_at": True},
        {"quiescent": True, "groups": [], "verified_at": float("nan")},
    ],
)
def test_missing_or_incomplete_proof_remains_unresolved(proof):
    assert not runtime.confirmed_quiescence({"ownership": proof, "managed": []})


def test_prelaunch_cancellation_records_explicit_no_process_proof(tmp_path, monkeypatch):
    directory = tmp_path / "run"
    directory.mkdir()
    (directory / "cancel").touch()
    (directory / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": "a" * 32,
                "checkout": str(tmp_path / "checkout"),
                "base": str(tmp_path),
                "sha": "b" * 40,
                "setup": None,
                "argv": ["native"],
            }
        )
    )
    monkeypatch.setattr(runtime, "processes", lambda: {})
    monkeypatch.setattr(runtime.signal, "signal", lambda *args: None)

    def never_launch(*args, **kwargs):
        raise AssertionError("prelaunch cancellation must not create a subprocess")

    monkeypatch.setattr(runtime.subprocess, "Popen", never_launch)
    runtime.supervise(directory)
    result = json.loads((directory / "result.json").read_text())
    assert result["outcome"] == "cancelled"
    assert result["ownership"]["basis"] == "no_process_started"
    assert not runtime.live_owned(result)
