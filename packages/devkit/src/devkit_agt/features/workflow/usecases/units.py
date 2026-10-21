"""Creating and listing work units."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath

from devkit_core.base.errors import UnsafePathError
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core.paths import resolve_within

import devkit_agt.features.workflow.repositories.unit.frontmatter as frontmatter
from devkit_agt.features.workflow.models.binding import Binding
from devkit_agt.features.workflow.models.errors import (
    AnchorInvalidError,
    LayoutError,
    UnitDirNotEmptyError,
    UnitExistsError,
)
from devkit_agt.features.workflow.models.layout import TemplateLayout
from devkit_agt.features.workflow.repositories.layout import discover_units
from devkit_agt.features.workflow.repositories.unit.binding import read_anchor
from devkit_agt.features.workflow.repositories.unit.decisions import DECISIONS_DIR
from devkit_agt.features.workflow.repositories.unit.records import is_temporary, write_new_file
from devkit_agt.features.workflow.services.envelope import ENVELOPES_DIR
from devkit_agt.features.workflow.usecases.workspace import UnitRef, Workspace


class CreateUnitUseCase(BaseUseCase):
    """Execute the create unit operation."""

    def execute(
        self,
        ws: Workspace,
        slug: str,
        *,
        workflow: str | None = None,
        when: date | None = None,
        status: str = "planned",
    ) -> UnitRef:
        """Create a unit from the workflow's layout and bind it; ``workflow`` defaults to ``[workflow].default``.

        Raises ``SlugError`` (``SLUG_INVALID``) for a malformed slug and
        ``UnitExistsError`` (``UNIT_EXISTS``) when the unit already has an anchor
        (also when a concurrent call creates it first: the anchor is created
        exclusively and whole). An existing unit directory without an anchor is
        used, unless it holds leftover records (``decisions/*.yaml`` or
        ``envelopes/*.y[a]ml``), which would count in the new unit: that is a
        ``UnitDirNotEmptyError`` (``UNIT_DIR_NOT_EMPTY``). Other files
        (``.gitkeep``, notes, an empty ``envelopes/``) are left in place.
        A unit directory that resolves outside the layout's ``work_dir`` (through
        a symbolic link) is a ``LayoutError`` (``LAYOUT_INVALID``). A ``workflow``
        path outside the discovered definitions is a ``WorkflowNotBindableError``
        (``WORKFLOW_NOT_BINDABLE``), since the binding records only the id.
        """
        doc = ws.definition(workflow)
        ws.require_bindable(doc, workflow)
        day = when or date.today()
        layout = ws.layout_for(doc)
        anchor = ws.anchor_for(doc)
        rel = layout.new_unit(slug, day)
        unit_dir = _unit_dir(ws, layout, rel)
        exists = UnitExistsError(
            f"unit already exists: {rel.as_posix()}",
            fix="Choose another slug or continue the existing unit with `devkit workflow next --unit <dir>`",
        )
        # An anchor a concurrent `new` creates after this check fails the exclusive write below: UNIT_EXISTS as well.
        entries = {entry.name for entry in unit_dir.iterdir()} if unit_dir.is_dir() else set()
        if any((unit_dir / name).is_file() for name in {anchor, *ws.candidate_anchors()} & entries):
            raise exists
        leftovers = _leftover_records(unit_dir)
        if leftovers:
            raise UnitDirNotEmptyError(
                f"{rel.as_posix()} has no anchor but holds records that would count in the new unit",
                *leftovers,
                target_files=[f"{rel.as_posix()}/{name}" for name in leftovers],
                fix=(
                    f"Choose another slug, or move the decision records and envelopes out of {rel.as_posix()} "
                    "and run the command again"
                ),
            )
        unit_dir.mkdir(parents=True, exist_ok=True)
        binding = Binding(doc.id)
        data = {"id": slug, "status": status, "created": day, "workflow": binding.workflow}
        # Exclusive and whole: of two concurrent `new` calls for one slug, exactly one creates the anchor.
        if not write_new_file(unit_dir / anchor, frontmatter.render(data, f"# {slug}\n")):
            raise exists
        (unit_dir / ENVELOPES_DIR).mkdir(exist_ok=True)
        return UnitRef(unit_dir, anchor, binding, doc, rel.as_posix())


def _leftover_records(unit_dir: Path) -> list[str]:
    """The unit-relative ``decisions/*.yaml`` and ``envelopes/*.y[a]ml`` files in ``unit_dir``, sorted."""
    found: list[str] = []
    for directory, suffixes in ((DECISIONS_DIR, {".yaml"}), (ENVELOPES_DIR, {".yaml", ".yml"})):
        path = unit_dir / directory
        if path.is_dir():
            found += [
                f"{directory}/{entry.name}"
                for entry in path.iterdir()
                if entry.suffix in suffixes and not is_temporary(entry.name) and entry.is_file()
            ]
    return sorted(found)


def _unit_dir(ws: Workspace, layout: TemplateLayout, rel: PurePosixPath) -> Path:
    """``rel`` under the workspace root, refused unless it resolves inside the layout's ``work_dir``."""
    fix = (
        f"Replace the symbolic link on the path {rel.as_posix()} that leads outside {layout.work_dir} with a directory"
    )
    try:
        work_dir = resolve_within(ws.root, layout.work_dir)
        unit_dir = resolve_within(ws.root, rel)
    except UnsafePathError as exc:
        raise LayoutError(f"unit directory {rel.as_posix()}: {exc.message}", fix=fix) from exc
    if unit_dir == work_dir or not unit_dir.is_relative_to(work_dir):
        raise LayoutError(f"unit directory {rel.as_posix()} resolves outside {layout.work_dir}", fix=fix)
    return unit_dir


@dataclass(frozen=True)
class UnitInfo:
    """One discovered unit. ``error`` is set when its anchor could not be read."""

    unit: str
    anchor: str
    status: str | None
    binding: Binding
    error: AnchorInvalidError | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "unit": self.unit,
            "anchor": self.anchor,
            "status": self.status,
            "workflow": self.binding.workflow or None,
            "history": " ".join(h.workflow for h in self.binding.history) or None,
            "error": self.error.to_dict() if self.error is not None else None,
        }


def layouts_in_use(ws: Workspace) -> list[TemplateLayout]:
    """The project layout plus every distinct layout a discovered definition declares."""
    layouts: list[TemplateLayout] = [ws.layout]
    for doc in ws.definitions():
        layout = ws.layout_for(doc)
        if layout not in layouts:
            layouts.append(layout)
    return layouts


@dataclass(frozen=True)
class UnitListing:
    """Discovered units and the directories searched, including an empty result."""

    units: tuple[UnitInfo, ...]
    directories: tuple[str, ...]


class ListUnitsUseCase(BaseUseCase):
    """Execute the list units operation."""

    def execute(self, ws: Workspace, *, statuses: Iterable[str] = (), excluded: Iterable[str] = ()) -> UnitListing:
        """Units across every layout in use, sorted; ``statuses``/``excluded`` filter on the exact anchor status."""
        keep, drop = set(statuses), set(excluded)
        rows: dict[tuple[str, str], UnitInfo] = {}
        layouts = layouts_in_use(ws)
        for layout in layouts:
            for rel in discover_units(layout, ws.root):
                key = (rel.as_posix(), layout.anchor)
                if key in rows:
                    continue
                try:
                    state = read_anchor(ws.root / rel / layout.anchor, f"{key[0]}/{layout.anchor}")
                except AnchorInvalidError as exc:
                    rows[key] = UnitInfo(key[0], layout.anchor, None, Binding(), exc)
                    continue
                rows[key] = UnitInfo(key[0], layout.anchor, state.status or None, state.binding)
        ordered = [rows[k] for k in sorted(rows)]
        if keep:
            ordered = [row for row in ordered if (row.status or "") in keep]
        if drop:
            ordered = [row for row in ordered if (row.status or "") not in drop]
        return UnitListing(tuple(ordered), tuple(dict.fromkeys(layout.work_dir for layout in layouts)))
