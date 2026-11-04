"""Typed application entrypoint for each history command."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from devkit_core.base.usecase import BaseUseCase

from ..models.errors import InputError
from ..models.records import PLAYBOOKS, HistoryResult
from ..repositories.config import destination
from ..repositories.github import Runner, run_gh
from ..repositories.local import read_record
from ..services import runs
from ..services.publication import GitHubHistory, publish, update


@dataclass(frozen=True)
class HistoryRequest:
    operation: Literal["init", "start", "finish", "publish", "update", "list", "get"]
    root: Path
    repository: str | None = None
    branch: str | None = None
    authority: str = ""
    playbook: str = "weekly-report"
    scope: str = ""
    into: Path = Path(".")
    report: Path | None = None
    timezone: str | None = None
    supersedes: tuple[str, ...] = ()
    prior_runs: tuple[str, ...] = ()
    run: Path = Path(".")
    outcome: str = "completed"
    result: str | None = None
    applied_commits: tuple[str, ...] = ()
    follow_ups: tuple[str, ...] = ()
    files: tuple[Path, ...] = ()
    integration_state: str = ""
    source_sha: str | None = None
    outcome_filter: str | None = None
    include_superseded: bool = False
    limit: int = 20
    run_id: str = ""
    file: str = "record.json"


class HistoryOperation(BaseUseCase):
    def __init__(self, runner: Runner = run_gh) -> None:
        self.runner = runner

    def execute(self, request: HistoryRequest) -> HistoryResult:
        root = request.root.resolve()
        if request.operation == "finish":
            return runs.finish(
                request.run.resolve(),
                outcome=request.outcome,
                result=request.result,
                report=request.report,
                applied_commits=request.applied_commits,
                follow_ups=request.follow_ups,
                files=request.files,
            )
        repository, branch = request.repository, request.branch
        if request.operation == "update":
            record = read_record(request.run.resolve())
            if not isinstance(record.get("destination"), str) or "#" not in record["destination"]:
                raise InputError("A published destination is required for amendments")
            repository, branch = record["destination"].split("#", 1)
        repository, branch = destination(root, repository, branch)
        if request.operation == "start":
            if request.report is None:
                raise InputError("start requires a report path")
            return runs.start(
                root,
                repository=repository,
                playbook=request.playbook,
                scope=request.scope,
                into=request.into,
                report=request.report,
                zone=request.timezone,
                supersedes=request.supersedes,
                prior_runs=request.prior_runs,
            )
        history = GitHubHistory(repository, branch, self.runner)
        if request.operation == "init":
            return history.initialize(request.authority)
        if request.operation == "publish":
            return publish(history, request.run.resolve(), request.authority, request.files, repository)
        if request.operation == "update":
            return update(
                history, request.run.resolve(), request.authority, request.integration_state, request.applied_commits
            )
        if request.operation == "list":
            if request.playbook not in PLAYBOOKS or request.limit < 1:
                raise InputError("Name a supported playbook and a positive limit")
            return history.listing(
                request.playbook, request.source_sha, request.outcome_filter, request.include_superseded, request.limit
            )
        return history.get(request.run_id, request.file)
