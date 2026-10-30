"""Host-authorized, source-bound handoff of a reviewed proposal to Development."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_agt.features.workflow import Workspace
from devkit_agt.features.worktree import StartResult, branch_marker, locate, path_for, read_worktree_config, start
from devkit_agt.features.worktree.usecases.lifecycle import _prepare
from devkit_core.base.usecase import BaseUseCase
from devkit_core.core import GitError, run_git, run_git_text
from devkit_core.core.frontmatter import parse
from devkit_dist.features.project.models.invocation import devkit_command
from devkit_dist.features.project.usecases.invocation import guard_execution

from devkit_spec.base.axes import (
    DEFAULT_EFFORT,
    DEFAULT_TASK_KIND,
    DEV_EFFORT,
    EFFORTS,
    PLANNING_EFFORT,
    PROPOSAL_WORKFLOW,
    TASK_KINDS,
)
from devkit_spec.base.errors import (
    HandoffBaseDirtyError,
    HandoffCommitRefusedError,
    HandoffNotReadyError,
    HandoffReplyError,
    HandoffStaleError,
    HandoffWorktreeConflictError,
    ProposalInvalidError,
    ProposalWrongWorktreeError,
    SpecConfigError,
)
from devkit_spec.base.units import PROPOSAL_FILE, proposal_unit
from devkit_spec.features.delivery.usecases.handoff import handoff_and_register
from devkit_spec.features.policy import require_sdd
from devkit_spec.features.policy.usecases.approvals import approval_policy
from devkit_spec.features.proposals.models.handoff import HandoffPreview


def _existing(root: Path, slug: str, head: str) -> bool:
    """Recover only an untouched devkit-created checkout of this exact accepted base."""
    position = locate(root)
    path = path_for(position, f"dev-{slug}")
    if not path.exists() and not path.is_symlink():
        return False
    reason = None
    try:
        current = locate(path)
        marker = branch_marker(position.base, f"dev-{slug}")
        if path.is_symlink() or not current.linked or current.root != path or current.base != position.base:
            reason = "it is not a linked worktree of this repository at the devkit worktree path"
        elif current.branch != f"dev-{slug}" or marker != str(path):
            reason = f"devkit did not create it for branch dev-{slug}"
        elif run_git(path, "rev-parse", "HEAD").decode().strip() != head:
            reason = "its HEAD is not the accepted base commit"
        elif run_git(path, "status", "--porcelain", "--untracked-files=normal").strip():
            reason = "it has uncommitted changes"
    except AdvisoryError as exc:
        reason = f"it cannot be inspected ({exc.code}): {exc.message}"
    if reason is not None:
        raise HandoffWorktreeConflictError(
            f"a Development worktree for dev-{slug} already exists and cannot be reused",
            reason,
            target_files=[f"dev-{slug}"],
        )
    return True


HANDOFF_SUBJECT = "spec: hand off {slug} to Development"
"""The subject of the composed handoff's one commit (``ADR-composed-handoff-commits-its-own-transaction``)."""


def _dirty_paths(root: Path) -> list[str]:
    """Every path ``git status`` reports in ``root``, untracked files one by one, in Git's order."""
    entries = run_git(root, "status", "--porcelain", "-z", "--untracked-files=all").decode(errors="surrogateescape")
    paths, fields = [], iter(entries.split("\0"))
    for entry in fields:
        if not entry:
            continue
        paths.append(entry[3:])
        if entry[0] in "RC":  # a staged rename or copy names its source in the next field
            paths.append(next(fields, ""))
    return [path for path in paths if path]


def _commit_handoff(root: Path, slug: str, base: str) -> str:
    """Commit the whole handoff delta once in ``root`` and return HEAD read after ``git commit`` returns.

    The worktree was clean at ``base`` before the handoff, so the delta ``git status`` reports is the handoff's own.
    Raises ``HandoffCommitRefusedError`` when nothing landed; the writes stay staged and nothing is rolled back. A
    failure after which HEAD moved (a timeout, a failing post-commit step) returns the landed HEAD for verification.
    """
    dirty = _dirty_paths(root)
    run_git_text(root, "add", "-A")
    guard_execution()
    subject = HANDOFF_SUBJECT.format(slug=slug)
    try:
        run_git_text(root, "commit", "-q", "-m", subject, timeout=None)
    except GitError as exc:
        if run_git_text(root, "rev-parse", "HEAD") == base:
            output = [line for line in exc.stderr.splitlines() if line.strip()][-20:]
            raise HandoffCommitRefusedError(
                f"git commit refused the handoff transaction of PROP-{slug} in dev-{slug}; its writes are kept staged",
                *(output or [exc.message]),
                target_files=dirty,
                fix=f"In the dev-{slug} worktree ({root}) fix the cause [DETAIL] shows, then commit the staged handoff "
                f"there with `git -C {root} commit -m '{subject}'`; do not rerun the handoff",
            ) from exc
    return run_git_text(root, "rev-parse", "HEAD")


def _verify_handoff_commit(root: Path, slug: str, base: str, head: str) -> None:
    """Raise ``HandoffStaleError`` unless ``head`` is one direct child of ``base`` and ``root`` is clean."""
    parents = run_git_text(root, "rev-list", "--parents", "-n", "1", head).split()[1:]
    left = _dirty_paths(root)
    if parents != [base] or left:
        raise HandoffStaleError(
            f"the handoff commit {head} of PROP-{slug} is not one clean direct child of the reviewed base {base}",
            f"parents: {' '.join(parents) or '-'}",
            *(f"dirty: {path}" for path in left),
            target_files=[f"dev-{slug}"],
        )


def _handoff_command(slug: str, effort: str | None) -> str:
    """The composed handoff command; without a known effort, the instruction to add one (low, medium or high)."""
    if effort:
        return f"`{devkit_command(f'spec proposal handoff {slug} --effort {effort}')}`"
    return f"`{devkit_command(f'spec proposal handoff {slug} --effort')}` with low, medium or high"


def prepare(root: Path, slug: str, effort: str | None = None) -> HandoffPreview:
    """Check every prerequisite of the composed handoff of ``slug`` and return what it would do; writes nothing.

    ``effort`` only completes the command the refusals name. Raises ``ProposalWrongWorktreeError`` off the retained
    base checkout, ``HandoffBaseDirtyError``, ``HandoffNotReadyError`` (not accepted, decomposition, incomplete
    Planning), ``ProposalInvalidError`` (a field without a valid value) and ``HandoffWorktreeConflictError``.
    """
    require_sdd(root)
    position = locate(root)
    command = _handoff_command(slug, effort)
    if position.linked or not position.branch or position.branch.startswith(("dev-", "plan-")):
        raise ProposalWrongWorktreeError(
            f"the composed handoff of PROP-{slug} runs in the retained base checkout, not on "
            f"{position.branch or '- (detached HEAD)'}",
            fix=f"Run {command} in the main worktree on its base branch",
        )
    dirty = run_git_text(position.base, "status", "--porcelain", "--untracked-files=normal").splitlines()
    if any(line.strip() for line in dirty):
        paths = [line[3:] for line in dirty if line.strip()]
        raise HandoffBaseDirtyError(
            "the base checkout has uncommitted changes",
            *([f"{len(paths) - 20} more paths"] if len(paths) > 20 else []),
            target_files=paths[:20],
        )
    head = run_git(position.base, "rev-parse", "HEAD").decode().strip()
    unit = proposal_unit(slug)
    rel = f"{unit}/proposal.md"
    mode = run_git_text(position.base, "ls-tree", head, "--", rel).split()
    if not mode or mode[0] not in {"100644", "100755"}:
        raise HandoffNotReadyError(
            f"PROP-{slug} has no committed proposal.md on the base",
            "the accepted proposal must be a committed regular proposal.md file",
            target_files=[rel],
        )
    text = run_git(position.base, "show", f"{head}:{rel}").decode()
    meta = parse(text).data or {}
    if meta.get("status") != "accepted":
        raise HandoffNotReadyError(
            f"PROP-{slug} is not accepted on the base",
            f"status: {meta.get('status') or '-'}",
            target_files=[rel],
            fix=f"Once the user accepts the proposal, run `{devkit_command(f'spec proposal accept {slug} --by user --mode accept_only')}`"
            " from the base checkout, then rerun the same command",
        )
    if meta.get("needs_decompose") is True:
        raise HandoffNotReadyError(
            f"PROP-{slug} is marked needs_decompose: true", "Backlog splits it first", target_files=[rel]
        )
    invalid = []
    if meta.get("task_kind", DEFAULT_TASK_KIND) not in TASK_KINDS:
        invalid.append(f"task_kind {meta.get('task_kind')!r} is not one of {' | '.join(TASK_KINDS)}")
    if meta.get(PLANNING_EFFORT, DEFAULT_EFFORT) not in EFFORTS:
        invalid.append(f"planning_effort {meta.get('planning_effort')!r} is not one of {' | '.join(EFFORTS)}")
    invalid += [f"{key} is not text" for key in ("title", "summary") if key in meta and not isinstance(meta[key], str)]
    effort_hint = meta.get(DEV_EFFORT, DEFAULT_EFFORT)
    if effort_hint not in EFFORTS:
        invalid.append(f"dev_effort {effort_hint!r} is not one of {' | '.join(EFFORTS)}")
    if invalid:
        raise ProposalInvalidError(
            f"PROP-{slug} has frontmatter values the handoff cannot use",
            *invalid,
            target_files=[rel],
            fix="Correct the values in [DETAIL] on the base (a reviewed commit), then rerun the same command",
        )
    workspace = Workspace(root)
    ref = workspace.resolve_unit(unit)
    evaluation = workspace.evaluate_unit(ref, lint=False)
    passed = {gate.name for _stage, gate in evaluation.passed_gates if gate.satisfied}
    missing = sorted({"plan-intent", "plan-accept"} - passed)
    if ref.doc.id != PROPOSAL_WORKFLOW or not evaluation.complete or evaluation.errors or missing:
        details = [f"workflow: {ref.doc.id}" if ref.doc.id != PROPOSAL_WORKFLOW else ""]
        details += [f"unmet: {check.name}" for check in evaluation.unmet]
        details += [f"problem ({error.code}): {error.message}" for error in evaluation.errors]
        details += [f"missing approval: {name}" for name in missing]
        raise HandoffNotReadyError(
            f"PROP-{slug} has no completed {PROPOSAL_WORKFLOW} Planning with its own plan-intent and plan-accept",
            *(line for line in details if line),
            target_files=[rel],
        )
    config = read_worktree_config(root)
    policy = hashlib.sha256()
    for name in ("config.toml", "installation.json"):
        file = root / ".devkit" / name
        policy.update(file.read_bytes() if file.exists() else b"")
    return HandoffPreview(
        root,
        slug,
        head,
        position.branch,
        str(path_for(position, f"dev-{slug}")),
        config.setup,
        policy.hexdigest(),
        str(meta.get("title") or f"PROP-{slug}"),
        str(meta.get("summary") or ""),
        text,
        effort_hint,
        _existing(root, slug, head),
    )


class HandoffUseCase(BaseUseCase):
    def __init__(self, root: Path) -> None:
        self.root = root

    def execute(self, slug: str, effort: str) -> dict[str, Any]:
        """Start Development after Host-carried approval, rechecking the base."""
        self.root = self.root.resolve()
        if effort not in EFFORTS:
            raise HandoffReplyError("choose low, medium or high Development effort")
        guard_execution()
        preview = prepare(self.root, slug, effort)
        authority = approval_policy(self.root, "proposal-handoff")
        if authority not in {"ask", "auto"}:
            raise SpecConfigError(f"proposal-handoff policy must be ask or auto, not {authority!r}")
        if authority == "auto" and effort != preview.effort:
            raise HandoffReplyError(
                "automatic handoff must use the proposal's declared dev_effort",
                fix=f"Rerun {_handoff_command(slug, preview.effort)}: proposal-handoff=auto uses dev_effort "
                f"{preview.effort}",
            )
        result = self._execute(preview, effort)
        return {**result, "authority": "policy" if authority == "auto" else "host-conversation"}

    def _execute(self, preview: HandoffPreview, effort: str) -> dict:
        guard_execution()
        if prepare(self.root, preview.slug) != preview:
            raise HandoffStaleError(
                "the base, accepted plan or policy changed after review",
                target_files=[f"{proposal_unit(preview.slug)}/{PROPOSAL_FILE}"],
            )
        position = locate(self.root)
        guard_execution()
        try:
            if preview.existing:
                notices = []
                setup, synced = _prepare(
                    Path(preview.worktree),
                    preview.setup,
                    True,
                    notices,
                    before_step=lambda _step: guard_execution(),
                )
                started = StartResult(
                    f"dev-{preview.slug}",
                    Path(preview.worktree),
                    position.base,
                    False,
                    setup,
                    synced,
                    notices,
                    existing=True,
                )
            else:
                started = start(
                    position,
                    f"dev-{preview.slug}",
                    setup=preview.setup,
                    sync=True,
                    revision=preview.head,
                    before_step=lambda _step: guard_execution(),
                )
        except AdvisoryError as exc:
            return {
                "status": "needs_recovery" if Path(preview.worktree).exists() else "blocked",
                "worktree": {"path": preview.worktree, "created": Path(preview.worktree).exists()},
                "activity_effort": effort,
                "commit": None,
                "errors": [exc.to_dict()],
                "notices": [],
            }
        result = {
            "status": "needs_recovery",
            "worktree": started.to_dict(),
            "activity_effort": effort,
            "commit": None,
            "errors": [],
            "notices": [item.to_dict() for item in started.notices],
        }
        if any(item.code in {"WORKTREE_SETUP_FAILED", "WORKTREE_SYNC_FAILED"} for item in started.notices):
            return result
        root = started.path
        try:
            if run_git(root, "rev-parse", "HEAD").decode().strip() != preview.head:
                raise HandoffStaleError("the new worktree no longer contains the reviewed base commit")
            if run_git(root, "status", "--porcelain", "--untracked-files=normal").strip():
                raise HandoffStaleError(
                    "setup changed tracked or untracked worktree files; inspect them before handoff"
                )
            guard_execution()
            completed = handoff_and_register(root, preview.slug, before_registration=guard_execution)
            handed, registered = completed.handoff, completed.registered
            result["handoff"] = handed.to_dict()
            result["notices"] += [item.to_dict() for item in completed.notices]
            if registered is not None:
                result["scope_token"] = registered.token
            result["commit"] = _commit_handoff(root, preview.slug, preview.head)
            _verify_handoff_commit(root, preview.slug, preview.head, result["commit"])
            result.update(status="handed_off", next_command=devkit_command(f"workflow next --unit {handed.dir}"))
        except HandoffCommitRefusedError as exc:
            # The writes landed uncommitted: the next step is the Host's commit there, not the spec workflow.
            result["handoff"]["next_command"] = None
            result.update(errors=[exc.to_dict()], next_action=exc.fix)
        except AdvisoryError as exc:
            result["errors"] = [exc.to_dict()]
        return result
