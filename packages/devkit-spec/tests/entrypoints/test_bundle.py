from __future__ import annotations

import pytest

from devkit_spec.entrypoints.bundle import parse_targets
from devkit_spec.errors import EntrypointsInputInvalidError


def test_parse_targets_preserves_order_and_defaults() -> None:
    targets = parse_targets(
        "---\ntargets:\n  - file: docs/b.md\n    resolution: updated\n  - {}\n"
        "  - file: docs/a.md\n    resolution: 3\n---\n",
        "unmaterialized/reconcile.md",
    )
    assert [(target.file, target.resolution) for target in targets] == [
        ("docs/b.md", "updated"),
        ("", ""),
        ("docs/a.md", ""),
    ]


@pytest.mark.parametrize("field", ["other: value", "targets: []", "targets: null", "targets: false"])
def test_parse_targets_preserves_empty_defaults(field: str) -> None:
    assert parse_targets(f"---\n{field}\n---\n", "record.md") == ()


@pytest.mark.parametrize(
    "text",
    [
        "no frontmatter",
        "---\ntargets: [\n---\n",
        "---\ntargets: bad\n---\n",
        "---\ntargets: [bad]\n---\n",
        "---\ntargets: [{file: 3}]\n---\n",
    ],
)
def test_parse_targets_preserves_invalid_input_diagnostics(text: str) -> None:
    with pytest.raises(EntrypointsInputInvalidError) as raised:
        parse_targets(text, "committed/reconcile.md")
    assert raised.value.code == "SPEC_ENTRYPOINTS_INPUT_INVALID"
    assert raised.value.target_files == ("committed/reconcile.md",)
    assert "committed/reconcile.md" in str(raised.value)
