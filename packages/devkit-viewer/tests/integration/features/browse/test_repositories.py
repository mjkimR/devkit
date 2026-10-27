from __future__ import annotations

from pathlib import Path

import pytest
from viewer_fixtures import MakeRepo

from devkit_viewer.features.browse.models.errors import NoRepositoryError, RepoDuplicateError, RepoInvalidError
from devkit_viewer.features.browse.usecases.register import RegisterRepositoriesUseCase


def test_repos_sorted_by_id(make_repo: MakeRepo, tmp_path: Path) -> None:
    beta = make_repo("beta")
    alpha = make_repo("alpha", devkit=False)
    repos = RegisterRepositoriesUseCase().execute([beta, alpha], [], tmp_path)
    assert [(repo.id, repo.root) for repo in repos] == [("alpha", alpha), ("beta", beta)]


def test_scan_registers_devkit_repositories_only(make_repo: MakeRepo, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    one = make_repo("one", parent=workspace)
    make_repo("two", devkit=False, parent=workspace)
    (workspace / "three").mkdir()
    (workspace / "file.txt").write_text("x")
    assert [repo.root for repo in RegisterRepositoriesUseCase().execute([], [workspace], tmp_path)] == [one]


def test_default_is_the_current_devkit_project(make_repo: MakeRepo) -> None:
    one = make_repo("one", {"docs/a.md": "a\n"})
    assert [repo.root for repo in RegisterRepositoriesUseCase().execute([], [], one / "docs")] == [one]


def test_repo_and_scan_combine_without_duplicates(make_repo: MakeRepo, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    one = make_repo("one", parent=workspace)
    other = make_repo("other")
    assert [repo.id for repo in RegisterRepositoriesUseCase().execute([one, other], [workspace], tmp_path)] == [
        "one",
        "other",
    ]


def test_duplicate_ids_are_refused(make_repo: MakeRepo, tmp_path: Path) -> None:
    first = make_repo("same", parent=tmp_path / "a")
    second = make_repo("same", parent=tmp_path / "b")
    with pytest.raises(RepoDuplicateError) as caught:
        RegisterRepositoriesUseCase().execute([first, second], [], tmp_path)
    assert caught.value.code == "VIEWER_REPO_DUPLICATE"
    assert int(caught.value.exit_code) == 2


@pytest.mark.parametrize("target", ["subdirectory", "plain", "missing"])
def test_invalid_repos_are_refused(make_repo: MakeRepo, tmp_path: Path, target: str) -> None:
    root = make_repo("one", {"docs/a.md": "a\n"})
    (tmp_path / "plain").mkdir()
    path = {"subdirectory": root / "docs", "plain": tmp_path / "plain", "missing": tmp_path / "missing"}[target]
    with pytest.raises(RepoInvalidError) as caught:
        RegisterRepositoriesUseCase().execute([path], [], tmp_path)
    assert caught.value.code == "VIEWER_REPO_INVALID"


def test_scan_without_eligible_child_is_refused(make_repo: MakeRepo, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    make_repo("two", devkit=False, parent=workspace)
    with pytest.raises(NoRepositoryError) as caught:
        RegisterRepositoriesUseCase().execute([], [workspace], tmp_path)
    assert caught.value.code == "VIEWER_NO_REPOSITORY"
    assert "<" not in (caught.value.fix or "") and "uv run devkit viewer serve --repo ." in (caught.value.fix or "")


def test_outside_a_devkit_project_is_refused(make_repo: MakeRepo, tmp_path: Path) -> None:
    plain = make_repo("plain", devkit=False)
    for cwd in (tmp_path, plain):
        with pytest.raises(NoRepositoryError):
            RegisterRepositoriesUseCase().execute([], [], cwd)
