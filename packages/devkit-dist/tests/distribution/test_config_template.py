"""The commented template in ``.devkit/config.toml``: devkit's keys, the tables engines register for the reserved
top-level names (``devkit.config_tables``) and the ``[tool.<name>]`` tables of installed tools.

The engine templates here are stand-ins registered by the test; devkit-agt's real ``workflow`` and ``worktree``
templates are tested with devkit-agt (``packages/devkit/tests/test_config_tables.py``)."""

from __future__ import annotations

import json
import tomllib
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from devkit.core import TemplateKey, TemplateTable
from devkit.core.config_template import uncomment
from devkit.core.receipt import CONFIG_PATH
from devkit.distribution.installation import config_template
from devkit.distribution.installation.config import (
    TEMPLATE_HEADER,
    ProjectConfig,
    prepare_config_update,
    preview_config_template,
    read_config,
    refresh_config_template,
    update_config,
)
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.sync import sync_project
from distsupport.distribution import cli, make_bundle

COMMON_TABLES = ["workflow.approvals", "workflow.stages", "worktree", "shared"]
DEVKIT_PARTS = ["agents", "guidance_block", "override_drift", *COMMON_TABLES]

# Stand-ins for the templates an engine package registers for reserved tables, in entry-point name order.
RESERVED = {
    "workflow": [
        TemplateTable(
            (TemplateKey("integration", "ask", "approve integrating the change", kind='"ask" | "auto" | "off"'),),
            path=("approvals",),
            help="Workflow approval gates: an example gate.",
        ),
        TemplateTable(
            (TemplateKey("collect-feedback", "on", "set off to skip it", kind='"on" | "off"'),),
            path=("stages",),
            help="Workflow stages: an example stage.",
        ),
    ],
    "worktree": [
        TemplateTable(
            (
                TemplateKey("pull_request", "auto", "integration policy", kind='"auto" | "required"'),
                TemplateKey("setup", help="setup command; unset: none", example="uv sync"),
            ),
            help="Git worktree behavior: an example table.",
        )
    ],
}

DEMO = [
    TemplateTable((TemplateKey("enabled", True, "turn demo on"),)),
    TemplateTable((TemplateKey("timeout", 10, "seconds per call"),), path=("limits",), help="Limits."),
]


def _entry(name: str, extension: Callable[[], object], package: str | None = "demo-tool") -> SimpleNamespace:
    """A ``devkit.config_template`` entry point whose ``load()`` returns ``extension``."""
    return SimpleNamespace(
        name=name, value=f"pkg:{name}", load=lambda: extension, dist=SimpleNamespace(name=package) if package else None
    )


@pytest.fixture
def reserved() -> list[SimpleNamespace]:
    """The ``devkit.config_tables`` entry points the test registers: the ``RESERVED`` stand-ins, as with an engine."""
    return [_entry(name, (lambda tables=tables: tables), package="engine-pkg") for name, tables in RESERVED.items()]


@pytest.fixture
def tools(monkeypatch: pytest.MonkeyPatch, reserved: list[SimpleNamespace]) -> list[SimpleNamespace]:
    """The ``devkit.config_template`` entry points the test registers; none unless it appends one."""
    entries: list[SimpleNamespace] = []
    groups = {config_template.GROUP: entries, config_template.RESERVED_GROUP: reserved}
    monkeypatch.setattr(config_template.metadata, "entry_points", lambda group: list(groups.get(group, [])))
    return entries


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / ".devkit").mkdir(parents=True)
    return root


def _write(root: Path, text: str) -> None:
    (root / CONFIG_PATH).write_text(text)


def _text(root: Path) -> str:
    return (root / CONFIG_PATH).read_text()


def test_creates_the_file_with_devkit_keys_at_their_defaults(tmp_path: Path, tools: list[SimpleNamespace]) -> None:
    result = refresh_config_template(tmp_path)
    assert result.to_dict() == {
        "path": CONFIG_PATH,
        "state": "created",
        "added": DEVKIT_PARTS,
        "notices": [],
    }
    text = _text(tmp_path)
    assert text.startswith(f"schema = 1\n\n## {TEMPLATE_HEADER.split()[0]} ")
    assert read_config(tmp_path) == ProjectConfig()
    uncommented = tmp_path / "uncommented"
    (uncommented / ".devkit").mkdir(parents=True)
    _write(uncommented, uncomment(text))
    assert tomllib.loads(uncomment(text)) == {
        "schema": 1,
        "agents": ["antigravity", "claude-code", "codex"],
        "guidance_block": True,
        "override_drift": "warn",
        "workflow": {
            "approvals": {"integration": "ask"},
            "stages": {"collect-feedback": "on"},
        },
        "worktree": {"pull_request": "auto", "setup": "uv sync"},
        "shared": {"adapter": "local"},
    }
    assert read_config(uncommented) == ProjectConfig()  # every commented value is the default
    assert not (tmp_path / ".devkit/transient").exists()  # no lock file in a project without .devkit/


def test_adds_devkit_keys_after_the_last_top_level_key_and_keeps_every_line(
    project: Path, tools: list[SimpleNamespace]
) -> None:
    before = '# team notes\nschema = 1\nagents = ["codex"]  # ours\n\n[presets]\nteam = "all"\n'
    _write(project, before)
    result = refresh_config_template(project)
    assert (result.state, result.added) == ("updated", ["guidance_block", "override_drift", *COMMON_TABLES])
    text = _text(project)
    head, tail = text.split("\n[presets]\n")
    assert head.startswith('# team notes\nschema = 1\nagents = ["codex"]  # ours\n\n## devkit project configuration')
    assert "# agents =" not in text  # set by the project
    assert "# guidance_block = true" in head and '# override_drift = "warn"' in head
    assert tail.startswith('team = "all"\n\n## Workflow approval gates')
    assert tomllib.loads(text) == tomllib.loads(before)
    assert refresh_config_template(project).to_dict()["state"] == "unchanged"
    assert _text(project) == text


def test_a_key_mentioned_in_a_comment_is_not_added_again(project: Path, tools: list[SimpleNamespace]) -> None:
    _write(project, 'schema = 1\n# override_drift = "block"  # we tried\n')
    assert refresh_config_template(project).added == ["agents", "guidance_block", *COMMON_TABLES]
    assert _text(project).count("override_drift") == 1


def test_a_file_without_top_level_keys_gets_devkit_keys_first(project: Path, tools: list[SimpleNamespace]) -> None:
    _write(project, '[presets]\nteam = "all"\n')
    refresh_config_template(project)
    text = _text(project)
    assert text.startswith("## devkit project configuration") and '\n[presets]\nteam = "all"\n' in text
    assert tomllib.loads(text) == {"presets": {"team": "all"}}


def test_without_engine_templates_no_reserved_table_is_written(
    project: Path, tools: list[SimpleNamespace], reserved: list[SimpleNamespace]
) -> None:
    reserved.clear()  # a standalone devkit-dist installation: no package registers reserved tables
    result = refresh_config_template(project)
    assert result.added == ["agents", "guidance_block", "override_drift", "shared"]
    assert "[workflow" not in _text(project) and "[worktree" not in _text(project)
    _write(project, _text(project) + '\n[workflow.approvals]\nintegration = "auto"\n\n[worktree]\nsetup = "uv sync"\n')
    assert read_config(project) == ProjectConfig()  # reserved tables are passed through unread


def test_reserved_tables_render_before_tool_tables_without_an_intro(
    project: Path, tools: list[SimpleNamespace]
) -> None:
    tools.append(_entry("demo", lambda: DEMO[:1]))
    refresh_config_template(project)
    text = _text(project)
    assert text.index("# [workflow.approvals]") < text.index("# [workflow.stages]") < text.index("# [worktree]")
    assert text.index("# [worktree]") < text.index("## [tool.demo]: the settings")
    assert "engine-pkg" not in text  # reserved tables carry no "the settings of" line


@pytest.mark.parametrize(
    ("entry", "problem"),
    [
        (_entry("tool", lambda: DEMO), "the entry-point name is not a reserved table"),
        (_entry("workflows", lambda: DEMO), "the entry-point name is not a reserved table"),
        (_entry("gates", lambda: "tables"), "returned str, expected a list of TemplateTable"),
        (_entry("rules", lambda: 1 / 0), "division by zero"),
    ],
)
def test_a_failing_or_unreserved_table_extension_is_a_warning(
    project: Path, tools: list[SimpleNamespace], reserved: list[SimpleNamespace], entry: SimpleNamespace, problem: str
) -> None:
    reserved.append(entry)
    result = refresh_config_template(project)
    assert [notice.code for notice in result.notices] == ["CONFIG_TEMPLATE_EXTENSION_FAILED"]
    assert problem in result.notices[0].message
    assert "devkit.config_tables" in result.notices[0].to_dict()["advisory"]["what_to_report"]
    assert f"[{entry.name}" not in _text(project).replace("[workflow", "").replace("[worktree", "")
    assert "# [workflow.approvals]" in _text(project) and "# [worktree]" in _text(project)


@pytest.mark.parametrize(
    "existing",
    [
        '[workflow.approvals]\nintent = "auto"\n',
        '#[ workflow . "approvals" ]\n# intent = "auto"\n',
        'workflow.approvals.intent = "auto"\n',
    ],
)
def test_existing_common_tables_are_preserved(project: Path, tools: list[SimpleNamespace], existing: str) -> None:
    before = "schema = 1\n" + existing
    _write(project, before)
    result = refresh_config_template(project)
    assert result.added == ["agents", "guidance_block", "override_drift", "workflow.stages", "worktree", "shared"]
    assert existing in _text(project)
    assert "# [workflow.approvals]" not in _text(project)
    assert tomllib.loads(_text(project)) == tomllib.loads(before)
    assert refresh_config_template(project).state == "unchanged"


def test_deleted_common_table_is_added_again(project: Path, tools: list[SimpleNamespace]) -> None:
    refresh_config_template(project)
    before = _text(project)
    _write(project, before[: before.index("## Git worktree behavior")])
    assert refresh_config_template(project).added == ["worktree", "shared"]
    assert _text(project) == before


def test_adds_tool_tables_at_the_end(project: Path, tools: list[SimpleNamespace]) -> None:
    tools.append(_entry("demo", lambda: DEMO))
    _write(project, 'schema = 1\n\n[presets]\nteam = "all"\n')
    result = refresh_config_template(project)
    assert result.added == [*DEVKIT_PARTS, "tool.demo", "tool.demo.limits"]
    assert _text(project).endswith(
        "## [tool.demo]: the settings of demo-tool; devkit passes [tool.*] tables through unread.\n"
        "# [tool.demo]\n"
        "#   enabled = true  # boolean; turn demo on\n"
        "\n"
        "## Limits.\n"
        "# [tool.demo.limits]\n"
        "#   timeout = 10  # integer; seconds per call\n"
    )
    assert tomllib.loads(uncomment(_text(project)))["tool"] == {"demo": {"enabled": True, "limits": {"timeout": 10}}}


def test_a_tool_table_the_file_mentions_or_defines_is_left_out(project: Path, tools: list[SimpleNamespace]) -> None:
    tools.append(_entry("demo", lambda: DEMO))
    _write(project, 'schema = 1\n\n[tool.demo.limits]\ntimeout = 5\n\n#[ tool . "demo" ]\n')
    assert refresh_config_template(project).added == DEVKIT_PARTS
    _write(project, "schema = 1\ntool.demo.enabled = false\n")
    assert refresh_config_template(project).added[-1:] == ["tool.demo.limits"]
    assert tomllib.loads(uncomment(_text(project).split("## Limits.")[1]))["tool"]["demo"]["limits"] == {"timeout": 10}


def test_a_new_table_of_an_installed_tool_is_added_later(project: Path, tools: list[SimpleNamespace]) -> None:
    tools.append(_entry("demo", lambda: DEMO[:1]))
    refresh_config_template(project)
    tools[0] = _entry("demo", lambda: DEMO)
    assert refresh_config_template(project).added == ["tool.demo.limits"]
    assert _text(project).count("[tool.demo]") == 2  # one intro line, one header


@pytest.mark.parametrize(
    ("entry", "problem"),
    [
        (_entry("Demo", lambda: DEMO), "the entry-point name is not a [tool.<name>] name"),
        (_entry("demo", lambda: "tables"), "returned str, expected a list of TemplateTable"),
        (_entry("demo", lambda: [TemplateTable(())]), "expected one TemplateKey or more"),
        (_entry("demo", lambda: 1 / 0), "division by zero"),
    ],
)
def test_a_failing_extension_is_a_warning_and_its_tables_are_left_out(
    project: Path, tools: list[SimpleNamespace], entry: SimpleNamespace, problem: str
) -> None:
    tools.extend([entry, _entry("other", lambda: DEMO[:1], package=None)])
    result = refresh_config_template(project)
    assert result.state == "created"
    assert [notice.code for notice in result.notices] == ["CONFIG_TEMPLATE_EXTENSION_FAILED"]
    assert problem in result.notices[0].message
    assert result.notices[0].to_dict()["level"] == "WARNING"
    assert "[tool.demo]" not in _text(project) and "# [tool.other]" in _text(project)
    assert "## [tool.other]: the settings; devkit passes" in _text(project)


def test_an_invalid_config_is_left_alone(project: Path, tools: list[SimpleNamespace]) -> None:
    _write(project, "schema = 1\nunknown = true\n")
    with pytest.raises(Exception, match="unknown fields") as raised:
        refresh_config_template(project)
    assert getattr(raised.value, "code", None) == "CONFIG_INVALID"
    assert _text(project) == "schema = 1\nunknown = true\n"


def test_selection_edits_never_land_below_a_commented_tool_table(project: Path, tools: list[SimpleNamespace]) -> None:
    tools.append(_entry("demo", lambda: DEMO))
    _write(project, 'schema = 1\n\n[presets]\nteam = "all"\n')
    refresh_config_template(project)
    update_config(project, agents=["codex"], presets={"other": ["core"]}, opt_out=["devkit"])
    text = _text(project)
    assert text.index('agents = ["codex"]') < text.index("## devkit project configuration")
    assert tomllib.loads(text)["presets"] == {"team": "all", "other": "core", "devkit": False}
    tool_part = text[text.index("## [tool.demo]") :]
    assert tomllib.loads(uncomment(tool_part)) == {"tool": {"demo": {"enabled": True, "limits": {"timeout": 10}}}}


def test_a_selection_command_creates_the_file_with_the_template(tmp_path: Path, tools: list[SimpleNamespace]) -> None:
    tools.append(_entry("demo", lambda: DEMO))
    update_config(tmp_path, presets={"team": ["all"]})
    text = _text(tmp_path)
    assert text.startswith("schema = 1\n\n## devkit project configuration")
    assert text.index('[presets]\nteam = "all"') < text.index("# [tool.demo]")
    assert tomllib.loads(text) == {"schema": 1, "presets": {"team": "all"}}
    assert refresh_config_template(tmp_path).state == "unchanged"


def test_update_config_returns_failed_extensions_and_takes_the_lock(
    tmp_path: Path, tools: list[SimpleNamespace]
) -> None:
    from devkit.distribution.errors import LockHeldError
    from devkit.distribution.installation.transaction import project_lock

    tools.append(_entry("demo", lambda: 1 / 0))
    notices = update_config(tmp_path, presets={"team": ["all"]})
    assert [notice.code for notice in notices] == ["CONFIG_TEMPLATE_EXTENSION_FAILED"]
    assert not (tmp_path / ".devkit/transient").exists()  # a project without .devkit/ gets no lock file
    assert update_config(tmp_path, agents=["codex"]) == []  # only on creation
    with project_lock(tmp_path), pytest.raises(LockHeldError):
        update_config(tmp_path, agents=["claude-code"])
    assert 'agents = ["codex"]' in _text(tmp_path)


def test_a_sync_that_creates_the_file_reports_failed_extensions(tmp_path: Path, tools: list[SimpleNamespace]) -> None:
    tools.append(_entry("demo", lambda: 1 / 0))
    installed: list[InstalledBundle] = [make_bundle(tmp_path, "team")]
    target = tmp_path / "target"
    target.mkdir()
    result = sync_project(target, installed, save=lambda: prepare_config_update(target, presets={"team": ["guidance"]}))
    assert "CONFIG_TEMPLATE_EXTENSION_FAILED" in [notice.code for notice in result.notices]
    assert 'team = "guidance"' in _text(target)
    again = sync_project(target, installed, save=lambda: prepare_config_update(target, agents=["codex"]))
    assert "CONFIG_TEMPLATE_EXTENSION_FAILED" not in [notice.code for notice in again.notices]  # only on creation


def test_cli_prints_the_result_as_json(project: Path, tools: list[SimpleNamespace]) -> None:
    tools.append(_entry("demo", lambda: 1 / 0))
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "template", "--workspace-root", str(project)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert (payload["state"], payload["added"]) == ("created", DEVKIT_PARTS)
    assert [notice["code"] for notice in payload["notices"]] == ["CONFIG_TEMPLATE_EXTENSION_FAILED"]
    assert result.stderr == ""
    strict = runner.invoke(cli, ["config", "template", "--workspace-root", str(project), "--strict"])
    assert strict.exit_code == 1 and json.loads(strict.stdout)["state"] == "unchanged"
    _write(project, "schema = 2\n")
    refused = runner.invoke(cli, ["config", "template", "--workspace-root", str(project)])
    assert refused.exit_code == 2 and json.loads(refused.stdout)["error"]["code"] == "CONFIG_INVALID"


def test_preview_writes_nothing_and_shows_the_file_a_write_would_produce(
    tmp_path: Path, tools: list[SimpleNamespace]
) -> None:
    preview = preview_config_template(tmp_path)
    assert not (tmp_path / ".devkit").exists()  # no file, directory or lock file
    assert (preview.state, preview.added) == ("created", DEVKIT_PARTS)
    written = refresh_config_template(tmp_path)
    assert (written.state, written.added) == (preview.state, preview.added)
    assert preview.text == _text(tmp_path)
    again = preview_config_template(tmp_path)
    assert (again.state, again.added, again.text) == ("unchanged", [], _text(tmp_path))


def test_preview_refuses_an_invalid_config(project: Path, tools: list[SimpleNamespace]) -> None:
    _write(project, "schema = 2\n")
    with pytest.raises(Exception) as raised:
        preview_config_template(project)
    assert getattr(raised.value, "code", "") == "CONFIG_INVALID"
    assert _text(project) == "schema = 2\n"


def test_cli_print_adds_the_text_and_leaves_the_file(project: Path, tools: list[SimpleNamespace]) -> None:
    before = 'schema = 1\n[presets]\nteam = "all"\n'
    _write(project, before)
    result = CliRunner().invoke(cli, ["config", "template", "--print", "--workspace-root", str(project)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert list(payload) == ["path", "state", "added", "text", "notices"]
    assert payload["state"] == "updated" and payload["text"].startswith("schema = 1\n")
    assert '# override_drift = "warn"' in payload["text"]
    assert _text(project) == before
    assert not (project / ".devkit/transient").exists()
    plain = json.loads(CliRunner().invoke(cli, ["config", "template", "--workspace-root", str(project)]).stdout)
    assert "text" not in plain and _text(project) == payload["text"]
