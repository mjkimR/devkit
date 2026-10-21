"""CLI transport for the shared domain. Put reads UTF-8 Markdown from stdin."""

from __future__ import annotations

import json
import sys

import click

from devkit.core.cli import boundary, echo_json, resolve_root
from devkit.shared.api import MAX_BYTES, PutRequest
from devkit.shared.errors import InputError
from devkit.shared.service import adapter


@click.group()
def cli() -> None:
    """Immutable seven-day report artifacts."""


def common(fn):
    fn = click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text")(fn)
    return click.option("--workspace-root", type=click.Path())(fn)


def filters(fn):
    for name in ("language", "source-sha", "slug", "kind"):
        fn = click.option("--" + name, required=True)(fn)
    return fn


def emit(result: dict, selected, output_format: str) -> None:
    result.update(adapter=selected.adapter_id, repository_namespace=selected.repository_namespace)
    if output_format == "json":
        echo_json(result)
    else:
        click.echo("[SHARED_RESULT: " + json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "]")


@cli.command()
@filters
@common
@boundary
def put(kind: str, slug: str, source_sha: str, language: str, workspace_root: str | None, output_format: str) -> None:
    raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    try:
        content = raw.decode("utf-8")
    except UnicodeError as exc:
        raise InputError("content is not UTF-8") from exc
    request = PutRequest(kind, slug, source_sha, language, content)
    request.validate()
    selected = adapter(resolve_root(workspace_root))
    emit(selected.put(request).to_dict(), selected, output_format)


@cli.command()
@click.argument("artifact_uri")
@common
@boundary
def get(artifact_uri: str, workspace_root: str | None, output_format: str) -> None:
    selected = adapter(resolve_root(workspace_root))
    emit(selected.get(artifact_uri).to_dict(), selected, output_format)


@cli.command(name="list")
@click.option("--kind", required=True)
@click.option("--slug", required=True)
@click.option("--source-sha")
@click.option("--language")
@click.option("--cursor")
@click.option("--limit", default=100, type=int)
@common
@boundary
def list_artifacts(
    kind: str,
    slug: str,
    source_sha: str | None,
    language: str | None,
    cursor: str | None,
    limit: int,
    workspace_root: str | None,
    output_format: str,
) -> None:
    selected = adapter(resolve_root(workspace_root))
    emit(
        selected.list(kind, slug, source_sha=source_sha, language=language, cursor=cursor, limit=limit).to_dict(),
        selected,
        output_format,
    )


@cli.command()
@click.option("--apply", "apply_changes", is_flag=True)
@click.option("--cursor")
@common
@boundary
def sweep(apply_changes: bool, cursor: str | None, workspace_root: str | None, output_format: str) -> None:
    selected = adapter(resolve_root(workspace_root))
    emit(selected.sweep(apply=apply_changes, cursor=cursor).to_dict(), selected, output_format)
