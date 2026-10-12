"""Check registry: reference syntax, classes, primitives and aliases."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

SKELETON_MARKER = "<!-- devkit:skeleton -->"
GATE_PREFIX = "gate:"


class CheckClass(StrEnum):
    DISK = "disk"  # evaluated from files in the unit directory (and git)
    LINT = "lint"  # evaluated by running agent-rule-engine
    RUNNER = "runner"  # an external runner; declared, never evaluated here
    HUMAN = "human"  # a person; declared, never evaluated here


DECLARABLE = (CheckClass.RUNNER, CheckClass.HUMAN)


@dataclass(frozen=True)
class Check:
    name: str
    class_: CheckClass
    description: str
    params: tuple[str, ...] = ()
    alias: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "class": self.class_.value,
            "description": self.description,
            "params": list(self.params),
            "alias": self.alias,
        }


@dataclass(frozen=True)
class Invocation:
    name: str
    args: tuple[str, ...] = ()

    def __str__(self) -> str:
        return self.name if not self.args else f"{self.name}({' '.join(self.args)})"


class CheckError(ValueError):
    """Malformed or unregistered check reference."""


# Primitive names
FILE_EXISTS = "file-exists"
FRONTMATTER = "frontmatter"
TASKS_CHECKED = "tasks-checked"
NOT_SKELETON = "not-skeleton"
ENVELOPE_COMPLETED = "envelope-completed"
ENVELOPE_CHECK_PASS = "envelope-check-pass"
REVISION_ANCESTOR = "revision-ancestor"
LINT_CLEAN = "lint-clean"

PRIMITIVES: tuple[Check, ...] = (
    Check(FILE_EXISTS, CheckClass.DISK, "the file exists in the unit directory", ("file",)),
    Check(FRONTMATTER, CheckClass.DISK, "the file's frontmatter field equals the value", ("file", "field", "value")),
    Check(TASKS_CHECKED, CheckClass.DISK, "the file has at least one task checkbox and no unchecked one", ("file",)),
    Check(NOT_SKELETON, CheckClass.DISK, f"the file is missing or has no line equal to {SKELETON_MARKER}", ("file",)),
    Check(
        ENVELOPE_COMPLETED,
        CheckClass.DISK,
        "the deciding envelopes/<kind>-NN.yaml is completed with no open findings",
        ("kind",),
    ),
    Check(
        ENVELOPE_CHECK_PASS,
        CheckClass.DISK,
        "the deciding envelopes/<kind>-NN.yaml is completed and checks.<key> starts with PASS",
        ("kind", "key"),
    ),
    Check(
        REVISION_ANCESTOR,
        CheckClass.DISK,
        "diff_scope.head of the latest <ancestor-kind> envelope is a git ancestor of (or equal to) that of the latest <descendant-kind> envelope",
        ("ancestor-kind", "descendant-kind"),
    ),
    Check(LINT_CLEAN, CheckClass.LINT, "agent-rule-engine reports no violation for files under the unit directory"),
)


def anchor_aliases(anchor: str) -> tuple[Check, ...]:
    return (
        Check(
            "anchor-exists", CheckClass.DISK, f"{anchor} exists in the unit directory", alias=f"{FILE_EXISTS}({anchor})"
        ),
        Check(
            "anchor-status-planned",
            CheckClass.DISK,
            f"{anchor} frontmatter status is planned",
            alias=f"{FRONTMATTER}({anchor} status planned)",
        ),
        Check(
            "anchor-status-in-progress",
            CheckClass.DISK,
            f"{anchor} frontmatter status is in-progress",
            alias=f"{FRONTMATTER}({anchor} status in-progress)",
        ),
        Check(
            "anchor-status-completed",
            CheckClass.DISK,
            f"{anchor} frontmatter status is completed",
            alias=f"{FRONTMATTER}({anchor} status completed)",
        ),
        Check(
            "tasks-exists", CheckClass.DISK, "tasks.md exists in the unit directory", alias=f"{FILE_EXISTS}(tasks.md)"
        ),
        Check(
            "tasks-all-checked",
            CheckClass.DISK,
            "tasks.md has at least one task and no unchecked task",
            alias=f"{TASKS_CHECKED}(tasks.md)",
        ),
        Check(
            "envelope-review-passed",
            CheckClass.DISK,
            "the latest review round (or the reverify closing it) is completed with no open findings",
            alias=f"{ENVELOPE_COMPLETED}(review)",
        ),
    )


def parse_check(text: str) -> Invocation:
    """Parse ``name`` or ``name(arg1 arg2 ...)``."""
    s = text.strip()
    open_idx = s.find("(")
    if open_idx < 0:
        if not s or any(c in s for c in ") \t"):
            raise CheckError(f"malformed check {text!r}")
        return Invocation(s)
    name = s[:open_idx]
    if not name or not s.endswith(")") or any(c in name for c in " \t"):
        raise CheckError(f"malformed check {text!r}")
    inner = s[open_idx + 1 : -1]
    if "(" in inner or ")" in inner:
        raise CheckError(f"malformed check {text!r}")
    args = tuple(inner.split())
    if not args:
        raise CheckError(f"malformed check {text!r}: empty argument list")
    return Invocation(name, args)


@dataclass
class Registry:
    """Built-in checks plus anchor aliases plus a workflow's declared runner/human checks."""

    checks: dict[str, Check] = field(default_factory=dict)

    @classmethod
    def build(cls, anchor: str, declared: tuple[Check, ...] = ()) -> Registry:
        reg = cls()
        for c in PRIMITIVES + anchor_aliases(anchor):
            reg.checks[c.name] = c
        for c in declared:
            if c.class_ not in DECLARABLE:
                raise CheckError(f"declared check {c.name!r} must be runner or human")
            if c.name in reg.checks:
                raise CheckError(f"declared check {c.name!r} collides with a built-in check")
            reg.checks[c.name] = c
        return reg

    def entries(self) -> list[Check]:
        return list(self.checks.values())

    def lookup(self, name: str) -> Check | None:
        return self.checks.get(name)

    def resolve(self, inv: Invocation) -> tuple[Invocation, Check]:
        """Validate against the registry and expand an alias to its primitive."""
        check = self.lookup(inv.name)
        if check is None:
            raise CheckError(f"unregistered check {inv.name!r} (see `agent-workflow checks`)")
        if check.alias:
            if inv.args:
                raise CheckError(f"check {inv.name!r} takes no arguments (it is an alias of {check.alias})")
            return self.resolve(parse_check(check.alias))
        if len(inv.args) != len(check.params):
            if not check.params:
                raise CheckError(f"check {inv.name!r} takes no arguments")
            raise CheckError(
                f"check {inv.name!r} expects {len(check.params)} argument(s) ({' '.join(check.params)}), got {len(inv.args)}"
            )
        return inv, check

    def resolve_name(self, text: str) -> tuple[Invocation, Check]:
        return self.resolve(parse_check(text))


def count_tasks(text: str) -> tuple[int, int]:
    """Return (checked, total) Markdown task checkboxes."""
    checked = total = 0
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped[:2] in {"- ", "* ", "+ "}:
            rest = stripped[2:]
        else:
            continue
        if rest.startswith("[ ] "):
            total += 1
        elif rest[:4].lower() == "[x] ":
            total += 1
            checked += 1
    return checked, total
