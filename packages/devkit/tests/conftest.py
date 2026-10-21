from collections.abc import Callable
from pathlib import Path

import pytest
from testsupport.rules import git

Write = Callable[[str, str], Path]


@pytest.fixture(autouse=True)
def _no_output_options_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """``DEVKIT_QUIET``/``VERBOSE``/``STRICT`` from the shell, or from ``devkit run -q``, must not change any test."""
    for name in ("DEVKIT_QUIET", "DEVKIT_VERBOSE", "DEVKIT_STRICT"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def refuse_deleting(tmp_path: Path) -> Callable[[Path, str], Path]:
    """Make Git refuse to delete a branch of a repository, as ``git branch -d`` can after ``finish`` merged.

    A ``reference-transaction`` hook aborts the deletion; the call returns the hook, and deleting it lifts the refusal.
    """

    def install(repo: Path, branch: str) -> Path:
        hooks = tmp_path / "hooks"
        hooks.mkdir(exist_ok=True)
        hook = hooks / "reference-transaction"
        hook.write_text(
            '#!/bin/sh\n[ "$1" = prepared ] || exit 0\nwhile read old new ref; do\n'
            f'  [ "$ref" = refs/heads/{branch} ] && [ -z "$(echo "$new" | tr -d 0)" ] && exit 1\n'
            "done\nexit 0\n"
        )
        hook.chmod(0o755)
        git(repo, "config", "core.hooksPath", str(hooks))
        return hook

    return install
