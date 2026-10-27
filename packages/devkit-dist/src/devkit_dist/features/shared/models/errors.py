"""Stable shared-artifact advisory codes for every transport and adapter; each class has its own mode."""

from devkit.advisory import Actor, AdvisoryError, Retry


class SharedError(AdvisoryError):
    """Corrupt envelope, unsafe storage path or missing stable lock (``MAINTENANCE``); nothing is repaired."""

    code = "SHARED_ARTIFACT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class InputError(SharedError):
    """A malformed field, URI, cursor, limit or body (``INPUT_ERROR``); the raiser names the flag in the target."""

    code = "SHARED_INPUT_INVALID"
    input_error = True
    fix = "Correct the value of [TARGET], then rerun"


class WorkspaceError(SharedError):
    """The workspace is not a Git checkout root with a retained main checkout (``INPUT_ERROR``)."""

    code = "SHARED_WORKSPACE_UNAVAILABLE"
    input_error = True
    target_files = ("--workspace-root",)
    fix = "Pass the top level of a Git checkout whose main checkout is retained to -w/--workspace-root"


class ExclusionError(SharedError):
    """Storage would hide tracked or visible foreign content (``BLOCKED``); no file was hidden."""

    code = "SHARED_EXCLUSION_CONFLICT"
    guardrail = True


class AdapterError(SharedError):
    """The selected adapter is unknown, duplicated or violates its contract (``MAINTENANCE``)."""

    code = "SHARED_ADAPTER_UNAVAILABLE"


class MissingError(SharedError):
    """The exact generation no longer exists (``INTERACTION``): only a fresh publication replaces it."""

    code = "SHARED_ARTIFACT_MISSING"
    actor = Actor.USER
    what_to_report = "The shared artifact no longer exists; the report must be published again as a fresh generation"


class ExpiredError(SharedError):
    """The seven-day lifetime elapsed (``INTERACTION``): only a fresh publication replaces it."""

    code = "SHARED_ARTIFACT_EXPIRED"
    actor = Actor.USER
    what_to_report = (
        "The shared artifact expired after seven days; the report must be published again as a fresh generation"
    )


class AccessError(SharedError):
    """Local permissions deny access (``INTERACTION``); never reroute to another transport or storage root."""

    code = "SHARED_ACCESS_DENIED"
    actor = Actor.USER
    what_to_report = "Local file permissions deny access to the shared artifact store; the user must grant access"


class TimeoutError(SharedError):
    """The ten-second operation deadline elapsed (``DEFER``)."""

    code = "SHARED_TIMEOUT"
    actor = Actor.NONE
    retry = Retry.SAFE
    retry_after = "10s"
