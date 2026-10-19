"""Errors raised by ``devkit.core``: ``AdvisoryError`` subclasses with stable codes.

Each class carries the code and the Agent Advisory Protocol fields that fit
its condition, so a caller can branch on ``error.code`` and a CLI boundary
renders the error as it is. A caller that knows more (the command that
repairs the file, the flag that named the path) re-raises with its own fields.
"""

from __future__ import annotations

from typing import Unpack

from devkit.advisory import Actor, AdvisoryError, AdvisoryFields, Retry

# The source-explicit requirements of the two devkit wheels: no package index hosts them, so a directive never names
# a bare package that the default index would resolve to something else.
REPOSITORY_URL = "git+https://github.com/mjkimR/devkit.git"
DIST_REQUIREMENT = f"devkit-dist @ {REPOSITORY_URL}#subdirectory=packages/devkit-dist"
AGT_REQUIREMENT = f"devkit-agt @ {REPOSITORY_URL}#subdirectory=packages/devkit"
# The one directive that adds the devkit-agt harness to an installation, whatever its form (devkit-dist never detects
# it): shared by ``HARNESS_COMMAND_UNAVAILABLE`` and the ``HARNESS_ENGINE_MISSING`` notice of ``devkit.distribution``.
HARNESS_INSTALL_FIX = (
    f"Add devkit-agt to the installation. In a project, replace the devkit-dist requirement with '{AGT_REQUIREMENT}'"
    " in the same dependency group (devkit-agt depends on devkit-dist at the same version; never declare both);"
    f" for a tool installation, run: uv tool install --reinstall '{DIST_REQUIREMENT}' --with '{AGT_REQUIREMENT}'"
)


def extra_install_fix(extra: str) -> str:
    """The directive that installs a devkit extra on the devkit requirement the project already declares.

    It names both forms instead of detecting the installation, and never a second requirement next to the first.
    """
    agt = AGT_REQUIREMENT.replace("devkit-agt", f"devkit-agt[{extra}]", 1)
    dist = DIST_REQUIREMENT.replace("devkit-dist", f"devkit-dist[{extra}]", 1)
    return (
        f"Add the {extra} extra to the devkit requirement the project declares: uv add '{agt}' when it depends on"
        f" devkit-agt, else uv add '{dist}'"
    )


class DevkitCoreError(AdvisoryError):
    """Base class of every error raised by ``devkit.core``."""


class FrontmatterError(DevkitCoreError):
    """A document opens a YAML frontmatter block that cannot be used."""

    code = "FRONTMATTER_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class ReceiptError(DevkitCoreError):
    """``.devkit/installation.json`` exists but is unreadable or does not match its schema."""

    code = "RECEIPT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    target_files = (".devkit/installation.json",)
    fix = "Restore .devkit/installation.json from version control (git checkout -- .devkit/installation.json), then run `devkit sync`"


class ConfigError(DevkitCoreError):
    """A TOML configuration file exists but cannot be read or parsed (``CONFIG_INVALID``).

    The base of every configuration error: an area whose own table is malformed
    raises a subclass with its own code (``RULES_CONFIG_INVALID``,
    ``WORKFLOW_CONFIG_INVALID``, ``GATE_CONFIG_INVALID``).
    """

    code = "CONFIG_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True
    target_files = (".devkit/config.toml",)


class ArgumentError(DevkitCoreError):
    """A command argument or library parameter is malformed or names something that does not exist.

    Command lines raise it for every semantic argument check (click only parses
    syntax), so a JSON caller still receives one ``{"error": ...}`` document.
    """

    code = "ARGUMENT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class DevkitRootNestedError(DevkitCoreError):
    """A ``.devkit/`` directory sits below the top level of a Git work tree whose top level has none.

    Inside a Git work tree the repository's top level is the devkit root, so such a ``.devkit/`` belongs to no
    project: resolving to the top level would read no configuration, receipt or managed rules (and a check would
    pass vacuously). The message names both directories.
    """

    code = "DEVKIT_ROOT_NESTED"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class CommandPluginError(DevkitCoreError):
    """An installed package's ``devkit.commands`` entry point cannot be used (``MAINTENANCE``).

    Its module fails to import, its target is not a click command, or two
    packages declare the same command name. Only that command fails.
    """

    code = "COMMAND_PLUGIN_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    fix = "Reinstall or upgrade the package that declares the command (uv sync), or remove the duplicate"


class HarnessCommandUnavailableError(DevkitCoreError):
    """A harness command name (``devkit rules``, ``devkit run``, ...) in an installation without ``devkit-agt``.

    ``devkit-dist`` knows the names ``devkit-agt`` mounts, never their modules, and answers one only when no installed
    command has it (``INTERACTION``: adding a package is the user's decision).
    """

    code = "HARNESS_COMMAND_UNAVAILABLE"
    actor = Actor.USER
    retry = Retry.AFTER_FIX
    fix = HARNESS_INSTALL_FIX


class UnsafePathError(DevkitCoreError):
    """A workspace-relative path is absolute, escapes its root, or is otherwise unusable."""

    code = "PATH_UNSAFE"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


class AssetFileError(DevkitCoreError):
    """A file the receipt lists for a synchronized asset is missing, unsafe, or differs from its recorded hash."""

    code = "ASSET_FILE_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    fix = "Run `devkit sync`"


class GitError(DevkitCoreError):
    """A Git command could not run, timed out, or exited with a nonzero status.

    ``returncode`` is ``None`` when Git never produced an exit status (not
    installed, not executable, or timed out). ``stderr`` is Git's decoded
    diagnostic output, possibly empty.
    """

    code = "GIT_FAILED"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX

    def __init__(
        self,
        message: str,
        *details: object,
        command: tuple[str, ...] = (),
        returncode: int | None = None,
        stderr: str = "",
        **fields: Unpack[AdvisoryFields],
    ) -> None:
        super().__init__(message, *details, **fields)
        self.command = command
        self.returncode = returncode
        self.stderr = stderr


class DeadlineExceededError(DevkitCoreError):
    """An operation bounded by a ``Deadline`` ran out of time (``DEFER``): something else kept it busy.

    ``what`` names the step that ran out (``git fetch``, ``waiting for the lock on <path>``) and
    ``seconds`` the deadline's length. A caller with a code of its own catches it and re-raises, or gives
    its ``Deadline`` an ``error`` factory so the deadline raises the caller's error directly.
    """

    code = "DEADLINE_EXCEEDED"
    actor = Actor.NONE
    retry = Retry.SAFE

    def __init__(
        self,
        message: str,
        *details: object,
        what: str = "",
        seconds: float = 0.0,
        **fields: Unpack[AdvisoryFields],
    ) -> None:
        super().__init__(message, *details, **fields)
        self.what = what
        self.seconds = seconds


class LockHeldError(DeadlineExceededError):
    """Another process held a file lock past the wait the caller allowed (``DEFER``); ``seconds`` is that wait."""

    code = "LOCK_HELD"


class LockUnsupportedError(DevkitCoreError):
    """The platform has no ``fcntl.flock``, which every devkit file lock uses (``BLOCKED``)."""

    code = "LOCK_UNSUPPORTED"
    guardrail = True
    fix = "Run the command on Linux or macOS"
