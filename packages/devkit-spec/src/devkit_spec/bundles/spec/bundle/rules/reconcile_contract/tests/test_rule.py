"""``RULE-reconcile-contract``, loaded from this folder as devkit loads the deployed copy."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from devkit_agt.features.rules import RuleContext, Violation, evaluate_rules, git_snapshot
from devkit_agt.features.rules.services.testing import check, load_rule, write_files

RULE = load_rule(__file__)
BUNDLE = "specs/2026-10/20261001-x"
SPEC = f"{BUNDLE}/spec.md"
RECORD = f"{BUNDLE}/reconcile.md"
WAIVER = "rationale: The acceptance criteria of this use case are unchanged.\n"


def _found(violations: list[Violation]) -> list[tuple[str, int, str]]:
    """``(file, line, message)`` of the violations that remain (not fixed)."""
    return [(v.file, v.line, v.message) for v in violations if not v.fixed]


def _record(body: str) -> str:
    return f"---\nreconcile_id: REC-x\n{body}---\n# Reconcile\n"


def _spec(status: str = "in-progress") -> str:
    return f"---\nid: SPEC-x\nstatus: {status}\n---\n"


def test_a_well_formed_record_passes(tmp_path: Path) -> None:
    files = {
        SPEC: _spec(),
        RECORD: _record(
            "status: resolved\ntargets:\n  - file: docs/a.md\n    resolution: modified\n"
            f"  - file: docs/b.md\n    resolution: waived\n    {WAIVER}"
        ),
    }
    assert check(RULE, tmp_path, files) == []
    assert check(RULE, tmp_path, {RECORD: _record("status: pending\ntargets: []\n")}) == []


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("status: done\ntargets: []\n", "status must be pending or resolved, got 'done'"),
        ("status: resolved\n", "targets must be a list (empty when nothing in the Living Spec is affected)"),
        ("status: resolved\ntargets: [x]\n", "targets[1] must be a mapping of file, resolution and rationale"),
        (
            "status: resolved\ntargets:\n  - {file: ../a.md, resolution: modified}\n",
            "targets[1].file '../a.md' must be a unique workspace-relative path",
        ),
        (
            "status: resolved\ntargets:\n  - {file: a.md, resolution: modified}\n  - {file: a.md, resolution: modified}\n",
            "targets[2].file 'a.md' must be a unique workspace-relative path",
        ),
        (
            "status: resolved\ntargets:\n  - {file: ./docs/a.md, resolution: modified}\n",
            "targets[1].file './docs/a.md' must be written in canonical form: docs/a.md",
        ),
        (
            "status: resolved\ntargets:\n  - {file: docs//a.md, resolution: modified}\n",
            "targets[1].file 'docs//a.md' must be written in canonical form: docs/a.md",
        ),
        (
            "status: resolved\ntargets:\n  - {file: docs/a.md, resolution: modified}\n"
            "  - {file: ./docs/a.md, resolution: modified}\n",
            "targets[2].file './docs/a.md' must be written in canonical form: docs/a.md",
        ),
        (
            "status: resolved\ntargets:\n  - {file: a.md, resolution: kept}\n",
            "targets[1].resolution must be modified or waived, got 'kept'",
        ),
        (
            "status: resolved\ntargets:\n  - {file: a.md, resolution: waived, rationale: not needed}\n",
            "targets[1] waiver of a.md needs a rationale of at least 20 non-whitespace characters, has 9",
        ),
    ],
)
def test_malformed_records(tmp_path: Path, body: str, message: str) -> None:
    assert _found(check(RULE, tmp_path, {SPEC: _spec(), RECORD: _record(body)})) == [(RECORD, 1, message)]


def test_missing_id_and_frontmatter(tmp_path: Path) -> None:
    files = {SPEC: _spec(), RECORD: "---\nstatus: pending\ntargets: []\n---\n"}
    assert [m for _, _, m in _found(check(RULE, tmp_path, files))] == ["reconcile_id is missing"]
    files = {RECORD: "# no frontmatter\n"}
    assert [m for _, _, m in _found(check(RULE, tmp_path, files))] == ["reconcile.md has no frontmatter"]
    files = {RECORD: "---\nstatus: [\n---\n"}
    assert _found(check(RULE, tmp_path, files))[0][2].startswith("frontmatter is malformed")


def test_completed_bundles_only_when_targeted(tmp_path: Path) -> None:
    files = {SPEC: _spec("completed"), RECORD: _record("status: done\n")}
    assert check(RULE, tmp_path, files) == []
    assert len(_found(check(RULE, tmp_path, targets=[RECORD]))) == 2


def test_only_targets_are_reported(tmp_path: Path) -> None:
    files = {SPEC: _spec(), RECORD: _record("status: done\ntargets: []\n")}
    assert check(RULE, tmp_path, files, targets=[SPEC]) == []


# Diff evidence in snapshot runs (``check --staged``/``--ci``): the rule reads ``ctx.snapshot``.


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _repo(root: Path) -> None:
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")


def _staged(root: Path) -> list[tuple[str, str]]:
    _git(root, "add", "-A")
    snapshot = git_snapshot(root, staged=True)
    ctx = RuleContext(workspace_root=root, changed_files=list(snapshot.changed), snapshot=snapshot)
    result = evaluate_rules(ctx, [RULE])
    assert result.errors == []
    return [(v.file, v.message) for v in result.violations]


COVERED = (
    "formal_docs:\n"
    '  design: "none: no persisted format, derivation or ordering changes"\n'
    '  domain: "none: no concept, identity or lifecycle changes here"\n'
    '  operations: "none: no symptom or action routing changes here"\n'
)


def _targets_record(targets: str, status: str = "resolved", coverage: str = COVERED) -> str:
    listed = f"targets:\n{targets}" if targets else "targets: []\n"
    return f"---\nreconcile_id: REC-x\nstatus: {status}\n{listed}{coverage}---\n"


def test_a_resolved_record_needs_its_modified_targets_in_the_diff(tmp_path: Path) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {"docs/a.md": "a\n", "docs/b.md": "b\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    write_files(
        tmp_path,
        {
            "docs/a.md": "a changed\n",
            SPEC: _spec(),
            RECORD: _targets_record(
                "  - {file: docs/a.md, resolution: modified}\n  - {file: docs/b.md, resolution: modified}\n"
            ),
        },
    )
    assert _staged(tmp_path) == [
        (
            RECORD,
            "target docs/b.md is resolved as modified but absent from the staged diff or the branch's earlier commits",
        )
    ]


def test_a_pending_record_and_a_body_only_edit_need_no_evidence(tmp_path: Path) -> None:
    _repo(tmp_path)
    targets = "  - {file: docs/b.md, resolution: modified}\n"
    write_files(tmp_path, {SPEC: _spec(), RECORD: _targets_record(targets, status="pending")})
    assert _staged(tmp_path) == []
    write_files(tmp_path, {RECORD: _targets_record(targets), "docs/b.md": "b\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "resolved")
    write_files(tmp_path, {RECORD: _targets_record(targets) + "Body note.\n"})
    assert _staged(tmp_path) == []


def test_a_target_an_earlier_commit_of_the_branch_changed_counts_at_commit_time(tmp_path: Path) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {"docs/a.md": "a\n", "docs/b.md": "b\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    _git(tmp_path, "switch", "-q", "-c", "dev-x")
    _git(tmp_path, "config", "branch.dev-x.devkitBase", "main")  # what `devkit worktree start --no-worktree` records
    write_files(tmp_path, {"docs/a.md": "a promoted by the handoff\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "handoff")
    targets = "  - {file: docs/a.md, resolution: modified}\n  - {file: docs/b.md, resolution: modified}\n"
    write_files(tmp_path, {SPEC: _spec(), RECORD: _targets_record(targets)})
    # docs/a.md changed in the branch's earlier commit; docs/b.md never did.
    assert _staged(tmp_path) == [
        (
            RECORD,
            "target docs/b.md is resolved as modified but absent from the staged diff or the branch's earlier commits",
        )
    ]


def test_without_an_integration_base_the_staged_diff_alone_is_the_evidence(tmp_path: Path) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {"docs/a.md": "a\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    write_files(tmp_path, {"docs/a.md": "a changed\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "on main itself")
    write_files(tmp_path, {SPEC: _spec(), RECORD: _targets_record("  - {file: docs/a.md, resolution: modified}\n")})
    assert len(_staged(tmp_path)) == 1  # no other branch to integrate into: an earlier commit on main is not evidence


# The design, domain and operations assessment: ``formal_docs`` form in every run, coverage when newly resolved.

REASON = "none: the change persists nothing a later run reads back"


@pytest.mark.parametrize(
    ("coverage", "message"),
    [
        ("formal_docs: [none]\n", "formal_docs must be a mapping of design, domain and operations to a none reason"),
        (
            f'formal_docs:\n  designs: "{REASON}"\n',
            "formal_docs.designs is not a role: use design, domain or operations",
        ),
        (
            'formal_docs:\n  domain: "no concept changes in this record at all"\n',
            'formal_docs.domain must be a string starting "none: " followed by the reason',
        ),
        (
            "formal_docs:\n  domain: [x]\n",
            'formal_docs.domain must be a string starting "none: " followed by the reason',
        ),
        (
            'formal_docs:\n  operations: "none: too short"\n',
            "formal_docs.operations needs a reason of at least 20 non-whitespace characters, has 8",
        ),
        (
            f'related_designs: [DESIGN-x]\nformal_docs:\n  design: "{REASON}"\n',
            "formal_docs.design conflicts with related_designs: give affected IDs or a none reason, not both",
        ),
    ],
)
def test_a_malformed_formal_docs_is_reported_in_every_run(tmp_path: Path, coverage: str, message: str) -> None:
    files = {SPEC: _spec(), RECORD: _record(f"status: pending\ntargets: []\n{coverage}")}
    assert _found(check(RULE, tmp_path, files)) == [(RECORD, 1, message)]


def test_a_plain_run_accepts_an_uncovered_record(tmp_path: Path) -> None:
    files = {SPEC: _spec("completed"), RECORD: _record("status: resolved\ntargets: []\n")}
    assert check(RULE, tmp_path, files, targets=[RECORD]) == []


def _uncovered(*roles: str) -> list[tuple[str, str]]:
    fields = {"design": "related_designs", "domain": "related_domains", "operations": "related_operations"}
    return [
        (
            RECORD,
            f"formal_docs role {role} is not covered: list affected IDs in {fields[role]} or give"
            f' formal_docs.{role}: "none: <reason>"',
        )
        for role in roles
    ]


def test_a_newly_resolved_record_needs_every_role_covered_in_a_staged_run(tmp_path: Path) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {SPEC: _spec(), RECORD: _targets_record("", coverage="")})
    assert _staged(tmp_path) == _uncovered("design", "domain", "operations")
    partial = f'related_domains: [DOMAIN-x]\nformal_docs:\n  design: "{REASON}"\n'
    write_files(tmp_path, {RECORD: _targets_record("", coverage=partial)})
    assert _staged(tmp_path) == _uncovered("operations")


@pytest.mark.parametrize(
    "coverage",
    [
        COVERED,
        "related_designs: [DESIGN-x]\nrelated_domains: [DOMAIN-x]\nrelated_operations: [OPS-x]\n",
        f'related_designs: [DESIGN-x]\nformal_docs:\n  domain: "{REASON}"\n  operations: "{REASON}"\n',
    ],
)
def test_full_coverage_by_ids_reasons_or_a_mix_passes(tmp_path: Path, coverage: str) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {SPEC: _spec(), RECORD: _targets_record("", coverage=coverage)})
    assert _staged(tmp_path) == []


def test_a_pending_record_or_one_resolved_at_the_base_needs_no_coverage(tmp_path: Path) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {SPEC: _spec(), RECORD: _targets_record("", status="pending", coverage="")})
    assert _staged(tmp_path) == []
    _git(tmp_path, "commit", "-q", "-m", "pending")
    write_files(tmp_path, {RECORD: _targets_record("", coverage=COVERED)})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "resolved")
    # A record resolved at the base keeps its old shape when a later commit edits it.
    write_files(tmp_path, {RECORD: _targets_record("", coverage="") + "Link repaired.\n"})
    assert _staged(tmp_path) == []


def test_a_record_resolved_in_a_merge_head_needs_no_coverage(tmp_path: Path) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {"docs/a.md": "a\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    _git(tmp_path, "switch", "-q", "-c", "dev-x")
    write_files(tmp_path, {"docs/a.md": "a on the branch\n"})
    _git(tmp_path, "commit", "-q", "-am", "branch")
    _git(tmp_path, "switch", "-q", "main")
    write_files(tmp_path, {"docs/a.md": "a on main\n", SPEC: _spec(), RECORD: _targets_record("", coverage="")})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "an older record resolved on main")
    _git(tmp_path, "switch", "-q", "dev-x")
    subprocess.run(["git", "-C", str(tmp_path), "merge", "-q", "main"], capture_output=True, check=False)
    assert (tmp_path / ".git/MERGE_HEAD").exists()  # docs/a.md conflicts, so the merge waits to be concluded
    write_files(tmp_path, {"docs/a.md": "a resolved\n"})
    assert _staged(tmp_path) == []


def test_a_record_resolved_by_a_picked_commit_needs_no_coverage(tmp_path: Path) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {"docs/a.md": "a\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    _git(tmp_path, "switch", "-q", "-c", "dev-x")
    write_files(tmp_path, {"docs/a.md": "a on the branch\n"})
    _git(tmp_path, "commit", "-q", "-am", "branch")
    _git(tmp_path, "switch", "-q", "main")
    write_files(tmp_path, {"docs/a.md": "a on main\n", SPEC: _spec(), RECORD: _targets_record("", coverage="")})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "an older record resolved on main")
    _git(tmp_path, "switch", "-q", "dev-x")
    subprocess.run(["git", "-C", str(tmp_path), "cherry-pick", "main"], capture_output=True, check=False)
    assert (tmp_path / ".git/CHERRY_PICK_HEAD").exists()  # docs/a.md conflicts, so the pick waits to be concluded
    write_files(tmp_path, {"docs/a.md": "a resolved\n"})
    assert _staged(tmp_path) == []
    (tmp_path / ".git/CHERRY_PICK_HEAD").unlink()  # without the operation head the record is newly resolved
    assert _staged(tmp_path) == _uncovered("design", "domain", "operations")


def test_a_newly_resolved_record_needs_coverage_in_a_ci_run(tmp_path: Path) -> None:
    _repo(tmp_path)
    write_files(tmp_path, {"docs/a.md": "a\n"})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    base = subprocess.run(
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    write_files(tmp_path, {SPEC: _spec(), RECORD: _targets_record("", coverage="")})
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "resolve")
    snapshot = git_snapshot(tmp_path, staged=False, base=base)
    ctx = RuleContext(workspace_root=tmp_path, changed_files=list(snapshot.changed), snapshot=snapshot)
    result = evaluate_rules(ctx, [RULE])
    assert [(v.file, v.message) for v in result.violations] == _uncovered("design", "domain", "operations")
