"""Reconcile and inspect the owning workspace's retained runtime registration."""

from pathlib import Path

from devkit_dist.features.distribution.services.installation.config import read_config
from devkit_dist.features.distribution.services.installation.transaction import project_lock
from devkit_dist.features.host.usecases import registrations


def setup(root: Path, hosts: tuple[str, ...], *, executable: str | None = None):
    with registrations.clone_lock(root), project_lock(root):
        registrations.recover(root)
        planned = registrations.plan(root, hosts or read_config(root).agents, executable=executable)
        registrations.apply(planned)
    return planned


def remove(root: Path):
    with registrations.clone_lock(root), project_lock(root):
        registrations.recover(root)
        planned = registrations.plan(root, (), remove=True)
        registrations.apply(planned)
    return planned


def status(root: Path):
    return registrations.inspect(root, read_config(root).agents)
