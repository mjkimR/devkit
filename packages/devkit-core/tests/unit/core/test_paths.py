"""``devkit_core.core.paths.display_path``: a path as a message shows it."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_core.core import display_path


@pytest.mark.parametrize(
    ("path", "root", "expected"),
    [
        (Path("/work/a/b.md"), Path("/work"), "a/b.md"),
        (Path("/work"), Path("/work"), "."),
        (Path("/elsewhere/b.md"), Path("/work"), "/elsewhere/b.md"),
        (Path("/work2/b.md"), Path("/work"), "/work2/b.md"),
        (Path("/link/b.md"), Path("/work"), "/link/b.md"),  # lexical: a symlink to /work is never resolved
        (Path("rel/b.md"), None, "rel/b.md"),
        (Path("/work/b.md"), None, "/work/b.md"),
    ],
)
def test_display_path(path: Path, root: Path | None, expected: str) -> None:
    assert display_path(path, root) == expected


def test_display_path_of_no_path() -> None:
    assert display_path(None, Path("/work")) is None
