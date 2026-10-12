"""Evaluators of the ``disk`` primitives: one function per primitive name."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from devkit.core.errors import FrontmatterError
from devkit.rules import count_tasks
from devkit.workflow.definition.checks import (
    ENVELOPE_CHECK_PASS,
    ENVELOPE_COMPLETED,
    FILE_EXISTS,
    FRONTMATTER,
    NOT_SKELETON,
    REVISION_ANCESTOR,
    SKELETON_MARKER,
    TASKS_CHECKED,
)
from devkit.workflow.evaluation.git import is_revision
from devkit.workflow.unit import frontmatter
from devkit.workflow.unit.envelope import Envelopes

# ``(workspace_root, ancestor, descendant) -> bool``; raising means Git could not answer.
AncestorFunc = Callable[[Path, str, str], bool]


@dataclass(frozen=True)
class Outcome:
    satisfied: bool
    detail: str = ""
    evaluated: bool = True


@dataclass(frozen=True)
class PrimitiveContext:
    workspace_root: Path
    unit_dir: Path
    envelopes: Envelopes
    ancestor: AncestorFunc | None = None

    def read(self, name: str) -> str | None:
        try:
            return (self.unit_dir / name).read_text("utf-8")
        except (OSError, UnicodeError):
            return None


def file_exists(ctx: PrimitiveContext, args: tuple[str, ...]) -> Outcome:
    return Outcome((ctx.unit_dir / args[0]).exists())


def frontmatter_equals(ctx: PrimitiveContext, args: tuple[str, ...]) -> Outcome:
    file, fld, want = args
    text = ctx.read(file)
    if text is None:
        return Outcome(False, f"{file} missing")
    try:
        got = frontmatter.field(frontmatter.parse(text), fld)
    except FrontmatterError as exc:
        return Outcome(False, f"{file}: {exc}")
    return Outcome(got == want, f"{fld}={got or '-'}")


def not_skeleton(ctx: PrimitiveContext, args: tuple[str, ...]) -> Outcome:
    text = ctx.read(args[0])
    if text is None:
        return Outcome(True, f"{args[0]} missing")
    if any(line.strip() == SKELETON_MARKER for line in text.splitlines()):
        return Outcome(False, f"{args[0]} is a handoff skeleton")
    return Outcome(True)


def tasks_checked(ctx: PrimitiveContext, args: tuple[str, ...]) -> Outcome:
    text = ctx.read(args[0])
    if text is None:
        return Outcome(False, f"{args[0]} missing")
    checked, total = count_tasks(text)
    if total == 0:
        return Outcome(False, "no tasks")
    return Outcome(checked == total, f"{checked}/{total} checked")


def envelope_completed(ctx: PrimitiveContext, args: tuple[str, ...]) -> Outcome:
    env = ctx.envelopes.deciding(args[0])
    if env is None:
        return Outcome(False, f"no {args[0]} envelope")
    open_count = env.open_findings()
    return Outcome(
        env.status == "completed" and open_count == 0, f"{env.file} status={env.status} open_findings={open_count}"
    )


def envelope_check_pass(ctx: PrimitiveContext, args: tuple[str, ...]) -> Outcome:
    kind, key = args
    env = ctx.envelopes.deciding(kind)
    if env is None:
        return Outcome(False, f"no {kind} envelope")
    return Outcome(
        env.status == "completed" and env.check_pass(key),
        f"{env.file} status={env.status} {key}={env.checks.get(key, '')!r}",
    )


def revision_ancestor(ctx: PrimitiveContext, args: tuple[str, ...]) -> Outcome:
    """A failure to ask Git is reported as not evaluated, never as a definite answer."""
    heads: list[str] = []
    for kind in args:
        env = ctx.envelopes.latest(kind)
        if env is None:
            return Outcome(False, f"no {kind} envelope")
        if not env.diff_head:
            return Outcome(False, f"{env.file} has no diff_scope.head")
        if not is_revision(env.diff_head):
            return Outcome(False, f"{env.file} head {env.diff_head!r} is not a revision")
        heads.append(env.diff_head)
    if ctx.ancestor is None:
        return Outcome(False, "no git function configured", evaluated=False)
    try:
        ok = ctx.ancestor(ctx.workspace_root, heads[0], heads[1])
    except Exception as exc:
        return Outcome(False, f"git: {exc}", evaluated=False)
    return Outcome(ok, f"{heads[0]}..{heads[1]} ancestor={str(ok).lower()}")


EVALUATORS: dict[str, Callable[[PrimitiveContext, tuple[str, ...]], Outcome]] = {
    FILE_EXISTS: file_exists,
    FRONTMATTER: frontmatter_equals,
    NOT_SKELETON: not_skeleton,
    TASKS_CHECKED: tasks_checked,
    ENVELOPE_COMPLETED: envelope_completed,
    ENVELOPE_CHECK_PASS: envelope_check_pass,
    REVISION_ANCESTOR: revision_ancestor,
}


def evaluate_primitive(ctx: PrimitiveContext, name: str, args: tuple[str, ...]) -> Outcome:
    evaluator = EVALUATORS.get(name)
    if evaluator is None:
        return Outcome(False, "no evaluator", evaluated=False)
    return evaluator(ctx, args)
