"""Load read-only project checks contributed by optional installed packages."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

from devkit.advisory import AdvisoryError, Level
from devkit_core.core.extensions import ExtensionFailed, call_extensions

from devkit_dist.features.distribution.models.errors import StatusCheckExtensionFailedNotice

GROUP = "devkit.status_checks"


def _failed(name: str, problem: str) -> AdvisoryError:
    return StatusCheckExtensionFailedNotice(
        f"status check {name} failed: {problem}",
        what_to_report=f"Report the failure of the {GROUP} entry point {name} to its package maintainer; "
        "core project status and other checks remain available",
    )


def status_check_notices(root: Path) -> list[AdvisoryError]:
    """Run each optional provider once in name/value order; isolate malformed results and provider failures.

    Providers accept the resolved project root and return a list or tuple of WARNING/NOTICE advisories.
    Validate the entire result before accepting any advisory, retaining its identity and result order.
    Interrupts propagate; an extension calling sys.exit() cannot conceal the core status report.
    """
    notices: list[AdvisoryError] = []
    for outcome in call_extensions(GROUP, lambda entry: _checked(entry, root)):
        if isinstance(outcome, ExtensionFailed):
            name = outcome.name if outcome.entry is None else f"{outcome.entry.name} ({outcome.entry.value})"
            notices.append(_failed(name, outcome.problem))
            continue
        notices.extend(outcome.result)
    return notices


def _checked(entry: metadata.EntryPoint, root: Path) -> list[AdvisoryError] | tuple[AdvisoryError, ...]:
    """What the provider ``entry`` returned for ``root``; ``TypeError`` unless every item is a WARNING or NOTICE."""
    result = entry.load()(root)
    if not isinstance(result, (list, tuple)) or any(
        not isinstance(item, AdvisoryError) or item.level not in (Level.WARNING, Level.NOTICE) for item in result
    ):
        raise TypeError("expected a list or tuple of WARNING/NOTICE AdvisoryError values")
    return result
