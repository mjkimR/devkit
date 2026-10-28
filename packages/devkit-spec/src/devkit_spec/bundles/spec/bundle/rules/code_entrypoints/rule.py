"""``RULE-code-entrypoints``, loaded by ``devkit rules`` from this synchronized copy.

The implementation is ``devkit_docs.features.governance.usecases.code_entrypoints`` in the installed devkit-docs package; the class
defined here is what ``devkit rules`` instantiates, and the guide beside this file is what ``devkit rules explain``
prints.
"""

from devkit_docs.features.governance.usecases.code_entrypoints import CodeEntrypointsRule as _Implementation


class CodeEntrypointsRule(_Implementation):
    """Every entrypoints path of a capability or use case exists in the workspace."""
