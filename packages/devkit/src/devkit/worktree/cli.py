"""``devkit worktree`` commands: start a slug's task worktree, finish it after the merge, report leftovers.

Text output: ``start`` prints ``[WORKTREE_STARTED: <slug> path= branch= base= created= setup= synced=]`` and
``[NEXT_CMD: cd <path>]``; ``finish`` prints ``[WORKTREE_FINISHED: <slug> path= merged= push= removed=
branch_deleted=]``, also before a refusal that stopped it after the merge; ``status`` prints one
``[WORKTREE: <path> ...]`` line per worktree, one ``[BRANCH: <name> head=]`` line per unmerged branch no
worktree checks out, and ``[SUMMARY: ...]``. ``--format json`` prints the result object (a refused
``finish`` that changed something adds ``errors``). ``status`` only reports and exits ``0``.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

import click

from devkit.core.cli import (
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
from devkit.core.project import find_project_root
from devkit.worktree.config import WorktreeConfig, read_worktree_config
from devkit.worktree.errors import WorktreeError
from devkit.worktree.extensions import run_post_finish
from devkit.worktree.lifecycle import FinishResult, Position, finish, locate, start, status

WORKSPACE = workspace_option("Any directory inside the checkout [default: the current directory]")
SLUG = click.argument("slug")
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
    position, project = locate(start), find_project_root(start)
    relative = project.relative_to(position.root) if project.is_relative_to(position.root) else None
    return position, read_worktree_config(project), relative


@click.group(name="worktree")
def cli() -> None:
    """Task worktrees: one checkout per slug, integrated and removed by finish."""


@cli.command(name="start")
@SLUG
@WORKSPACE
@FORMAT_OPTION
@boundary
def start_cmd(slug: str, workspace_root: str | None, output_format: str) -> None:
    """Create (or reuse) <parent>/<repo>-wt-<SLUG> on branch SLUG from the base HEAD.

    A new worktree runs the [worktree] setup command, then `devkit sync --locked` to restore the managed files a
    fresh checkout lacks; continue the task in the printed directory.
    """
    position, config, project = _position(workspace_root)
    result = start(position, slug, setup=config.setup, project=project)
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        click.echo(
            f"[WORKTREE_STARTED: {_value(result.slug)} path={_value(result.path)} branch={_value(result.branch)}"
            f" base={_value(result.base)} created={_value(result.created)} setup={_value(result.setup)}"
            f" synced={_value(result.synced)}]"
        )
        click.echo(f"[NEXT_CMD: cd {shlex.quote(str(result.path))}]")
    echo_notices(result.notices)
    exit_on_warnings(result.notices)


def _finished(result: FinishResult) -> str:
    return (
        f"[WORKTREE_FINISHED: {_value(result.slug)} path={_value(result.path)} merged={_value(result.merged)}"
        f" push={_value(result.push)} removed={_value(result.removed)}"
        f" branch_deleted={_value(result.branch_deleted)}]"
    )


@cli.command(name="finish")
@SLUG
@WORKSPACE
@click.option(
    "--merge",
    is_flag=True,
    help="Fast-forward the base onto the branch and push it to its upstream first (refused under [worktree] pull_request = true)",
)
@FORMAT_OPTION
@boundary
def finish_cmd(slug: str, workspace_root: str | None, merge: bool, output_format: str) -> None:
    """Integrate SLUG's branch into the base, then remove its worktree and branch; run it from the base.

    Without --merge the branch must already be merged (for example through its pull request). Rerun the
    same command after resolving a refusal: the steps already done are skipped.
    """
    position, config, _ = _position(workspace_root)
    try:
        result = finish(
            position, slug, merge=merge, pull_request=config.pull_request, delete_branch=config.delete_branch
        )
    except WorktreeError as error:
        partial = error.result
        if not isinstance(partial, FinishResult):
            raise
        if is_json(output_format):
            echo_json(partial.to_dict() | {"errors": [error.to_dict()]})
        else:
            click.echo(_finished(partial))
        echo_notices(partial.notices)
        raise Reported(error) from error
    result.notices.extend(run_post_finish(position.base, result.to_dict()))
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        click.echo(_finished(result))
    echo_notices(result.notices)
    exit_on_warnings(result.notices)


@cli.command(name="status")
@WORKSPACE
@FORMAT_OPTION
@boundary
def status_cmd(workspace_root: str | None, output_format: str) -> None:
    """List every worktree with its branch, merge and dirty state, and the unmerged branches no worktree checks out.

    Changes nothing. A merged, clean linked worktree is finished with `devkit worktree finish <slug>`; remove
    anything unmerged, dirty or prunable only with the user's authorization.
    """
    result = status(_position(workspace_root)[0])
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
