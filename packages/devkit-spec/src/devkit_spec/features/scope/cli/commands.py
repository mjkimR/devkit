"""``devkit spec scope compare|register|query|update|release|sweep``: work-scope overlaps and the shared registry.

Text output (paths are workspace-relative; ``<a>``/``<b>`` are spec, proposal or task IDs):

- ``[PAIR: a= b= docs= code= unresolved=]`` per compared pair, each followed by its
  ``[EVIDENCE: <path> a= b= kind=doc|code granularity= other= source= other_source=]`` lines;
- ``compare``: ``[DIFF: <path> set= in=target-docs|reconcile]`` and ``[UNRESOLVED: <value> set= reason=]`` per set,
  then ``[SUMMARY: sets= pairs= overlapping=]``;
- ``register``: ``[SCOPE: <task> namespace= revision= scopes= unresolved= shared_path= token=]``, the only place
  the owner token is ever printed;
- ``query``: ``[RECORD: <task> revision= worktree= host= spec= scopes= unresolved= shared_worktree= own=]``, the
  pairs, then ``[SUMMARY: namespace= records= pairs= overlapping= problems=]``; with ``--history``,
  ``[EVENT: <event> at= ...]`` per page event, ``[PAGE: limit= total= next_cursor=]`` and
  ``[SUMMARY: namespace= events= problems=]``;
- ``update``: the pairs of this task with the others, then
  ``[SCOPE_ACK: status=applied|failed|stale|timeout revision= added= removed= overlaps= unresolved= request_id=]``;
- ``release``: ``[SCOPE: <task> released=yes|no registered= already= revision=]``;
- ``sweep``: ``[SWEEP: <task> verdict=active|stale|unverifiable|error|removed reason= revision=]`` and
  ``[SUMMARY: namespace= active= stale= unverifiable= error= removed=]``.

A failed update prints its ACK, then its ``SPEC_SCOPE_*`` error. Warnings (unreadable records or journal lines, a
journal that cannot be written, a shared worktree) follow the result on stderr. Contract: ``CAP-COLL-work-scope-registry``.
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
    is_json,
    resolve_root,
    workspace_option,
)

from devkit_spec.features.scope import (
    Event,
    PairResult,
    Record,
    Session,
    open_session,
)
from devkit_spec.features.scope.cli.output import echo_registered, registered_dict
from devkit_spec.features.scope.usecases.flow import RegisterScopeUseCase, ReleaseScopeUseCase, UpdateScopeUseCase
from devkit_spec.features.scope.usecases.history import QueryScopeHistoryUseCase
from devkit_spec.features.scope.usecases.query import (
    CompareScopesUseCase,
    QueryScopesUseCase,
    _record_warnings,
    _spec_dir,
)
from devkit_spec.features.scope.usecases.sweep import SweepScopesUseCase
from devkit_spec.utils.output import fields_line, sentinel


@click.group(name="scope")
def scope_group() -> None:
    """Compare declared work scopes and share them between worktrees through a registry."""


# --- shared rendering -------------------------------------------------------------------------------------------


def _echo_pairs(pairs: Sequence[PairResult]) -> None:
    for pair in pairs:
        click.echo(
            fields_line(
                "PAIR", a=pair.a, b=pair.b, docs=len(pair.docs), code=len(pair.code), unresolved=pair.unresolved
            )
        )
        for item in pair.docs:
            click.echo(
                sentinel("EVIDENCE", item.path, a=pair.a, b=pair.b, kind="doc", granularity=str(item.granularity))
            )
        for item in pair.code:
            click.echo(
                sentinel(
                    "EVIDENCE",
                    item.path,
                    a=pair.a,
                    b=pair.b,
                    kind="code",
                    granularity=str(item.granularity),
                    other=item.other,
                    source=str(item.source),
                    other_source=str(item.other_source),
                )
            )


def _finish(notices: Sequence[AdvisoryError]) -> None:
    echo_notices(notices)
    exit_on_warnings(notices)


# --- compare ----------------------------------------------------------------------------------------------------


@scope_group.command(name="compare")
@click.option("--proposal", "proposals", multiple=True, help="Proposal slug (repeat)")
@click.option("--spec", "specs", multiple=True, help="Spec bundle directory (repeat)")
@workspace_option()
@FORMAT_OPTION
@boundary
def compare_cmd(
    proposals: tuple[str, ...], specs: tuple[str, ...], workspace_root: str | None, output_format: str
) -> None:
    """Compare the declared scopes of two or more proposals and spec bundles pairwise, without the registry.

    Document overlap is the same target document; code overlap is a declared or candidate path equal to or
    containing the other side's. Unresolved inputs are counted, never read as no overlap.
    """
    if len(proposals) + len(specs) < 2:
        raise ArgumentError(
            "compare needs at least two inputs",
            target_files=["--proposal", "--spec"],
            fix="Pass two or more --proposal <slug> / --spec <dir> options",
        )
    root = resolve_root(workspace_root)
    sets, pairs, summary = CompareScopesUseCase().execute(root, proposals, specs)
    if is_json(output_format):
        echo_json(
            {"sets": [item.to_dict() for item in sets], "pairs": [pair.to_dict() for pair in pairs], "summary": summary}
        )
        return
    _echo_pairs(pairs)
    for item in sets:
        for diff in item.diff:
            click.echo(sentinel("DIFF", diff.path, set=item.id, **{"in": diff.side}))
        for unresolved in item.unresolved:
            click.echo(sentinel("UNRESOLVED", unresolved.value, set=item.id, reason=unresolved.reason))
    click.echo(fields_line("SUMMARY", **summary))


# --- register ---------------------------------------------------------------------------------------------------


@scope_group.command(name="register")
@click.option("--spec", "spec_dir", default=None, help="Spec bundle directory of this worktree's task")
@click.option("--task-id", default=None, help="Task ID in the namespace [default: the spec ID]")
@workspace_option()
@FORMAT_OPTION
@boundary
def register_cmd(spec_dir: str | None, task_id: str | None, workspace_root: str | None, output_format: str) -> None:
    """Register this worktree's task scope and print its owner token once.

    The record carries the bundle's declared scope and what Git observes in the worktree; the token is saved in
    the worktree's Git directory and is what update and release use.
    """
    root = resolve_root(workspace_root)
    relative = _spec_dir(root, spec_dir)
    registered = RegisterScopeUseCase().execute(open_session(root), relative, task_id or None)
    if is_json(output_format):
        echo_json(
            registered_dict(registered.location, registered.record, registered.token)
            | {"notices": [notice.to_dict() for notice in registered.notices]}
        )
    else:
        echo_registered(registered.location, registered.record, registered.token)
    _finish(registered.notices)


# --- query ------------------------------------------------------------------------------------------------------


def _record_line(record: Record, mine: bool) -> str:
    return sentinel(
        "RECORD",
        record.task_id,
        revision=record.revision,
        worktree=record.worktree,
        host=record.hostname,
        spec=record.spec,
        scopes=len(record.scopes),
        unresolved=len(record.unresolved),
        shared_worktree=record.shared_worktree,
        own=mine,
    )


@scope_group.command(name="query")
@click.option(
    "--spec",
    "spec_dir",
    default=None,
    help="Compare this bundle's declared scope with every record not owned by this worktree",
)
@click.option("--history", is_flag=True, help="Print the namespace's event journal instead of the records")
@click.option("--task", default=None, help="With --history: only the events whose task ID or slug is this value")
@click.option("--limit", type=click.IntRange(1, 100), default=None, help="With --history: page size [default: 50]")
@click.option("--cursor", default=None, help="With --history: continue to older events using next_cursor")
@workspace_option()
@FORMAT_OPTION
@boundary
def query_cmd(
    spec_dir: str | None,
    history: bool,
    task: str | None,
    limit: int | None,
    cursor: str | None,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """List the namespace's records and the overlaps of this worktree's task with the others, or the journal.

    Without a registration in this worktree every pair of records is compared. The token is never printed.
    """
    if (task is not None or limit is not None or cursor is not None) and not history:
        raise ArgumentError(
            "--task, --limit and --cursor filter the event journal and need --history",
            target_files=["--task", "--limit", "--cursor"],
            fix="Add --history, or drop the history options",
        )
    if history and spec_dir is not None:
        raise ArgumentError("--spec and --history cannot be combined", target_files=["--spec", "--history"])
    root = resolve_root(workspace_root)
    session = open_session(root)
    if history:
        _history(session, task, limit or 50, cursor, output_format)
        return
    mine, others, records, pairs, summary, notices = QueryScopesUseCase().execute(root, session, spec_dir)
    if is_json(output_format):
        echo_json(
            {
                "own": mine.public_dict() if mine else None,
                "records": [record.public_dict() for record in others],
                "pairs": [pair.to_dict() for pair in pairs],
                "summary": summary,
                "notices": [notice.to_dict() for notice in notices],
            }
        )
    else:
        for record in records:
            click.echo(_record_line(record, record is mine))
        _echo_pairs(pairs)
        click.echo(fields_line("SUMMARY", **summary))
    _finish(notices)


def _event_line(event: Event) -> str:
    data = event.to_dict()
    del data["event"], data["at"]
    return sentinel("EVENT", event.event, at=event.at, **data)


def _history(session: Session, task: str | None, limit: int, cursor: str | None, output_format: str) -> None:
    result = QueryScopeHistoryUseCase().execute(session, task=task, limit=limit, cursor=cursor)
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        for event in result.events:
            click.echo(_event_line(event))
        click.echo(fields_line("PAGE", **result.pagination))
        click.echo(fields_line("SUMMARY", **result.summary))
    _finish(result.notices)


# --- update -----------------------------------------------------------------------------------------------------


@scope_group.command(name="update", hidden=True)
@click.option("--spec", "spec_dir", default=None, help="Spec bundle directory of this worktree's task")
@click.option(
    "--request-id",
    default=None,
    help="Retry an update whose outcome was not seen: an ID already applied is answered without a second write",
)
@workspace_option()
@FORMAT_OPTION
@boundary
def update_cmd(spec_dir: str | None, request_id: str | None, workspace_root: str | None, output_format: str) -> None:
    """Recollect the bundle's declared and observed scope, write it to this worktree's record and print the ACK.

    Overlaps in the ACK are information for scheduling and integration order, never a block.
    """
    root = resolve_root(workspace_root)
    relative = _spec_dir(root, spec_dir)
    session = open_session(root)
    ack = UpdateScopeUseCase().execute(session, relative, request_id or None)
    notices = [*_record_warnings(session.location, ack.problems), *ack.notices]
    if is_json(output_format):
        document: dict[str, object] = {
            "ack": ack.to_dict(),
            "pairs": [pair.to_dict() for pair in ack.pairs],
            "notices": [notice.to_dict() for notice in notices],
        }
        if ack.error is not None:
            document["errors"] = [ack.error.to_dict()]
        echo_json(document)
    else:
        _echo_pairs(ack.pairs)
        click.echo(
            fields_line(
                "SCOPE_ACK",
                status=ack.status,
                revision=ack.revision,
                added=ack.added,
                removed=ack.removed,
                overlaps=ack.overlaps,
                unresolved=ack.unresolved,
                request_id=ack.request_id,
            )
        )
    echo_notices(notices)
    if ack.error is not None:
        raise Reported(ack.error)
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
        click.echo(sentinel("SCOPE", released.task, **fields))
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
                fix="Pass --expect SPEC-x=3 with the revision a previous query or sweep reported",
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
@click.option("--mode", default="worktrees", help="Observation inputs: snapshot, refs or worktrees (default)")
@click.option("--base", default=None, help="Explicit integration-base ref")
@click.option("--fetch", "remotes", multiple=True, help="Refresh one configured remote (repeatable)")
@click.option("--timeout", default=30, type=int, help="Total observation budget in seconds (1..300)")
@click.option("--source-timeout", default=5, type=int, help="Per-source budget in seconds (1..300)")
@workspace_option()
@FORMAT_OPTION
@boundary
def collect_cmd(
    mode: str,
    base: str | None,
    remotes: tuple[str, ...],
    timeout: int,
    source_timeout: int,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Observe host-visible work without modifying worker registrations."""
    from devkit_spec.features.scope.models.observation import CollectionOptions
    from devkit_spec.features.scope.usecases.collection import CollectScopesUseCase

    report = CollectScopesUseCase().execute(
        resolve_root(workspace_root), CollectionOptions(mode, base, remotes, timeout, source_timeout)
    )
    if is_json(output_format):
        echo_json(report.data)
    else:
        render_collection(report.data)
    _finish(report.notices)


def render_collection(data: dict[str, object]) -> None:
    """Render the bounded report without exposing maintenance tokens or worker ACKs."""
    from devkit_spec.features.scope.cli.collection_output import render

    render(data)
