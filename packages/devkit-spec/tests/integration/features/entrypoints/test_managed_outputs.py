from __future__ import annotations

from pathlib import Path

import pytest
from devkit_dist.base.errors import ReceiptError
from spec_support.entrypoints import BUNDLE, documents, fixture, managed_receipt
from spec_support.types import Write

from devkit_spec.features.entrypoints import classify_boundary, derive, load_bundle
from devkit_spec.features.entrypoints.repositories.managed import load_managed_outputs


def _derive_boundaries(root: Path, write: Write, *paths: str) -> tuple[set[str], dict[str, str]]:
    fixture(write)
    write(f"{BUNDLE}/tasks.md", "- [x] task\n  - _Boundary: " + ", ".join(paths) + "\n")
    pairs, skipped = derive(root, load_bundle(root, BUNDLE), documents(root))
    return {pair.code for pair in pairs}, {item.value: str(item.reason) for item in skipped}


def test_known_outputs_are_excluded_without_receipt(workspace: Path, write: Write) -> None:
    paths = (".devkit/managed/", ".devkit/managed/docs/rule.py", ".devkit/installation.json")
    candidates, skipped = _derive_boundaries(workspace, write, *paths, "src/pkg/")
    assert candidates == {"src/pkg"}
    assert {path: skipped[path] for path in paths} == dict.fromkeys(paths, "managed-output")
    # Shared classification still supplies these writes to scope collection.
    assert [classify_boundary(path) for path in paths] == [(path.rstrip("/"), None) for path in paths]


def test_receipt_distinguishes_generated_directories_and_authored_siblings(workspace: Path, write: Write) -> None:
    managed_receipt(write, ".claude/skills/generated.md", ".agents/generated.md", "src/projected.py")
    write(".claude/skills/generated.md", "generated")
    write(".agents/generated.md", "generated")
    write(".agents/custom.md", "authored")
    write("src/custom.py", "authored")
    write(".gitignore", "src/custom.py\n")
    boundaries = (
        ".claude/",
        ".agents/",
        ".agents/generated.md",
        ".agents/custom.md",
        "src/custom.py",
        "src/projected.py",
    )
    candidates, skipped = _derive_boundaries(workspace, write, *boundaries)
    assert candidates == {".agents", ".agents/custom.md", "src/custom.py"}
    assert skipped[".claude/"] == skipped[".agents/generated.md"] == skipped["src/projected.py"] == "managed-output"


def test_seeded_paths_and_host_directories_without_ownership_remain_authored(workspace: Path, write: Write) -> None:
    managed_receipt(write, seeded=("src/seeded.py",))
    write("src/seeded.py", "project-owned")
    write(".claude/custom.md", "authored")
    candidates, _ = _derive_boundaries(workspace, write, "src/seeded.py", ".claude/")
    assert candidates == {"src/seeded.py", ".claude"}


def test_unowned_directory_symlink_is_not_traversed_for_ownership(workspace: Path, write: Write) -> None:
    managed_receipt(write, ".claude/skills/generated.md")
    write("project/skills/generated.md", "authored")
    (workspace / ".claude").symlink_to(workspace / "project", target_is_directory=True)
    assert not load_managed_outputs(workspace).contains(".claude")


def test_malformed_present_receipt_is_not_treated_as_absent(workspace: Path, write: Write) -> None:
    write(".devkit/installation.json", "{}")
    with pytest.raises(ReceiptError) as raised:
        _derive_boundaries(workspace, write, "src/pkg/")
    assert raised.value.code == "RECEIPT_INVALID"
