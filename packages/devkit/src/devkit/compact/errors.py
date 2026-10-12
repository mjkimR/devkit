"""Errors and notices of ``devkit.compact``: ``AdvisoryError`` subclasses, one class per code.

Codes carry the ``RUN_`` prefix of the command agents call (``devkit run``),
not the module name.
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, Level, Retry


class CompactError(AdvisoryError):
    """Base class of every error raised by ``devkit.compact``; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class CommandNotStartedError(CompactError):
    """The command could not be started: it does not exist, or it is not executable (``INPUT_ERROR``)."""

    code = "RUN_COMMAND_NOT_STARTED"
    input_error = True
    fix = "Check the command name and the current directory; pass the command after `--`, as on a shell"


class SlowCommandNotice(CompactError):
    """The command ran longer than ``--slow-after`` (``NOTE``); returned with the result, never raised."""

    code = "RUN_SLOW_COMMAND"
    level = Level.NOTICE
