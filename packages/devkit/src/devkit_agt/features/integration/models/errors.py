"""Actionable failures of scoped local integration."""

from devkit.advisory import Actor, AdvisoryError, Level, Retry


class IntegrationError(AdvisoryError):
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class IntegrationConfigError(IntegrationError):
    code = "INTEGRATION_CONFIG_INVALID"
    input_error = True
    target_files = (".devkit/config.toml",)
    fix = "Correct the reported integration configuration or route in the retained base .devkit/config.toml"


class ProviderError(IntegrationError):
    code = "INTEGRATION_PROVIDER_FAILED"
    fix = (
        "Inspect the failing integration operation and completed effects, repair its cause and prepare remaining scope"
    )


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


class CleanupIncompleteWarning(IntegrationError):
    code = "INTEGRATION_CLEANUP_INCOMPLETE"
    level = Level.WARNING
    fix = (
        "Git integration and cleanup landed; inspect each reported cleanup target, resolve its condition, then run"
        " that extension's owning command against the exact target; do not prepare or integrate again"
    )


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
        " on the target. Recheck the source, target and policy, then obtain fresh Host approval and run"
        " `uv run devkit integration integrate` for the current observed state"
    )
