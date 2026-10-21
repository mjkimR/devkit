"""Worker inspection uses committed records and never mutates the repository."""

from __future__ import annotations

import importlib
import json
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest
from click.testing import CliRunner

from devkit_spec.cli import cli
from devkit_spec.features.worker.usecases.inputs import BaseUnresolved, HeadUnresolved, UnitUnresolved
from devkit_spec.features.worker.usecases.inspect import inspect

UNIT = "specs/2026-10/20261020-example"


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


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-qb", "main")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.invalid")
    write(root, "seed", "initial")
    commit(root)
    git(root, "checkout", "-qb", "dev-example")
    git(root, "config", "branch.dev-example.devkitBase", "main")
    write(root, f"{UNIT}/spec.md", "---\nid: SPEC-example\nworkflow: sdd-spec-feature\n---\n")
    write(root, f"{UNIT}/tasks.md", "- [x] implement\n  - **_Boundary**: `src/`\n")
    write(root, f"{UNIT}/reconcile.md", "---\ntargets:\n  - file: docs/contract.md\n    resolution: modified\n---\n")
    write(root, "src/code.py", "pass\n")
    commit(root)
    return root


def worker(root: Path, number: int, *, problem_base: str | None = None) -> str:
    problem = ""
    if problem_base is not None:
        problem = (
            f"diff_scope:\n  base: {problem_base}\nproblem:\n  cause: failed\n  attempts: [check]\n  recovery: fix\n"
        )
    write(
        root,
        f"{UNIT}/envelopes/worker-{number:02}.yaml",
        f"kind: worker\nstatus: {'failed' if problem else 'completed'}\nstage: build-verify\nsummary: fixture\n{problem}",
    )
    return commit(root)


def passed(_root: Path, _args: object) -> dict:
    return {"status": "pass", "result": {"stage": "build-verify"}}


def test_first_turn_derives_range_scope_and_preserves_state(repo: Path) -> None:
    returned = worker(repo, 1)
    before = git(repo, "status", "--porcelain")
    result = inspect(repo, runner=passed)
    assert result["base"] == git(repo, "rev-parse", "main")
    assert result["head"] == returned
    assert result["inputs"]["unit"]["source"] == "activity-branch"
    assert result["outside_scope"] == []
    assert result["checks"]["envelopes"]["status"] == "pass"
    assert result["exit_code"] == 0
    assert git(repo, "status", "--porcelain") == before
    assert {e["source"] for e in result["scope"]} == {"unit", "boundary", "materials", "reconcile"}


def test_previous_result_and_dirty_documents(repo: Path) -> None:
    previous = worker(repo, 1)
    returned = worker(repo, 2)
    write(repo, f"{UNIT}/tasks.md", "- [ ] changed\n  - **_Boundary**: other/\n")
    write(repo, f"{UNIT}/envelopes/worker-03.yaml", "malformed")
    result = inspect(repo, runner=passed)
    assert result["base"] == previous
    assert result["head"] == returned
    assert "src" in [e["path"] for e in result["scope"]]
    assert result["checks"]["worktree"]["status"] == "fail"
    assert result["checks"]["envelopes"]["status"] == "pass"


def test_blocked_previous_range_and_resolution(repo: Path) -> None:
    initial = git(repo, "rev-parse", "main")
    worker(repo, 1, problem_base=initial)
    worker(repo, 2)
    result = inspect(repo, runner=passed)
    assert result["base"] == initial
    assert result["checks"]["envelopes"]["result"]["blocked"]
    assert result["exit_code"] == 1
    write(
        repo,
        f"{UNIT}/envelopes/resolution-01.yaml",
        "kind: resolution\nstatus: completed\nresolves: worker-01.yaml\nsummary: fixed\n",
    )
    previous = worker(repo, 3)
    worker(repo, 4)
    assert inspect(repo, runner=passed)["base"] == previous


def test_conflicting_problem_bases(repo: Path) -> None:
    worker(repo, 1, problem_base=git(repo, "rev-parse", "main"))
    worker(repo, 2, problem_base=git(repo, "rev-parse", "HEAD"))
    worker(repo, 3)
    with pytest.raises(BaseUnresolved):
        inspect(repo, runner=passed)


def test_override_scope_is_replacement_and_component_prefix(repo: Path) -> None:
    write(repo, "src-extra/file", "outside")
    worker(repo, 1)
    result = inspect(repo, scope=["src"], runner=passed)
    assert "src-extra/file" in result["outside_scope"]
    assert "src/code.py" not in result["outside_scope"]
    assert all(e["source"] == "argument" for e in result["scope"])


def test_missing_scope_input_does_not_stop_other_checks(repo: Path) -> None:
    (repo / UNIT / "reconcile.md").unlink()
    worker(repo, 1)
    result = inspect(repo, runner=passed)
    assert result["checks"]["scope"]["status"] == "not-run"
    assert "outside_scope" not in result
    assert result["checks"]["rules"]["status"] == "pass"
    assert result["exit_code"] == 0
    assert result["notices"][0]["code"] == "WORKER_CHECK_NOT_RUN"


def test_head_mismatch_skips_rules(repo: Path) -> None:
    returned = worker(repo, 1)
    write(repo, "src/later", "later")
    commit(repo)
    calls = []

    def runner(_root: Path, args: object) -> dict:
        calls.append(args)
        return passed(_root, args)

    result = inspect(repo, runner=runner)
    assert result["head"] == returned
    assert result["checks"]["head"]["status"] == "fail"
    assert result["checks"]["rules"]["status"] == "not-run"
    assert len(calls) == 1


def test_required_inputs(repo: Path) -> None:
    with pytest.raises(HeadUnresolved):
        inspect(repo, runner=passed)
    worker(repo, 1)
    git(repo, "checkout", "--detach", "-q")
    with pytest.raises(UnitUnresolved):
        inspect(repo, runner=passed)
    assert inspect(repo, unit=UNIT, base="main", head="HEAD", runner=passed)["head"] == git(repo, "rev-parse", "HEAD")


def test_feedback_and_marker(repo: Path) -> None:
    write(repo, f"{UNIT}/spec.md", (repo / UNIT / "spec.md").read_text() + "\n## Source feedback\n`FB-observation`\n")
    write(repo, "specs/earlier/feedback/observation.md", "---\nid: FB-observation\nstatus: open\n---\n")
    git(repo, "config", "branch.dev-example.devkitUnit", UNIT)
    worker(repo, 1)
    result = inspect(repo, runner=passed)
    assert result["inputs"]["unit"]["source"] == "branch.devkitUnit"
    assert {
        "path": "specs/earlier/feedback/observation.md",
        "source": "source-feedback",
        "id": "FB-observation",
    } in result["scope"]


@pytest.mark.parametrize("status", ["promoted", "resolved", "dismissed", "forwarded", "unknown", None])
def test_terminal_source_edits_need_explicit_boundary(repo: Path, status: str | None) -> None:
    source = "specs/earlier/feedback/observation.md"
    write(repo, f"{UNIT}/spec.md", (repo / UNIT / "spec.md").read_text() + "\n## Source feedback\n`FB-observation`\n")
    metadata = f"status: {status}\n" if status is not None else ""
    write(repo, source, f"---\nid: FB-observation\n{metadata}---\n")
    previous = worker(repo, 1)
    write(repo, source, (repo / source).read_text() + "\nA later edit.\n")
    worker(repo, 2)
    result = inspect(repo, base=previous, runner=passed)
    assert source in result["outside_scope"]
    assert not any(entry["source"] == "source-feedback" for entry in result["scope"])

    write(
        repo,
        f"{UNIT}/tasks.md",
        (repo / UNIT / "tasks.md").read_text() + f"\n- [x] Explicit edit\n  - **_Boundary**: `{source}`\n",
    )
    worker(repo, 3)
    result = inspect(repo, base=previous, runner=passed)
    assert source not in result["outside_scope"]
    assert any(entry["path"] == source and entry["source"] == "boundary" for entry in result["scope"])


def test_rename_reports_old_and_new_names(repo: Path) -> None:
    previous = worker(repo, 1)
    git(repo, "mv", "src/code.py", "outside.py")
    worker(repo, 2)
    result = inspect(repo, base=previous, runner=passed)
    assert {"src/code.py", "outside.py"} <= set(result["changed_paths"])
    assert result["outside_scope"] == ["outside.py"]


def test_cli_json_and_mutually_exclusive_scope(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    worker(repo, 1)
    monkeypatch.chdir(repo)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    monkeypatch.setattr(module, "inspect", lambda root, **kw: inspect(root, **kw, runner=passed))
    runner = CliRunner()
    result = runner.invoke(cli, ["worker", "inspect", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["checks"]["scope"]["status"] == "pass"
    result = runner.invoke(cli, ["worker", "inspect", "--scope", "src", "--scope-file", "scope"])
    assert result.exit_code == 2
    result = runner.invoke(cli, ["worker", "inspect"])
    assert result.exit_code == 0
    assert "[WORKER_INSPECTION:" in result.stdout
    assert "[INPUT: unit" in result.stdout


def test_cli_summary_keeps_current_findings_and_failures_details_restore_history(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(
        repo,
        f"{UNIT}/envelopes/review-01.yaml",
        "kind: review\nstatus: completed\nsummary: old history\nfindings:\n  - issue: old\n    evidence: historical\n",
    )
    write(
        repo,
        f"{UNIT}/envelopes/review-02.yaml",
        "kind: review\nstatus: completed\nsummary: latest review\nfindings:\n  - issue: current defect\n    evidence: source.py:3\n    suggested_action: fix it\n",
    )
    worker(repo, 1, problem_base=git(repo, "rev-parse", "main"))
    monkeypatch.chdir(repo)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    monkeypatch.setattr(module, "inspect", lambda root, **kw: inspect(root, **kw, runner=passed))
    runner = CliRunner()
    compact = runner.invoke(cli, ["worker", "inspect", "--format", "json"])
    detailed = runner.invoke(cli, ["worker", "inspect", "--format", "json", "--details"])
    assert compact.exit_code == detailed.exit_code == 1
    summary, full = json.loads(compact.stdout), json.loads(detailed.stdout)
    envelopes = summary["checks"]["envelopes"]["result"]
    entries = {e["file"]: e for e in envelopes["envelopes"]}
    assert "findings" not in entries["envelopes/review-01.yaml"]
    assert entries["envelopes/review-02.yaml"]["findings"][0]["suggested_action"] == "fix it"
    assert envelopes["problems"][0]["recovery"] == "fix"
    assert "summary" not in entries["envelopes/worker-01.yaml"]
    assert full["checks"]["envelopes"]["result"]["envelopes"][0]["summary"] == "old history"
    assert "result" not in summary["checks"]["rules"]
    assert "result" in full["checks"]["rules"]
    assert summary["inputs"] == full["inputs"] and summary["head"] == full["head"]


def test_linked_worktree_observes_base_without_checking_it(repo: Path) -> None:
    worker(repo, 1)
    git(repo, "checkout", "-q", "main")
    linked = repo.parent / "linked"
    git(repo, "worktree", "add", "-q", str(linked), "dev-example")
    write(repo, "untracked", "base dirt")
    result = inspect(linked, runner=passed)
    assert result["base_checkout"]["dirty_paths"] == ["untracked"]
    assert result["inputs"]["base_checkout"]["value"] == str(repo)
    assert result["exit_code"] == 0


def test_missing_problem_base_is_unresolved(repo: Path) -> None:
    worker(repo, 1, problem_base="")
    worker(repo, 2)
    with pytest.raises(BaseUnresolved):
        inspect(repo, runner=passed)


def test_ambiguous_unit_and_readded_worker(repo: Path) -> None:
    write(repo, "specs/2026-09/20260920-example/spec.md", "---\nworkflow: sdd-spec-feature\n---\n")
    worker(repo, 1)
    with pytest.raises(UnitUnresolved):
        inspect(repo, runner=passed)
    path = repo / UNIT / "envelopes/worker-01.yaml"
    text = path.read_text()
    path.unlink()
    commit(repo)
    path.write_text(text)
    commit(repo)
    with pytest.raises(HeadUnresolved):
        inspect(repo, unit=UNIT, runner=passed)


def test_malformed_envelope_is_failed_check(repo: Path) -> None:
    worker(repo, 1)
    write(repo, f"{UNIT}/envelopes/review-01.yaml", "not: [yaml")
    returned = commit(repo)
    result = inspect(repo, head=returned, runner=passed)
    assert result["checks"]["envelopes"]["status"] == "fail"
    assert result["checks"]["envelopes"]["result"]["errors"][0]["code"] == "ENVELOPE_INVALID"


def test_planning_scope_is_only_proposal(repo: Path) -> None:
    git(repo, "checkout", "-qb", "plan-example")
    git(repo, "config", "branch.plan-example.devkitBase", "main")
    proposal = "docs/proposals/PROP-example"
    write(repo, f"{proposal}/proposal.md", "---\nworkflow: sdd-proposal\nstatus: draft\n---\n")
    write(repo, f"{proposal}/envelopes/worker-01.yaml", "kind: worker\nstage: plan\nstatus: completed\n")
    returned = commit(repo)
    result = inspect(repo, base=returned, runner=passed)
    assert result["scope"] == [{"path": proposal, "source": "unit"}]


def test_scope_file_unknown_ref_and_notice_cli(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    worker(repo, 1)
    monkeypatch.chdir(repo)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    monkeypatch.setattr(module, "inspect", lambda root, **kw: inspect(root, **kw, runner=passed))
    runner = CliRunner()
    write(repo, "scope.txt", "src\n")
    result = runner.invoke(cli, ["worker", "inspect", "--scope-file", "scope.txt", "--format", "json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)["scope"] == [{"path": "src", "source": "argument"}]
    result = runner.invoke(cli, ["worker", "inspect", "--head", "unknown-ref", "--format", "json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["code"] == "ARGUMENT_INVALID"
    result = runner.invoke(cli, ["worker", "inspect", "--head", "main", "--format", "json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)["notices"][0]["code"] == "WORKER_CHECK_NOT_RUN"
    assert json.loads(result.stdout)["checks"]["rules"]["status"] == "not-run"


def test_wrapped_checks_preserve_output_and_failures(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("devkit_spec.features.worker.usecases.inspect")
    for code, expected in [(0, "pass"), (1, "fail"), (2, "not-run")]:
        monkeypatch.setattr(
            module.subprocess,
            "run",
            lambda *a, code=code, **kw: subprocess.CompletedProcess(
                a, code, '{"errors": [{"code": "EXISTING"}]}', "[ERROR] (EXISTING)\n[ACTION] correct it\n"
            ),
        )
        result = module.run_check(repo, ["workflow", "next"])
        assert result["status"] == expected
        assert result["result"]["errors"][0]["code"] == "EXISTING"
        assert "[ACTION]" in result["stderr"]


def test_pending_questions_are_failed_check(repo: Path) -> None:
    worker(repo, 1)
    path = repo / UNIT / "envelopes/worker-01.yaml"
    path.write_text(
        path.read_text().replace("status: completed", "status: needs_input")
        + "questions:\n  - id: choice\n    title: Choice\n    prompt: Choose behavior\n    context: Contract choice\n    options:\n      - id: first\n        description: First\n        recommended: true\n      - id: second\n        description: Second\n"
    )
    head = commit(repo)
    result = inspect(repo, head=head, runner=passed)
    assert result["checks"]["envelopes"]["status"] == "fail"

    assert result["checks"]["envelopes"]["result"]["pending_questions"]
    assert not result["checks"]["envelopes"]["result"]["errors"]


def test_non_envelope_files_are_ignored_at_current_and_previous_commits(repo: Path) -> None:
    for name in ["README.md", ".gitkeep", ".worker-02.yaml.abcdef123456.tmp"]:
        write(repo, f"{UNIT}/envelopes/{name}", "not an envelope")
    previous = worker(repo, 1)
    worker(repo, 2)
    result = inspect(repo, runner=passed)
    assert result["base"] == previous
    assert result["checks"]["envelopes"]["status"] == "pass"
    assert len(result["checks"]["envelopes"]["result"]["envelopes"]) == 2


def test_dirty_record_never_reaches_disk_workflow_runner(repo: Path) -> None:
    worker(repo, 1)
    write(repo, f"{UNIT}/envelopes/worker-02.yaml", "kind: worker\nstatus: failed\n")
    calls = []

    def runner(root: Path, args: Sequence[str]) -> dict:
        calls.append(args)
        return passed(root, args)

    result = inspect(repo, runner=runner)
    assert result["checks"]["workflow"]["status"] == "not-run"
    assert all(args[0] != "workflow" for args in calls)
    assert result["checks"]["envelopes"]["status"] == "pass"


def test_text_scope_unknown_omits_outside_and_history(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / UNIT / "reconcile.md").unlink()
    worker(repo, 1)
    monkeypatch.chdir(repo)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    monkeypatch.setattr(module, "inspect", lambda root, **kw: inspect(root, **kw, runner=passed))
    result = CliRunner().invoke(cli, ["worker", "inspect"])
    assert result.exit_code == 0, result.output
    assert "[CHANGED:" in result.stdout
    assert "outside=" not in result.stdout
    assert "fixture" not in result.stdout
    assert "envelopes':" not in result.stdout
    assert "WORKER_CHECK_NOT_RUN" in result.stderr


def test_structured_advisories_use_stderr_once(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_core.base.errors import ArgumentError

    worker(repo, 1)
    monkeypatch.chdir(repo)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    error = ArgumentError("wrapped input invalid", fix="Pass the valid input").to_dict()

    def runner(_root: Path, _args: object) -> dict:
        return {"status": "not-run", "result": {"errors": [error]}, "stderr": ""}

    monkeypatch.setattr(module, "inspect", lambda root, **kw: inspect(root, **kw, runner=runner))
    result = CliRunner().invoke(cli, ["worker", "inspect"])
    assert result.exit_code == 0, result.output
    assert "ARGUMENT_INVALID" not in result.stdout
    assert result.stderr.count("(ARGUMENT_INVALID)") == 1
    assert "[ACTION]" in result.stderr and "[FIX]" in result.stderr
    assert "Pass the valid input" in result.stderr
