"""The opt-in ``git-commits`` bundle: commit conventions and the AGENTS.md line that points to them."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from click.testing import CliRunner
from devkit_dist.cli import cli
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.installation import guidance_block
from distsupport.guidance import assert_rule

PACKAGE = Path(__file__).parents[4]
BUNDLE = PACKAGE / "src/devkit_dist/bundles/git_commits/bundle"


def test_manifest_is_opt_in_with_one_preset() -> None:
    bundle = load_bundle(BUNDLE)
    assert (bundle.name, bundle.default_preset, bundle.auto_select) == ("git-commits", "core", False)
    assert bundle.select(["core"]) == {"git-commits", "commit-pointer"}
    assert bundle.version == tomllib.loads((PACKAGE / "pyproject.toml").read_text())["project"]["version"]
    hangul = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")
    assert not any(hangul.search(path.read_text()) for path in BUNDLE.rglob("*.md"))


def _run(*args: str) -> str:
    result = CliRunner().invoke(cli, list(args))
    assert result.exit_code == 0, result.output
    return result.stdout


def _block(root: Path) -> str:
    return guidance_block.extract((root / "AGENTS.md").read_text()) or ""


def test_add_writes_the_pointer_and_get_context_lists_the_conventions(tmp_path: Path) -> None:
    _run("sync", "--workspace-root", str(tmp_path))
    assert "commit message" not in _block(tmp_path)

    _run("add", "git-commits", "--workspace-root", str(tmp_path))
    managed = ".devkit/managed/git-commits/instructions/git-commits.md"
    assert_rule(_block(tmp_path), "before", "commit message", "read", f"`{managed}`")
    assert (tmp_path / managed).is_file()
    context = json.loads(_run("get-context", "git-commits", "--workspace-root", str(tmp_path)))
    assert [Path(item["path"]).name for item in context["instructions"]] == ["git-commits.md"]

    _run("override", "create", "git-commits:git-commits", "--workspace-root", str(tmp_path))
    override = ".devkit/overrides/git-commits/instructions/git-commits.md"
    assert_rule(_block(tmp_path), "before", "commit message", "read", f"`{override}`")

    _run("remove", "git-commits", "--workspace-root", str(tmp_path))
    assert "commit message" not in _block(tmp_path)
    assert "git-commits" not in tomllib.loads((tmp_path / ".devkit/config.toml").read_text())["presets"]
