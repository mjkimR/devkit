"""Assignment lifecycle policy: one function per operation; each change is one event in one ledger transaction."""

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from devkit_core.base.errors import ArgumentError

from devkit_adaptive.base import errors as e
from devkit_adaptive.features.assignment.models.values import Assignment, Result, fold
from devkit_adaptive.features.assignment.repositories import git, governing
from devkit_adaptive.features.assignment.repositories.ledger import Ledger
from devkit_adaptive.features.assignment.services import validation, verification

# What an operation appends: the assignment ID, the event name, the event data and the operation's result.
type _Appended = tuple[str, str, dict[str, Any], Result]


def timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def show_assignment(root: Path, options: dict[str, Any]) -> Result:
    events, notices, _ = Ledger(root).read()
    value = validation.assignment(fold(events), options["id"])
    return Result({"assignment": value, "events": [item for item in events if item["id"] == value["id"]]}, notices)


def list_assignments(root: Path, options: dict[str, Any]) -> Result:
    events, notices, _ = Ledger(root).read()
    values = fold(events)
    assignments = [
        {**value, "observed": verification.observe(root, value, values)}
        for value in values.values()
        if options.get("all", False) or value["status"] != "closed"
    ]
    summary = {
        status: sum(item["status"] == status for item in assignments)
        for status in ("open", "returned", "verified", "rejected", "closed")
    }
    return Result({"assignments": assignments, "summary": summary}, notices)


def new_assignment(root: Path, options: dict[str, Any]) -> Result:
    def build(values: dict[str, Assignment], at: str) -> _Appended:
        value = _assigned(root, values, options, at)
        return value["id"], "assigned", value, Result({"assignment": value})

    return _append(root, build)


def return_assignment(root: Path, options: dict[str, Any]) -> Result:
    def build(values: dict[str, Assignment], at: str) -> _Appended:
        value = validation.assignment(values, options["id"], mutable=True)
        if options["status"] not in {"completed", "needs_input", "failed"}:
            raise ArgumentError("--status must be completed, needs_input or failed")
        final = options.get("final")
        # A given --final resolves in the assignment's worktree when present, else in this repository.
        try:
            tree = git.require_worktree(root, Path(value["worktree"]))
        except e.WorktreeUnavailable:
            if final is None:
                raise
            tree = root
        data = {
            "status": options["status"],
            "final": git.revision(tree, "HEAD" if final is None else final),
            "checks": validation.check_values(options.get("check", []), outcomes=True),
            "unverified": options.get("unverified", []),
            "summary": options.get("summary"),
            "returned_at": at,
        }
        return options["id"], "returned", data, Result({})

    return _append(root, build, refold=True)


def verify_assignment(root: Path, options: dict[str, Any]) -> Result:
    def build(values: dict[str, Assignment], at: str) -> _Appended:
        value = validation.assignment(values, options["id"], mutable=True)
        result = verification.verify(root, value, values)
        data = {
            "result": result.payload["result"],
            "final": result.payload["final"],
            "checks": {key: check["status"] for key, check in result.payload["checks"].items()},
            "verified_at": at,
        }
        return options["id"], "verified", data, result

    return _append(root, build)


def close_assignment(root: Path, options: dict[str, Any]) -> Result:
    def build(values: dict[str, Assignment], at: str) -> _Appended:
        identifier = options["id"]
        value = validation.assignment(values, identifier, mutable=True)
        outstanding = [
            item["id"] for item in values.values() if item["parent"] == identifier and item["status"] != "closed"
        ]
        if outstanding:
            raise e.ChildrenOutstanding("children must be closed before their parent", *outstanding)
        outcome, reason = options["outcome"], options.get("reason")
        if outcome not in {"integrated", "abandoned"}:
            raise ArgumentError("--outcome must be integrated or abandoned")
        if not reason and (outcome == "abandoned" or value["status"] != "verified"):
            raise ArgumentError("--reason is required for abandoned or unverified integration")
        result = Result({})
        if outcome == "integrated" and value["status"] != "verified":
            result.notices.append(e.ClosedUnverified("assignment closed as integrated without passed verification"))
        return identifier, "closed", {"outcome": outcome, "reason": reason, "closed_at": at}, result

    return _append(root, build, refold=True)


def _append(root: Path, build: Callable[[dict[str, Assignment], str], _Appended], *, refold: bool = False) -> Result:
    """Append the event ``build`` returns for the folded ledger, inside one ledger transaction.

    With ``refold`` the result's payload becomes the assignment folded with the new event. The read's notices lead.
    """
    ledger = Ledger(root)
    with ledger.transaction():
        events, notices, end = ledger.read()
        at = timestamp()
        identifier, event, data, result = build(fold(events), at)
        record = {"schema": 1, "at": at, "event": event, "id": identifier, "data": data}
        ledger.append(record, end)
        if refold:
            result.payload = {"assignment": fold([*events, record])[identifier]}
        # The writer repaired the fragment before appending; the warning still describes this read.
        result.notices[:0] = notices
        return result


def _assigned(root: Path, values: dict[str, Assignment], options: dict[str, Any], at: str) -> Assignment:
    number = len(values) + 1
    while f"a{number}" in values:
        number += 1
    identifier = validation.identifier(f"a{number}" if options.get("id") is None else options["id"])
    if identifier in values:
        raise e.AssignmentExists(f"assignment {identifier} already exists")
    tree = git.require_worktree(root, Path(options.get("worktree") or root))
    write = validation.scope(tree, options.get("write", []))
    depends = list(options.get("depends_on", []))
    parent, commit = options.get("parent"), options.get("commit", False)
    validation.authority(values, write, commit, parent, depends)
    return {
        "id": identifier,
        "status": "open",
        "owner": options["owner"],
        "role": options.get("role"),
        "goal": options["goal"],
        "worktree": str(tree),
        "base": git.revision(tree, "HEAD" if options.get("base") is None else options["base"]),
        "write": write,
        "commit": commit,
        "checks": validation.check_values(options.get("check", [])),
        "governing": governing.resolve(tree, options.get("governing", [])),
        "depends_on": depends,
        "parent": parent,
        "evidence": options.get("evidence"),
        "handoff": options.get("handoff"),
        "stop": options.get("stop"),
        "assigned_at": at,
        "dirty_at_assign": git.dirty(tree),
        "return": None,
        "verification": None,
        "close": None,
    }
