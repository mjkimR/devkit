"""Errors and notices of ``devkit_dist.features.distribution``: ``AdvisoryError`` subclasses with stable codes, one class per code.

``devkit_dist.base.errors`` errors pass through unchanged: an unreadable receipt is
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
``WARNING`` (``override_drift``).
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level, Retry
from devkit_core.base.errors import LockHeldError as CoreLockHeldError

from devkit_dist.base.errors import HARNESS_INSTALL_FIX
from devkit_dist.features.project.models.invocation import devkit_command

LOCK_RETRY_AFTER = "the running devkit command finishes"


class DistributionError(AdvisoryError):
    """Base class of every error raised by ``devkit_dist.features.distribution``; on its own an internal defect (``MAINTENANCE``)."""

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


class PlaybookAliasAmbiguousError(SelectionError):
    """A ``devkit playbook get`` alias is declared by more than one effective playbook header of the bundle."""

    code = "PLAYBOOK_ALIAS_AMBIGUOUS"


class NotSynchronizedError(DistributionError):
    """The project has no receipt, or a file an agent reads no longer matches it; ``devkit sync`` reconciles."""

    code = "NOT_SYNCHRONIZED"
    actor = Actor.TOOL
    fix = devkit_command("sync")


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
    fix = devkit_command("sync")


class ConflictError(DistributionError):
    """Writing would overwrite project-owned work: a hand-edited or unowned file."""

    code = "SYNC_CONFLICT"
    actor = Actor.USER
    what_to_report = "Which file to keep; devkit does not overwrite edits it does not own"


class BundleConflictError(ConflictError):
    """Two selected bundles, or a seeded file and a managed file, claim the same destination."""

    code = "BUNDLE_CONFLICT"
    what_to_report = "Which of the colliding assets to keep; devkit deploys one file per destination"

    @classmethod
    def between(cls, message: str, destination: str, bundles: list[str]) -> BundleConflictError:
        """The collision of ``destination`` claimed by ``bundles``.

        Two bundles: the question names both, and each ``[DETAIL]`` is the command that deselects one of them.
        """
        bundles = sorted(set(bundles))
        if len(bundles) < 2:
            return cls(message, target_files=[destination])
        return cls(
            message,
            *(devkit_command(f"remove {name}") for name in bundles),
            target_files=[destination],
            what_to_report=f"Which bundle to keep: {' or '.join(bundles)}; the other is deselected",
        )


class GuidanceBlockError(DistributionError):
    """The root ``AGENTS.md`` is not UTF-8, or its devkit block markers are malformed."""

    code = "GUIDANCE_BLOCK_INVALID"
    input_error = True
    target_files = ("AGENTS.md",)


class OverrideDriftError(DistributionError):
    """An override hides upstream changes: under ``override_drift = "block"`` the sync refuses (``INTERACTION``:
    whether the override takes over the change is the user's decision); under ``warn`` it is lowered to a
    ``WARNING``. Built by ``override_drift`` for ``devkit sync`` and ``devkit status`` alike."""

    code = "OVERRIDE_DRIFT"
    actor = Actor.USER


def review_commands(selectors: list[str]) -> tuple[str, list[str]]:
    """The ``fix`` and ``[DETAIL]`` lines that review and accept the overrides ``selectors`` (``bundle:asset``).

    One override: its ``override diff`` is the fix and its ``override accept`` the detail. Several: ``override list``
    is the fix and each override's ``diff`` and ``accept`` are details.
    """
    if len(selectors) == 1:
        return devkit_command(f"override diff {selectors[0]}"), [devkit_command(f"override accept {selectors[0]}")]
    details = [devkit_command(f"override {verb} {item}") for item in selectors for verb in ("diff", "accept")]
    return devkit_command("override list"), details


def override_drift(
    selectors: list[str], paths: list[str], *, blocked: bool, exit_code: ExitCode | None = None
) -> OverrideDriftError:
    """One ``OVERRIDE_DRIFT`` for every drifted override: ``selectors`` (``bundle:asset``) in the message, their
    workspace-relative override ``paths`` as targets. ``blocked`` (``override_drift = "block"``) keeps the error;
    otherwise it is lowered to ``WARNING``."""
    policy = ' (override_drift = "block")' if blocked else ""
    fix, details = review_commands(selectors)
    error = OverrideDriftError(
        f"upstream drift behind an override{policy}: {', '.join(selectors)}",
        *details,
        target_files=paths,
        fix=fix,
        what_to_report=(
            "Upstream changed an asset this project overrides; whether to merge the change into the override"
            " (review the diff, then accept it) or keep the override as it is"
        ),
        exit_code=exit_code,
    )
    return error if blocked else error.with_level(Level.WARNING)


class UnsafeWorkspaceError(DistributionError):
    """A path devkit would read or write is a symlink, not a regular file, or outside what it may own."""

    code = "WORKSPACE_UNSAFE"
    guardrail = True


class LockHeldError(DistributionError, CoreLockHeldError):
    """Another devkit command holds the project lock.

    Also a ``devkit_core.core.LockHeldError`` (the same ``LOCK_HELD`` code), so catching either class catches it.
    """

    code = "LOCK_HELD"
    actor = Actor.NONE
    retry = Retry.SAFE
    retry_after = LOCK_RETRY_AFTER


class PendingTransactionError(DistributionError):
    """An interrupted synchronization left its journal; ``devkit recover`` rolls it back."""

    code = "TRANSACTION_PENDING"
    actor = Actor.TOOL
    fix = devkit_command("recover")
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
    """Files devkit no longer uses, left on disk untouched: a hand-edited managed file (or guidance block) that is no
    longer desired, dropped from the receipt; or a project file under an override that ``override remove`` keeps."""

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


class PostSyncExtensionFailedNotice(SyncNotice):
    """A ``devkit.post_sync`` extension raised or returned something other than a list; the sync itself succeeded."""

    code = "POST_SYNC_EXTENSION_FAILED"
    level = Level.WARNING


class ConfigTemplateExtensionFailedNotice(DistributionError):
    """A ``devkit.config_template`` or ``devkit.config_tables`` extension failed to load, raised, returned no valid
    tables or (``devkit.config_tables``) is not named after a reserved table; never raised.

    Its tables are left out of the template and the command that renders it succeeds.
    """

    code = "CONFIG_TEMPLATE_EXTENSION_FAILED"
    level = Level.WARNING
    target_files = (".devkit/config.toml",)


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
    """A line a ``devkit.post_sync`` extension returned; its package owns its meaning (``brief``)."""

    code = "POST_SYNC_NOTICE"
    brief = True


class HarnessEngineMissingNotice(SyncNotice):
    """Deployed rule, gate or workflow assets that no installed engine runs: no ``devkit.commands`` entry point named
    ``rules``, ``gate`` or ``workflow`` (``devkit-agt`` is not installed). The assets are deployed as selected; only
    the engine is missing, and adding it is the user's decision (``[FIX]`` when they ask). Reported by ``devkit sync``
    and ``devkit status``."""

    code = "HARNESS_ENGINE_MISSING"
    level = Level.WARNING
    fix = HARNESS_INSTALL_FIX
    what_to_report = "These assets are deployed, but nothing runs them until devkit-agt is installed"


class OverrideRetainedNotice(SyncNotice):
    """``devkit remove`` deselected a bundle whose project overrides stay under ``.devkit/overrides/<bundle>/``: they
    apply again, with their drift reported, when the bundle is selected again; ``devkit override list`` keeps them."""

    code = "OVERRIDE_RETAINED"
    what_to_report = "Overrides of the removed bundles stay in place; delete the directories to drop them"


class OverrideSyncDeferredNotice(SyncNotice):
    """``devkit override accept`` under ``override_drift = "block"`` recorded the new baseline only: other deployed
    overrides still drift, and a sync now would deploy their upstream changes beside stale override files. The last
    accept synchronizes; until then ``sync --check`` may report pending work."""

    code = "OVERRIDE_SYNC_DEFERRED"


class McpRegistrationPendingNotice(SyncNotice):
    """Selected hosts whose local MCP registration ``[mcp] register`` asks for but this checkout does not hold:
    ``devkit sync --locked`` restores assets only, so a fresh clone or worktree registers in a separate step."""

    code = "MCP_REGISTRATION_PENDING"
    fix = devkit_command("sync --registrations-only")
