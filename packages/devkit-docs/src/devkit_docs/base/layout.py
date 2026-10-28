"""The document layout and frontmatter vocabulary of delivery documents that the document layer validates.

Proposal bundles live under ``docs/proposals/PROP-<slug>/`` with their ``proposal.md`` and optional
``target-docs.md``; a scaffolded document keeps ``SKELETON_MARKER`` until it is written. A proposal's effort hints
take one of ``EFFORTS``. The delivery process (devkit-spec) builds on these names; it owns what they mean for its
workflow.
"""

PROPOSALS = "docs/proposals"
PROPOSAL_FILE = "proposal.md"
TARGET_DOCS = "target-docs.md"
# devkit's not-skeleton check: specify stays open until the spec, plan and tasks are written and the line removed.
SKELETON_MARKER = "<!-- devkit:skeleton -->"

EFFORTS = ("low", "medium", "high")
PLANNING_EFFORT = "planning_effort"
DEV_EFFORT = "dev_effort"
