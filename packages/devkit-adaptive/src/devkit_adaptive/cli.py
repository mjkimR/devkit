"""Mount adaptive commands through devkit.commands."""

import click

from devkit_adaptive.features.assignment.cli.commands import assignment


@click.group(name="adaptive")
def cli() -> None:
    """Adaptive delegation commands."""


cli.add_command(assignment)
