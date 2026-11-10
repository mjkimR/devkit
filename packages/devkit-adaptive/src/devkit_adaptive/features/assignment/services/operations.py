"""Assignment lifecycle policy inside one ledger transaction."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from devkit_core.base.errors import ArgumentError

from devkit_adaptive.base import errors as e
from devkit_adaptive.features.assignment.models.values import Assignment, Result, fold
from devkit_adaptive.features.assignment.repositories import git, governing
from devkit_adaptive.features.assignment.repositories.ledger import Ledger
from devkit_adaptive.features.assignment.services import validation, verification


def timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def read(root: Path, verb: str, options: dict[str, Any]) -> Result:
    events, notices, _ = Ledger(root).read()
    values = fold(events)
    if verb == "show":
        value = validation.assignment(values, options["id"])
        return Result({"assignment": value, "events": [item for item in events if item["id"] == value["id"]]}, notices)
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


def mutate(root: Path, verb: str, options: dict[str, Any]) -> Result:
    ledger = Ledger(root)
    with ledger.transaction():
        events, notices, end = ledger.read()
        values = fold(events)
        at = timestamp()
        if verb == "new":
            value = new(root, values, options, at)
            identifier, event, data = value["id"], "assigned", value
            result = Result({"assignment": value})
        else:
            identifier = options["id"]
            value = validation.assignment(values, identifier, mutable=True)
            match verb:
                case "return":
                    if options["status"] not in {"completed", "needs_input", "failed"}:
                        raise ArgumentError("--status must be completed, needs_input or failed")
                    final = options.get("final")
                    tree = git.require_worktree(root, Path(value["worktree"])) if final is None else root
                    data = {
                        "status": options["status"],
                        "final": git.revision(tree, final or "HEAD"),
                        "checks": validation.check_values(options.get("check", []), outcomes=True),
                        "unverified": options.get("unverified", []),
                        "summary": options.get("summary"),
                        "returned_at": at,
                    }
                    event = "returned"
                    result = Result({})
                case "verify":
                    result = verification.verify(root, value, values)
                    data = {
                        "result": result.payload["result"],
                        "final": result.payload["final"],
                        "checks": {key: check["status"] for key, check in result.payload["checks"].items()},
                        "verified_at": at,
                    }
                    event = "verified"
                case "close":
                    outstanding = [
                        item["id"]
                        for item in values.values()
                        if item["parent"] == identifier and item["status"] != "closed"
                    ]
                    if outstanding:
                        raise e.ChildrenOutstanding("children must be closed before their parent", *outstanding)
                    outcome, reason = options["outcome"], options.get("reason")
                    if outcome not in {"integrated", "abandoned"}:
                        raise ArgumentError("--outcome must be integrated or abandoned")
                    if not reason and (outcome == "abandoned" or value["status"] != "verified"):
                        raise ArgumentError("--reason is required for abandoned or unverified integration")
                    data = {"outcome": outcome, "reason": reason, "closed_at": at}
                    event = "closed"
                    result = Result({})
                    if outcome == "integrated" and value["status"] != "verified":
                        result.notices.append(
                            e.ClosedUnverified("assignment closed as integrated without passed verification")
                        )
                case _:
                    raise ValueError(verb)
        record = {"schema": 1, "at": at, "event": event, "id": identifier, "data": data}
        ledger.append(record, end)
        if verb not in {"new", "verify"}:
            result.payload = {"assignment": fold([*events, record])[identifier]}
        # The writer repaired the fragment before appending; the warning still describes this read.
        result.notices[:0] = notices
        return result


def new(root: Path, values: dict[str, Assignment], options: dict[str, Any], at: str) -> Assignment:
    number = len(values) + 1
    while f"a{number}" in values:
        number += 1
    identifier = validation.identifier(options.get("id") or f"a{number}")
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
        "base": git.revision(tree, options.get("base") or "HEAD"),
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
