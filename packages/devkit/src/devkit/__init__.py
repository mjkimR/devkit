"""devkit: agent asset distribution, repository rules, delivery workflows and commit gates.

Modules (lower layers never import higher ones):

- ``devkit.core``: shared foundation (frontmatter, receipt, paths, Git, plugins, project).
- ``devkit.advisory``: the Agent Advisory Protocol: agent-directed errors, warnings and notices.
- ``devkit.rules``: the repository rule engine (``devkit rules``).
- ``devkit.workflow``: the delivery workflow engine (``devkit workflow``).
- ``devkit.gate``: pluggable Git commit gates (``devkit gate``).
- ``devkit.distribution``: bundle packaging and synchronization (``devkit sync`` and friends).

Importing ``devkit`` has no side effects beyond a ``NullHandler`` on the
``devkit`` logger, so log records never reach Python's last-resort handler on
stderr; ``devkit.cli`` assembles the command line, and ``--verbose`` prints the
records as ``[INFO]`` lines.
"""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
