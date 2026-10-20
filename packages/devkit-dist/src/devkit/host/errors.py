"""Stable advisories for host configuration and hook dispatch."""

from devkit.advisory import Actor, AdvisoryError, Retry


class HostError(AdvisoryError):
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class HookDefinitionError(HostError):
    code = "HOST_HOOK_INVALID"
    input_error = True
    fix = "Correct the hook definition in [TARGET], then run devkit sync"


class HostConfigError(HostError):
    code = "HOST_CONFIG_INVALID"
    fix = "Correct the host configuration in [TARGET], then run devkit sync"


class HookConflictError(HostError):
    code = "HOST_HOOK_CONFLICT"
    guardrail = True
    fix = "Restore the receipt-recorded hook entries in [TARGET], preserve other entries, then run devkit sync"


class HookDispatchError(HostError):
    code = "HOST_HOOK_DISPATCH_FAILED"
    fix = "Run devkit host status --format json, correct the reported installation or handler problem, then retry"


class HookMissingError(HostError):
    code = "HOST_HOOK_MISSING"
    fix = "Run devkit sync to restore the missing host hook configuration"


class HostMcpError(HostError):
    code = "HOST_MCP_FAILED"
    fix = "Inspect the installed devkit.host.services entry points and server environment, correct the failure and reconnect"


class HostMcpInputError(HostError):
    code = "HOST_MCP_ARGUMENT_INVALID"
    input_error = True
    fix = "Read the MCP tool input schema and call it with the declared arguments"


class HostConfirmationError(HostError):
    code = "HOST_CONFIRMATION_UNAVAILABLE"
    guardrail = True
    fix = "Use an interactive Codex client with form elicitation enabled; repeat the confirmation call only after inspecting Git state"
