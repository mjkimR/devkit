"""``RULE-ux-links``, loaded by ``devkit rules`` from this synchronized copy.

The implementation is ``devkit_spec.features.governance.usecases.ux_links`` in the installed devkit-spec package; the
class defined here is what ``devkit rules`` instantiates, and the guide beside this file is what ``devkit rules
explain`` prints.
"""

from devkit_spec.features.governance.usecases.ux_links import UxLinksRule as _Implementation


class UxLinksRule(_Implementation):
    """UX documents and the use case steps that cite them do not contradict each other."""
