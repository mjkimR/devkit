"""CLI transport for the shared domain. Put reads UTF-8 Markdown from stdin."""

from __future__ import annotations

import json
import sys

import click

from devkit_dist.adapters.cli import boundary, echo_json, resolve_root
from devkit_dist.features.shared.models.api import MAX_BYTES, PutRequest
from devkit_dist.features.shared.models.errors import InputError
from devkit_dist.features.shared.usecases.commands import GetArtifact, ListArtifacts, PutArtifact, SweepArtifacts


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


def emit(result: dict, output_format: str) -> None:
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
    emit(PutArtifact().execute(resolve_root(workspace_root), request), output_format)


@cli.command()
@click.argument("artifact_uri")
@common
@boundary
def get(artifact_uri: str, workspace_root: str | None, output_format: str) -> None:
    emit(GetArtifact().execute(resolve_root(workspace_root), artifact_uri), output_format)


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
    emit(
        ListArtifacts().execute(
            resolve_root(workspace_root),
            kind,
            slug,
            source_sha=source_sha,
            language=language,
            cursor=cursor,
            limit=limit,
        ),
        output_format,
    )


@cli.command()
@click.option("--apply", "apply_changes", is_flag=True)
@click.option("--cursor")
@common
@boundary
def sweep(apply_changes: bool, cursor: str | None, workspace_root: str | None, output_format: str) -> None:
    emit(SweepArtifacts().execute(resolve_root(workspace_root), apply=apply_changes, cursor=cursor), output_format)
