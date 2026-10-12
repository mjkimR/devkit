"""Post-sync extension point.

Other packages register a callable under the ``devkit.post_sync`` entry-point
group. After a successful write (never on ``--dry-run`` or ``--check``) every
hook is called in sorted entry-point name order with the project root and the
sync result; the strings it returns become ``NOTICE`` lines. A hook cannot fail
the sync: the files are already on disk, so an exception becomes a notice too.
"""

from __future__ import annotations

from collections.abc import Callable
from importlib import metadata
from pathlib import Path

GROUP = "devkit.post_sync"

Hook = Callable[[Path, dict[str, object]], "list[str] | None"]


def run_post_sync(root: Path, result: dict[str, object]) -> list[str]:
    notices: list[str] = []
    for entry in sorted(metadata.entry_points(group=GROUP), key=lambda item: (item.name, item.value)):
        try:
            hook: Hook = entry.load()
            returned = hook(root, result)
        except Exception as exc:
            notices.append(f"post-sync hook {entry.name} failed: {exc}")
            continue
        if returned is None:
            continue
        if not isinstance(returned, list) or not all(isinstance(item, str) for item in returned):
            notices.append(
                f"post-sync hook {entry.name} failed: returned {type(returned).__name__}, expected list[str]"
            )
            continue
        notices.extend(returned)
    return notices
