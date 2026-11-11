"""Committed adjacent extension evidence across turns and explicit scope replacement."""

import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml
from click.testing import CliRunner

from devkit_spec.cli import cli
from devkit_spec.features.worker.usecases.inspect import InspectWorkerUseCase

UNIT = "specs/2026-11/20261104-example"
PATH = "src/feature/helper.py"
REASON = "shares parsing: AC-01, AC-02"
EXTENSION = {"path": PATH, "task": 1, "reason": REASON, "requirements": ["AC-01", "AC-02"]}


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def commit(root: Path) -> str:
    git(root, "add", ".")
    git(root, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fixture")
    return git(root, "rev-parse", "HEAD")


def tasks(root: Path, *, path: str = PATH, reason: str = REASON, annotation: bool = True) -> None:
    note = f" (scope extension: {reason})" if annotation else ""
    boundary = f", `{PATH}`" if annotation and path != PATH else ""
    boundary += f", `{path}`{note}" if annotation else ""
    write(
        root,
        f"{UNIT}/tasks.md",
        f"- [x] Task 1\n  - **_Boundary**: `src/feature/code.py`{boundary}\n  - _Requirements: AC-01, AC-02_\n",
    )


def worker(root: Path, seq: int, extensions: list | None = None, *, problem: bool = False) -> str:
    data: dict[str, Any] = {"kind": "worker", "stage": "build-verify", "status": "failed" if problem else "completed"}
    if extensions is not None:
        data["scope_extensions"] = extensions
    if problem:
        data["diff_scope"] = {"base": git(root, "rev-parse", "main")}
        data["problem"] = {"cause": "fixture", "recovery": "fix"}
    write(root, f"{UNIT}/envelopes/worker-{seq:02}.yaml", yaml.safe_dump(data))
    return commit(root)


def passed(_root, _args):
    return {"status": "pass", "result": {}}


def inspect(root: Path, **kwargs):
    return InspectWorkerUseCase().execute(root, runner=passed, **kwargs)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-qb", "main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    write(tmp_path, "seed", "initial")
    commit(tmp_path)
    git(tmp_path, "checkout", "-qb", "dev-example")
    git(tmp_path, "config", "branch.dev-example.devkitBase", "main")
    write(
        tmp_path, f"{UNIT}/spec.md", "---\nworkflow: sdd-spec-feature\n---\n### [AC-01] Parse\n### [AC-02] Validate\n"
    )
    write(tmp_path, "src/feature/code.py", "pass\n")
    tasks(tmp_path)
    write(tmp_path, PATH, "pass\n")
    return tmp_path


def test_valid_extension_is_additive_and_survives_next_turn(repo: Path) -> None:
    first = worker(repo, 1, [EXTENSION])
    result = inspect(repo)
    assert result["exit_code"] == 0
    assert result["checks"]["scope_extensions"] == {"status": "pass"}
    assert result["scope_extensions"] == [{**EXTENSION, "source": "worker-01.yaml"}]
    entry = next(e for e in result["scope"] if e["path"] == PATH)
    assert entry["extension"] == {"reason": REASON} and entry["task"] == 1
    worker(repo, 2)
    second = inspect(repo)
    assert second["base"] == first
    assert second["scope_extensions"] == result["scope_extensions"]
    assert second["checks"]["scope_extensions"]["status"] == "pass"


@pytest.mark.parametrize("changes", [{"reason": "wrong"}, {"task": 2}, {"requirements": ["AC-03"]}])
def test_record_disagreement_fails(repo: Path, changes: dict) -> None:
    worker(repo, 1, [{**EXTENSION, **changes}])
    result = inspect(repo)
    assert result["checks"]["scope_extensions"]["status"] == "fail"
    assert "SPEC_WORKER_SCOPE_EXTENSION_INVALID" in [e["code"] for e in result["errors"]]


def test_missing_record_and_removed_annotation_never_add_historical_scope(repo: Path) -> None:
    worker(repo, 1)
    assert inspect(repo)["checks"]["scope_extensions"]["status"] == "fail"
    worker(repo, 2, [EXTENSION])
    tasks(repo, annotation=False)
    worker(repo, 3)
    result = inspect(repo)
    assert not any(e["path"] == PATH for e in result["scope"])
    assert result["checks"]["scope_extensions"]["status"] == "fail"


def test_latest_record_wins_and_metadata_change_needs_new_record(repo: Path) -> None:
    worker(repo, 1, [EXTENSION])
    tasks(repo, reason="new reason AC-01")
    worker(repo, 2)
    assert inspect(repo)["checks"]["scope_extensions"]["status"] == "fail"
    worker(repo, 3, [{**EXTENSION, "reason": "new reason AC-01"}])
    result = inspect(repo)
    assert result["checks"]["scope_extensions"]["status"] == "pass"
    assert result["scope_extensions"][0]["source"] == "worker-03.yaml"


@pytest.mark.parametrize(
    "path",
    [
        ".devkit/owned.md",
        ".agents/skills/example.md",
        "docs/architecture/contract.md",
        "specs/2026-11/20261104-other/spec.md",
        "src/bundle/rules/example/rule.py",
        ".github/workflows/ci.yml",
        "uv.lock",
        "packages/devkit-viewer/frontend/package.json",
        "AGENTS.md",
        "packages/example/CLAUDE.md",
    ],
)
def test_protected_extension_fails_even_inside_derived_scope(repo: Path, path: str) -> None:
    tasks(repo, path=path)
    write(repo, path, "protected\n")
    # Keep the fixture's helper initially declared so scope remains complete.
    write(repo, PATH, "pass\n")
    worker(repo, 1, [{**EXTENSION, "path": path}])
    result = inspect(repo)
    assert result["checks"]["scope_extensions"]["status"] == "fail"
    assert any(issue["path"] == path for issue in result["checks"]["scope_extensions"]["issues"])
    assert result["checks"]["scope"]["status"] == "pass"
    assert [e["code"] for e in result["errors"]] == ["SPEC_WORKER_SCOPE_EXTENSION_INVALID"]


@pytest.mark.parametrize(
    "path", ["docs/development/reference/core.md", "packages/example/README.md", "guides/INSTALL_GUIDE.md"]
)
def test_derived_reference_extension_passes(repo: Path, path: str) -> None:
    tasks(repo, path=path, reason="restates devkit_core.core.memo")
    write(repo, path, "reference\n")
    write(repo, PATH, "pass\n")
    worker(repo, 1, [{**EXTENSION, "path": path, "reason": "restates devkit_core.core.memo"}])
    result = inspect(repo)
    assert result["checks"]["scope_extensions"] == {"status": "pass"}
    assert result["exit_code"] == 0


def test_explicit_scope_and_scope_file_do_not_union_extensions(repo: Path, monkeypatch) -> None:
    worker(repo, 1, [EXTENSION])
    result = inspect(repo, scope=[UNIT, "src/feature/code.py"])
    assert result["checks"]["scope_extensions"]["status"] == "pass"
    assert result["outside_scope"] == [PATH]
    assert result["errors"][0]["code"] == "SPEC_WORKER_SCOPE_OUTSIDE"
    # The CLI injects the module runner through its adapter.
    import importlib

    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    monkeypatch.setattr(module, "InspectWorkerUseCase", lambda: SimpleNamespace(execute=inspect))
    source = repo.parent / "scope.txt"
    source.write_text(f"{UNIT}\nsrc/feature/code.py\n")
    result = CliRunner().invoke(
        cli, ["worker", "inspect", "-w", str(repo), "--scope-file", str(source), "--format", "json"]
    )
    assert result.exit_code == 1, result.output


@pytest.mark.parametrize("reason", ["", "nested (why)"])
def test_malformed_annotation_is_not_run(repo: Path, reason: str) -> None:
    tasks(repo, reason=reason)
    worker(repo, 1)
    result = inspect(repo)
    assert result["checks"]["scope_extensions"]["status"] == "not-run"
    assert result["checks"]["scope_extensions"]["cause"]["code"] == "SPEC_WORKER_SCOPE_UNRESOLVED"


def test_invalid_record_is_not_run_and_empty_compatibility_passes(repo: Path) -> None:
    tasks(repo, annotation=False)
    worker(repo, 1, [{**EXTENSION, "task": 0}])
    assert inspect(repo)["checks"]["scope_extensions"]["status"] == "not-run"


def test_non_file_annotation_is_not_run(repo: Path) -> None:
    tasks(repo, path="src/feature/")
    worker(repo, 1, [EXTENSION])
    assert inspect(repo)["checks"]["scope_extensions"]["status"] == "not-run"


def test_blocked_cumulative_range_retains_earlier_extension_records(repo: Path) -> None:
    worker(repo, 1, [EXTENSION], problem=True)
    worker(repo, 2)
    result = inspect(repo)
    assert result["base"] == git(repo, "rev-parse", "main")
    assert result["checks"]["scope_extensions"]["status"] == "pass"
    assert result["scope_extensions"][0]["source"] == "worker-01.yaml"
    assert result["checks"]["envelopes"]["status"] == "fail"
    write(
        repo,
        f"{UNIT}/envelopes/resolution-01.yaml",
        "kind: resolution\nstatus: completed\nsummary: fixture fixed\nresolves: worker-01.yaml\n",
    )
    worker(repo, 3)
    assert inspect(repo)["checks"]["scope_extensions"]["status"] == "pass"


def test_task_move_requires_current_matching_record(repo: Path) -> None:
    worker(repo, 1, [EXTENSION])
    text = (repo / UNIT / "tasks.md").read_text()
    write(repo, f"{UNIT}/tasks.md", "- [x] Other task\n" + text)
    worker(repo, 2)
    assert inspect(repo)["checks"]["scope_extensions"]["status"] == "fail"
    worker(repo, 3, [{**EXTENSION, "task": 2}])
    assert inspect(repo)["checks"]["scope_extensions"]["status"] == "pass"
