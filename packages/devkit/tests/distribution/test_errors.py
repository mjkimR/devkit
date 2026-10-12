"""Every distribution error is an ``AdvisoryError`` with a stable code and the directive its condition needs."""

from __future__ import annotations

import pytest
from devkit.advisory import ActionMode, AdvisoryError, ExitCode
from devkit.distribution import errors


@pytest.mark.parametrize(
    ("cls", "code", "mode"),
    [
        (errors.DistributionError, "DISTRIBUTION_FAILED", ActionMode.MAINTENANCE),
        (errors.BundleError, "BUNDLE_INVALID", ActionMode.INPUT_ERROR),
        (errors.PackageError, "BUNDLE_PACKAGE_INVALID", ActionMode.MAINTENANCE),
        (errors.SelectionError, "SELECTION_INVALID", ActionMode.INPUT_ERROR),
        (errors.NotSynchronizedError, "NOT_SYNCHRONIZED", ActionMode.AUTO),
        (errors.ConflictError, "SYNC_CONFLICT", ActionMode.INTERACTION),
        (errors.BundleConflictError, "BUNDLE_CONFLICT", ActionMode.INTERACTION),
        (errors.GuidanceBlockError, "GUIDANCE_BLOCK_INVALID", ActionMode.INPUT_ERROR),
        (errors.OverrideDriftError, "OVERRIDE_DRIFT", ActionMode.BLOCKED),
        (errors.UnsafeWorkspaceError, "WORKSPACE_UNSAFE", ActionMode.BLOCKED),
        (errors.LockHeldError, "LOCK_HELD", ActionMode.DEFER),
        (errors.PendingTransactionError, "TRANSACTION_PENDING", ActionMode.AUTO),
        (errors.RecoveryError, "RECOVERY_BLOCKED", ActionMode.HALT),
    ],
)
def test_error_classes_carry_code_and_mode(cls: type[errors.DistributionError], code: str, mode: ActionMode) -> None:
    error = cls("x")
    assert isinstance(error, AdvisoryError) and not isinstance(error, ValueError)
    assert (error.code, error.mode, error.exit_code) == (code, mode, ExitCode.ERROR)


@pytest.mark.parametrize(
    ("cls", "code", "mode"),
    [
        (errors.OrphanLeftNotice, "ORPHAN_LEFT", ActionMode.INTERACTION),
        (errors.ToolVersionChangedNotice, "TOOL_VERSION_CHANGED", ActionMode.DEFER),
        (errors.PostSyncNotice, "POST_SYNC_NOTICE", ActionMode.DEFER),
        (errors.PostSyncHookFailedNotice, "POST_SYNC_HOOK_FAILED", ActionMode.MAINTENANCE),
    ],
)
def test_notices_are_coded_and_never_fail(cls: type[errors.SyncNotice], code: str, mode: ActionMode) -> None:
    notice = cls("x")
    assert (notice.code, notice.mode, notice.exit_code) == (code, mode, ExitCode.OK)


def test_fixes_name_the_command_that_repairs_the_state() -> None:
    assert errors.NotSynchronizedError("x").fix == "devkit sync"
    assert errors.PendingTransactionError("x").fix == "devkit recover"
    assert errors.LockHeldError("x").retry_after == errors.LOCK_RETRY_AFTER
