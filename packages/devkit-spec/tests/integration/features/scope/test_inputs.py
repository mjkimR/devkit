from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from spec_support.scope import CAP_A, CAP_B, CAP_EMPTY, CAP_PLANNED, GIT_ENV, SPEC, git, make_repo, write

from devkit_spec.base.errors import ProposalNotFoundError, ScopeInputInvalidError, ScopeSpecNotFoundError
from devkit_spec.features.scope import (
    Deadline,
    Diff,
    Granularity,
    ScopePath,
    ScopeSet,
    Source,
    Stage,
    compare,
    compare_all,
    from_proposal,
    from_spec,
    observe_git,
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path / "repo")


def _reasons(scope: ScopeSet) -> dict[str, str]:
    return {item.value: item.reason for item in scope.unresolved}


def test_from_proposal(repo: Path) -> None:
    scope = from_proposal(repo, "one")
    assert scope.id == "PROP-one"
    assert [(item.path, item.kind) for item in scope.docs] == [
        (CAP_A, Granularity.FILE),
        (CAP_EMPTY, Granularity.FILE),
        (CAP_PLANNED, Granularity.UNKNOWN),
        ("docs/decisions/ADR-x.md", Granularity.FILE),
    ]
    assert all(item.stage is Stage.PROP for item in scope.docs)
    assert [(item.path, item.kind, item.source) for item in scope.code] == [
        ("src/a", Granularity.DIR, Source.CANDIDATE),
        ("src/shared.py", Granularity.FILE, Source.CANDIDATE),
    ]
    assert _reasons(scope) == {CAP_EMPTY: "no-entrypoints", CAP_PLANNED: "planned-doc"}
    assert from_proposal(repo, "PROP-one").id == "PROP-one"

    bare = from_proposal(repo, "bare")
    assert bare.docs == [] and _reasons(bare) == {"target-docs.md": "missing-target-docs"}
    write(repo, "docs/proposals/PROP-bare/target-docs.md", "---\nid: PROP-bare-target\n---\n")
    assert _reasons(from_proposal(repo, "bare")) == {"target-docs.md": "no-targets"}
    write(repo, "docs/proposals/PROP-single.md", "---\nid: PROP-single\nstatus: draft\n---\n")
    assert _reasons(from_proposal(repo, "single")) == {"target-docs.md": "missing-target-docs"}
    with pytest.raises(ProposalNotFoundError):
        from_proposal(repo, "nope")


def test_from_spec(repo: Path) -> None:
    scope = from_spec(repo, SPEC)
    assert scope.id == "SPEC-s"
    assert [(item.path, item.stage) for item in scope.docs] == [(CAP_A, Stage.SPEC)]
    assert {item.path: item.source for item in scope.code} == {
        "src/a": Source.DECLARED_CODE,  # declared code replaces the target's entrypoint candidates
        "src/b": Source.DECLARED_CODE,
    }
    assert _reasons(scope) == {
        "N/A": "not-a-path",
        "docs/capabilities/": "excluded-tree",
        "src/**": "invalid-path",
        CAP_B: "waived",
    }
    assert scope.diff == [Diff(CAP_EMPTY, "target-docs")]

    write(repo, "specs/2026-10/20261002-n/spec.md", "---\nid: SPEC-n\n---\n")
    write(repo, "specs/2026-10/20261002-n/target-docs.md", f"---\ntargets:\n  - file: {CAP_B}\n---\n")
    planned = from_spec(repo, "specs/2026-10/20261002-n")
    assert [(item.path, item.stage) for item in planned.docs] == [(CAP_B, Stage.PROP)]
    assert _reasons(planned) == {"reconcile.md": "missing-reconcile", "tasks.md": "missing-tasks"}

    with pytest.raises(ScopeSpecNotFoundError):
        from_spec(repo, "specs/2026-10/20261003-missing")
    write(repo, "specs/2026-10/20261002-n/reconcile.md", "---\ntargets: nope\n---\n")
    with pytest.raises(ScopeInputInvalidError):
        from_spec(repo, "specs/2026-10/20261002-n")


OTHER = "specs/2026-09/20260901-other"
FEEDBACK_FILE = f"{OTHER}/feedback/observation.md"


def _tasks(repo: Path, spec_dir: str, *entries: str) -> None:
    write(repo, f"{spec_dir}/spec.md", f"---\nid: SPEC-{spec_dir.rsplit('-', 1)[-1]}\n---\n")
    boundary = ", ".join(f"`{entry}`" for entry in entries)
    write(
        repo, f"{spec_dir}/tasks.md", f"- [ ] **Task 1**: t\n  - **_Boundary**: {boundary}\n  - _Requirements: AC-01_\n"
    )


# SPEC-feedback-guidance-and-scope AC-05, AC-06
def test_a_declared_feedback_file_of_another_bundle_is_a_file_scope(repo: Path) -> None:
    write(repo, FEEDBACK_FILE, "---\nid: FB-observation\nstatus: open\n---\n")
    write(repo, f"{OTHER}/spec.md", "---\nid: SPEC-other\n---\n")
    planned = f"{OTHER}/feedback/planned.md"
    _tasks(
        repo,
        SPEC,
        "src/a/",
        FEEDBACK_FILE,
        planned,
        f"{OTHER}/spec.md",
        f"{OTHER}/feedback/",
        f"{OTHER}/feedback/*.md",
        f"{SPEC}/feedback/own.md",
        "docs/capabilities/x/feedback/x.md",
    )
    scope = from_spec(repo, SPEC)
    assert {(item.path, item.kind, item.source) for item in scope.code} == {
        ("src/a", Granularity.DIR, Source.DECLARED_CODE),
        (FEEDBACK_FILE, Granularity.FILE, Source.DECLARED_CODE),
        (planned, Granularity.UNKNOWN, Source.DECLARED_CODE),
    }
    assert {key: value for key, value in _reasons(scope).items() if value != "waived"} == {
        f"{OTHER}/spec.md": "excluded-tree",
        f"{OTHER}/feedback/": "excluded-tree",
        f"{OTHER}/feedback/*.md": "invalid-path",
        f"{SPEC}/feedback/own.md": "excluded-tree",
        "docs/capabilities/x/feedback/x.md": "excluded-tree",
    }


def test_a_feedback_path_that_is_a_directory_stays_excluded(repo: Path) -> None:
    write(repo, f"{OTHER}/feedback/odd.md/inner.md", "x\n")
    _tasks(repo, SPEC, f"{OTHER}/feedback/odd.md")
    scope = from_spec(repo, SPEC)
    assert _reasons(scope)[f"{OTHER}/feedback/odd.md"] == "excluded-tree"


# SPEC-feedback-guidance-and-scope AC-07
def test_feedback_files_do_not_replace_the_entrypoint_candidates(repo: Path) -> None:
    write(repo, FEEDBACK_FILE, "---\nid: FB-observation\nstatus: open\n---\n")
    _tasks(repo, SPEC, FEEDBACK_FILE, "N/A")
    scope = from_spec(repo, SPEC)
    assert {item.path: item.source for item in scope.code} == {
        FEEDBACK_FILE: Source.DECLARED_CODE,
        "src/a": Source.CANDIDATE,
        "src/shared.py": Source.CANDIDATE,
    }


# SPEC-feedback-guidance-and-scope AC-05
def test_two_units_resolving_the_same_feedback_overlap(repo: Path) -> None:
    write(repo, FEEDBACK_FILE, "---\nid: FB-observation\nstatus: open\n---\n")
    second = "specs/2026-10/20261002-t"
    _tasks(repo, SPEC, "src/a/", FEEDBACK_FILE)
    _tasks(repo, second, "src/b/", FEEDBACK_FILE)
    pair = compare(from_spec(repo, SPEC), from_spec(repo, second))
    assert [(item.path, item.other, item.granularity) for item in pair.code] == [
        (FEEDBACK_FILE, FEEDBACK_FILE, Granularity.FILE)
    ]


def test_observe_git(repo: Path) -> None:
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "src/committed.py", "c = 1\n")
    git(repo, "add", "src/committed.py")
    git(repo, "commit", "-q", "-m", "c")
    write(repo, "src/staged.py", "s = 1\n")
    git(repo, "add", "src/staged.py")
    write(repo, "src/a/a.py", "a = 2\n")
    write(repo, "src/untracked.py", "u = 1\n")
    write(repo, "src/odd[1].py", "o = 1\n")  # outside the path contract: left out
    observed, unresolved = observe_git(repo, base, Deadline(30), "2026-10-13T00:00:00.000000Z")
    assert unresolved == []
    assert [item.path for item in observed] == ["src/a/a.py", "src/committed.py", "src/staged.py", "src/untracked.py"]
    assert {(item.source, item.stage, item.first_seen) for item in observed} == {
        (Source.OBSERVED, Stage.BUILD, "2026-10-13T00:00:00.000000Z")
    }
    assert [item.reason for item in observe_git(repo, "deadbeef", Deadline(30), "")[1]] == ["unknown-base-revision"]
    assert [item.reason for item in observe_git(repo, "", Deadline(30), "")[1]] == ["missing-base-revision"]


def test_observe_git_from_the_fork_point_of_the_base_ref(repo: Path) -> None:
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "-q", "-c", "task")
    write(repo, "src/a/a.py", "a = 2\n")
    write(repo, "src/shared.py", "s = 'task'\n")
    git(repo, "commit", "-q", "-am", "task")
    git(repo, "switch", "-q", "main")
    write(repo, "src/b/b.py", "b = 2\n")
    write(repo, "src/shared.py", "s = 'main'\n")
    git(repo, "commit", "-q", "-am", "upstream")
    git(repo, "switch", "-q", "task")
    merge = subprocess.run(
        ["git", "merge", "-q", "main"], cwd=repo, env={**os.environ, **GIT_ENV}, capture_output=True, check=False
    )
    assert merge.returncode == 1, "the merge conflicts on src/shared.py"
    write(repo, "src/shared.py", "s = 'resolved'\n")  # the conflict resolution is the task's own change
    git(repo, "commit", "-q", "-am", "merge main")

    observed, unresolved = observe_git(repo, base, Deadline(30), "", base_ref="refs/heads/main")
    assert unresolved == []
    assert [item.path for item in observed] == ["src/a/a.py", "src/shared.py"], "upstream changes are not observed"
    fixed, _ = observe_git(repo, base, Deadline(30), "")
    assert "src/b/b.py" in {item.path for item in fixed}, "without a base ref the range starts at base_revision"
    observed, unresolved = observe_git(repo, base, Deadline(30), "", base_ref="refs/heads/gone")
    assert [(item.value, item.reason) for item in unresolved] == [("refs/heads/gone", "missing-base-ref")]
    assert "src/b/b.py" in {item.path for item in observed}, "an unresolvable base ref falls back to base_revision"


def test_observe_git_registered_after_a_task_commit_skips_a_later_merge_of_the_base_ref(repo: Path) -> None:
    git(repo, "switch", "-q", "-c", "task")
    write(repo, "src/a/a.py", "a = 2\n")
    git(repo, "commit", "-q", "-am", "task")
    base = git(repo, "rev-parse", "HEAD")  # registered after the task's first commit
    git(repo, "switch", "-q", "main")
    write(repo, "src/b/b.py", "b = 2\n")
    git(repo, "commit", "-q", "-am", "upstream")
    git(repo, "switch", "-q", "task")
    git(repo, "merge", "-q", "--no-edit", "main")  # the fork point and base_revision have diverged
    write(repo, "src/shared.py", "s = 'task'\n")
    git(repo, "commit", "-q", "-am", "after the merge")

    observed, unresolved = observe_git(repo, base, Deadline(30), "", base_ref="refs/heads/main")
    assert unresolved == []
    assert [item.path for item in observed] == ["src/shared.py"], "what the task merged in is not observed"
    observed, unresolved = observe_git(repo, "deadbeef", Deadline(30), "", base_ref="refs/heads/main")
    assert [item.reason for item in unresolved] == ["unknown-base-revision"]


@pytest.mark.parametrize("stage", ["committed", "staged", "unstaged"])
def test_observe_git_lists_both_sides_of_a_rename(repo: Path, stage: str) -> None:
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "mv", "src/a/a.py", "src/moved.py")
    if stage == "committed":
        git(repo, "commit", "-q", "-m", "move")
    elif stage == "unstaged":
        git(repo, "reset", "-q")
        git(repo, "add", "-N", "src/moved.py")
    observed, _ = observe_git(repo, base, Deadline(30), "")
    assert {"src/a/a.py", "src/moved.py"} <= {item.path for item in observed}


def test_observe_git_is_relative_to_a_workspace_below_the_top_level(repo: Path) -> None:
    write(repo, "pkg/.devkit/config.toml", "")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "pkg")
    base = git(repo, "rev-parse", "HEAD")
    write(repo, "pkg/src/x.py", "x = 1\n")
    write(repo, "outside.py", "o = 1\n")
    observed, _ = observe_git(repo / "pkg", base, Deadline(30), "")
    assert [item.path for item in observed] == ["src/x.py"]


def test_compare(repo: Path) -> None:
    one, two = from_proposal(repo, "one"), from_proposal(repo, "two")
    result = compare(one, two)
    assert (result.a, result.b) == ("PROP-one", "PROP-two")
    assert [(item.path, item.granularity) for item in result.docs] == [(CAP_PLANNED, Granularity.UNKNOWN)]
    assert result.code == () and result.unresolved == 3

    a = ScopeSet("a", code=[ScopePath("src/a", Granularity.DIR, Source.DECLARED_CODE, Stage.SPEC)])
    b = ScopeSet(
        "b",
        observed=[
            ScopePath("src/a/x.py", Granularity.FILE, Source.OBSERVED, Stage.BUILD),
            ScopePath("src/ab/y.py", Granularity.FILE, Source.OBSERVED, Stage.BUILD),
        ],
    )
    pair = compare(a, b)
    assert [(item.path, item.other, item.granularity, item.source, item.other_source) for item in pair.code] == [
        ("src/a", "src/a/x.py", Granularity.DIR, Source.DECLARED_CODE, Source.OBSERVED)
    ]
    assert pair.overlapping and not compare(b, ScopeSet("c")).overlapping
    assert len(compare_all([one, two, a])) == 3


def test_package_targets_keep_shared_code_candidates(repo: Path) -> None:
    target = "docs/packages/p/capabilities/core/CAP-CORE-shared.md"
    write(repo, target, "---\nid: CAP-CORE-shared\nstatus: active\nentrypoints: [src/shared.py]\n---\n")
    for slug in ("one", "two"):
        write(repo, f"docs/proposals/PROP-{slug}/target-docs.md", f"---\ntargets:\n  - file: {target}\n---\n")
    a, b = from_proposal(repo, "one"), from_proposal(repo, "two")
    assert [item.path for item in a.code] == ["src/shared.py"]
    result = compare(a, b)
    assert len(result.docs) == 1 and len(result.code) == 1 and result.unresolved == 0


def test_from_spec_reads_a_wrapped_boundary(repo: Path) -> None:
    # AC-03: the registry takes the parse of CAP-TRACE-code-entrypoints, continuation lines included.
    base = "specs/2026-10/20261004-w"
    write(repo, f"{base}/spec.md", "---\nid: SPEC-w\n---\n")
    write(repo, f"{base}/tasks.md", "- [ ] t\n  - **_Boundary**: `src/a`,\n    `src/b`,\n    `src/shared.py`\n")
    scope = from_spec(repo, base)
    assert [item.path for item in scope.code if item.source is Source.DECLARED_CODE] == [
        "src/a",
        "src/b",
        "src/shared.py",
    ]


def test_from_spec_skips_skeleton_tasks(repo: Path) -> None:
    for slug in ("alpha", "beta"):
        base = f"specs/2026-10/20261015-{slug}"
        write(repo, f"{base}/spec.md", f"---\nid: SPEC-{slug}\n---\n<!-- devkit:skeleton -->\n")
        write(
            repo,
            f"{base}/tasks.md",
            f"---\nid: TASKS-{slug}\n---\n<!-- devkit:skeleton -->\n- [ ] **Task 1.1**: Core\n  - **_Boundary**: <target area>\n",
        )
    a, b = from_spec(repo, "specs/2026-10/20261015-alpha"), from_spec(repo, "specs/2026-10/20261015-beta")
    assert a.code == [] and b.code == []
    assert _reasons(a) == {"reconcile.md": "missing-reconcile", "tasks.md": "missing-tasks"}
    result = compare(a, b)
    assert result.docs == () and result.code == ()

    write(
        repo,
        "specs/2026-10/20261015-alpha/tasks.md",
        "---\nid: TASKS-alpha\n---\n- [ ] **Task 1.1**: Core\n  - **_Boundary**: <target area>, `src/a`\n",
    )
    edited = from_spec(repo, "specs/2026-10/20261015-alpha")
    assert [item.path for item in edited.code] == ["src/a"]
    assert _reasons(edited)["<target area>"] == "not-a-path"


def _bundle(repo: Path, slug: str, tasks: str | None, targets: tuple[str, ...] = (CAP_A,)) -> str:
    """A spec bundle whose ``reconcile.md`` modifies ``targets``; ``tasks`` is its ``tasks.md`` (``None``: none)."""
    base = f"specs/2026-10/20261022-{slug}"
    write(repo, f"{base}/spec.md", f"---\nid: SPEC-{slug}\n---\n")
    entries = "".join(f"  - file: {target}\n    resolution: modified\n" for target in targets)
    write(repo, f"{base}/reconcile.md", f"---\nreconcile_id: REC-{slug}\nstatus: pending\ntargets:\n{entries}---\n")
    if tasks is not None:
        write(repo, f"{base}/tasks.md", tasks)
    return base


def _boundary(*values: str) -> str:
    return f"- [ ] **Task 1**: t\n  - **_Boundary**: {', '.join(values)}\n  - _Requirements: AC-01_\n"


def test_declared_code_replaces_target_entrypoint_candidates(repo: Path) -> None:
    # AC-01: CAP_A lists src/a/ and src/shared.py; the boundary names only src/b/.
    scope = from_spec(repo, _bundle(repo, "narrow", _boundary("`src/b/`")))
    assert [(item.path, item.source) for item in scope.code] == [("src/b", Source.DECLARED_CODE)]
    assert [(item.path, item.source) for item in scope.docs] == [(CAP_A, Source.DECLARED_DOC)]
    assert scope.unresolved == []


def test_a_candidate_only_path_no_longer_overlaps(repo: Path) -> None:
    # AC-02: PROP-one's candidates (src/a, src/shared.py) meet the bundle only through the shared target document.
    narrow = from_spec(repo, _bundle(repo, "narrow", _boundary("`src/b/`")))
    other = ScopeSet("other", code=[ScopePath("src/shared.py", Granularity.FILE, Source.DECLARED_CODE, Stage.SPEC)])
    assert compare(narrow, other).code == ()
    pair = compare(narrow, from_proposal(repo, "one"))
    assert pair.code == () and [item.path for item in pair.docs] == [CAP_A]


@pytest.mark.parametrize(
    "tasks",
    [
        None,
        "---\nid: TASKS-x\n---\n<!-- devkit:skeleton -->\n- [ ] **Task 1.1**: Core\n  - **_Boundary**: `src/b/`\n",
        _boundary("N/A", "<target area>", "`docs/capabilities/`", "`specs/2026-10/`", "`src/**`"),
    ],
    ids=["missing", "skeleton", "no-code-path"],
)
def test_candidates_stay_before_code_is_declared(repo: Path, tasks: str | None) -> None:
    # AC-03: without a declared code path the target entrypoints remain the code estimate.
    scope = from_spec(repo, _bundle(repo, "early", tasks))
    assert [(item.path, item.source) for item in scope.code] == [
        ("src/a", Source.CANDIDATE),
        ("src/shared.py", Source.CANDIDATE),
    ]
    assert [(item.path, item.source) for item in from_proposal(repo, "one").code] == [
        ("src/a", Source.CANDIDATE),
        ("src/shared.py", Source.CANDIDATE),
    ]


def test_missing_target_entrypoints_stay_unresolved_with_declared_code(repo: Path) -> None:
    # AC-05: no-entrypoints reports the target's traceability gap whether or not candidates are used.
    scope = from_spec(repo, _bundle(repo, "gap", _boundary("`src/b/`"), (CAP_A, CAP_EMPTY)))
    assert [item.source for item in scope.code] == [Source.DECLARED_CODE]
    assert [(item.value, item.reason, item.source) for item in scope.unresolved] == [
        (CAP_EMPTY, "no-entrypoints", Source.CANDIDATE)
    ]
