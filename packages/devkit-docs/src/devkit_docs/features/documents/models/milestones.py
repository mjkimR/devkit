"""The two supported global milestone locations and their lifecycle placement."""

import re

from devkit_docs.features.documents.models.ids import word_led


def milestone_path_valid(path: str, status: str | None = None) -> bool:
    """Validate layout and, when supplied, lifecycle placement without reading or moving a file."""
    match = re.fullmatch(r"docs/roadmap/(_archive/)?MS-([a-z0-9]+(?:-[a-z0-9]+)*)\.md", path)
    if match is None or not word_led(match[2]):
        return False
    if status is None:
        return True
    return status in ({"done", "dropped"} if match[1] else {"planned", "active"})
