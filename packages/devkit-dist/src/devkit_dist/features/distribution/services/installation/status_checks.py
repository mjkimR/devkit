"""Load read-only project checks contributed by optional installed packages."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

from devkit.advisory import AdvisoryError, Level

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
    try:
        entries = sorted(metadata.entry_points(group=GROUP), key=lambda entry: (entry.name, entry.value))
    except (Exception, SystemExit) as exc:
        return [_failed("discovery", str(exc) or type(exc).__name__)]
    notices: list[AdvisoryError] = []
    for entry in entries:
        try:
            result = entry.load()(root)
            if not isinstance(result, (list, tuple)) or any(
                not isinstance(item, AdvisoryError) or item.level not in (Level.WARNING, Level.NOTICE)
                for item in result
            ):
                raise TypeError("expected a list or tuple of WARNING/NOTICE AdvisoryError values")
        except (Exception, SystemExit) as exc:
            notices.append(_failed(f"{entry.name} ({entry.value})", str(exc) or type(exc).__name__))
            continue
        notices.extend(result)
    return notices
