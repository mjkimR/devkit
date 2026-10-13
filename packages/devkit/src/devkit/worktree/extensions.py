"""Post-finish extension point (``devkit.post_finish``).

Other packages register a callable under the ``devkit.post_finish`` entry-point group. After ``devkit worktree
finish`` succeeded (the branch is merged, the worktree removed and the branch deleted as configured; never after a
refusal) every extension is called in sorted entry-point name order as ``extension(base, result)``, with the base checkout's
root and the finish result as its JSON object (``FinishResult.to_dict()``: ``slug``, ``path``, ``branch``,
``merged``, ``push``, ``removed``, ``branch_deleted``). An extension cleans up what its package keeps per task. It returns
``None`` or a list whose items become notices: a string is a ``PostFinishNotice`` (``POST_FINISH_NOTICE``), an
``AdvisoryError`` keeps its code and level, an ``ERROR`` lowered to ``WARNING``. An extension cannot fail the finish:
an exception or a malformed return value becomes a ``PostFinishExtensionFailedNotice`` (``POST_FINISH_EXTENSION_FAILED``,
a warning).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit.core.extensions import run_extensions
from devkit.worktree.errors import PostFinishExtensionFailedNotice, PostFinishNotice

GROUP = "devkit.post_finish"

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
