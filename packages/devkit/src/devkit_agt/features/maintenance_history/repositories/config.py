"""Destination defaults: configuration is input, never publication authority."""

from __future__ import annotations

import re
from pathlib import Path

from devkit_core.base.errors import GitError
from devkit_core.core.git import run_git, run_git_text
from devkit_dist.features.project.repositories.project import read_project_config
from devkit_dist.features.project.services.config_template import TemplateKey, TemplateTable

from ..models.errors import InputError


def config_tables() -> tuple[TemplateTable, ...]:
    return (
        TemplateTable(
            (
                TemplateKey("repository", help="credential-free owner/repo; defaults to origin", example="owner/repo"),
                TemplateKey(
                    "branch", "maintenance-history", "dedicated history branch; grants no publication authority"
                ),
            ),
            path=("history",),
            help="Maintenance history destination inputs only.",
        ),
    )


def destination(root: Path, repository: str | None, branch: str | None) -> tuple[str, str]:
    config = read_project_config(root).get("maintenance", {})
    if not isinstance(config, dict) or not isinstance(config.get("history", {}), dict):
        raise InputError("maintenance.history must be a table")
    history = config.get("history", {})
    repo = repository or history.get("repository")
    if not repo:
        try:
            url = run_git_text(root, "remote", "get-url", "origin").strip()
        except GitError:
            url = ""
        match = re.fullmatch(r"(?:git@github\.com:|https://github\.com/)([^/]+/[^/]+?)(?:\.git)?", url)
        if not match:
            raise InputError("Set maintenance.history.repository or pass --repository with owner/repo")
        repo = match[1]
    if not isinstance(repo, str) or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) is None:
        raise InputError("History repository must be credential-free owner/repo")
    selected = branch or history.get("branch", "maintenance-history")
    if not isinstance(selected, str) or not selected or selected.startswith("-"):
        raise InputError("Invalid history branch name")
    try:
        run_git(root, "check-ref-format", "refs/heads/" + selected)
    except GitError as exc:
        raise InputError("Invalid history branch name") from exc
    return repo, selected
