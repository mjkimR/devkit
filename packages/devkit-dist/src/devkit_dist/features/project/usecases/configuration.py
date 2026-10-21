"""Read effective checkout settings for command and MCP invocations."""

from pathlib import Path

from devkit_dist.features.project.repositories import local_config
from devkit_dist.features.project.services import presentation


def read_effective_config(root: Path, *, local: bool = True):
    return local_config.read_effective_config(root, local=local)


def resolve_execution_environment(root: Path):
    return local_config.resolve_execution_environment(root)


def approval_language(executor: Path) -> str:
    return presentation.approval_language(executor)
