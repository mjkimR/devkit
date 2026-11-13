"""Real Git/filesystem contract of the optional context-link shell helper."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).parents[3]
    / "src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/scripts/link-impeccable-context.sh"
)
ENTRIES = ("PRODUCT.md", "DESIGN.md", ".impeccable")
PATTERNS = b"/PRODUCT.md\n/DESIGN.md\n/.impeccable\n"
SHELLS = ["sh", *(["dash"] if shutil.which("dash") else [])]


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE).strip()


def repository(tmp_path: Path, source_name: str = "docs/materials/impeccable") -> tuple[Path, Path]:
    root = tmp_path / "repo with spaces"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "Context test")
    git(root, "config", "user.email", "context@example.invalid")
    source = root / source_name
    source.mkdir(parents=True)
    (source / "PRODUCT.md").write_text("Tracked product context.\n")
    (source / "DESIGN.md").write_text("Tracked design context.\n")
    (source / ".impeccable").mkdir()
    (source / ".impeccable/config.json").write_text("{}\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "fixture")
    return root, source


def run(
    root: Path, *args: str, shell: str = "sh", extra_env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, **(extra_env or {})}
    return subprocess.run([shell, str(SCRIPT), *args], cwd=root, env=env, text=True, capture_output=True, timeout=15)


def tree(root: Path) -> dict[str, tuple[int, int, bytes | str]]:
    return {
        path.relative_to(root).as_posix(): (
            path.lstat().st_mode,
            path.lstat().st_mtime_ns,
            os.readlink(path) if path.is_symlink() else path.read_bytes() if path.is_file() else b"",
        )
        for path in root.rglob("*")
    }


@pytest.mark.parametrize("shell", SHELLS)
def test_links_are_relative_idempotent_and_checked_without_writes(tmp_path: Path, shell: str) -> None:
    root, source = repository(tmp_path)
    before_head = git(root, "rev-parse", "HEAD")
    first = run(root, shell=shell)
    assert first.returncode == 0, first
    assert "code=LINK_CLEAN exit=0" in first.stdout
    for entry in ENTRIES:
        assert (root / entry).is_symlink()
        assert os.readlink(root / entry) == f"docs/materials/impeccable/{entry}"
        assert (root / entry).resolve() == source / entry
        assert f"[CONTEXT_LINK: {entry} code=LINK_CREATED action=NONE]" in first.stdout
    exclude = root / ".git/info/exclude"
    assert exclude.read_bytes().endswith(PATTERNS)
    assert git(root, "check-ignore", "PRODUCT.md", ".impeccable") == "PRODUCT.md\n.impeccable"
    before = tree(root)
    repeated = run(root, shell=shell)
    checked = run(root, "--check", shell=shell)
    assert repeated.returncode == checked.returncode == 0
    assert tree(root) == before
    assert git(root, "rev-parse", "HEAD") == before_head
    assert all("LINK_OK" in line for line in checked.stdout.splitlines() if line.startswith("[CONTEXT_LINK:"))


@pytest.mark.parametrize("shell", SHELLS)
def test_check_reports_every_unresolved_state_and_preserves_root(tmp_path: Path, shell: str) -> None:
    root, source = repository(tmp_path)
    assert run(root).returncode == 0
    (root / "PRODUCT.md").unlink()
    (root / "PRODUCT.md").write_bytes((source / "PRODUCT.md").read_bytes())
    (root / "DESIGN.md").unlink()
    (root / "DESIGN.md").symlink_to("absent")
    (root / ".impeccable").unlink()
    (root / ".impeccable").mkdir()
    (root / ".impeccable/config.json").write_text("different\n")
    before = tree(root)
    checked = run(root, "--check", shell=shell)
    assert checked.returncode == 1
    assert "PRODUCT.md code=LINK_REPLACED content=equal" in checked.stdout
    assert "DESIGN.md code=LINK_DANGLING" in checked.stdout
    assert ".impeccable code=LINK_REPLACED content=differs" in checked.stdout
    assert tree(root) == before
    linked = run(root, shell=shell)
    assert linked.returncode == 1
    assert tree(root) == before


def test_source_absence_stale_missing_wrong_and_type_mismatch(tmp_path: Path) -> None:
    root, source = repository(tmp_path)
    (source / "DESIGN.md").unlink()
    (source / ".impeccable/config.json").unlink()
    (source / ".impeccable").rmdir()
    (root / "DESIGN.md").symlink_to("absent")
    (root / ".impeccable").write_text("occupied")
    before = tree(root)
    result = run(root, "--check")
    assert result.returncode == 1
    assert "PRODUCT.md code=LINK_MISSING" in result.stdout
    assert "DESIGN.md code=LINK_STALE" in result.stdout
    assert ".impeccable code=LINK_OCCUPIED" in result.stdout
    assert "code=EXCLUDE_MISSING" in result.stdout
    assert tree(root) == before
    result = run(root)
    assert result.returncode == 1
    assert (root / "PRODUCT.md").is_symlink()  # Eligible entries progress despite occupied peers.
    (root / "PRODUCT.md").unlink()
    (root / "PRODUCT.md").symlink_to(str(source / "PRODUCT.md"))
    assert "PRODUCT.md code=LINK_WRONG_TARGET" in run(root, "--check").stdout
    (root / "PRODUCT.md").unlink()
    (root / "PRODUCT.md").mkdir()
    assert "PRODUCT.md code=LINK_REPLACED content=type_mismatch" in run(root, "--check").stdout
    (root / "DESIGN.md").unlink()
    assert "DESIGN.md code=LINK_ABSENT" in run(root, "--check").stdout


@pytest.mark.parametrize("shell", SHELLS)
def test_newline_foreign_target_is_distinct_with_native_and_gnu_ls(tmp_path: Path, shell: str) -> None:
    root, source = repository(tmp_path, "docs/source -> context")
    (source / "PRODUCT.md\n").write_text("foreign")
    (root / "PRODUCT.md").symlink_to("docs/source -> context/PRODUCT.md\n")
    util_dirs: list[Path | None] = [None]
    if gnu_ls := shutil.which("gls"):
        utilities = tmp_path / "gnu-utils"
        utilities.mkdir()
        (utilities / "ls").symlink_to(gnu_ls)
        util_dirs.append(utilities)
    for utilities in util_dirs:
        env = {"PATH": f"{utilities}:{os.environ['PATH']}"} if utilities else {}
        before = tree(root)
        result = run(root, "--check", "docs/source -> context", shell=shell, extra_env=env)
        assert result.returncode == 1
        assert "PRODUCT.md code=LINK_WRONG_TARGET" in result.stdout
        assert "foreign" not in result.stdout
        assert len(result.stdout.splitlines()) == 7
        assert tree(root) == before


def test_tracked_root_is_preserved_and_source_content_never_changes(tmp_path: Path) -> None:
    root, source = repository(tmp_path)
    (root / "PRODUCT.md").write_text("tracked root\n")
    git(root, "add", "PRODUCT.md")
    git(root, "commit", "-qm", "root context")
    source_before = tree(source)
    result = run(root)
    assert result.returncode == 1
    assert "PRODUCT.md code=LINK_TRACKED action=UNTRACK_MANUALLY" in result.stdout
    assert (root / "PRODUCT.md").read_text() == "tracked root\n"
    assert tree(source) == source_before
    assert git(root, "ls-files", "PRODUCT.md") == "PRODUCT.md"


def test_linked_worktree_links_its_own_source_and_shared_exclude(tmp_path: Path) -> None:
    root, _ = repository(tmp_path)
    linked = tmp_path / "linked worktree"
    git(root, "worktree", "add", "-qb", "other", str(linked))
    # This fixture's worktree lifecycle is local Git only, without devkit or hooks.
    result = run(linked / "docs")
    assert result.returncode == 0, result
    assert os.readlink(linked / "PRODUCT.md") == "docs/materials/impeccable/PRODUCT.md"
    assert (linked / "PRODUCT.md").resolve() == linked / "docs/materials/impeccable/PRODUCT.md"
    assert not (root / "PRODUCT.md").exists()
    assert (root / ".git/info/exclude").read_bytes().endswith(PATTERNS)


@pytest.mark.parametrize("args", [("--bad",), ("one", "two"), ("--check", "--bad"), ("",)])
def test_invalid_arguments_do_not_mutate(tmp_path: Path, args: tuple[str, ...]) -> None:
    root, _ = repository(tmp_path)
    before = tree(root)
    result = run(root, *args)
    assert result.returncode == 2
    assert tree(root) == before


def test_source_preflight_bounds_paths_and_accepts_explicit_dash_path(tmp_path: Path) -> None:
    root, source = repository(tmp_path, "-context")
    assert run(root, "--", "-context").returncode == 0
    assert run(root, "--check", "./docs/../-context").returncode == 2  # Missing physical parent.
    (root / "docs").mkdir()
    assert run(root, "--check", "./docs/../-context").returncode == 0
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "escape").symlink_to(outside, target_is_directory=True)
    for name in ("escape", ".", ".git", "missing"):
        before = tree(root)
        assert run(root, name).returncode == 2
        assert tree(root) == before
    (source / "PRODUCT.md").unlink()
    (source / "PRODUCT.md").symlink_to(outside / "secret")
    before = tree(root)
    assert run(root, "--", "-context").returncode == 2
    assert tree(root) == before
    git(root, "config", "core.symlinks", "false")
    assert "LINK_SYMLINKS_DISABLED" in run(root, "--", "-context").stdout
    assert "LINK_NOT_WORKTREE" in run(tmp_path).stdout


def test_source_control_characters_and_wrong_types_refuse_before_links(tmp_path: Path) -> None:
    root, source = repository(tmp_path)
    bad_source = root / "line\nbreak"
    source.rename(bad_source)
    before = tree(root)
    assert "LINK_SOURCE_INVALID" in run(root, str(bad_source)).stdout
    assert tree(root) == before
    bad_source.rename(source)
    (source / "PRODUCT.md").unlink()
    (source / "PRODUCT.md").mkdir()
    before = tree(root)
    assert run(root).returncode == 2
    assert tree(root) == before


def test_excludes_preserve_unterminated_bytes_deduplicate_and_respect_lock(tmp_path: Path) -> None:
    root, _ = repository(tmp_path)
    exclude = root / ".git/info/exclude"
    exclude.write_bytes(b"# keep\n/DESIGN.md\nunrelated")
    lock = Path(f"{exclude}.impeccable-context.lock")
    lock.mkdir()
    before = tree(root)
    assert "LINK_EXCLUDE_BUSY" in run(root).stdout
    assert tree(root) == before
    lock.rmdir()
    assert run(root).returncode == 0
    assert exclude.read_bytes() == b"# keep\n/DESIGN.md\nunrelated\n/PRODUCT.md\n/.impeccable\n"
    before = tree(root)
    assert run(root).returncode == 0
    assert tree(root) == before


def test_io_failure_keeps_completed_link_and_releases_only_owned_lock(tmp_path: Path) -> None:
    root, _ = repository(tmp_path)
    utilities = tmp_path / "fault-utils"
    utilities.mkdir()
    ln = utilities / "ln"
    ln.write_text('#!/bin/sh\ncase "$4" in ./DESIGN.md) exit 1 ;; esac\nexec /bin/ln "$@"\n')
    ln.chmod(0o755)
    result = run(root, extra_env={"PATH": f"{utilities}:{os.environ['PATH']}"})
    assert result.returncode == 2
    assert "PRODUCT.md code=LINK_CREATED" in result.stdout
    assert "LINK_IO_FAILED" in result.stdout
    assert (root / "PRODUCT.md").is_symlink()
    assert not (root / "DESIGN.md").exists()
    assert not Path(f"{root / '.git/info/exclude'}.impeccable-context.lock").exists()


def test_replaced_directory_comparison_disables_external_diff(tmp_path: Path) -> None:
    root, source = repository(tmp_path)
    shutil.copytree(source / ".impeccable", root / ".impeccable")
    marker = root / "external-diff-ran"
    git(root, "config", "diff.external", f"touch {marker}")
    before = tree(root)
    result = run(root, "--check")
    assert ".impeccable code=LINK_REPLACED content=equal" in result.stdout
    assert tree(root) == before
    assert not marker.exists()


def test_file_difference_and_failed_directory_inspection_are_distinct(tmp_path: Path) -> None:
    root, source = repository(tmp_path)
    (root / "PRODUCT.md").write_text("different product\n")
    shutil.copytree(source / ".impeccable", root / ".impeccable")
    utilities = tmp_path / "diagnostic-utils"
    utilities.mkdir()
    real_git = shutil.which("git")
    assert real_git
    wrapper = utilities / "git"
    wrapper.write_text(
        '#!/bin/sh\ncase "$*" in *diff*--no-index*) printf "cannot read nested file\\n" >&2; exit 1;; esac\n'
        'exec "$CONTEXT_TEST_GIT" "$@"\n'
    )
    wrapper.chmod(0o755)
    before = tree(root)
    result = run(root, "--check", extra_env={"PATH": f"{utilities}:{os.environ['PATH']}", "CONTEXT_TEST_GIT": real_git})
    assert result.returncode == 2
    assert "PRODUCT.md code=LINK_REPLACED content=differs" in result.stdout
    assert "code=LINK_INSPECTION_FAILED exit=2" in result.stdout
    assert ".impeccable code=LINK_REPLACED" not in result.stdout
    assert tree(root) == before
