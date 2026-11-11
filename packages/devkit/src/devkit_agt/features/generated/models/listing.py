"""How many paths an advisory lists, and the detail that counts the rest."""

LISTED = 20  # paths listed in an advisory's details


def unlisted(total: int) -> list[str]:
    """The ``... and <N> more`` detail closing a list of ``total`` items cut to ``LISTED``; ``[]`` when none was cut."""
    return [f"... and {total - LISTED} more"] if total > LISTED else []
