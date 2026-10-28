"""Shared test fixture type contracts."""

from collections.abc import Callable
from pathlib import Path

Write = Callable[[str, str], Path]
