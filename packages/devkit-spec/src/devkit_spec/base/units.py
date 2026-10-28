"""Shared workspace layout contracts for delivery units: where proposals and spec bundles live and how a slug names
them."""

import re

# The layout names the document layer validates; delivery modules read them from here.
from devkit_docs.base.layout import PROPOSAL_FILE as PROPOSAL_FILE
from devkit_docs.base.layout import PROPOSALS as PROPOSALS
from devkit_docs.base.layout import SKELETON_MARKER as SKELETON_MARKER
from devkit_docs.base.layout import TARGET_DOCS as TARGET_DOCS

PROPOSAL_UNIT = re.compile(r"(?:.+/)?docs/proposals/PROP-(?P<slug>[^/]+)")
SPEC_UNIT = re.compile(r"(?:.+/)?specs/\d{4}-\d{2}/\d{8}-(?P<slug>[^/]+)")
SPEC_DIR = re.compile(r"\d{8}-(?P<slug>.+)")


def proposal_unit(slug: str) -> str:
    """The proposal bundle directory of ``slug``: ``docs/proposals/PROP-<slug>``."""
    return f"{PROPOSALS}/PROP-{slug}"


def is_spec_dir(name: str, slug: str) -> bool:
    """Whether the directory ``name`` is the spec bundle of ``slug``: exactly ``<YYYYMMDD>-<slug>``.

    ``cleanup`` never claims ``20261001-hook-cleanup``.
    """
    return re.fullmatch(rf"\d{{8}}-{re.escape(slug)}", name) is not None
