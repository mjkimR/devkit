"""Compact command output for agents (``devkit run``).

A command runs with its complete output in a log file; the caller gets its
outcome, recognized summaries (or the output's last lines) and warnings, the advisory blocks of nested
``devkit`` commands and, on failure, a head-and-tail excerpt, each within a
fixed budget. See ``docs/compact/overview.md``.
"""

from devkit.compact.errors import CommandNotStartedError, CompactError, LogDirectoryError, SlowCommandNotice
from devkit.compact.execute import CommandRun, default_log_dir, log_root, run_command
from devkit.compact.scan import Failure, Omitted, RelayedAdvisory, Scan, ToolWarning, scan

__all__ = [
    "CommandNotStartedError",
    "CommandRun",
    "CompactError",
    "Failure",
    "LogDirectoryError",
    "Omitted",
    "RelayedAdvisory",
    "Scan",
    "SlowCommandNotice",
    "ToolWarning",
    "default_log_dir",
    "log_root",
    "run_command",
    "scan",
]
