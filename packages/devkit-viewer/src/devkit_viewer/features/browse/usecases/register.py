"""Which repositories one ``devkit viewer serve`` serves, and under which IDs.

A repository is the top level of a Git work tree; its ID is its directory name. ``--repo`` names one,
``--scan`` adds each direct child that is a devkit repository (a Git top level holding ``.devkit/config.toml``),
and with neither the devkit project containing the current directory is served.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from devkit_core.base.usecase import BaseUseCase
from devkit_dist.features.project.repositories.project import git_toplevel

from devkit_viewer.features.browse.models.errors import NoRepositoryError, RepoDuplicateError, RepoInvalidError
from devkit_viewer.features.browse.models.repository import Repository

CONFIG = Path(".devkit") / "config.toml"


def _toplevel(path: Path) -> Path | None:
    """``path`` resolved when it is the top level of a Git work tree, else ``None``."""
    try:
        resolved = path.resolve()
    except (RuntimeError, OSError):
        return None
    if not resolved.is_dir():
        return None
    toplevel = git_toplevel(resolved)
    return resolved if toplevel is not None and toplevel.resolve() == resolved else None


def _is_devkit_repository(path: Path) -> bool:
    return (path / CONFIG).is_file()


class RegisterRepositoriesUseCase(BaseUseCase):
    def execute(self, repos: Iterable[str | Path], scans: Iterable[str | Path], cwd: Path) -> tuple[Repository, ...]:
        """The repositories to serve, sorted by ID.

        Raises ``RepoInvalidError`` for a ``--repo`` that is not a Git top level, ``RepoDuplicateError`` when two share
        a directory name, and ``NoRepositoryError`` when nothing is left to serve.
        """
        roots: list[Path] = []
        repos, scans = list(repos), list(scans)
        for value in repos:
            root = _toplevel(Path(value))
            if root is None:
                raise RepoInvalidError(
                    f"--repo {value}: not the top level of a Git work tree", target_files=[str(value)]
                )
            roots.append(root)
        for value in scans:
            directory = Path(value)
            if not directory.is_dir():
                continue
            for child in sorted(directory.iterdir()):
                root = _toplevel(child) if child.is_dir() else None
                if root is not None and _is_devkit_repository(root):
                    roots.append(root)
        if not repos and not scans:
            root = git_toplevel(cwd)
            if root is not None and _is_devkit_repository(root):
                roots.append(root.resolve())
        unique = list(dict.fromkeys(roots))
        if not unique:
            raise NoRepositoryError(
                "no repository to serve: "
                + ("no --scan child is a devkit repository" if scans else "not inside a devkit project")
            )
        by_id: dict[str, Path] = {}
        for root in unique:
            if root.name in by_id:
                raise RepoDuplicateError(
                    f"two repositories have the ID {root.name!r}", target_files=[str(by_id[root.name]), str(root)]
                )
            by_id[root.name] = root
        return tuple(Repository(id=repo_id, root=by_id[repo_id]) for repo_id in sorted(by_id))
