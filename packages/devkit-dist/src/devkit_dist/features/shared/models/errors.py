"""Stable shared-artifact advisory codes for every transport and adapter."""

from devkit.advisory import Actor, AdvisoryError, Retry


class SharedError(AdvisoryError):
    code = "SHARED_ARTIFACT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    fix = "Inspect the artifact and configuration; retry only after correcting the reported condition"


class InputError(SharedError):
    code = "SHARED_INPUT_INVALID"
    input_error = True


class WorkspaceError(SharedError):
    code = "SHARED_WORKSPACE_UNAVAILABLE"


class ExclusionError(SharedError):
    code = "SHARED_EXCLUSION_CONFLICT"
    guardrail = True


class AdapterError(SharedError):
    code = "SHARED_ADAPTER_UNAVAILABLE"


class MissingError(SharedError):
    code = "SHARED_ARTIFACT_MISSING"


class ExpiredError(SharedError):
    code = "SHARED_ARTIFACT_EXPIRED"


class AccessError(SharedError):
    code = "SHARED_ACCESS_DENIED"
    guardrail = True
    fix = "Inspect local permissions without switching transport or storage root"


class TimeoutError(SharedError):
    code = "SHARED_TIMEOUT"
    actor = Actor.NONE
    retry = Retry.SAFE
