"""Actionable failures of scoped local integration."""

from devkit.advisory import Actor, AdvisoryError, Level, Retry


class IntegrationError(AdvisoryError):
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class IntegrationConfigError(IntegrationError):
    code = "INTEGRATION_CONFIG_INVALID"
    input_error = True
    fix = "Configure integration.provider in the base project's .devkit/config.toml and install its readiness provider"


class ReadinessError(IntegrationError):
    code = "INTEGRATION_NOT_READY"
    guardrail = True
    fix = "Resolve the reported readiness conditions, commit the final changes and prepare a new integration request"


class ProviderError(IntegrationError):
    code = "INTEGRATION_PROVIDER_FAILED"
    fix = "Repair or install the configured readiness provider, then prepare a new integration request"


class StaleRequestError(IntegrationError):
    code = "INTEGRATION_REQUEST_STALE"
    guardrail = True
    fix = "Inspect Git and cleanup state, preserve completed steps and obtain approval for a new request covering only the remaining scope"


class AuthorityError(IntegrationError):
    code = "INTEGRATION_AUTHORITY_REQUIRED"
    guardrail = True
    fix = "Call integration_integrate for current shared-policy authority or native ask confirmation; resume only an authorized request retained in this server process"


class CleanupContractError(IntegrationError):
    code = "INTEGRATION_CLEANUP_UNSCOPED"
    guardrail = True
    fix = (
        "Update the named post-finish extension to the scoped local-only cleanup contract before preparing integration"
    )


class RuntimeLocationError(IntegrationError):
    code = "INTEGRATION_RUNTIME_IN_WORKTREE"
    guardrail = True
    fix = "Run the MCP server from the retained base checkout using an installed runtime outside the worktree being removed"


class CleanupIncompleteWarning(IntegrationError):
    code = "INTEGRATION_CLEANUP_INCOMPLETE"
    level = Level.WARNING
    fix = "Inspect the approved cleanup targets, resolve the reported condition and call integration_resume with the same request id"


class TargetMovedError(IntegrationError):
    code = "INTEGRATION_TARGET_MOVED"
    guardrail = True
    fix = (
        "Inspect the base branch: a non-devkit write moved it between the build and its fast-forward; nothing changed"
        " on the target. Call integration_resume while the target still equals the last build target, else call"
        " integration_integrate for a new confirmation"
    )


class ReceiptConflictError(IntegrationError):
    code = "INTEGRATION_RECEIPT_CONFLICT"
    guardrail = True
    fix = (
        "Merge the target into the task branch in its worktree, run devkit sync there so the receipt matches the"
        " merged files, commit, re-verify and call integration_integrate again"
    )
