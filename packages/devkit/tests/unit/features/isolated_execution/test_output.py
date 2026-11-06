"""Public execution inspection remains bounded independently of stored evidence size."""

import json

from click.testing import CliRunner
from devkit_agt.features.isolated_execution.cli import cli
from devkit_agt.features.isolated_execution.usecases.operations import WaitExecution


def test_wait_projects_large_process_history_and_argv(monkeypatch) -> None:
    record = {
        "run_id": "a" * 32,
        "sha": "b" * 40,
        "phase": "passed",
        "outcome": "passed",
        "exit_code": 0,
        "argv": ["x" * 2000] * 1000,
        "managed": [{"pid": n, "argv": "y" * 2000} for n in range(1000)],
        "result": "/evidence/result.json",
        "log": "/evidence/output.log",
    }
    monkeypatch.setattr(WaitExecution, "execute", lambda *args, **kwargs: record)
    result = CliRunner().invoke(cli, ["wait", "a" * 32, "--format", "json"])
    assert result.exit_code == 0
    assert len(result.stdout.encode()) < 32768
    data = json.loads(result.stdout)
    assert data["managed_count"] == 1000 and data["argv_truncated"]
    assert data["result"] == record["result"]
    assert len(record["managed"]) == 1000  # public projection never mutates ownership evidence


def test_empty_list_has_explicit_text_result(monkeypatch) -> None:
    from devkit_agt.features.isolated_execution.usecases.operations import ListExecutions

    monkeypatch.setattr(
        ListExecutions,
        "execute",
        lambda *args, **kwargs: {"runs": [], "total": 0, "offset": 0, "limit": 20, "next_offset": None},
    )
    result = CliRunner().invoke(cli, ["list"])
    assert result.exit_code == 0
    assert result.stdout == "[EXECUTION_LIST: total=0 offset=0 count=0 next=-]\n"


def test_text_fields_quote_paths_and_preserve_cleanup_reason(monkeypatch) -> None:
    from devkit_agt.features.isolated_execution.usecases.operations import CleanExecution

    record = {
        "run_id": "a" * 32,
        "sha": "b" * 40,
        "phase": "passed",
        "outcome": "passed",
        "exit_code": 0,
        "log": "/path with [brackets]/output.log",
        "cleanup_requested": True,
        "cleanup": {"outcome": "refused", "code": "EXECUTION_CLEAN_REFUSED", "detail": "checkout is dirty"},
    }
    monkeypatch.setattr(CleanExecution, "execute", lambda *args, **kwargs: record)
    result = CliRunner().invoke(cli, ["clean", "a" * 32])
    assert result.exit_code == 2
    assert 'log="/path with [brackets]/output.log"' in result.stdout
    assert 'detail="checkout is dirty"' in result.stdout
    assert "EXECUTION_CLEAN_REFUSED" in result.stdout


def test_list_paginates_and_corrupt_record_does_not_hide_other_runs(tmp_path, monkeypatch) -> None:
    from devkit_agt.features.isolated_execution.repositories.runs import error
    from devkit_agt.features.isolated_execution.usecases import operations

    for index in range(25):
        directory = tmp_path / f"{index:032x}"
        directory.mkdir()
        (directory / "manifest.json").write_text("{}")

    class Repository:
        directory = tmp_path

        def read(self, run_id):
            if int(run_id, 16) == 2:
                raise error("EXECUTION_RECORD_UNREADABLE", "fixture corruption")
            return {
                "run_id": run_id,
                "sha": "b" * 40,
                "phase": "passed",
                "argv": ["x" * 100000],
                "managed": [{"pid": n} for n in range(1000)],
            }

    monkeypatch.setattr(operations, "Runs", lambda root: Repository())
    first = operations.ListExecutions().execute(tmp_path)
    assert len(first["runs"]) == 20 and first["next_offset"] == 20 and first["total"] == 25
    assert first["runs"][2]["outcome"] == "unknown"
    assert len(json.dumps(first)) < 10000
    second = operations.ListExecutions().execute(tmp_path, offset=20)
    assert len(second["runs"]) == 5 and second["next_offset"] is None
