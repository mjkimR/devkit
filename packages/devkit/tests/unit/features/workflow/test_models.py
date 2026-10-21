"""Workflow model operations consume values without consulting the filesystem."""

from datetime import date
from pathlib import Path, PurePosixPath

import pytest
from devkit_agt.features.workflow.models.definition import parse_definition
from devkit_agt.features.workflow.models.layout import TemplateLayout


def test_definition_parsing_and_layout_calculation_do_not_read_disk(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_io(*args: object, **kwargs: object) -> None:
        pytest.fail("workflow models must not consult the filesystem")

    for operation in ("read_text", "read_bytes", "open", "is_dir", "is_file", "exists", "glob", "resolve"):
        monkeypatch.setattr(Path, operation, unexpected_io)
    path = Path("absent/workflow.md")
    doc = parse_definition("---\nid: delivery\nstages:\n  - id: build\n---\n", path)
    assert doc.id == "delivery" and doc.path == path
    layout = TemplateLayout("specs", "{date:%Y/%m}/{slug}", "spec.md")
    assert layout.new_unit("login", date(2026, 10, 12)) == PurePosixPath("specs/2026/10/login")
    assert layout.discovery_glob() == "*/*/*"
