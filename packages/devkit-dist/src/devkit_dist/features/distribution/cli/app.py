"""Compose the distribution command set for the root CLI."""

import click

from .bundles import bundle
from .configuration import config
from .context import context
from .overrides import override
from .playbooks import playbook
from .selection import add, list_resources, recover, remove, status, sync

COMMANDS: tuple[click.Command, ...] = (
    context,
    playbook,
    bundle,
    sync,
    add,
    remove,
    list_resources,
    status,
    config,
    recover,
    override,
)
