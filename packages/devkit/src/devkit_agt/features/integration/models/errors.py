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
    fix = "Inspect Git, PR and cleanup state, preserve completed steps, then obtain Host approval for a new `devkit integration integrate` invocation covering only the remaining scope"


class AuthorityError(IntegrationError):
    code = "INTEGRATION_AUTHORITY_REQUIRED"
    guardrail = True
    fix = "Inspect the retained base policy and selected route; under `ask`, obtain Host conversational approval before running `devkit integration integrate`, and obtain separate publication authority for the pull-request route"


class CleanupContractError(IntegrationError):
    code = "INTEGRATION_CLEANUP_UNSCOPED"
    guardrail = True
    fix = (
        "Update the named post-finish extension to the scoped local-only cleanup contract before preparing integration"
    )


class RuntimeLocationError(IntegrationError):
    code = "INTEGRATION_RUNTIME_IN_WORKTREE"
    guardrail = True
    fix = "Run `devkit integration integrate` from the retained base checkout with an installed runtime outside the worktree being removed"


class RuleRuntimeMismatchError(IntegrationError):
    code = "INTEGRATION_RULE_RUNTIME_MISMATCH"
    actor = Actor.USER
    fix = (
        "The source's synchronized rules import code this runtime does not provide, so readiness cannot evaluate them"
        " here; the source needs no change. Obtain separately granted Host authority, build a runtime from the"
        " source's code outside the worktree being removed (for example a `git archive` of the source installed into"
        " a scratch environment), then run `devkit integration integrate <branch>` from the base checkout with that"
        " runtime. Do not edit the rules, skip readiness or run the worktree's own runtime"
    )


class CleanupIncompleteWarning(IntegrationError):
    code = "INTEGRATION_CLEANUP_INCOMPLETE"
    level = Level.WARNING
    fix = "Inspect the approved cleanup targets and actual Git or PR state, resolve the reported condition, then rerun `devkit integration integrate` only when the source and remaining cleanup scope can be revalidated"


class TargetMovedError(IntegrationError):
    code = "INTEGRATION_TARGET_MOVED"
    guardrail = True
    fix = (
        "Inspect the base branch: a non-devkit write moved it between the build and its fast-forward; nothing changed"
        " on the target. Recheck the source, target and readiness, then obtain fresh Host approval and run"
        " `devkit integration integrate` for the current observed state"
    )


class ReceiptConflictError(IntegrationError):
    code = "INTEGRATION_RECEIPT_CONFLICT"
    guardrail = True
    fix = (
        "Merge the target into the task branch in its worktree, run devkit sync there so the receipt matches the"
        " merged files, commit, re-verify and rerun `devkit integration integrate <branch>` after Host approval"
    )


class ReceiptReaderChangedError(IntegrationError):
    code = "INTEGRATION_RECEIPT_READER_CHANGED"
    actor = Actor.USER
    fix = (
        "A runtime built from the target cannot read this source's receipt; restarting the MCP server does not help."
        " Resolve the runtime mismatch, then obtain"
        " Host authority for `devkit integration integrate <branch>` in the base checkout using a runtime built from"
        " the source's code. Do not edit the receipt or switch routes without that authority"
    )
