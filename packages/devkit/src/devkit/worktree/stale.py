"""Stale activity branches: ``plan-*`` and ``dev-*`` branches nobody has moved for ``[worktree] stale_after``.

A branch's last activity is the later of its last commit (over its local branch and every remote-tracking copy) and
the last update of its pull request on GitHub. The check runs only when ``gh auth status`` succeeds; otherwise it
reports a ``WORKTREE_STALE_SKIPPED`` notice and judges nothing. A ``gh pr list`` that fails judges by the last commit
alone (``WORKTREE_STALE_PR_UNKNOWN``). Nothing is cleaned up: each stale branch becomes a ``WORKTREE_STALE_BRANCH``
warning whose ``[FIX]`` names how to resume it and, once the user decides, how to discard it.

``hygiene`` is the ``devkit.hygiene`` extension that shows the warnings in ``devkit rules check -p hygiene``.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from devkit_core.base.errors import GitError
from devkit_core.core.git import run_git

from devkit.advisory import AdvisoryError
from devkit.worktree.config import parse_period, read_worktree_config
from devkit.worktree.errors import (
    StaleBranchWarning,
    StalePullRequestsUnknownNotice,
    StaleSkippedNotice,
    UnsupportedLayoutError,
)
from devkit.worktree.lifecycle import BRANCH, BRANCH_LIMIT, UNIT_KEY, Position, locate

GH_TIMEOUT = 60.0  # seconds for one gh call
PR_LIMIT = 1000  # pull requests read in one `gh pr list`
PR_FIELDS = "headRefName,state,isDraft,mergeStateStatus,updatedAt,url"

# ``gh`` run in a directory with arguments: its exit code and stdout (exit 127 when gh is missing, 124 on timeout).
GhRunner = Callable[[Path, list[str]], tuple[int, str]]


def run_gh(cwd: Path, args: list[str]) -> tuple[int, str]:
    """Run ``gh`` with ``args`` in ``cwd`` without a prompt; its exit code and stdout."""
    env = {**os.environ, "GH_PROMPT_DISABLED": "1", "NO_COLOR": "1"}
    try:
        completed = subprocess.run(
            ["gh", *args],
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            timeout=GH_TIMEOUT,
        )
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""
    return completed.returncode, os.fsdecode(completed.stdout)


@dataclass(frozen=True)
class StaleBranch:
    branch: str
    unit: str | None  # the unit `attach` recorded (`devkitUnit`), if any
    last_activity: datetime  # UTC
    pr: str  # none | draft | open | blocked | merged | closed | unknown (gh pr list failed)
    pr_url: str | None
    refs: tuple[str, ...]  # where the branch exists: "local" and remote names

    def source(self) -> str:
        """The ``--existing-branch`` value that resumes the branch: local first, else the first remote's copy."""
        return self.branch if "local" in self.refs else f"{self.refs[0]}/{self.branch}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "unit": self.unit,
            "last_activity": _iso(self.last_activity),
            "pr": self.pr,
            "pr_url": self.pr_url,
            "refs": list(self.refs),
        }

    def warning(self, base: Path, stale_after: str) -> StaleBranchWarning:
        quoted = shlex.quote(str(base))
        remotes = [ref for ref in self.refs if ref != "local"]
        discard = [f"devkit worktree finish {self.branch} --discard -w {quoted}"] if "local" in self.refs else []
        discard += [f"git -C {quoted} push {shlex.quote(remote)} --delete {self.branch}" for remote in remotes]
        pr = " close its pull request," if self.pr in {"draft", "open", "blocked"} else ""
        return StaleBranchWarning(
            f"activity branch {self.branch} has had no activity since {_iso(self.last_activity)}, longer than"
            f" [worktree] stale_after = {stale_after!r} (pull request: {self.pr})",
            f"unit: {self.unit or '-'}",
            f"refs: {', '.join(self.refs)}",
            *([f"pull request: {self.pr_url}"] if self.pr_url else []),
            fix=f"To resume it, devkit worktree start {self.branch} --existing-branch {self.source()} --unit"
            f" {self.unit or '<unit directory>'}; to discard it, only once the user decides:{pr} "
            + " && ".join(discard),
        )


@dataclass
class StaleResult:
    checked: bool  # False when gh is missing or not logged in
    stale_after: str
    branches: int  # activity branches examined
    stale: list[StaleBranch] = field(default_factory=list)
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked": self.checked,
            "stale_after": self.stale_after,
            "branches": self.branches,
            "stale": [item.to_dict() for item in self.stale],
            "notices": [notice.to_dict() for notice in self.notices],
        }


def _iso(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _activity_branches(base: Path) -> dict[str, tuple[datetime, list[str]]]:
    """Every ``plan-*``/``dev-*`` branch, local or remote-tracking: its latest commit time and where it exists."""
    remotes = sorted(os.fsdecode(run_git(base, "remote")).split(), key=len, reverse=True)
    listing = os.fsdecode(
        run_git(base, "for-each-ref", "--format=%(refname)%00%(committerdate:unix)", "refs/heads", "refs/remotes")
    )
    found: dict[str, tuple[datetime, list[str]]] = {}
    for line in listing.splitlines():
        ref, _, stamp = line.partition("\0")
        if ref.startswith("refs/heads/"):
            name, where = ref.removeprefix("refs/heads/"), "local"
        else:
            remote = next((r for r in remotes if ref.startswith(f"refs/remotes/{r}/")), None)
            if remote is None:
                continue
            name, where = ref.removeprefix(f"refs/remotes/{remote}/"), remote
        if not BRANCH.fullmatch(name) or len(name) > BRANCH_LIMIT or not stamp.isdigit():
            continue
        when = datetime.fromtimestamp(int(stamp), UTC)
        latest, refs = found.get(name, (when, []))
        found[name] = (max(latest, when), [*refs, where])
    return found


def _pull_requests(base: Path, gh: GhRunner) -> dict[str, dict[str, Any]] | None:
    """The latest pull request per head branch, ``None`` when ``gh pr list`` fails."""
    code, out = gh(base, ["pr", "list", "--state", "all", "--limit", str(PR_LIMIT), "--json", PR_FIELDS])
    if code != 0:
        return None
    try:
        items = json.loads(out)
    except ValueError:
        return None
    if not isinstance(items, list):
        return None
    latest: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("headRefName"), str):
            continue
        name = item["headRefName"]
        if name not in latest or str(item.get("updatedAt", "")) > str(latest[name].get("updatedAt", "")):
            latest[name] = item
    return latest


def _pr_state(item: dict[str, Any] | None) -> str:
    if item is None:
        return "none"
    state = item.get("state")
    if state == "MERGED":
        return "merged"
    if state == "CLOSED":
        return "closed"
    if item.get("isDraft"):
        return "draft"
    return "blocked" if item.get("mergeStateStatus") == "BLOCKED" else "open"


def _pr_updated(item: dict[str, Any] | None) -> datetime | None:
    value = item.get("updatedAt") if item else None
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def stale_branches(
    position: Position, stale_after: str = "14d", *, gh: GhRunner | None = None, now: datetime | None = None
) -> StaleResult:
    """The activity branches idle longer than ``stale_after`` (``<N>d`` or ``<N>w``), most idle first.

    ``gh`` runs the GitHub CLI (``run_gh`` when ``None``, looked up at call time); ``now`` defaults to the clock.
    """
    gh = gh or run_gh
    period = parse_period(stale_after)
    base = position.base
    code, _ = gh(base, ["auth", "status"])
    if code != 0:
        reason = "gh is not installed" if code == 127 else "gh auth status failed"
        return StaleResult(
            False,
            stale_after,
            0,
            notices=[
                StaleSkippedNotice(
                    f"{reason}, so activity branches were not checked for staleness",
                    fix="Log in with gh auth login to have stale plan-*/dev-* branches reported",
                )
            ],
        )
    branches = _activity_branches(base)
    pulls = _pull_requests(base, gh) if branches else {}
    notices: list[AdvisoryError] = []
    if pulls is None:
        notices.append(
            StalePullRequestsUnknownNotice(
                "gh pr list failed, so activity branches were judged by their last commit alone",
                fix="Check gh pr list in this repository, then rerun",
            )
        )
    moment = now or datetime.now(UTC)
    stale: list[StaleBranch] = []
    for name, (committed, refs) in sorted(branches.items()):
        item = pulls.get(name) if pulls is not None else None
        updated = _pr_updated(item)
        last = max(committed, updated) if updated is not None else committed
        if moment - last <= period:
            continue
        unit = _unit(base, name, refs)
        state = _pr_state(item) if pulls is not None else "unknown"
        url = item.get("url") if item and isinstance(item.get("url"), str) else None
        stale.append(StaleBranch(name, unit, last, state, url, tuple(refs)))
    stale.sort(key=lambda item: (item.last_activity, item.branch))
    return StaleResult(True, stale_after, len(branches), stale, notices)


def _unit(base: Path, branch: str, refs: list[str]) -> str | None:
    """The unit ``attach`` recorded for the branch, while the branch still holds it (a handoff replaces a proposal
    with its spec, so the recorded directory can be gone): ``None`` otherwise, for the caller to map the slug."""
    try:
        value = os.fsdecode(run_git(base, "config", "--local", "--get", f"branch.{branch}.{UNIT_KEY}")).strip()
    except GitError:
        return None
    if not value:
        return None
    remotes = [ref for ref in refs if ref != "local"]
    tip = f"refs/heads/{branch}" if "local" in refs else f"refs/remotes/{remotes[0]}/{branch}" if remotes else None
    if tip is None:
        return None
    try:
        kind = os.fsdecode(run_git(base, "cat-file", "-t", f"{tip}:{value}")).strip()
    except GitError:
        return None
    return value if kind == "tree" else None


def hygiene(root: Path) -> list[AdvisoryError] | None:
    """The ``devkit.hygiene`` extension: each stale activity branch of the checkout at ``root`` as a warning.

    Outside a Git work tree, or in a layout ``devkit worktree`` does not support, there is nothing to judge.
    """
    try:
        position = locate(root)
    except (GitError, UnsupportedLayoutError):
        return None
    config = read_worktree_config(root)
    result = stale_branches(position, config.stale_after)
    return [*result.notices, *(item.warning(position.base, config.stale_after) for item in result.stale)]
