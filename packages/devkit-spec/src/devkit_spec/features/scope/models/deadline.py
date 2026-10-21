"""The deadline contract every registry operation runs under.

A command gets one ``Deadline`` (``[tool.spec.scope] timeout``): devkit's ``Deadline`` whose expiry raises
``ScopeTimeoutError``. The lock wait (``devkit_core.core.file_lock``) and each Git subprocess (``devkit_core.core.run_git``)
take the time that is left; a Git subprocess that outlives its share is killed, so a timed-out command ends within a
moment of its deadline.
"""

from __future__ import annotations

from devkit_core import core

from devkit_spec.base.errors import ScopeTimeoutError

JOURNAL_SECONDS = 5.0  # one journal append, independent of the operation's own deadline
ROLLBACK_SECONDS = 5.0  # removing a record whose token could not be saved, independent of the command's deadline


def timeout_error(what: str, seconds: float) -> ScopeTimeoutError:
    return ScopeTimeoutError(f"{what} exceeded the scope timeout of {seconds:g}s")


class Deadline(core.Deadline):
    """devkit's ``Deadline`` that raises ``ScopeTimeoutError`` (``SPEC_SCOPE_TIMEOUT``) when it runs out."""

    def __init__(self, seconds: float) -> None:
        super().__init__(seconds, error=timeout_error)
