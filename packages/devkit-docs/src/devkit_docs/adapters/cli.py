"""The ``devkit docs`` command line prefix its ``[NEXT_CMD: ...]`` and ``[HISTORY_CMD: ...]`` lines repeat.

The sentinel lines themselves are devkit's (``devkit_dist.adapters.cli``: ``sentinel``, ``fields_line``,
``echo_page``), rendered with its one field renderer (``ARCH-08-1-agent-output`` section 3).
"""

from __future__ import annotations

from devkit_docs.base.errors import DEVKIT

COMMAND = f"{DEVKIT} docs"
