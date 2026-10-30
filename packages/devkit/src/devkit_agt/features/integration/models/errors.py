"""Actionable failures of scoped local integration."""

from devkit.advisory import Actor, AdvisoryError, Level, Retry


class IntegrationError(AdvisoryError):
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class IntegrationConfigError(IntegrationError):
    code = "INTEGRATION_CONFIG_INVALID"
    input_error = True
    target_files = (".devkit/config.toml",)
    fix = "Configure integration.provider in the base project's .devkit/config.toml and install its readiness provider"


class ReadinessError(IntegrationError):
    """The provider found readiness conditions the agent resolves in the source (``INPUT_ERROR``); its reasons are
    the details."""

    code = "INTEGRATION_NOT_READY"
    input_error = True
    fix = "Resolve the reported readiness conditions, commit the final changes and prepare a new integration request"


class ProviderError(IntegrationError):
    code = "INTEGRATION_PROVIDER_FAILED"
    fix = "Repair or install the configured readiness provider, then prepare a new integration request"


class StaleRequestError(IntegrationError):
    """The observed state no longer matches the approved scope (``BLOCKED``). A digest presented to ``integrate`` that
    differs from the current scope is raised with ``actor=USER`` instead (``INTERACTION``): the user approves again."""

    code = "INTEGRATION_REQUEST_STALE"
    guardrail = True
    fix = "Inspect Git, PR and cleanup state, preserve completed steps, then obtain Host approval for a new `uv run devkit integration integrate` invocation covering only the remaining scope"


class AuthorityError(IntegrationError):
    """Integration lacks authority (``BLOCKED``): the automatic policy refusing the pull-request route, a request
    without authority. ``integrate`` under ``ask`` without a digest is raised with ``actor=USER`` instead
    (``INTERACTION``): the user approves the prepared scope."""

    code = "INTEGRATION_AUTHORITY_REQUIRED"
    guardrail = True
    fix = "Inspect the retained base policy and selected route; under `ask`, obtain Host conversational approval before running `uv run devkit integration integrate`, and obtain separate publication authority for the pull-request route"


class CleanupContractError(IntegrationError):
    code = "INTEGRATION_CLEANUP_UNSCOPED"
    guardrail = True
    fix = (
        "Update the named post-finish extension to the scoped local-only cleanup contract before preparing integration"
    )


class RuntimeLocationError(IntegrationError):
    code = "INTEGRATION_RUNTIME_IN_WORKTREE"
    guardrail = True
    fix = "Run `uv run devkit integration integrate` from the retained base checkout with an installed runtime outside the worktree being removed"


class RuleRuntimeMismatchError(IntegrationError):
    code = "INTEGRATION_RULE_RUNTIME_MISMATCH"
    actor = Actor.USER
    fix = (
        "The source's synchronized rules import code this runtime does not provide, so readiness cannot evaluate them"
        " here; the source needs no change. Obtain separately granted Host authority, build a runtime from the"
        " source's code outside the worktree being removed (for example a `git archive` of the source installed into"
        " a scratch environment), then run `uv run devkit integration integrate` for this branch from the base checkout with that"
        " runtime. Do not edit the rules, skip readiness or run the worktree's own runtime"
    )


class CleanupIncompleteWarning(IntegrationError):
    code = "INTEGRATION_CLEANUP_INCOMPLETE"
    level = Level.WARNING
    fix = "Inspect the approved cleanup targets and actual Git or PR state, resolve the reported condition, then rerun `uv run devkit integration integrate` only when the source and remaining cleanup scope can be revalidated"


class GeneratedSeededWarning(IntegrationError):
    """The merge kept generated files from one side without regenerating them (``WARNING``,
    ``ADR-generated-conflicts-in-prepared-merge``): they are stale on the target until regenerated. The raiser sets
    one detail per artifact and the fix with the exact ``devkit generated regen`` command."""

    code = "INTEGRATION_GENERATED_SEEDED"
    level = Level.WARNING


class TargetMovedError(IntegrationError):
    code = "INTEGRATION_TARGET_MOVED"
    guardrail = True
    fix = (
        "Inspect the base branch: a non-devkit write moved it between the build and its fast-forward; nothing changed"
        " on the target. Recheck the source, target and readiness, then obtain fresh Host approval and run"
        " `uv run devkit integration integrate` for the current observed state"
    )


class ReceiptConflictError(IntegrationError):
    code = "INTEGRATION_RECEIPT_CONFLICT"
    guardrail = True
    fix = (
        "Merge the target into the task branch in its worktree to resolve the receipt conflict, run `uv run devkit sync`"
        " there so the receipt matches the merged files, commit, re-verify what the merge changed and prepare again;"
        " run `uv run devkit integration integrate` for this branch only after Host approval of the new scope"
    )


class ReceiptReaderChangedError(IntegrationError):
    code = "INTEGRATION_RECEIPT_READER_CHANGED"
    actor = Actor.USER
    fix = (
        "A runtime built from the target cannot read this source's receipt; restarting the MCP server does not help."
        " Resolve the runtime mismatch, then obtain"
        " Host authority for `uv run devkit integration integrate` for this branch in the base checkout using a runtime built from"
        " the source's code. Do not edit the receipt or switch routes without that authority"
    )


class ApproachMismatchError(ReadinessError):
    code = "INTEGRATION_APPROACH_MISMATCH"
    fix = "Use the existing SDD readiness provider for SDD projects; inspect `uv run devkit config show`"


class LifecycleValidationRequiredError(ReadinessError):
    code = "INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED"
    fix = "Run the matching lifecycle validator for the touched retained Unit before integration"
