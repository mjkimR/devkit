"""``guidance`` assets: bundle fragments rendered into the root ``AGENTS.md`` block."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.bundles.fragments import MAX_FRAGMENT_BYTES
from devkit_dist.features.distribution.services.installation import guidance_block
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.workspace import AGENTS_FILE
from devkit_dist.features.distribution.usecases.override_commands import create_override
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.distribution import instruction, write_bundle

MANIFEST = """schema = 1
name = "{name}"
version = "0.1.0"
[[assets]]
id = "conventions"
kind = "instruction"
source = "instructions/conventions.md"
[[assets]]
id = "pointer"
kind = "guidance"
source = "guidance/pointer.md"
[presets.core]
assets = ["conventions", "pointer"]
[presets.bare]
assets = ["conventions"]
"""
POINTER = "- Before drafting a commit message, read `{path:conventions}`.\n"


def _bundle(root: Path, name: str, pointer: str = POINTER) -> InstalledBundle:
    return write_bundle(
        root / name,
        MANIFEST.format(name=name),
        {"instructions/conventions.md": instruction("conventions"), "guidance/pointer.md": pointer},
        package=f"{name}-content",
    )


def _target(tmp_path: Path, presets: dict[str, list[str]]) -> Path:
    root = tmp_path / "consumer"
    root.mkdir()
    update_config(root, presets=presets, agents=["codex"])
    return root


def _block(root: Path) -> str:
    block = guidance_block.extract((root / AGENTS_FILE).read_text())
    assert block is not None
    return block


def test_fragment_renders_with_the_managed_path_in_a_stable_order(tmp_path: Path) -> None:
    alpha = _bundle(tmp_path, "alpha", "- Alpha: read `{path:conventions}`.\n  Then follow it.\n")
    beta = _bundle(tmp_path, "beta", "- Beta rule.\n")
    target = _target(tmp_path, {"alpha": ["core"], "beta": ["core"]})
    sync_project(target, [beta, alpha])
    block = _block(target)
    lines = block.splitlines()
    alpha_line = "- Alpha: read `.devkit/managed/alpha/instructions/conventions.md`."
    assert lines[lines.index(alpha_line) + 1 :][:2] == ["  Then follow it.", "- Beta rule."]
    assert lines.index(alpha_line) > next(i for i, line in enumerate(lines) if line.startswith("- Never edit"))
    # Discovery order does not matter: the same selection yields the same block.
    actions = sync_project(target, [alpha, beta]).to_dict()["actions"]
    assert all(action["path"] != AGENTS_FILE for action in actions)  # type: ignore[index]
    assert _block(target) == block


def test_preset_without_the_fragment_leaves_the_block_alone(tmp_path: Path) -> None:
    item = _bundle(tmp_path, "team")
    target = _target(tmp_path, {"team": ["core"]})
    sync_project(target, [item])
    assert "commit message" in _block(target)
    sync_project(target, [item], presets={"team": ["bare"]})
    assert "commit message" not in _block(target)


def test_overrides_change_the_cited_path_and_the_fragment(tmp_path: Path) -> None:
    item = _bundle(tmp_path, "team")
    target = _target(tmp_path, {"team": ["core"]})
    sync_project(target, [item])
    create_override(target, [item], "team:conventions")
    assert "`.devkit/overrides/team/instructions/conventions.md`" in _block(target)

    create_override(target, [item], "team:pointer")
    (target / ".devkit/overrides/team/guidance/pointer.md").write_text("- Project wording for `{path:conventions}`.\n")
    sync_project(target, [item])
    assert "- Project wording for `.devkit/overrides/team/instructions/conventions.md`." in _block(target)

    (target / ".devkit/overrides/team/guidance/pointer.md").write_text("Not a list item.\n")
    with pytest.raises(BundleError, match="list items only"):
        sync_project(target, [item])
    (target / ".devkit/overrides/team/guidance/pointer.md").write_text("- Read `{path:pointer}`.\n")
    with pytest.raises(BundleError, match="must name a selected single-file"):
        sync_project(target, [item])


@pytest.mark.parametrize(
    ("pointer", "message"),
    [
        ("- " + "x" * MAX_FRAGMENT_BYTES + "\n", "limited to"),
        ("- First.\n\n- After a blank line.\n", "list items only"),
        ("  Continuation first.\n", "list items only"),
        ("# Heading\n", "list items only"),
        ("- <!-- DEVKIT:END -->\n", "HTML comment"),
        ("- Windows line.\r\n- Second.\r\n", "LF line endings"),
        ("- Read `{path:missing}`.\n", "must name a single-file"),
        ("- Read `{path:pointer}`.\n", "must name a single-file"),
    ],
)
def test_invalid_fragments_are_rejected_when_the_bundle_loads(tmp_path: Path, pointer: str, message: str) -> None:
    with pytest.raises(BundleError, match=message):
        _bundle(tmp_path, "team", pointer)


def test_presets_must_select_what_a_fragment_names(tmp_path: Path) -> None:
    manifest = MANIFEST.format(name="team").replace('assets = ["conventions"]\n', 'assets = ["pointer"]\n')
    with pytest.raises(BundleError, match="bare: selects guidance pointer without the assets it names"):
        write_bundle(
            tmp_path / "team",
            manifest,
            {"instructions/conventions.md": instruction("conventions"), "guidance/pointer.md": POINTER},
        )


def test_guidance_is_one_file_without_variants(tmp_path: Path) -> None:
    root = tmp_path / "team"
    (root / "guidance").mkdir(parents=True)
    (root / "guidance/pointer.md").write_text("- Rule.\n")
    (root / "bundle.toml").write_text(
        'schema = 1\nname = "team"\nversion = "0.1.0"\n'
        '[[assets]]\nid = "pointer"\nkind = "guidance"\nsource = "guidance"\n'
    )
    with pytest.raises(BundleError, match="guidance source must be one file"):
        load_bundle(root)
    (root / "bundle.toml").write_text(
        'schema = 1\nname = "team"\nversion = "0.1.0"\n'
        '[[assets]]\nid = "pointer"\nkind = "guidance"\nvariants = {codex = "guidance/pointer.md"}\n'
    )
    with pytest.raises(BundleError, match="declares a single source"):
        load_bundle(root)
