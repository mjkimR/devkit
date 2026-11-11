"""Authority normalization independent of command transport."""

import re
from pathlib import Path
from typing import Any

from devkit_core.base.errors import ArgumentError
from devkit_docs.utils.paths import covers

from devkit_adaptive.base.errors import (
    AssignmentClosed,
    AssignmentUnknown,
    AuthorityNotNarrowed,
    NestingDepth,
    ScopeOverlap,
)
from devkit_adaptive.features.assignment.models.values import Assignment


def identifier(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", value):
        raise ArgumentError("assignment IDs must match [a-z0-9][a-z0-9-]{0,39}")
    return value


def assignment(values: dict[str, Assignment], value: str, *, mutable: bool = False) -> Assignment:
    identifier(value)
    if value not in values:
        raise AssignmentUnknown(f"unknown assignment {value}")
    result = values[value]
    if mutable and result["status"] == "closed":
        raise AssignmentClosed(f"assignment {value} is closed")
    return result


def scope(root: Path, values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        try:
            path = (root / value).resolve()
        except (OSError, RuntimeError) as exc:
            raise ArgumentError(f"write scope must be a resolvable path inside the worktree: {value}") from exc
        if not value or any(char in value for char in "*?[") or not path.is_relative_to(root):
            raise ArgumentError(f"write scope must be a literal path inside the worktree: {value}")
        entry = path.relative_to(root).as_posix()
        if entry not in result:
            result.append(entry)
    return result


def check_values(values: list[str], *, outcomes: bool = False) -> list[dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for value in values:
        name, separator, command = value.partition("=")
        if not name.strip() or (
            outcomes and (not separator or command not in {"pass", "fail", "skipped", "unavailable"})
        ):
            raise ArgumentError(f"invalid check: {value}")
        result[name] = {"name": name, "outcome" if outcomes else "command": command if separator else None}
    return list(result.values())


def authority(
    values: dict[str, Assignment], write: list[str], commit: bool, parent: str | None, depends: list[str]
) -> None:
    for dependency in depends:
        assignment(values, dependency)
    if parent:
        lead = assignment(values, parent, mutable=True)
        if lead["parent"]:
            raise NestingDepth("a child cannot delegate another level")
        if (commit and not lead["commit"]) or any(
            not any(covers(entry, path) for entry in lead["write"]) for path in write
        ):
            raise AuthorityNotNarrowed("child write scope and commit grant must fit the parent")
    for other in values.values():
        if other["status"] == "closed" or other["id"] == parent or other["id"] in depends:
            continue
        for mine in write:
            for theirs in other["write"]:
                if covers(mine, theirs) or covers(theirs, mine):
                    raise ScopeOverlap(
                        f"assignment {other['id']} holds overlapping scope", f"new: {mine}; other: {theirs}"
                    )
