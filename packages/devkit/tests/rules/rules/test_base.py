"""``devkit.rules.rules.base``: what every rule shares. Each rule's own tests live in its folder (``<rule>/tests/``)."""

from __future__ import annotations

from devkit.rules.rules import FileLengthRule, guide_path


def test_guide_path_for_classes_without_a_source_file() -> None:
    floating = type("Floating", (FileLengthRule,), {"__module__": "not_loaded_anywhere"})
    assert guide_path(FileLengthRule()) is not None
    assert guide_path(floating()) is None
