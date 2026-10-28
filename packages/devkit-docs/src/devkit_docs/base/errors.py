"""Errors, warnings and notices of devkit-docs: ``AdvisoryError`` subclasses with ``DOCS_`` codes.

Each class carries the code and the Agent Advisory Protocol fields that fit
its condition, so a caller branches on ``error.code`` and the CLI boundary
renders the error as it is. devkit's own errors (``ARGUMENT_INVALID``,
``CONFIG_INVALID``, ``FRONTMATTER_INVALID``, ...) pass through unchanged.
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, Level, Retry
from devkit_dist.base.errors import ConfigError

DEVKIT = "uv run devkit"
"""How every command an advisory or sentinel of devkit-docs names is run: devkit_dist's ``AGENT_INVOCATION``
(``ADR-keep-uv-run-as-the-agent-facing-devkit-invocation``). The package base may not import a feature module of
devkit_dist, so it is repeated here; a test keeps both equal."""


class DocsError(AdvisoryError):
    """Base class of every devkit-docs error; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class DocumentInvalidWarning(DocsError):
    """A file under ``docs/`` or ``specs/`` could not be read as a document and was left out (``WARNING``)."""

    code = "DOCS_DOCUMENT_INVALID"
    level = Level.WARNING
    fix = "Correct the file's frontmatter (devkit's frontmatter grammar; id, reconcile_id and status are strings)"


class UnresolvedIdError(DocsError):
    """A document ID given to a command names no document (``INPUT_ERROR``)."""

    code = "DOCS_ID_UNRESOLVED"
    input_error = True
    fix = f"Pass the exact ID of an existing document ({DEVKIT} docs list shows them)"


class DuplicateIdError(DocsError):
    """More than one document declares the ID (``MAINTENANCE``); references to it are ambiguous."""

    code = "DOCS_ID_DUPLICATE"
    fix = "Give each document its own ID: the ID follows the document's path (RULE-id-convention)"


class DocsConfigError(DocsError, ConfigError):
    """The ``[tool.docs]`` table of ``.devkit/config.toml`` is malformed (``INPUT_ERROR``)."""

    code = "DOCS_CONFIG_INVALID"
    target_files = (".devkit/config.toml",)
    fix = "Correct the value the message names in the [tool.docs] table of .devkit/config.toml, then rerun"


class GlossaryInvalidError(DocsError):
    """``docs/steering/glossary.yaml`` cannot be read or does not hold ``terms: [{primary, synonyms}]``
    (``INPUT_ERROR``)."""

    code = "DOCS_GLOSSARY_INVALID"
    input_error = True
    target_files = ("docs/steering/glossary.yaml",)
    fix = (
        "Correct docs/steering/glossary.yaml: terms is a list of mappings, each with a primary string and an optional "
        "synonyms list of strings"
    )


class ListStatusUnknownNotice(DocsError):
    """``devkit docs list --status``: a requested status occurs on no indexed document of the selected kinds
    (``NOTICE``); the filter still applies, since a valid status may simply be unused so far."""

    code = "DOCS_LIST_STATUS_UNKNOWN"
    level = Level.NOTICE
    fix = f"Pass a status the documents of the selected kinds carry ({DEVKIT} docs list shows them)"


class OverlayFailedWarning(DocsError):
    """A ``devkit.docs.status_overlay`` extension failed to load, raised or returned something other than
    ``{document ID: {field: text}}`` with no field ``list`` already shows (``WARNING``); its display is left out."""

    code = "DOCS_OVERLAY_FAILED"
    level = Level.WARNING
    fix = "Fix or uninstall the package that registers the named devkit.docs.status_overlay extension"


class EntrypointsPathError(DocsError):
    """An entrypoint path is not a literal workspace-relative path: empty, absolute, with a ``..`` segment, a glob,
    a backslash, a drive colon or a control character (``INPUT_ERROR``)."""

    code = "DOCS_ENTRYPOINTS_PATH_INVALID"
    input_error = True
    fix = "Pass a literal workspace-relative file or directory path (no glob, no leading /, no .. segment)"
