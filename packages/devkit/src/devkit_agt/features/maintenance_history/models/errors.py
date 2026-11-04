"""Stable failures and notices for maintenance history."""

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level, Retry


class HistoryError(AdvisoryError):
    actor = Actor.USER
    retry = Retry.AFTER_FIX
    fix = "Correct the history input and rerun the same command"


class InputError(HistoryError):
    code = "HISTORY_INPUT_INVALID"
    input_error = True


class AuthorityMissing(HistoryError):
    code = "HISTORY_AUTHORITY_MISSING"
    input_error = True
    fix = "Pass --authority only after the user authorizes the selected destination"


class BranchForeign(HistoryError):
    code = "HISTORY_BRANCH_FOREIGN"
    guardrail = True
    fix = "Choose a history branch that descends from the frozen root; the foreign branch is unchanged"


class BranchMissing(HistoryError):
    code = "HISTORY_BRANCH_MISSING"
    fix = "Request authority to run maintenance history init for the selected destination"


class RepositoryEmpty(HistoryError):
    code = "HISTORY_REPOSITORY_EMPTY"
    guardrail = True
    fix = "Create the repository initial commit before initializing history"


class GhUnavailable(HistoryError):
    code = "HISTORY_GH_UNAVAILABLE"
    fix = "Install gh or log in with gh auth login, then rerun"


class Deferred(HistoryError):
    code = "HISTORY_DEFERRED"
    actor = Actor.NONE
    retry = Retry.SAFE
    retry_after = "60s"
    exit_code = ExitCode.FINDINGS
    fix = "Retry later with the same run and inputs"


class SnapshotFailed(HistoryError):
    code = "HISTORY_SNAPSHOT_FAILED"
    input_error = True
    fix = "Fix the clean filter or unreadable inspected path, then rerun"


class ReportMismatch(HistoryError):
    code = "HISTORY_REPORT_MISMATCH"
    input_error = True
    fix = "Use the report path fixed at history start"


class SecretFound(HistoryError):
    code = "HISTORY_SECRET_FOUND"
    input_error = True
    exit_code = ExitCode.FINDINGS
    fix = "Remove the secret from the report or record, or deselect the added file, then rerun"


class EvidenceChanged(HistoryError):
    code = "HISTORY_EVIDENCE_CHANGED"
    input_error = True
    exit_code = ExitCode.FINDINGS
    fix = "Create a new run for changed evidence; use an amendment for later integration state"


class PublishFailed(HistoryError):
    code = "HISTORY_PUBLISH_FAILED"
    exit_code = ExitCode.FINDINGS
    fix = "Correct destination permissions or branch rules, then rerun the same run"


class RecordCollision(HistoryError):
    code = "HISTORY_RECORD_COLLISION"
    guardrail = True
    exit_code = ExitCode.FINDINGS
    fix = "Create a new run for different content; never overwrite the existing record"


class PublishUnknown(HistoryError):
    code = "HISTORY_PUBLISH_UNKNOWN"
    exit_code = ExitCode.FINDINGS
    fix = "Inspect the destination by rerunning the same operation; never resend blindly"


class RunMissing(HistoryError):
    code = "HISTORY_RUN_MISSING"
    input_error = True
    exit_code = ExitCode.FINDINGS
    fix = "Check the run ID with maintenance history list"


class RunDrifted(HistoryError):
    code = "HISTORY_RUN_DRIFTED"
    level = Level.WARNING
    fix = "Revalidate the report evidence against the changed inspected content"


class BranchAbsent(BranchMissing):
    level = Level.NOTICE
    fix = "Initialize history only after the user authorizes its destination"
