"""Shared workspace layout contracts for delivery units: where proposals and spec bundles live and how a slug names
them."""

import posixpath
import re
from pathlib import Path
from typing import Protocol, Self

from devkit_core.base.errors import ArgumentError
from devkit_docs.base.layout import PROPOSAL_FILE, PROPOSALS

from devkit_spec.base.errors import DEVKIT

PROPOSAL_UNIT = re.compile(r"(?:.+/)?docs/proposals/PROP-(?P<slug>[^/]+)")
SPEC_UNIT = re.compile(r"(?:.+/)?specs/\d{4}-\d{2}/\d{8}-(?P<slug>[^/]+)")
SPEC_DIR = re.compile(r"\d{8}-(?P<slug>.+)")


def proposal_unit(slug: str) -> str:
    """The proposal bundle directory of ``slug``: ``docs/proposals/PROP-<slug>``."""
    return f"{PROPOSALS}/PROP-{slug}"


class TreePath(Protocol):
    """A path of the workspace tree or of a pinned Git tree: joined with ``/``, and asked whether it is a directory."""

    def __truediv__(self, value: str, /) -> Self: ...
    def is_dir(self) -> bool: ...


def proposal_anchor[P: TreePath](root: P, slug: str) -> P:
    """The anchor file of proposal ``slug`` under ``root``: ``docs/proposals/PROP-<slug>/proposal.md`` when that
    bundle directory exists, else the single file ``docs/proposals/PROP-<slug>.md``.

    The anchor is not checked for existence: each caller raises its own not-found error. A bundle anchor is named
    ``proposal.md`` (``PROPOSAL_FILE``), a single-file one never is.
    """
    bundle = root / proposal_unit(slug)
    return bundle / PROPOSAL_FILE if bundle.is_dir() else root / f"{proposal_unit(slug)}.md"


def spec_bundle_dir(root: Path, value: str) -> str:
    """The workspace-relative form of ``--spec`` (absolute, or relative to the workspace root); ``ArgumentError``
    when it names no directory inside the workspace. Existence is the caller's check."""
    path = Path(value)
    absolute = path.resolve() if path.is_absolute() else Path(posixpath.normpath((root / path).as_posix()))
    try:
        relative = absolute.relative_to(root).as_posix()
    except ValueError:
        relative = ""
    if not relative or relative == ".":
        raise ArgumentError(
            f"--spec {value}: not a directory inside the workspace",
            target_files=["--spec"],
            fix=f"Pass the spec bundle directory relative to the workspace root ({DEVKIT} docs list spec --history lists them)",
        )
    return relative


def is_spec_dir(name: str, slug: str) -> bool:
    """Whether the directory ``name`` is the spec bundle of ``slug``: exactly ``<YYYYMMDD>-<slug>``.

    ``cleanup`` never claims ``20261001-hook-cleanup``.
    """
    return re.fullmatch(rf"\d{{8}}-{re.escape(slug)}", name) is not None
