"""Content resources for the ``advisory`` bundle: the Agent Advisory Protocol guides and ``RULE-advisory-unique-code``.

This module imports nothing. The rule under ``bundle/rules/`` is loaded by ``devkit rules`` from the synchronized
copy, never through this package.

The protocol's Python library is the separate ``devkit-advisory`` distribution (``devkit.advisory``), which
registers no bundle, so a runtime environment that installs only the library carries no agent content.
"""
