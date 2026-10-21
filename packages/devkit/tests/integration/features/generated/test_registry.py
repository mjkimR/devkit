"""The registry of generated artifacts: patterns, built-in entries and ``.devkit/generated.toml``."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.generated import GeneratedConfigError, builtin_artifacts, load_registry, matches
from testsupport.rules import write


def configure(root: Path, table: str) -> None:
    write(root, ".devkit/generated.toml", table)


@pytest.mark.parametrize(
    ("pattern", "path", "expected"),
    [
        ("uv.lock", "uv.lock", True),
        ("uv.lock", "sub/uv.lock", False),
        ("*.lock", "uv.lock", True),
        ("*.lock", "a/uv.lock", False),
        ("packages/*/pyproject.toml", "packages/devkit/pyproject.toml", True),
        ("packages/*/pyproject.toml", "packages/a/b/pyproject.toml", False),
        ("gen/**", "gen/a.txt", True),
        ("gen/**", "gen/a/b/c.txt", True),
        ("gen/**", "gen", True),
        ("**/out.txt", "out.txt", True),
        ("**/out.txt", "a/b/out.txt", True),
        ("a/**/z.txt", "a/z.txt", True),
        ("a/**/z.txt", "a/b/c/z.txt", True),
        ("a/**/z.txt", "b/z.txt", False),
        ("file?.[ch]", "file1.c", True),
        ("file?.[ch]", "file12.c", False),
    ],
)
def test_patterns_match_within_segments_and_across_them_only_with_double_star(
    pattern: str, path: str, expected: bool
) -> None:
    assert matches(pattern, path) is expected


def test_the_receipt_is_built_in_and_optional(tmp_path: Path) -> None:
    receipt = load_registry(tmp_path).get("devkit-receipt")
    assert receipt is not None and receipt.builtin and receipt.optional
    assert receipt.paths == (".devkit/installation.json",)
    assert "devkit-receipt" in builtin_artifacts()
    assert receipt.shell.endswith("-P -m devkit_dist sync")


def test_a_project_table_changes_only_the_fields_it_sets_and_can_drop_a_builtin(tmp_path: Path) -> None:
    configure(
        tmp_path,
        '[artifacts.uv-lock]\npaths = ["uv.lock"]\ncommand = "uv lock"\n\n'
        '[artifacts.devkit-receipt]\nafter = ["uv-lock"]\nseed = "theirs"\n',
    )
    registry = load_registry(tmp_path)
    assert [item.id for item in registry.artifacts] == ["uv-lock", "devkit-receipt"]
    receipt = registry.get("devkit-receipt")
    assert receipt is not None and receipt.seed == "theirs" and receipt.after == ("uv-lock",)
    assert receipt.paths == (".devkit/installation.json",) and receipt.builtin
    assert registry.closure(["uv-lock"]) == registry.artifacts

    configure(tmp_path, "[artifacts.devkit-receipt]\nenabled = false\n")
    assert load_registry(tmp_path).artifacts == ()


@pytest.mark.parametrize(
    ("table", "message"),
    [
        ("artifact = {}\n", "unknown fields: ['artifact']"),
        ('[artifacts.x]\npaths = ["a"]\ncommand = "c"\nseeds = "ours"\n', "unknown fields: ['seeds']"),
        ('[artifacts.x]\npaths = ["a"]\n', "missing command"),
        ('[artifacts.x]\ncommand = "c"\n', "missing paths"),
        ('[artifacts.x]\npaths = ["../a"]\ncommand = "c"\n', "not a relative"),
        ('[artifacts.x]\npaths = ["/a"]\ncommand = "c"\n', "not a relative"),
        ('[artifacts.x]\npaths = "a"\ncommand = "c"\n', "paths must be an array of strings"),
        ('[artifacts.x]\npaths = ["a"]\ncommand = "c"\nseed = "base"\n', 'seed must be "ours" or "theirs"'),
        ('[artifacts.X]\npaths = ["a"]\ncommand = "c"\n', "artifact id 'X'"),
        ('[artifacts.x]\npaths = ["a"]\ncommand = "c"\nafter = ["y"]\n', "unknown or disabled"),
        (
            '[artifacts.x]\npaths = ["a"]\ncommand = "c"\nafter = ["y"]\n'
            '[artifacts.y]\npaths = ["b"]\ncommand = "c"\nafter = ["x"]\n',
            "cycle",
        ),
    ],
)
def test_a_malformed_table_is_generated_config_invalid(tmp_path: Path, table: str, message: str) -> None:
    configure(tmp_path, table)
    with pytest.raises(GeneratedConfigError, match=message.replace("[", r"\[").replace("]", r"\]")) as caught:
        load_registry(tmp_path)
    assert caught.value.code == "GENERATED_CONFIG_INVALID"
    assert caught.value.target_files == (".devkit/generated.toml",)


def test_the_project_file_is_optional_and_config_toml_is_not_read(tmp_path: Path) -> None:
    write(tmp_path, ".devkit/config.toml", '[generated.artifacts.x]\npaths = ["a"]\ncommand = "c"\n')
    assert [item.id for item in load_registry(tmp_path).artifacts] == ["devkit-receipt"]


def test_a_path_two_artifacts_own_is_refused(tmp_path: Path) -> None:
    configure(
        tmp_path,
        '[artifacts.a]\npaths = ["gen/**"]\ncommand = "c"\n[artifacts.b]\npaths = ["gen/*.txt"]\ncommand = "c"\n',
    )
    registry = load_registry(tmp_path)
    assert registry.owner("gen/x.bin") is not None
    with pytest.raises(GeneratedConfigError, match="owned by more than one artifact: a, b"):
        registry.owner("gen/x.txt")
