"""A click group that imports a command's module only when the command is looked up.

A tool's root group names each subcommand as ``"module:attribute"``, so running one command never pays for the
imports of the others::

    @click.group(cls=LazyGroup, lazy_commands={"scan": "mytool.features.scan.cli:scan"})
    def cli() -> None: ...

Listing the commands (``--help`` on the group) imports every one of them for its help text.
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping, MutableMapping, Sequence
from typing import Any

import click


class LazyGroup(click.Group):
    """A ``click.Group`` whose ``lazy_commands`` (``name -> "module:attribute"``) load on first lookup.

    Commands added eagerly (``add_command``, ``@group.command``) win over a lazy one of the same name. A subclass
    extends ``resolve_lazy`` to find further commands (plugins) by name.
    """

    def __init__(
        self,
        name: str | None = None,
        commands: MutableMapping[str, click.Command] | Sequence[click.Command] | None = None,
        *,
        lazy_commands: Mapping[str, str] | None = None,
        **attrs: Any,
    ) -> None:
        super().__init__(name, commands, **attrs)
        self.lazy_commands: Mapping[str, str] = lazy_commands if lazy_commands is not None else {}

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted({*super().list_commands(ctx), *self.lazy_commands})

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        command = super().get_command(ctx, cmd_name)
        if command is not None:
            return command
        return self.resolve_lazy(ctx, cmd_name)

    def resolve_lazy(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """The lazy command ``cmd_name``, imported now; ``None`` when there is none.

        A target that is not a click command raises ``TypeError`` naming it: a wiring defect, not a user error.
        """
        target = self.lazy_commands.get(cmd_name)
        if target is None:
            return None
        module, _, attribute = target.partition(":")
        command = getattr(importlib.import_module(module), attribute)
        if not isinstance(command, click.Command):
            raise TypeError(f"{target} is not a click command")
        return command
