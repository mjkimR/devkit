"""Typed application entrypoint for each history command: one use case per operation."""

from __future__ import annotations

from pathlib import Path

from devkit_core.base.usecase import BaseUseCase

from ..models.errors import InputError
from ..models.records import PLAYBOOKS, HistoryResult
from ..repositories.config import destination
from ..repositories.github import Runner, run_gh
from ..repositories.local import read_record
from ..services import runs
from ..services.publication import GitHubHistory, publish, update


class _Remote:
    """Mixin of the operations on the history destination through ``gh``; the runner is injectable for offline tests."""

    def __init__(self, runner: Runner = run_gh) -> None:
        self.runner = runner

    def _history(self, root: Path, repository: str | None, branch: str | None) -> tuple[GitHubHistory, str]:
        """The destination resolved from the arguments, configuration and ``origin``, and its repository name."""
        repository, branch = destination(root.resolve(), repository, branch)
        return GitHubHistory(repository, branch, self.runner), repository


class InitHistory(_Remote, BaseUseCase):
    def execute(self, root: Path, *, repository: str | None, branch: str | None, authority: str) -> HistoryResult:
        history, _ = self._history(root, repository, branch)
        return history.initialize(authority)


class StartRun(BaseUseCase):
    def execute(
        self,
        root: Path,
        *,
        repository: str | None,
        playbook: str,
        scope: str,
        into: Path,
        report: Path,
        zone: str | None,
        supersedes: tuple[str, ...],
        prior_runs: tuple[str, ...],
    ) -> HistoryResult:
        root = root.resolve()
        repository, _ = destination(root, repository, None)
        return runs.start(
            root,
            repository=repository,
            playbook=playbook,
            scope=scope,
            into=into,
            report=report,
            zone=zone,
            supersedes=supersedes,
            prior_runs=prior_runs,
        )


class FinishRun(BaseUseCase):
    def execute(
        self,
        run: Path,
        *,
        outcome: str,
        result: str | None,
        report: Path | None,
        applied_commits: tuple[str, ...],
        follow_ups: tuple[str, ...],
        files: tuple[Path, ...],
    ) -> HistoryResult:
        return runs.finish(
            run.resolve(),
            outcome=outcome,
            result=result,
            report=report,
            applied_commits=applied_commits,
            follow_ups=follow_ups,
            files=files,
        )


class PublishRun(_Remote, BaseUseCase):
    def execute(
        self,
        root: Path,
        run: Path,
        *,
        authority: str,
        repository: str | None,
        branch: str | None,
        files: tuple[Path, ...],
    ) -> HistoryResult:
        history, repository = self._history(root, repository, branch)
        return publish(history, run.resolve(), authority, files, repository)


class UpdateRun(_Remote, BaseUseCase):
    def execute(
        self, root: Path, run: Path, *, authority: str, integration_state: str, applied_commits: tuple[str, ...]
    ) -> HistoryResult:
        record = read_record(run.resolve())
        if not isinstance(record.get("destination"), str) or "#" not in record["destination"]:
            raise InputError("A published destination is required for amendments")
        repository, branch = record["destination"].split("#", 1)
        history, _ = self._history(root, repository, branch)
        return update(history, run.resolve(), authority, integration_state, applied_commits)


class ListRuns(_Remote, BaseUseCase):
    def execute(
        self,
        root: Path,
        *,
        playbook: str,
        source_sha: str | None,
        outcome: str | None,
        include_superseded: bool,
        limit: int,
        repository: str | None,
        branch: str | None,
    ) -> HistoryResult:
        history, _ = self._history(root, repository, branch)
        if playbook not in PLAYBOOKS or limit < 1:
            raise InputError("Name a supported playbook and a positive limit")
        return history.listing(playbook, source_sha, outcome, include_superseded, limit)


class GetRunFile(_Remote, BaseUseCase):
    def execute(
        self, root: Path, *, run_id: str, file: str, repository: str | None, branch: str | None
    ) -> HistoryResult:
        history, _ = self._history(root, repository, branch)
        return history.get(run_id, file)
