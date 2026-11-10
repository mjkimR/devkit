"""Stable adaptive assignment advisories."""

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level, Retry


class AdaptiveError(AdvisoryError):
    """Base for assignment advisories."""

    input_error = True
    retry = Retry.AFTER_FIX
    fix = "Correct the assignment input or returned work, then rerun the command"


class RepositoryUnsupported(AdaptiveError):
    """repository unsupported."""

    code = "ADAPTIVE_REPOSITORY_UNSUPPORTED"


class LedgerUnreadable(AdaptiveError):
    """ledger unreadable."""

    code = "ADAPTIVE_LEDGER_UNREADABLE"
    input_error = False
    actor = Actor.USER
    fix = "Ask whether to move the damaged ledger aside before recording further assignments"


class LedgerUnwritable(AdaptiveError):
    """ledger unwritable."""

    code = "ADAPTIVE_LEDGER_UNWRITABLE"
    input_error = False
    actor = Actor.USER
    fix = "Report assignments as unrecorded and ask the user to restore write access to the ledger"


class AssignmentUnknown(AdaptiveError):
    """assignment unknown."""

    code = "ADAPTIVE_ASSIGNMENT_UNKNOWN"


class AssignmentExists(AdaptiveError):
    """assignment exists."""

    code = "ADAPTIVE_ASSIGNMENT_EXISTS"


class AssignmentClosed(AdaptiveError):
    """assignment closed."""

    code = "ADAPTIVE_ASSIGNMENT_CLOSED"


class AssignmentNotReturned(AdaptiveError):
    """assignment not returned."""

    code = "ADAPTIVE_ASSIGNMENT_NOT_RETURNED"


class WorktreeUnavailable(AdaptiveError):
    """worktree unavailable."""

    code = "ADAPTIVE_WORKTREE_UNAVAILABLE"


class RevisionUnresolved(AdaptiveError):
    """revision unresolved."""

    code = "ADAPTIVE_REVISION_UNRESOLVED"


class GoverningUnresolved(AdaptiveError):
    """governing unresolved."""

    code = "ADAPTIVE_GOVERNING_UNRESOLVED"
    fix = "Correct the governing value, bring the document into the assignment worktree, or pass an absolute path of a readable copy"


class ScopeOverlap(AdaptiveError):
    """scope overlap."""

    code = "ADAPTIVE_SCOPE_OVERLAP"
    fix = "Narrow the write scope, close the other assignment when finished, or name it in --depends-on for sequenced work"


class AuthorityNotNarrowed(AdaptiveError):
    """authority not narrowed."""

    code = "ADAPTIVE_AUTHORITY_NOT_NARROWED"


class NestingDepth(AdaptiveError):
    """nesting depth."""

    code = "ADAPTIVE_NESTING_DEPTH"


class ChildrenOutstanding(AdaptiveError):
    """children outstanding."""

    code = "ADAPTIVE_CHILDREN_OUTSTANDING"


class ReturnNotCompleted(AdaptiveError):
    """return not completed."""

    exit_code = ExitCode.FINDINGS

    code = "ADAPTIVE_RETURN_NOT_COMPLETED"


class BaseNotAncestor(AdaptiveError):
    """base not ancestor."""

    exit_code = ExitCode.FINDINGS

    code = "ADAPTIVE_BASE_NOT_ANCESTOR"


class HeadMoved(AdaptiveError):
    """head moved."""

    exit_code = ExitCode.FINDINGS

    code = "ADAPTIVE_HEAD_MOVED"


class CommitNotGranted(AdaptiveError):
    """commit not granted."""

    exit_code = ExitCode.FINDINGS

    code = "ADAPTIVE_COMMIT_NOT_GRANTED"


class ScopeViolation(AdaptiveError):
    """scope violation."""

    exit_code = ExitCode.FINDINGS

    code = "ADAPTIVE_SCOPE_VIOLATION"


class CheckOutcomeMissing(AdaptiveError):
    """check outcome missing."""

    exit_code = ExitCode.FINDINGS

    code = "ADAPTIVE_CHECK_OUTCOME_MISSING"


class CheckNotPassed(AdaptiveError):
    """check not passed."""

    exit_code = ExitCode.FINDINGS

    code = "ADAPTIVE_CHECK_NOT_PASSED"


class UncommittedChanges(AdaptiveError):
    """uncommitted changes."""

    code = "ADAPTIVE_UNCOMMITTED_CHANGES"
    level = Level.WARNING


class ClosedUnverified(AdaptiveError):
    """closed unverified."""

    code = "ADAPTIVE_CLOSED_UNVERIFIED"
    level = Level.WARNING


class LedgerFragmentIgnored(AdaptiveError):
    """ledger fragment ignored."""

    code = "ADAPTIVE_LEDGER_FRAGMENT_IGNORED"
    level = Level.WARNING


class PreexistingDirty(AdaptiveError):
    """preexisting dirty."""

    code = "ADAPTIVE_PREEXISTING_DIRTY"
    level = Level.NOTICE
