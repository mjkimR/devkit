"""Errors of ``devkit.gate``: ``AdvisoryError`` subclasses, one class per code.

Every class derives from ``GateError``, which sets the area's ``actor`` and
``retry`` defaults once. Construct them message first, with keyword fields
(``fix=``, ``target_files=``, ``code=`` for a gate's own refusal code).

``devkit.core`` errors pass through unchanged: an unreadable
``.devkit/config.toml`` or ``devkit.config`` is ``ConfigError``
(``CONFIG_INVALID``), a malformed receipt ``ReceiptError``
(``RECEIPT_INVALID``), a missing or drifted gate file ``AssetFileError``
(``ASSET_FILE_INVALID``), a failed Git query ``GitError`` (``GIT_FAILED``).
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level, Retry
from devkit.core.errors import ConfigError

PYTHON_FIX = (
    "Pass `--python` the interpreter of an environment where devkit is installed: `devkit gate install --python <path>`"
)


class GateError(AdvisoryError):
    """Base class of every error raised by ``devkit.gate``; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class GateRefusedError(GateError):
    """Raised by a gate to refuse the commit (``BLOCKED``).

    A refusal is the negative result of a check that ran, so it exits
    ``FINDINGS`` (``1``). ``GATE_FAILED`` is the default code; a gate passes its
    own (``code="GATE_MESSAGE_EMPTY"``) and puts the remediation in ``fix``.
    """

    code = "GATE_FAILED"
    guardrail = True
    exit_code = ExitCode.FINDINGS


class GateConfigError(GateError, ConfigError):
    """The ``[gates]`` table or a gate's configured settings are invalid, or a configured gate is not installed.

    A subclass of the core ``ConfigError``: a configuration file that cannot be
    read or parsed at all is that core error (``CONFIG_INVALID``) itself.
    """

    code = "GATE_CONFIG_INVALID"
    target_files = ()
    fix = "Correct the [gates] table in .devkit/config.toml or in the clone-local <common-git-dir>/devkit.config"


class VerifyNotRunError(GateError):
    """A ``verify-commands`` command could not do its job: a nested ``devkit`` command exited ``2`` with an error
    of its own, such as rules that cannot load. Not a refusal of the commit's content, so not ``BLOCKED``:
    ``MAINTENANCE``, or ``AUTO`` with the relayed fix when every relayed error is ``AUTO`` with that one fix."""

    code = "GATE_VERIFY_NOT_RUN"
    fix = "Resolve the errors the commands relayed (each has its own [FIX]; the log has the full output), then commit again"


class VerifyUnstagedNotice(GateError):
    """``verify-commands`` ran on a working tree that differs from the commit (``NOTICE``); never raised."""

    code = "GATE_VERIFY_UNSTAGED"
    level = Level.NOTICE
    what_to_report = "The verification ran on files that are not part of this commit; its result may not match it"


class GateTemplateNotice(GateError):
    """The commented settings template could not be written to ``devkit.config`` (a warning, never raised).

    Returned by ``devkit gate install`` and the post-sync refresh; the command itself succeeded, and the hook
    notices it returns (``GATE_HOOK_PRESERVED``) are still reported.
    """

    code = "GATE_CONFIG_TEMPLATE_SKIPPED"
    level = Level.WARNING


class GateLoadError(GateError):
    """A deployed gate package fails to import or to instantiate its gates, or two gates share an ``id``."""

    code = "GATE_LOAD_FAILED"


class GateDefinitionError(GateError):
    """A gate's code is defective: an unusable ``id``, ``stage``, ``order`` or settings declaration,
    or a context property used outside its stage (``MAINTENANCE``)."""

    code = "GATE_DEFINITION_INVALID"


class GateResultError(GateError):
    """A gate built a ``FAILED`` ``GateResult`` or returned something other than a ``GateResult`` or ``None``."""

    code = "GATE_RESULT_INVALID"


class GatePythonError(GateError):
    """``devkit gate install --python`` names an interpreter that cannot import ``devkit.gate``."""

    code = "GATE_PYTHON_INVALID"
    input_error = True
    target_files = ("--python",)
    fix = PYTHON_FIX


class GateInterpreterError(GateError):
    """A hook entry found no interpreter that can import ``devkit.gate``, so the stage's gates did not run.

    Rendered into the ``20-devkit`` entry when it is written: the shell prints it when the interpreter is
    missing, a small bootstrap when the interpreter cannot import ``devkit.gate``. ``MAINTENANCE`` exiting
    ``2`` in a blocking stage; a ``WARNING`` exiting ``0`` in ``post-commit``, after the commit exists.
    """

    code = "GATE_INTERPRETER_UNAVAILABLE"
    fix = (
        "Run `uv sync` in this repository so its .venv provides devkit, or rerun `devkit gate install` "
        "from an environment where devkit is installed"
    )
    what_to_report = "The devkit commit gates did not run: no interpreter can import devkit.gate"


class HooksPathSetError(GateError):
    """``core.hooksPath`` sends Git to another hooks directory, so managed wrappers would not run (``INTERACTION``)."""

    code = "GATE_HOOKS_PATH_SET"
    actor = Actor.USER
    what_to_report = "Another tool owns the hooks directory. Ask whether to unset core.hooksPath."


class ForeignHookError(GateError):
    """``install`` would move symbolic links or non-regular hooks (``INTERACTION``)."""

    code = "GATE_FOREIGN_HOOK"
    actor = Actor.USER
    what_to_report = (
        "Existing hooks would be moved aside; the managed wrapper keeps running them before the gates. "
        "Ask whether to proceed."
    )


class HookBackupExistsError(GateError):
    """``install`` would overwrite a hook an earlier ``install --force`` moved aside (``INTERACTION``)."""

    code = "GATE_BACKUP_EXISTS"
    actor = Actor.USER
    what_to_report = "An earlier backup would be overwritten. Ask the user how to resolve it."


class HookLayoutError(GateError):
    """A reserved script path cannot safely be replaced."""

    code = "GATE_HOOK_LAYOUT_INVALID"
    fix = "Move the conflicting hook paths to another location, then run `devkit sync`"


class HookPreservedNotice(GateError):
    """An existing hook was preserved and chained; returned once when moved."""

    code = "GATE_HOOK_PRESERVED"
    level = Level.WARNING
    what_to_report = (
        "An existing Git hook was renamed and still runs first; check scripts that depend on their filename"
    )


class HookScriptFailedNotice(GateError):
    """A ``post-commit`` hook script exited nonzero (a warning, printed by the dispatcher; never raised).

    Rendered into the dispatcher when it is written; the dispatcher appends the stage, script and exit status.
    """

    code = "GATE_HOOK_SCRIPT_FAILED"
    level = Level.WARNING
    what_to_report = "A post-commit hook script failed after the commit was made; the remaining scripts still ran"


class HookEntryMissingNotice(GateError):
    """Enabled gates of a stage do not run: the stage has no managed dispatcher with a ``20-devkit`` entry.

    Returned by ``devkit gate status`` (a warning, never raised), for example after a gate of a stage that had
    no enabled gate when the hooks were installed is enabled in the configuration.
    """

    code = "GATE_HOOK_ENTRY_MISSING"
    level = Level.WARNING
    fix = "Run `devkit gate install` (or `devkit sync`) to install the hook entry of every stage with enabled gates"
    what_to_report = "Enabled commit gates do not run at commit time until their hook entry is installed"


class HookInstallSkippedNotice(GateError):
    """Automatic hook installation could not safely run; the sync succeeded."""

    code = "GATE_HOOK_INSTALL_SKIPPED"
    level = Level.WARNING
    what_to_report = "Git hook installation was skipped; report the reason and remediation to the user"
