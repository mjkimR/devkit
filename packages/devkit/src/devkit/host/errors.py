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


class HostMcpDependencyError(HostError):
    code = "HOST_MCP_EXTRA_REQUIRED"
    fix = "Install the devkit-agt[mcp] extra into the server runtime, then reconnect the MCP server"


class HostMcpRegistrationError(HostError):
    code = "HOST_MCP_REGISTRATION_FAILED"
    fix = "Run codex mcp list --json and codex mcp get devkit --json, correct CLI/configuration access, then retry devkit host mcp status"


class HostMcpRegistrationMissing(HostError):
    code = "HOST_MCP_REGISTRATION_MISSING"
    fix = "Run devkit host mcp setup --host codex from the retained base runtime"


class HostMcpRegistrationConflict(HostError):
    code = "HOST_MCP_REGISTRATION_CONFLICT"
    guardrail = True
    fix = "Inspect codex mcp get devkit --json; to replace that user-scoped entry, run devkit host mcp setup --host codex --replace from the retained base runtime"


class HostMcpRuntimeError(HostError):
    code = "HOST_MCP_RUNTIME_UNSAFE"
    fix = "Run devkit host mcp setup --host codex using the retained base checkout and its Python environment outside linked worktrees"


class HostMcpRegistrationShadowed(HostError):
    code = "HOST_MCP_REGISTRATION_SHADOWED"
    guardrail = True
    fix = "Inspect Codex project/profile MCP settings and the user devkit entry; resolve the override explicitly before retrying user-scoped setup"
