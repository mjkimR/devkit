"""Shared CLI rendering for scope registration results."""

import click

from devkit_spec.adapters.cli import sentinel
from devkit_spec.features.scope.models.location import Location
from devkit_spec.features.scope.models.model import Record


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
            shared_path=location.shown(location.shared_path),
            token=token,
        )
    )


def registered_dict(location: Location, record: Record, token: str) -> dict[str, object]:
    """The registration as JSON: what the ``[SCOPE]`` line carries, with the unresolved inputs listed; no timestamps
    or record internals (``query`` shows the record)."""
    return {
        "task": record.task_id,
        "namespace": location.namespace,
        "revision": record.revision,
        "spec": record.spec,
        "scopes": len(record.scopes),
        "unresolved": [item.to_dict() for item in record.unresolved],
        "shared_path": location.shown(location.shared_path),
        "token": token,
    }
