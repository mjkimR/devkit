"""``[tool.docs]`` in devkit's commented config template reads back as ``read_docs_config``'s values."""

from __future__ import annotations

from pathlib import Path

from devkit_dist.features.project.services.config_template import check_tables, render_tool_template, uncomment
from docs_support.types import Write

from devkit_docs.features.documents.models.namespace import Namespace
from devkit_docs.features.documents.repositories.config import DocsConfig, read_docs_config, template


def test_the_template_renders() -> None:
    assert [table.path for table in check_tables(template())] == [("namespaces",)]


def test_an_absent_table_has_no_namespaces(workspace: Path) -> None:
    assert read_docs_config(workspace) == DocsConfig()


def test_uncommented_examples_are_valid(workspace: Path, write: Write) -> None:
    write(".devkit/config.toml", uncomment(render_tool_template("docs", template())))
    assert read_docs_config(workspace).namespaces == (Namespace("api", "services/api"),)
