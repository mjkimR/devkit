"""The two supported global milestone locations and their lifecycle placement."""

import re


def milestone_path_valid(path: str, status: str | None = None) -> bool:
    """Validate layout and, when supplied, lifecycle placement without reading or moving a file."""
    match = re.fullmatch(r"docs/roadmap/(_archive/)?MS-([a-z0-9]+(?:-[a-z0-9]+)*)\.md", path)
    if match is None or re.search(r"[a-z]", match[2].split("-", 1)[0]) is None:
        return False
    if status is None:
        return True
    return status in ({"done", "dropped"} if match[1] else {"planned", "active"})
