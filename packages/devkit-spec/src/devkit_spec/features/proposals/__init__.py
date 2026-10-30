"""devkit_spec.features.proposals: proposals and the spec bundles they become.

``create_proposal`` scaffolds ``docs/proposals/PROP-<slug>/`` (bound to workflow ``sdd-proposal`` when the project
has it), ``CreateProposalDecisionUseCase`` (``usecases.scaffold``) a preliminary decision inside it, ``accept_proposal`` records the user's acceptance (also a
direct acceptance of an eligible draft), and ``handoff_proposal`` turns an approved proposal into
``specs/<YYYY-MM>/<YYYYMMDD>-<slug>/``, promoting PADRs to ADRs, moving materials and rewriting what pointed into
the proposal. ``create_spec`` creates a spec bundle without a proposal. Contracts: ``CAP-DLV-proposal-planning`` and ``CAP-DLV-spec-bundles`` (``docs/capabilities/delivery/``).
"""

from devkit_spec.base.axes import (
    EFFORTS,
    PROPOSAL_WORKFLOW,
    TASK_KINDS,
)
from devkit_spec.features.proposals.services.body import carry_proposal_body, ensure_ac_ids
from devkit_spec.features.proposals.services.rewrite import Rewritten, Unresolved
from devkit_spec.features.proposals.usecases.accept import accept_proposal
from devkit_spec.features.proposals.usecases.handoff import (
    TASK_KIND,
    CarriedGate,
    HandoffResult,
    handoff_proposal,
)
from devkit_spec.features.proposals.usecases.prune import prune_proposals
from devkit_spec.features.proposals.usecases.scaffold import (
    TARGET_DOCS,
    CreatedProposal,
    clean_slug,
    create_proposal,
)
from devkit_spec.features.proposals.usecases.specs import (
    SKELETON_MARKER,
    CreatedSpec,
    create_spec,
    mark_skeleton,
    spec_files,
)

__all__ = [
    "EFFORTS",
    "PROPOSAL_WORKFLOW",
    "SKELETON_MARKER",
    "TARGET_DOCS",
    "TASK_KIND",
    "TASK_KINDS",
    "CarriedGate",
    "CreatedProposal",
    "CreatedSpec",
    "HandoffResult",
    "Rewritten",
    "Unresolved",
    "accept_proposal",
    "carry_proposal_body",
    "clean_slug",
    "create_proposal",
    "create_spec",
    "ensure_ac_ids",
    "handoff_proposal",
    "mark_skeleton",
    "prune_proposals",
    "spec_files",
]
