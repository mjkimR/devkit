"""``devkit spec resolve``, ``refs`` and ``list``: find documents by ID, follow their references, browse them.

Text output (paths are relative to the workspace root):

- ``resolve``: one ``[DOCUMENT: <id> kind= status= path=]`` line per resolved ID; unresolved or duplicated IDs
  are errors after the lines that did resolve.
- ``refs``: ``[REF: <id> path= status= fields= count=]`` per referenced (``--direction out``) or referencing
  (``--direction in``) document, in ID order; ``path=-`` is a reference to an ID no document declares.
- ``list``: ``[DOCUMENT: <id> kind= status= path= tasks= title=]`` per document in kind, then ID order (feedback by
  severity first); ``tasks`` is ``<checked>/<total>`` of a spec's ``tasks.md``. Proposal lines add ``task_kind=``,
  ``planning_effort=`` and ``dev_effort=`` after ``tasks=``; feedback lines add ``severity=``,
  ``scope=`` and ``target=`` after ``tasks=``. ``--where FIELD=A,B`` keeps documents whose frontmatter ``FIELD``
  is one of the values.

``refs`` and ``list`` end with ``[PAGE: total= offset= limit= count= next=]`` and, when more items follow,
``[NEXT_CMD: ...]`` for the next page. Files that could not be indexed are ``SPEC_DOCUMENT_INVALID`` warnings;
``list --status`` adds a ``SPEC_LIST_STATUS_UNKNOWN`` notice naming the values no document of the selected kinds
carries.
"""

from __future__ import annotations

from collections.abc import Sequence

import click
from devkit.advisory import AdvisoryError
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    exit_on_problems,
    exit_on_warnings,
    is_json,
    resolve_root,
    workspace_option,
)

from devkit_spec.features.documents import Kind
from devkit_spec.features.documents.usecases.browse import (
    ListDocumentsUseCase,
    ReferenceDocumentsUseCase,
    ResolveDocumentsUseCase,
    _feedback_fields,
    _planning_fields,
    _proposal_fields,
    _shown_status,
)
from devkit_spec.utils.output import echo_page, sentinel

WORKSPACE = workspace_option()
LIMIT = click.option("--limit", "-n", type=int, default=20, show_default=True, help="Items per page; 0 for all")
OFFSET = click.option("--offset", type=int, default=0, show_default=True, help="Items to skip")
# Feedback ``severity`` values from the most to the least urgent; any other value, or none, ranks after them.
# The proposal frontmatter fields ``list`` prints on proposal lines and records.
# The feedback frontmatter fields ``list`` prints on feedback lines and records.


NAMESPACE = click.option(
    "--namespace", default=None, help="Show this namespace and the global documents; global shows only those"
)
ALL_NAMESPACES = click.option("--all-namespaces", is_flag=True, help="Show every namespace")


def _paging_args(workspace_root: str | None, limit: int) -> list[str]:
    return [*(["-w", workspace_root] if workspace_root is not None else []), "--limit", str(limit)]


def _finish(notices: Sequence[AdvisoryError]) -> None:
    echo_notices(notices)
    exit_on_warnings(notices)


@click.command(name="resolve")
@click.argument("ids", nargs=-1, required=True, metavar="ID...")
@WORKSPACE
@FORMAT_OPTION
@boundary
def resolve_cmd(ids: tuple[str, ...], workspace_root: str | None, output_format: str) -> None:
    """Print the path of each document ID."""
    found, errors, notices = ResolveDocumentsUseCase().execute(resolve_root(workspace_root), ids)
    if is_json(output_format):
        echo_json(
            {
                "documents": [document.to_dict() for document in found],
                "errors": [error.to_dict() for error in errors],
                "notices": [notice.to_dict() for notice in notices],
            }
        )
    else:
        for document in found:
            click.echo(
                sentinel("DOCUMENT", document.id, kind=document.kind, status=document.status, path=document.path)
            )
    echo_notices(notices)
    exit_on_problems(errors)
    exit_on_warnings(notices)


@click.command(name="refs")
@click.argument("document_id", metavar="ID")
@click.option(
    "--direction",
    type=click.Choice(["out", "in"]),
    default="out",
    show_default=True,
    help="out: the documents ID references; in: the documents that reference ID",
)
@LIMIT
@OFFSET
@WORKSPACE
@FORMAT_OPTION
@boundary
def refs_cmd(
    document_id: str, direction: str, limit: int, offset: int, workspace_root: str | None, output_format: str
) -> None:
    """List the documents a document references, or the documents referencing it."""
    document, keys, items, notices = ReferenceDocumentsUseCase().execute(
        resolve_root(workspace_root), document_id, direction, limit, offset
    )
    if is_json(output_format):
        echo_json(
            {
                "id": document.id,
                "direction": direction,
                "total": len(keys),
                "offset": offset,
                "limit": limit,
                "items": [item.to_dict() for item in items],
                "notices": [notice.to_dict() for notice in notices],
            }
        )
    else:
        for item in items:
            click.echo(
                sentinel(
                    "REF",
                    item.id,
                    path=item.document.path if item.document else None,
                    status=item.document.status if item.document else None,
                    fields=",".join(sorted({ref.field for ref in item.references})),
                    count=len(item.references),
                )
            )
        args = ["refs", document.id, "--direction", direction, *_paging_args(workspace_root, limit)]
        echo_page(len(keys), offset, limit, len(items), args)
    _finish(notices)


@click.command(name="list")
@click.argument("kinds", nargs=-1, type=click.Choice([str(kind) for kind in Kind]), metavar="[KIND]...")
@click.option("--status", "-s", default=None, help="Comma-separated statuses to keep (case-insensitive)")
@click.option("--area", "-a", default=None, help="Keep documents whose frontmatter area contains this text")
@click.option("--query", "query", default=None, help="Keep documents whose ID or title contains this text")
@click.option(
    "--history", is_flag=True, help="Include the files of completed spec bundles (their feedback is always included)"
)
@click.option(
    "--where",
    "where_items",
    multiple=True,
    metavar="FIELD=VALUE[,VALUE...]",
    help="Keep documents whose frontmatter FIELD is one of the values (case-insensitive; a list field when one "
    "element is); repeat to require several fields",
)
@click.option(
    "--file",
    "file",
    default=None,
    help="Keep documents whose frontmatter entrypoints overlap this workspace-relative file or directory",
)
@NAMESPACE
@ALL_NAMESPACES
@LIMIT
@OFFSET
@WORKSPACE
@FORMAT_OPTION
@boundary
def list_cmd(
    kinds: tuple[str, ...],
    status: str | None,
    area: str | None,
    query: str | None,
    history: bool,
    where_items: tuple[str, ...],
    file: str | None,
    namespace: str | None,
    all_namespaces: bool,
    limit: int,
    offset: int,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """List documents of the given KINDs (default: all), current ones only unless --history.

    --file finds the documents that own a code path through their ``entrypoints``; --where filters by any
    frontmatter field, such as a feedback document's severity or scope. Feedback is ordered by severity. KIND is one
    of: capability, story, architecture, decision, proposal, proposal-decision, spec, plan, tasks, reconcile,
    feedback, material. In a workspace with namespaces, the namespace of the current directory (plus the
    global documents) is shown unless --namespace or --all-namespaces says otherwise.
    """
    selected, shown, tasks, notices, scope, planning, where, historical = ListDocumentsUseCase().execute(
        resolve_root(workspace_root),
        kinds,
        status,
        area,
        query,
        file,
        history,
        namespace,
        all_namespaces,
        where_items,
        offset,
        limit,
    )
    if is_json(output_format):
        echo_json(
            {
                "total": len(selected),
                "offset": offset,
                "limit": limit,
                "namespace": scope.selection.name,
                "documents": [
                    document.to_dict()
                    | _planning_fields(document, planning)
                    | {
                        "namespace": scope.namespace_of(document),
                        "historical": historical[document.path],
                        "tasks": tasks[document.path],
                    }
                    | _proposal_fields(document)
                    | _feedback_fields(document)
                    for document in shown
                ],
                "notices": [notice.to_dict() for notice in notices],
            }
        )
    else:
        for document in shown:
            click.echo(
                sentinel(
                    "DOCUMENT",
                    document.id,
                    kind=document.kind,
                    status=_shown_status(document, planning),
                    path=document.path,
                    **{key: value for key, value in _planning_fields(document, planning).items() if key != "status"},
                    tasks=tasks[document.path],
                    **_proposal_fields(document),
                    **_feedback_fields(document),
                    **scope.fields(document),
                    title=document.title,
                )
            )
        args = ["list", *kinds]
        for flag, given in (("--status", status), ("--area", area), ("--query", query), ("--file", file)):
            if given is not None:
                args += [flag, given]
        args += ["--history"] if history else []
        for item in where:
            args += ["--where", item.given]
        args += scope.args(namespace, all_namespaces)
        echo_page(len(selected), offset, limit, len(shown), [*args, *_paging_args(workspace_root, limit)])
    _finish(notices)
