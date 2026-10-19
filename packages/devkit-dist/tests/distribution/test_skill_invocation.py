"""``invocation`` on a skill asset: validation and the native setting each agent's projection carries."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from devkit.core.frontmatter import parse
from devkit.core.receipt import OVERRIDES_PATH
from devkit.distribution.bundles import load_bundle
from devkit.distribution.errors import BundleError
from devkit.distribution.installation.config import update_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.sync import sync_project

HEADER = 'schema = 1\nname = "team"\nversion = "0.1.0"\n'
SKILL = "---\nname: release\ndescription: Cut a release.\n---\nSteps.\n"


def write(root: Path, manifest: str, files: dict[str, str]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    (root / "bundle.toml").write_text(HEADER + manifest)
    return root


def skill_manifest(invocation: str | None = "user") -> str:
    line = f'invocation = "{invocation}"\n' if invocation is not None else ""
    return f'[[assets]]\nid = "release"\nkind = "skill"\nsource = "skills/release"\n{line}'


def deploy(tmp_path: Path, files: dict[str, str], invocation: str | None = "user") -> Path:
    source = write(tmp_path / "source", skill_manifest(invocation), files)
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"team": ["all"]}, agents=["codex", "claude-code", "antigravity"])
    sync_project(target, [InstalledBundle("team-content", "0.1.0", load_bundle(source))])
    return target


def test_invocation_defaults_to_auto(tmp_path: Path) -> None:
    bundle = load_bundle(write(tmp_path / "b", skill_manifest(None), {"skills/release/SKILL.md": SKILL}))
    assert bundle.assets[0].invocation == "auto"


@pytest.mark.parametrize(
    ("manifest", "message"),
    [
        (skill_manifest("model"), r"release: invocation must be one of \['auto', 'user'\]"),
        (skill_manifest(None) + "invocation = true\n", "invocation must be one of"),
        ('[[assets]]\nid = "doc"\nkind = "document"\nsource = "doc.md"\ninvocation = "user"\n', "only skill assets"),
    ],
)
def test_invalid_invocation_is_rejected(tmp_path: Path, manifest: str, message: str) -> None:
    files = {"skills/release/SKILL.md": SKILL, "doc.md": "x\n"}
    with pytest.raises(BundleError, match=message):
        load_bundle(write(tmp_path / "b", manifest, files))


@pytest.mark.parametrize("invocation", [None, "user"])
@pytest.mark.parametrize(
    ("files", "message"),
    [
        (
            {"skills/release/SKILL.md": SKILL.replace("---\nSteps", "disable-model-invocation: true\n---\nSteps")},
            r"release/skills/release/SKILL\.md: disable-model-invocation is set by invocation in bundle\.toml",
        ),
        (
            {
                "skills/release/SKILL.md": SKILL,
                "skills/release/agents/openai.yaml": "policy:\n  allow_implicit_invocation: false\n",
            },
            r"release/skills/release/agents/openai\.yaml: policy\.allow_implicit_invocation is set by invocation",
        ),
        (
            {"skills/release/SKILL.md": SKILL, "skills/release/agents/openai.yaml": "- not a mapping\n"},
            r"agents/openai\.yaml: expected a YAML mapping",
        ),
    ],
)
def test_sources_never_declare_the_native_setting(
    tmp_path: Path, invocation: str | None, files: dict[str, str], message: str
) -> None:
    with pytest.raises(BundleError, match=message) as info:
        load_bundle(write(tmp_path / "b", skill_manifest(invocation), files))
    assert info.value.code == "BUNDLE_INVALID"


def test_user_skill_projects_each_agents_native_setting(tmp_path: Path) -> None:
    target = deploy(tmp_path, {"skills/release/SKILL.md": SKILL.replace("\n", "\r\n")})
    claude = (target / ".claude/skills/release/SKILL.md").read_bytes()
    assert claude.startswith(
        b"---\r\nname: release\r\ndescription: Cut a release.\r\ndisable-model-invocation: true\r\n---"
    )
    assert parse(claude.decode()).data == {
        "name": "release",
        "description": "Cut a release.",
        "disable-model-invocation": True,
    }
    shared = target / ".agents/skills/release"
    assert b"disable-model-invocation" not in (shared / "SKILL.md").read_bytes()
    assert yaml.safe_load((shared / "agents/openai.yaml").read_text()) == {
        "policy": {"allow_implicit_invocation": False}
    }
    # The managed copy stays the upstream source; only the projections carry host settings.
    managed = target / ".devkit/managed/team/skills/release"
    assert b"disable-model-invocation" not in (managed / "SKILL.md").read_bytes()
    assert not (managed / "agents").exists()


def test_auto_skill_projections_are_the_source(tmp_path: Path) -> None:
    target = deploy(tmp_path, {"skills/release/SKILL.md": SKILL}, invocation="auto")
    assert (target / ".claude/skills/release/SKILL.md").read_text() == SKILL
    assert not (target / ".agents/skills/release/agents").exists()


@pytest.mark.parametrize(
    ("skill", "expected"),
    [
        ("# Release\n", "---\ndisable-model-invocation: true\n---\n# Release\n"),
        ("---\n---\n# Release\n", "---\ndisable-model-invocation: true\n---\n# Release\n"),
    ],
)
def test_frontmatter_is_added_where_the_source_has_none(tmp_path: Path, skill: str, expected: str) -> None:
    target = deploy(tmp_path, {"skills/release/SKILL.md": skill})
    assert (target / ".claude/skills/release/SKILL.md").read_text() == expected


@pytest.mark.parametrize(
    ("shipped", "expected"),
    [
        (
            "interface:\n  display_name: Release  # shown in the picker\n",
            "interface:\n  display_name: Release  # shown in the picker\npolicy:\n  allow_implicit_invocation: false\n",
        ),
        (
            "interface:\n  display_name: Release",
            "interface:\n  display_name: Release\npolicy:\n  allow_implicit_invocation: false\n",
        ),
        (
            "policy:\n  products: [codex]\n",
            "policy:\n  products:\n  - codex\n  allow_implicit_invocation: false\n",
        ),
    ],
)
def test_shipped_codex_settings_gain_the_policy(tmp_path: Path, shipped: str, expected: str) -> None:
    target = deploy(tmp_path, {"skills/release/SKILL.md": SKILL, "skills/release/agents/openai.yaml": shipped})
    assert (target / ".agents/skills/release/agents/openai.yaml").read_text() == expected


def test_override_may_not_declare_the_native_setting(tmp_path: Path) -> None:
    target = deploy(tmp_path, {"skills/release/SKILL.md": SKILL})
    override = target / OVERRIDES_PATH / "team/skills/release/SKILL.md"
    override.parent.mkdir(parents=True)
    override.write_text(SKILL.replace("---\nSteps", "disable-model-invocation: false\n---\nSteps"))
    source = tmp_path / "source"
    with pytest.raises(BundleError, match=r"overrides/team/skills/release/SKILL\.md: disable-model-invocation is set"):
        sync_project(target, [InstalledBundle("team-content", "0.1.0", load_bundle(source))])
