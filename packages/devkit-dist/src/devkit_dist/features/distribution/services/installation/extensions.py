"""Post-sync extension point.

Other packages register a callable under the ``devkit.post_sync`` entry-point
group. After a successful write (never on ``--dry-run`` or ``--check``) every
extension is called in sorted entry-point name order as ``extension(root, result)``,
with the project root and the sync result as its JSON object
(``SyncResult.to_dict()``). It returns ``None`` or a list whose items become
notices: a string is a ``PostSyncNotice`` (``POST_SYNC_NOTICE``), an
``AdvisoryError`` is kept with its own code and level, except that an
``ERROR`` is lowered to ``WARNING``. An extension cannot fail the sync: the files are
already on disk, so an exception or a malformed return value becomes a
``PostSyncExtensionFailedNotice`` (``POST_SYNC_EXTENSION_FAILED``, a warning).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.core.extensions import run_extensions

from devkit_dist.features.distribution.models.errors import PostSyncExtensionFailedNotice, PostSyncNotice

GROUP = "devkit.post_sync"
# What each post-sync extension would change, for ``devkit sync --dry-run``; same signature, writes nothing.
PREVIEW_GROUP = "devkit.post_sync_preview"

Extension = Callable[[Path, dict[str, Any]], "list[str | AdvisoryError] | None"]


def _failed(name: str, problem: str) -> PostSyncExtensionFailedNotice:
    return PostSyncExtensionFailedNotice(
        f"post-sync extension {name} failed: {problem}",
        what_to_report=f"The failure of the {GROUP} entry point {name}; the sync itself succeeded",
    )


def run_post_sync(root: Path, result: dict[str, Any]) -> list[AdvisoryError]:
    """Call every registered extension; return the notices they produced, in entry-point name order."""
    return run_extensions(
        GROUP,
        lambda extension: extension(root, result),
        failed=_failed,
        notice=lambda line, name: PostSyncNotice(line, f"extension: {name}"),
    )


def run_post_sync_preview(root: Path, result: dict[str, Any]) -> list[AdvisoryError]:
    """Call every registered preview extension of a dry run; return the notices they produced, in name order."""
    return run_extensions(
        PREVIEW_GROUP,
        lambda extension: extension(root, result),
        failed=_failed,
        notice=lambda line, name: PostSyncNotice(line, f"extension: {name}"),
    )
