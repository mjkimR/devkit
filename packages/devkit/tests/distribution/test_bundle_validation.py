"""Load-time validation: ``bundle validate`` and discovery reject what a sync for any agent would reject."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml
from devkit.core.errors import ArgumentError
from devkit.distribution.bundles import Bundle, build_bundle, load_bundle
from devkit.distribution.bundles.manifest import RESERVED_SKILL_IDS
from devkit.distribution.bundles.subagents import read_contract, render_projection
from devkit.distribution.errors import BundleError
from devkit.distribution.installation import playbook_skill, workflow_skill

HEADER = 'schema = 1\nname = "team"\nversion = "0.1.0"\n'
INSTRUCTION = "---\nname: guide\ndescription: Read first.\n---\nBody.\n"
PLAYBOOK = "---\nname: recover\ndescription: Recover a replica.\n---\nSteps.\n"
CONTRACT = """---
role: {role}
title: Reviewer
description: Reviews a change.
hosts:
  claude-code: native
  codex: native
  antigravity: native
---
Prompt.
"""


def write(root: Path, manifest: str, files: dict[str, str]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    (root / "bundle.toml").write_text(HEADER + manifest)
    return root


def load(root: Path, manifest: str, files: dict[str, str]) -> Bundle:
    return load_bundle(write(root, manifest, files))


SUBAGENT_VARIANT = '[[assets]]\nid = "rev"\nkind = "subagent"\n[assets.variants]\n'


@pytest.mark.parametrize(
    ("variant", "files"),
    [
        ('codex = "native/rev.md"', {"native/rev.md": "x\n"}),
        ('claude-code = "native/rev.toml"', {"native/rev.toml": "x = 1\n"}),
        ('codex = "native/d"', {"native/d/a.toml": "x = 1\n", "native/d/b.toml": "y = 1\n"}),
    ],
)
def test_subagent_variant_must_be_one_native_file(tmp_path: Path, variant: str, files: dict[str, str]) -> None:
    with pytest.raises(BundleError, match=r"rev/native/\S+: the \S+ subagent variant must be one \.(toml|md) file"):
        load(tmp_path / "b", SUBAGENT_VARIANT + variant + "\n", files)


def test_native_subagent_variants_load(tmp_path: Path) -> None:
    bundle = load(
        tmp_path / "b",
        SUBAGENT_VARIANT + 'codex = "native/rev.toml"\nclaude-code = "native/rev.md"\n',
        {"native/rev.toml": "x = 1\n", "native/rev.md": "---\nname: rev\n---\nPrompt.\n"},
    )
    assert bundle.assets[0].sources == (("claude-code", "native/rev.md"), ("codex", "native/rev.toml"))


@pytest.mark.parametrize("manifest_key", ['source = "skills/s"', '[assets.variants]\nclaude-code = "skills/s"'])
def test_skill_frontmatter_is_checked_against_its_source(tmp_path: Path, manifest_key: str) -> None:
    # The context prerequisite goes after the frontmatter; an unclosed block fails here, naming the source.
    with pytest.raises(BundleError, match=r"^s/skills/s/SKILL\.md: .*never closed"):
        load(
            tmp_path / "b",
            f'[[assets]]\nid = "s"\nkind = "skill"\n{manifest_key}\n',
            {"skills/s/SKILL.md": "---\nname: s\n"},
        )


@pytest.mark.parametrize("skill_id", sorted(RESERVED_SKILL_IDS))
def test_generated_entry_skill_ids_are_reserved(tmp_path: Path, skill_id: str) -> None:
    assert {playbook_skill.NAME, workflow_skill.NAME} == RESERVED_SKILL_IDS
    with pytest.raises(BundleError, match=f"{skill_id}: skill id is reserved"):
        load(
            tmp_path / "b",
            f'[[assets]]\nid = "{skill_id}"\nkind = "skill"\nsource = "skills/p"\n'
            '[[assets]]\nid = "pb"\nkind = "playbook"\nsource = "pb.md"\n',
            {"skills/p/SKILL.md": "# P\n", "pb.md": PLAYBOOK},
        )


def test_contract_must_name_every_agent(tmp_path: Path) -> None:
    contract = CONTRACT.format(role="rev").replace("  antigravity: native\n", "")
    with pytest.raises(BundleError, match=r"rev/c\.md: hosts must name every agent; missing \['antigravity'\]") as info:
        load(tmp_path / "b", '[[assets]]\nid = "rev"\nkind = "subagent"\nsource = "c.md"\n', {"c.md": contract})
    assert info.value.fix is not None and "status: unsupported" in info.value.fix


def test_shared_skill_directory_variants_must_be_identical(tmp_path: Path) -> None:
    manifest = '[[assets]]\nid = "s"\nkind = "skill"\n[assets.variants]\ncodex = "a"\nantigravity = "b"\n'
    with pytest.raises(BundleError, match=r"codex and antigravity skill variants .* must be identical"):
        load(tmp_path / "differ", manifest, {"a/SKILL.md": "# A\n", "b/SKILL.md": "# B\n"})
    with pytest.raises(BundleError, match="must be identical"):
        load(tmp_path / "extra", manifest, {"a/SKILL.md": "# A\n", "b/SKILL.md": "# A\n", "b/x.sh": "x\n"})
    root = write(tmp_path / "mode", manifest, {"a/SKILL.md": "# A\n", "b/SKILL.md": "# A\n"})
    (root / "b/SKILL.md").chmod(0o755)
    with pytest.raises(BundleError, match="must be identical"):
        load_bundle(root)
    same = load(tmp_path / "same", manifest, {"a/SKILL.md": "# A\n", "b/SKILL.md": "# A\n"})
    assert dict(same.assets[0].sources) == {"antigravity": "b", "codex": "a"}


@pytest.mark.parametrize(
    ("kind", "files"),
    [
        ("instruction", {"a.md": INSTRUCTION, "b.md": INSTRUCTION}),
        ("playbook", {"a.md": PLAYBOOK, "b.md": PLAYBOOK}),
        ("rule", {"a.md": "A = 1\n", "b.md": "B = 1\n"}),
        ("workflow", {"a.md": "---\nid: a\nstages: [x]\n---\n", "b.md": "---\nid: b\nstages: [x]\n---\n"}),
        ("document", {"a.md": "a\n", "b.md": "b\n"}),
    ],
)
def test_variants_are_only_for_projected_kinds(tmp_path: Path, kind: str, files: dict[str, str]) -> None:
    with pytest.raises(BundleError, match=f"only skill and subagent assets declare variants; a {kind} asset"):
        load(
            tmp_path / "b",
            f'[[assets]]\nid = "x"\nkind = "{kind}"\n[assets.variants]\ncodex = "a.md"\nclaude-code = "b.md"\n',
            files,
        )


@pytest.mark.parametrize("target", ["vendor/x/.git/hooks/post-checkout", "vendor/.GIT/config", ".Git/x"])
def test_seeded_target_never_enters_a_git_directory(tmp_path: Path, target: str) -> None:
    with pytest.raises(BundleError, match="target may not be under devkit, Git"):
        load(
            tmp_path / "b",
            f'[[assets]]\nid = "h"\nkind = "document"\nseeded = true\nsource = "hook"\ntarget = "{target}"\n',
            {"hook": "#!/bin/sh\n"},
        )


def test_workflow_ids_are_unique_within_a_bundle(tmp_path: Path) -> None:
    flow = "---\nid: same\nstages: [a]\n---\n"
    with pytest.raises(BundleError, match="wb: workflow id 'same' is already declared by asset wa"):
        load(
            tmp_path / "b",
            '[[assets]]\nid = "wa"\nkind = "workflow"\nsource = "w/a.md"\n'
            '[[assets]]\nid = "wb"\nkind = "workflow"\nsource = "w/b.md"\n',
            {"w/a.md": flow, "w/b.md": flow},
        )


def test_deeply_nested_manifest_is_invalid(tmp_path: Path) -> None:
    root = tmp_path / "b"
    root.mkdir()
    (root / "bundle.toml").write_text("x = " + "[" * 5000 + "]" * 5000 + "\n")
    with pytest.raises(BundleError, match=r"cannot read bundle\.toml"):
        load_bundle(root)


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads unreadable files")
def test_unreadable_source_is_invalid_and_names_the_bundle(tmp_path: Path) -> None:
    root = write(
        tmp_path / "b",
        '[[assets]]\nid = "guide"\nkind = "instruction"\nsource = "guide.md"\n',
        {"guide.md": INSTRUCTION},
    )
    (root / "guide.md").chmod(0)
    try:
        with pytest.raises(BundleError, match=r"guide: cannot read source guide\.md") as info:
            load_bundle(root)
    finally:
        (root / "guide.md").chmod(0o644)
    assert info.value.target_files == (str(root.resolve()),)


def test_bundle_errors_name_the_bundle_directory(tmp_path: Path) -> None:
    root = write(tmp_path / "b", '[[assets]]\nid = "x"\nkind = "document"\nsource = "missing.md"\n', {})
    with pytest.raises(BundleError, match=r"source missing or nonregular: missing\.md") as info:
        load_bundle(root)
    assert info.value.target_files == (str(root.resolve()),)
    # The manifest instead of its directory: say what a source is.
    with pytest.raises(BundleError, match=r"bundle source must be a directory containing bundle\.toml") as info:
        load_bundle(root / "bundle.toml")
    assert info.value.target_files == (str((root / "bundle.toml").resolve()),)


@pytest.mark.parametrize("role", ["null", "true", "no"])
def test_projected_name_is_a_yaml_string(role: str) -> None:
    contract = read_contract(CONTRACT.format(role=f'"{role}"').encode(), "x", role)
    for agent in ("claude-code", "antigravity"):
        rendered = render_projection(agent, contract, "p")
        assert rendered is not None
        assert yaml.safe_load(rendered.decode().split("---\n")[1])["name"] == role


@pytest.fixture
def small(tmp_path: Path) -> Bundle:
    return load(tmp_path / "src", '[[assets]]\nid = "doc"\nkind = "document"\nsource = "a.md"\n', {"a.md": "a\n"})


def test_unusable_output_is_an_argument_error(small: Bundle, tmp_path: Path) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("x")
    for output in (blocker / "a.zip", blocker / "sub/a.zip"):
        with pytest.raises(ArgumentError, match="cannot create the archive") as info:
            build_bundle(small, output)
        assert info.value.target_files == ("--output",)
    existing = tmp_path / "out.zip"
    existing.write_bytes(b"")
    with pytest.raises(ArgumentError, match="archive already exists"):
        build_bundle(small, existing)


@pytest.mark.skipif(os.geteuid() == 0, reason="root writes into read-only directories")
def test_unwritable_output_directory_is_an_argument_error(small: Bundle, tmp_path: Path) -> None:
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o500)
    try:
        with pytest.raises(ArgumentError, match="cannot create the archive"):
            build_bundle(small, locked / "a.zip")
    finally:
        locked.chmod(0o700)
