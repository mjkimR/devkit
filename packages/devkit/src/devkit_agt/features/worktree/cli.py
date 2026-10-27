"""``devkit worktree`` commands: start an activity branch (with its worktree, without one, or attached to an existing
branch), finish it after the merge, report leftovers and stale branches.

Text output: ``start`` prints ``[WORKTREE_STARTED: <branch> path= base= created= existing= unit= setup= synced=]``
and ``[NEXT_CMD: cd <path>]``, or with ``--no-worktree`` ``[BRANCH_STARTED: <branch> checkout= from=]``; ``finish``
prints ``[WORKTREE_FINISHED: <branch> path= merged= push= removed= branch_deleted=]``, also before a refusal that
stopped it after the merge; ``status`` prints one ``[WORKTREE: <path> ...]`` line per worktree, one ``[BRANCH:
<name> head=]`` line per unmerged branch no worktree checks out, and ``[SUMMARY: ...]``; ``status --stale`` prints
one ``[STALE_BRANCH: <branch> ...]`` line per stale activity branch and ``[SUMMARY: checked= branches= stale=
stale_after=]``. ``--format json`` prints the result object (a refused ``finish`` that changed something adds
``errors``). ``status``, with or without ``--stale``, only reports and exits ``0``.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

import click
from devkit_core.base.errors import ArgumentError
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    Reported,
    boundary,
    echo_json,
    echo_notices,
    existing_directory,
    exit_on_warnings,
    is_json,
    workspace_option,
)

from devkit_agt.features.worktree.models.config import WorktreeConfig
from devkit_agt.features.worktree.models.errors import WorktreeError
from devkit_agt.features.worktree.usecases.configured import FinishActivity, LocateProject, StartActivity
from devkit_agt.features.worktree.usecases.lifecycle import (
    FinishResult,
    Position,
    StartBranch,
    WorktreeStatusQuery,
)
from devkit_agt.features.worktree.usecases.stale import StaleBranches

WORKSPACE = workspace_option("Any directory inside the checkout [default: the current directory]")
BRANCH = click.argument("branch")
_BARE = re.compile(r'[^\s"\]=]+')


def _value(value: object) -> str:
    """``-`` when empty, ``yes``/``no`` for a boolean, bare without spaces, quotes or brackets, else a JSON string."""
    if value is None or value == "":
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    text = str(value)
    return text if _BARE.fullmatch(text) else json.dumps(text, ensure_ascii=False)


def _position(workspace_root: str | None) -> tuple[Position, WorktreeConfig, Path | None]:
    """The checkout containing ``--workspace-root`` (default: the current directory), its devkit project's
    ``[worktree]`` settings, and that project's directory relative to the checkout (``None`` outside it)."""
    start = existing_directory(workspace_root) if workspace_root is not None else Path.cwd()
    return LocateProject().execute(start)


@click.group(name="worktree")
def cli() -> None:
    """Task worktrees: one checkout per activity branch (plan-<slug>, dev-<slug>), integrated and removed by finish."""


@cli.command(name="start")
@BRANCH
@WORKSPACE
@click.option(
    "--no-worktree",
    is_flag=True,
    help="Create the branch at the current HEAD and switch this checkout to it, carrying uncommitted changes",
)
@click.option(
    "--existing-branch",
    "existing",
    default=None,
    metavar="BRANCH|REMOTE/BRANCH",
    help="Attach a worktree to the existing BRANCH (local, or a fetched remote-tracking copy) instead of creating it",
)
@click.option(
    "--unit", default=None, help="With --existing-branch: the unit directory on the branch (project-relative)"
)
@FORMAT_OPTION
@boundary
def start_cmd(
    branch: str,
    workspace_root: str | None,
    no_worktree: bool,
    existing: str | None,
    unit: str | None,
    output_format: str,
) -> None:
    """Create <parent>/<repo>-wt-<BRANCH> on the new activity branch BRANCH (plan-<slug> or dev-<slug>).

    A branch that exists locally or on a remote is refused; continue it with --existing-branch BRANCH --unit DIR,
    which attaches a worktree to it after checking that the branch is in sync with its remote and holds the unit.
    --no-worktree creates the branch in this checkout instead. A new worktree runs the [worktree] setup command,
    then `devkit sync --locked` to restore the managed files a fresh checkout lacks; continue the task in the
    printed directory.
    """
    if no_worktree and (existing is not None or unit is not None):
        raise ArgumentError(
            "--no-worktree starts a new branch; --existing-branch and --unit attach a worktree to an existing one",
            target_files=["--no-worktree"],
            fix="Drop --no-worktree, or drop --existing-branch and --unit",
        )
    if (existing is None) != (unit is None):
        raise ArgumentError(
            "--existing-branch and --unit go together",
            target_files=["--unit"] if unit is None else ["--existing-branch"],
            fix="Add --unit with the unit directory the branch holds, relative to the devkit project"
            if unit is None
            else f"Add --existing-branch {branch}",
        )
    position, config, project = _position(workspace_root)
    if no_worktree:
        started = StartBranch().execute(position, branch)
        if is_json(output_format):
            echo_json(started.to_dict())
        else:
            click.echo(
                f"[BRANCH_STARTED: {_value(started.branch)} checkout={_value(started.checkout)}"
                f" from={_value(started.started_from)}]"
            )
        echo_notices(started.notices)
        exit_on_warnings(started.notices)
        return
    result = StartActivity().execute(position, config, project, branch, existing=existing, unit=unit)
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        click.echo(
            f"[WORKTREE_STARTED: {_value(result.branch)} path={_value(result.path)} base={_value(result.base)}"
            f" created={_value(result.created)} existing={_value(result.existing)} unit={_value(result.unit)}"
            f" setup={_value(result.setup)} synced={_value(result.synced)}]"
        )
        click.echo(f"[NEXT_CMD: cd {shlex.quote(str(result.path))}]")
    echo_notices(result.notices)
    exit_on_warnings(result.notices)


def _finished(result: FinishResult, kind: str = "WORKTREE_FINISHED") -> str:
    """The finish result line; ``WORKTREE_FINISH_PARTIAL`` for the progress of a run a refusal stopped."""
    return (
        f"[{kind}: {_value(result.branch)} path={_value(result.path)} merged={_value(result.merged)}"
        f" push={_value(result.push)} removed={_value(result.removed)}"
        f" branch_deleted={_value(result.branch_deleted)} discarded={_value(result.discarded)}]"
    )


@cli.command(name="finish")
@BRANCH
@WORKSPACE
@click.option(
    "--merge",
    is_flag=True,
    help="Land the branch on the base first (a merge commit, or a fast-forward under [worktree] merge ="
    ' "ff-only"; the branch must contain the base HEAD) and push the base to its upstream (refused under'
    ' [worktree] pull_request = "required")',
)
@click.option(
    "--discard",
    is_flag=True,
    help="Close: drop the unmerged branch (remove its worktree, git branch -D) on the authority the close needs",
)
@FORMAT_OPTION
@boundary
@click.option("--local-only", is_flag=True, help="Exclude fetch and push; keep all local merge and cleanup guards")
def finish_cmd(
    branch: str, workspace_root: str | None, merge: bool, discard: bool, output_format: str, local_only: bool
) -> None:
    """Integrate BRANCH into the base, then remove its worktree and the branch; run it from the base.

    Without --merge the branch must already be merged (for example through its pull request). With --merge the
    installed devkit.finish_guard extensions check the branch first (WORKTREE_BLOCKED), the devkit integration lock
    of the common Git directory is taken (LOCK_HELD while another integration runs), and the base fast-forwards onto
    a merge commit built from the base HEAD and the branch tip (onto the tip under [worktree] merge = "ff-only" in
    the base's or the branch's policy); a branch that does not contain the base HEAD is WORKTREE_MERGE_NOT_FF, and
    one the base already contains builds nothing. --discard closes a task
    instead: the branch is dropped unmerged, only on the authority its close needs. Rerun the same command after
    resolving a refusal: the steps already done are skipped.
    """
    if merge and discard:
        raise ArgumentError("--merge and --discard exclude each other", target_files=["--discard"])
    position, config, _ = _position(workspace_root)
    try:
        result = FinishActivity().execute(
            position, config, branch, merge=merge, discard_branch=discard, local_only=local_only
        )
    except WorktreeError as error:
        partial = error.result
        if not isinstance(partial, FinishResult):
            raise
        if is_json(output_format):
            echo_json(partial.to_dict() | {"errors": [error.to_dict()]})
        else:
            click.echo(_finished(partial, "WORKTREE_FINISH_PARTIAL"))
        echo_notices(partial.notices)
        raise Reported(error) from error
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        click.echo(_finished(result))
    echo_notices(result.notices)
    exit_on_warnings(result.notices)


@cli.command(name="status")
@click.option("--stale", is_flag=True, help="Show idle activity branches instead of worktrees (optional gh query)")
@WORKSPACE
@FORMAT_OPTION
@boundary
def status_cmd(workspace_root: str | None, output_format: str, stale: bool) -> None:
    """List every worktree with its branch, merge and dirty state, and the unmerged branches no worktree checks out.

    Changes nothing. A merged, clean linked worktree is finished with `devkit worktree finish <branch>`; remove
    anything unmerged, dirty or prunable only with the user's authorization.
    """
    if stale:
        _show_stale(workspace_root, output_format)
        return
    result = WorktreeStatusQuery().execute(_position(workspace_root)[0])
    if is_json(output_format):
        echo_json(result.to_dict())
        return
    for item in result.worktrees:
        click.echo(
            f"[WORKTREE: {_value(item.path)} branch={_value(item.branch)} head={_value(item.head)} role={item.role}"
            f" merged={_value(item.merged)} dirty={_value(item.dirty)} prunable={_value(item.prunable)}]"
        )
    for branch in result.branches:
        click.echo(f"[BRANCH: {_value(branch.name)} head={branch.head} merged=no]")
    linked = [item for item in result.worktrees if item.role == "linked"]
    click.echo(
        f"[SUMMARY: base={_value(result.base)} base_branch={_value(result.base_branch)} worktrees={len(linked)}"
        f" unmerged={sum(item.merged is False for item in linked)} dirty={sum(item.dirty is True for item in linked)}"
        f" branches={len(result.branches)}]"
    )


def _show_stale(workspace_root: str | None, output_format: str) -> None:
    """List the plan-*/dev-* branches idle longer than [worktree] stale_after (needs gh logged in).

    Changes nothing. Each stale branch is also a WORKTREE_STALE_BRANCH warning whose fix names how to resume it and,
    once the user decides, how to discard it; without gh the check is skipped with a notice.
    """
    position, config, _ = _position(workspace_root)
    result = StaleBranches().execute(position, config.stale_after)
    notices = [*result.notices, *(item.warning(position.base, config.stale_after) for item in result.stale)]
    if is_json(output_format):
        echo_json(result.to_dict() | {"notices": [notice.to_dict() for notice in notices]})
    else:
        for item in result.stale:
            data = item.to_dict()
            click.echo(
                f"[STALE_BRANCH: {_value(item.branch)} unit={_value(item.unit)}"
                f" last_activity={data['last_activity']} pr={item.pr} refs={','.join(item.refs)}]"
            )
        click.echo(
            f"[SUMMARY: checked={_value(result.checked)} branches={result.branches} stale={len(result.stale)}"
            f" stale_after={result.stale_after}]"
        )
    echo_notices(notices)
