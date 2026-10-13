"""``RULE-file-length``: files stay under a line budget (hygiene). Code in ``rule.py``, guide in ``guide.md``."""

from __future__ import annotations

from devkit.rules.rules.file_length.rule import FileLengthRule, FileLengthSettings

__all__ = ["FileLengthRule", "FileLengthSettings"]
