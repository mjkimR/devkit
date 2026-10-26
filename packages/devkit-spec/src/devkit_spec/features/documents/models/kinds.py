"""The document kinds and their definition table: one row per ``Kind`` member, the single source of each kind's facts.

``Kind`` is a declared enum, so static checks see every member
(``ADR-kind-definition-table-keyed-on-the-declared-kind-enum``). Each member has exactly one ``KindDefinition`` row,
in enum order, holding the facts the index, the spec rules and the entrypoint paths read: the ID prefix, the
directory under a docs root, Living Spec membership, area scoping, the ``RULE-spec-format`` scope, whether a first H1
carries an ID token, the summary requirement, whether ``entrypoints`` may be declared, the terminal statuses, the
fix-time default status and the relation fields that take the kind's IDs.

Consumers read the rows through ``definitions()`` and ``definition(kind)`` when they run, never through constants
bound at import, so an injected table changes their results; the ID grammar (``ids.PREFIXES``, ``ids.ID_SOURCE``)
is the one exception and is built from the rows at import. Path and stem grammars, unit anchors and the lifecycles
stay kind-specific code. The table is validated at import: a member without a row, a duplicated prefix or relation
field, or an inconsistent row raises ``KindTableError``.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum


class Kind(StrEnum):
    """What a document is, derived from its ID prefix."""

    CAPABILITY = "capability"
    USECASE = "usecase"
    ARCHITECTURE = "architecture"
    DECISION = "decision"
    PROPOSAL = "proposal"
    PROPOSAL_DECISION = "proposal-decision"
    SPEC = "spec"
    PLAN = "plan"
    TASKS = "tasks"
    RECONCILE = "reconcile"
    FEEDBACK = "feedback"
    MATERIAL = "material"
    MILESTONE = "milestone"


class Summary(StrEnum):
    """When ``RULE-document-summary`` requires a ``summary``."""

    ALWAYS = "always"
    ANCHOR = "anchor"  # only on the kind's anchor file (``KindDefinition.anchor``)
    NEVER = "never"


class FormatScope(StrEnum):
    """Where ``RULE-spec-format`` checks the kind's directory."""

    NONE = "none"
    GLOBAL = "global"  # ``docs/<directory>`` only
    EVERY_ROOT = "every-root"  # ``docs/<directory>`` and the same directory of every namespace docs root


class KindTableError(ValueError):
    """The kind definitions are inconsistent, or a consumer lacks a fact a kind needs: a defect in the code."""


@dataclass(frozen=True, slots=True)
class KindDefinition:
    """The facts of one kind. Every field is required, so a new row states each of them."""

    kind: Kind
    prefix: str
    directory: str  # the kind's directory under a docs root ("capabilities"), "" when it has none
    living_spec: bool  # its ID is the file stem and its directory is checked in every docs root
    area_scoped: bool  # stored under ``<directory>/<area>/`` with a matching ``area:`` field
    format_scope: FormatScope
    heading_token: bool  # ``RULE-id-convention`` reads a first-H1 ``[ID]`` token of this prefix
    summary: Summary
    anchor: str  # the anchor file name of an ``ANCHOR`` summary, "" otherwise
    entrypoints: bool  # documents of the kind may declare ``entrypoints``
    terminal_statuses: frozenset[
        str
    ]  # lower-cased statuses that settle a document (``ADR-terminal-statuses-are-historical``)
    default_status: str  # the status ``RULE-spec-format``'s fix writes
    relation_fields: tuple[str, ...]  # frontmatter relation fields that take this kind's IDs


_NONE: frozenset[str] = frozenset()
_PREFIX = re.compile(r"^[A-Z]+$")


ROWS: tuple[KindDefinition, ...] = (
    KindDefinition(
        Kind.CAPABILITY,
        "CAP",
        "capabilities",
        living_spec=True,
        area_scoped=True,
        format_scope=FormatScope.EVERY_ROOT,
        heading_token=True,
        summary=Summary.ALWAYS,
        anchor="",
        entrypoints=True,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=("capabilities", "related_capabilities"),
    ),
    KindDefinition(
        Kind.USECASE,
        "UC",
        "usecases",
        living_spec=True,
        area_scoped=True,
        format_scope=FormatScope.EVERY_ROOT,
        heading_token=True,
        summary=Summary.ALWAYS,
        anchor="",
        entrypoints=True,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=("usecases", "related_usecases"),
    ),
    KindDefinition(
        Kind.ARCHITECTURE,
        "ARCH",
        "architecture",
        living_spec=True,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=True,
        summary=Summary.ALWAYS,
        anchor="",
        entrypoints=False,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=(),
    ),
    KindDefinition(
        Kind.DECISION,
        "ADR",
        "decisions",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=True,
        summary=Summary.ALWAYS,
        anchor="",
        entrypoints=False,
        terminal_statuses=frozenset({"superseded"}),
        default_status="draft",
        relation_fields=(),
    ),
    KindDefinition(
        Kind.PROPOSAL,
        "PROP",
        "proposals",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.GLOBAL,
        heading_token=False,
        summary=Summary.ANCHOR,
        anchor="proposal.md",
        entrypoints=False,
        terminal_statuses=frozenset({"rejected"}),
        default_status="draft",
        relation_fields=(),
    ),
    KindDefinition(
        Kind.PROPOSAL_DECISION,
        "PADR",
        "",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=False,
        summary=Summary.NEVER,
        anchor="",
        entrypoints=False,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=(),
    ),
    KindDefinition(
        Kind.SPEC,
        "SPEC",
        "",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=True,
        summary=Summary.ANCHOR,
        anchor="spec.md",
        entrypoints=False,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=("spec",),
    ),
    KindDefinition(
        Kind.PLAN,
        "PLAN",
        "",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=True,
        summary=Summary.NEVER,
        anchor="",
        entrypoints=False,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=("plan",),
    ),
    KindDefinition(
        Kind.TASKS,
        "TASKS",
        "",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=True,
        summary=Summary.NEVER,
        anchor="",
        entrypoints=False,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=(),
    ),
    KindDefinition(
        Kind.RECONCILE,
        "REC",
        "",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=True,
        summary=Summary.NEVER,
        anchor="",
        entrypoints=False,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=(),
    ),
    KindDefinition(
        Kind.FEEDBACK,
        "FB",
        "",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=True,
        summary=Summary.NEVER,
        anchor="",
        entrypoints=False,
        terminal_statuses=frozenset({"resolved", "promoted", "dismissed", "forwarded"}),
        default_status="open",
        relation_fields=(),
    ),
    KindDefinition(
        Kind.MATERIAL,
        "MAT",
        "materials",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.NONE,
        heading_token=False,
        summary=Summary.NEVER,
        anchor="",
        entrypoints=False,
        terminal_statuses=_NONE,
        default_status="draft",
        relation_fields=(),
    ),
    KindDefinition(
        Kind.MILESTONE,
        "MS",
        "roadmap",
        living_spec=False,
        area_scoped=False,
        format_scope=FormatScope.GLOBAL,
        heading_token=True,
        summary=Summary.ALWAYS,
        anchor="",
        entrypoints=False,
        terminal_statuses=_NONE,
        default_status="planned",
        relation_fields=("milestone", "depends_on"),
    ),
)


def validate(rows: Sequence[KindDefinition]) -> tuple[KindDefinition, ...]:
    """``rows`` as a table: one row per ``Kind`` member in enum order, unique prefixes and relation fields, and
    rows whose facts agree. Raises ``KindTableError`` naming the first defect."""
    kinds = [row.kind for row in rows]
    if kinds != list(Kind):
        missing = [str(kind) for kind in Kind if kind not in kinds]
        raise KindTableError(
            f"the kind table must hold one row per Kind member in enum order; missing: {', '.join(missing) or '-'},"
            f" rows: {', '.join(str(kind) for kind in kinds)}"
        )
    prefixes: set[str] = set()
    fields: dict[str, Kind] = {}
    for row in rows:
        if not _PREFIX.match(row.prefix) or row.prefix in prefixes:
            raise KindTableError(f"kind {row.kind}: prefix {row.prefix!r} is not a unique upper-case word")
        prefixes.add(row.prefix)
        for name in row.relation_fields:
            if name in fields:
                raise KindTableError(f"relation field {name!r} is declared by both {fields[name]} and {row.kind}")
            fields[name] = row.kind
        if (row.summary is Summary.ANCHOR) != bool(row.anchor):
            raise KindTableError(f"kind {row.kind}: an anchor file is required exactly for an anchor-only summary")
        needs_directory = (
            row.living_spec or row.area_scoped or row.entrypoints or row.format_scope is not FormatScope.NONE
        )
        if needs_directory and not row.directory:
            raise KindTableError(
                f"kind {row.kind}: its Living Spec, area, entrypoints or format scope needs a directory"
            )
    return tuple(rows)


_TABLE: tuple[KindDefinition, ...] = validate(ROWS)


def definitions() -> tuple[KindDefinition, ...]:
    """The kind table in enum order, read when called."""
    return _TABLE


def definition(kind: Kind) -> KindDefinition:
    """The row of ``kind``; ``KindTableError`` when the table has none."""
    for row in _TABLE:
        if row.kind is kind:
            return row
    raise KindTableError(f"kind {kind} has no row in the kind table")


def by_prefix(value: str) -> KindDefinition | None:
    """The row whose prefix opens ``value`` as ``<PREFIX>-...``, whether or not the rest is a well-formed ID."""
    prefix, dash, _ = value.partition("-")
    if not dash:
        return None
    return next((row for row in _TABLE if row.prefix == prefix), None)


def relation_prefixes() -> dict[str, str]:
    """The ID prefix each relation field takes, with its dash: ``{"capabilities": "CAP-", ...}``."""
    return {name: f"{row.prefix}-" for row in _TABLE for name in row.relation_fields}
