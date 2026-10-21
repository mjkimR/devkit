"""Host integration: declarative lifecycle hooks, native adapters and package service handlers.

Deployment belongs to devkit_dist.features.distribution; host protocols and execution belong here. Services such as integration
consume these contracts without putting methodology, Git mutations or approval policy into the host adapter.
"""

from devkit_dist.features.host.models.errors import (
    HookConflictError,
    HookDefinitionError,
    HookDispatchError,
    HookMissingError,
    HostConfigError,
    HostConfirmationError,
    HostError,
    HostMcpError,
    HostMcpInputError,
)
from devkit_dist.features.host.models.hooks import HookDefinition, HookEvent, HookResponse
from devkit_dist.features.host.repositories.adapters.codex import CodexAdapter
from devkit_dist.features.host.services.configuration import adapter_for, plan_config, read_hook
from devkit_dist.features.host.usecases.runner import dispatch
from devkit_dist.features.host.usecases.status import HostStatus, inspect_host

__all__ = [
    "CodexAdapter",
    "HookConflictError",
    "HookDefinition",
    "HookDefinitionError",
    "HookDispatchError",
    "HookEvent",
    "HookMissingError",
    "HookResponse",
    "HostConfigError",
    "HostConfirmationError",
    "HostError",
    "HostMcpError",
    "HostMcpInputError",
    "HostStatus",
    "adapter_for",
    "dispatch",
    "inspect_host",
    "plan_config",
    "read_hook",
]
