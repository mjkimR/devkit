"""Shared workspace layout contracts for delivery units: where proposals and spec bundles live and how a slug names
them."""

import re

PROPOSALS = "docs/proposals"
PROPOSAL_FILE = "proposal.md"
TARGET_DOCS = "target-docs.md"
# devkit's not-skeleton check: specify stays open until the spec, plan and tasks are written and the line removed.
SKELETON_MARKER = "<!-- devkit:skeleton -->"

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
