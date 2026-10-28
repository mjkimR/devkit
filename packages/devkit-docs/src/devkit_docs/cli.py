"""``devkit docs``: the command group devkit-docs mounts under the ``devkit`` command line.

devkit's root group finds it through the ``devkit.commands`` entry point
``docs`` and imports this module only when ``devkit docs`` runs. Commands
follow devkit's output contract: each one is built on ``devkit_dist.adapters.cli``
(``boundary``, ``FORMAT_OPTION``, ``workspace_option``) and raises
``AdvisoryError`` subclasses with ``DOCS_`` codes. ``--version`` prints one
``[VERSION: devkit-docs <version>]`` line; ``devkit --version`` reports devkit
itself.
"""

from __future__ import annotations

import click

from devkit_docs.features.documents.cli.commands import list_cmd, refs_cmd, resolve_cmd
from devkit_docs.features.documents.cli.search import search_cmd

DISTRIBUTION = "devkit-docs"


def _print_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    from importlib.metadata import version

    click.echo(f"[VERSION: {DISTRIBUTION} {version(DISTRIBUTION)}]")
    ctx.exit()


@click.group(name="docs")
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_print_version,
    help=f"Print a [VERSION: {DISTRIBUTION} <version>] line and exit",
)
def cli() -> None:
    """Living Spec documents: resolve IDs, follow references, list and search documents."""


cli.add_command(resolve_cmd)
cli.add_command(refs_cmd)
cli.add_command(list_cmd)
cli.add_command(search_cmd)
