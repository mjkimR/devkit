"""Hygiene extension point (``devkit.hygiene``): checks of repository state that are not file rules.

Other packages register a callable under the ``devkit.hygiene`` entry-point group. A whole-workspace ``devkit rules
check --phase hygiene`` calls every extension in sorted entry-point name order as ``extension(root)``, with the
workspace root, after the rules ran, and reports what they return with the run's notices: a string is a
``HygieneNotice`` (``HYGIENE_NOTICE``), an ``AdvisoryError`` keeps its code and level (an ``ERROR`` lowered to
``WARNING``). An extension never fails the run or changes its exit code (except as a warning under ``--strict``):
an exception or a malformed return value becomes a ``HygieneExtensionFailedNotice`` (``HYGIENE_EXTENSION_FAILED``,
a warning). The ``linter`` phase, explicit targets, Git snapshots (the commit gate, CI) and ``fix`` never run them.
``devkit_agt.features.worktree`` registers ``worktree-stale``, the stale activity branch report.
"""

from __future__ import annotations

from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.core.extensions import run_extensions

from devkit_agt.features.rules.models.errors import HygieneExtensionFailedNotice, HygieneNotice

HYGIENE_GROUP = "devkit.hygiene"


def _failed(name: str, problem: str) -> HygieneExtensionFailedNotice:
    return HygieneExtensionFailedNotice(
        f"hygiene extension {name} failed: {problem}",
        what_to_report=f"The failure of the {HYGIENE_GROUP} entry point {name}; the rules run itself completed",
    )


def run_hygiene_extensions(root: Path) -> list[AdvisoryError]:
    """Call every registered extension with ``root``; return the notices they produced, in entry-point name order."""
    return run_extensions(
        HYGIENE_GROUP,
        lambda extension: extension(root),
        failed=_failed,
        notice=lambda line, name: HygieneNotice(line, f"extension: {name}"),
    )
