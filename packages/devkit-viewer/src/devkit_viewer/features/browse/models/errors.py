"""Errors of devkit-viewer.

``ViewerError`` subclasses are ``AdvisoryError``s with ``VIEWER_`` codes: refusals of ``devkit viewer serve``
before it serves, rendered by the CLI boundary. ``ReadError`` is what one HTTP request answers: a status and a
stable code in a JSON body; it never reaches the command line.
"""

from __future__ import annotations

from devkit.advisory import Actor, AdvisoryError, Retry


class ViewerError(AdvisoryError):
    """Base class of every devkit-viewer refusal; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class RepoDuplicateError(ViewerError):
    """Two registered repositories have the same directory name, which is their ID (``INPUT_ERROR``)."""

    code = "VIEWER_REPO_DUPLICATE"
    input_error = True
    fix = "Register only one of the repositories named in [TARGET], or serve them from separate commands"


class RepoInvalidError(ViewerError):
    """A ``--repo`` path is not the top level of a Git work tree (``INPUT_ERROR``)."""

    code = "VIEWER_REPO_INVALID"
    input_error = True
    fix = "Pass the top-level directory of a Git work tree to --repo"


class NoRepositoryError(ViewerError):
    """Nothing to serve: no ``--repo``, no eligible ``--scan`` child, and no devkit project here (``INPUT_ERROR``)."""

    code = "VIEWER_NO_REPOSITORY"
    input_error = True
    fix = "Pass --repo <git work tree>, --scan <directory of devkit repositories>, or run from inside a devkit project"


class PortInUseError(ViewerError):
    """The port is already bound on 127.0.0.1 (``INPUT_ERROR``)."""

    code = "VIEWER_PORT_IN_USE"
    input_error = True
    fix = "Pass another --port, or --port 0 for any free port"


class ReadError(Exception):
    """One HTTP request's failure: the ``status`` and ``code`` its JSON body carries."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def repo_unknown(repo_id: str) -> ReadError:
    return ReadError(404, "VIEWER_REPO_UNKNOWN", f"no registered repository has the ID {repo_id!r}")


def path_not_found(path: str, kind: str) -> ReadError:
    return ReadError(404, "VIEWER_PATH_NOT_FOUND", f"no {kind} at {path!r} in this working tree")


def path_invalid(path: str) -> ReadError:
    return ReadError(400, "VIEWER_PATH_INVALID", f"{path!r} is not a repository-relative path")


def source_unknown(source: str) -> ReadError:
    return ReadError(404, "VIEWER_SOURCE_UNKNOWN", f"no Planning source {source!r} in this repository")


def source_path_refused(path: str, source: str) -> ReadError:
    return ReadError(
        400, "VIEWER_SOURCE_PATH_REFUSED", f"{path!r} is outside the proposal directory of the source {source!r}"
    )
