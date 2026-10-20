"""Record the user's acceptance of a proposal in one validated step (``devkit spec proposal accept``).

``accept_proposal`` is the one writer of an acceptance (``ADR-direct-acceptance-command-and-handoff-guard``), run
only after the user's explicit acceptance. Its form follows from the status and ``direct``:

- ``planning``: a proposal in review (``status: reviewing``) on its ``plan-<slug>``, the acceptance after Planning;
- ``direct``: an eligible draft (``ADR-eligibility-for-direct-acceptance``) on the base checkout, Backlog work
  without a Planning branch or run;
- ``repair``: with ``direct``, a proposal already ``accepted`` that has no effective ``gate:plan-accept`` and no
  ``worker`` envelope (no Planning ran), held to every direct condition except the status.

It writes ``status: accepted`` (not for a repair) and records ``gate:plan-accept`` through devkit's
``record_answer``, so the workflow decides whether ``collect-feedback`` holds, is switched off or is skipped by
policy; when the workflow does not open the gate it restores ``proposal.md`` byte-for-byte and reports the unmet
checks and hold reasons. ``check`` runs every check and writes nothing; a missing ``gate:plan-intent`` is then a
pending condition, not a blocking one. The command never records ``plan-intent``, commits, merges or hands off.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit.core import FrontmatterError
from devkit.core.errors import ArgumentError
from devkit.core.frontmatter import parse
from devkit.workflow import UnitRef, Workspace, load_envelopes, record_answer

from devkit_spec.branches import PLANNING_PREFIX, base_checkout_problem, checkout, planning_branches
from devkit_spec.errors import (
    ProposalAcceptRefusedError,
    ProposalGateNotOpenError,
    ProposalInvalidError,
    ProposalNotEligibleError,
    ProposalNotFoundError,
    ProposalWrongWorktreeError,
)
from devkit_spec.proposals.binding import DEFAULT_TASK_KIND, TASK_KINDS
from devkit_spec.proposals.handoff import (
    ACCEPT_GATE,
    ACCEPTED,
    INTENT_GATE,
    NEEDS_DECOMPOSE,
    TASK_KIND,
    proposal_gates,
)
from devkit_spec.proposals.scaffold import PROPOSAL_FILE, bundle_dir, require_slug, single_file
from devkit_spec.proposals.specs import text_value

PLANNING, DIRECT, REPAIR = "planning", "direct", "repair"
FORMS = (PLANNING, DIRECT, REPAIR)
ACTOR = "user"
"""The only ``--by``: ``plan-accept`` is always the user's (policy ``ask`` only); autohub records the user's UI
acceptance the same way."""
DRAFT, REVIEWING, REJECTED = "draft", "reviewing", "rejected"
SUPERSEDES = "supersedes"
WORKER = "worker"

# The frontmatter ``status:`` line (plain or quoted value); a trailing comment ("#" after whitespace) stays.
_STATUS = re.compile(r"""^status:[ \t]*(?:[A-Za-z-]+|"[A-Za-z-]*"|'[A-Za-z-]*')(?=[ \t]*\r?$|[ \t]+#)""", re.MULTILINE)


@dataclass(frozen=True)
class AcceptResult:
    """What ``accept_proposal`` checked or wrote; paths are workspace-relative.

    ``status`` is the proposal's status after the command (its current one under ``checked``), ``decision`` the
    ``gate:plan-accept`` record written (``None`` under ``checked``), ``pending`` the conditions a ``checked`` run
    reports as still to be recorded before the acceptance (``gate:plan-intent``).
    """

    proposal: str
    path: str
    form: str
    status: str
    checked: bool
    decision: str | None = None
    pending: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "proposal": self.proposal,
            "path": self.path,
            "form": self.form,
            "status": self.status,
            "checked": self.checked,
            "eligible": True,
            "decision": self.decision,
            "pending": list(self.pending),
        }


def accept_proposal(
    root: Path, slug: str, *, by: str, note: str = "", direct: bool = False, check: bool = False
) -> AcceptResult:
    """Accept proposal ``slug`` under the workspace ``root`` for the user (see the module docstring).

    Raises, before writing anything: ``ArgumentError`` (``by`` other than ``user``; ``direct`` without a non-blank
    ``note``), ``ProposalSlugError``, ``ProposalNotFoundError``, ``ProposalInvalidError``,
    ``ProposalAcceptRefusedError`` (a form the status does not allow, a single-file or unbound proposal),
    ``ProposalWrongWorktreeError`` (the Planning form off ``plan-<slug>``) and ``ProposalNotEligibleError`` (every
    failed direct condition in its details). After writing the status: ``ProposalGateNotOpenError``, with the status
    restored.
    """
    if by != ACTOR:
        raise ArgumentError(
            f"--by {by!r}: plan-accept is always the user's decision",
            target_files=["--by"],
            fix="Pass --by user, only after the user's explicit acceptance",
        )
    reason = note.strip()
    if direct and not reason:
        raise ArgumentError(
            "--note is required with --direct: the reason the draft was eligible",
            target_files=["--note"],
            fix='Pass --note "<why the direction leaves nothing to compare>"',
        )
    root = root.resolve()
    slug = require_slug(slug.strip().removeprefix("PROP-"))
    bundle, single = bundle_dir(root, slug), single_file(root, slug)
    if not bundle.is_dir():
        if single.is_file():
            raise ProposalAcceptRefusedError(
                f"PROP-{slug} is a single-file proposal, which has no gate records",
                target_files=[single.relative_to(root).as_posix()],
                fix="Its acceptance is its status line alone: after the user's explicit acceptance set status: "
                "accepted by hand",
            )
        raise ProposalNotFoundError(f"proposal PROP-{slug} not found", target_files=[f"PROP-{slug}"])
    path = bundle / PROPOSAL_FILE
    rel = path.relative_to(root).as_posix()
    try:
        original = path.read_bytes()
        meta: dict[str, Any] = parse(original.decode("utf-8")).data or {}
    except (OSError, UnicodeDecodeError) as exc:
        raise ProposalInvalidError(f"{rel} cannot be read: {exc}", target_files=[rel]) from exc
    except FrontmatterError as exc:
        raise ProposalInvalidError(f"{rel}: {exc.message}", target_files=[rel]) from exc
    workflow = text_value(meta.get("workflow"))
    if not workflow:
        raise ProposalAcceptRefusedError(
            f"PROP-{slug} is not bound to a workflow, so it has no gate records",
            target_files=[rel],
            fix="Bind it with devkit workflow bind --unit <dir> --workflow sdd-proposal and rerun, or, after the "
            "user's explicit acceptance, set status: accepted by hand (an unbound proposal's acceptance is its status)",
        )
    status = text_value(meta.get("status")).lower()
    gates = {gate.request for gate in proposal_gates(bundle, workflow)}
    form = _form(slug, status, direct, ACCEPT_GATE in gates, rel)
    pending: list[str] = []
    workspace = Workspace(root, lint=None, ancestor=None)
    unit = workspace.resolve_unit(bundle.relative_to(root).as_posix())
    if form == PLANNING:
        found = checkout(root)
        expected = f"{PLANNING_PREFIX}{slug}"
        if found is not None and found[1] != expected:
            raise ProposalWrongWorktreeError(
                f"the Planning acceptance of PROP-{slug} runs on branch {expected}, not on"
                f" {found[1] or '- (detached HEAD)'}",
                target_files=[rel],
                fix=f"Run it in the checkout of {expected}; for a draft on the base checkout use --direct",
            )
    else:
        blocking = _direct_conditions(root, bundle, slug, meta, form, workspace, unit)
        if INTENT_GATE not in gates:
            pending.append(INTENT_GATE)
        if blocking or (pending and not check):
            raise ProposalNotEligibleError(
                f"PROP-{slug} is not eligible for a direct acceptance ({form})",
                *(f"blocking: {item}" for item in blocking),
                *(f"pending: {item} is not recorded (the user's explicit answer first)" for item in pending),
                target_files=[rel],
            )
    if check:
        return AcceptResult(f"PROP-{slug}", rel, form, status, True, pending=tuple(pending))

    recorded = _note(meta, form, reason)
    if form != REPAIR:
        _write_status(path, original, rel)
    try:
        decision = record_answer(workspace, unit, ACCEPT_GATE, "accept", note=recorded, by=by, lint=False)
    except AdvisoryError as exc:
        details = _not_open_details(workspace, unit, exc)
        if form != REPAIR:
            path.write_bytes(original)
        undone = "nothing was recorded" if form == REPAIR else "the status was restored"
        raise ProposalGateNotOpenError(
            f"{ACCEPT_GATE} of PROP-{slug} is not open; {undone}",
            *details,
            target_files=[rel],
        ) from exc
    except BaseException:
        # Any other failure (a write error, an interruption) leaves no status without its record.
        if form != REPAIR:
            path.write_bytes(original)
        raise
    return AcceptResult(
        f"PROP-{slug}",
        rel,
        form,
        ACCEPTED,
        False,
        decision=f"{bundle.relative_to(root).as_posix()}/{decision.file}",
    )


def _form(slug: str, status: str, direct: bool, recorded: bool, rel: str) -> str:
    """The form the status and ``direct`` select; ``ProposalAcceptRefusedError`` for any other combination."""
    if status == REVIEWING and not direct:
        return PLANNING
    if status == DRAFT and direct:
        return DIRECT
    if status == ACCEPTED and direct and not recorded:
        return REPAIR
    if status == DRAFT:
        reason, fix = "is a draft", "Accept an eligible draft with --direct on the base checkout, or run Planning"
    elif status == REVIEWING:
        reason, fix = "is in review", f"Accept it without --direct on {PLANNING_PREFIX}{slug} once Planning is done"
    elif status == ACCEPTED and recorded:
        reason, fix = "is accepted and its gate:plan-accept is recorded", "Nothing to accept: hand it off"
    elif status == ACCEPTED:
        reason, fix = (
            "is accepted without its gate:plan-accept record",
            "Repair it with --direct on the base checkout, after the user's explicit acceptance",
        )
    elif status == REJECTED:
        reason, fix = "is rejected", "A rejected proposal is never accepted; leave it to the hygiene cleanup"
    else:
        reason, fix = f"has status {status or '-'}", "Correct the proposal's status (draft, reviewing, accepted)"
    raise ProposalAcceptRefusedError(
        f"PROP-{slug} {reason}; {'--direct' if direct else 'the Planning form'} does not accept it",
        target_files=[rel],
        fix=fix,
    )


def _direct_conditions(
    root: Path, bundle: Path, slug: str, meta: dict[str, Any], form: str, workspace: Workspace, unit: UnitRef
) -> list[str]:
    """Every failed blocking condition of a direct acceptance or repair, in a fixed order."""
    failed: list[str] = []
    if meta.get(NEEDS_DECOMPOSE) is True:
        failed.append(f"{NEEDS_DECOMPOSE}: true (Backlog splits it first)")
    if meta.get(SUPERSEDES):
        failed.append(
            f"{SUPERSEDES}: {text_value(meta.get(SUPERSEDES))} (a supersede decides its direction in Planning)"
        )
    branch = planning_branches(root).get(slug)
    if branch is not None:
        failed.append(f"Planning branch {branch} exists (Planning runs there)")
    kind = meta.get(TASK_KIND, DEFAULT_TASK_KIND)
    if not (isinstance(kind, str) and kind.strip() in TASK_KINDS):
        failed.append(f"{TASK_KIND} {kind!r} is not one of {' | '.join(TASK_KINDS)}")
    hold = workspace.evaluate_unit(unit, lint=False).hold
    failed += [f"envelope hold: {line}" for line in hold.reasons()]
    if form == REPAIR and load_envelopes(bundle).by_kind.get(WORKER):
        failed.append("a worker envelope exists: Planning ran, so a missing record is not repaired")
    if (problem := base_checkout_problem(root)) is not None:
        failed.append(problem)
    return failed


def _note(meta: dict[str, Any], form: str, reason: str) -> str:
    """The recorded note: the given one for the Planning form, the stated direct acceptance otherwise."""
    if form == PLANNING:
        return reason
    kind = text_value(meta.get(TASK_KIND)) or DEFAULT_TASK_KIND
    return f"direct acceptance, Planning skipped: {reason}; task_kind {kind} confirmed"


def _write_status(path: Path, original: bytes, rel: str) -> None:
    text = original.decode("utf-8")
    end = _frontmatter_end(text)
    updated, count = _STATUS.subn("status: accepted", text[:end], count=1)
    if count != 1:
        raise ProposalInvalidError(f"{rel} has no status line to change", target_files=[rel])
    path.write_bytes((updated + text[end:]).encode("utf-8"))


def _frontmatter_end(text: str) -> int:
    """The offset just past the closing ``---`` of the frontmatter (0 when there is none)."""
    match = re.match(r"---\r?\n.*?^---[ \t]*\r?$", text, re.DOTALL | re.MULTILINE)
    return match.end() if match else 0


def _not_open_details(workspace: Workspace, unit: UnitRef, exc: AdvisoryError) -> list[str]:
    """The workflow's reasons the gate did not open: its unmet checks and hold reasons, then the engine's code."""
    details: list[str] = []
    try:
        evaluation = workspace.evaluate_unit(unit, lint=False)
    except AdvisoryError as error:
        details.append(f"evaluation failed ({error.code}): {error.message}")
    else:
        stage = evaluation.stage.id if evaluation.stage is not None else "complete"
        details += [f"unmet at {stage}: {check.name}" for check in evaluation.unmet]
        details += [f"hold: {line}" for line in evaluation.hold.reasons()]
    details.append(f"{exc.code}: {exc.message}")
    return details
