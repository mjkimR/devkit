"""Agent-first command-line boundary for click tools.

A tool built on ``devkit_cli`` reports like ``devkit`` does: results on stdout (``[KIND: ...]`` lines, or one JSON
object under ``--format json``), Agent Advisory Protocol blocks on stderr, exit codes ``0``/``1``/``2``, and the
same ``-q``/``-v``/``--strict`` options. It depends on ``click`` and ``devkit.advisory`` only and imports nothing
else. ``devkit_cli.testing`` (tests only) is not imported here.
"""

from devkit_cli.boundary import Boundary
from devkit_cli.lazy import LazyGroup
from devkit_cli.output import (
    FORMAT_OPTION,
    OutputSettings,
    Reported,
    echo_json,
    echo_notices,
    exit_on_problems,
    exit_on_warnings,
    highest_exit_code,
    is_json,
    output_settings,
    report_exit_code,
)

__all__ = [
    "FORMAT_OPTION",
    "Boundary",
    "LazyGroup",
    "OutputSettings",
    "Reported",
    "echo_json",
    "echo_notices",
    "exit_on_problems",
    "exit_on_warnings",
    "highest_exit_code",
    "is_json",
    "output_settings",
    "report_exit_code",
]
