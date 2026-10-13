"""Errors of ``devkit.search``: ``AdvisoryError`` subclasses, one class per code.

Only dense and hybrid search raise them: lexical search needs nothing beyond the
standard library.
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, Retry


class SearchError(AdvisoryError):
    """Base class of every error raised by ``devkit.search``; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class SearchExtraMissingError(SearchError):
    """numpy or tokenizers cannot be imported (``INTERACTION``): the ``agt-devkit[search]`` extra is not installed."""

    code = "SEARCH_EXTRA_MISSING"
    actor = Actor.USER
    fix = "Install the search extra in the project: uv add 'agt-devkit[search] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'"
    what_to_report = (
        "dense and hybrid search need the agt-devkit[search] extra (numpy, tokenizers and the embedding model)"
    )


class ModelNotFoundError(SearchError):
    """No installed package registers the embedding model under the requested name (``INTERACTION``)."""

    code = "SEARCH_MODEL_NOT_FOUND"
    actor = Actor.USER
    fix = "Install the package that provides the model; the default model comes with: uv add 'agt-devkit[search] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'"
    what_to_report = "the embedding model this search needs is not installed"


class ModelInvalidError(SearchError):
    """The model package is installed, but its files are missing or malformed (``MAINTENANCE``)."""

    code = "SEARCH_MODEL_INVALID"
    fix = "Reinstall the model package (uv sync --reinstall-package <package>)"
