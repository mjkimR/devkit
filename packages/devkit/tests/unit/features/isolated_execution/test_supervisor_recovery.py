"""Supervisor-level regressions from independent review round two."""

import json
import os
from typing import cast

import pytest
from devkit_agt.features.isolated_execution.repositories import runtime
from devkit_agt.features.isolated_execution.repositories.runs import Runs as RunRepository


@pytest.mark.parametrize("cancel_requested", [False, True])
def test_terminal_requires_group_observation_after_reap(tmp_path, monkeypatch, cancel_requested):
    # ps enumerates/processes a non-atomic process list before poll reaps the
    # leader. A same-group orphan missing from that first pre-reap scan is
    # visible in the following scan. The established group must survive until
    # a post-reap observation either discovers it or verifies emptiness.
    directory = tmp_path / "run"
    directory.mkdir()
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    record = {
        "run_id": "a" * 32,
        "checkout": str(checkout),
        "base": str(tmp_path),
        "sha": "b" * 40,
        "setup": None,
        "argv": ["native"],
    }
    (directory / "manifest.json").write_text(json.dumps(record))
    state = {"active": None, "preparation": 0, "native": 0}

    def row(pid, group):
        return {"pid": pid, "ppid": 1, "pgid": group, "birth": str(pid), "argv": "fixture"}

    class Child:
        def __init__(self, argv, **kwargs):
            self.pid = 100 if len(argv) > 1 and str(argv[1]).endswith("checkout.py") else 200
            self.returncode = None
            state["active"] = self

        def poll(self):
            self.returncode = 0
            return 0

    def snapshot():
        child = state["active"]
        if child is None:
            return {os.getpid(): row(os.getpid(), os.getpid())}
        if child.pid == 100:
            state["preparation"] += 1
            return {100: row(100, 100)} if state["preparation"] == 1 else {}
        state["native"] += 1
        if state["native"] == 1:
            if cancel_requested:
                (directory / "cancel").touch()
            return {}  # pre-reap scan did not capture the newly orphaned child
        if state["native"] == 2:
            return {201: row(201, 200)}
        return {}

    monkeypatch.setattr(runtime.subprocess, "Popen", Child)
    monkeypatch.setattr(runtime, "processes", snapshot)
    monkeypatch.setattr(runtime.signal, "signal", lambda *args: None)
    monkeypatch.setattr(runtime.os, "kill", lambda *args: None)
    monkeypatch.setattr(runtime.time, "sleep", lambda duration: None)
    runtime.supervise(directory)
    result = json.loads((directory / "result.json").read_text())
    assert result["outcome"] == ("cancelled" if cancel_requested else "passed"), result
    assert 201 in {p["pid"] for p in result["managed"]}, (
        "terminal result bypassed retained group before post-reap observation"
    )


def test_interrupted_cleanup_remains_recorded_and_inspectable(tmp_path, monkeypatch):
    import contextlib

    import pytest
    from devkit_agt.features.isolated_execution.services import lifecycle

    (tmp_path / "result.json").write_text("{}")
    record = {
        "run_id": "a" * 32,
        "outcome": "passed",
        "checkout": "/run-owned/checkout",
        "sha": "b" * 40,
        "managed": [],
    }

    class Runs:
        base = tmp_path

        def path(self, run_id):
            return tmp_path

        def read(self, run_id):
            result = dict(record)
            if (tmp_path / "cleanup.json").exists():
                result["cleanup"] = json.loads((tmp_path / "cleanup.json").read_text())
            return result

        def cleanup_lock(self, run_id):
            return contextlib.nullcontext()

    def interrupted_remove(*args):
        raise KeyboardInterrupt()

    monkeypatch.setattr(lifecycle, "remove", interrupted_remove)
    monkeypatch.setattr(runtime, "processes", lambda: {})
    with pytest.raises(KeyboardInterrupt):
        lifecycle.clean(cast(RunRepository, Runs()), "a" * 32)
    observed = Runs().read("a" * 32)
    assert "cleanup" in observed, "interrupted cleanup left no durable in-progress/unfinished cleanup evidence"


@pytest.mark.parametrize("stage", ["preparing", "native"])
def test_discovery_failure_after_launch_never_creates_terminal_evidence(tmp_path, monkeypatch, stage):
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
    state = {"child": None, "scans": 0}

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
            return {}
        if stage == "preparing" or child.pid == 200:
            raise OSError("process enumeration unavailable with a writer active")
        state["scans"] += 1
        return {} if state["scans"] > 1 else {100: {"pid": 100, "ppid": 1, "pgid": 100, "birth": "prep"}}

    monkeypatch.setattr(runtime.subprocess, "Popen", Child)
    monkeypatch.setattr(runtime, "processes", snapshot)
    monkeypatch.setattr(runtime.signal, "signal", lambda *args: None)
    runtime.supervise(directory)
    assert not (directory / "result.json").exists()
    result = json.loads((directory / "state.json").read_text())
    assert result["outcome"] == "unknown"
    assert result["ownership"]["quiescent"] is False
    assert result["ownership"]["groups"] == [100 if stage == "preparing" else 200]


def test_retired_stage_pid_reuse_does_not_block_or_signal_new_stage(tmp_path, monkeypatch):
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
    state = {"stage": 0, "scan": 0}

    class Child:
        def __init__(self, *args, **kwargs):
            self.pid = 100
            self.returncode = None
            state["stage"] += 1
            state["scan"] = 0

        def poll(self):
            self.returncode = 0
            return 0

    def snapshot():
        state["scan"] += 1
        if not state["stage"] or state["scan"] > 1:
            return {}
        return {100: {"pid": 100, "ppid": 1, "pgid": 100, "birth": str(state["stage"])}}

    monkeypatch.setattr(runtime.subprocess, "Popen", Child)
    monkeypatch.setattr(runtime, "processes", snapshot)
    monkeypatch.setattr(runtime.signal, "signal", lambda *args: None)
    runtime.supervise(directory)
    result = json.loads((directory / "result.json").read_text())
    assert result["outcome"] == "passed"
    assert [p["birth"] for p in result["managed"]] == ["1", "2"]
    monkeypatch.setattr(runtime, "processes", lambda: {100: {"pid": 100, "birth": "unrelated"}})
    assert not runtime.live_owned(result)
