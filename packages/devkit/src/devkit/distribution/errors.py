"""Errors raised by ``devkit.distribution``: ``AdvisoryError`` subclasses with stable codes.

``devkit.core`` errors pass through unchanged: an unreadable receipt is
``ReceiptError`` (``RECEIPT_INVALID``), an invalid ``.devkit/config.toml`` is
``ConfigError`` (``CONFIG_INVALID``). Everything else a distribution operation
refuses is one of the classes below, so a caller branches on ``error.code``
and the CLI renders the error as it is.
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, Retry

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


class ArgumentError(DistributionError):
    """A command argument or library parameter is malformed (a selector, a query, a bound, a path)."""

    code = "ARGUMENT_INVALID"
    input_error = True


class SelectionError(DistributionError):
    """The named bundle, preset, asset or override does not exist in the current selection or installation."""

    code = "SELECTION_INVALID"
    input_error = True


class NotSynchronizedError(DistributionError):
    """The project has no receipt, or a file an agent reads no longer matches it; ``devkit sync`` reconciles."""

    code = "NOT_SYNCHRONIZED"
    actor = Actor.TOOL
    fix = "devkit sync"


class ConflictError(DistributionError):
    """Writing would overwrite project-owned work: a hand-edited or unowned file, or two bundles claiming one path."""

    code = "SYNC_CONFLICT"
    actor = Actor.USER
    what_to_report = "Which file to keep; devkit does not overwrite edits it does not own"


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
