from __future__ import annotations

from datetime import date
from pathlib import Path, PurePosixPath

import pytest
from devkit.advisory import ActionMode
from devkit.workflow import ConfigError, LayoutError, TemplateLayout, load_workflow_config, validate_template
from devkit.workflow.config import parse_workflow_config
from testsupport.workflow import write_config, write_unit

# --- template validation ------------------------------------------------------


@pytest.mark.parametrize("template", ["{slug}", "{date:%Y-%m}/{date:%Y%m%d}-{slug}", "units/{slug}"])
def test_valid_templates(template: str) -> None:
    assert any(name == "slug" for name, _ in validate_template(template))


@pytest.mark.parametrize(
    ("template", "match"),
    [
        ("", "empty"),
        ("/abs/{slug}", "relative"),
        ("../{slug}", "relative"),
        ("{date:%Y}", "must contain {slug}"),
        ("{ticket}-{slug}", "unknown placeholder"),
        ("{slug:>10}", "takes no format spec"),
        ("{slug!r}", "conversion"),
        ("{slug", "invalid format syntax"),
    ],
)
def test_invalid_templates(template: str, match: str) -> None:
    with pytest.raises(LayoutError, match=match) as info:
        validate_template(template)
    assert info.value.code == "LAYOUT_INVALID" and info.value.mode is ActionMode.INPUT_ERROR


# --- layout -----------------------------------------------------------------------


def test_new_unit_renders_specrig_style_layout() -> None:
    layout = TemplateLayout("specs", "{date:%Y-%m}/{date:%Y%m%d}-{slug}", "spec.md")
    assert layout.new_unit("login-flow", date(2026, 10, 12)) == PurePosixPath("specs/2026-10/20261012-login-flow")


def test_new_unit_rejects_bad_slug() -> None:
    layout = TemplateLayout("work", "{slug}", "task.md")
    with pytest.raises(LayoutError, match="slug"):
        layout.new_unit("Bad Slug", date(2026, 10, 12))


def test_discovery_glob_and_anchor_filter(tmp_path: Path) -> None:
    layout = TemplateLayout("specs", "{date:%Y-%m}/{date:%Y%m%d}-{slug}", "spec.md")
    assert layout.discovery_glob() == "*/*-*"
    write_unit(tmp_path, "specs/2026-10/20261012-a", anchor="spec.md")
    write_unit(tmp_path, "specs/2026-10/20261011-b", anchor="spec.md")
    (tmp_path / "specs/2026-10/20261013-no-anchor").mkdir()
    (tmp_path / "specs/2026-10/stray.md").write_text("x")
    found = layout.discover(tmp_path)
    assert found == [PurePosixPath("specs/2026-10/20261011-b"), PurePosixPath("specs/2026-10/20261012-a")]


def test_discover_missing_work_dir_is_empty(tmp_path: Path) -> None:
    assert TemplateLayout("nope", "{slug}", "task.md").discover(tmp_path) == []


# --- config -----------------------------------------------------------------------


def test_defaults_without_config(tmp_path: Path) -> None:
    cfg = load_workflow_config(tmp_path)
    assert (cfg.work_dir, cfg.unit_path, cfg.anchor, cfg.definitions_dir, cfg.default) == (
        ".devkit/transient/work",
        "{slug}",
        "task.md",
        ".devkit/workflows",
        None,
    )
    assert cfg.policy("anything") == "ask"


def test_config_reads_workflow_table(tmp_path: Path) -> None:
    write_config(
        tmp_path,
        """schema = 1
[workflow]
work_dir = "specs"
unit_path = "{date:%Y-%m}/{date:%Y%m%d}-{slug}"
anchor = "spec.md"
definitions_dir = "workflows"
default = "direct-delivery"

[workflow.approvals]
direction = "auto"
integration = "ask"
feedback = "off"
""",
    )
    cfg = load_workflow_config(tmp_path)
    assert cfg.work_dir == "specs" and cfg.anchor == "spec.md" and cfg.default == "direct-delivery"
    assert cfg.approvals == {"direction": "auto", "feedback": "off", "integration": "ask"}
    assert cfg.policy("direction") == "auto" and cfg.policy("unknown") == "ask"


@pytest.mark.parametrize(
    ("body", "match"),
    [
        ("[workflow]\nbogus = 1\n", "unknown fields"),
        ("workflow = 1\n", "expected a table"),
        ('[workflow]\nwork_dir = "/abs"\n', "workspace-relative"),
        ('[workflow]\nunit_path = "{ticket}"\n', "unknown placeholder"),
        ('[workflow]\nanchor = "dir/task.md"\n', "bare file name"),
        ('[workflow]\ndefault = ""\n', "workflow id"),
        ('[workflow.approvals]\nintegration = "maybe"\n', "not one of"),
        ('[workflow.approvals]\n"Bad Gate" = "ask"\n', "gate names"),
        ("invalid [[\n", "invalid config"),
    ],
)
def test_invalid_config(tmp_path: Path, body: str, match: str) -> None:
    write_config(tmp_path, body)
    with pytest.raises(ConfigError, match=match):
        load_workflow_config(tmp_path)


def test_parse_rejects_non_table() -> None:
    with pytest.raises(ConfigError):
        parse_workflow_config([])
