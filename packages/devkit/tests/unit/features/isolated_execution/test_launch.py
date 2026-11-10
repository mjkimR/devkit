"""Launch acknowledgement while the supervisor has not yet published state."""

from devkit_agt.features.isolated_execution.repositories import runs, runtime
from devkit_agt.features.isolated_execution.repositories.runs import Runs


def _runs(tmp_path) -> Runs:
    repository = object.__new__(Runs)
    repository.root = tmp_path / "base"
    repository.common = tmp_path / "base" / ".git"
    repository.base = tmp_path / "base"
    repository.directory = repository.common / "devkit" / "executions"
    return repository


def test_slow_supervisor_start_remains_pending(tmp_path, monkeypatch) -> None:
    # On a loaded host the supervisor may publish state.json after launch stops polling.
    supervisor = {"pid": 4242, "ppid": 1, "pgid": 4242, "birth": "supervisor", "argv": "runtime.py"}

    class SlowSupervisor:
        pid = 4242

        def __init__(self, *args, **kwargs) -> None:
            pass

        def poll(self) -> None:
            return None

    monkeypatch.setattr(runs.execution, "git", lambda root, *args: "c" * 40)
    monkeypatch.setattr(runs.subprocess, "Popen", SlowSupervisor)
    monkeypatch.setattr(runtime, "processes", lambda: {4242: dict(supervisor)})
    monkeypatch.setattr(runs.time, "sleep", lambda duration: None)
    repository = _runs(tmp_path)
    record = repository.launch("c" * 40, ("native",), None)
    assert record["outcome"] is None and record["phase"] == "preparing", record
    observed = repository.read(record["run_id"])
    assert observed["outcome"] is None and observed["phase"] == "preparing", observed


def test_exited_supervisor_without_state_is_unknown(tmp_path, monkeypatch) -> None:
    class ExitedSupervisor:
        pid = 4242

        def __init__(self, *args, **kwargs) -> None:
            pass

        def poll(self) -> int:
            return 1

    monkeypatch.setattr(runs.execution, "git", lambda root, *args: "c" * 40)
    monkeypatch.setattr(runs.subprocess, "Popen", ExitedSupervisor)
    monkeypatch.setattr(runtime, "processes", lambda: {})
    monkeypatch.setattr(runs.time, "sleep", lambda duration: None)
    repository = _runs(tmp_path)
    record = repository.launch("c" * 40, ("native",), None)
    assert record["outcome"] == "unknown"
    assert repository.read(record["run_id"])["outcome"] == "unknown"
