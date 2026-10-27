"""Bounded, injectable GitHub operations. Authentication remains owned by gh."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote, urlparse

from devkit.advisory import Actor, AdvisoryError, Retry
from devkit_core.base.errors import GitError
from devkit_core.core.git import run_git

from devkit_agt.features.worktree.models.pull_request import Repository as Repository

NETWORK_TIMEOUT = 5.0
NETWORK_BUDGET = 20.0
PR_FIELDS = "number,url,state,isDraft,isCrossRepository,headRefName,headRefOid,baseRefName,mergeCommit,mergeStateStatus,mergeable,reviewDecision,statusCheckRollup"


class PullRequestError(AdvisoryError):
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    code = "INTEGRATION_REMOTE_UNSUPPORTED"
    fix = "Inspect the bound GitHub repository and prepare again; use local integration for unsupported remotes"

    def __init__(self, code: str, message: str, fix: str, *details: object) -> None:
        super().__init__(message, *details, fix=fix)
        self.code = code


@dataclass(frozen=True)
class CommandResult:
    returncode: int | None
    stdout: str = ""
    stderr: str = ""
    http_status: int | None = None


class Runner(Protocol):
    def __call__(self, cwd: Path, args: list[str]) -> CommandResult: ...


def run_gh(cwd: Path, args: list[str], *, timeout: float = NETWORK_TIMEOUT) -> CommandResult:
    env = {**os.environ, "GH_PROMPT_DISABLED": "1", "NO_COLOR": "1", "GH_PAGER": "cat"}
    # Repository discovery cannot inherit a caller's unrelated override.
    env.pop("GH_REPO", None)
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    try:
        result = subprocess.run(
            ["gh", *args],
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return CommandResult(127)
    except subprocess.TimeoutExpired:
        return CommandResult(None)
    return CommandResult(result.returncode, os.fsdecode(result.stdout), os.fsdecode(result.stderr))


class GitHub:
    """All repository calls carry explicit identity; the runner is injectable for offline tests."""

    def __init__(self, root: Path, runner: Runner = run_gh) -> None:
        self.root = root
        self.runner = runner
        self._budget = threading.local()

    def begin_call(self) -> None:
        self._budget.deadline = time.monotonic() + NETWORK_BUDGET

    def _remaining(self) -> float:
        if not hasattr(self._budget, "deadline"):
            self.begin_call()
        return min(NETWORK_TIMEOUT, self._budget.deadline - time.monotonic())

    def _call(self, cwd: Path, args: list[str]) -> CommandResult:
        remaining = self._remaining()
        if remaining <= 0:
            return CommandResult(None)
        if self.runner is run_gh:
            return run_gh(cwd, args, timeout=remaining)
        return self.runner(cwd, args)

    def _network(self, *args: str) -> bytes:
        remaining = self._remaining()
        if remaining <= 0:
            raise PullRequestError(
                "INTEGRATION_STEP_UNKNOWN",
                "Network budget exhausted before the next operation",
                "Inspect Git and pull-request state; after confirming the mutation outcome, rerun `uv run devkit integration integrate <branch> --task-kind <kind> --task-id <id> --route pull-request` for remaining work; do not repeat an unknown mutation",
            )
        return run_git(self.root, *args, timeout=remaining)

    def _json(self, args: list[str], *, cwd: Path | None = None) -> Any:
        result = self._call(cwd or self.root, args)
        if result.returncode is None:
            raise PullRequestError(
                "INTEGRATION_STEP_UNKNOWN",
                "GitHub observation timed out or exhausted the network budget",
                "Inspect Git and pull-request state; after confirming the mutation outcome, rerun `uv run devkit integration integrate <branch> --task-kind <kind> --task-id <id> --route pull-request` for remaining work; do not repeat an unknown mutation",
            )
        if result.returncode != 0:
            raise PullRequestError(
                "INTEGRATION_GH_UNAVAILABLE",
                "GitHub observation failed",
                "Install/authenticate gh for the bound host, inspect its permissions and prepare again",
            )
        try:
            return json.loads(result.stdout)
        except (ValueError, TypeError) as exc:
            raise PullRequestError(
                "INTEGRATION_REMOTE_UNSUPPORTED",
                "GitHub returned invalid JSON",
                "Inspect the GitHub response and prepare again",
            ) from exc

    def _push_url(self, remote: str) -> str:
        urls = run_git(self.root, "remote", "get-url", "--push", "--all", remote).decode().splitlines()
        if len(urls) != 1:
            raise PullRequestError(
                "INTEGRATION_REMOTE_UNSUPPORTED",
                "Selected remote must have exactly one effective push destination",
                "Configure one push destination for the selected remote and prepare again",
            )
        return urls[0]

    def resolve(self, remote: str) -> Repository:
        fetch_url = run_git(self.root, "remote", "get-url", remote).decode().strip()
        push_url = self._push_url(remote)
        for url in (fetch_url, push_url):
            parsed = urlparse(url)
            if parsed.scheme in {"http", "https"} and (parsed.username or parsed.password):
                raise PullRequestError(
                    "INTEGRATION_REMOTE_UNSUPPORTED",
                    "Credential-bearing HTTP remote URL is unsupported",
                    "Use gh authentication with a credential-free remote URL and prepare again",
                )
        # Let gh's own SSH translator resolve aliases. A private discovery repository contains only the bound
        # remote, so multiple remotes and gh's default selection cannot silently select another repository.
        with tempfile.TemporaryDirectory(prefix="devkit-pr-discovery-") as directory:
            discovery = Path(directory)
            run_git(discovery, "init", "--quiet")
            run_git(discovery, "remote", "add", "origin", fetch_url)
            data = self._json(
                ["repo", "view", "--json", "nameWithOwner,url,mergeCommitAllowed,deleteBranchOnMerge"], cwd=discovery
            )
        url = urlparse(data["url"])
        name = data["nameWithOwner"]
        if url.scheme != "https" or not url.hostname or url.path.strip("/") != name:
            raise PullRequestError(
                "INTEGRATION_REMOTE_UNSUPPORTED",
                "Repository identity is inconsistent",
                "Use a GitHub remote gh resolves and prepare again",
            )
        if not data["mergeCommitAllowed"]:
            raise PullRequestError(
                "INTEGRATION_MERGE_COMMIT_FORBIDDEN",
                "Repository forbids merge commits",
                "Integrate outside this route; do not substitute squash or rebase",
            )
        repository = Repository(remote, fetch_url, push_url, url.hostname, name, data["deleteBranchOnMerge"])
        # Separate push URLs can publish elsewhere; resolve and compare them rather than assuming fetch identity.
        if push_url != fetch_url:
            pushed = self._json(["repo", "view", push_url, "--json", "url"])
            if pushed["url"].rstrip("/") != data["url"].rstrip("/"):
                raise PullRequestError(
                    "INTEGRATION_REMOTE_UNSUPPORTED",
                    "Push and fetch repositories differ",
                    "Configure one GitHub repository for the selected remote and prepare again",
                )
        return repository

    def validate(self, repository: Repository) -> None:
        for push, expected in ((False, repository.fetch_url), (True, repository.push_url)):
            args = ["remote", "get-url", *(["--push"] if push else []), repository.remote]
            actual = self._push_url(repository.remote) if push else run_git(self.root, *args).decode().strip()
            if actual != expected:
                raise PullRequestError("INTEGRATION_PR_CONFLICT", "Bound remote URL changed", "Prepare a new request")

    def rules(self, repository: Repository, branch: str) -> list[dict[str, Any]]:
        owner, name = repository.name.split("/")
        queue = self._json(
            [
                "api",
                "--hostname",
                repository.host,
                "graphql",
                "-f",
                "query=query($owner:String!,$name:String!,$branch:String!){repository(owner:$owner,name:$name){mergeQueue(branch:$branch){id}}}",
                "-f",
                f"owner={owner}",
                "-f",
                f"name={name}",
                "-f",
                f"branch={branch}",
            ]
        )
        if queue.get("errors") or queue["data"]["repository"]["mergeQueue"]:
            raise PullRequestError(
                "INTEGRATION_REMOTE_UNSUPPORTED",
                "Target merge queue is enabled or cannot be ruled out",
                "Inspect target queue configuration and use the platform queue outside this route",
            )
        endpoint = f"repos/{repository.name}/rules/branches/{quote(branch, safe='')}"
        data = self._json(["api", "--hostname", repository.host, "--method", "GET", endpoint, "--paginate", "--slurp"])
        rules = [rule for page in data for rule in page]
        for rule in rules:
            kind = rule.get("type")
            params = rule.get("parameters", {})
            if kind == "merge_queue":
                raise PullRequestError(
                    "INTEGRATION_REMOTE_UNSUPPORTED",
                    "Target requires a merge queue",
                    "Integrate outside this route without bypassing the queue",
                )
            if kind == "required_linear_history" or (
                kind == "pull_request"
                and "allowed_merge_methods" in params
                and "merge" not in params["allowed_merge_methods"]
            ):
                raise PullRequestError(
                    "INTEGRATION_MERGE_COMMIT_FORBIDDEN",
                    "Target rules forbid merge commits",
                    "Integrate outside this route; do not substitute squash or rebase",
                )
        classic = self._call(
            self.root,
            [
                "api",
                "--hostname",
                repository.host,
                "--method",
                "GET",
                f"repos/{repository.name}/branches/{quote(branch, safe='')}/protection",
            ],
        )
        if classic.returncode == 0:
            protection = json.loads(classic.stdout)
            if protection.get("required_linear_history", {}).get("enabled"):
                raise PullRequestError(
                    "INTEGRATION_MERGE_COMMIT_FORBIDDEN",
                    "Classic protection requires linear history",
                    "Integrate outside this route; do not substitute squash or rebase",
                )
        else:
            rules.append({"type": "unverified_classic_protection"})
        return rules

    def find(self, repository: Repository, branch: str) -> list[dict[str, Any]]:
        return self._json(
            [
                "pr",
                "list",
                "-R",
                repository.selector,
                "--head",
                branch,
                "--state",
                "all",
                "--limit",
                "1000",
                "--json",
                PR_FIELDS,
            ]
        )

    def view(self, repository: Repository, number: int) -> dict[str, Any]:
        return self._json(["pr", "view", str(number), "-R", repository.selector, "--json", PR_FIELDS])

    def checks(self, repository: Repository, number: int) -> list[dict[str, Any]]:
        pr = self._json(["pr", "view", str(number), "-R", repository.selector, "--json", "id"])
        query = """query($owner:String!,$name:String!,$number:Int!,$id:ID!,$endCursor:String){
          repository(owner:$owner,name:$name){pullRequest(number:$number){commits(last:1){nodes{commit{
          statusCheckRollup{contexts(first:100,after:$endCursor){nodes{
          ... on StatusContext{context state isRequired(pullRequestId:$id)}
          ... on CheckRun{name status conclusion isRequired(pullRequestId:$id)}}
          pageInfo{hasNextPage endCursor}}}}}}}}}"""
        owner, name = repository.name.split("/")
        pages = self._json(
            [
                "api",
                "--hostname",
                repository.host,
                "graphql",
                "-f",
                f"query={query}",
                "-f",
                f"owner={owner}",
                "-f",
                f"name={name}",
                "-F",
                f"number={number}",
                "-f",
                f"id={pr['id']}",
                "--paginate",
                "--slurp",
            ]
        )
        checks = []
        for page in pages:
            if page.get("errors"):
                raise PullRequestError(
                    "INTEGRATION_STEP_UNKNOWN", "Required check query failed", "Inspect the PR and resume"
                )
            commits = page["data"]["repository"]["pullRequest"]["commits"]["nodes"]
            if not commits:
                raise PullRequestError(
                    "INTEGRATION_STEP_UNKNOWN", "PR commit is unavailable", "Inspect the PR and resume"
                )
            rollup = commits[0]["commit"]["statusCheckRollup"]
            for check in (rollup or {}).get("contexts", {}).get("nodes", []):
                if not check["isRequired"]:
                    continue
                state = (
                    check.get("conclusion")
                    if check.get("status") == "COMPLETED"
                    else check.get("state", check.get("status"))
                )
                bucket = (
                    "pass"
                    if state in {"SUCCESS", "NEUTRAL", "SKIPPED"}
                    else "fail"
                    if state in {"FAILURE", "ERROR", "TIMED_OUT", "ACTION_REQUIRED", "CANCELLED", "STARTUP_FAILURE"}
                    else "pending"
                )
                checks.append({"name": check.get("name", check.get("context")), "bucket": bucket, "state": state})
        return checks

    def create(self, repository: Repository, branch: str, target: str, task_id: str) -> CommandResult:
        return self._call(
            self.root,
            [
                "pr",
                "create",
                "-R",
                repository.selector,
                "--head",
                branch,
                "--base",
                target,
                "--title",
                f"Integrate {branch} into {target}",
                "--body",
                f"devkit task: {task_id}",
            ],
        )

    def merge(
        self, repository: Repository, number: int, source: str, branch: str, target: str, task_id: str
    ) -> CommandResult:
        # The synchronous endpoint cannot enqueue. gh pr merge can enqueue implicitly when queue policy changes.
        result = self._call(
            self.root,
            [
                "api",
                "--hostname",
                repository.host,
                "--method",
                "PUT",
                "--include",
                f"repos/{repository.name}/pulls/{number}/merge",
                "-f",
                f"sha={source}",
                "-f",
                "merge_method=merge",
                "-f",
                f"commit_title=chore(merge): integrate {branch} into {target}",
                "-f",
                f"commit_message={task_id}",
            ],
        )
        lines = result.stdout.splitlines()
        status = None
        if lines and lines[0].startswith("HTTP/"):
            parts = lines[0].split()
            if len(parts) > 1 and parts[1].isdigit():
                status = int(parts[1])
        return CommandResult(result.returncode, result.stdout, result.stderr, status)

    def dependents(self, repository: Repository, branch: str) -> list[dict[str, Any]]:
        return self._json(
            [
                "pr",
                "list",
                "-R",
                repository.selector,
                "--base",
                branch,
                "--state",
                "open",
                "--limit",
                "1",
                "--json",
                "number,url",
            ]
        )

    def ref(self, repository: Repository, ref: str) -> str | None:
        self.validate(repository)
        text = self._network("ls-remote", "--refs", repository.remote, ref).decode().strip()
        return text.split()[0] if text else None

    def fetch(self, repository: Repository, branch: str) -> str:
        self.validate(repository)
        tracking = f"refs/remotes/{repository.remote}/{branch}"
        self._network(
            "fetch",
            "--no-tags",
            repository.remote,
            f"+refs/heads/{branch}:{tracking}",
        )
        return run_git(self.root, "rev-parse", "--verify", tracking).decode().strip()

    def _mutate(self, *args: str) -> None:
        try:
            self._network(*args)
        except GitError as exc:
            raise PullRequestError(
                "INTEGRATION_STEP_UNKNOWN",
                "Git mutation outcome is unconfirmed",
                "Inspect Git and pull-request state; after confirming the mutation outcome, rerun `uv run devkit integration integrate <branch> --task-kind <kind> --task-id <id> --route pull-request` for remaining work; do not repeat an unknown mutation",
                str(exc),
            ) from exc

    def push(self, repository: Repository, source: str, branch: str) -> None:
        self.validate(repository)
        self._mutate("push", repository.remote, f"{source}:refs/heads/{branch}")

    def delete(self, repository: Repository, source: str, branch: str) -> None:
        self.validate(repository)
        self._mutate(
            "push",
            f"--force-with-lease=refs/heads/{branch}:{source}",
            repository.remote,
            "--delete",
            branch,
        )

    def fetch_commit(self, repository: Repository, sha: str) -> None:
        self.validate(repository)
        self._network("fetch", "--no-tags", repository.remote, sha)
