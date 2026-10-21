"""Local Planning-to-Development handoff using the host's native form confirmation."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from pathlib import Path

from devkit.advisory import AdvisoryError
from devkit.core import run_git
from devkit.core.frontmatter import parse
from devkit.core.mcp import Confirmation, McpTool
from devkit.core.mcp_context import guard_execution
from devkit.core.presentation import approval_language
from devkit.workflow import Workspace
from devkit.worktree import StartResult, locate, path_for, read_worktree_config, start
from devkit.worktree.lifecycle import _prepare

from devkit_spec.errors import HandoffNotReadyError, HandoffReplyError, HandoffStaleError
from devkit_spec.handoff_language import schema as approval_schema
from devkit_spec.proposal_report import validate
from devkit_spec.proposals import handoff_proposal
from devkit_spec.proposals.binding import EFFORTS, TASK_KINDS
from devkit_spec.scope.flow import SOURCE_HANDOFF, auto_register


@dataclass(frozen=True)
class HandoffPreview:
    root: Path
    slug: str
    head: str
    base_branch: str
    worktree: str
    setup: str | None
    policy: str
    title: str
    summary: str
    plan: str
    effort: str
    report_uri: str = ""
    existing: bool = False

    def message(self, language: str = "en") -> str:
        from devkit_spec.handoff_language import message

        return message(self, language)


def _existing(root: Path, slug: str, head: str) -> bool:
    """Recover only an untouched devkit-created checkout of this exact accepted base."""
    position = locate(root)
    path = path_for(position, f"dev-{slug}")
    if not path.exists() and not path.is_symlink():
        return False
    try:
        current = locate(path)
        marker = run_git(position.base, "config", "--get", f"branch.dev-{slug}.devkitWorktree").decode().strip()
        if (
            path.is_symlink()
            or not current.linked
            or current.root != path
            or current.base != position.base
            or current.branch != f"dev-{slug}"
            or marker != str(path)
            or run_git(path, "rev-parse", "HEAD").decode().strip() != head
            or run_git(path, "status", "--porcelain", "--untracked-files=normal").strip()
        ):
            raise HandoffNotReadyError("existing Development worktree provenance or clean source differs")
    except AdvisoryError as exc:
        raise HandoffNotReadyError(
            "inspect the existing Development worktree and preserve its changes before requesting fresh handoff"
        ) from exc
    return True


def prepare(root: Path, slug: str, report_uri: str = "") -> HandoffPreview:
    position = locate(root)
    if position.linked or not position.branch or position.branch.startswith(("dev-", "plan-")):
        raise HandoffNotReadyError("run the handoff service from the retained base checkout on its base branch")
    if run_git(position.base, "status", "--porcelain", "--untracked-files=normal").strip():
        raise HandoffNotReadyError("the base checkout has uncommitted changes; commit or resolve them before review")
    head = run_git(position.base, "rev-parse", "HEAD").decode().strip()
    if report_uri:
        validate(root, slug, head, report_uri)
    relative = root.relative_to(position.base)
    unit = f"docs/proposals/PROP-{slug}"
    anchor = relative / unit / "proposal.md"
    mode = run_git(position.base, "ls-tree", head, "--", anchor.as_posix()).decode().split()
    if not mode or mode[0] not in {"100644", "100755"}:
        raise HandoffNotReadyError("the accepted proposal must be a committed regular proposal.md file")
    text = run_git(position.base, "show", f"{head}:{anchor.as_posix()}").decode()
    meta = parse(text).data or {}
    if meta.get("status") != "accepted" or meta.get("needs_decompose") is True:
        raise HandoffNotReadyError("the proposal must be accepted and must not need decomposition")
    if meta.get("task_kind", "feature") not in TASK_KINDS or meta.get("planning_effort", "medium") not in EFFORTS:
        raise HandoffNotReadyError("the proposal task_kind or Planning effort hint is invalid")
    if any(key in meta and not isinstance(meta[key], str) for key in ("title", "summary")):
        raise HandoffNotReadyError("the proposal title and summary must be text")
    effort = meta.get("dev_effort", "medium")
    if effort not in EFFORTS:
        raise HandoffNotReadyError("dev_effort must be low, medium or high")
    workspace = Workspace(root)
    ref = workspace.resolve_unit(unit)
    evaluation = workspace.evaluate_unit(ref, lint=False)
    if ref.doc.id != "sdd-proposal" or not evaluation.complete or evaluation.errors:
        raise HandoffNotReadyError("the proposal workflow must be complete with its own plan-intent and plan-accept")
    passed = {gate.name for _stage, gate in evaluation.passed_gates if gate.satisfied}
    if not {"plan-intent", "plan-accept"}.issubset(passed):
        raise HandoffNotReadyError("the proposal needs its own satisfied plan-intent and plan-accept approvals")
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
        effort,
        report_uri,
        _existing(root, slug, head),
    )


class HandoffService:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self._lock = asyncio.Lock()

    async def handoff(self, slug: str, report_uri: str, confirm: Confirmation) -> dict:
        guard_execution()
        async with self._lock:
            guard_execution()
            language = approval_language(self.root)
            preview = await asyncio.to_thread(prepare, self.root, slug, report_uri)
            await asyncio.to_thread(validate, self.root, slug, preview.head, report_uri)
            guard_execution()
            reply = await confirm(
                preview.message(language),
                approval_schema(preview.effort, language),
            )
            if reply.action != "accept" or reply.content.get("approve") is not True:
                return {"status": {"decline": "declined", "cancel": "cancelled"}.get(reply.action, "not_approved")}
            guard_execution()
            effort = reply.content.get("activity_effort")
            if effort not in EFFORTS:
                raise HandoffReplyError("choose low, medium or high in the native form")
            return await asyncio.to_thread(self._execute, preview, effort)

    def _execute(self, preview: HandoffPreview, effort: str) -> dict:
        guard_execution()
        if prepare(self.root, preview.slug, preview.report_uri) != preview:
            raise HandoffStaleError("the base, accepted plan or policy changed after review")
        position = locate(self.root)
        guard_execution()
        try:
            if preview.existing:
                notices = []
                setup, synced = _prepare(
                    Path(preview.worktree),
                    preview.setup,
                    self.root.relative_to(position.base),
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
                    project=self.root.relative_to(position.base),
                    revision=preview.head,
                    before_step=lambda _step: guard_execution(),
                )
        except AdvisoryError as exc:
            return {
                "status": "needs_recovery" if Path(preview.worktree).exists() else "blocked",
                "worktree": {"path": preview.worktree, "created": Path(preview.worktree).exists()},
                "activity_effort": effort,
                "errors": [exc.to_dict()],
                "notices": [],
            }
        result = {
            "status": "needs_recovery",
            "worktree": started.to_dict(),
            "activity_effort": effort,
            "errors": [],
            "notices": [item.to_dict() for item in started.notices],
        }
        if any(item.code in {"WORKTREE_SETUP_FAILED", "WORKTREE_SYNC_FAILED"} for item in started.notices):
            return result
        root = started.path / self.root.relative_to(position.base)
        try:
            if run_git(root, "rev-parse", "HEAD").decode().strip() != preview.head:
                raise HandoffStaleError("the new worktree no longer contains the reviewed base commit")
            if run_git(root, "status", "--porcelain", "--untracked-files=normal").strip():
                raise HandoffStaleError(
                    "setup changed tracked or untracked worktree files; inspect them before handoff"
                )
            guard_execution()
            handed = handoff_proposal(root, preview.slug)
            guard_execution()
            registered, notices = auto_register(root, handed.dir, source=SOURCE_HANDOFF)
            result.update(
                status="handed_off", handoff=handed.to_dict(), next_command=f"devkit workflow next --unit {handed.dir}"
            )
            result["notices"] += [item.to_dict() for item in handed.notices + notices]
            if registered is not None:
                result["scope_token"] = registered.token
        except AdvisoryError as exc:
            result["errors"] = [exc.to_dict()]
        return result


def create_tools(root: Path) -> tuple[McpTool, ...]:
    from devkit_spec import plan_accept_mcp, proposal_report_mcp

    service = HandoffService(root)

    async def handoff(arguments: dict, confirm: Confirmation) -> dict:
        return await service.handoff(arguments["slug"], arguments["report_uri"], confirm)

    return (
        McpTool(
            "spec_handoff",
            "Review an accepted proposal summary and exact live report URI in one native form, select activity effort defaulted from dev_effort, then explicitly approve starting local Development. Creates dev-<slug> and its worktree and runs proposal handoff only after approval. Decline, cancellation or unavailable confirmation makes no changes. Changed base or policy requires fresh review. Returns selected effort as run input; the caller continues in the returned worktree and records effort in its worker envelope. Does not approve or execute final merge.",
            {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$", "maxLength": 59},
                    "report_uri": {"type": "string", "minLength": 1},
                },
                "required": ["slug", "report_uri"],
                "additionalProperties": False,
            },
            handoff,
            destructive=True,
            open_world=True,
        ),
        *proposal_report_mcp.create_tools(root),
        *plan_accept_mcp.create_tools(root),
    )
