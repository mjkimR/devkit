"""The ``devkit`` logger hierarchy.

``devkit`` is a namespace package shared with the ``devkit-advisory``
distribution, so it has no ``__init__`` that could configure its logger. Every
devkit module takes its logger from ``get_logger``; importing this module adds a
``NullHandler`` to the ``devkit`` logger once, so records never reach Python's
last-resort handler on stderr. ``devkit.core.cli`` attaches the stderr handler
that prints them as ``[INFO]`` lines under ``--verbose``.
"""

from __future__ import annotations

import logging

ROOT = "devkit"

logging.getLogger(ROOT).addHandler(logging.NullHandler())


def get_logger(name: str) -> logging.Logger:
    """The logger of the devkit module ``name`` (its ``__name__``)."""
    return logging.getLogger(name)
