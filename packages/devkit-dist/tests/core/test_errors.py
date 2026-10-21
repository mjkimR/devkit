from __future__ import annotations

from pathlib import Path

import pytest
from devkit.advisory import ActionMode, AdvisoryError, ExitCode
from devkit.core import ConfigError, ReceiptError, parse_receipt, read_project_config
from devkit_core.core import (
    ArgumentError,
    DeadlineExceededError,
    DevkitCoreError,
    FrontmatterError,
    GitError,
    LockHeldError,
    LockUnsupportedError,
    UnsafePathError,
    frontmatter,
    normalize_relpath,
    run_git,
)


@pytest.mark.parametrize(
    ("cls", "code", "mode"),
    [
        (FrontmatterError, "FRONTMATTER_INVALID", ActionMode.INPUT_ERROR),
        (ReceiptError, "RECEIPT_INVALID", ActionMode.MAINTENANCE),
        (ConfigError, "CONFIG_INVALID", ActionMode.INPUT_ERROR),
        (ArgumentError, "ARGUMENT_INVALID", ActionMode.INPUT_ERROR),
        (UnsafePathError, "PATH_UNSAFE", ActionMode.INPUT_ERROR),
        (GitError, "GIT_FAILED", ActionMode.MAINTENANCE),
        (DeadlineExceededError, "DEADLINE_EXCEEDED", ActionMode.DEFER),
        (LockHeldError, "LOCK_HELD", ActionMode.DEFER),
        (LockUnsupportedError, "LOCK_UNSUPPORTED", ActionMode.BLOCKED),
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


def test_distribution_facade_exports_existing_contracts_from_their_owners() -> None:
    from devkit import core
    from devkit_core import core as foundation

    assert all(hasattr(core, name) for name in core.__all__)
    assert core.Deadline is foundation.Deadline
    assert core.GitError is foundation.GitError
    assert core.run_git is foundation.run_git
    assert core.ReceiptError.__module__ == "devkit.core.errors"
