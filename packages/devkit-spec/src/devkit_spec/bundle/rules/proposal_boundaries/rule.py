"""``RULE-proposal-boundaries``, loaded by ``devkit rules`` from this synchronized copy.

The implementation is ``devkit_spec.rules.proposal_boundaries`` in the installed devkit-spec package; the class
defined here is what ``devkit rules`` instantiates, and the guide beside this file is what ``devkit rules explain``
prints.
"""

from devkit_spec.rules.proposal_boundaries import ProposalBoundariesRule as _Implementation


class ProposalBoundariesRule(_Implementation):
    """A proposal's target_area and boundaries.owns entries name existing paths."""
