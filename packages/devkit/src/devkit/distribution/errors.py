"""Errors and notices of ``devkit.distribution``: ``AdvisoryError`` subclasses with stable codes, one class per code.

``devkit.core`` errors pass through unchanged: an unreadable receipt is
``ReceiptError`` (``RECEIPT_INVALID``), an invalid ``.devkit/config.toml`` is
``ConfigError`` (``CONFIG_INVALID``), a malformed argument (a selector, a
query, a bound, a path) is ``ArgumentError`` (``ARGUMENT_INVALID``).
Everything else a distribution operation refuses is one of the
``DistributionError`` classes below, so a caller branches on ``error.code`` and
the CLI renders the error as it is.

A ``SyncNotice`` is never raised: a synchronization collects it in
``SyncResult.notices`` (exit code ``0``) for something the caller should know
about although the sync succeeded, at level ``WARNING`` (the user must learn
or decide something) or ``NOTICE`` (worth knowing). Override drift under
``override_drift = "warn"`` is an ``OverrideDriftError`` lowered to
``WARNING``.
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level, Retry

LOCK_RETRY_AFTER = "the running devkit command finishes"


class DistributionError(AdvisoryError):
    """Base class of every error raised by ``devkit.distribution``; on its own an internal defect (``MAINTENANCE``)."""

    code = "DISTRIBUTION_FAILED"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class BundleError(DistributionError):
    """A bundle source is invalid: ``bundle.toml``, a declared source file, or the assets selected together."""

    code = "BUNDLE_INVALID"
    input_error = True


class PackageError(BundleError):
    """An installed content package does not register a usable bundle (a packaging defect, ``MAINTENANCE``)."""

    code = "BUNDLE_PACKAGE_INVALID"
    input_error = False


class SelectionError(DistributionError):
    """The named bundle, preset, asset or override does not exist in the current selection or installation."""

    code = "SELECTION_INVALID"
    input_error = True


class NotSynchronizedError(DistributionError):
    """The project has no receipt, or a file an agent reads no longer matches it; ``devkit sync`` reconciles."""

    code = "NOT_SYNCHRONIZED"
    actor = Actor.TOOL
    fix = "devkit sync"


class ReceiptStaleError(DistributionError):
    """``devkit sync --locked`` refused: the committed state (receipt, ``AGENTS.md`` block, seeded files) no longer
    matches the installed bundles, so restoring would mean changing it. Nothing was written.

    ``INTERACTION`` with exit code ``1``: a negative result, as for ``sync --check``. Updating committed files is
    the user's decision (a bundle source, the lock or the selection changed without its receipt), never an
    automatic retry.
    """

    code = "RECEIPT_STALE"
    actor = Actor.USER
    retry = Retry.AFTER_FIX
    exit_code = ExitCode.FINDINGS
    fix = "devkit sync, then commit the files it changes"


class ConflictError(DistributionError):
    """Writing would overwrite project-owned work: a hand-edited or unowned file."""

    code = "SYNC_CONFLICT"
    actor = Actor.USER
    what_to_report = "Which file to keep; devkit does not overwrite edits it does not own"


class BundleConflictError(ConflictError):
    """Two selected bundles, or a seeded file and a managed file, claim the same destination."""

    code = "BUNDLE_CONFLICT"
    what_to_report = "Which bundle to keep; deselect the other with `devkit remove <bundle>`"


class GuidanceBlockError(DistributionError):
    """The root ``AGENTS.md`` is not UTF-8, or its devkit block markers are malformed."""

    code = "GUIDANCE_BLOCK_INVALID"
    input_error = True
    target_files = ("AGENTS.md",)


class OverrideDriftError(DistributionError):
    """``override_drift = "block"`` refused a sync while an override hides upstream changes."""

    code = "OVERRIDE_DRIFT"
    guardrail = True


class UnsafeWorkspaceError(DistributionError):
    """A path devkit would read or write is a symlink, not a regular file, or outside what it may own."""

    code = "WORKSPACE_UNSAFE"
    guardrail = True


class LockHeldError(DistributionError):
    """Another devkit command holds the project lock."""

    code = "LOCK_HELD"
    actor = Actor.NONE
    retry = Retry.SAFE
    retry_after = LOCK_RETRY_AFTER


class PendingTransactionError(DistributionError):
    """An interrupted synchronization left its journal; ``devkit recover`` rolls it back."""

    code = "TRANSACTION_PENDING"
    actor = Actor.TOOL
    fix = "devkit recover"
    target_files = (".devkit/transient/sync-journal.json",)


class RecoveryError(DistributionError):
    """The journal of an interrupted synchronization is unusable, or later edits block its rollback (``HALT``)."""

    code = "RECOVERY_BLOCKED"
    actor = Actor.NONE
    retry = Retry.UNSAFE
    what_to_report = "The interrupted synchronization and the files named here; recovery needs a person"


class SyncNotice(DistributionError):
    """Base class of what a successful synchronization reports in ``SyncResult.notices``; never raised."""

    code = "SYNC_NOTICE"
    level = Level.NOTICE


class OrphanLeftNotice(SyncNotice):
    """A managed file edited by hand is no longer desired: left on disk untouched and dropped from the receipt."""

    code = "ORPHAN_LEFT"
    level = Level.WARNING


class StrayFilesNotice(SyncNotice):
    """Files under ``.devkit/managed/`` that neither the receipt nor the inventory owns: never deployed or removed."""

    code = "MANAGED_FILE_STRAY"
    level = Level.WARNING
    what_to_report = (
        "devkit neither deploys nor removes these files, yet tools that scan the managed root may read them; "
        "move project-owned files out of .devkit/managed/"
    )


class PostSyncHookFailedNotice(SyncNotice):
    """A ``devkit.post_sync`` hook raised or returned something other than a list; the sync itself succeeded."""

    code = "POST_SYNC_HOOK_FAILED"
    level = Level.WARNING


class UnprojectedNotice(SyncNotice):
    """A skill or subagent has no variant for a selected agent and was not projected for it (``brief``)."""

    code = "ASSET_UNPROJECTED"
    brief = True
    target_files = (".devkit/config.toml",)


class BundleUnselectedNotice(SyncNotice):
    """Installed bundles the project neither selected nor opted out of, announced once per clone when they appear."""

    code = "BUNDLE_UNSELECTED"


class BundleAutoSelectedNotice(SyncNotice):
    """Auto-selected bundles of other packages that this sync adds to the receipt with their default preset."""

    code = "BUNDLE_AUTO_SELECTED"
    what_to_report = "These bundles are now deployed because their packages are installed and declare auto_select"


class ToolVersionChangedNotice(SyncNotice):
    """The receipt was written by another devkit version; this sync recorded the running one."""

    code = "TOOL_VERSION_CHANGED"
    brief = True


class PostSyncNotice(SyncNotice):
    """A line a ``devkit.post_sync`` hook returned; the hook's package owns its meaning (``brief``)."""

    code = "POST_SYNC_NOTICE"
    brief = True
