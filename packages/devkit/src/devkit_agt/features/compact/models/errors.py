"""Errors and notices of ``devkit_agt.features.compact``: ``AdvisoryError`` subclasses, one class per code.

Codes carry the ``RUN_`` prefix of the command agents call (``devkit run``),
not the module name.
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, Level, Retry


class CompactError(AdvisoryError):
    """Base class of every error raised by ``devkit_agt.features.compact``; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class CommandNotStartedError(CompactError):
    """The command could not be started (``INPUT_ERROR``): there is none, it does not exist or is not
    executable, or its working directory does not exist or cannot be entered."""

    code = "RUN_COMMAND_NOT_STARTED"
    input_error = True
    fix = "Check the command name and the current directory; pass the command after `--`, as on a shell"


class LogDirectoryError(CompactError):
    """The log cannot be written (``INTERACTION``): the per-user log directory or the project's directory in it
    is a symlink, not a directory, or someone else's, or the log directory cannot be created or written (no
    permission, disk full)."""

    code = "RUN_LOG_DIR_INVALID"
    actor = Actor.USER
    what_to_report = "devkit run keeps its logs in a private directory that another user, a link or a file now occupies"


class SlowCommandNotice(CompactError):
    """The command ran longer than ``--slow-after`` (``NOTE``); returned with the result, never raised."""

    code = "RUN_SLOW_COMMAND"
    level = Level.NOTICE
