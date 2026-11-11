"""``devkit spec scope collect|release|sweep``: Host scope observation and the registry's record removal.

Text output (paths are workspace-relative):

- ``collect``: ``[SCOPE_CANDIDATE: ...]``, ``[SCOPE_OBSERVATION: ...]``, ``[PAIR: ...]`` with its ``[EVIDENCE: <path>
  ...]`` lines and ``[SUMMARY: ...]`` (``cli.collection_output``);
- ``release``: ``[SCOPE_RELEASE: <task> released=yes|no registered= already= revision=]``;
- ``sweep``: ``[SWEEP: <task> verdict=active|stale|unverifiable|error|removed reason= revision=]`` and
  ``[SUMMARY: namespace= active= stale= unverifiable= error= removed=]``.

Warnings (unreadable records, partial collection coverage) follow the result on stderr. Contract:
``CAP-COLL-work-scope-registry``.
"""

from __future__ import annotations

from collections.abc import Sequence

import click
from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    Reported,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    fields_line,
    is_json,
    resolve_root,
    sentinel,
    workspace_option,
)

from devkit_spec.features.scope.usecases.flow import ReleaseScopeUseCase, open_session
from devkit_spec.features.scope.usecases.sweep import SweepScopesUseCase


@click.group(name="scope")
def scope_group() -> None:
    """Observe host-visible work scopes with collect; release removes this worktree's registry record."""


def _finish(notices: Sequence[AdvisoryError]) -> None:
    echo_notices(notices)
    exit_on_warnings(notices)


# --- release ----------------------------------------------------------------------------------------------------


@scope_group.command(name="release")
@click.option("--task-id", default=None, help="Release this record; this worktree's token must own it")
@workspace_option()
@FORMAT_OPTION
@boundary
def release_cmd(task_id: str | None, workspace_root: str | None, output_format: str) -> None:
    """Remove this worktree's record with its saved token and delete the token.

    Repeating it, or running it in a worktree that registered nothing, changes nothing and succeeds.
    """
    root = resolve_root(workspace_root)
    released = ReleaseScopeUseCase().execute(open_session(root), task_id or None)
    fields = {
        "released": released.registered and not released.already,
        "registered": released.registered,
        "already": released.already,
        "revision": released.revision or None,
    }
    if is_json(output_format):
        echo_json(
            {"task": released.task or None, **fields} | {"notices": [notice.to_dict() for notice in released.notices]}
        )
    else:
        click.echo(sentinel("SCOPE_RELEASE", released.task, **fields))
    _finish(released.notices)


# --- sweep ------------------------------------------------------------------------------------------------------


def _expected(expects: Sequence[str]) -> dict[str, int]:
    expected: dict[str, int] = {}
    for item in expects:
        task, separator, revision = item.partition("=")
        if not separator or not task or not revision.isdigit():
            raise ArgumentError(
                f"--expect {item!r}: expected <task-id>=<revision>",
                target_files=["--expect"],
                fix="Pass --expect SPEC-x=3 with the revision a previous sweep reported",
            )
        expected[task] = int(revision)
    return expected


@scope_group.command(name="sweep", hidden=True)
@click.option("--apply", "apply", is_flag=True, help="Remove the stale records whose revision is unchanged")
@click.option(
    "--expect",
    "expects",
    multiple=True,
    help="With --apply: the revision a previous read reported for a task; a record changed since is kept (repeat)",
)
@workspace_option()
@FORMAT_OPTION
@boundary
def sweep_cmd(apply: bool, expects: tuple[str, ...], workspace_root: str | None, output_format: str) -> None:
    """Report stale (worktree gone), unverifiable (other host) and unreadable records; --apply removes stale ones.

    Without --expect, --apply protects each record at the revision this command read first.
    """
    if expects and not apply:
        raise ArgumentError("--expect requires --apply", target_files=["--expect"], fix="Add --apply or drop --expect")
    expected = _expected(expects)
    root = resolve_root(workspace_root)
    session = open_session(root)
    swept = SweepScopesUseCase().execute(session, apply=apply, expected=expected)
    results, summary, notices, error = swept.results, swept.summary, swept.notices, swept.error
    if is_json(output_format):
        document: dict[str, object] = {
            "results": [result.to_dict() for result in results],
            "summary": summary,
            "notices": [notice.to_dict() for notice in notices],
        }
        if error is not None:
            document["errors"] = [error.to_dict()]
        echo_json(document)
    else:
        for result in results:
            click.echo(
                sentinel(
                    "SWEEP", result.task_id, verdict=str(result.verdict), reason=result.reason, revision=result.revision
                )
            )
        click.echo(fields_line("SUMMARY", **summary))
    echo_notices(notices)
    if error is not None:
        raise Reported(error)
    exit_on_warnings(notices)


@scope_group.command(name="collect")
@click.option("--base", default=None, help="Explicit integration-base ref")
@click.option("--fetch", "remotes", multiple=True, help="Refresh one configured remote (repeatable)")
@click.option("--timeout", default=30, type=int, help="Total observation budget in seconds (1..300)")
@click.option("--source-timeout", default=5, type=int, help="Per-source budget in seconds (1..300)")
@workspace_option()
@FORMAT_OPTION
@boundary
def collect_cmd(
    base: str | None,
    remotes: tuple[str, ...],
    timeout: int,
    source_timeout: int,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Observe registry snapshots, plan-*/dev-* refs and accessible worktrees without modifying registrations."""
    from devkit_spec.features.scope.models.observation import CollectionOptions
    from devkit_spec.features.scope.usecases.collection import CollectScopesUseCase

    report = CollectScopesUseCase().execute(
        resolve_root(workspace_root), CollectionOptions(base, remotes, timeout, source_timeout)
    )
    if is_json(output_format):
        echo_json(report.data)
    else:
        render_collection(report.data)
    _finish(report.notices)


def render_collection(data: dict[str, object]) -> None:
    """Render the bounded report without exposing owner tokens."""
    from devkit_spec.features.scope.cli.collection_output import render

    render(data)
