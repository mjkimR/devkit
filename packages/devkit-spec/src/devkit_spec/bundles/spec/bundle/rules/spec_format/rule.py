"""``RULE-spec-format``, loaded by ``devkit rules`` from this synchronized copy.

The implementation is ``devkit_spec.features.governance.usecases.spec_format`` in the installed devkit-spec package; the class defined here
is what ``devkit rules`` instantiates, and the guide beside this file is what ``devkit rules explain`` prints.
"""

from devkit_spec.features.governance.usecases.spec_format import SpecFormatRule as _Implementation


class SpecFormatRule(_Implementation):
    """Capabilities, use cases and proposals carry YAML frontmatter with id, title and status."""
