"""The ``devkit`` command line: distribution commands at the top level, one group per engine.

``devkit sync``, ``add``, ``remove``, ``list``, ``status`` and the other
distribution commands sit at the top level, as does ``devkit run`` (compact
command output); ``devkit rules``, ``devkit workflow`` and ``devkit gate`` are
the rule engine, workflow engine and commit gate groups. ``devkit --version``
prints one ``[VERSION: devkit <version>]`` line.

Commands load lazily: the root group knows each command only as a
``module:attribute`` reference and imports the module when the command is
invoked, so one command never pays for the import of the others. ``--help``
on the root group lists every command and therefore imports all of them.
"""

from __future__ import annotations

import importlib

import click

_DISTRIBUTION = "devkit.distribution.cli"

# Top-level command name -> "module:attribute" of its click command.
COMMANDS: dict[str, str] = {
    "get-context": f"{_DISTRIBUTION}:context",
    "playbook": f"{_DISTRIBUTION}:playbook",
    "bundle": f"{_DISTRIBUTION}:bundle",
    "sync": f"{_DISTRIBUTION}:sync",
    "add": f"{_DISTRIBUTION}:add",
    "remove": f"{_DISTRIBUTION}:remove",
    "list": f"{_DISTRIBUTION}:list_resources",
    "status": f"{_DISTRIBUTION}:status",
    "recover": f"{_DISTRIBUTION}:recover",
    "override": f"{_DISTRIBUTION}:override",
    "run": "devkit.compact.cli:run_cmd",
    "rules": "devkit.rules.cli:cli",
    "workflow": "devkit.workflow.cli:cli",
    "gate": "devkit.gate.cli:cli",
}


class _LazyGroup(click.Group):
    """A group that imports a command's module only when the command is looked up."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted({*super().list_commands(ctx), *COMMANDS})

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        command = super().get_command(ctx, cmd_name)
        if command is not None or cmd_name not in COMMANDS:
            return command
        module, _, attribute = COMMANDS[cmd_name].partition(":")
        command = getattr(importlib.import_module(module), attribute)
        if not isinstance(command, click.Command):
            raise TypeError(f"{COMMANDS[cmd_name]} is not a click command")
        return command


def _print_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    from importlib.metadata import version

    click.echo(f"[VERSION: devkit {version('devkit')}]")
    ctx.exit()


@click.group(name="devkit", cls=_LazyGroup)
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_print_version,
    help="Print a [VERSION: devkit <version>] line and exit",
)
def cli() -> None:
    """Devkit: agent asset distribution, repository rules, delivery workflows, commit gates and compact command output."""
