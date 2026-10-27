"""Scaffold proposals: a bundle ``docs/proposals/PROP-<slug>/`` and the PADRs inside it.

A bundle holds ``proposal.md``, ``decisions/`` (``PADR-<slug>.md`` preliminary decisions), ``materials/`` and,
optionally, ``target-docs.md`` (the Living Spec blueprint). A proposal and a spec never share a slug, so a
handed-off ``PROP-<slug>`` maps to exactly one ``SPEC-<slug>``.

``proposal.md`` is the anchor of a devkit workflow unit: a new proposal is bound to workflow ``sdd-proposal`` when the
project has it. ``workflow`` records that binding. ``task_kind`` (``feature`` or ``bugfix``) is the
provisional ``task-kind`` the proposal is confirmed with at ``plan-accept``; the spec follows ``sdd-spec-<task_kind>``
after handoff. ``supersedes`` names the accepted proposal a close by supersede replaces, and ``needs_decompose: true``
marks a draft Backlog splits before Planning starts. ``namespace`` names the document namespace (``devkit_spec.features.documents.services.namespaces``) the bundle
belongs to; without it the bundle is global, and handoff carries it to ``spec.md``. ``summary`` is the one or two
English sentences ``RULE-document-summary`` requires of ``proposal.md``; handoff carries it to ``spec.md``, and a
PADR's ``summary`` stays in its promoted ADR.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml
from devkit.advisory import AdvisoryError
from devkit_agt.features.workflow import write_binding
from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import parse
from devkit_dist.features.project.models.invocation import AGENT_INVOCATION as DEVKIT

from devkit_spec.base.axes import (
    DEFAULT_EFFORT,
    DEFAULT_TASK_KIND,
    EFFORTS,
    PROPOSAL_WORKFLOW,
    TASK_KINDS,
)
from devkit_spec.base.errors import (
    ProposalDecisionExistsError,
    ProposalExistsError,
    ProposalInPlanningError,
    ProposalNotApprovedError,
    ProposalNotFoundError,
    ProposalSlugConflictError,
    ProposalSlugError,
    ProposalUnboundNotice,
    ProposalWorkflowError,
    SpecError,
)
from devkit_spec.base.units import PROPOSAL_FILE, PROPOSALS, TARGET_DOCS, proposal_unit
from devkit_spec.features.documents import DocumentIndex
from devkit_spec.features.documents.services.namespaces import detect, require
from devkit_spec.features.policy.repositories.branches import SLUG_LIMIT, planning_branch_elsewhere
from devkit_spec.features.policy.services.config import GLOBAL, read_spec_config
from devkit_spec.features.proposals.usecases.binding import resolve_binding, unbound_guidance
from devkit_spec.utils.text import foreign_letters

DECISIONS = "decisions"
MATERIALS = "materials"
DEFAULT_TARGET_AREA = "capabilities/<area>/"
_SUMMARY_LIMIT = 300

_UNSAFE = re.compile(r"[^a-zA-Z0-9_-]+")
_DASHES = re.compile(r"[_-]+")
_FIRST_SEGMENT_LETTER = re.compile(r"^[0-9]*[a-z]")


def clean_slug(raw: str) -> str:
    """``raw`` without a ``PROP-`` prefix or ``.md`` suffix, other characters than letters, digits, ``_`` and
    ``-`` collapsed to ``-``, outer dashes trimmed, lower-cased."""
    slug = raw.strip().removeprefix("PROP-").removesuffix(".md")
    return _UNSAFE.sub("-", slug).strip("-").lower()


def require_slug(raw: str, what: str = "slug") -> str:
    """``clean_slug(raw)``; ``ProposalSlugError`` when nothing is left."""
    slug = clean_slug(raw)
    if not slug:
        raise ProposalSlugError(f"{what} {raw!r} has no letter or digit", target_files=[raw])
    return slug


def new_slug(
    raw: str,
    what: str = "slug",
    error: type[SpecError] = ProposalSlugError,
    fix: str | None = None,
    limit: int | None = SLUG_LIMIT,
) -> str:
    """The slug of a new document: ``clean_slug(raw)`` with ``_`` written as ``-``.

    Raises ``error`` when nothing is left, when it is longer than ``limit`` (its activity branches
    ``plan-<slug>`` and ``dev-<slug>`` must fit devkit worktree's 64 characters when ``limit=SLUG_LIMIT``), or when
    the first segment has no letter: ``RULE-id-convention`` reads ``2024-budget`` as a retired number-based ID
    (``fix`` replaces the default directive then). Lookups of existing documents use ``require_slug``.
    """
    slug = _DASHES.sub("-", clean_slug(raw)).strip("-")
    if not slug:
        raise error(f"{what} {raw!r} has no letter or digit", target_files=[raw])
    if limit is not None and len(slug) > limit:
        raise error(
            f"{what} {slug!r} is {len(slug)} characters; at most {limit}, so its activity branches plan-<slug>"
            " and dev-<slug> fit 64 characters",
            target_files=[raw],
            fix=f"Pass a shorter {what}",
        )
    if not first_segment_has_letter(slug):
        raise error(
            f"{what} {raw!r} gives {slug!r}, whose first segment has no letter",
            target_files=[raw],
            fix=fix or f"Pass a {what} whose first word has a letter (for example budget-2024 instead of 2024-budget)",
        )
    return slug


def first_segment_has_letter(slug: str) -> bool:
    """Whether the first ``-`` segment of ``slug`` has a letter; ``RULE-id-convention`` reads ``2024-budget`` as the
    retired number-based ID ``2024``."""
    return _FIRST_SEGMENT_LETTER.match(slug) is not None


def yaml_scalar(value: str) -> str:
    """``value`` as a YAML scalar for a frontmatter line, quoted only when YAML needs it (``A: B`` titles)."""
    dumped = yaml.safe_dump(value, allow_unicode=True, width=10**6)
    return dumped.removesuffix("\n...\n").removesuffix("\n")


def require_task_kind(value: str | None) -> str:
    """``value`` (default ``feature``) when it is one of ``TASK_KINDS``; ``ArgumentError`` (``--task-kind``) otherwise."""
    kind = (value or "").strip() or DEFAULT_TASK_KIND
    if kind in TASK_KINDS:
        return kind
    raise ArgumentError(
        f"--task-kind {value!r} is not one of {' | '.join(TASK_KINDS)}",
        target_files=["--task-kind"],
        fix=f"Pass --task-kind {' or '.join(TASK_KINDS)}",
    )


def require_effort(value: str | None, option: str = "--planning-effort") -> str:
    """``value`` (default ``medium``) when it is one of ``EFFORTS``; ``ArgumentError`` (``option``) otherwise."""
    effort = (value or "").strip() or DEFAULT_EFFORT
    if effort in EFFORTS:
        return effort
    raise ArgumentError(
        f"{option} {value!r} is not one of {' | '.join(EFFORTS)}",
        target_files=[option],
        fix=f"Pass {option} {' | '.join(EFFORTS)}",
    )


def _supersedes(value: str | None, slug: str) -> str | None:
    """The ``PROP-<slug>`` ID a new proposal supersedes, ``None`` without one; ``ArgumentError`` for anything else or
    for the proposal's own ID (a superseding draft takes a new slug)."""
    if value is None:
        return None
    old = clean_slug(value)
    if value.strip().startswith("PROP-") and old and old != slug:
        return f"PROP-{old}"
    raise ArgumentError(
        f"--supersedes {value!r} must name another proposal as PROP-<slug>",
        target_files=["--supersedes"],
        fix="Pass --supersedes with the PROP- ID of the accepted proposal this draft replaces; the new draft takes a new slug",
    )


def _check_superseded(root: Path, proposal_id: str | None) -> None:
    """The proposal ``proposal_id`` (``PROP-<slug>``) a draft supersedes must exist and be ``accepted``: a supersede
    reverses its ``plan-accept`` (01 §7.4). ``ProposalNotFoundError`` without one, ``ProposalNotApprovedError`` for
    any other status; nothing for ``None``."""
    if proposal_id is None:
        return
    old = proposal_id.removeprefix("PROP-")
    bundle, single = bundle_dir(root, old), single_file(root, old)
    anchor = bundle / PROPOSAL_FILE if bundle.is_dir() else single
    rel = anchor.relative_to(root).as_posix()
    if not anchor.is_file():
        raise ProposalNotFoundError(
            f"--supersedes {proposal_id}: no proposal at {rel}",
            target_files=["--supersedes"],
            fix=f"Pass --supersedes the PROP- ID of the accepted proposal this draft replaces ({DEVKIT} spec list proposal"
            " shows them)",
        )
    try:
        status = str((parse(anchor.read_text("utf-8")).data or {}).get("status") or "")
    except (FrontmatterError, OSError, UnicodeError):
        status = ""
    if status != "accepted":
        raise ProposalNotApprovedError(
            f"--supersedes {proposal_id} is {status or 'without a status'}, not accepted; a supersede replaces an"
            " accepted proposal only",
            target_files=[rel],
            what_to_report="The status of the proposal --supersedes names; a supersede reverses an accepted direction",
            fix="Pass --supersedes the PROP- ID of an accepted proposal, or drop the option: a draft or reviewing"
            " proposal is changed in Backlog or its Planning, a rejected one is cleaned up by hygiene",
        )


def known_namespaces(root: Path) -> list[str]:
    """``global`` and the namespaces registered in the project at ``root`` (``SpecConfigError`` when malformed)."""
    return [GLOBAL, *(namespace.name for namespace in read_spec_config(root).namespaces)]


def bundle_namespace(root: Path, namespace: str | None, cwd: Path | None) -> tuple[str | None, str | None]:
    """The ``namespace`` field a new bundle gets (``None``: no field) and the namespace it reports.

    An explicit ``namespace`` must be ``global`` or registered in the project at ``root``. Without one, the bundle
    takes the namespace ``cwd`` lies in (``devkit_spec.features.documents.services.namespaces.detect``), none outside every package or without
    ``cwd``. The reported namespace is the field, else ``global`` in a project that registers namespaces, else
    ``None``. Raises ``ArgumentError`` (``--namespace``) for an unregistered name, and ``SpecConfigError`` for a
    malformed ``[tool.spec]`` table unless the name is ``global``.
    """
    if namespace == GLOBAL:
        return GLOBAL, GLOBAL
    namespaces = read_spec_config(root).namespaces
    if namespace is not None:
        written: str | None = require(namespaces, namespace)
    else:
        written = detect(namespaces, root, cwd) if cwd is not None else None
    return written, written or (GLOBAL if namespaces else None)


def require_summary(summary: str | None) -> str | None:
    """``summary`` stripped when it is non-empty English text of at most 300 characters; ``None`` when omitted.

    Raises ``ArgumentError`` (``--summary``) for an empty summary, one with a letter outside the Latin script, or
    one exceeding the default ``RULE-document-summary`` length limit.
    """
    if summary is None:
        return None
    text = summary.strip()
    letters = foreign_letters(text)
    if text and not letters:
        if len(text) <= _SUMMARY_LIMIT:
            return text
        problem = f"has {len(text)} characters; at most {_SUMMARY_LIMIT} are allowed"
    else:
        problem = f"contains {''.join(letters[:5])}, not English" if letters else "is empty"
    raise ArgumentError(
        f"--summary {problem}",
        target_files=["--summary"],
        fix=f"Pass --summary with one or two English sentences of at most {_SUMMARY_LIMIT} characters"
        " saying what the document defines",
    )


def bundle_dir(root: Path, slug: str) -> Path:
    return root / PROPOSALS / f"PROP-{slug}"


def single_file(root: Path, slug: str) -> Path:
    return root / PROPOSALS / f"PROP-{slug}.md"


def check_spec_conflict(index: DocumentIndex, slug: str) -> None:
    """Raise ``ProposalSlugConflictError`` when a document declares ``SPEC-<slug>`` as its ID or an alias.

    A broken document is a problem of the index, not a conflict, so it never blocks a proposal.
    """
    spec_id = f"SPEC-{slug}"
    found = index.declares(spec_id)
    if found:
        path = found[0].path
        raise ProposalSlugConflictError(
            f"{spec_id} already exists at {path}; a proposal and a spec cannot share a slug", target_files=[path]
        )


@dataclass
class CreatedProposal:
    """A scaffolded bundle: its ``id``, directory and ``proposal.md`` (workspace-relative), ``target-docs.md``
    when it was requested, the ``workflow`` ``proposal.md`` is bound to (``None``: unbound), and the scaffolded
    ``planning_effort`` and ``dev_effort`` hints."""

    id: str
    dir: str
    path: str
    target_docs: str | None
    workflow: str | None = None
    namespace: str | None = None
    planning_effort: str = DEFAULT_EFFORT
    dev_effort: str = DEFAULT_EFFORT
    notices: list[AdvisoryError] = field(default_factory=list)

    @property
    def next_command(self) -> str | None:
        return f"{DEVKIT} workflow next --unit {self.dir}" if self.workflow else None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "dir": self.dir,
            "path": self.path,
            "target_docs": self.target_docs,
            "workflow": self.workflow,
            "namespace": self.namespace,
            "planning_effort": self.planning_effort,
            "dev_effort": self.dev_effort,
            "next_command": self.next_command,
            "notices": [notice.to_dict() for notice in self.notices],
        }


def create_proposal(
    root: Path,
    slug: str,
    *,
    title: str | None = None,
    target_area: str | None = None,
    milestone: str | None = None,
    task_kind: str | None = None,
    planning_effort: str | None = None,
    dev_effort: str | None = None,
    namespace: str | None = None,
    summary: str | None = None,
    supersedes: str | None = None,
    decomposed_from: str | None = None,
    needs_decompose: bool = False,
    with_target_docs: bool = False,
    today: date | None = None,
    cwd: Path | None = None,
) -> CreatedProposal:
    """Compose the application entrypoint for internal callers."""
    return CreateProposalUseCase().execute(
        root,
        slug,
        title=title,
        target_area=target_area,
        milestone=milestone,
        task_kind=task_kind,
        planning_effort=planning_effort,
        dev_effort=dev_effort,
        namespace=namespace,
        summary=summary,
        supersedes=supersedes,
        decomposed_from=decomposed_from,
        needs_decompose=needs_decompose,
        with_target_docs=with_target_docs,
        today=today,
        cwd=cwd,
    )


def _proposal(
    slug: str,
    title: str,
    area: str,
    milestone: str,
    task_kind: str,
    namespace: str,
    summary: str,
    created: str,
    *,
    planning_effort: str = DEFAULT_EFFORT,
    dev_effort: str = DEFAULT_EFFORT,
    supersedes: str | None = None,
    decomposed_from: str | None = None,
    needs_decompose: bool = False,
) -> str:
    summary_line = (
        f"summary: {yaml_scalar(summary)}"
        if summary
        else "# summary: <one or two English sentences: what this proposal changes and why>"
    )
    namespace_line = f"namespace: {yaml_scalar(namespace)}\n" if namespace else ""
    milestone_line = f"milestone: {yaml_scalar(milestone)}\n" if milestone else ""
    planning_effort_line = f"planning_effort: {planning_effort:<20} # low | medium | high (hint for Planning)"
    dev_effort_line = f"dev_effort: {dev_effort:<25} # low | medium | high (hint for Development)"
    task_kind_line = f"task_kind: {task_kind:<26} # feature | bugfix: the spec follows sdd-spec-<task_kind>"
    supersedes_line = f"supersedes: {yaml_scalar(supersedes)}\n" if supersedes else ""
    supersedes_line += f"decomposed_from: {yaml_scalar(decomposed_from)}\n" if decomposed_from else ""
    decompose_line = (
        "needs_decompose: true                 # split in Backlog before Planning starts\n" if needs_decompose else ""
    )
    return f"""---
id: PROP-{slug}
title: {yaml_scalar(title)}
{summary_line}
status: draft                         # draft | reviewing | accepted | rejected
created_at: {created}
target_area: {yaml_scalar(area)}
{namespace_line}priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
{planning_effort_line}
{dev_effort_line}
{milestone_line}boundaries:
  owns:
    - {yaml_scalar(area)}
  excludes:
    - docs/decisions/
{task_kind_line}
{supersedes_line}{decompose_line}---

# [PROP-{slug}] {title}

## 1. Background & Hypothesis
<!-- Describe background, current challenges, and core hypothesis to address -->

## 2. Technical Spike Questions
<!-- Define key uncertainties and technical questions to answer -->
- **Q1**:
- **Q2**:

## 3. Proposed Design & Impact
<!-- Describe expected architectural design, CLI commands, and structural impact -->

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr {slug} "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept {slug} --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff {slug}.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
"""


def _target_docs(slug: str, title: str, created: str) -> str:
    return f"""---
id: PROP-{slug}-target
title: Target Living Spec Structure for PROP-{slug}
status: draft
proposal: PROP-{slug}
created_at: {created}
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets: []
---

# [Blueprint] PROP-{slug}: Target Living Spec Structure for {title}

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-{slug} is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets.

---

## 1. System Capabilities Plan (docs/capabilities/)

<Specify new, modified, or deprecated CAP documents, rationale, and key changes.>

---

## 2. Use Cases Plan (docs/usecases/)

<Specify new or modified UC documents, their scenarios and updated acceptance criteria.>

### Screens (docs/ux/)

<Only when the proposal changes what a person sees: one draft per screen, modal or panel in the ux template's shape
(ux-writing), with the use case step citations and docs/steering/ux-objects.md rows they need. Write IDs this proposal
creates as plain text. Drop this subsection otherwise.>

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

<Specify impacted ARCH documents and candidate ADRs (PADRs).>

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

<Specify new rules, workflows, skills, or CLI changes.>

---

## 5. System Before & After Comparison (Before & After)

<Compare As-Is and To-Be structures, optionally with Mermaid diagrams.>
"""


@dataclass(frozen=True)
class CreatedDecision:
    """A scaffolded PADR: its ``id``, path (workspace-relative) and the ``proposal`` it belongs to."""

    id: str
    path: str
    proposal: str

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "path": self.path, "proposal": self.proposal}


def _padr(padr_id: str, title: str, summary: str | None, slug: str, created: str) -> str:
    summary_line = (
        f"summary: {yaml_scalar(summary)}\n"
        if summary
        else "# summary: <English Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>\n"
    )
    return f"""---
id: {padr_id}
title: {yaml_scalar(title)}
{summary_line}proposal: PROP-{slug}
status: draft
created_at: {created}
---

# [{padr_id}] {title}

- **Status**: Draft
- **Date**: {created}

---

## 1. Context & Problem Statement

## 2. Decision Drivers

## 3. Considered Options

## 4. Decision Outcome

## 5. Consequences

## 6. Confirmation
"""


class CreateProposalUseCase(BaseUseCase):
    """Application entrypoint for create proposal."""

    def execute(
        self,
        root: Path,
        slug: str,
        *,
        title: str | None = None,
        target_area: str | None = None,
        milestone: str | None = None,
        task_kind: str | None = None,
        planning_effort: str | None = None,
        dev_effort: str | None = None,
        namespace: str | None = None,
        summary: str | None = None,
        supersedes: str | None = None,
        decomposed_from: str | None = None,
        needs_decompose: bool = False,
        with_target_docs: bool = False,
        today: date | None = None,
        cwd: Path | None = None,
    ) -> CreatedProposal:
        """Scaffold ``docs/proposals/PROP-<slug>/`` under the workspace ``root`` and bind ``proposal.md``.

        ``task_kind`` (default ``feature``), ``planning_effort`` (default ``medium``) and ``dev_effort`` (default
        ``medium``) are always written; ``summary`` only when given (without it, a commented placeholder line);
        ``supersedes`` (a ``PROP-<slug>`` ID) and ``needs_decompose`` only when given; ``namespace`` when given, else the
        namespace ``cwd`` lies in (``bundle_namespace``, reported on the result). Handoff resolves
        ``sdd-spec-<task_kind>``, carries the namespace and summary, and returns ``dev_effort`` without writing the effort
        hints to ``spec.md``. ``proposal.md`` is bound to ``sdd-proposal`` when it resolves and validates, else left
        unbound with a ``SPEC_PROPOSAL_UNBOUND`` notice. Raises ``ProposalSlugError`` for a slug without letters or
        digits, ``ArgumentError`` for a ``task_kind`` outside ``TASK_KINDS``, a ``planning_effort`` or ``dev_effort``
        outside ``EFFORTS``, a ``supersedes`` that is not a proposal ID, a ``namespace`` that is neither ``global`` nor
        registered or a ``summary`` that is empty, not English or longer than 300 stripped characters,
        ``ProposalNotFoundError`` for a ``supersedes`` naming no proposal and ``ProposalNotApprovedError`` for one that is not ``accepted``, ``ProposalExistsError`` when the
        bundle or a single-file proposal of the slug exists, ``ProposalSlugConflictError`` when ``SPEC-<slug>`` exists.
        """
        root = root.resolve()
        slug = new_slug(slug)
        namespace, reported = bundle_namespace(root, namespace, cwd)
        summary = require_summary(summary)
        kind = require_task_kind(task_kind)
        planning = require_effort(planning_effort, "--planning-effort")
        dev = require_effort(dev_effort, "--dev-effort")
        from devkit_spec.features.proposals.usecases.roadmap import decomposition_source, milestone_id

        milestone = milestone_id(root, milestone)
        decomposed_from = decomposition_source(root, decomposed_from, slug)
        replaced = _supersedes(supersedes, slug)
        _check_superseded(root, replaced)
        title = (title or "").strip() or slug
        area = (target_area or "").strip() or DEFAULT_TARGET_AREA
        area = area if area.endswith("/") else area + "/"
        bundle = bundle_dir(root, slug)
        for existing in (bundle, single_file(root, slug)):
            if existing.exists():
                rel = existing.relative_to(root).as_posix()
                raise ProposalExistsError(f"proposal PROP-{slug} already exists: {rel}", target_files=[rel])
        index = DocumentIndex.load(root)
        aliased = [document.path for document in index.by_alias.get(f"PROP-{slug}", [])]
        if aliased:
            raise ProposalExistsError(
                f"PROP-{slug} is already declared as an alias: {', '.join(aliased)}", target_files=aliased
            )
        check_spec_conflict(index, slug)
        binding, unbound = resolve_binding(
            root, None, PROPOSAL_FILE, default=PROPOSAL_WORKFLOW, error=ProposalWorkflowError
        )

        created = (today or date.today()).isoformat()
        (bundle / DECISIONS).mkdir(parents=True)
        (bundle / MATERIALS).mkdir()
        proposal = bundle / PROPOSAL_FILE
        text = _proposal(
            slug,
            title,
            area,
            (milestone or "").strip(),
            kind,
            namespace or "",
            summary or "",
            created,
            planning_effort=planning,
            dev_effort=dev,
            supersedes=replaced,
            decomposed_from=decomposed_from,
            needs_decompose=needs_decompose,
        )
        proposal.write_text(text, encoding="utf-8")
        if binding is not None:
            write_binding(proposal, binding)
        target_docs = None
        if with_target_docs:
            target_docs = bundle / TARGET_DOCS
            target_docs.write_text(_target_docs(slug, title, created), encoding="utf-8")
        result = CreatedProposal(
            id=f"PROP-{slug}",
            dir=bundle.relative_to(root).as_posix(),
            path=proposal.relative_to(root).as_posix(),
            target_docs=target_docs.relative_to(root).as_posix() if target_docs else None,
            workflow=binding.workflow if binding else None,
            namespace=reported,
            planning_effort=planning,
            dev_effort=dev,
        )
        if unbound is not None:
            fix, choices = unbound_guidance(root, result.dir, PROPOSAL_WORKFLOW)
            result.notices.append(
                ProposalUnboundNotice(
                    f"PROP-{slug} is not bound to a workflow: {PROPOSAL_WORKFLOW} is not available ({unbound.code})",
                    *choices,
                    target_files=[result.path],
                    fix=fix,
                )
            )
        return result


class CreateProposalDecisionUseCase(BaseUseCase):
    """Application entrypoint for create padr."""

    def execute(
        self,
        root: Path,
        slug: str,
        title: str,
        *,
        summary: str | None = None,
        padr_slug: str | None = None,
        today: date | None = None,
    ) -> CreatedDecision:
        """Scaffold ``decisions/PADR-<padr slug>.md`` in the bundle of proposal ``slug``.

        The PADR slug is ``padr_slug`` when given (a leading ``PADR-`` dropped), else the title's (``new_slug``); the
        title stays free text, so ``"2024 roadmap"`` works with ``padr_slug="roadmap-2024"``. ``summary`` is written only
        when given; the promoted ADR keeps it. Raises ``ProposalSlugError`` for a slug without letters or digits or a
        PADR slug whose first segment has no letter, ``ArgumentError`` for a ``summary`` that is empty, not English or
        longer than 300 stripped characters, ``ProposalNotFoundError`` when the bundle does not exist, ``ProposalInPlanningError`` when ``plan-<slug>`` exists
        and the checkout is not on it (a proposal in Planning is changed on that branch only, 01 §4.7),
        ``ProposalDecisionExistsError`` when any document already declares the PADR ID.
        """
        root = root.resolve()
        slug = require_slug(slug)
        summary = require_summary(summary)
        title = title.strip()
        if padr_slug is not None:
            padr_id = f"PADR-{new_slug(padr_slug.strip().removeprefix('PADR-'), '--slug', limit=None)}"
        else:
            padr_id = "PADR-" + new_slug(
                title,
                "title",
                fix="Pass --slug with a slug whose first word has a letter (for example --slug roadmap-2024), keeping the"
                " title as it is",
                limit=None,
            )
        bundle = bundle_dir(root, slug)
        if not bundle.is_dir():
            rel = bundle.relative_to(root).as_posix()
            raise ProposalNotFoundError(
                f"proposal bundle {rel} does not exist",
                target_files=[rel],
                fix=f"Create the bundle first with {DEVKIT} spec proposal new {slug}",
            )
        branch = planning_branch_elsewhere(root, slug)
        if branch is not None:
            rel = (bundle / PROPOSAL_FILE).relative_to(root).as_posix()
            raise ProposalInPlanningError(
                f"PROP-{slug} is in Planning on {branch}; a PADR is written on that branch only",
                target_files=[rel],
                fix=f"Run it in the checkout of {branch} ({DEVKIT} worktree start plan-{slug} --existing-branch {branch}"
                f" --unit {proposal_unit(slug)} attaches one), or wait until that branch is merged and removed",
            )
        path = bundle / DECISIONS / f"{padr_id}.md"
        existing = [document.path for document in DocumentIndex.load(root).declares(padr_id)]
        if path.exists() and path.relative_to(root).as_posix() not in existing:
            existing.append(path.relative_to(root).as_posix())
        if existing:
            raise ProposalDecisionExistsError(
                f"PADR ID {padr_id} already exists: {', '.join(existing)}", target_files=existing
            )
        created = (today or date.today()).isoformat()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_padr(padr_id, title, summary, slug, created), encoding="utf-8")
        return CreatedDecision(id=padr_id, path=path.relative_to(root).as_posix(), proposal=f"PROP-{slug}")
