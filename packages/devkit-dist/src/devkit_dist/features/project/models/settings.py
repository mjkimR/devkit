"""Configuration grammars every feature shares: the lowercase slug and the ``[playbooks]`` search bounds.

``playbook_value`` is the one check of a ``[playbooks]`` value. The shared configuration, the local overlay and the
``devkit playbook search`` options all apply it; each keeps its own error code and message. A boolean is never a
number here, although Python's ``bool`` is an ``int``.
"""

from __future__ import annotations

import math
import re

# A lowercase slug: bundle, preset, asset, adapter and hook names.
SLUG = re.compile(r"[a-z][a-z0-9-]*\Z")

PLAYBOOK_LIMIT_MIN, PLAYBOOK_LIMIT_MAX = 1, 20
PLAYBOOK_MAX_BYTES_MIN, PLAYBOOK_MAX_BYTES_MAX = 1024, 65536
# The values of ``devkit_dist.features.search.SearchMode``, in its order (a test keeps them equal).
PLAYBOOK_MODES = ("auto", "lexical", "dense", "hybrid")
PLAYBOOK_KEYS = frozenset({"limit", "max_bytes", "min_score", "min_similarity", "mode"})


def _number(value: object) -> float | None:
    """``value`` as a float when it is an ``int`` or ``float`` and not a ``bool``."""
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def playbook_value(key: str, value: object) -> int | float | str | None:
    """``value`` of the ``[playbooks]`` key ``key`` as the search uses it, ``None`` when it is out of bounds.

    ``limit`` and ``max_bytes`` are integers within their bounds; ``min_score`` a finite nonnegative number and
    ``min_similarity`` a number between 0 and 1, both returned as ``float``; ``mode`` one of ``PLAYBOOK_MODES`` in
    any case, returned in lowercase. An unknown key is ``None``.
    """
    if key in ("limit", "max_bytes"):
        low, high = (
            (PLAYBOOK_LIMIT_MIN, PLAYBOOK_LIMIT_MAX)
            if key == "limit"
            else (PLAYBOOK_MAX_BYTES_MIN, PLAYBOOK_MAX_BYTES_MAX)
        )
        return value if type(value) is int and low <= value <= high else None
    if key in ("min_score", "min_similarity"):
        number = _number(value)
        if number is None or not math.isfinite(number) or number < 0 or (key == "min_similarity" and number > 1):
            return None
        return number
    if key == "mode":
        return value.lower() if isinstance(value, str) and value.lower() in PLAYBOOK_MODES else None
    return None
