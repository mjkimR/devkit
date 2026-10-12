from __future__ import annotations

from pathlib import Path

import pytest
from devkit.advisory import ActionMode, AdvisoryError, ExitCode
from devkit.core import (
    ConfigError,
    DevkitCoreError,
    FrontmatterError,
    GitError,
    ReceiptError,
    UnsafePathError,
    frontmatter,
    normalize_relpath,
    parse_receipt,
    read_project_config,
    run_git,
)


@pytest.mark.parametrize(
    ("cls", "code", "mode"),
    [
        (FrontmatterError, "FRONTMATTER_INVALID", ActionMode.INPUT_ERROR),
        (ReceiptError, "RECEIPT_INVALID", ActionMode.MAINTENANCE),
        (ConfigError, "CONFIG_INVALID", ActionMode.INPUT_ERROR),
        (UnsafePathError, "PATH_UNSAFE", ActionMode.INPUT_ERROR),
        (GitError, "GIT_FAILED", ActionMode.MAINTENANCE),
    ],
)
def test_core_errors_are_advisories_with_stable_codes(cls: type[DevkitCoreError], code: str, mode: ActionMode) -> None:
    error = cls("x")
    assert isinstance(error, AdvisoryError) and not isinstance(error, ValueError)
    assert (error.code, error.mode, error.exit_code) == (code, mode, ExitCode.ERROR)


def test_raised_core_errors_carry_their_codes(tmp_path: Path) -> None:
    with pytest.raises(FrontmatterError) as fm:
        frontmatter.parse("---\na: [\n---\n")
    assert fm.value.code == "FRONTMATTER_INVALID"
    with pytest.raises(UnsafePathError) as unsafe:
        normalize_relpath("../x")
    assert unsafe.value.code == "PATH_UNSAFE"
    with pytest.raises(ReceiptError) as receipt:
        parse_receipt(b"{")
    assert receipt.value.target_files == (".devkit/installation.json",) and receipt.value.fix
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/config.toml").write_text("[x", encoding="utf-8")
    with pytest.raises(ConfigError) as config:
        read_project_config(tmp_path)
    assert config.value.target_files == (".devkit/config.toml",)
    with pytest.raises(GitError) as git:
        run_git(tmp_path, "rev-parse", "--show-toplevel")
    assert git.value.code == "GIT_FAILED" and git.value.returncode not in (None, 0)


def test_git_error_forwards_advisory_fields() -> None:
    error = GitError("not a repo", command=("git",), returncode=128, input_error=True, fix="Pass -w")
    assert (error.mode, error.fix, error.returncode, error.command) == (
        ActionMode.INPUT_ERROR,
        "Pass -w",
        128,
        ("git",),
    )
