"""Compare recorded returns with Git observations and authority."""

from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError, ExitCode
from devkit_core.base.errors import GitError
from devkit_core.core import is_ancestor
from devkit_docs.utils.paths import covers

from devkit_adaptive.base import errors as e
from devkit_adaptive.features.assignment.models.values import Assignment, Result
from devkit_adaptive.features.assignment.repositories import git


def verify(root: Path, value: Assignment, values: dict[str, Assignment]) -> Result:
    tree = git.require_worktree(root, Path(value["worktree"]))
    returned = value["return"]
    if returned is None:
        raise e.AssignmentNotReturned(f"assignment {value['id']} has no return")
    final, base = returned["final"], value["base"]
    head = git.head(tree)
    ancestor = is_ancestor(tree, base, final)
    all_dirty = git.dirty(tree)
    preexisting = sorted(set(all_dirty).intersection(value["dirty_at_assign"]))
    dirty = sorted(set(all_dirty).difference(value["dirty_at_assign"]))
    committed = git.committed(tree, base, final) if ancestor else []
    outside = [
        {"path": path, "change": change}
        for change, paths in (("committed", committed), ("uncommitted", dirty))
        for path in paths
        if not any(covers(entry, path) for entry in value["write"])
    ]
    errors: list[AdvisoryError] = []
    checks: dict[str, dict[str, Any]] = {}

    def check(name: str, passed: bool, error: type[AdvisoryError], **facts: Any) -> None:
        checks[name] = {"status": "pass" if passed else "fail", **facts}
        if not passed:
            errors.append(error(f"assignment {value['id']}: {name} check failed"))

    check("return", returned["status"] == "completed", e.ReturnNotCompleted, returned=returned["status"])
    check("base", ancestor, e.BaseNotAncestor, base=base, final=final)
    check("head", head == final, e.HeadMoved, head=head, final=final)
    check("commit", final == base or value["commit"], e.CommitNotGranted)
    if value["commit"]:
        checks["commit"]["status"] = "not-applicable"
    checks["scope"] = {"status": ("fail" if outside else "pass") if ancestor else "not-run", "outside": outside}
    if ancestor and outside:
        details = [f"{item['path']} ({item['change']})" for item in outside[:20]]
        if len(outside) > 20:
            details.append(f"{len(outside) - 20} further paths")
        errors.append(e.ScopeViolation("returned work exceeds the write scope", *details))
    outcomes = {item["name"]: item["outcome"] for item in returned["checks"]}
    missing = [item["name"] for item in value["checks"] if item["name"] not in outcomes]
    not_passed = [
        {"name": item["name"], "outcome": outcomes[item["name"]]}
        for item in value["checks"]
        if item["name"] in outcomes and outcomes[item["name"]] != "pass"
    ]
    checks["checks"] = {
        "status": "fail" if missing or not_passed else "pass" if value["checks"] else "not-applicable",
        "missing": missing,
        "not_passed": not_passed,
    }
    if missing:
        errors.append(e.CheckOutcomeMissing("declared outcomes missing", *missing))
    if not_passed:
        errors.append(
            e.CheckNotPassed(
                "declared outcomes not passed", *(f"{item['name']}={item['outcome']}" for item in not_passed)
            )
        )
    children = [item["id"] for item in values.values() if item["parent"] == value["id"]]
    outstanding = [child for child in children if values[child]["status"] != "closed"]
    checks["children"] = {
        "status": "fail" if outstanding else "pass" if children else "not-applicable",
        "outstanding": outstanding,
    }
    if outstanding:
        errors.append(
            e.ChildrenOutstanding(
                "children must be closed before the parent returns", *outstanding, exit_code=ExitCode.FINDINGS
            )
        )
    notices: list[AdvisoryError] = []
    if preexisting:
        notices.append(e.PreexistingDirty("preexisting dirty paths are excluded", *preexisting))
    if value["commit"] and any(any(covers(entry, path) for entry in value["write"]) for path in dirty):
        notices.append(e.UncommittedChanges("in-scope changes are not contained in the final commit"))
    result = "pass" if all(item["status"] not in {"fail", "not-run"} for item in checks.values()) else "fail"
    return Result(
        {
            "id": value["id"],
            "result": result,
            "final": final,
            "checks": checks,
            "changed_paths": {"committed": committed, "uncommitted": dirty, "preexisting_dirty": preexisting},
        },
        notices,
        errors,
    )


def observe(root: Path, value: Assignment, values: dict[str, Assignment]) -> dict[str, Any] | None:
    if value["status"] == "closed":
        return None
    waiting_on = [key for key in value["depends_on"] if values[key]["status"] != "closed"]

    def degraded(state: str, attention: str) -> dict[str, Any]:
        return {
            "worktree_state": state,
            "head": None,
            "commits": None,
            "dirty": None,
            "waiting_on": waiting_on,
            "attention": [attention],
        }

    try:
        tree = git.require_worktree(root, Path(value["worktree"]))
    except e.WorktreeUnavailable:
        return degraded("missing", "worktree-missing")
    try:
        head = git.head(tree)
        ancestor = is_ancestor(tree, value["base"], head)
        dirty = len(set(git.dirty(tree)).difference(value["dirty_at_assign"]))
        commits = git.count(tree, value["base"], head)
    except (GitError, e.RevisionUnresolved):
        # An unborn HEAD or an unreachable base: report what is known and keep listing.
        return degraded("present", "worktree-unreadable")
    attention = []
    if not ancestor:
        attention.append("base-not-ancestor")
    if value["return"] and value["return"]["final"] != head:
        attention.append("head-moved")
    if value["status"] == "open" and head == value["base"] and dirty == 0:
        attention.append("no-changes")
    return {
        "worktree_state": "present",
        "head": head,
        "commits": commits,
        "dirty": dirty,
        "waiting_on": waiting_on,
        "attention": attention,
    }
