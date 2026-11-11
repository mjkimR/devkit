"""The document layout and frontmatter vocabulary of delivery documents that the document layer validates.

Proposal bundles live under ``docs/proposals/PROP-<slug>/`` with their ``proposal.md`` and optional
``target-docs.md``; a scaffolded document keeps ``SKELETON_MARKER`` until it is written. A proposal's effort hints
take one of ``EFFORTS``. The delivery process (devkit-spec) builds on these names; it owns what they mean for its
workflow.

The bundle and anchor path grammar of delivery units, on workspace-relative paths written with ``/``:

- a spec bundle is ``specs/<month>/<bundle>/`` (any ``<bundle>`` but ``feedback``, which holds month-level
  feedback), anchored by its ``spec.md``;
- a proposal bundle is ``docs/proposals/PROP-<slug>/``, anchored by its ``proposal.md``; a single-file proposal
  ``docs/proposals/PROP-<slug>.md`` is its own anchor and lies in no bundle.

``bundle_of`` and ``anchor_of`` map a path inside a unit to its bundle directory and anchor; ``is_spec_anchor`` and
``is_proposal_anchor`` accept an anchor at its exact depth only. They read the global roots; a namespace's docs root
``docs/packages/<name>/`` mirrors ``docs/``, and ``unnamespaced`` maps a path under it to the global path it mirrors,
for a caller that also accepts namespaced proposals (``docs/packages/<name>/proposals/PROP-<slug>/proposal.md``).
"""

PROPOSALS = "docs/proposals"
PROPOSAL_FILE = "proposal.md"
PROPOSAL_PREFIX = "PROP-"
TARGET_DOCS = "target-docs.md"
PACKAGES_DIR = "docs/packages"
SPECS = "specs"
SPEC_FILE = "spec.md"
FEEDBACK = "feedback"
# devkit's not-skeleton check: specify stays open until the spec, plan and tasks are written and the line removed.
SKELETON_MARKER = "<!-- devkit:skeleton -->"

EFFORTS = ("low", "medium", "high")
PLANNING_EFFORT = "planning_effort"
DEV_EFFORT = "dev_effort"

_PROPOSAL_PARTS = PROPOSALS.split("/")
_PACKAGES_PARTS = PACKAGES_DIR.split("/")


def unnamespaced(path: str) -> str:
    """``docs/packages/<name>/X`` as the global ``docs/X`` it mirrors, registered namespace or not; any other path
    unchanged."""
    parts = path.split("/")
    if len(parts) < 4 or parts[:2] != _PACKAGES_PARTS:
        return path
    return "/".join(["docs", *parts[3:]])


def bundle_of(path: str) -> str | None:
    """The bundle directory holding ``path``: ``specs/<month>/<bundle>`` or ``docs/proposals/PROP-<slug>``; ``None``
    for a path in no bundle (a single-file proposal, month-level spec feedback, anything else)."""
    parts = path.split("/")
    if len(parts) < 4:
        return None
    if parts[0] == SPECS and parts[2] != FEEDBACK:
        return "/".join(parts[:3])
    if parts[:2] == _PROPOSAL_PARTS and parts[2].startswith(PROPOSAL_PREFIX):
        return "/".join(parts[:3])
    return None


def anchor_of(path: str) -> str | None:
    """The anchor of the unit holding ``path``: its bundle's ``spec.md`` or ``proposal.md``, or ``path`` itself for a
    single-file proposal; ``None`` outside every unit."""
    bundle = bundle_of(path)
    if bundle is not None:
        return f"{bundle}/{SPEC_FILE if bundle.startswith(f'{SPECS}/') else PROPOSAL_FILE}"
    return path if is_proposal_anchor(path) else None


def is_spec_anchor(path: str) -> bool:
    """Whether ``path`` is a spec bundle's anchor, ``specs/<month>/<bundle>/spec.md``."""
    parts = path.split("/")
    return len(parts) == 4 and parts[0] == SPECS and parts[2] != FEEDBACK and parts[3] == SPEC_FILE


def is_proposal_anchor(path: str) -> bool:
    """Whether ``path`` is a proposal anchor: ``docs/proposals/PROP-<slug>/proposal.md`` or a single-file proposal
    ``docs/proposals/PROP-<slug>.md``."""
    parts = path.split("/")
    if len(parts) not in (3, 4) or parts[:2] != _PROPOSAL_PARTS or not parts[2].startswith(PROPOSAL_PREFIX):
        return False
    return parts[2].endswith(".md") if len(parts) == 3 else parts[3] == PROPOSAL_FILE
