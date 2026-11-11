"""The ``devkit spec`` command prefix shared by the spec command modules.

The sentinel lines come from ``devkit_dist.adapters.cli`` (``sentinel``, ``fields_line`` and ``echo_page``, on
devkit's one field renderer; ``ARCH-08-1-agent-output`` section 3).
"""

from __future__ import annotations

from devkit_spec.base.errors import DEVKIT

COMMAND = f"{DEVKIT} spec"
