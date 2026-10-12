"""devkit: agent asset distribution, repository rules, delivery workflows and commit gates.

Modules (lower layers never import higher ones):

- ``devkit.core``: shared foundation (frontmatter, receipt, paths, Git, plugins, project).
- ``devkit.advisory``: the Agent Advisory Protocol for agent-directed errors.
- ``devkit.rules``: the repository rule engine (``devkit rules``).
- ``devkit.workflow``: the delivery workflow engine (``devkit workflow``).
- ``devkit.gate``: pluggable Git commit gates (``devkit gate``).
- ``devkit.distribution``: bundle packaging and synchronization (``devkit sync`` and friends).

Importing ``devkit`` has no side effects; ``devkit.cli`` assembles the command line.
"""
