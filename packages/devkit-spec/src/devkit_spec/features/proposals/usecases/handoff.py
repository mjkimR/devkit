"""Hand an approved proposal off to a spec bundle and retire the proposal.

``handoff_proposal`` validates everything before it writes (slug, approval, slug conflict, workflow binding, every
path it would create), then:

1. writes ``specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`` with ``spec.md``, ``plan.md`` and ``tasks.md`` carried from the
   proposal body, each marked as a skeleton (``spec.md`` keeps the proposal's ``namespace``, which must be
   ``global`` or registered, and its ``summary``, which must be a string), and binds ``spec.md`` to
   ``sdd-spec-<task_kind>`` (the proposal's ``task_kind``, default ``feature``). A spec bound to ``sdd-spec-bugfix``
   gets ``spec.md`` only, with the proposal's target area and boundaries in its carried notes;
2. copies ``target-docs.md`` into the spec bundle;
3. promotes each ``decisions/PADR-<slug>.md`` to ``docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md`` as an accepted
   ``ADR-<slug>`` (its frontmatter, ``summary`` included, is kept);
4. moves open proposal ``feedback/*.md`` into the spec feedback directory; settled feedback follows generic extras.
   Moves ``materials/`` to ``docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`` when it holds a file other than
   operating-system junk (``JUNK_FILES``), together with every other file of the bundle that steps 1 to 3 do not
   carry (``notes.md``, a non-PADR file in ``decisions/``; junk aside), at its path relative to the bundle. Symbolic
   links are moved as links, never followed. When that directory already exists, the materials are merged into it
   per leaf (``_plan_materials``): every conflict is refused before the first write and no pre-existing path is ever
   moved, written or removed. The proposal unit's devkit workflow records (decision records and envelopes, as
   devkit's loaders find them) are not carried: they are dropped with the proposal;
5. rewrites links and ID references that pointed into the proposal (``rewrite``);
6. removes the proposal;
7. carries the proposal's ``gate:plan-intent`` and ``gate:plan-accept`` records to the spec under the same names
   (``proposal_gates``, ``_record_gates``), each with the note ``PROP-<slug>: <the proposal record's note>``: a carried
   approval is never turned into the approval of another decision.

A bundle bound to ``sdd-proposal`` hands off only with its effective accepted ``gate:plan-accept`` (the rule that
carries it), not on ``status: accepted`` alone (``ProposalAcceptanceUnrecordedError``); a single-file or unbound
proposal, which can carry no gate record, and one bound to another workflow keep the status-only rule.

A legacy proposal or PADR whose slug starts with a number (``PROP-2024-budget``) is refused: the ID it would become
breaks ``RULE-id-convention``. A failure of any kind in steps 1 to 4 removes what they wrote, moves what they moved
back and keeps the proposal; a directory still holding something that could not be moved back is kept and reported.
Across file systems step 4 copies and removes the sources only after every write succeeded. A single-file proposal
``docs/proposals/PROP-<slug>.md`` gets the plain skeleton (its body is not carried) and has no PADRs, materials or
blueprint.
"""

from __future__ import annotations

import filecmp
import os
import re
import shutil
import stat
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path
from typing import Any, NoReturn

from devkit.advisory import Actor, AdvisoryError
from devkit_agt.features.workflow import (
    Binding,
    Decision,
    Workspace,
    load_decisions,
    load_envelopes,
    new_decision,
    record_answer,
    write_decision,
)
from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import locate, parse
from devkit_dist.features.project.models.invocation import AGENT_INVOCATION as DEVKIT
from devkit_docs.features.documents import DocumentIndex, parse_document
from devkit_docs.features.documents.models.ids import is_legacy_id
from devkit_docs.features.documents.models.markdown import visible_lines
from devkit_docs.features.documents.models.model import Document
from devkit_docs.features.documents.models.namespace import GLOBAL
from devkit_docs.features.documents.services.dependencies import cycle_members, live_unit, target_problem

from devkit_spec.base.axes import (
    DEFAULT_TASK_KIND,
    DEFAULT_WORKFLOW,
    DEV_EFFORT,
    EFFORTS,
    PLANNING_EFFORT,
    PROPOSAL_WORKFLOW,
    TASK_KINDS,
    spec_workflow,
)
from devkit_spec.base.errors import (
    ProposalAcceptanceUnrecordedError,
    ProposalCleanupWarning,
    ProposalGateNotCarriedWarning,
    ProposalHandoffError,
    ProposalInvalidError,
    ProposalLinkUnresolvedWarning,
    ProposalNeedsDecomposeError,
    ProposalNotApprovedError,
    ProposalNotFoundError,
    ProposalReferencesRewrittenNotice,
    ProposalSlugError,
    ProposalTargetExistsError,
    ProposalUnboundNotice,
    ProposalWrongWorktreeError,
    acceptance_unrecorded_fix,
)
from devkit_spec.features.policy import require_sdd
from devkit_spec.features.policy.repositories.branches import require_development_branch
from devkit_spec.features.proposals.services.body import CarriedProposal, carry_proposal_body
from devkit_spec.features.proposals.services.history import rewrite_history
from devkit_spec.features.proposals.services.rewrite import (
    ID,
    RelocationPlan,
    RewriteReport,
    Rewritten,
    Unresolved,
    completed_bundles,
    markdown_files,
    rewrite_ids,
    rewrite_links,
    rewrite_paths,
)
from devkit_spec.features.proposals.usecases.binding import resolve_binding, unbound_guidance
from devkit_spec.features.proposals.usecases.feedback import plan_open_feedback
from devkit_spec.features.proposals.usecases.scaffold import (
    DECISIONS,
    MATERIALS,
    PROPOSAL_FILE,
    TARGET_DOCS,
    bundle_dir,
    check_spec_conflict,
    clean_slug,
    first_segment_has_letter,
    known_namespaces,
    require_slug,
    single_file,
)
from devkit_spec.features.proposals.usecases.specs import (
    SPEC_FILE,
    make_dirs,
    move_path,
    remove_paths,
    roll_back,
    spec_dir,
    spec_files,
    spec_only,
    text_value,
    text_values,
    write_spec_bundle,
)

TASK_KIND = "task_kind"
"""The proposal frontmatter key holding its ``task-kind``; the spec follows ``sdd-spec-<task_kind>`` after handoff
(``workflow`` is devkit's own binding of the proposal)."""
NEEDS_DECOMPOSE = "needs_decompose"
NAMESPACE = "namespace"
SUMMARY = "summary"
ACCEPTED = "accepted"
INTENT_GATE = "gate:plan-intent"
ACCEPT_GATE = "gate:plan-accept"
# The proposal's approvals the spec carries by name, in this order (handoff never re-labels them).
CARRIED_GATES = (INTENT_GATE, ACCEPT_GATE)
RETURN_PREFIX = "return:"

# Files an operating system leaves behind; never carried, they are deleted with the proposal.
JUNK_FILES = frozenset({".DS_Store", "Thumbs.db", "desktop.ini"})

# The collision kinds of a materials merge (``_plan_materials``), named in the refusal's fix.
DIFFERENT_CONTENT = "different-content"
FILE_DIRECTORY = "file-directory"
SYMBOLIC_LINK = "symbolic-link"
NON_REGULAR = "non-regular"
_RECONCILE = {
    DIFFERENT_CONTENT: "make the two files identical, or rename or move the proposal's copy",
    FILE_DIRECTORY: "rename or move the proposal's path",
    SYMBOLIC_LINK: "replace the symbolic link with a regular file or directory, or rename or move the proposal's path",
    NON_REGULAR: "replace the non-regular file with a regular file, or rename or move the proposal's path",
}

# A PADR ID by the document ID grammar (``ids.ID_SOURCE``): letters of either case, digits, ``_`` and ``-``.
_PADR = re.compile(r"\bPADR-[A-Za-z0-9][A-Za-z0-9_-]*")
# A frontmatter ``status: draft`` (or ``proposed``, plain or quoted); a trailing comment ("#" after whitespace) stays.
_DRAFT_STATUS = re.compile(
    r"""^status:[ \t]*(?:draft|proposed|"(?:draft|proposed)"|'(?:draft|proposed)')(?=[ \t]*\r?$|[ \t]+#)""",
    re.MULTILINE,
)
_DRAFT_BODY_STATUS = re.compile(r"(- \*\*Status\*\*:[ \t]*)(?:Draft|Proposed)[ \t]*")


@dataclass(frozen=True)
class PromotedDecision:
    """A PADR promoted to an ADR: the ADR's ``id`` and path (workspace-relative), and the PADR's ``padr`` ID."""

    id: str
    path: str
    padr: str

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "path": self.path, "padr": self.padr}


@dataclass(frozen=True)
class CarriedGate:
    """A gate of the spec the handoff recorded from the proposal: the ``request`` and its ``decision`` record's path
    (workspace-relative)."""

    request: str
    decision: str

    def to_dict(self) -> dict[str, object]:
        return {"request": self.request, "decision": self.decision}


@dataclass
class HandoffResult:
    """What a handoff wrote, moved and rewrote; paths are workspace-relative.

    ``workflow`` is the workflow ``spec.md`` is bound to (``None``: unbound), ``dev_effort`` the proposal's
    non-authoritative Development effort hint (``None`` when the proposal omitted it; never written to ``spec.md``),
    ``rewritten_files`` the files whose links or references changed, ``unresolved`` what pointed into the proposal and
    could not be mapped. ``materials_merged`` says whether the materials went into a ``materials`` directory that
    already existed, ``dropped_duplicates`` the files kept there whose byte-identical proposal copy was dropped.
    ``dropped_records`` are the proposal unit's workflow records removed with it, ``carried_gates`` the proposal's own
    approvals recorded in the spec under their names. ``notices`` are the warnings and notices the caller reports
    with the result.
    """

    proposal: str
    spec: str
    dir: str
    workflow: str | None
    dev_effort: str | None = None
    target_docs: str | None = None
    materials: str | None = None
    materials_merged: bool = False
    dropped_duplicates: list[str] = field(default_factory=list)
    decisions: list[PromotedDecision] = field(default_factory=list)
    dropped_records: list[str] = field(default_factory=list)
    carried_gates: list[CarriedGate] = field(default_factory=list)
    rewritten_files: list[str] = field(default_factory=list)
    rewritten: list[Rewritten] = field(default_factory=list)
    unresolved: list[Unresolved] = field(default_factory=list)
    notices: list[AdvisoryError] = field(default_factory=list)

    @property
    def next_command(self) -> str | None:
        return f"{DEVKIT} workflow next --unit {self.dir}" if self.workflow else None

    def to_dict(self) -> dict[str, object]:
        return {
            "proposal": self.proposal,
            "spec": self.spec,
            "dir": self.dir,
            "workflow": self.workflow,
            "dev_effort": self.dev_effort,
            "target_docs": self.target_docs,
            "materials": self.materials,
            "materials_merged": self.materials_merged,
            "dropped_duplicates": self.dropped_duplicates,
            "decisions": [decision.to_dict() for decision in self.decisions],
            "dropped_records": self.dropped_records,
            "carried_gates": [gate.to_dict() for gate in self.carried_gates],
            "rewritten_files": self.rewritten_files,
            "rewritten": [item.to_dict() for item in self.rewritten],
            "unresolved": [item.to_dict() for item in self.unresolved],
            "next_command": self.next_command,
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass(frozen=True)
class _Decision:
    padr: Path
    padr_id: str
    target: Path
    adr_id: str
    text: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Conflict:
    """A proposal path that cannot be merged onto ``destination``, and why (one of ``_RECONCILE``)."""

    source: Path
    destination: Path
    kind: str


@dataclass
class _MaterialsPlan:
    """How ``materials/`` and the carried extras reach the materials directory.

    ``moves`` are the ``materials/`` paths moved, ``(source, destination)``: ``materials/`` itself when the directory
    is new, else each absent subtree (``subtrees``, the destinations moved as directories) and each absent leaf.
    ``extras`` are the carried files moved, ``duplicates`` the ``(source, destination)`` pairs of byte-identical
    regular files left at the destination, the proposal copy dropped. Every destination was absent in preflight.
    """

    merged: bool = False
    moves: list[tuple[Path, Path]] = field(default_factory=list)
    subtrees: set[Path] = field(default_factory=set)
    extras: list[tuple[Path, Path]] = field(default_factory=list)
    duplicates: list[tuple[Path, Path]] = field(default_factory=list)


def _read(path: Path, root: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        rel = path.relative_to(root).as_posix()
        raise ProposalInvalidError(f"{rel} cannot be read: {exc}", target_files=[rel]) from exc


def handoff_proposal(root: Path, slug: str, *, today: date | None = None) -> HandoffResult:
    """Hand proposal ``slug`` off to a spec bundle under the workspace ``root`` (see the module docstring).

    Approval is ``status: accepted``, written once ``plan-accept`` was given; it is never inferred. The spec carries
    the proposal's own ``gate:plan-intent`` and ``gate:plan-accept`` records under their names; a failure there is a
    ``ProposalGateNotCarriedWarning``. Raises, before writing anything: ``ProposalSlugError`` (also for a
    proposal or PADR slug whose first segment has no letter), ``ProposalNotFoundError``, ``ProposalInvalidError``
    (also a ``task_kind`` outside ``TASK_KINDS`` or a ``planning_effort``/``dev_effort`` outside ``EFFORTS``),
    ``ProposalNotApprovedError``, ``ProposalAcceptanceUnrecordedError``, ``ProposalNeedsDecomposeError``,
    ``ProposalSlugConflictError``, ``ProposalWorkflowError``,
    ``ProposalTargetExistsError``, ``ProposalWrongWorktreeError`` (``_check_worktree``). A failure while writing
    removes what was written, moves the materials and carried files back and keeps the proposal, then raises
    ``ProposalHandoffError`` (with what the roll-back could not undo in its details), or the ``AdvisoryError``
    itself when the failure was one (such as a ``FrontmatterError`` binding ``spec.md``) and the roll-back was
    complete.
    """
    require_sdd(root)
    root = root.resolve()
    slug = require_slug(slug)
    _check_worktree(root, slug)
    day = today or date.today()
    bundle, single = bundle_dir(root, slug), single_file(root, slug)
    is_bundle = bundle.is_dir()
    if not is_bundle and not single.is_file():
        raise ProposalNotFoundError(f"proposal PROP-{slug} not found", target_files=[f"PROP-{slug}"])
    proposal_path = bundle / PROPOSAL_FILE if is_bundle else single
    proposal_rel = proposal_path.relative_to(root).as_posix()
    _require_lettered_slug(f"PROP-{slug}", slug, proposal_rel, "SPEC")
    text = _read(proposal_path, root)
    try:
        meta: dict[str, Any] = parse(text).data or {}
    except FrontmatterError as exc:
        raise ProposalInvalidError(f"{proposal_rel}: {exc.message}", target_files=[proposal_rel]) from exc

    status = text_value(meta.get("status")).lower()
    if status != ACCEPTED:
        raise ProposalNotApprovedError(
            f"proposal PROP-{slug} has status {status or '-'}; handoff needs accepted (given at plan-accept)",
            target_files=[proposal_rel],
        )
    if meta.get(NEEDS_DECOMPOSE) is True:
        raise ProposalNeedsDecomposeError(
            f"proposal PROP-{slug} is marked {NEEDS_DECOMPOSE}: true; it is split in Backlog, never handed off",
            target_files=[proposal_rel],
        )
    gates = proposal_gates(bundle, text_value(meta.get("workflow"))) if is_bundle else []
    if (
        is_bundle
        and text_value(meta.get("workflow")) == PROPOSAL_WORKFLOW
        and ACCEPT_GATE not in {gate.request for gate in gates}
    ):
        raise ProposalAcceptanceUnrecordedError(
            f"proposal PROP-{slug} is accepted but has no effective accepted {ACCEPT_GATE} record; the handoff needs"
            " the user's recorded acceptance",
            target_files=[proposal_rel],
            fix=acceptance_unrecorded_fix(slug),
        )
    namespace = _namespace(root, meta, proposal_rel)
    summary = _summary(meta, proposal_rel)
    kind = _task_kind(meta, proposal_rel)
    _effort(meta, PLANNING_EFFORT, proposal_rel)
    dev_effort = _effort(meta, DEV_EFFORT, proposal_rel)
    index = DocumentIndex.load(root)
    source = next((d for d in index.documents if d.path == proposal_rel), None)
    if source is None:
        raise ProposalInvalidError(
            f"proposal has no valid id; its frontmatter must carry id: PROP-{slug}",
            target_files=[proposal_rel],
            fix=f"Set id: PROP-{slug} in the frontmatter of {proposal_rel}, then rerun the handoff",
        )
    if any("depends_on" in issue.message for issue in source.issues):
        raise ProposalInvalidError(
            "proposal depends_on must be a list of string anchor IDs", target_files=[proposal_rel]
        )
    check_spec_conflict(index, slug)
    # The default task-kind binds like no field: a project without its workflow gets an unbound spec and a notice.
    explicit = spec_workflow(kind) if kind and kind != DEFAULT_TASK_KIND else None
    binding, unbound = resolve_binding(root, explicit, proposal_rel, field=TASK_KIND)

    month, stamp = day.strftime("%Y-%m"), day.strftime("%Y%m%d")
    target_dir = spec_dir(root, slug, day)
    targets: list[Path] = [target_dir]
    materials_dir = bundle / MATERIALS
    move_materials = is_bundle and _has_material(materials_dir)
    materials_target: Path | None = None
    target_docs_text: str | None = None
    decisions: list[_Decision] = []
    extras: list[tuple[Path, Path]] = []
    feedback: list[tuple[Path, Path]] = []
    records: list[Path] = []
    if is_bundle:
        if (bundle / TARGET_DOCS).is_file():
            target_docs_text = _read(bundle / TARGET_DOCS, root)
        decisions = _plan_decisions(root, bundle / DECISIONS, month, stamp)
        targets += [decision.target for decision in decisions]
        records = _unit_records(bundle)
        preserved = root / "docs" / MATERIALS / month / f"{stamp}-{slug}"
        feedback = plan_open_feedback(root, bundle, target_dir)
        extras = _plan_extras(
            root, bundle, decisions, records + [source for source, _ in feedback], preserved, move_materials
        )
        if move_materials or extras:
            materials_target = preserved
            if not os.path.lexists(preserved):
                targets.append(materials_target)  # an existing one is merged into (_plan_materials)
    spec_aliases = tuple(f"SPEC-{alias.removeprefix('PROP-')}" for alias in source.aliases)
    legacy = [alias for alias in spec_aliases if is_legacy_id(alias)]
    if legacy:
        raise ProposalInvalidError(
            f"proposal aliases would become date-based spec aliases: {', '.join(legacy)}",
            target_files=[proposal_rel],
            fix="Remove the dated alias from the proposal's aliases (a SPEC- ID never carries a date), then rerun the"
            " handoff",
        )
    _check_targets(root, index, targets, decisions, [f"SPEC-{slug}", *spec_aliases])
    # Merge conflicts first: a symbolic link inside an existing materials directory is a conflict, not a path outside.
    materials = (
        _plan_materials(root, materials_dir, materials_target, move_materials, extras)
        if materials_target is not None
        else _MaterialsPlan()
    )
    for destination in [*targets, *(destination for _, destination in extras + feedback)]:
        _require_inside(root, destination)

    title = text_value(meta.get("title")) or slug
    materials_ref = (
        f"\n- **Preserved Materials**: `{materials_target.relative_to(root).as_posix()}`" if materials_target else ""
    )
    target_docs_ref = (
        f"\n- Target Docs Blueprint: {_target_docs_reference(target_docs_text)} "
        "(Living Spec targets for this plan and reconcile.md)"
        if target_docs_text is not None
        else ""
    )
    carried = carry_proposal_body(text) if is_bundle else CarriedProposal()
    bugfix = spec_only(binding)
    if bugfix:
        # No plan.md: what it would hold from the proposal is carried in spec.md's notes.
        carried.notes += _scope_notes(meta)
    created = day.isoformat()
    files = spec_files(
        slug,
        title,
        created,
        origin=f"Handed off from proposal PROP-{slug} on {created}.{materials_ref}{target_docs_ref}\n",
        carried=carried,
        meta=meta,
        namespace=namespace,
        summary=summary,
        target_docs_ref=target_docs_ref,
        bugfix=bugfix,
        aliases=spec_aliases,
    )
    if bugfix:
        # sdd-spec-bugfix writes plan.md and tasks.md in its plan-tasks stage; skeletons would have to match the
        # characterized criteria for the characterize stage's lint-clean exit.
        files = {SPEC_FILE: files[SPEC_FILE]}

    _check_dependency_projection(
        index, proposal_rel, target_dir.relative_to(root).as_posix() + "/spec.md", files[SPEC_FILE]
    )

    written: list[Path] = []
    moved: list[tuple[Path, Path]] = []
    leftovers: list[Path] = []  # sources copied across file systems, removed once every write succeeded
    promoted: dict[str, str] = {}
    try:
        write_spec_bundle(target_dir, files, binding, written)
        if target_docs_text is not None:
            (target_dir / TARGET_DOCS).write_text(target_docs_text, encoding="utf-8")
        for decision in decisions:
            make_dirs(decision.target.parent, written)
            written.append(decision.target)
            decision.target.write_text(decision.text, encoding="utf-8")
            promoted[str(decision.padr)] = str(decision.target)
        # Every destination was absent in preflight: no pre-existing path enters written or moved.
        for source, destination in materials.moves:
            make_dirs(destination.parent, written)
            move_path(source, destination, written, moved, leftovers)
        for source, destination in feedback + materials.extras:
            _require_inside(root, destination)  # the moved materials/ may hold a symbolic link
            make_dirs(destination.parent, written)
            move_path(source, destination, written, moved, leftovers)
    except Exception as exc:
        problems = roll_back(written, moved)
        if isinstance(exc, AdvisoryError) and not problems:
            raise
        what = (
            "the files it wrote were removed and the proposal is kept"
            if not problems
            else "the roll-back was incomplete; inspect the paths in the details before retrying"
        )
        raise ProposalHandoffError(f"handoff of PROP-{slug} failed; {what}", str(exc), *problems) from exc
    remove_paths(leftovers)

    plan = RelocationPlan(proposal=str(bundle if is_bundle else single))
    if is_bundle:
        plan.dir_target = str(target_dir)
        # Carried proposal text and the copied blueprint were written for the bundle directory.
        plan.moved[str(target_dir)] = str(bundle)
        plan.exact[str(bundle / PROPOSAL_FILE)] = str(target_dir / SPEC_FILE)
        if target_docs_text is not None:
            plan.exact[str(bundle / TARGET_DOCS)] = str(target_dir / TARGET_DOCS)
        plan.exact.update(promoted)
        # A promoted ADR was written for decisions/: its relative links resolve from there.
        plan.moved_files.update({str(d.target): str(d.padr) for d in decisions})
        if materials_target is not None and move_materials:
            plan.prefixes[str(materials_dir)] = str(materials_target)
        # Moved files resolve their links from where they were written; a pre-existing file from where it is.
        for source, destination in materials.moves:
            if destination in materials.subtrees:
                plan.moved[str(destination)] = str(source)
            else:
                plan.material_files[str(destination)] = str(source)
        for source, destination in feedback + materials.extras:
            plan.exact[str(source)] = str(destination)
            plan.moved_files[str(destination)] = str(source)
        for source, destination in materials.duplicates:
            plan.exact.setdefault(str(source), str(destination))  # links to a dropped copy reach the kept one
    else:
        plan.exact[str(single)] = str(target_dir / SPEC_FILE)
    index = DocumentIndex.load(root)
    sources = markdown_files(root, plan, completed_bundles(index))
    report = RewriteReport()
    rewrite_history(root, sources, plan, records, report)
    rewrite_links(root, sources, plan, report)
    rewrite_ids(root, sources, plan, index, report)
    rewrite_paths(root, sources, plan, report)

    notices: list[AdvisoryError] = []
    try:
        if is_bundle:
            shutil.rmtree(bundle)
        else:
            single.unlink()
    except OSError as exc:
        removed = plan.proposal
        rel = Path(removed).relative_to(root).as_posix()
        notices.append(ProposalCleanupWarning(f"{rel} could not be removed: {exc}", target_files=[rel]))
    carried = _record_gates(root, target_dir, slug, binding, gates, notices) if gates and binding is not None else []
    result = _result(
        root, slug, target_dir, binding, unbound, target_docs_text, materials_target, decisions, report, notices
    )
    result.dev_effort = dev_effort
    result.materials_merged = materials.merged
    result.dropped_duplicates = sorted(path.relative_to(root).as_posix() for _, path in materials.duplicates)
    result.dropped_records = [path.relative_to(root).as_posix() for path in records]
    result.carried_gates = carried
    return result


def _check_worktree(root: Path, slug: str) -> None:
    """Refuse a handoff on another branch than ``dev-<slug>``, Development's activity branch, in a linked worktree
    and in the base checkout alike (``require_development_branch``); outside Git nothing is checked."""
    require_development_branch(root, slug, "handoff of the proposal", ProposalWrongWorktreeError)


def _namespace(root: Path, meta: dict[str, Any], proposal_rel: str) -> str | None:
    """The proposal's ``namespace``, carried to ``spec.md``; ``None`` when it has none.

    Raises ``ProposalInvalidError`` when it is not a string naming ``global`` or a registered namespace, and
    ``DocsConfigError`` when ``[tool.docs]`` is malformed.
    """
    if NAMESPACE not in meta:
        return None
    value = meta[NAMESPACE]
    known = [GLOBAL] if value == GLOBAL else known_namespaces(root)
    if isinstance(value, str) and value in known:
        return value
    raise ProposalInvalidError(
        f"{proposal_rel}: namespace {value!r} is not global or a registered namespace",
        target_files=[proposal_rel],
        fix=(
            f"Set the proposal's namespace to one of {', '.join(known)} (registered in [[tool.docs.namespaces]] of"
            " .devkit/config.toml), or remove the field to hand it off as global, then rerun the handoff"
        ),
    )


def _summary(meta: dict[str, Any], proposal_rel: str) -> str | None:
    """The proposal's ``summary``, carried to ``spec.md``; ``None`` when it has none or it is blank.

    Raises ``ProposalInvalidError`` when it is not a string.
    """
    value = meta.get(SUMMARY)
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    raise ProposalInvalidError(
        f"{proposal_rel}: summary {value!r} is not a string",
        target_files=[proposal_rel],
        fix=(
            "Write the proposal's summary as one or two English sentences in quotes, or remove the field, then rerun"
            " the handoff"
        ),
    )


def _scope_notes(meta: dict[str, Any]) -> str:
    """The proposal's target area and boundaries as a carried-notes section, ``""`` when it declares none."""
    boundaries = meta.get("boundaries")
    boundaries = boundaries if isinstance(boundaries, dict) else {}
    lines = []
    if area := text_value(meta.get("target_area")):
        lines.append(f"- Target Area: {area}")
    for label, key in (("Planned Boundaries", "owns"), ("Excluded Boundaries", "excludes")):
        if items := text_values(boundaries.get(key)):
            lines.append(f"- {label}: " + ", ".join(f"`{item}`" for item in items))
    return "### Target Area & Boundaries\n\n" + "\n".join(lines) + "\n\n" if lines else ""


def _require_lettered_slug(name: str, slug: str, rel: str, prefix: str) -> None:
    """Refuse a legacy ``name`` whose slug starts with a number: its ``<prefix>-<slug>`` would fail
    ``RULE-id-convention`` (``2024-budget`` reads as the retired number-based ID ``2024``)."""
    if first_segment_has_letter(slug):
        return
    raise ProposalSlugError(
        f"{name} has slug {slug!r}, whose first segment has no letter; {prefix}-{slug} would break RULE-id-convention",
        target_files=[rel],
        fix=f"Rename {name} (its file or directory and its id) so the first segment of its slug has a letter (for"
        " example budget-2024 instead of 2024-budget), update references to it, then rerun the handoff",
    )


def _plan_decisions(root: Path, decisions_dir: Path, month: str, stamp: str) -> list[_Decision]:
    """The ADRs the bundle's ``PADR-*.md`` files become, with their promoted text."""
    if not decisions_dir.is_dir():
        return []
    sources = []
    for padr in sorted(p for p in decisions_dir.iterdir() if p.is_file() and p.name.startswith("PADR-")):
        if not padr.name.endswith(".md"):
            continue
        adr_slug = clean_slug(padr.name.removeprefix("PADR-").removesuffix(".md"))
        if not adr_slug:
            continue
        rel = padr.relative_to(root).as_posix()
        _require_lettered_slug(f"PADR-{adr_slug}", adr_slug, rel, "ADR")
        original = _read(padr, root)
        try:
            old = parse_document(rel, original)
        except FrontmatterError as exc:
            raise ProposalInvalidError(f"{rel}: {exc.message}", target_files=[rel]) from exc
        if old is not None:
            # A carried alias follows its document's rename: PADR-<x> becomes ADR-<x> in the aliases field only.
            for start, end in sorted(old.alias_spans, reverse=True):
                original = original[:start] + original[start:end].replace("PADR-", "ADR-", 1) + original[end:]
        sources.append((padr, adr_slug, original, rel, old.id if old else f"PADR-{adr_slug}"))
    padr_ids = {source[4] for source in sources}

    def promote_id(match: re.Match[str]) -> str:
        # Only the PADRs promoted here become ADRs; a file name (PADR-x.md in a link) is left to the link rewrite.
        if match.group() not in padr_ids or match.string.startswith(".md", match.end()):
            return match.group()
        return match.group().removeprefix("P")

    planned = []
    for padr, adr_slug, original, rel, padr_id in sources:
        promoted = _PADR.sub(promote_id, original)
        promoted = _accept_status(promoted)
        try:
            new = parse_document(rel, promoted)
        except FrontmatterError as exc:
            raise ProposalInvalidError(f"{rel}: {exc.message}", target_files=[rel]) from exc
        target = root / "docs" / DECISIONS / month / f"{stamp}-{adr_slug}.md"
        planned.append(
            _Decision(
                padr=padr,
                padr_id=padr_id,
                target=target,
                adr_id=new.id if new else f"ADR-{adr_slug}",
                text=promoted,
                aliases=new.aliases if new else (),
            )
        )
    return planned


def _accept_status(text: str) -> str:
    """``text`` with its frontmatter ``status: draft`` and its first prose ``- **Status**: Draft`` line accepted; a
    fenced or indented example or an HTML comment in the body keeps its draft status."""
    block = locate(text)
    end = block.end if block else 0
    text = _DRAFT_STATUS.sub("status: accepted", text[:end]) + text[end:]
    for line in visible_lines(text, start=end):
        # ``line.text`` is the source line with comments blanked in place, so its positions are the source's: only
        # the status word is replaced and a trailing comment stays.
        if (match := _DRAFT_BODY_STATUS.fullmatch(line.text)) is not None:
            word = line.offset + match.end(1)
            return text[:word] + "Accepted" + text[word + len(match.group(0).rstrip()) - match.end(1) :]
    return text


def _unit_records(bundle: Path) -> list[Path]:
    """The proposal unit's devkit workflow records: every decision record and envelope devkit's loaders find in
    ``bundle``, malformed ones included, sorted. A PADR or another file under ``decisions/`` is not one of them."""
    decisions, envelopes = load_decisions(bundle), load_envelopes(bundle)
    files = [record.file for record in decisions.records]
    files += [envelope.file for items in envelopes.by_kind.values() for envelope in items]
    files += [error.file for error in [*decisions.errors, *envelopes.errors]]
    return sorted({bundle / file for file in files if file})


def _task_kind(meta: dict[str, Any], proposal_rel: str) -> str | None:
    """The proposal's ``task_kind``; ``None`` when it has none (the default, ``feature``).

    Raises ``ProposalInvalidError`` when it is not one of ``TASK_KINDS``.
    """
    if TASK_KIND not in meta:
        return None
    value = meta[TASK_KIND]
    if isinstance(value, str) and value.strip() in TASK_KINDS:
        return value.strip()
    raise ProposalInvalidError(
        f"{proposal_rel}: {TASK_KIND} {value!r} is not one of {' | '.join(TASK_KINDS)}",
        target_files=[proposal_rel],
        fix=f"Set the proposal's {TASK_KIND} to the task-kind confirmed at plan-accept ({' or '.join(TASK_KINDS)}),"
        " then rerun the handoff",
    )


def _effort(meta: dict[str, Any], field: str, proposal_rel: str) -> str | None:
    """The proposal's ``planning_effort`` or ``dev_effort`` hint; ``None`` when omitted.

    Raises ``ProposalInvalidError`` when it is present and not one of ``EFFORTS``.
    """
    if field not in meta:
        return None
    value = meta[field]
    if isinstance(value, str) and value.strip() in EFFORTS:
        return value.strip()
    raise ProposalInvalidError(
        f"{proposal_rel}: {field} {value!r} is not one of {' | '.join(EFFORTS)}",
        target_files=[proposal_rel],
        fix=f"Set the proposal's {field} to one of {' | '.join(EFFORTS)}, or remove the field, then rerun the handoff",
    )


def proposal_gates(bundle: Path, workflow: str) -> list[Decision]:
    """The proposal's approvals the spec carries (``CARRIED_GATES``, in order): for each, the latest record of the
    unit's bound ``workflow`` that is not ``cancel``, when it is ``accept`` and no return record that is not a
    ``cancel`` follows it. Stricter than devkit's voiding, so a doubtful approval is asked again rather than carried.
    """
    if not workflow:
        return []
    records = load_decisions(bundle).segment(workflow, 0)
    carried = []
    for request in CARRIED_GATES:
        answer = records.effective(request)
        if answer is None or answer.action != "accept":
            continue
        if any(
            record.request.startswith(RETURN_PREFIX) and record.action != "cancel" and record.seq > answer.seq
            for record in records.records
        ):
            continue
        carried.append(answer)
    return carried


def _record_gates(
    root: Path,
    target_dir: Path,
    slug: str,
    binding: Binding,
    gates: list[Decision],
    notices: list[AdvisoryError],
) -> list[CarriedGate]:
    """Record each of the proposal's ``gates`` in the spec under its own name, with its ``by`` and the note
    ``PROP-<slug>: <the gate's note>`` (``PROP-<slug>`` when it has none), so the spec shows how its direction was
    accepted. A gate that is an open request of the bound spec (``gate:plan-intent`` at its ``intent`` stage)
    is answered with devkit's ``record_answer``; one the spec's workflow never asks (``gate:plan-accept``) is written
    as a decision record of the spec's workflow with the proposal's stage, kept for the audit trail and counting for
    no stage. A gate the spec answered by policy is skipped. The first failure of any kind stops and is added to
    ``notices`` as a ``ProposalGateNotCarriedWarning``: the handoff itself is done by then."""
    rel = target_dir.relative_to(root).as_posix()
    origin = f"PROP-{slug}"
    carried: list[CarriedGate] = []
    request = gates[0].request
    try:
        workspace = Workspace(root, lint=None, ancestor=None)
        for gate in gates:
            request = gate.request
            note = f"{origin}: {gate.note.strip()}" if gate.note and gate.note.strip() else origin
            unit = workspace.resolve_unit(rel)
            evaluation = workspace.evaluate_unit(unit, lint=False)
            if request in {open_request.id for open_request in evaluation.requests}:
                decision = record_answer(workspace, unit, request, "accept", note=note, by=gate.by, lint=False)
            elif any(stage.gate == request.removeprefix("gate:") for stage in unit.doc.stages):
                continue  # the spec's own gate, not open: answered by policy or already recorded
            else:
                record = new_decision(
                    load_decisions(target_dir),
                    request,
                    "accept",
                    workflow=binding.workflow,
                    stage=gate.stage,
                    note=note,
                    by=gate.by,
                )
                decision = write_decision(target_dir, record)
            carried.append(CarriedGate(request, f"{rel}/{decision.file}"))
    except Exception as exc:  # the handoff is done: any failure here is reported, never raised
        detail = f"{exc.code}: {exc.message}" if isinstance(exc, AdvisoryError) else str(exc)
        notices.append(
            ProposalGateNotCarriedWarning(
                f"{request} of SPEC-{slug} was not carried from {origin}",
                detail,
                target_files=[f"{rel}/{SPEC_FILE}"],
                fix=f"Once the cause is resolved, ask the user again for each gate {DEVKIT} workflow next --unit {rel} "
                f"reports as waiting and record the answer with {DEVKIT} workflow answer",
            )
        )
    return carried


def _has_material(materials_dir: Path) -> bool:
    """Whether ``materials_dir`` holds anything worth preserving: a file other than ``JUNK_FILES`` or a symbolic link,
    at any depth (empty directories and junk are deleted with the proposal). A symbolic link ``materials_dir`` is
    preserved as the link."""
    if materials_dir.is_symlink():
        return True
    if not materials_dir.is_dir():
        return False
    for current, dirnames, filenames in os.walk(materials_dir):
        here = Path(current)
        if any(name not in JUNK_FILES or (here / name).is_symlink() for name in filenames):
            return True
        if any((here / name).is_symlink() for name in dirnames):
            return True
    return False


def _plan_extras(
    root: Path,
    bundle: Path,
    decisions: list[_Decision],
    records: list[Path],
    materials: Path,
    move_materials: bool,
) -> list[tuple[Path, Path]]:
    """Every bundle file the handoff does not carry otherwise, with its destination under ``materials`` at its path
    relative to the bundle (``materials/`` itself moves as a whole when ``move_materials``). ``JUNK_FILES`` and the
    unit's workflow ``records`` are not carried; other hidden files are. Symbolic links are never followed: one is
    carried as a file.

    Raises ``ProposalTargetExistsError`` when a destination is also the destination of a path in ``materials/``, or
    lies below a file or symbolic link there or below a ``materials/`` that is a symbolic link (moving into it would
    leave the preserved directory).
    """
    carried = {bundle / PROPOSAL_FILE, bundle / TARGET_DOCS, *(decision.padr for decision in decisions), *records}
    materials_dir = bundle / MATERIALS

    def taken(rel: Path) -> bool:
        """Whether moving ``materials/`` already puts something at ``rel``, or a file or symlink at a parent (a
        ``materials/`` that is itself one takes every destination)."""
        if materials_dir.is_symlink() or materials_dir.is_file() or os.path.lexists(materials_dir / rel):
            return True
        return any(
            (materials_dir / parent).is_symlink() or (materials_dir / parent).is_file() for parent in rel.parents[:-1]
        )

    extras = []
    for path in sorted(bundle.rglob("*")):
        if (path.is_dir() and not path.is_symlink()) or path in carried:
            continue
        if (materials_dir.is_dir() or materials_dir.is_symlink()) and path.is_relative_to(materials_dir):
            continue  # moved as a whole, or junk deleted with the proposal
        if path.name in JUNK_FILES and not path.is_symlink():
            continue
        extras.append((path, materials / path.relative_to(bundle)))
    clashes = [source for source, _ in extras if move_materials and taken(source.relative_to(bundle))]
    if clashes:
        rels = [path.relative_to(root).as_posix() for path in clashes]
        raise ProposalTargetExistsError(
            f"the handoff would move {', '.join(rels)} onto a path of materials/ (the same path, or below a file or"
            " symbolic link)",
            target_files=rels,
            fix="Rename or move the path in [TARGET] (or its counterpart in materials/), then rerun the handoff",
        )
    return extras


def _lstat(path: Path) -> os.stat_result | None:
    """``path``'s own status (a symbolic link is not followed), ``None`` when nothing is there."""
    try:
        return path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return None


def _collision(root: Path, source: Path, destination: Path, here: os.stat_result, there: os.stat_result) -> str | None:
    """The collision kind of ``source`` (status ``here``) against the existing ``destination`` (``there``), both
    taken by ``lstat``; ``None`` for regular files with identical bytes. A symbolic link on either side always
    collides, equal link text included; links are never followed."""
    if stat.S_ISLNK(here.st_mode) or stat.S_ISLNK(there.st_mode):
        return SYMBOLIC_LINK
    kinds = (
        stat.S_ISREG(here.st_mode),
        stat.S_ISDIR(here.st_mode),
        stat.S_ISREG(there.st_mode),
        stat.S_ISDIR(there.st_mode),
    )
    if not (kinds[0] or kinds[1]) or not (kinds[2] or kinds[3]):
        return NON_REGULAR
    if kinds[1] or kinds[3]:
        return FILE_DIRECTORY  # both directories are descended into by the caller
    try:
        same = filecmp.cmp(source, destination, shallow=False)
    except OSError as exc:
        rels = [source.relative_to(root).as_posix(), destination.relative_to(root).as_posix()]
        raise ProposalInvalidError(
            f"{rels[0]} and {rels[1]} cannot be compared: {exc}",
            target_files=rels,
            fix="Make both files in [TARGET] readable, then rerun the handoff",
        ) from exc
    return None if same else DIFFERENT_CONTENT


def _plan_materials(
    root: Path, materials_dir: Path, preserved: Path, move_materials: bool, extras: list[tuple[Path, Path]]
) -> _MaterialsPlan:
    """The moves into the materials directory ``preserved``: today's whole move when it does not exist, else a per-leaf
    merge into it.

    The merge descends into every real directory present on both sides, moves each absent path that holds material
    (a subtree whole), drops non-symlink ``JUNK_FILES`` of the proposal, ignores the destination's other files and
    keeps a byte-identical regular file at the destination (a duplicate). ``preserved`` and every existing directory
    on the way to a planned path must be real directories by ``lstat``. Raises ``ProposalTargetExistsError`` listing
    every conflict before anything is written; a file written at a planned path after this check may be replaced
    (no concurrent-change guarantee, ``ADR-merge-proposal-materials-per-leaf-at-handoff``).
    """
    there = _lstat(preserved)
    if there is None:
        moves = [(materials_dir, preserved)] if move_materials else []
        return _MaterialsPlan(moves=moves, subtrees={preserved} if moves else set(), extras=list(extras))
    _require_inside(root, preserved)
    plan = _MaterialsPlan(merged=True)
    conflicts: list[_Conflict] = []
    origin = materials_dir if move_materials else extras[0][0]  # the proposal path that needs the directory
    if stat.S_ISLNK(there.st_mode):
        _refuse_merge(root, preserved, [_Conflict(origin, preserved, SYMBOLIC_LINK)])
    if not stat.S_ISDIR(there.st_mode):
        kind = FILE_DIRECTORY if stat.S_ISREG(there.st_mode) else NON_REGULAR
        _refuse_merge(root, preserved, [_Conflict(origin, preserved, kind)])

    def merge(source_dir: Path, destination_dir: Path) -> None:
        for source in sorted(source_dir.iterdir()):
            destination = destination_dir / source.name
            here = source.lstat()
            if source.name in JUNK_FILES and not stat.S_ISLNK(here.st_mode) and not stat.S_ISDIR(here.st_mode):
                continue
            existing = _lstat(destination)
            if existing is None:
                if stat.S_ISDIR(here.st_mode):
                    if not _has_material(source):
                        continue  # junk and empty directories are deleted with the proposal
                    plan.subtrees.add(destination)
                plan.moves.append((source, destination))
            elif stat.S_ISDIR(here.st_mode) and stat.S_ISDIR(existing.st_mode):
                merge(source, destination)
            elif (kind := _collision(root, source, destination, here, existing)) is None:
                plan.duplicates.append((source, destination))
            else:
                conflicts.append(_Conflict(source, destination, kind))

    if move_materials:
        here = materials_dir.lstat()
        if stat.S_ISLNK(here.st_mode):
            conflicts.append(_Conflict(materials_dir, preserved, SYMBOLIC_LINK))
        else:
            merge(materials_dir, preserved)
    for source, destination in extras:
        conflict = _merge_extra(root, source, destination, preserved, plan)
        if conflict is not None:
            conflicts.append(conflict)
    if conflicts:
        _refuse_merge(root, preserved, conflicts)
    return plan


def _merge_extra(
    root: Path, source: Path, destination: Path, preserved: Path, plan: _MaterialsPlan
) -> _Conflict | None:
    """Plan the carried file ``source`` into the existing ``preserved``: a move, a duplicate, or the conflict."""
    for parent in reversed(destination.relative_to(preserved).parents[:-1]):
        on_the_way = _lstat(preserved / parent)
        if on_the_way is None:
            break  # created by make_dirs, or by a subtree moved whole before the extras
        if stat.S_ISLNK(on_the_way.st_mode):
            return _Conflict(source, preserved / parent, SYMBOLIC_LINK)
        if not stat.S_ISDIR(on_the_way.st_mode):
            kind = FILE_DIRECTORY if stat.S_ISREG(on_the_way.st_mode) else NON_REGULAR
            return _Conflict(source, preserved / parent, kind)
    else:
        existing = _lstat(destination)
        if existing is not None:
            kind = _collision(root, source, destination, source.lstat(), existing)
            if kind is not None:
                return _Conflict(source, destination, kind)
            plan.duplicates.append((source, destination))
            return None
    plan.extras.append((source, destination))
    return None


def _refuse_merge(root: Path, preserved: Path, conflicts: list[_Conflict]) -> NoReturn:
    """Raise the merge refusal: every conflict in the message and details, the first (in destination order) named in
    the fix with its kind's reconciliation; the materials directory is never to be removed.

    The conflict is a data collision the user resolves, not a rule: it is raised without the guardrail and with the
    user as actor, so its directive is ``INTERACTION`` and ``[FIX]`` is the reconciliation once they agree."""

    def rel(path: Path) -> str:
        return path.relative_to(root).as_posix()

    ordered = sorted(conflicts, key=lambda item: (rel(item.destination), rel(item.source)))
    lines = [f"{rel(item.source)} -> {rel(item.destination)}: {item.kind}" for item in ordered]
    first = ordered[0]
    others = "; reconcile each other conflict in [DETAIL] the same way" if len(ordered) > 1 else ""
    fix = (
        f"Reconcile {rel(first.source)} with the existing {rel(first.destination)} ({first.kind}):"
        f" {_RECONCILE[first.kind]}, keeping {rel(preserved)} and its other files{others}, then rerun the handoff"
    )
    if first.destination == preserved:
        # The dated path holds no materials directory: only renaming it aside, its content kept, lets the handoff run.
        fix = (
            f"Rename {rel(preserved)} aside ({first.kind}: it is not a real directory), keeping its content, or"
            " replace it with a real directory holding that content, then rerun the handoff"
        )
    raise ProposalTargetExistsError(
        f"the handoff cannot merge the proposal's materials into {rel(preserved)}: {len(ordered)} conflict(s)",
        *lines,
        target_files=list(dict.fromkeys(rel(item.destination) for item in ordered)),
        fix=fix,
        guardrail=False,
        actor=Actor.USER,
    )


def _require_inside(root: Path, destination: Path) -> None:
    """Refuse to write or carry anything to ``destination`` when its directory resolves outside the workspace
    ``root`` (a symbolic link on the way)."""
    if destination.parent.resolve().is_relative_to(root):
        return
    rel = destination.relative_to(root).as_posix()
    raise ProposalTargetExistsError(
        f"the handoff would write {rel}, whose directory resolves outside the workspace",
        target_files=[rel],
        fix="Replace the symbolic link on the way to [TARGET] with a directory, then rerun the handoff",
    )


def _check_targets(
    root: Path, index: DocumentIndex, targets: list[Path], decisions: list[_Decision], spec_names: list[str]
) -> None:
    """Refuse a handoff that would overwrite a path, write one path twice, or declare an ID twice: a graduating
    ``SPEC-<slug>`` or ``ADR-<slug>``, or a translated alias (``spec_names`` after the spec ID, each decision's
    ``aliases``), equal to an existing document ID or alias, or to another one graduating in the same handoff."""
    clashes = [path for path in targets if path.exists() or path.is_symlink()]
    clashes += [path for position, path in enumerate(targets) if path in targets[:position]]
    names = [*spec_names, *(name for decision in decisions for name in (decision.adr_id, *decision.aliases))]
    for name in names:
        clashes += [root / document.path for document in index.declares(name)]
    if clashes:
        rels = list(dict.fromkeys(path.relative_to(root).as_posix() for path in clashes))
        raise ProposalTargetExistsError(f"the handoff would overwrite {', '.join(rels)}", target_files=rels)
    twice = sorted({name for position, name in enumerate(names) if name in names[:position]})
    if twice:
        raise ProposalTargetExistsError(
            f"the handoff would declare {', '.join(twice)} more than once (as an ID or a carried alias)",
            target_files=twice,
            fix="Remove the repeated alias or rename one of the decisions, then rerun the handoff",
        )


def _target_docs_reference(text: str) -> str:
    try:
        document = parse_document(TARGET_DOCS, text)
    except FrontmatterError:
        document = None
    return f"`{document.id}`" if document else f"[{TARGET_DOCS}]({TARGET_DOCS})"


def _result(
    root: Path,
    slug: str,
    target_dir: Path,
    binding: Binding | None,
    unbound: AdvisoryError | None,
    target_docs_text: str | None,
    materials_target: Path | None,
    decisions: list[_Decision],
    report: RewriteReport,
    notices: list[AdvisoryError],
) -> HandoffResult:
    def rel(path: Path) -> str:
        return path.relative_to(root).as_posix()

    spec_rel = rel(target_dir)
    result = HandoffResult(
        proposal=f"PROP-{slug}",
        spec=f"SPEC-{slug}",
        dir=spec_rel,
        workflow=binding.workflow if binding else None,
        target_docs=f"{spec_rel}/{TARGET_DOCS}" if target_docs_text is not None else None,
        materials=rel(materials_target) if materials_target else None,
        decisions=[PromotedDecision(d.adr_id, rel(d.target), d.padr_id) for d in decisions],
        rewritten_files=sorted(set(report.files)),
        rewritten=sorted(report.rewritten, key=lambda r: (r.path, r.line, r.kind)),
        unresolved=sorted(report.unresolved, key=lambda u: (u.path, u.line, u.kind)),
    )
    if unbound is not None:
        fix, choices = unbound_guidance(root, spec_rel, DEFAULT_WORKFLOW)
        notices.append(
            ProposalUnboundNotice(
                f"SPEC-{slug} is not bound to a workflow: {DEFAULT_WORKFLOW} is not available ({unbound.code})",
                *choices,
                target_files=[f"{spec_rel}/{SPEC_FILE}"],
                fix=fix,
            )
        )
    if result.unresolved:
        files = list(dict.fromkeys(item.path for item in result.unresolved))
        notices.append(
            ProposalLinkUnresolvedWarning(
                f"{len(result.unresolved)} link(s) or reference(s) into PROP-{slug} have no new target",
                target_files=files,
            )
        )
    id_rewrites = [item for item in result.rewritten if item.kind == ID]
    if id_rewrites:
        notices.append(
            ProposalReferencesRewrittenNotice(
                f"{len(id_rewrites)} ID reference(s) to PROP-{slug} or its PADRs now name the spec or the ADRs",
                target_files=list(dict.fromkeys(item.path for item in id_rewrites)),
            )
        )
    result.notices = notices
    return result


def _check_dependency_projection(index: DocumentIndex, source_path: str, target_path: str, text: str) -> None:
    """Validate the resulting live unit graph before handoff's first write."""
    source = next((d for d in index.documents if d.path == source_path), None)
    target = parse_document(target_path, text)
    if source is None or target is None:
        raise ProposalInvalidError("handoff dependency anchor cannot be indexed", target_files=[source_path])
    if any("depends_on" in issue.message for issue in source.issues):
        raise ProposalInvalidError(
            "proposal depends_on must be a list of string anchor IDs", target_files=[source_path]
        )
    if len(index.by_id.get(source.id, [])) != 1:
        raise ProposalInvalidError(
            f"handoff source {source.id} is ambiguous",
            target_files=[source_path],
            fix="Give each proposal anchor a unique ID, repair incoming references, then rerun handoff",
        )

    def names_source(written: str) -> bool:
        found = index.canonical(written)
        return found is not None and found[0] is source

    # The projection keeps every document's aliases; a target written with the source's ID or one of its aliases
    # is the new spec.
    projected = DocumentIndex(root=index.root)
    for document in [*(d for d in index.documents if d.path != source_path), target]:
        copied: Document = document
        if live_unit(document):
            copied = replace(
                document,
                references=[
                    replace(ref, target=target.id) if ref.field == "depends_on" and names_source(ref.target) else ref
                    for ref in document.references
                ],
            )
        projected.add(copied)
    problems = []
    for document in projected.documents:
        if not live_unit(document):
            continue
        problems.extend(f"{document.id}: {issue.message}" for issue in document.issues if "depends_on" in issue.message)
        for ref in document.references:
            if ref.field == "depends_on" and (problem := target_problem(projected, ref.target)):
                problems.append(f"{document.id}: {problem}")
    problems.extend(f"unit dependency cycle includes {name}" for name in sorted(cycle_members(projected)))
    if problems:
        raise ProposalInvalidError(
            "handoff projected dependency graph is invalid",
            *problems,
            target_files=[source_path],
            fix="Repair the listed depends_on references and cycles, then rerun handoff",
        )
