"""``devkit viewer``: the command group devkit-viewer mounts under the ``devkit`` command line.

devkit's root group finds it through the ``devkit.commands`` entry point ``viewer``. ``serve`` registers the
repositories, binds ``127.0.0.1:<port>``, prints one ``[VIEWER: url=<url> repos=<n>]`` line and serves in the
foreground until ``SIGINT`` or ``SIGTERM``, then exits ``0``. Refusals before serving are ``VIEWER_`` advisories on
stderr with exit ``2``; request logs appear only under ``-v``. ``--version`` prints one
``[VERSION: devkit-viewer <version>]`` line.
"""

from __future__ import annotations

import signal
import sys
from pathlib import Path
from types import FrameType

import click
from devkit_dist.adapters.cli import boundary

from devkit_viewer.features.browse.http.server import ViewerServer
from devkit_viewer.features.browse.usecases.register import RegisterRepositoriesUseCase

DISTRIBUTION = "devkit-viewer"
DEFAULT_PORT = 8765


def _print_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    from importlib.metadata import version

    click.echo(f"[VERSION: {DISTRIBUTION} {version(DISTRIBUTION)}]")
    ctx.exit()


@click.group(name="viewer")
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_print_version,
    help=f"Print a [VERSION: {DISTRIBUTION} <version>] line and exit",
)
def cli() -> None:
    """A local, read-only page for the Living Spec, proposals, specs and roadmap of devkit repositories."""


def _stop(_signum: int, _frame: FrameType | None) -> None:
    raise KeyboardInterrupt


@cli.command(name="serve")
@click.option("--repo", "repos", multiple=True, help="Top level of a Git work tree to serve (repeatable)")
@click.option("--scan", "scans", multiple=True, help="Serve each direct child that is a devkit repository (repeatable)")
@click.option(
    "--port",
    type=click.IntRange(0, 65535),
    default=DEFAULT_PORT,
    show_default=True,
    help="Port on 127.0.0.1; 0 picks a free one",
)
@boundary
def serve_cmd(repos: tuple[str, ...], scans: tuple[str, ...], port: int) -> None:
    """Serve repositories on 127.0.0.1 until interrupted; with no --repo or --scan, the current devkit project."""
    repositories = RegisterRepositoriesUseCase().execute(repos, scans, Path.cwd())
    server = ViewerServer(repositories, port)
    signal.signal(signal.SIGTERM, _stop)
    click.echo(f"[VIEWER: url={server.url} repos={len(repositories)}]")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
