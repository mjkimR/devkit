"""Real CLI and detached supervisor probes over disposable consumer repositories."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest
from devkit_agt.features.isolated_execution.repositories import runtime

PYTHON = str(Path(getattr(sys, "_base_executable", sys.executable)).resolve())


def git(root: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.check_output(
        ["git", "-C", str(root), "-c", "user.name=test", "-c", "user.email=test@example.com", *args], text=True, env=env
    ).strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    (root / ".gitignore").write_text(".venv/\n")
    (root / "value").write_text("fixed")
    git(root, "add", ".")
    git(root, "commit", "-qm", "fixture")
    return root


def cli(repo: Path, *args: str, expected: int | None = None) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", "devkit_dist", "exec", *args, "--format", "json"]
        if args[0] != "start"
        else [sys.executable, "-m", "devkit_dist", "exec", "start", "--format", "json", *args[1:]],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )
    if expected is not None:
        assert result.returncode == expected, (result.stdout, result.stderr)
    assert not result.stderr, result.stderr
    return json.loads(result.stdout)


def launch(repo: Path, code: str, *, setup: str | None = None) -> dict[str, Any]:
    args = ["start", "--ref", git(repo, "rev-parse", "HEAD")]
    if setup is not None:
        args += ["--setup", setup]
    return cli(repo, *args, "--", PYTHON, "-c", code, expected=0)


def wait_file(path: Path) -> None:
    deadline = time.monotonic() + 10
    while not path.exists():
        assert time.monotonic() < deadline, str(path)
        time.sleep(0.02)


def test_fixed_sha_parent_exit_and_persistent_native_build(repo: Path) -> None:
    gate = repo.parent / "gate"
    ready = repo.parent / "ready"
    record = launch(
        repo,
        f"from pathlib import Path; import time; Path({str(ready)!r}).touch();\nwhile not Path({str(gate)!r}).exists(): time.sleep(.02)\nprint(Path('value').read_text())",
    )
    wait_file(ready)
    # Independent work completes before releasing the native command's latch.
    (repo / "value").write_text("advanced")
    git(repo, "add", "value")
    git(repo, "commit", "-qm", "source advances")
    assert git(repo, "rev-parse", "HEAD") != record["sha"]
    assert cli(repo, "status", record["run_id"], expected=0)["phase"] == "running"
    gate.touch()
    done = cli(repo, "wait", record["run_id"], expected=0)
    assert done["sha"] == record["sha"] and done["exit_code"] == 0
    assert cli(repo, "logs", record["run_id"], expected=0)["lines"] == ["fixed"]
    assert Path(done["checkout"]).is_dir()
    assert record["run_id"] in {r["run_id"] for r in cli(repo, "list", expected=0)["runs"]}
    clean = cli(repo, "wait", record["run_id"], "--clean", expected=0)
    assert clean["cleanup"]["outcome"] == "cleaned"
    assert Path(clean["result"]).is_file() and Path(clean["log"]).is_file()
    assert cli(repo, "clean", record["run_id"], expected=0)["cleanup"]["outcome"] == "already_clean"


def test_setup_failure_never_runs_native_and_retains_evidence(repo: Path) -> None:
    touched = repo.parent / "should-not-exist"
    record = launch(repo, f"from pathlib import Path; Path({str(touched)!r}).touch()", setup="exit 17")
    done = cli(repo, "wait", record["run_id"], "--clean", expected=1)
    assert done["outcome"] == "setup_failed" and done["exit_code"] is None
    assert done["cleanup"]["outcome"] == "cleaned"
    assert not touched.exists() and Path(done["log"]).is_file()


def test_failed_result_survives_cleanup_and_nonpytest_argv(repo: Path) -> None:
    record = cli(
        repo,
        "start",
        "--ref",
        git(repo, "rev-parse", "HEAD"),
        "--",
        "/bin/sh",
        "-c",
        "echo native-build; exit 7",
        expected=0,
    )
    done = cli(repo, "wait", record["run_id"], "--clean", expected=1)
    assert done["outcome"] == "failed" and done["exit_code"] == 7
    assert cli(repo, "logs", record["run_id"], expected=1)["lines"] == ["native-build"]


def test_wait_timeout_and_interruption_never_cancel(repo: Path) -> None:
    record = launch(repo, "import time; time.sleep(30)")
    observed = cli(repo, "wait", record["run_id"], "--timeout", "0.05", "--clean", expected=2)
    assert observed["observer"] == "timeout" and "cleanup" not in observed
    waiter = subprocess.Popen(
        [sys.executable, "-m", "devkit_dist", "exec", "wait", record["run_id"], "--clean", "--format", "json"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(0.2)
    waiter.send_signal(signal.SIGINT)
    waiter.communicate(timeout=5)
    assert cli(repo, "status", record["run_id"], expected=0)["phase"] in {"preparing", "running"}
    refused = cli(repo, "clean", record["run_id"], expected=2)
    assert refused["cleanup"]["outcome"] == "refused" and Path(record["checkout"]).exists()
    cancelled = cli(repo, "cancel", record["run_id"], expected=1)
    assert cancelled["outcome"] == "cancelled" and Path(record["checkout"]).exists()
    assert not runtime.live_owned(cancelled)
    cli(repo, "wait", record["run_id"], "--clean", expected=1)


@pytest.mark.parametrize("setup", [False, True])
def test_cancel_managed_nested_sessions_and_surviving_child(repo: Path, setup: bool) -> None:
    ready = repo.parent / "child-ready"
    child = f"import time; from pathlib import Path; Path({str(ready)!r}).touch(); time.sleep(30)"
    # A nested session represents compact's independent process group. The outer leader exits.
    code = f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child!r}],start_new_session=True); time.sleep(.5)"
    if setup:
        import shlex

        record = launch(repo, "raise RuntimeError('native must not execute')", setup=shlex.join([PYTHON, "-c", code]))
    else:
        record = launch(repo, code)
    wait_file(ready)
    time.sleep(0.7)
    done = cli(repo, "cancel", record["run_id"], expected=1)
    assert done["outcome"] == "cancelled"
    assert len(done["managed"]) >= 2 and not runtime.live_owned(done)
    cli(repo, "wait", record["run_id"], "--clean", expected=1)


def test_unknown_supervisor_and_reused_pid_never_signal_or_clean(repo: Path) -> None:
    record = launch(repo, "import time; time.sleep(30)")
    state_path = Path(record["result"]).with_name("state.json")
    state = json.loads(state_path.read_text())
    actual = state["supervisor"]
    state["supervisor"] = {**actual, "birth": "not-the-same-process"}
    # Pause the real supervisor so injected lost-identity evidence remains stable.
    os.kill(actual["pid"], signal.SIGSTOP)
    try:
        runtime.atomic(state_path, state)
        unknown = cli(repo, "status", record["run_id"], expected=2)
        assert unknown["outcome"] == "unknown"
        assert cli(repo, "cancel", record["run_id"], expected=2)["outcome"] == "unknown"
        assert cli(repo, "wait", record["run_id"], "--clean", expected=2)["observer"] == "unknown"
        assert cli(repo, "clean", record["run_id"], expected=2)["cleanup"]["outcome"] == "refused"
        assert actual["pid"] in runtime.processes()
    finally:
        os.kill(actual["pid"], signal.SIGCONT)
    # Resume trusted ownership and request cancellation after state is refreshed.
    time.sleep(0.2)
    cli(repo, "cancel", record["run_id"], expected=1)


def test_dirty_and_unrelated_checkout_refuse_cleanup(repo: Path) -> None:
    record = launch(repo, "from pathlib import Path; Path('diagnostic').write_text('retain')")
    done = cli(repo, "wait", record["run_id"], "--clean", expected=2)
    assert done["outcome"] == "passed" and done["cleanup"]["outcome"] == "refused"
    checkout = Path(done["checkout"])
    assert (checkout / "diagnostic").read_text() == "retain"
    marker = Path(git(checkout, "rev-parse", "--absolute-git-dir")) / "devkit-execution.json"
    marker.write_text("{}")
    refused = cli(repo, "clean", record["run_id"], expected=2)
    assert "ownership differs" in refused["cleanup"]["detail"]
    assert checkout.is_dir()


def test_concurrent_cleanup_is_idempotent(repo: Path) -> None:
    record = launch(repo, "print('done')")
    cli(repo, "wait", record["run_id"], expected=0)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: cli(repo, "wait", record["run_id"], "--clean", expected=0), range(2)))
    assert {r["cleanup"]["outcome"] for r in results} == {"cleaned", "already_clean"}
    assert all(Path(r["result"]).is_file() for r in results)


def test_checkout_environment_and_dependencies_stay_fixed(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / "dependency").write_text("dependency-at-A")
    git(repo, "add", "dependency")
    git(repo, "commit", "-qm", "dependency at A")
    gate = repo.parent / "env-gate"
    ready = repo.parent / "env-ready"
    monkeypatch.setenv("VIRTUAL_ENV", "/not/the/project/environment")
    monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", "/not/the/project/environment")
    monkeypatch.setenv("PYTHONPATH", "/not/the/project/environment")
    setup = "mkdir -p .venv/bin; cp dependency .venv/pinned"
    code = f"from pathlib import Path; import time,os; Path({str(ready)!r}).touch();\nwhile not Path({str(gate)!r}).exists(): time.sleep(.02)\nassert all(k not in os.environ for k in ('VIRTUAL_ENV','UV_PROJECT_ENVIRONMENT','PYTHONPATH')); print(Path('.venv/pinned').read_text())"
    record = launch(repo, code, setup=setup)
    wait_file(ready)
    (repo / "dependency").write_text("dependency-at-B")
    git(repo, "add", "dependency")
    git(repo, "commit", "-qm", "dependency at B")
    gate.touch()
    done = cli(repo, "wait", record["run_id"], expected=0)
    assert cli(repo, "logs", record["run_id"], expected=0)["lines"] == ["dependency-at-A"]
    assert Path(done["environment"]).is_relative_to(Path(done["checkout"]))


def test_locked_sync_failure_blocks_native(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    (repo / ".devkit/installation.json").write_text("{}")
    git(repo, "add", ".devkit")
    git(repo, "commit", "-qm", "receipt requires isolated sync")
    marker = repo.parent / "native-forbidden"
    record = launch(repo, f"from pathlib import Path; Path({str(marker)!r}).touch()")
    done = cli(repo, "wait", record["run_id"], expected=1)
    assert done["outcome"] == "setup_failed" and "locked sync" in done["detail"]
    assert not marker.exists()


def test_supervisor_interruption_confirms_managed_shutdown(repo: Path) -> None:
    ready = repo.parent / "interrupt-ready"
    record = launch(repo, f"from pathlib import Path; import time; Path({str(ready)!r}).touch(); time.sleep(30)")
    wait_file(ready)
    state = cli(repo, "status", record["run_id"], expected=0)
    os.kill(state["supervisor"]["pid"], signal.SIGTERM)
    done = cli(repo, "wait", record["run_id"], expected=1)
    assert done["outcome"] == "interrupted" and not runtime.live_owned(done)
    cli(repo, "wait", record["run_id"], "--clean", expected=1)


def test_lost_supervisor_without_terminal_evidence_is_unknown(repo: Path) -> None:
    ready = repo.parent / "lost-ready"
    record = launch(repo, f"from pathlib import Path; import time; Path({str(ready)!r}).touch(); time.sleep(1)")
    wait_file(ready)
    state = cli(repo, "status", record["run_id"], expected=0)
    os.kill(state["supervisor"]["pid"], signal.SIGKILL)
    time.sleep(0.1)
    unknown = cli(repo, "wait", record["run_id"], "--clean", expected=2)
    assert unknown["outcome"] == "unknown" and Path(record["checkout"]).is_dir()
    assert cli(repo, "clean", record["run_id"], expected=2)["cleanup"]["outcome"] == "refused"
    # The fixture's short-lived unmanaged remainder exits itself; no unsafe recovery signalling.
    time.sleep(1)


def test_actual_compact_wrapper_cancellation(repo: Path) -> None:
    # Install a fixture-local wrapper invoking the existing compact API in the caller environment.
    # Native argv is generic: the captured supervisor imports no compact implementation.
    ready = repo.parent / "compact-ready"
    child = f"from pathlib import Path; import time; Path({str(ready)!r}).touch(); time.sleep(30)"
    record = cli(
        repo,
        "start",
        "--ref",
        git(repo, "rev-parse", "HEAD"),
        "--",
        sys.executable,
        "-m",
        "devkit_dist",
        "run",
        "--",
        PYTHON,
        "-c",
        child,
        expected=0,
    )
    wait_file(ready)
    state = cli(repo, "status", record["run_id"], expected=0)
    assert len({p["pgid"] for p in state["managed"]}) >= 2
    done = cli(repo, "cancel", record["run_id"], expected=1)
    assert done["outcome"] == "cancelled" and not runtime.live_owned(done)
    cli(repo, "wait", record["run_id"], "--clean", expected=1)
