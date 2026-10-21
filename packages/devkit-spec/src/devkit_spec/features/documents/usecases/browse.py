"""Document browsing selections, filters and metadata queries."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_spec.base.errors import ListStatusUnknownNotice
from devkit_spec.features.documents import Document, DocumentIndex, Kind, Reference
from devkit_spec.features.documents.services.namespaces import Selection, namespace_resolver, select
from devkit_spec.features.policy.repositories.branches import planning_branches
from devkit_spec.features.policy.services.config import Namespace, read_spec_config
from devkit_spec.utils.output import page
from devkit_spec.utils.paths import normalize, overlaps

_KIND_ORDER = {kind: position for position, kind in enumerate(Kind)}


SEVERITY_ORDER = ("critical", "blocked", "workaround", "noise")


PROPOSAL_FIELDS = ("task_kind", "planning_effort", "dev_effort")


FEEDBACK_FIELDS = ("severity", "scope", "target")


@dataclass(frozen=True)
class WhereItem:
    """One ``--where FIELD=A,B`` item: the frontmatter field, its accepted values lower-cased, the text given."""

    field: str
    values: frozenset[str]
    given: str


Where = tuple[WhereItem, ...]


@dataclass(frozen=True)
class NamespaceScope:
    """The namespaces of the workspace and the selection a browsing command applies."""

    namespaces: tuple[Namespace, ...]
    selection: Selection
    namespace_of: Callable[[Document], str]

    @classmethod
    def of(cls, index: DocumentIndex, name: str | None, every: bool) -> NamespaceScope:
        namespaces = read_spec_config(index.root).namespaces
        selection = select(namespaces, index.root, Path.cwd(), name, every)
        return cls(namespaces, selection, namespace_resolver(index, namespaces))

    def accepts(self, document: Document) -> bool:
        return self.selection.matches(self.namespace_of(document))

    def fields(self, document: Document) -> dict[str, str]:
        """``namespace=`` for text output, only in a workspace that has namespaces."""
        return {"namespace": self.namespace_of(document)} if self.namespaces else {}

    @staticmethod
    def args(name: str | None, every: bool) -> list[str]:
        return ["--namespace", name] if name is not None else ["--all-namespaces"] if every else []


def _where(given: tuple[str, ...]) -> Where:
    """Parse ``--where FIELD=A,B`` items; a missing ``=``, field or value is an ``ARGUMENT_INVALID``."""
    parsed: list[WhereItem] = []
    for item in given:
        field, equals, listed = item.partition("=")
        values = frozenset(part.strip().lower() for part in listed.split(",") if part.strip())
        if not equals or not field.strip() or not values:
            raise ArgumentError(
                f"--where {item}: expected FIELD=VALUE[,VALUE...]",
                target_files=["--where"],
                fix="Pass --where with a frontmatter field and at least one value, e.g. --where severity=critical",
            )
        parsed.append(WhereItem(field.strip(), values, item))
    return tuple(parsed)


def _field_values(value: object) -> set[str]:
    """The lower-cased texts a parsed frontmatter value matches: a scalar its text (a boolean ``true``/``false``, a
    date or timestamp its ISO 8601 form), a list the texts of its scalar elements; a mapping or ``null`` nothing."""
    if isinstance(value, list):
        return {text for element in value if not isinstance(element, list) for text in _field_values(element)}
    if value is None or isinstance(value, dict):
        return set()
    if isinstance(value, bool):
        return {"true" if value else "false"}
    if isinstance(value, date):
        return {value.isoformat().lower()}
    return {str(value).strip().lower()}


def _matches(document: Document, where: Where) -> bool:
    return all(_field_values(document.frontmatter.get(item.field)) & item.values for item in where)


def _severity_rank(document: Document) -> int:
    """The position of a feedback document's ``severity`` in ``SEVERITY_ORDER``; ``0`` for other kinds."""
    if document.kind is not Kind.FEEDBACK:
        return 0
    severity = _text(document.frontmatter.get("severity")).lower()
    return SEVERITY_ORDER.index(severity) if severity in SEVERITY_ORDER else len(SEVERITY_ORDER)


def _proposal_fields(document: Document) -> dict[str, str | None]:
    """``task_kind``, ``planning_effort`` and ``dev_effort`` of a proposal document (``None`` when absent); empty for
    other kinds."""
    if document.kind is not Kind.PROPOSAL:
        return {}
    return {name: _text(document.frontmatter.get(name)) or None for name in PROPOSAL_FIELDS}


def _feedback_fields(document: Document) -> dict[str, str | None]:
    """``severity``, ``scope`` and ``target`` of a feedback document (``None`` when absent); empty for other kinds."""
    if document.kind is not Kind.FEEDBACK:
        return {}
    return {name: _text(document.frontmatter.get(name)) or None for name in FEEDBACK_FIELDS}


def _text(value: object) -> str:
    return str(value).strip() if value is not None and not isinstance(value, (list, dict)) else ""


def _planning(index: DocumentIndex) -> dict[str, str]:
    """``slug -> plan-<slug> ref`` of the proposals whose Planning branch exists (``planning_branches``)."""
    return planning_branches(index.root)


def _shown_status(document: Document, planning: dict[str, str]) -> str:
    """The status ``list`` shows: a draft proposal whose ``plan-<slug>`` exists is ``reviewing`` (01 §5.1). Only the
    display changes; the base's ``status`` is not written."""
    if document.kind == Kind.PROPOSAL and document.status == "draft" and document.id.removeprefix("PROP-") in planning:
        return "reviewing"
    return document.status


def _planning_fields(document: Document, planning: dict[str, str]) -> dict[str, object]:
    """``status`` and ``planning_branch`` of a draft proposal shown as ``reviewing``; nothing for any other."""
    shown = _shown_status(document, planning)
    if shown == document.status:
        return {}
    return {"status": shown, "planning_branch": planning[document.id.removeprefix("PROP-")]}


def _unknown_statuses(index: DocumentIndex, wanted: set[Kind], requested: list[str]) -> list[AdvisoryError]:
    """``SPEC_LIST_STATUS_UNKNOWN`` for the requested statuses that no indexed document of the wanted kinds (every
    kind when none is wanted) carries, whatever its history or namespace; empty when each one occurs."""
    if not requested:
        return []
    known = {document.status.lower() for document in index.documents if not wanted or document.kind in wanted}
    known.discard("")
    unknown = [value for value in requested if value not in known]
    if not unknown:
        return []
    kinds = " or ".join(str(kind) for kind in sorted(wanted, key=_KIND_ORDER.__getitem__))
    fix = (
        f"Pass one of the statuses these documents carry: {', '.join(sorted(known))}"
        if known
        else "No document of these kinds carries a status; drop --status"
    )
    return [
        ListStatusUnknownNotice(
            f"--status {','.join(unknown)}: no {kinds + ' ' if kinds else ''}document carries "
            f"{'this status' if len(unknown) == 1 else 'these statuses'}; the filter was applied as given",
            target_files=["--status"],
            fix=fix,
        )
    ]


def _overlaps(document: Document, path: str) -> bool:
    """Whether one of the document's ``entrypoints`` is ``path``, under it, or a directory containing it."""
    entrypoints = document.frontmatter.get("entrypoints")
    if not isinstance(entrypoints, list):
        return False
    return any(isinstance(entry, str) and overlaps(entry, path) for entry in entrypoints)


def _tasks(root: Path, document: Document) -> str | None:
    """``<checked>/<total>`` of the ``tasks.md`` beside a spec, ``None`` for other kinds or without one."""
    if document.kind is not Kind.SPEC:
        return None
    tasks = root / document.path.rsplit("/", 1)[0] / "tasks.md"
    if not tasks.is_file():
        return None
    from devkit_agt.features.rules import count_tasks

    checked, total = count_tasks(tasks.read_text(encoding="utf-8", errors="replace"))
    return f"{checked}/{total}"


def parse_filter_options(where_items: tuple[str, ...], file: str | None) -> Where:
    """Validate document filters before loading the index."""
    where = _where(where_items)
    if file is not None:
        normalize(file)
    return where


def _check_page(limit: int, offset: int) -> None:
    if limit < 0 or offset < 0:
        raise ArgumentError(
            f"--limit {limit} --offset {offset}: must not be negative",
            target_files=["--limit", "--offset"],
            fix="Pass --limit 0 or more (0 returns every item) and --offset 0 or more",
        )


@dataclass(frozen=True)
class _RefGroup:
    """The references between the requested document and the document ``id`` (``None`` when no single document
    declares it)."""

    id: str
    document: Document | None
    references: list[Reference]

    @classmethod
    def of(cls, index: DocumentIndex, other: str, references: list[Reference]) -> _RefGroup:
        declared = index.by_id.get(other, [])
        return cls(other, declared[0] if len(declared) == 1 else None, references)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "path": self.document.path if self.document else None,
            "status": self.document.status if self.document else None,
            "references": [ref.to_dict() for ref in self.references],
        }


class ResolveDocumentsUseCase(BaseUseCase):
    """ResolveDocuments execution boundary."""

    def execute(
        self, root: Path, ids: tuple[str, ...]
    ) -> tuple[list[Document], list[AdvisoryError], Sequence[AdvisoryError]]:
        index = DocumentIndex.load(root)
        found: list[Document] = []
        errors: list[AdvisoryError] = []
        for document_id in ids:
            try:
                found.append(index.resolve(document_id))
            except AdvisoryError as error:
                errors.append(error)
        return found, errors, index.problems


class ReferenceDocumentsUseCase(BaseUseCase):
    """ReferenceDocuments execution boundary."""

    def execute(
        self, root: Path, document_id: str, direction: str, limit: int, offset: int
    ) -> tuple[Document, list[str], list[_RefGroup], Sequence[AdvisoryError]]:
        _check_page(limit, offset)
        index = DocumentIndex.load(root)
        document = index.resolve(document_id)
        groups = index.outgoing(document) if direction == "out" else index.incoming(document.id)
        keys = list(groups)
        shown = page(keys, offset, limit)
        items = [_RefGroup.of(index, key, groups[key]) for key in shown]
        return document, keys, items, index.problems


class ListDocumentsUseCase(BaseUseCase):
    """ListDocuments execution boundary."""

    def execute(
        self,
        root: Path,
        kinds: tuple[str, ...],
        status: str | None,
        area: str | None,
        query: str | None,
        file: str | None,
        history: bool,
        namespace: str | None,
        all_namespaces: bool,
        where_items: tuple[str, ...],
        offset: int,
        limit: int,
    ) -> tuple[
        list[Document],
        list[Document],
        dict[str, str | None],
        list[AdvisoryError],
        NamespaceScope,
        dict[str, str],
        Where,
        dict[str, bool],
    ]:
        _check_page(limit, offset)
        where = parse_filter_options(where_items, file)
        index = DocumentIndex.load(root)
        scope = NamespaceScope.of(index, namespace, all_namespaces)
        requested = (
            list(dict.fromkeys(part.strip().lower() for part in status.split(",") if part.strip())) if status else []
        )
        statuses = set(requested)
        wanted = {Kind(kind) for kind in kinds}
        planning = _planning(index)
        selected = [
            document
            for document in index.documents
            if (not wanted or document.kind in wanted)
            and (history or not index.is_historical(document))
            and (not statuses or _shown_status(document, planning).lower() in statuses)
            and (not area or area.lower() in document.area.lower())
            and (not query or query.lower() in document.id.lower() or query.lower() in document.title.lower())
            and _matches(document, where)
            and scope.accepts(document)
            and (file is None or _overlaps(document, file))
        ]
        selected.sort(
            key=lambda document: (_KIND_ORDER[document.kind], _severity_rank(document), document.id, document.path)
        )
        shown = page(selected, offset, limit)
        tasks = {document.path: _tasks(index.root, document) for document in shown}
        notices = [*index.problems, *_unknown_statuses(index, wanted, requested)]
        historical = {document.path: index.is_historical(document) for document in shown}
        return selected, shown, tasks, notices, scope, planning, where, historical
