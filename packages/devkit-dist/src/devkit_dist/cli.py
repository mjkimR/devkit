"""The ``devkit`` command line: the distribution commands of ``devkit-dist``, then the commands installed packages mount.

``devkit sync``, ``add``, ``remove``, ``list``, ``status`` and the other
distribution commands sit at the top level, with ``devkit host`` (native host
hooks and the MCP server). ``devkit --version`` prints one
``[VERSION: devkit <version>]`` line with the ``devkit-dist`` version.

Commands load lazily: the root group knows each command only as a
``module:attribute`` reference and imports the module when the command is
invoked, so one command never pays for the import of the others. ``--help``
on the root group lists every command and therefore imports all of them.

Installed packages mount further commands through the ``devkit.commands``
entry-point group: the entry point name is the command name and its value the
``module:attribute`` of a click command (``spec = "devkit_spec.cli:cli"`` makes
``devkit spec``). ``devkit-agt`` mounts the harness this way: ``rules``,
``workflow``, ``gate``, ``worktree``, ``generated``, ``integration`` and
``run``. Built-in names are reserved and always win. Entry points are read only
for a name that is not built in, or for the root ``--help``, so the built-in
commands never pay for the scan. A plugin that cannot be used (its module fails
to import, its target is not a click command, or two packages declare its
name) fails only its own command, with ``COMMAND_PLUGIN_INVALID``.

When no installed command has the name, a harness command name
(``HARNESS_COMMANDS``, names only: this module never names a harness module)
answers with ``HARNESS_COMMAND_UNAVAILABLE`` and the directive to add
``devkit-agt``; any other unknown name keeps click's usage error. See
``docs/architecture/ARCH-05-3-command-plugins.md``.
"""

from __future__ import annotations

import functools
import itertools
import sys
from typing import TYPE_CHECKING

import click
from devkit_cli import LazyGroup

if TYPE_CHECKING:
    from importlib.metadata import EntryPoint

    from devkit.advisory import AdvisoryError

PLUGIN_GROUP = "devkit.commands"

_DISTRIBUTION = "devkit_dist.features.distribution.cli"

# Top-level command name -> "module:attribute" of its click command; only modules devkit-dist ships.
COMMANDS: dict[str, str] = {
    "get-context": f"{_DISTRIBUTION}.context:context",
    "playbook": f"{_DISTRIBUTION}.playbooks:playbook",
    "bundle": f"{_DISTRIBUTION}.bundles:bundle",
    "sync": f"{_DISTRIBUTION}.selection:sync",
    "add": f"{_DISTRIBUTION}.selection:add",
    "remove": f"{_DISTRIBUTION}.selection:remove",
    "list": f"{_DISTRIBUTION}.selection:list_resources",
    "status": f"{_DISTRIBUTION}.selection:status",
    "config": f"{_DISTRIBUTION}.configuration:config",
    "recover": f"{_DISTRIBUTION}.selection:recover",
    "override": f"{_DISTRIBUTION}.overrides:override",
    "host": "devkit_dist.features.host.cli:cli",
    "shared": "devkit_dist.features.shared.cli:cli",
}

# The command names devkit-agt mounts through devkit.commands. Names only, consulted last: an installed command of
# the name always wins, and the list is never shown by ``--help``.
HARNESS_COMMANDS: tuple[str, ...] = ("rules", "workflow", "gate", "worktree", "generated", "integration", "run")
# The command names an optional extra mounts, by command name: the extra that provides it. Consulted the same way.
EXTRA_COMMANDS: dict[str, str] = {"mcp": "mcp"}


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
            from devkit_cli import echo_json

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
    from devkit_dist.base.errors import CommandPluginError

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


def _extra_unavailable(name: str) -> click.Command | None:
    """The stand-in for an extra's command name no installed package provides; ``None`` for any other name."""
    if name not in EXTRA_COMMANDS:
        return None
    from devkit_dist.base.errors import MCP_INSTALL_FIX, ExtraCommandUnavailableError, extra_install_fix

    extra = EXTRA_COMMANDS[name]
    error = ExtraCommandUnavailableError(
        f"command {name}: not installed; devkit {name} comes with the {extra} extra",
        fix=MCP_INSTALL_FIX if extra == "mcp" else extra_install_fix(extra),
    )
    return _unusable(name, error)


def _harness_unavailable(name: str) -> click.Command | None:
    """The stand-in for a harness command name no installed package provides; ``None`` for any other name."""
    if name not in HARNESS_COMMANDS:
        return None
    from devkit_dist.base.errors import HarnessCommandUnavailableError

    error = HarnessCommandUnavailableError(
        f"command {name}: not installed; devkit {name} is a command of devkit-agt, the devkit harness"
    )
    return _unusable(name, error)


class _LazyGroup(LazyGroup):
    """The root group: the built-in ``COMMANDS`` load lazily, then installed plugins and harness stand-ins by name."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted({*super().list_commands(ctx), *plugin_entry_points()})

    def resolve_lazy(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        if cmd_name in COMMANDS:
            return super().resolve_lazy(ctx, cmd_name)
        return _load_plugin(cmd_name) or _harness_unavailable(cmd_name) or _extra_unavailable(cmd_name)


def _print_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    from importlib.metadata import version

    click.echo(f"[VERSION: devkit {version('devkit-dist')}]")
    ctx.exit()


@click.group(name="devkit", cls=_LazyGroup, lazy_commands=COMMANDS)
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=_print_version,
    help="Print a [VERSION: devkit <version>] line and exit",
)
def cli() -> None:
    """Devkit: agent asset distribution; installed packages add their commands (devkit-agt: rules, workflows, gates)."""
