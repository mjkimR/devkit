"""Discover existing work units using a workflow layout."""

from pathlib import Path, PurePosixPath

from devkit_agt.features.workflow.models.layout import TemplateLayout


def discover_units(layout: TemplateLayout, workspace_root: Path) -> list[PurePosixPath]:
    """Return sorted workspace-relative unit directories containing the configured anchor."""
    base = workspace_root / layout.work_dir
    if not base.is_dir():
        return []
    found: list[PurePosixPath] = []
    for candidate in base.glob(layout.discovery_glob()):
        if candidate.is_dir() and (candidate / layout.anchor).is_file():
            found.append(PurePosixPath(candidate.relative_to(workspace_root).as_posix()))
    return sorted(found)
