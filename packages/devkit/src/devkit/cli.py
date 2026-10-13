"""The ``devkit`` command line: distribution commands at the top level, one group per engine.

``devkit sync``, ``add``, ``remove``, ``list``, ``status`` and the other
distribution commands sit at the top level, as does ``devkit run`` (compact
command output); ``devkit rules``, ``devkit workflow``, ``devkit gate`` and
``devkit worktree`` are the rule engine, workflow engine, commit gate and task
worktree groups. ``devkit --version`` prints one ``[VERSION: devkit <version>]``
line.

Commands load lazily: the root group knows each command only as a
``module:attribute`` reference and imports the module when the command is
invoked, so one command never pays for the import of the others. ``--help``
on the root group lists every command and therefore imports all of them.

Installed packages mount further commands through the ``devkit.commands``
entry-point group: the entry point name is the command name and its value the
``module:attribute`` of a click command (``spec = "devkit_spec.cli:cli"`` makes
``devkit spec``). Built-in names are reserved and always win. Entry points are
read only for a name that is not built in, or for the root ``--help``, so the
built-in commands never pay for the scan. A plugin that cannot be used (its
module fails to import, its target is not a click command, or two packages
declare its name) fails only its own command, with ``COMMAND_PLUGIN_INVALID``.
See ``docs/architecture/command-plugins.md``.
"""

from __future__ import annotations

import functools
import importlib
import itertools
import sys
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from importlib.metadata import EntryPoint

    from devkit.advisory import AdvisoryError

PLUGIN_GROUP = "devkit.commands"

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
    "config": f"{_DISTRIBUTION}:config",
    "recover": f"{_DISTRIBUTION}:recover",
    "override": f"{_DISTRIBUTION}:override",
    "run": "devkit.compact.cli:run_cmd",
    "rules": "devkit.rules.cli:cli",
    "workflow": "devkit.workflow.cli:cli",
    "gate": "devkit.gate.cli:cli",
    "worktree": "devkit.worktree.cli:cli",
}


@functools.cache
def plugin_entry_points() -> dict[str, tuple[EntryPoint, ...]]:
    """The ``devkit.commands`` entry points of the installed packages by command name, built-in names left out.

    The same target declared twice (one package visible through two paths) counts once.
    """
    from importlib.metadata import entry_points

    found: dict[str, list[EntryPoint]] = {}
    for entry in entry_points(group=PLUGIN_GROUP):
        if entry.name in COMMANDS:
            continue
        declared = found.setdefault(entry.name, [])
        if all(other.value != entry.value for other in declared):
            declared.append(entry)
    return {name: tuple(entries) for name, entries in found.items()}


def _origin(entry: EntryPoint) -> str:
    dist = getattr(entry, "dist", None)
    return f"{entry.value} (package {dist.name})" if dist is not None else entry.value


def _json_requested(args: tuple[str, ...]) -> bool:
    lowered = [arg.lower() for arg in args]
    return "--format=json" in lowered or any(
        arg == "--format" and value == "json" for arg, value in itertools.pairwise(lowered)
    )


def _unusable(name: str, error: AdvisoryError) -> click.Command:
    """A stand-in for a plugin command that cannot be used: whatever its arguments, it reports ``error`` and exits."""

    def report(args: tuple[str, ...]) -> None:
        if _json_requested(args):
            from devkit.core.cli import echo_json

            echo_json({"error": error.to_dict()})
        else:
            click.echo(error.render(), err=True)
        sys.exit(int(error.exit_code))

    return click.Command(
        name,
        callback=report,
        params=[click.Argument(["args"], nargs=-1, type=click.UNPROCESSED)],
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True, "help_option_names": []},
        short_help=f"Unusable plugin command ({error.code})",
    )


def _load_plugin(name: str) -> click.Command | None:
    entries = plugin_entry_points().get(name)
    if not entries:
        return None
    from devkit.core.errors import CommandPluginError

    entry, *others = entries
    if others:
        origins = sorted(_origin(declared) for declared in entries)
        return _unusable(name, CommandPluginError(f"command {name}: declared by more than one package", *origins))
    try:
        command = entry.load()
    except Exception as exc:
        message = f"command {name}: {_origin(entry)} cannot be loaded: {type(exc).__name__}: {exc}"
        return _unusable(name, CommandPluginError(message))
    if not isinstance(command, click.Command):
        return _unusable(name, CommandPluginError(f"command {name}: {_origin(entry)} is not a click command"))
    return command


class _LazyGroup(click.Group):
    """A group that imports a command's module only when the command is looked up."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted({*super().list_commands(ctx), *COMMANDS, *plugin_entry_points()})

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        command = super().get_command(ctx, cmd_name)
        if command is not None:
            return command
        if cmd_name not in COMMANDS:
            return _load_plugin(cmd_name)
        module, _, attribute = COMMANDS[cmd_name].partition(":")
        command = getattr(importlib.import_module(module), attribute)
        if not isinstance(command, click.Command):
            raise TypeError(f"{COMMANDS[cmd_name]} is not a click command")
        return command


def _print_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    from importlib.metadata import version

    click.echo(f"[VERSION: devkit {version('devkit-agt')}]")
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
