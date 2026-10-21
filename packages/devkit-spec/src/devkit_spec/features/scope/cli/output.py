"""Shared CLI rendering for scope registration results."""

import click

from devkit_spec.features.scope.models.location import Location
from devkit_spec.features.scope.models.model import Record
from devkit_spec.utils.output import sentinel


def echo_registered(location: Location, record: Record, token: str) -> None:
    """The ``[SCOPE]`` line of a registration: the only place its token is printed (``proposal handoff`` too)."""
    click.echo(
        sentinel(
            "SCOPE",
            record.task_id,
            namespace=location.namespace,
            revision=record.revision,
            scopes=len(record.scopes),
            unresolved=len(record.unresolved),
            shared_path=str(location.shared_path),
            token=token,
        )
    )


def registered_dict(location: Location, record: Record, token: str) -> dict[str, object]:
    return {
        "record": record.public_dict(),
        "token": token,
        "namespace": location.namespace,
        "shared_path": str(location.shared_path),
    }
