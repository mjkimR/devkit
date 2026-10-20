# GitHub PR platform verification

Development verified the following against official documentation and CLI source. No live repository was created,
pushed, merged or deleted. Offline fake-platform tests use local bare repositories, so server behavior and host
transport cancellation remain externally unverified.

- [Synchronous REST merge](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request) accepts a pinned head
  `sha`, merge method and title/body; it has no base-SHA precondition. Its documentation explicitly excludes merge
  queues and stacked pull requests. HTTP 403/405/409/422 are recognized refusals only when a subsequent observation
  still shows an unmerged PR. Other nonzero or timed-out results remain unknown until observed.
- [gh pr merge](https://cli.github.com/manual/gh_pr_merge) implicitly enqueues on a queue branch. The implementation
  therefore uses synchronous REST and never calls this command. A fake policy change between prepare and merge
  returns HTTP 405 and proves no enqueue/auto/admin command is issued; this is not a live queue experiment.
- [gh repo view](https://cli.github.com/manual/gh_repo_view), [gh api](https://cli.github.com/manual/gh_api) and
  [gh ruleset check](https://cli.github.com/manual/gh_ruleset_check) have different binding/output options.
  Repo discovery uses a private one-remote repository so gh resolves SSH aliases; PR calls use `-R`; API calls
  use an explicit host and repository endpoint or GraphQL owner/name. Rules use structured API responses.
- [CLI required-check source](https://github.com/cli/cli/blob/v2.96.0/api/query_builder.go) selects CheckRun and
  StatusContext via `isRequired(pullRequestId:)`. The adapter uses this structured query because
  [checks command source](https://github.com/cli/cli/blob/v2.96.0/pkg/cmd/pr/checks/checks.go) returns an unstructured
  error for zero required checks. Empty required checks do not block; optional failures do not become required.
- [Skipped workflows](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs) can leave
  required checks pending. The API reports pending check/review names and returns without polling; the agent must
  bound any external watch and escalate checks that never start.
- [Required reviews](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews)
  exclude author self-approval and can become stale after a push. Review and mergeability are freshly observed;
  server enforcement is retained. Unreadable classic branch protection is disclosed, never treated as permission.
- [Deleting branches](https://docs.github.com/en/pull-requests/how-tos/commit-changes/managing-branches-within-your-repository)
  may retarget dependent PRs. Explicit deletion therefore checks for open dependents and exact source identity;
  platform automatic deletion is separately disclosed in confirmation.

## Call bounds and limitations

Each default gh/network Git subprocess has a maximum five-second timeout and each observed/executed network phase
shares a twenty-second monotonic budget. Tests inject timeout outcomes and verify state remains inspectable and
unknown mutations are not repeated. Repository-lock approval wait is separately bounded at twenty seconds; resume
uses zero wait. Provider checks, local Git hooks and local readiness work are not made time-bounded by this change.

[Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) documents a default tool timeout of
60 seconds. [Claude environment variables](https://code.claude.com/docs/en/env-vars) document transport-dependent
request/idle timers, including a default 60-second network request timer and a much larger tool timeout in the
current release. These are documentation defaults, not inspected settings for this user. A long local provider can
exceed a host timeout despite bounded network work. Host timeout does not establish cancellation or rollback:
inspect status after the server worker becomes available; active execution can keep the record busy. Requests and
checked-build evidence survive only in the same process. Restart requires fresh preparation and confirmation.


The offline approving call was measured around `IntegrationService.integrate` including preparation, immediate
fixture confirmation, build and execution: a completed merge/cleanup took 1.678 seconds; a pending return took
0.729 seconds (two tests passed). These exclude human confirmation delay and use local bare remotes/fake GitHub,
so they do not establish live latency or a hard bound for arbitrary provider checks. The twenty-second shared
network deadline and five-second subprocess bounds limit network contributions under the common sixty-second
host default; long local work remains the explicitly disclosed limit.
