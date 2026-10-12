"""Post-sync extension point.

Other packages register a callable under the ``devkit.post_sync`` entry-point
group. After a successful write (never on ``--dry-run`` or ``--check``) every
hook is called in sorted entry-point name order as ``hook(root, result)``,
with the project root and the sync result as its JSON object
(``SyncResult.to_dict()``). It returns ``None`` or a list whose items become
notices: a string is a ``PostSyncNotice`` (``POST_SYNC_NOTICE``), an
``AdvisoryError`` is kept with its own code. A hook cannot fail the sync: the
files are already on disk, so an exception or a malformed return value becomes
a ``PostSyncHookFailedNotice`` (``POST_SYNC_HOOK_FAILED``).
"""

from __future__ import annotations

from collections.abc import Callable
from importlib import metadata
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit.distribution.errors import PostSyncHookFailedNotice, PostSyncNotice

GROUP = "devkit.post_sync"

Hook = Callable[[Path, dict[str, Any]], "list[str | AdvisoryError] | None"]


def _failed(name: str, problem: str) -> PostSyncHookFailedNotice:
    return PostSyncHookFailedNotice(
        f"post-sync hook {name} failed: {problem}",
        what_to_report=f"The failure of the {GROUP} entry point {name}; the sync itself succeeded",
    )


def run_post_sync(root: Path, result: dict[str, Any]) -> list[AdvisoryError]:
    """Call every registered hook; return the notices they produced, in hook order."""
    notices: list[AdvisoryError] = []
    for entry in sorted(metadata.entry_points(group=GROUP), key=lambda item: (item.name, item.value)):
        try:
            hook: Hook = entry.load()
            returned = hook(root, result)
        except Exception as exc:
            notices.append(_failed(entry.name, str(exc) or type(exc).__name__))
            continue
        if returned is None:
            continue
        if not isinstance(returned, list) or not all(isinstance(item, (str, AdvisoryError)) for item in returned):
            notices.append(
                _failed(entry.name, f"returned {type(returned).__name__}, expected list[str | AdvisoryError]")
            )
            continue
        notices.extend(
            item if isinstance(item, AdvisoryError) else PostSyncNotice(item, f"hook: {entry.name}")
            for item in returned
        )
    return notices
