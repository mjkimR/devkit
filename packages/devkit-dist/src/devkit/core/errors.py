"""Errors raised by ``devkit.core``: ``AdvisoryError`` subclasses with stable codes.

Each class carries the code and the Agent Advisory Protocol fields that fit
its condition, so a caller can branch on ``error.code`` and a CLI boundary
renders the error as it is. A caller that knows more (the command that
repairs the file, the flag that named the path) re-raises with its own fields.
"""

from __future__ import annotations

from devkit_core.base.errors import DevkitCoreError

from devkit.advisory import Actor, Retry

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


class AssetFileError(DevkitCoreError):
    """A file the receipt lists for a synchronized asset is missing, unsafe, or differs from its recorded hash."""

    code = "ASSET_FILE_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    fix = "Run `devkit sync`"
