"""Agent Advisory Protocol runtime.

Standard library only and free of import-time side effects: devkit imports this
module to read the bundled guide under ``bundle/``.
"""

from devkit.advisory.advisory import ACTION_TEXT, Advisory
from devkit.advisory.error import UNEXPECTED_CODE, AdvisoryError, AdvisoryFields, as_advisory_error, render_error
from devkit.advisory.types import ActionMode, Actor, ExitCode, Retry

__all__ = [
    "ACTION_TEXT",
    "UNEXPECTED_CODE",
    "ActionMode",
    "Actor",
    "Advisory",
    "AdvisoryError",
    "AdvisoryFields",
    "ExitCode",
    "Retry",
    "as_advisory_error",
    "render_error",
]
