"""Extension points: entry-point groups whose callables devkit runs, each isolated from the others.

``call_extensions`` is the one loop over an entry-point group: it calls every entry point of the group in sorted
``(name, value)`` order and isolates each one, so an entry point that fails to load, raises (``SystemExit``
included) or returns something its caller refuses becomes an ``ExtensionFailed`` outcome instead of stopping the
command; a failure to list the group at all is one ``ExtensionFailed`` named ``discovery``. ``KeyboardInterrupt``
and other ``BaseException`` subclasses still propagate. Each caller keeps its own error codes and messages: it maps
each failure to its own advisory, or raises on the first one.

``run_extensions`` serves the groups whose callables devkit calls after one of its commands succeeded
(``devkit.post_sync``, ``devkit.post_finish``). An extension returns ``None`` or a list whose items become notices:
a string through the group's ``notice`` factory, an ``AdvisoryError`` kept with its own code and level, except that
an ``ERROR`` is lowered to ``WARNING``. An extension cannot fail the command, whose work is already done: an
``AdvisoryError`` it raises is kept the same way, with an ``extension: <name>`` detail, and any other exception,
``SystemExit``, a failed discovery or a malformed return value becomes the group's ``failed`` advisory (a warning).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib import metadata

from devkit.advisory import AdvisoryError, Level

# Calls one loaded extension with the group's arguments and returns what it returned.
Invoke = Callable[[Callable[..., object]], object]

DISCOVERY = "discovery"  # the name of the failure to list a group's entry points


def problem(error: BaseException) -> str:
    """How an extension failure reads in a message: ``str(error)``, else the exception's type name."""
    return str(error) or type(error).__name__


@dataclass(frozen=True)
class ExtensionCalled[T]:
    """An entry point whose call returned ``result``."""

    entry: metadata.EntryPoint
    result: T

    @property
    def name(self) -> str:
        return self.entry.name


@dataclass(frozen=True)
class ExtensionFailed:
    """An entry point whose call raised ``error``; ``entry`` is ``None`` for a failed discovery (``name`` is then
    ``DISCOVERY``). ``problem`` is ``str(error)``, else the exception's type name."""

    name: str
    entry: metadata.EntryPoint | None
    error: BaseException

    @property
    def problem(self) -> str:
        return problem(self.error)


type ExtensionOutcome[T] = ExtensionCalled[T] | ExtensionFailed


def call_extensions[T](
    group: str, call: Callable[[metadata.EntryPoint], T], *, fail_fast: bool = False
) -> list[ExtensionOutcome[T]]:
    """Call ``call(entry)`` for every entry point of ``group`` in sorted ``(name, value)`` order; one outcome each.

    ``call`` loads the entry point (``entry.load()``), invokes it and validates what it returned, raising to refuse
    it; whatever it raises, ``Exception`` or ``SystemExit``, is that entry point's ``ExtensionFailed``. When the group
    cannot be listed the only outcome is an ``ExtensionFailed`` named ``DISCOVERY`` with no entry. With
    ``fail_fast`` the outcomes end at the first failure, so no later entry point is loaded.
    """
    try:
        entries = sorted(metadata.entry_points(group=group), key=lambda item: (item.name, item.value))
    except (Exception, SystemExit) as exc:
        return [ExtensionFailed(DISCOVERY, None, exc)]
    outcomes: list[ExtensionOutcome[T]] = []
    for entry in entries:
        try:
            outcomes.append(ExtensionCalled(entry, call(entry)))
        except (Exception, SystemExit) as exc:
            outcomes.append(ExtensionFailed(entry.name, entry, exc))
            if fail_fast:
                break
    return outcomes


def _notices(returned: object) -> list[str | AdvisoryError]:
    """What an extension returned, ``None`` as ``[]``; ``TypeError`` unless it is ``list[str | AdvisoryError]``."""
    if returned is None:
        return []
    if not isinstance(returned, list) or not all(isinstance(item, (str, AdvisoryError)) for item in returned):
        raise TypeError(f"returned {type(returned).__name__}, expected list[str | AdvisoryError]")
    return returned


def run_extensions(
    group: str,
    invoke: Invoke,
    *,
    failed: Callable[[str, str], AdvisoryError],
    notice: Callable[[str, str], AdvisoryError],
) -> list[AdvisoryError]:
    """Call every extension of ``group``; return the notices they produced, in entry-point name order.

    ``failed(name, problem)`` builds the advisory for an extension that raised (``SystemExit`` included) or
    returned something else than ``list[str | AdvisoryError]``, and for a group that cannot be listed (name
    ``discovery``); ``notice(line, name)`` the notice for a string an extension returned.
    """
    notices: list[AdvisoryError] = []
    for outcome in call_extensions(group, lambda entry: _notices(invoke(entry.load()))):
        if isinstance(outcome, ExtensionFailed):
            error = outcome.error
            if isinstance(error, AdvisoryError):
                raised = error.with_level(Level.WARNING if error.level is Level.ERROR else error.level)
                raised.details = (*raised.details, f"extension: {outcome.name}")
                notices.append(raised)
            else:
                notices.append(failed(outcome.name, outcome.problem))
            continue
        for item in outcome.result:
            if isinstance(item, str):
                notices.append(notice(item, outcome.name))
            else:
                notices.append(item.with_level(Level.WARNING) if item.level is Level.ERROR else item)
    return notices
