"""``devkit spec entrypoints derive``: derive capability/use case entrypoints from spec bundles, and write chosen ones.

Text output (paths are workspace-relative):

- ``[CANDIDATES: <doc-id> path= new= missing= folded= declared=]`` per document, in document path order: its
  candidate paths by state, comma-separated (``-`` for none). ``new`` paths exist and are not declared yet,
  ``missing`` ones are new but absent from the working tree, ``folded`` ones are covered by a same-bundle ancestor
  candidate, ``declared`` ones are already covered by an entrypoint. With ``--all`` each path carries its spec count,
  ``src/a.py(2)``. ``--format json`` lists every pair with its spec and task (or count and specs);
- ``[SKIPPED_COUNT: <reason> kind=boundary|target|bundle|apply count=]`` per kind and reason of the inputs or
  candidates left out; with ``--skipped`` instead ``[SKIPPED: <value> kind= reason=]`` per item, with ``spec=`` and
  ``task=`` when known (JSON: ``skipped`` holds the counts, or the items with ``--skipped``);
- ``[APPLIED: <doc-id> path= added=]`` per document ``--apply`` wrote;
- ``[PAGE: total= offset= limit= count= next=]`` over the documents, with ``[NEXT_CMD: ...]`` when more follow
  (``--limit``, default 20, ``0`` for all; ``--offset``); JSON pages ``pairs`` by the same documents;
- ``[SUMMARY: pairs= new= missing= folded= declared= skipped= applied=]`` last, over every pair.

``SKIPPED`` (an input left out of the derivation) differs from ``scope``'s ``UNRESOLVED`` (an input counted as an
unknown overlap) even where both name the reason ``not-a-path``.

Nothing is written without ``--apply``. Files that could not be indexed are ``SPEC_DOCUMENT_INVALID`` warnings; a
document ``--apply`` could not write is a ``SPEC_ENTRYPOINTS_APPLY_FAILED`` error after the result. A ``--code`` that
matches no candidate refuses the run with ``SPEC_ENTRYPOINTS_CODE_UNMATCHED`` before anything is written.
"""

from __future__ import annotations

from collections.abc import Sequence

import click
from devkit_core.base.errors import ArgumentError
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

from devkit_spec.features.entrypoints import Applied
from devkit_spec.features.entrypoints.models.derive import Pair, Skipped, State
from devkit_spec.features.entrypoints.usecases.derive import DEFAULT_STATUS, DeriveEntrypointsUseCase, _check_options
from devkit_spec.utils.output import echo_page, fields_line, page, sentinel

DEFAULT_LIMIT = 20


@click.group(name="entrypoints")
def entrypoints_group() -> None:
    """Code entrypoints of capabilities and use cases, derived from spec bundles."""


@entrypoints_group.command(name="derive")
@click.option("--spec", "spec_dir", default=None, help="One spec bundle directory (specs/<YYYY-MM>/<YYYYMMDD>-<slug>)")
@click.option("--all", "every", is_flag=True, help="Aggregate every spec bundle under specs/")
@click.option("--status", default=None, help=f"With --all: comma-separated spec statuses [default: {DEFAULT_STATUS}]")
@click.option(
    "--min-count", type=int, default=None, help="With --all: keep pairs seen in at least N specs [default: 1]"
)
@click.option("--apply", "write", is_flag=True, help="Write new, existing candidate paths into the documents")
@click.option("--target", "targets", multiple=True, help="With --apply: write only this document ID or path (repeat)")
@click.option(
    "--code",
    "codes",
    multiple=True,
    help="Keep only candidates at or under this path, or this path inside one (repeat)",
)
@click.option("--exclude", "excludes", multiple=True, help="Drop candidates equal to or under this path (repeat)")
@click.option("--skipped", "list_skipped", is_flag=True, help="List every skipped input instead of per-reason counts")
@click.option("--limit", "-n", type=int, default=DEFAULT_LIMIT, show_default=True, help="Documents per page; 0 for all")
@click.option("--offset", type=int, default=0, show_default=True, help="Documents to skip")
@workspace_option()
@FORMAT_OPTION
@boundary
def derive_cmd(
    spec_dir: str | None,
    every: bool,
    status: str | None,
    min_count: int | None,
    write: bool,
    targets: tuple[str, ...],
    codes: tuple[str, ...],
    excludes: tuple[str, ...],
    list_skipped: bool,
    limit: int,
    offset: int,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Join tasks.md _Boundary paths with reconcile.md capability/use case targets into document-code pairs.

    Exactly one of --spec and --all. Pairs are declarations joined mechanically, not proof that the code
    implements the document: review them, then --apply with --target and --code for the chosen ones. --apply
    appends to the documents' entrypoints frontmatter, keeps every other byte and is idempotent.
    """
    _check_options(spec_dir, every, status, min_count, write, targets)
    if limit < 0 or offset < 0:
        raise ArgumentError(
            "--limit and --offset must not be negative", target_files=["--limit", "--offset"], fix="Pass 0 or more"
        )
    root = resolve_root(workspace_root)
    pairs, skipped, applied, summary, errors, notices = DeriveEntrypointsUseCase().execute(
        root, spec_dir, status, min_count, write, targets, codes, excludes
    )
    documents = list(dict.fromkeys(pair.doc for pair in pairs))
    shown = set(page(documents, offset, limit))
    paged = [pair for pair in pairs if pair.doc in shown]
    if is_json(output_format):
        echo_json(
            {
                "pairs": [pair.to_dict() for pair in paged],
                "skipped": [item.to_dict() for item in skipped] if list_skipped else _skipped_counts(skipped),
                "applied": [item.to_dict() for item in applied],
                "page": {"total": len(documents), "offset": offset, "limit": limit, "count": len(shown)},
                "summary": summary,
                "errors": [error.to_dict() for error in errors],
                "notices": [notice.to_dict() for notice in notices],
            }
        )
    else:
        _echo_text(paged, skipped, applied, list_skipped)
        args = ["entrypoints", "derive", *(["--spec", spec_dir] if spec_dir else ["--all"])]
        for flag, given in (("--status", status), ("--min-count", min_count)):
            if given is not None:
                args += [flag, str(given)]
        args += [item for code in codes for item in ("--code", code)]
        args += [item for exclude in excludes for item in ("--exclude", exclude)]
        args += ["--skipped"] if list_skipped else []
        args += [*(["-w", workspace_root] if workspace_root is not None else []), "--limit", str(limit)]
        echo_page(len(documents), offset, limit, len(shown), args)
        click.echo(fields_line("SUMMARY", **summary))
    echo_notices(notices)
    exit_on_problems(errors)
    exit_on_warnings(notices)


CANDIDATE_GROUPS = ("new", "missing", "folded", "declared")


def _candidates(pairs: Sequence[Pair]) -> list[tuple[str, str, dict[str, list[str]]]]:
    """The pairs grouped per document (in pair order): each candidate path under its group of ``CANDIDATE_GROUPS``."""
    grouped: dict[tuple[str, str], dict[str, list[str]]] = {}
    for pair in pairs:
        groups = grouped.setdefault((pair.doc, pair.doc_path), {name: [] for name in CANDIDATE_GROUPS})
        if pair.state is State.DECLARED:
            group = "declared"
        elif pair.folded_into is not None:
            group = "folded"
        else:
            group = "new" if pair.exists else "missing"
        groups[group].append(pair.code if pair.count is None else f"{pair.code}({pair.count})")
    return [(doc, doc_path, groups) for (doc, doc_path), groups in grouped.items()]


def _skipped_counts(skipped: Sequence[Skipped]) -> list[dict[str, object]]:
    """One ``{kind, reason, count}`` per kind and reason, in first-seen order."""
    counts: dict[tuple[str, str], int] = {}
    for item in skipped:
        key = (str(item.kind), str(item.reason))
        counts[key] = counts.get(key, 0) + 1
    return [{"kind": kind, "reason": reason, "count": count} for (kind, reason), count in counts.items()]


def _echo_text(
    pairs: Sequence[Pair], skipped: Sequence[Skipped], applied: Sequence[Applied], list_skipped: bool
) -> None:
    for doc, doc_path, groups in _candidates(pairs):
        click.echo(
            sentinel("CANDIDATES", doc, path=doc_path, **{name: ",".join(paths) for name, paths in groups.items()})
        )
    if list_skipped:
        for item in skipped:
            extra: dict[str, object] = {"kind": str(item.kind)}
            if item.spec:
                extra["spec"] = item.spec
            if item.task:
                extra["task"] = item.task
            click.echo(sentinel("SKIPPED", item.value, **extra, reason=str(item.reason)))
    else:
        for count in _skipped_counts(skipped):
            click.echo(sentinel("SKIPPED_COUNT", count["reason"], kind=count["kind"], count=count["count"]))
    for item in applied:
        click.echo(sentinel("APPLIED", item.doc, path=item.doc_path, added=",".join(item.added)))
