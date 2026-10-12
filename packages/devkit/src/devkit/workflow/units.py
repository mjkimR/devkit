"""Creating and listing work units."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from devkit.core.errors import FrontmatterError
from devkit.workflow import frontmatter
from devkit.workflow.binding import Binding, binding_from
from devkit.workflow.definition import schema_hash
from devkit.workflow.envelope import ENVELOPES_DIR
from devkit.workflow.errors import input_error
from devkit.workflow.layout import TemplateLayout
from devkit.workflow.workspace import UnitRef, Workspace


def create_unit(
    ws: Workspace,
    slug: str,
    *,
    workflow: str | None = None,
    when: date | None = None,
    status: str = "planned",
) -> UnitRef:
    """Create a unit from the workflow's layout and bind it; ``workflow`` defaults to ``[workflow].default``."""
    doc = ws.definition(workflow)
    day = when or date.today()
    layout = ws.layout_for(doc)
    anchor = ws.anchor_for(doc)
    try:
        rel = layout.new_unit(slug, day)
    except ValueError as exc:
        raise input_error(str(exc), code="SLUG_INVALID", fix="Use lowercase letters, digits and hyphens") from exc
    unit_dir = ws.root / rel
    if any((unit_dir / name).is_file() for name in {anchor, *ws.candidate_anchors()}):
        raise input_error(
            f"unit already exists: {rel.as_posix()}",
            code="UNIT_EXISTS",
            fix="Choose another slug or continue the existing unit with `devkit workflow next --unit <dir>`",
        )
    unit_dir.mkdir(parents=True, exist_ok=True)
    (unit_dir / ENVELOPES_DIR).mkdir(exist_ok=True)
    binding = Binding(doc.id, schema_hash(doc))
    data = {"id": slug, "status": status, "created": day, "workflow": binding.workflow, "workflow_hash": binding.hash}
    (unit_dir / anchor).write_text(frontmatter.render(data, f"# {slug}\n"), "utf-8")
    return UnitRef(unit_dir.resolve(), anchor, binding, doc, rel.as_posix())


@dataclass(frozen=True)
class UnitInfo:
    """One discovered unit. ``error`` is set when its anchor could not be read."""

    unit: str
    anchor: str
    status: str | None
    binding: Binding
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "unit": self.unit,
            "anchor": self.anchor,
            "status": self.status,
            "workflow": self.binding.workflow or None,
            "workflow_hash": self.binding.hash or None,
            "history": " ".join(h.workflow for h in self.binding.history) or None,
            "error": self.error,
        }


def layouts_in_use(ws: Workspace) -> list[TemplateLayout]:
    """The project layout plus every distinct layout a discovered definition declares."""
    layouts: list[TemplateLayout] = [ws.layout]
    for doc in ws.definitions():
        layout = ws.layout_for(doc)
        if layout not in layouts:
            layouts.append(layout)
    return layouts


def list_units(ws: Workspace, *, statuses: Iterable[str] = (), excluded: Iterable[str] = ()) -> list[UnitInfo]:
    """Units across every layout in use, sorted; ``statuses``/``excluded`` filter on the exact anchor status."""
    keep, drop = set(statuses), set(excluded)
    rows: dict[tuple[str, str], UnitInfo] = {}
    for layout in layouts_in_use(ws):
        for rel in layout.discover(ws.root):
            key = (rel.as_posix(), layout.anchor)
            if key in rows:
                continue
            try:
                data = frontmatter.read(ws.root / rel / layout.anchor)
            except (FrontmatterError, OSError, UnicodeError) as exc:
                rows[key] = UnitInfo(key[0], layout.anchor, None, Binding(), str(exc))
                continue
            status = frontmatter.field(data, "status") or None
            rows[key] = UnitInfo(key[0], layout.anchor, status, binding_from(data))
    ordered = [rows[k] for k in sorted(rows)]
    if keep:
        ordered = [row for row in ordered if (row.status or "") in keep]
    if drop:
        ordered = [row for row in ordered if (row.status or "") not in drop]
    return ordered
