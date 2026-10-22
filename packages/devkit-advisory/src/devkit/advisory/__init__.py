"""Agent Advisory Protocol runtime: errors, warnings and notices for AI agents.

Standard library only and free of import-time side effects. The protocol guides ship
separately, in the ``advisory`` bundle of ``devkit_dist.bundles.advisory``.
"""

from devkit.advisory.advisory import ACTION_TEXT, CONTINUATION, FIELDS, HEADLINE, Advisory
from devkit.advisory.error import (
    UNEXPECTED_CODE,
    AdvisoryError,
    AdvisoryFields,
    ArgumentError,
    as_advisory_error,
    render_error,
)
from devkit.advisory.types import ActionMode, Actor, ExitCode, Level, Retry

__all__ = [
    "ACTION_TEXT",
    "CONTINUATION",
    "FIELDS",
    "HEADLINE",
    "UNEXPECTED_CODE",
    "ActionMode",
    "Actor",
    "Advisory",
    "AdvisoryError",
    "AdvisoryFields",
    "ArgumentError",
    "ExitCode",
    "Level",
    "Retry",
    "as_advisory_error",
    "render_error",
]
