"""Host integration: declarative lifecycle hooks, native adapters and package service handlers.

Deployment belongs to devkit.distribution; host protocols and execution belong here. Services such as integration
consume these contracts without putting methodology, Git mutations or approval policy into the host adapter.
"""

from devkit.host.adapters.codex import CodexAdapter
from devkit.host.configuration import adapter_for, plan_config, read_hook
from devkit.host.errors import (
    HookConflictError,
    HookDefinitionError,
    HookDispatchError,
    HookMissingError,
    HostConfigError,
    HostConfirmationError,
    HostError,
    HostMcpDependencyError,
    HostMcpError,
    HostMcpInputError,
)
from devkit.host.hooks import HookDefinition, HookEvent, HookResponse
from devkit.host.runner import dispatch
from devkit.host.status import HostStatus, inspect_host

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
    "HostMcpDependencyError",
    "HostMcpError",
    "HostMcpInputError",
    "HostStatus",
    "adapter_for",
    "dispatch",
    "inspect_host",
    "plan_config",
    "read_hook",
]
