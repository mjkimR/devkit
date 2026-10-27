"""Every devkit command renders a sentinel field value one way (``ARCH-08-1-agent-output`` section 3)."""

from __future__ import annotations

import pytest
from devkit_dist.adapters.cli import field_value, yes_no


@pytest.mark.parametrize(
    ("value", "rendered"),
    [
        (None, "-"),
        ("", "-"),
        (True, "yes"),
        (False, "no"),
        (0, "0"),
        ("src/a.py", "src/a.py"),
        ("näive", "näive"),
        ("a b", '"a b"'),
        ("a\tb", '"a\\tb"'),
        ("line\nbreak", '"line\\nbreak"'),
        ('say "x"', '"say \\"x\\""'),
        ("a[0]", '"a[0]"'),
        ("a]", '"a]"'),
        ("k=v", '"k=v"'),
        ("C:\\dir", '"C:\\\\dir"'),
    ],
)
def test_a_value_is_bare_only_when_it_stays_one_token(value: object, rendered: str) -> None:
    assert field_value(value) == rendered


def test_yes_no_renders_a_boolean() -> None:
    assert (yes_no(True), yes_no(False)) == ("yes", "no")
