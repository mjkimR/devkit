from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_core.base.errors import ArgumentError
from devkit_dist.features.distribution.models.errors import BundleError, SelectionError
from devkit_dist.features.distribution.services.bundles import build_bundle, load_bundle
from devkit_dist.features.distribution.services.installation.config import update_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle
from devkit_dist.features.distribution.services.installation.plan import plan_bundle
from devkit_dist.features.distribution.usecases.sync import sync_project
from distsupport.distribution import cli


@pytest.fixture
def source(tmp_path: Path) -> Path:
    root = tmp_path / "source"
    (root / "skills/review/scripts").mkdir(parents=True)
    (root / "skills/review/SKILL.md").write_text("# Review\n")
    script = root / "skills/review/scripts/check.sh"
    script.write_text("#!/bin/sh\nexit 0\n")
    script.chmod(0o755)
    (root / "native").mkdir()
    (root / "native/reviewer.toml").write_bytes(b'model = "custom"\nfuture_option = true\n')
    (root / "bundle.toml").write_text("""schema = 1
name = "sample"
version = "0.1.0"
[[assets]]
id = "review"
kind = "skill"
source = "skills/review"
[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
codex = "native/reviewer.toml"
[presets.daily]
assets = ["review"]
""")
    return root


def test_archive_is_reproducible_and_preserves_native_bytes(source: Path, tmp_path: Path) -> None:
    bundle = load_bundle(source)
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    build_bundle(bundle, first)
    os.utime(source / "native/reviewer.toml", (1000000000, 1000000000))
    build_bundle(load_bundle(source), second)
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == sorted(archive.namelist())
        assert archive.read("native/reviewer.toml") == (source / "native/reviewer.toml").read_bytes()
        inventory = json.loads(archive.read("inventory.json"))
        script = "skills/review/scripts/check.sh"
        assert inventory[script]["mode"] == 0o755
        for name, metadata in inventory.items():
            assert metadata["sha256"] == hashlib.sha256(archive.read(name)).hexdigest()
            assert archive.getinfo(name).external_attr >> 16 & 0o777 == metadata["mode"]


def test_plan_preset_is_read_only(source: Path) -> None:
    before = sorted(source.rglob("*"))
    result = plan_bundle(load_bundle(source), "daily").to_dict()
    assert [asset["id"] for asset in result["assets"]] == ["review"]
    destinations = {file["destination"]: file["mode"] for file in result["files"]}
    # The plan is the sync inventory: managed copies plus every agent's native projection.
    assert destinations == {
        ".devkit/managed/sample/bundle.toml": "0644",
        ".devkit/managed/sample/skills/review/SKILL.md": "0644",
        ".devkit/managed/sample/skills/review/scripts/check.sh": "0755",
        ".agents/skills/review/SKILL.md": "0644",
        ".agents/skills/review/scripts/check.sh": "0755",
        ".claude/skills/review/SKILL.md": "0644",
        ".claude/skills/review/scripts/check.sh": "0755",
    }
    narrowed = plan_bundle(load_bundle(source), "all", ["codex"]).to_dict()
    assert {file["destination"] for file in narrowed["files"]} >= {".codex/agents/reviewer.toml"}
    assert not any(file["destination"].startswith(".claude/") for file in narrowed["files"])
    assert sorted(source.rglob("*")) == before
    with pytest.raises(SelectionError, match="unknown preset"):
        plan_bundle(load_bundle(source), "missing")


def test_default_preset_and_reserved_all(source: Path) -> None:
    bundle = load_bundle(source)
    assert bundle.default_preset is None
    assert bundle.preset_names == ["all", "daily"]
    assert bundle.select(["all"]) == {"review", "reviewer"}
    assert [asset["id"] for asset in plan_bundle(bundle).to_dict()["assets"]] == ["review", "reviewer"]
    manifest = source / "bundle.toml"
    manifest.write_text(
        manifest.read_text().replace('version = "0.1.0"', 'version = "0.1.0"\ndefault_preset = "daily"')
    )
    bundle = load_bundle(source)
    assert bundle.default_preset == "daily"
    assert [asset["id"] for asset in plan_bundle(bundle).to_dict()["assets"]] == ["review"]
    assert [asset["id"] for asset in plan_bundle(bundle, "all").to_dict()["assets"]] == ["review", "reviewer"]


@pytest.mark.parametrize(
    ("original", "replacement", "message"),
    [
        ("schema = 1", "schema = true", "unsupported schema"),
        ('version = "0.1.0"', 'version = "latest"', "version"),
        ('source = "skills/review"', 'source = "../escape"', "unsafe source"),
        ('source = "skills/review"', 'source = "/tmp"', "unsafe source"),
        ('source = "skills/review"', 'source = "missing"', "source missing"),
        ('id = "reviewer"', 'id = "review"', "duplicate asset"),
        ('kind = "skill"', 'kind = "unknown"', "unknown asset kind"),
        ('assets = ["review"]', 'assets = ["missing"]', "unknown asset selection"),
        ("schema = 1", "schema = 1\nextra = true", "unknown keys"),
        ("[presets.daily]", "[presets.all]", "preset all is reserved"),
        ('version = "0.1.0"', 'version = "0.1.0"\ndefault_preset = "missing"', "default_preset"),
        ('version = "0.1.0"', 'version = "0.1.0"\ndefault_preset = 1', "default_preset"),
    ],
)
def test_invalid_manifest(source: Path, original: str, replacement: str, message: str) -> None:
    manifest = source / "bundle.toml"
    manifest.write_text(manifest.read_text().replace(original, replacement))
    with pytest.raises(BundleError, match=message):
        load_bundle(source)


def test_nested_symlink_rejected(source: Path, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.write_text("external")
    (source / "skills/review/link").symlink_to(outside)
    with pytest.raises(BundleError, match="nonregular source"):
        load_bundle(source)


def test_build_protects_output(source: Path, tmp_path: Path) -> None:
    bundle = load_bundle(source)
    with pytest.raises(ArgumentError, match="outside") as outside:
        build_bundle(bundle, source / "output.zip")
    assert outside.value.target_files == ("--output",)
    output = tmp_path / "existing.zip"
    output.write_bytes(b"keep")
    with pytest.raises(ArgumentError, match="archive already exists") as exists:
        build_bundle(bundle, output)
    assert exists.value.code == "ARGUMENT_INVALID"
    assert output.read_bytes() == b"keep"


def test_cli_json_and_failure(source: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["bundle", "plan", str(source), "--preset", "daily", "--agent", "codex"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["bundle"] == "sample"
    assert json.loads(result.output)["agents"] == ["codex"]
    result = runner.invoke(cli, ["bundle", "plan", str(source), "--preset", "missing"])
    assert result.exit_code == 2
    assert "unknown preset" in result.output


def test_plan_matches_what_sync_deploys(source: Path, tmp_path: Path) -> None:
    bundle = load_bundle(source)
    target = tmp_path / "consumer"
    target.mkdir()
    update_config(target, presets={"sample": ["all"]}, agents=["codex", "claude-code"])
    sync_project(target, [InstalledBundle("sample-content", "0.1.0", bundle)])
    recorded = json.loads((target / ".devkit/installation.json").read_text())["files"]
    planned = plan_bundle(bundle, "all", ["codex", "claude-code"]).to_dict()["files"]
    assert {item["destination"]: (item["sha256"], item["mode"]) for item in planned} == {
        name: (meta["sha256"], f"{meta['mode']:04o}") for name, meta in recorded.items()
    }
