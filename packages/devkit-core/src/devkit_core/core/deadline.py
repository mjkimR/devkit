"""A deadline several steps share: each step takes the time that is left.

A command starts one ``Deadline`` and passes it to every bounded step (``run_git(..., deadline=...)``,
``file_lock(..., deadline=...)``); running out raises the deadline's error, so the command ends within a
moment of its deadline whichever step was running. The error is ``DeadlineExceededError``
(``DEADLINE_EXCEEDED``) unless the caller gives the deadline an ``error`` factory of its own.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from devkit_core.base.errors import DeadlineExceededError

ErrorFactory = Callable[[str, float], BaseException]


def deadline_exceeded(what: str, seconds: float) -> DeadlineExceededError:
    """The default error of an expired deadline: ``<what> exceeded the deadline of <seconds>s``."""
    return DeadlineExceededError(f"{what} exceeded the deadline of {seconds:g}s", what=what, seconds=seconds)


class Deadline:
    """A point in monotonic time ``seconds`` after its creation.

    ``error(what, seconds)`` builds the exception an expiry raises (``exceeded``); without it the error is
    ``DeadlineExceededError``. A caller with its own code passes its factory, so ``check``, ``run_git`` and
    ``file_lock`` raise that code directly.
    """

    def __init__(self, seconds: float, *, error: ErrorFactory | None = None) -> None:
        self.seconds = seconds
        self.error = error
        self._end = time.monotonic() + seconds

    def remaining(self) -> float:
        """Seconds until the deadline; zero or negative once it has passed."""
        return self._end - time.monotonic()

    def expired(self) -> bool:
        return self.remaining() <= 0

    def exceeded(self, what: str) -> BaseException:
        """The error that reports ``what`` running out of this deadline (built, not raised)."""
        factory = self.error or deadline_exceeded
        return factory(what, self.seconds)

    def check(self, what: str) -> None:
        """Raise ``exceeded(what)`` when the deadline has passed; ``what`` names the step about to start."""
        if self.expired():
            raise self.exceeded(what)
