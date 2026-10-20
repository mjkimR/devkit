---
id: ADR-github-pull-request-repository-binding
title: Explicit repository binding with supported GitHub CLI syntax
summary: "Every GitHub operation binds the resolved host and repository using the syntax its gh command supports; structured rules use gh api."
status: accepted
created_at: 2026-10-20
supersedes: ADR-github-pull-request-adapter-in-devkit-worktree
---

# [ADR-github-pull-request-repository-binding] Explicit repository binding with supported GitHub CLI syntax

## Context

The predecessor required `-R` on every gh invocation. Both installed gh 2.96.0 help and the official manuals show
that `gh repo view` takes a repository operand and `gh api` takes an endpoint and hostname. `gh ruleset check`
does not offer JSON output. The Host approved this concrete CLI correction during Development without changing
remote authority, platform scope or protection requirements.

## Decision

Preserve the predecessor's GitHub-only injectable port in `devkit.worktree`, gh-owned authentication, noninteractive
bounded subprocesses, pinned-source no-ff merging, refusal of forks/queues/auto-merge/admin bypass and leased remote
deletion. Bind every repository operation to the resolved host and owner/repository: use `-R` where supported,
a repository operand for `repo view`, and an explicit hostname and repository endpoint or GraphQL variables for
`gh api`. Use structured applicable-rule API responses through gh, rather than parsing ruleset display text.
Repository discovery must bind the selected Git remote, including SSH aliases gh resolves; never silently choose
an unrelated default remote or omit the Enterprise hostname. Tests verify each command's binding.

## Evidence

- [gh repo view](https://cli.github.com/manual/gh_repo_view)
- [gh api](https://cli.github.com/manual/gh_api)
- [gh ruleset check](https://cli.github.com/manual/gh_ruleset_check)

No token reader, direct HTTP client, additional hosting platform or protection bypass is introduced.

## Synchronous merge binding

`gh pr merge` can enqueue implicitly when target queue policy is enabled, even without `--auto`. A queue enabled
between preflight and execution must not expand the approved authority. The Host therefore selected the synchronous
`gh api --method PUT repos/<owner>/<repo>/pulls/<number>/merge`, with the explicit hostname, approved `sha`,
`merge_method=merge` and composed commit title/body. The [official merge API](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request)
states that this endpoint does not support stacked PRs or merging with a merge queue. It has no enqueue option;
a platform refusal leaves the PR unmerged. The [gh merge manual](https://cli.github.com/manual/gh_pr_merge)
documents the implicit queue behavior avoided here. Do not use the asynchronous endpoint or queue/admin bypass.
HTTP refusal statuses are reported separately from unknown transport outcomes, which remain observational recovery.
