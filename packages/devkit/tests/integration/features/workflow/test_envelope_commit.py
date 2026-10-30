"""Explicit single-record commits against real Git, hooks, index and workflow evaluation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from devkit_agt.features.workflow.models.errors import WorkflowError
from devkit_agt.features.workflow.usecases.commit_envelope import CommitEnvelopeUseCase
from devkit_agt.features.workflow.usecases.workspace import Workspace
from devkit_core.core import run_git
from testsupport.workflow import run_cli, simple_workspace

UNIT = ".devkit/transient/work/u"
FILE = "envelopes/review-01.yaml"


def git(root: Path, *args: str) -> str:
    return run_git(root, *args).decode().strip()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for name in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        monkeypatch.delenv(name, raising=False)
    simple_workspace(tmp_path)
    unit = tmp_path / UNIT
    unit.mkdir(parents=True)
    (unit / "task.md").write_text("---\nid: SPEC-example\nworkflow: w\nstatus: planned\n---\n# Example\n")
    git(tmp_path, "init", "-b", "different-branch-name")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "commit.gpgsign", "false")
    git(tmp_path, "config", "core.hooksPath", str(tmp_path / ".git/hooks"))
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "initial")
    (unit / "envelopes").mkdir()
    (unit / FILE).write_text(
        "kind: review\nstatus: completed\nsummary: Authored review\nstage: s\nworkflow: w\nsegment: 0\n"
    )
    return tmp_path


def commit(root: Path, file: str = FILE) -> dict[str, object]:
    return CommitEnvelopeUseCase().execute(Workspace(root, lint=None), UNIT, file)


def refusal(root: Path, code: str, file: str = FILE) -> WorkflowError:
    before = git(root, "rev-parse", "HEAD")
    index = git(root, "ls-files", "--stage")
    with pytest.raises(WorkflowError) as caught:
        commit(root, file)
    assert caught.value.code == code
    assert git(root, "rev-parse", "HEAD") == before
    assert git(root, "ls-files", "--stage") == index
    return caught.value


def hook(root: Path, name: str, script: str) -> Path:
    p = root / ".git/hooks" / name
    p.write_text("#!/bin/sh\n" + script + "\n")
    p.chmod(0o755)
    return p


def test_exact_commit_idempotence_and_evidence(repo: Path) -> None:
    record = repo / UNIT / FILE
    before = git(repo, "rev-parse", "HEAD")
    record.write_text(record.read_text() + f"diff_scope: {{base: '{before}', head: '{before}'}}\n")
    original = record.read_bytes()
    result = commit(repo)
    assert result["outcome"] == "committed"
    assert result["head"] == git(repo, "rev-parse", "HEAD")
    assert result["subject"] == "chore(workflow): record example review-01"
    assert git(repo, "show", "-s", "--format=%B") == f"{result['subject']}\n\nworkflow: w\nsegment: 0\nstage: s"
    assert git(repo, "diff", "--name-status", before) == f"A\t{UNIT}/{FILE}"
    assert git(repo, "rev-parse", "HEAD^") == before
    assert not git(repo, "status", "--porcelain")
    assert record.read_bytes() == original
    repeated = commit(repo)
    assert repeated == {**result, "outcome": "already_committed", "subject": None}
    # A record commit does not rewrite the evidence head or disturb ordinary readiness.
    assert (
        Workspace(repo, lint=None).evaluate_unit(Workspace(repo, lint=None).resolve_unit(UNIT), lint=False).unit == UNIT
    )


@pytest.mark.parametrize("dirty", ["untracked", "unstaged", "staged"])
def test_unrelated_changes_refuse_without_staging(repo: Path, dirty: str) -> None:
    path = repo / ("other" if dirty == "untracked" else ".devkit/workflows/w.md")
    path.write_text(path.read_text() + "\n" if path.exists() else "new")
    if dirty == "staged":
        git(repo, "add", ".")
    refusal(repo, "ENVELOPE_COMMIT_STATE")


def test_partial_staging_and_historical_edits_refuse(repo: Path) -> None:
    git(repo, "add", "--", f"{UNIT}/{FILE}")
    record = repo / UNIT / FILE
    record.write_text(record.read_text() + "checks: {tests: PASS}\n")
    refusal(repo, "ENVELOPE_COMMIT_INVALID")
    git(repo, "add", "--", f"{UNIT}/{FILE}")
    commit(repo)
    record.write_text(record.read_text() + "assumptions: [changed]\n")
    refusal(repo, "ENVELOPE_COMMIT_INVALID")


@pytest.mark.parametrize("name", ["pre-commit", "commit-msg"])
def test_hook_failure_retains_staged_record_and_same_file_retry(repo: Path, name: str) -> None:
    h = hook(repo, name, "echo rejected-hook >&2\nexit 1")
    before = git(repo, "rev-parse", "HEAD")
    original = (repo / UNIT / FILE).read_bytes()
    with pytest.raises(WorkflowError) as caught:
        commit(repo)
    assert caught.value.code == "ENVELOPE_COMMIT_FAILED"
    assert "staging=yes" in str(caught.value.details)
    assert "rejected-hook" in str(caught.value)
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "status", "--porcelain") == f"A  {UNIT}/{FILE}"
    h.write_text("#!/bin/sh\nexit 0\n")
    assert commit(repo)["outcome"] == "committed"
    assert (repo / UNIT / FILE).read_bytes() == original
    assert len(list((repo / UNIT / "envelopes").iterdir())) == 1


def test_signing_failure_is_retained_and_retryable(repo: Path) -> None:
    git(repo, "config", "commit.gpgsign", "true")
    git(repo, "config", "gpg.program", str(repo / "absent-signer"))
    with pytest.raises(WorkflowError) as caught:
        commit(repo)
    assert caught.value.code == "ENVELOPE_COMMIT_FAILED"
    git(repo, "config", "commit.gpgsign", "false")
    assert commit(repo)["outcome"] == "committed"


def test_post_commit_metadata_rewrite_reports_actual_head(repo: Path) -> None:
    hook(
        repo,
        "post-commit",
        'mv .git/hooks/post-commit .git/hooks/post-commit.used\ngit commit --amend --no-edit --author="Rewriter <rewrite@example.invalid>" >/dev/null',
    )
    before = git(repo, "rev-parse", "HEAD")
    result = commit(repo)
    assert result["head"] == git(repo, "rev-parse", "HEAD")
    assert git(repo, "rev-parse", "HEAD^") == before
    assert git(repo, "show", "-s", "--format=%an") == "Rewriter"


@pytest.mark.parametrize(
    "script",
    [
        'echo changed >> "' + UNIT + "/" + FILE + '"',
        "echo unexpected > extra\ngit add extra",
        "git -c core.hooksPath=/dev/null commit --allow-empty -m unexpected >/dev/null",
    ],
)
def test_unexpected_hook_effects_are_preserved(repo: Path, script: str) -> None:
    hook(repo, "post-commit", script)
    with pytest.raises(WorkflowError) as caught:
        commit(repo)
    assert caught.value.code == "ENVELOPE_COMMIT_UNCERTAIN"
    assert "Inspect" in (caught.value.fix or "")
    assert git(repo, "log", "--format=%s").count("chore(workflow)") == 1


@pytest.mark.parametrize("change", ["summary", "stage", "workflow", "segment", "malformed", "reference"])
def test_skeleton_and_invalid_records_refuse(repo: Path, change: str) -> None:
    p = repo / UNIT / FILE
    text = p.read_text()
    replacements = {
        "summary": ("summary: Authored review", "summary: ''"),
        "stage": ("stage: s", "stage: absent"),
        "workflow": ("workflow: w", "workflow: old"),
        "segment": ("segment: 0", "segment: 1"),
        "malformed": ("status: completed", "status: unknown"),
    }
    if change == "reference":
        p = p.with_name("reverify-01.yaml")
        p.write_text(text.replace("kind: review", "kind: reverify") + "review: review-99.yaml\n")
        refusal(repo, "ENVELOPE_COMMIT_INVALID", "envelopes/reverify-01.yaml")
    else:
        old, new = replacements[change]
        p.write_text(text.replace(old, new))
        error = refusal(repo, "ENVELOPE_COMMIT_INVALID")
        assert error.target_files == (f"{UNIT}/{FILE}",)


@pytest.mark.parametrize(
    "file",
    [
        "../review-01.yaml",
        "/envelopes/review-01.yaml",
        "envelopes/../envelopes/review-01.yaml",
        "envelopes/review-1.yaml",
        "envelopes/*",
    ],
)
def test_nonliteral_paths_refuse(repo: Path, file: str) -> None:
    refusal(repo, "ENVELOPE_COMMIT_INVALID", file)


def test_ignored_and_symlink_files_refuse(repo: Path) -> None:
    ignore = repo / ".git/info/exclude"
    ignore.write_text("review-01.yaml\n")
    refusal(repo, "ENVELOPE_COMMIT_INVALID")
    ignore.write_text("")
    p = repo / UNIT / "envelopes/review-02.yaml"
    p.symlink_to("review-01.yaml")
    refusal(repo, "ENVELOPE_COMMIT_INVALID", "envelopes/review-02.yaml")


@pytest.mark.parametrize(
    "state",
    [
        "detached",
        "MERGE_HEAD",
        "rebase-apply",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "sequencer",
        "index.lock",
        "alternate",
    ],
)
def test_unsupported_state_refuses(repo: Path, monkeypatch: pytest.MonkeyPatch, state: str) -> None:
    if state == "detached":
        git(repo, "checkout", "--detach")
    elif state == "alternate":
        monkeypatch.setenv("GIT_INDEX_FILE", str(repo / ".git/index"))
    else:
        (repo / ".git" / state).touch()
    refusal(repo, "ENVELOPE_COMMIT_STATE")


def test_cli_json_text_and_errors(repo: Path) -> None:
    args = ("envelope", "commit", "--workspace-root", str(repo), "--unit", UNIT, "--file", FILE)
    result = run_cli(*args, "--format", "json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert set(data) == {"unit", "file", "outcome", "head", "subject", "notices"}
    result = run_cli(*args)
    assert (
        result.stdout == f"[ENVELOPE_COMMIT: unit={UNIT} file={FILE} outcome=already_committed head={data['head']}]\n"
    )
    (repo / UNIT / FILE).write_text("broken")
    result = run_cli(*args)
    assert result.exit_code == 2
    assert "ENVELOPE_COMMIT_INVALID" in result.stderr


def test_no_git_authoring_remains_write_only(tmp_path: Path) -> None:
    simple_workspace(tmp_path)
    unit = tmp_path / UNIT
    unit.mkdir(parents=True)
    (unit / "task.md").write_text("---\nid: SPEC-example\nworkflow: w\n---\n")
    result = run_cli(
        "envelope",
        "review",
        "--workspace-root",
        str(tmp_path),
        "--unit",
        UNIT,
        "--summary",
        "Reviewed",
        "--stage",
        "work",
    )
    assert result.exit_code == 0, result.output
    refusal_code = run_cli("envelope", "commit", "--workspace-root", str(tmp_path), "--unit", UNIT, "--file", FILE)
    assert refusal_code.exit_code == 2
    assert "ENVELOPE_COMMIT_STATE" in refusal_code.stderr
    assert not (tmp_path / ".git").exists()


@pytest.mark.parametrize("status", ["failed", "needs_input"])
def test_authored_nonpassing_records_commit_without_passing_gate(repo: Path, status: str) -> None:
    p = repo / UNIT / FILE
    p.write_text(p.read_text().replace("status: completed", f"status: {status}"))
    definition = repo / ".devkit/workflows/w.md"
    definition.write_text(definition.read_text().replace("anchor-exists", "envelope-review-passed"))
    git(repo, "add", str(definition))
    git(repo, "commit", "-m", "require review")
    assert commit(repo)["outcome"] == "committed"
    ws = Workspace(repo, lint=None)
    assert not ws.evaluate_unit(ws.resolve_unit(UNIT), lint=False).complete


def test_review_reverify_final_report_readiness_and_read_only_commands(repo: Path) -> None:
    definition = repo / ".devkit/workflows/w.md"
    definition.write_text(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: s\n    exit: [envelope-review-passed]\n  - id: final\n    exit: [envelope-check-pass(final-report tests), revision-ancestor(review final-report)]\n---\n"
    )
    git(repo, "add", str(definition))
    git(repo, "commit", "-m", "declare record workflow")
    before = git(repo, "rev-parse", "HEAD")
    review = repo / UNIT / FILE
    review.write_text(review.read_text() + f"diff_scope: {{head: '{before}'}}\n")
    commit(repo)
    common = ("--workspace-root", str(repo), "--unit", UNIT)
    result = run_cli(
        "envelope", "reverify", *common, "--stage", "s", "--from", "latest", "--summary", "Verified", "--head", before
    )
    assert result.exit_code == 0, result.output
    commit(repo, "envelopes/reverify-01.yaml")
    record_head = git(repo, "rev-parse", "HEAD")
    result = run_cli(
        "envelope",
        "new",
        *common,
        "--kind",
        "final-report",
        "--stage",
        "final",
        "--summary",
        "Ready",
        "--check",
        "tests=PASS",
        "--head",
        record_head,
    )
    assert result.exit_code == 0, result.output
    # Same-head baseline: authoring and queries have no commit effects.
    baseline = (repo / UNIT / "envelopes/final-report-01.yaml").read_bytes()
    for query in (("next", "--no-lint"), ("show",), ("envelope", "check")):
        result = run_cli(*query, *common)
        assert result.exit_code == 0, result.output
        assert git(repo, "rev-parse", "HEAD") == record_head
    result = commit(repo, "envelopes/final-report-01.yaml")
    assert result["head"] != record_head
    assert (repo / UNIT / "envelopes/final-report-01.yaml").read_bytes() == baseline
    ws = Workspace(repo, lint=None)
    assert ws.evaluate_unit(ws.resolve_unit(UNIT), lint=False).complete


@pytest.mark.parametrize("identity", ["unsupported", "PROP-second-unit"])
def test_tracked_anchor_identity(repo: Path, identity: str) -> None:
    anchor = repo / UNIT / "task.md"
    anchor.write_text(anchor.read_text().replace("SPEC-example", identity))
    git(repo, "add", str(anchor))
    git(repo, "commit", "-m", "declare identity")
    if identity == "unsupported":
        refusal(repo, "ENVELOPE_COMMIT_INVALID")
    else:
        git(repo, "branch", "-m", "another-name")
        assert commit(repo)["subject"] == "chore(workflow): record second-unit review-01"


def test_unknown_git_outcome_keeps_staging(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_agt.features.workflow.repositories.envelope_commit import EnvelopeCommitRepository
    from devkit_core.core import GitError

    original = EnvelopeCommitRepository.git

    def interrupted(self: EnvelopeCommitRepository, *args: str, input: bytes | None = None) -> bytes:
        if args[0] == "commit":
            raise GitError("simulated timeout; completion unknown", returncode=None)
        return original(self, *args, input=input)

    monkeypatch.setattr(EnvelopeCommitRepository, "git", interrupted)
    with pytest.raises(WorkflowError) as caught:
        commit(repo)
    assert caught.value.code == "ENVELOPE_COMMIT_UNCERTAIN"
    assert git(repo, "status", "--porcelain") == f"A  {UNIT}/{FILE}"


def test_hook_branch_switch_is_uncertain_and_preserved(repo: Path) -> None:
    hook(repo, "post-commit", "git switch -c unexpected")
    with pytest.raises(WorkflowError) as caught:
        commit(repo)
    assert caught.value.code == "ENVELOPE_COMMIT_UNCERTAIN"
    assert git(repo, "symbolic-ref", "HEAD") == "refs/heads/unexpected"
    assert not git(repo, "status", "--porcelain")
    assert "before_ref=refs/heads/different-branch-name" in str(caught.value.details)
    assert "after_ref=refs/heads/unexpected" in str(caught.value.details)
