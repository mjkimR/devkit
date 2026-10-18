from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from devkit.core.errors import ConfigError
from devkit.distribution.bundles import load_bundle
from devkit.distribution.bundles.templates import render_template
from devkit.distribution.errors import BundleError, ReceiptStaleError
from devkit.distribution.installation.context import get_context
from devkit.distribution.installation.inventory import desired_inventory
from devkit.distribution.installation.override_commands import create_override, remove_override
from devkit.distribution.installation.sync import sync_project
from testsupport.distribution import instruction, write_bundle


def bundle(tmp_path: Path, *, text: str | None = None, declaration: str = 'type = "string"\ndefault = "auto"'):
    return write_bundle(
        tmp_path / "source",
        f"""schema = 1
name = "style"
version = "0.1.0"
[variables.language]
{declaration}
[[assets]]
id = "style"
kind = "instruction"
source = "style.md.jinja"
[[assets]]
id = "pointer"
kind = "guidance"
source = "pointer.md.jinja"
""",
        {
            "style.md.jinja": text if text is not None else instruction("style", "Language: {{ vars.language }}\n"),
            "pointer.md.jinja": "- Read {path:style}; language {{ vars.language }}.\n",
        },
    )


def config(root: Path, language: str = '"ko"') -> None:
    (root / ".devkit").mkdir(parents=True, exist_ok=True)
    (root / ".devkit/config.toml").write_text(f"""agents = []
[presets]
style = "all"
[bundles.style.variables]
language = {language}
""")


def test_render_sync_configuration_and_locked_restore(tmp_path: Path) -> None:
    item = bundle(tmp_path)
    root = tmp_path / "project"
    config(root)
    result = sync_project(root, [item])
    output = root / ".devkit/managed/style/style.md"
    assert "Language: ko" in output.read_text()
    assert not output.with_suffix(".md.jinja").exists()
    assert ".devkit/managed/style/style.md; language ko" in (root / "AGENTS.md").read_text()
    assert get_context(root, "style").to_dict()["instructions"][0]["path"].endswith("style.md")
    receipt = (root / ".devkit/installation.json").read_bytes()
    assert sync_project(root, [item]).to_dict()["actions"] == []
    output.unlink()
    sync_project(root, [item], locked=True)
    assert "Language: ko" in output.read_text()
    assert (root / ".devkit/installation.json").read_bytes() == receipt
    config(root, '"en"')
    preview = sync_project(root, [item], dry_run=True)
    assert preview.to_dict()["actions"]
    assert "Language: ko" in output.read_text()
    with pytest.raises(ReceiptStaleError):
        sync_project(root, [item], locked=True)
    assert (root / ".devkit/installation.json").read_bytes() == receipt
    sync_project(root, [item])
    assert "Language: en" in output.read_text()
    assert result.to_dict()["actions"]


def test_defaults_and_raw_override_lifecycle(tmp_path: Path) -> None:
    item = bundle(tmp_path)
    inventory = desired_inventory([item], {"style": ["all"]}, [])
    assert b"Language: auto" in inventory.files[".devkit/managed/style/style.md"].data
    root = tmp_path / "project"
    config(root)
    sync_project(root, [item])
    create_override(root, [item], "style:style")
    raw = root / ".devkit/overrides/style/style.md.jinja"
    assert "{{ vars.language }}" in raw.read_text()
    raw.write_text(instruction("style", "Custom {{ vars.language }}\n"))
    sync_project(root, [item])
    output = root / ".devkit/managed/style/style.md"
    assert "Custom ko" in output.read_text()
    assert get_context(root, "style").to_dict()["instructions"][0]["path"] == str(output)
    recorded = json.loads((root / ".devkit/installation.json").read_text())
    assert recorded["overrides"]["style"]["style"]["relative_path"] == "style.md.jinja"
    remove_override(root, [item], "style:style")
    assert "Language: ko" in output.read_text()
    assert not raw.exists()


@pytest.mark.parametrize("value", ["true", "1", "[]", "{}", "1.5"])
def test_invalid_project_variable_fails_before_writing(tmp_path: Path, value: str) -> None:
    item = bundle(tmp_path)
    root = tmp_path / "project"
    config(root, value)
    with pytest.raises(ConfigError):
        sync_project(root, [item])
    assert not (root / ".devkit/installation.json").exists()
    assert not (root / ".devkit/managed").exists()


def test_missing_required_and_unknown_variables(tmp_path: Path) -> None:
    item = bundle(tmp_path, declaration='type = "string"')
    with pytest.raises(ConfigError, match="missing required"):
        desired_inventory([item], {"style": ["all"]}, [])
    with pytest.raises(ConfigError, match="undeclared"):
        desired_inventory([item], {"style": ["all"]}, [], variables={"style": {"typo": "ko"}})


@pytest.mark.parametrize(
    "declaration", ['type = "integer"\ndefault = true', 'type = "float"', 'type = "string"\nextra = 1']
)
def test_invalid_declarations(tmp_path: Path, declaration: str) -> None:
    with pytest.raises(BundleError):
        bundle(tmp_path, declaration=declaration)


@pytest.mark.parametrize(
    "text",
    [
        "{{ vars.missing }}",
        "{% if %}",
        "{{ config.language }}",
        "{{ vars.language.upper() }}",
        "{{ cycler() }}",
        "{% include 'secret' %}",
        "{{ 1 / 0 }}",
    ],
)
def test_template_errors_are_bundle_errors(text: str) -> None:
    with pytest.raises(BundleError, match="template rendering failed"):
        render_template(text.encode(), {"language": "ko"}, "style.md.jinja")


@pytest.mark.parametrize("text", ["No frontmatter {{ vars.language }}", "---\nname: style\n---\nMissing description"])
def test_final_instruction_validation_before_writes(tmp_path: Path, text: str) -> None:
    item = bundle(tmp_path, text=text)
    root = tmp_path / "project"
    config(root)
    with pytest.raises(BundleError):
        sync_project(root, [item])
    assert not (root / ".devkit/managed").exists()


def test_final_fragment_limits(tmp_path: Path) -> None:
    item = bundle(tmp_path)
    (item.bundle.root / "pointer.md.jinja").write_text("- {{ vars.language }}")
    with pytest.raises(BundleError, match="300 bytes"):
        desired_inventory([item], {"style": ["all"]}, [], variables={"style": {"language": "x" * 301}})


def test_ordinary_markdown_keeps_jinja_literal_and_collision_fails(tmp_path: Path) -> None:
    item = bundle(tmp_path)
    path = item.bundle.root / "style.md"
    path.write_text(instruction("literal", "{{ vars.language }}\n"))
    manifest = item.bundle.root / "bundle.toml"
    original = manifest.read_text()
    manifest.write_text(original.replace('source = "style.md.jinja"', 'source = "style.md"'))
    ordinary = load_bundle(item.bundle.root)
    inventory = desired_inventory([replace(item, bundle=ordinary)], {"style": ["all"]}, [])
    assert b"{{ vars.language }}" in inventory.files[".devkit/managed/style/style.md"].data
    manifest.write_text(original + '\n[[assets]]\nid = "collision"\nkind = "instruction"\nsource = "style.md"\n')
    with pytest.raises(BundleError, match="collision"):
        load_bundle(item.bundle.root)


def test_lazy_cli_and_plain_inventory(tmp_path: Path) -> None:
    item = write_bundle(
        tmp_path / "plain",
        'schema=1\nname="plain"\nversion="0.1.0"\n[[assets]]\nid="guide"\nkind="instruction"\nsource="guide.md"\n',
        {"guide.md": instruction("guide")},
    )
    script = f"""import sys
from click.testing import CliRunner
from devkit.cli import cli
assert CliRunner().invoke(cli, ["--help"]).exit_code == 0
from devkit.distribution.bundles import load_bundle
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.inventory import desired_inventory
from devkit.distribution.installation.sync import sync_project
from pathlib import Path
bundle = load_bundle(Path({str(item.bundle.root)!r}))
desired_inventory([InstalledBundle("plain", "0.1.0", bundle)], {{"plain": ["all"]}}, [])
root = Path({str(tmp_path / "consumer")!r})
root.mkdir()
sync_project(root, [InstalledBundle("plain", "0.1.0", bundle)], agents=[], presets={{"plain": ["all"]}})
assert not any(name == "jinja2" or name.startswith("jinja2.") for name in sys.modules)
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_mapping_identifiers_and_exact_scalar_types(tmp_path: Path) -> None:
    assert (
        render_template(
            b"{{ vars.items }} {{ vars.count }} {{ vars.enabled }}\n",
            {"items": "value", "count": 2, "enabled": False},
            "test",
        )
        == b"value 2 False\n"
    )
    item = bundle(tmp_path, declaration='type = "integer"\ndefault = 2')
    inventory = desired_inventory([item], {"style": ["all"]}, [])
    assert b"Language: 2" in inventory.files[".devkit/managed/style/style.md"].data
    with pytest.raises(ConfigError):
        desired_inventory([item], {"style": ["all"]}, [], variables={"style": {"language": True}})


def test_document_directory_rendering_and_seed(tmp_path: Path) -> None:
    item = write_bundle(
        tmp_path / "source",
        """schema=1
name="docs"
version="0.1.0"
[variables.language]
type="string"
default="ko"
[[assets]]
id="reference"
kind="document"
source="reference"
[[assets]]
id="seed"
kind="document"
source="scaffold"
seeded=true
target="docs"
""",
        {
            "reference/README.md.jinja": "{{ vars.language }}\n",
            "reference/literal.md": "{{ literal }}\n",
            "scaffold/guide.md.jinja": "{{ vars.language }}\n",
        },
    )
    inventory = desired_inventory([item], {"docs": ["all"]}, [])
    assert inventory.files[".devkit/managed/docs/reference/README.md"].data == b"ko\n"
    assert inventory.files[".devkit/managed/docs/reference/literal.md"].data == b"{{ literal }}\n"
    assert inventory.seeds["docs/guide.md"].content.data == b"ko\n"


def test_rendered_guidance_reference_must_be_selected(tmp_path: Path) -> None:
    item = bundle(tmp_path)
    manifest = item.bundle.root / "bundle.toml"
    manifest.write_text(manifest.read_text() + '\n[presets.pointer]\nassets=["pointer"]\n')
    item = replace(item, bundle=load_bundle(item.bundle.root))
    with pytest.raises(BundleError, match="selected single-file"):
        desired_inventory([item], {"style": ["pointer"]}, [])


def test_invalid_template_override_is_rolled_back(tmp_path: Path) -> None:
    item = bundle(tmp_path)
    root = tmp_path / "project"
    config(root)
    sync_project(root, [item])
    before = (root / ".devkit/installation.json").read_bytes()
    # create_override stages this source before its sync; failure must restore the workspace.
    (item.bundle.root / "style.md.jinja").write_text("{{ vars.missing }}")
    with pytest.raises(BundleError):
        create_override(root, [item], "style:style")
    assert not (root / ".devkit/overrides/style/style.md.jinja").exists()
    assert (root / ".devkit/installation.json").read_bytes() == before


def test_template_file_cannot_be_another_destinations_directory(tmp_path: Path) -> None:
    with pytest.raises(BundleError, match="destination collision"):
        write_bundle(
            tmp_path / "source",
            """schema=1
name="collision"
version="0.1.0"
[[assets]]
id="docs"
kind="document"
source="docs"
""",
            {"docs/guide.md.jinja": "rendered\n", "docs/guide.md/child.md": "child\n"},
        )
    assert not (tmp_path / "source/.devkit").exists()
