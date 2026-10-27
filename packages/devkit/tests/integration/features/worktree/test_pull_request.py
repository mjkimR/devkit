from __future__ import annotations

import json
import subprocess

import pytest
from devkit_agt.features.worktree.models.pull_request import Repository
from devkit_agt.features.worktree.repositories.pull_request import (
    CommandResult,
    GitHub,
    PullRequestError,
    run_gh,
)
from testsupport.rules import git, init_repo

REPOSITORY = Repository(
    "origin", "git@alias:owner/repo.git", "git@alias:owner/repo.git", "github.example", "owner/repo", False
)


def test_discovery_binds_only_selected_remote_and_keeps_enterprise_host(tmp_path):
    root = init_repo(tmp_path / "repo")
    git(root, "remote", "add", "target", REPOSITORY.fetch_url)
    git(root, "remote", "add", "origin", "https://github.com/unrelated/repo")

    def runner(cwd, args):
        assert cwd != root
        assert git(cwd, "remote") == "origin"
        assert git(cwd, "remote", "get-url", "origin") == REPOSITORY.fetch_url
        assert args[:2] == ["repo", "view"]
        return CommandResult(
            0,
            json.dumps(
                {
                    "url": "https://github.example/owner/repo",
                    "nameWithOwner": "owner/repo",
                    "mergeCommitAllowed": True,
                    "deleteBranchOnMerge": True,
                }
            ),
        )

    result = GitHub(root, runner).resolve("target")
    assert result.selector == "github.example/owner/repo" and result.delete_on_merge


def test_pr_operations_bind_repository_and_merge_cannot_enqueue(tmp_path):
    calls = []

    def runner(cwd, args):
        calls.append(args)
        return (
            CommandResult(1, "HTTP/2.0 405 Method Not Allowed\n\n{}") if "--include" in args else CommandResult(0, "[]")
        )

    port = GitHub(tmp_path, runner)
    port.find(REPOSITORY, "dev-demo")
    port.view(REPOSITORY, 42)
    port.create(REPOSITORY, "dev-demo", "main", "SPEC-demo")
    response = port.merge(REPOSITORY, 42, "a" * 40, "dev-demo", "main", "SPEC-demo")
    port.dependents(REPOSITORY, "dev-demo")
    assert response.http_status == 405
    for args in calls:
        if args[0] == "pr":
            assert args[args.index("-R") + 1] == REPOSITORY.selector
        else:
            assert args[0] == "api" and args[args.index("--hostname") + 1] == REPOSITORY.host
            assert "repos/owner/repo/pulls/42/merge" in args
            assert "sha=" + "a" * 40 in args and "merge_method=merge" in args
        assert not set(args) & {"--auto", "--admin", "--delete-branch"}
        assert not any("merge-async" in arg for arg in args)


@pytest.mark.parametrize(
    "rule",
    [
        {"type": "merge_queue"},
        {"type": "required_linear_history"},
        {"type": "pull_request", "parameters": {"allowed_merge_methods": ["squash"]}},
    ],
)
def test_structured_rules_refuse_prohibited_merge(tmp_path, rule):
    def runner(cwd, args):
        if "graphql" in args:
            return CommandResult(0, '{"data":{"repository":{"mergeQueue":null}}}')
        assert "repos/owner/repo/rules/branches/main" in args
        return CommandResult(0, json.dumps([[rule]]))

    with pytest.raises(PullRequestError):
        GitHub(tmp_path, runner).rules(REPOSITORY, "main")


def test_classic_linear_history_is_refused_and_unreadable_is_disclosed(tmp_path):
    def runner(cwd, args):
        if "graphql" in args:
            return CommandResult(0, '{"data":{"repository":{"mergeQueue":null}}}')
        if "--paginate" in args:
            return CommandResult(0, "[[]]")
        return CommandResult(0, '{"required_linear_history":{"enabled":true}}')

    with pytest.raises(PullRequestError, match="Classic protection"):
        GitHub(tmp_path, runner).rules(REPOSITORY, "main")

    def unreadable(cwd, args):
        return CommandResult(1) if args[-1].endswith("/protection") else runner(cwd, args)

    assert GitHub(tmp_path, unreadable).rules(REPOSITORY, "main") == [{"type": "unverified_classic_protection"}]


@pytest.mark.parametrize(
    "nodes,expected",
    [
        ([], []),
        ([{"name": "optional", "status": "COMPLETED", "conclusion": "FAILURE", "isRequired": False}], []),
        ([{"name": "ci", "status": "QUEUED", "isRequired": True}], ["pending"]),
        ([{"context": "ci", "state": "ERROR", "isRequired": True}], ["fail"]),
        ([{"name": "ci", "status": "COMPLETED", "conclusion": "SKIPPED", "isRequired": True}], ["pass"]),
    ],
)
def test_required_checks_are_structured_and_optional_checks_do_not_block(tmp_path, nodes, expected):
    def runner(cwd, args):
        if args[0] == "pr":
            return CommandResult(0, '{"id":"PR_1"}')
        assert "owner=owner" in args and "name=repo" in args and "id=PR_1" in args
        assert args[args.index("--hostname") + 1] == "github.example"
        query = next(a for a in args if a.startswith("query="))
        assert query.count("{") == query.count("}")
        data = {
            "data": {
                "repository": {
                    "pullRequest": {
                        "commits": {"nodes": [{"commit": {"statusCheckRollup": {"contexts": {"nodes": nodes}}}}]}
                    }
                }
            }
        }
        return CommandResult(0, json.dumps([data]))

    checks = GitHub(tmp_path, runner).checks(REPOSITORY, 42)
    assert [c["bucket"] for c in checks] == expected


def test_runner_is_bounded_noninteractive_and_timeout_is_unknown(tmp_path, monkeypatch):
    def timeout(args, **kwargs):
        assert kwargs["timeout"] == 5 and kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["env"]["GH_PROMPT_DISABLED"] == "1" and "GH_REPO" not in kwargs["env"]
        raise subprocess.TimeoutExpired(args, 5)

    monkeypatch.setattr(subprocess, "run", timeout)
    assert run_gh(tmp_path, ["pr", "view", "1", "-R", REPOSITORY.selector]).returncode is None


def test_multiple_push_destinations_refused_at_prepare_and_revalidation(tmp_path):
    root = init_repo(tmp_path / "repo")
    git(root, "remote", "add", "origin", REPOSITORY.fetch_url)
    port = GitHub(
        root,
        lambda cwd, args: CommandResult(
            0,
            json.dumps(
                {
                    "url": "https://github.example/owner/repo",
                    "nameWithOwner": "owner/repo",
                    "mergeCommitAllowed": True,
                    "deleteBranchOnMerge": False,
                }
            ),
        ),
    )
    port.validate(REPOSITORY)
    git(root, "config", "--add", "remote.origin.pushurl", REPOSITORY.push_url)
    git(root, "config", "--add", "remote.origin.pushurl", "https://github.example/other/repo.git")
    for operation in (lambda: port.resolve("origin"), lambda: port.validate(REPOSITORY)):
        with pytest.raises(PullRequestError) as error:
            operation()
        assert error.value.code == "INTEGRATION_REMOTE_UNSUPPORTED"
