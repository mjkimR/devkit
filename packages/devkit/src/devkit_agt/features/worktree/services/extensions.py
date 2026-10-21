"""Extension points of ``devkit worktree``: ``devkit.post_finish``, ``devkit.finish_guard`` and ``devkit.attach_check``.

Other packages register a callable under the ``devkit.post_finish`` entry-point group. After ``devkit worktree
finish`` succeeded (the branch is merged, the worktree removed and the branch deleted as configured; never after a
refusal) every extension is called in sorted entry-point name order as ``extension(base, result)``, with the base checkout's
root and the finish result as its JSON object (``FinishResult.to_dict()``: ``slug``, ``path``, ``branch``,
``merged``, ``push``, ``removed``, ``branch_deleted``). An extension cleans up what its package keeps per task. It returns
``None`` or a list whose items become notices: a string is a ``PostFinishNotice`` (``POST_FINISH_NOTICE``), an
``AdvisoryError`` keeps its code and level, an ``ERROR`` lowered to ``WARNING``. An extension cannot fail the finish:
an exception or a malformed return value becomes a ``PostFinishExtensionFailedNotice`` (``POST_FINISH_EXTENSION_FAILED``,
a warning).

The two check groups run before a change and fail closed. ``devkit.finish_guard``: before ``finish --merge`` changes
anything, every extension is called as ``extension(base, branch, merge_base, tip)``, with the base checkout's root,
the activity branch, the commit id of its merge base with the base HEAD (empty when there is none) and its tip.
``devkit.attach_check``: before ``start --existing-branch`` changes anything, as ``extension(root, branch, unit,
tip)``, with the base checkout's root, the branch, the unit directory relative to that root and the commit id the
branch will be attached at; the files are read from ``tip`` (``git show <tip>:<unit>/...``), since no worktree may
exist yet. Either returns ``None`` or a list of strings, each a reason to refuse: any reason refuses the command
(``WORKTREE_BLOCKED``, ``WORKTREE_ATTACH_REFUSED``) with the reasons as details. An extension that raises, an
advisory included, or returns anything else refuses it too (``WORKTREE_GUARD_FAILED``,
``WORKTREE_ATTACH_CHECK_FAILED``): what it checks was not verified.
"""

from __future__ import annotations

from collections.abc import Callable
from importlib import metadata
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.core.extensions import run_extensions

from devkit_agt.features.worktree.models.errors import (
    AttachCheckFailedError,
    AttachRefusedError,
    BlockedError,
    GuardFailedError,
    PostFinishExtensionFailedNotice,
    PostFinishNotice,
)

GROUP = "devkit.post_finish"
FINISH_GUARD_GROUP = "devkit.finish_guard"
ATTACH_CHECK_GROUP = "devkit.attach_check"

Extension = Callable[[Path, dict[str, Any]], "list[str | AdvisoryError] | None"]


def _failed(name: str, problem: str) -> PostFinishExtensionFailedNotice:
    return PostFinishExtensionFailedNotice(
        f"post-finish extension {name} failed: {problem}",
        what_to_report=f"The failure of the {GROUP} entry point {name}; the finish itself succeeded",
    )


def run_post_finish(base: Path, result: dict[str, Any]) -> list[AdvisoryError]:
    """Call every registered extension; return the notices they produced, in entry-point name order."""
    return run_extensions(
        GROUP,
        lambda extension: extension(base, result),
        failed=_failed,
        notice=lambda line, name: PostFinishNotice(line, f"extension: {name}"),
    )


def _reasons(group: str, invoke: Callable[[Callable[..., object]], object]) -> tuple[list[str], list[str]]:
    """Call every extension of ``group``: the reasons they returned and the failures (``<name>: <problem>``)."""
    reasons: list[str] = []
    failures: list[str] = []
    for entry in sorted(metadata.entry_points(group=group), key=lambda item: (item.name, item.value)):
        try:
            returned = invoke(entry.load())
        except AdvisoryError as exc:
            failures.append(f"{entry.name}: ({exc.code}) {exc.message}")
            continue
        except Exception as exc:
            failures.append(f"{entry.name}: {str(exc) or type(exc).__name__}")
            continue
        if returned is None:
            continue
        if not isinstance(returned, list) or not all(isinstance(item, str) for item in returned):
            failures.append(f"{entry.name}: returned {type(returned).__name__}, expected list[str]")
            continue
        reasons.extend(f"{entry.name}: {item}" for item in returned)
    return reasons, failures


def run_finish_guards(base: Path, branch: str, merge_base: str, tip: str) -> None:
    """Refuse the merge of ``branch`` when a ``devkit.finish_guard`` extension objects or fails."""
    reasons, failures = _reasons(FINISH_GUARD_GROUP, lambda extension: extension(base, branch, merge_base, tip))
    if failures:
        raise GuardFailedError(
            f"a {FINISH_GUARD_GROUP} extension failed, so {branch} was not verified; nothing was changed",
            *failures,
        )
    if reasons:
        raise BlockedError(f"{branch} is blocked from integration; nothing was changed", *reasons)


def run_attach_checks(root: Path, branch: str, unit: str, tip: str) -> None:
    """Refuse attaching ``branch`` for ``unit`` when a ``devkit.attach_check`` extension objects or fails."""
    reasons, failures = _reasons(ATTACH_CHECK_GROUP, lambda extension: extension(root, branch, unit, tip))
    if failures:
        raise AttachCheckFailedError(
            f"a {ATTACH_CHECK_GROUP} extension failed, so {branch} and {unit} were not verified; nothing was changed",
            *failures,
        )
    if reasons:
        raise AttachRefusedError(f"{branch} and the unit {unit} do not correspond; nothing was changed", *reasons)
