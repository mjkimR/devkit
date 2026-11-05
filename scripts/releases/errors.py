"""Release-tool advisory failures, shared by silent helpers and the CLI boundary."""

from devkit.advisory import Actor, AdvisoryError, ExitCode, Retry


class ReleaseError(AdvisoryError):
    code = "RELEASE_INPUT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True
    fix = "Correct the named release metadata or supply a verified completed --baseline FILE, then rerun."


class StalePlanError(ReleaseError):
    code = "RELEASE_METADATA_STALE"
    exit_code = ExitCode.FINDINGS
    fix = "Run just version-sync --baseline FILE against the same completed baseline and commit the complete plan."


class ArtifactError(ReleaseError):
    code = "RELEASE_ARTIFACT_INVALID"
    input_error = False
    fix = "Restore the original immutable artifact and its verified checksum; never rebuild or overwrite that published identity."


class PreparationConflictError(ReleaseError):
    code = "RELEASE_PREPARATION_CONFLICT"
    input_error = False
    fix = "Keep the authored metadata edit and rerun just version-sync --baseline FILE after editing finishes."
