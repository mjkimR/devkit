"""Extension points: entry-point groups whose callables devkit runs after one of its commands succeeded.

A group (``devkit.post_sync``, ``devkit.post_finish``) holds callables, called extensions here, that devkit calls in
sorted entry-point name order once its command's work is done. An extension returns ``None`` or a list whose items
become notices: a string through the group's ``notice`` factory, an ``AdvisoryError`` kept with its own code and
level, except that an ``ERROR`` is lowered to ``WARNING``. An extension cannot fail the command, whose work is
already done: an exception or a malformed return value becomes the group's ``failed`` advisory (a warning).
"""

from __future__ import annotations

from collections.abc import Callable
from importlib import metadata

from devkit.advisory import AdvisoryError, Level

# Calls one loaded extension with the group's arguments and returns what it returned.
Invoke = Callable[[Callable[..., object]], object]


def run_extensions(
    group: str,
    invoke: Invoke,
    *,
    failed: Callable[[str, str], AdvisoryError],
    notice: Callable[[str, str], AdvisoryError],
) -> list[AdvisoryError]:
    """Call every extension of ``group``; return the notices they produced, in entry-point name order.

    ``failed(name, problem)`` builds the advisory for an extension that raised or returned something else than
    ``list[str | AdvisoryError]``; ``notice(line, name)`` the notice for a string an extension returned.
    """
    notices: list[AdvisoryError] = []
    for entry in sorted(metadata.entry_points(group=group), key=lambda item: (item.name, item.value)):
        try:
            returned = invoke(entry.load())
        except Exception as exc:
            notices.append(failed(entry.name, str(exc) or type(exc).__name__))
            continue
        if returned is None:
            continue
        if not isinstance(returned, list) or not all(isinstance(item, (str, AdvisoryError)) for item in returned):
            notices.append(
                failed(entry.name, f"returned {type(returned).__name__}, expected list[str | AdvisoryError]")
            )
            continue
        for item in returned:
            if isinstance(item, str):
                notices.append(notice(item, entry.name))
            else:
                notices.append(item.with_level(Level.WARNING) if item.level is Level.ERROR else item)
    return notices
