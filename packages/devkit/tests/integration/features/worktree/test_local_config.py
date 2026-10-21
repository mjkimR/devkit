from pathlib import Path

import devkit_agt.features.worktree.usecases.lifecycle as lifecycle
import pytest
from devkit_agt.features.worktree import attach, locate, start
from devkit_agt.features.worktree.models.errors import LocalCopyError, NestedError
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.repositories.local_config import LOCAL_CONFIG_PATH
from testsupport.rules import git, init_repo, write


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = init_repo(tmp_path / "repo").resolve()
    write(root, ".gitignore", ".devkit/config.local.toml\n")
    write(root, "specs/demo/spec.md", "# Demo\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "fixture")
    return root


def test_copy_before_setup_and_independent_snapshot(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = write(repo, LOCAL_CONFIG_PATH, '# personal\n[execution]\nenvironment="cloud"\n')
    source.chmod(0o600)
    expected = source.read_bytes()

    def prepare(path, setup, project, notices, *, before_step=None):
        copied = path / LOCAL_CONFIG_PATH
        assert copied.read_bytes() == expected
        assert copied.stat().st_mode & 0o777 == 0o600
        return setup, True

    monkeypatch.setattr(lifecycle, "_prepare", prepare)
    created = start(locate(repo), "dev-copy", project=Path("."), setup="example")
    destination = created.path / LOCAL_CONFIG_PATH
    source.write_text('[execution]\nenvironment="local"\n')
    assert destination.read_bytes() == expected
    destination.unlink()
    assert source.exists()
    attached = attach(locate(repo), "dev-copy", source="dev-copy", unit="specs/demo", project=Path("."))
    assert not (attached.path / LOCAL_CONFIG_PATH).exists()
    destination.write_bytes(expected)
    attach(locate(repo), "dev-copy", source="dev-copy", unit="specs/demo", project=Path("."))
    assert destination.read_bytes() == expected
    with pytest.raises(NestedError):
        start(locate(created.path), "dev-nested")


def test_absent_source_and_direct_git_worktree_have_no_copy(repo: Path) -> None:
    created = start(locate(repo), "dev-empty")
    assert not (created.path / LOCAL_CONFIG_PATH).exists()
    write(repo, LOCAL_CONFIG_PATH, '[execution]\nenvironment="cloud"\n')
    raw = repo.parent / "raw"
    git(repo, "worktree", "add", "-qb", "raw", str(raw))
    assert not (raw / LOCAL_CONFIG_PATH).exists()


@pytest.mark.parametrize("value", ["broken = [", "[rules]\nx=false"])
def test_invalid_source_fails_before_creation(repo: Path, value: str) -> None:
    write(repo, LOCAL_CONFIG_PATH, value)
    with pytest.raises(ConfigError):
        start(locate(repo), "dev-invalid")
    assert "dev-invalid" not in git(repo, "branch", "--list")
    assert not (repo.parent / "repo-wt-dev-invalid").exists()


def test_copy_failure_retains_checkout_without_setup(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = write(repo, LOCAL_CONFIG_PATH, '[execution]\nenvironment="cloud"\n')
    original = Path.chmod

    def fail(path, mode, *args, **kwargs):
        if path.name == "config.local.toml" and path != source:
            raise OSError("injected mode failure")
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "chmod", fail)
    monkeypatch.setattr(lifecycle, "_prepare", lambda *args: pytest.fail("setup must not run"))
    with pytest.raises(LocalCopyError) as caught:
        start(locate(repo), "dev-failure")
    assert (repo.parent / "repo-wt-dev-failure").is_dir()
    assert str(source) in caught.value.message
    assert "Deliberately copy" in (caught.value.fix or "")


def test_nested_project_helper_uses_corresponding_path(tmp_path: Path) -> None:
    base, target = tmp_path / "base", tmp_path / "target"
    project = Path("nested/project")
    source = write(base, str(project / LOCAL_CONFIG_PATH), "[mcp]\nregister=false\n")
    captured = lifecycle._local_snapshot(base, project)
    lifecycle._copy_local_snapshot(target, project, captured)
    assert (target / project / LOCAL_CONFIG_PATH).read_bytes() == source.read_bytes()


def test_copy_rejects_symlinked_destination_parent_before_setup(
    repo: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    write(repo, LOCAL_CONFIG_PATH, '[execution]\nenvironment="cloud"\n')
    outside = tmp_path / "outside"
    outside.mkdir()
    original = lifecycle._add

    def add(base, path, branch, **kwargs):
        original(base, path, branch, **kwargs)
        (path / ".devkit").symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(lifecycle, "_add", add)
    monkeypatch.setattr(lifecycle, "_prepare", lambda *args: pytest.fail("setup must not run"))
    with pytest.raises(LocalCopyError, match="parent is a symlink"):
        start(locate(repo), "dev-symlink")
    assert not (outside / "config.local.toml").exists()
    assert (repo.parent / "repo-wt-dev-symlink").is_dir()


def test_copy_rejects_escaping_project_path(tmp_path: Path) -> None:
    root = tmp_path / "checkout"
    root.mkdir()
    with pytest.raises(LocalCopyError, match="escapes"):
        lifecycle._copy_local_snapshot(root, Path("../outside"), (tmp_path / "source", b"", 0o600))
    assert not (tmp_path / "outside").exists()
