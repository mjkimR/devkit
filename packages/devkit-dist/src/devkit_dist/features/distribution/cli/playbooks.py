"""Distribution playbooks CLI adapters."""

from __future__ import annotations

import click

from devkit_dist.adapters.cli import (
    resolve_root,
)
from devkit_dist.features.distribution.models.settings import (
    DEFAULT_PLAYBOOK_LIMIT,
    DEFAULT_PLAYBOOK_MAX_BYTES,
    DEFAULT_PLAYBOOK_MIN_SCORE,
    DEFAULT_PLAYBOOK_MIN_SIMILARITY,
    DEFAULT_PLAYBOOK_MODE,
    PLAYBOOK_LIMIT_MAX,
    PLAYBOOK_LIMIT_MIN,
    PLAYBOOK_MAX_BYTES_MAX,
    PLAYBOOK_MAX_BYTES_MIN,
)
from devkit_dist.features.distribution.usecases.playbook_get import GetPlaybook, validate_playbook_id
from devkit_dist.features.distribution.usecases.playbook_search import SearchPlaybooks
from devkit_dist.features.search import SearchMode

from .output import WORKSPACE, _json_command


@click.group()
def playbook() -> None:
    """Discover occasional procedures after explicit devkit-playbook invocation."""


@playbook.command(name="get")
@click.argument("playbook_id")
@WORKSPACE
@_json_command
def playbook_get(playbook_id: str, workspace_root: str | None) -> object:
    """Return a complete synchronized playbook by exact bundle/asset ID without executing it."""
    validate_playbook_id(playbook_id)
    return GetPlaybook().execute(resolve_root(workspace_root), playbook_id)


@playbook.command(name="search")
@click.argument("query")
@WORKSPACE
@click.option(
    "--limit",
    default=None,
    type=int,
    help=f"Maximum candidates to return, {PLAYBOOK_LIMIT_MIN}..{PLAYBOOK_LIMIT_MAX}"
    f" (default: [playbooks] limit, else {DEFAULT_PLAYBOOK_LIMIT}).",
)
@click.option(
    "--min-score",
    default=None,
    type=float,
    help=f"Minimum nonnegative lexical (BM25) score (default: [playbooks] min_score, else {DEFAULT_PLAYBOOK_MIN_SCORE}).",
)
@click.option(
    "--min-similarity",
    default=None,
    type=float,
    help="Minimum cosine similarity, 0..1, for the dense ranking"
    f" (default: [playbooks] min_similarity, else {DEFAULT_PLAYBOOK_MIN_SIMILARITY}).",
)
@click.option(
    "--mode",
    default=None,
    type=click.Choice([mode.value for mode in SearchMode], case_sensitive=False),
    help="Ranking: auto (hybrid with the search extra, devkit-dist[search] or devkit-agt[search], else lexical), lexical, dense or hybrid"
    f" (default: [playbooks] mode, else {DEFAULT_PLAYBOOK_MODE}).",
)
@click.option(
    "--max-bytes",
    default=None,
    type=int,
    help=f"JSON response byte budget, {PLAYBOOK_MAX_BYTES_MIN}..{PLAYBOOK_MAX_BYTES_MAX}"
    f" (default: [playbooks] max_bytes, else {DEFAULT_PLAYBOOK_MAX_BYTES}).",
)
@_json_command
def search(
    query: str,
    workspace_root: str | None,
    limit: int | None,
    min_score: float | None,
    min_similarity: float | None,
    mode: str | None,
    max_bytes: int | None,
) -> object:
    """Search synchronized playbook metadata with an English query; return headers only."""
    return SearchPlaybooks().execute(
        resolve_root(workspace_root),
        query,
        limit=limit,
        min_score=min_score,
        min_similarity=min_similarity,
        max_bytes=max_bytes,
        mode=mode,
    )
