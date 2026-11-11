"""Public execution inspection remains bounded independently of stored evidence size."""

import json

import pytest
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
    assert result.stdout == "[PAGE: total=0 offset=0 limit=20 count=0 next=-]\n"


def _paged_runs(monkeypatch, total: int = 25) -> None:
    from devkit_agt.features.isolated_execution.usecases.operations import ListExecutions

    def execute(self, root, *, limit: int = 20, offset: int = 0):
        runs = [{"run_id": f"{index:032x}", "sha": "b" * 40, "phase": "passed"} for index in range(total)]
        return {
            "runs": runs[offset : offset + limit],
            "total": total,
            "offset": offset,
            "limit": limit,
            "next_offset": offset + limit if offset + limit < total else None,
        }

    monkeypatch.setattr(ListExecutions, "execute", execute)


def test_list_text_pages_with_shared_page_lines(monkeypatch) -> None:
    _paged_runs(monkeypatch)
    result = CliRunner().invoke(cli, ["list"])
    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    assert len(lines) == 22
    assert all(line.startswith("[EXECUTION_RUN: ") for line in lines[:20])
    assert lines[20:] == [
        "[PAGE: total=25 offset=0 limit=20 count=20 next=20]",
        "[NEXT_CMD: uv run devkit exec list --limit 20 --offset 20]",
    ]
    assert "EXECUTION_LIST" not in result.stdout


def test_list_text_last_page_has_no_next_command(monkeypatch) -> None:
    _paged_runs(monkeypatch)
    result = CliRunner().invoke(cli, ["list", "--offset", "20"])
    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    assert len(lines) == 6
    assert all(line.startswith("[EXECUTION_RUN: ") for line in lines[:5])
    assert lines[5] == "[PAGE: total=25 offset=20 limit=20 count=5 next=-]"


def test_list_text_next_command_repeats_custom_limit(monkeypatch) -> None:
    _paged_runs(monkeypatch)
    result = CliRunner().invoke(cli, ["list", "--limit", "5", "--offset", "5"])
    assert result.exit_code == 0
    assert result.stdout.splitlines()[-2:] == [
        "[PAGE: total=25 offset=5 limit=5 count=5 next=10]",
        "[NEXT_CMD: uv run devkit exec list --limit 5 --offset 10]",
    ]


def test_list_json_keeps_its_keys(monkeypatch) -> None:
    _paged_runs(monkeypatch)
    result = CliRunner().invoke(cli, ["list", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert set(data) == {"runs", "total", "offset", "limit", "next_offset"}
    assert data["next_offset"] == 20


@pytest.mark.parametrize("args", [["--limit", "0"], ["--limit", "101"], ["--offset", "-1"]])
def test_list_rejects_out_of_bound_paging(args, tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["list", *args])
    assert result.exit_code == 2
    assert "EXECUTION_LIST_ARGUMENT_INVALID" in result.output
    assert "[PAGE:" not in result.stdout


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
