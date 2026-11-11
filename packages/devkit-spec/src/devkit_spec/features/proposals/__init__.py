"""devkit_spec.features.proposals: proposals and the spec bundles they become.

``CreateProposalUseCase`` scaffolds ``docs/proposals/PROP-<slug>/`` (bound to workflow ``sdd-proposal`` when the project
has it), ``CreateProposalDecisionUseCase`` (``usecases.scaffold``) a preliminary decision inside it, ``AcceptProposalUseCase`` records the user's acceptance (also a
direct acceptance of an eligible draft), and ``handoff_proposal`` turns an approved proposal into
``specs/<YYYY-MM>/<YYYYMMDD>-<slug>/``, promoting PADRs to ADRs, moving materials and rewriting what pointed into
the proposal. ``create_spec`` creates a spec bundle without a proposal. Contracts: ``CAP-DLV-proposal-planning`` and ``CAP-DLV-spec-bundles`` (``docs/capabilities/delivery/``).
"""

from devkit_docs.base.layout import EFFORTS

from devkit_spec.base.axes import PROPOSAL_WORKFLOW, TASK_KINDS
from devkit_spec.features.proposals.services.body import carry_proposal_body, ensure_ac_ids
from devkit_spec.features.proposals.services.rewrite import Rewritten, Unresolved
from devkit_spec.features.proposals.usecases.accept import AcceptProposalUseCase
from devkit_spec.features.proposals.usecases.handoff import (
    TASK_KIND,
    CarriedGate,
    HandoffResult,
    SupersessionPointer,
    handoff_proposal,
)
from devkit_spec.features.proposals.usecases.prune import PruneProposalsUseCase
from devkit_spec.features.proposals.usecases.scaffold import (
    TARGET_DOCS,
    CreatedProposal,
    CreateProposalUseCase,
    clean_slug,
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
    "AcceptProposalUseCase",
    "CarriedGate",
    "CreateProposalUseCase",
    "CreatedProposal",
    "CreatedSpec",
    "HandoffResult",
    "PruneProposalsUseCase",
    "Rewritten",
    "SupersessionPointer",
    "Unresolved",
    "carry_proposal_body",
    "clean_slug",
    "create_spec",
    "ensure_ac_ids",
    "handoff_proposal",
    "mark_skeleton",
    "spec_files",
]
