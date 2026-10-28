"""Worker inspection uses committed records and never mutates the repository."""

from __future__ import annotations

import importlib
import json
import subprocess
from collections.abc import Sequence
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit_agt.features.rules import RuleContext, evaluate_rules, git_snapshot

from devkit_spec.base.errors import WorkerBaseUnresolvedError, WorkerHeadUnresolvedError, WorkerUnitUnresolvedError
from devkit_spec.cli import cli
from devkit_spec.features.governance.usecases.reconcile_contract import ReconcileContractRule
from devkit_spec.features.worker.usecases.inspect import InspectWorkerUseCase

UNIT = "specs/2026-10/20261020-example"


inspect = InspectWorkerUseCase().execute


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
    assert result["rules_base"] == result["base"]
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
    with pytest.raises(WorkerBaseUnresolvedError):
        inspect(repo, runner=passed)


def test_override_scope_is_replacement_and_component_prefix(repo: Path) -> None:
    write(repo, "src-extra/file", "outside")
    worker(repo, 1)
    result = inspect(repo, scope=["src"], runner=passed)
    assert "src-extra/file" in result["outside_scope"]
    assert "src/code.py" not in result["outside_scope"]
    assert all(e["source"] == "argument" for e in result["scope"])


@pytest.mark.parametrize("outside", [False, True])
def test_absent_optional_reconcile_still_audits_scope(repo: Path, outside: bool) -> None:
    (repo / UNIT / "reconcile.md").unlink()
    if outside:
        write(repo, "unrelated/file", "outside")
    worker(repo, 1)
    result = inspect(repo, runner=passed)
    assert result["checks"]["scope"]["status"] == ("fail" if outside else "pass")
    assert result["outside_scope"] == (["unrelated/file"] if outside else [])
    assert {e["source"] for e in result["scope"]} == {"unit", "boundary", "materials"}
    assert result["exit_code"] == int(outside)


@pytest.mark.parametrize("invalid", ["reconcile.md", "tasks.md"])
def test_invalid_present_or_missing_required_scope_record_is_not_run(repo: Path, invalid: str) -> None:
    path = repo / UNIT / invalid
    if invalid == "tasks.md":
        path.unlink()
    else:
        path.write_text("---\ntargets: invalid\n---\n")
    worker(repo, 1)
    result = inspect(repo, runner=passed)
    assert result["checks"]["scope"]["status"] == "not-run"
    assert "outside_scope" not in result
    assert result["checks"]["rules"]["status"] == "pass"
    assert result["notices"][0]["code"] == "SPEC_WORKER_CHECK_NOT_RUN"


def test_rules_keep_earlier_turn_target_in_cumulative_comparison(repo: Path) -> None:
    write(repo, "docs/contract.md", "created in first turn")
    record = "---\nreconcile_id: REC-example\nstatus: pending\ntargets:\n  - file: docs/contract.md\n    resolution: modified\n---\n"
    write(repo, f"{UNIT}/reconcile.md", record)
    previous = worker(repo, 1)
    write(repo, f"{UNIT}/reconcile.md", record.replace("pending", "resolved"))
    write(repo, "src/code.py", "changed in second turn")
    returned = worker(repo, 2)
    calls = []

    def cumulative_check(root: Path, args: Sequence[str]) -> dict:
        calls.append(list(args))
        if args[0] == "rules":
            snapshot = git_snapshot(root, staged=False, base=args[-1])
            ctx = RuleContext(workspace_root=root, changed_files=list(snapshot.changed), snapshot=snapshot)
            checked = evaluate_rules(ctx, [ReconcileContractRule()])
            assert checked.errors == []
            return {"status": "fail" if checked.violations else "pass"}
        return passed(root, args)

    result = inspect(repo, runner=cumulative_check)
    assert result["base"] == previous
    assert result["head"] == returned
    assert "docs/contract.md" not in result["changed_paths"]
    assert result["checks"]["rules"]["status"] == "pass"
    assert result["rules_base"] == git(repo, "rev-parse", "main")
    assert result["inputs"]["rules_base"] == {"value": result["rules_base"], "source": "branch-merge-base"}
    assert calls[0][-1] == result["rules_base"]
    assert result["checks"]["rules"]["status"] == "pass"
    # Reproduce the original governance failure without changing the write audit.
    scoped = inspect(repo, rules_base=previous, runner=cumulative_check)
    assert scoped["checks"]["rules"]["status"] == "fail"
    assert scoped["base"] == result["base"]
    assert scoped["changed_paths"] == result["changed_paths"]


def test_rules_base_override_and_manual_fallback(repo: Path) -> None:
    previous = worker(repo, 1)
    worker(repo, 2)
    result = inspect(repo, rules_base=previous, runner=passed)
    assert result["rules_base"] == previous
    assert result["inputs"]["rules_base"]["source"] == "argument"
    git(repo, "config", "--unset", "branch.dev-example.devkitBase")
    result = inspect(repo, base="main", runner=passed)
    assert result["rules_base"] == result["base"]
    assert result["inputs"]["rules_base"]["source"] == "audit-base-fallback"
    git(repo, "config", "branch.dev-example.devkitBase", "missing-recorded-branch")
    with pytest.raises(WorkerBaseUnresolvedError):
        inspect(repo, base="main", runner=passed)


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
    with pytest.raises(WorkerHeadUnresolvedError):
        inspect(repo, runner=passed)
    worker(repo, 1)
    git(repo, "checkout", "--detach", "-q")
    with pytest.raises(WorkerUnitUnresolvedError):
        inspect(repo, runner=passed)
    assert inspect(repo, unit=UNIT, base="main", head="HEAD", runner=passed)["head"] == git(repo, "rev-parse", "HEAD")


@pytest.mark.parametrize(
    ("source", "identifier"),
    [
        ("specs/earlier/feedback/observation.md", "FB-observation"),
        ("specs/2026-10/feedback/20261028-observation.md", "FB-observation"),
        ("specs/earlier/feedback/20261028-observation.md", "FB-20261028-observation"),
    ],
)
def test_feedback_and_marker(repo: Path, source: str, identifier: str) -> None:
    write(repo, f"{UNIT}/spec.md", (repo / UNIT / "spec.md").read_text() + f"\n## Source feedback\n`{identifier}`\n")
    write(repo, source, f"---\nid: {identifier}\nstatus: open\n---\n")
    write(repo, "specs/earlier/feedback/unrelated.md", "---\ninvalid: [\n")
    git(repo, "config", "branch.dev-example.devkitUnit", UNIT)
    worker(repo, 1)
    result = inspect(repo, runner=passed)
    assert result["inputs"]["unit"]["source"] == "branch.devkitUnit"
    assert {
        "path": source,
        "source": "source-feedback",
        "id": identifier,
    } in result["scope"]


def test_empty_reconcile_target_and_not_applicable_boundary_are_skipped(repo: Path) -> None:
    write(repo, f"{UNIT}/tasks.md", "- [x] implement\n  - _Boundary: `src/`\n- [x] review\n  - _Boundary: N/A\n")
    write(repo, f"{UNIT}/reconcile.md", '---\ntargets:\n  - file: ""\n    resolution: waived\n---\n')
    worker(repo, 1)
    result = inspect(repo, runner=passed)
    assert result["checks"]["scope"] == {"status": "pass"}
    assert {e["source"] for e in result["scope"]} == {"unit", "boundary", "materials"}


@pytest.mark.parametrize(
    "source", ["specs/earlier/feedback/observation.md", "specs/2026-10/feedback/20261028-observation.md"]
)
@pytest.mark.parametrize("status", ["promoted", "resolved", "dismissed", "forwarded", "unknown", None])
def test_terminal_source_edits_need_explicit_boundary(repo: Path, source: str, status: str | None) -> None:
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


def test_dated_and_undated_sources_with_the_same_id_are_ambiguous(repo: Path) -> None:
    write(repo, f"{UNIT}/spec.md", (repo / UNIT / "spec.md").read_text() + "\n## Source feedback\n`FB-observation`\n")
    for source in ("specs/earlier/feedback/observation.md", "specs/2026-10/feedback/20261028-observation.md"):
        write(repo, source, "---\nid: FB-observation\nstatus: open\n---\n")
    worker(repo, 1)
    result = inspect(repo, runner=passed)
    assert result["checks"]["scope"]["status"] == "not-run"
    assert result["checks"]["scope"]["cause"]["code"] == "SPEC_WORKER_SCOPE_UNRESOLVED"


def test_a_dated_filename_does_not_override_the_frontmatter_id(repo: Path) -> None:
    write(repo, f"{UNIT}/spec.md", (repo / UNIT / "spec.md").read_text() + "\n## Source feedback\n`FB-observation`\n")
    write(repo, "specs/2026-10/feedback/20261028-observation.md", "---\nid: FB-another\nstatus: open\n---\n")
    worker(repo, 1)
    result = inspect(repo, runner=passed)
    assert result["checks"]["scope"]["status"] == "not-run"
    assert result["checks"]["scope"]["cause"]["code"] == "SPEC_WORKER_SCOPE_UNRESOLVED"


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
    monkeypatch.setattr(
        module,
        "InspectWorkerUseCase",
        lambda: SimpleNamespace(execute=lambda root, **kw: inspect(root, **kw, runner=passed)),
    )
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
    monkeypatch.setattr(
        module,
        "InspectWorkerUseCase",
        lambda: SimpleNamespace(execute=lambda root, **kw: inspect(root, **kw, runner=passed)),
    )
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
    with pytest.raises(WorkerBaseUnresolvedError):
        inspect(repo, runner=passed)


def test_ambiguous_unit_and_readded_worker(repo: Path) -> None:
    write(repo, "specs/2026-09/20260920-example/spec.md", "---\nworkflow: sdd-spec-feature\n---\n")
    worker(repo, 1)
    with pytest.raises(WorkerUnitUnresolvedError):
        inspect(repo, runner=passed)
    path = repo / UNIT / "envelopes/worker-01.yaml"
    text = path.read_text()
    path.unlink()
    commit(repo)
    path.write_text(text)
    commit(repo)
    with pytest.raises(WorkerHeadUnresolvedError):
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
    monkeypatch.setattr(
        module,
        "InspectWorkerUseCase",
        lambda: SimpleNamespace(execute=lambda root, **kw: inspect(root, **kw, runner=passed)),
    )
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
    assert json.loads(result.stdout)["notices"][0]["code"] == "SPEC_WORKER_CHECK_NOT_RUN"
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
    write(repo, f"{UNIT}/reconcile.md", "---\ntargets: invalid\n---\n")
    worker(repo, 1)
    monkeypatch.chdir(repo)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    monkeypatch.setattr(
        module,
        "InspectWorkerUseCase",
        lambda: SimpleNamespace(execute=lambda root, **kw: inspect(root, **kw, runner=passed)),
    )
    result = CliRunner().invoke(cli, ["worker", "inspect"])
    assert result.exit_code == 0, result.output
    assert "[CHANGED:" in result.stdout
    assert "outside=" not in result.stdout
    assert "fixture" not in result.stdout
    assert "envelopes':" not in result.stdout
    assert "SPEC_WORKER_CHECK_NOT_RUN" in result.stderr


def test_structured_advisories_use_stderr_once(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_core.base.errors import ArgumentError

    worker(repo, 1)
    monkeypatch.chdir(repo)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    error = ArgumentError("wrapped input invalid", fix="Pass the valid input").to_dict()

    def runner(_root: Path, _args: object) -> dict:
        return {"status": "not-run", "result": {"errors": [error]}, "stderr": ""}

    monkeypatch.setattr(
        module,
        "InspectWorkerUseCase",
        lambda: SimpleNamespace(execute=lambda root, **kw: inspect(root, **kw, runner=runner)),
    )
    result = CliRunner().invoke(cli, ["worker", "inspect"])
    assert result.exit_code == 0, result.output
    assert "ARGUMENT_INVALID" not in result.stdout
    assert result.stderr.count("(ARGUMENT_INVALID)") == 1
    assert "[ACTION]" in result.stderr and "[FIX]" in result.stderr
    assert "Pass the valid input" in result.stderr


def test_cli_failed_checks_carry_advisories_workspace_and_compact_success(
    repo: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    previous = worker(repo, 1)
    write(repo, "outside.py", "x = 1\n")
    git(repo, "add", "outside.py")
    worker(repo, 2)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    monkeypatch.setattr(
        module,
        "InspectWorkerUseCase",
        lambda: SimpleNamespace(execute=lambda root, **kw: inspect(root, **kw, runner=passed)),
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)  # -w names the worktree; the cwd is not used
    runner = CliRunner()
    result = runner.invoke(cli, ["worker", "inspect", "--base", previous, "-w", str(repo)])
    assert result.exit_code == 1, result.output
    assert result.stdout.startswith(f"[WORKER_INSPECTION: verdict=fail base={previous} head=")
    assert "(SPEC_WORKER_SCOPE_OUTSIDE)" in result.stderr and "[TARGET] outside.py" in result.stderr
    data = json.loads(
        runner.invoke(cli, ["worker", "inspect", "--base", previous, "-w", str(repo), "--format", "json"]).stdout
    )
    assert [error["code"] for error in data["errors"]] == ["SPEC_WORKER_SCOPE_OUTSIDE"]
    # A passed check is its status: its wrapped body is left out without --details.
    assert "result" not in data["checks"]["envelopes"] and "result" not in data["checks"]["workflow"]
    head = git(repo, "rev-parse", "HEAD")
    clean = runner.invoke(cli, ["worker", "inspect", "--strict", "--base", head, "-w", str(repo), "--format", "json"])
    assert clean.exit_code == 0, clean.output


def test_rules_base_cli_evidence_and_invalid_ref(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    previous = worker(repo, 1)
    worker(repo, 2)
    monkeypatch.chdir(repo)
    module = importlib.import_module("devkit_spec.features.worker.cli.commands")
    monkeypatch.setattr(
        module,
        "InspectWorkerUseCase",
        lambda: SimpleNamespace(execute=lambda root, **kw: inspect(root, **kw, runner=passed)),
    )
    runner = CliRunner()
    args = ["worker", "inspect", "--rules-base", previous]
    compact = runner.invoke(cli, [*args, "--format", "json"])
    full = runner.invoke(cli, [*args, "--details", "--format", "json"])
    text = runner.invoke(cli, args)
    assert compact.exit_code == full.exit_code == text.exit_code == 0
    a, b = json.loads(compact.stdout), json.loads(full.stdout)
    assert a["rules_base"] == b["rules_base"] == previous
    assert a["inputs"]["rules_base"] == b["inputs"]["rules_base"] == {"value": previous, "source": "argument"}
    assert f"[INPUT: rules_base value={previous} source=argument]" in text.stdout
    invalid = runner.invoke(cli, ["worker", "inspect", "--rules-base", "unknown-rules-ref", "--format", "json"])
    assert invalid.exit_code == 2
    assert json.loads(invalid.stdout)["error"]["code"] == "ARGUMENT_INVALID"
