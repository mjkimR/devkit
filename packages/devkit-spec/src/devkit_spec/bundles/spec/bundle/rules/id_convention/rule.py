"""``RULE-id-convention``, loaded by ``devkit rules`` from this synchronized copy.

The implementation is ``devkit_docs.features.governance.usecases.id_convention`` in the installed devkit-docs package; the class defined
here is what ``devkit rules`` instantiates, and the guide beside this file is what ``devkit rules explain`` prints.
"""

from devkit_docs.features.governance.usecases.id_convention import IdConventionRule as _Implementation


class IdConventionRule(_Implementation):
    """Identifiers are slugs derived from the document's path, never dates or sequence numbers."""
