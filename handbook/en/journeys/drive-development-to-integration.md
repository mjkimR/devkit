---
sources:
  CAP-DLV-delivery-workflows: e1366a8cbed7bace6c51651085abc7d50b588768
  CAP-DLV-project-policy: 7cec046a7324de8f46048c80dea6a4286bf809ef
  CAP-DLV-workflow-envelopes: ac166b8217314babc0f4e8ab346a6a9041f85fef
  CAP-INT-mcp-services: 41636553f0fe6331719d5d0cfaad2965deda6eb1
  CAP-MCP-runtime-registration: 6dd9d3d5cf7a915a18d80f1adae375cf73823c1a
  CAP-WT-task-worktrees: a885013edf5dd548ffad4e9140c4b32b01b16ce2
  UC-drive-development-to-integration: bc214c7d80b401cf5b2ba5027c9144673d104393
title: Drive development to integration
---

# Drive development to integration

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `ae01161143be`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
- [Advisories](../areas/advisory.md)
- [Agent-first CLI toolkit](../areas/cli.md)
- [Collaboration](../areas/collaboration.md)
- [Compact command output](../areas/compact.md)
- [Delivery](../areas/delivery.md)
- [Distribution](../areas/distribution.md)
- [Documents](../areas/documents.md)
- [Commit gates](../areas/gate.md)
- [Generated Files](../areas/generated.md)
- [Governance rules](../areas/governance.md)
- [Harness](../areas/harness.md)
- [Host](../areas/host.md)
- [Integration](../areas/integration.md)
- [MCP](../areas/mcp.md)
- [Search](../areas/search.md)
- [Traceability](../areas/traceability.md)
- [Viewer](../areas/viewer.md)
- [Worktree](../areas/worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

The intent is agreed and the work has a branch. This journey follows the agent from implementation through review,
the Living Spec update and verification, to the moment the change lands on the base branch. Your part as the user is
small but decisive: under the default policy, nothing lands until you approve it in the conversation.

The use case is
[`UC-drive-development-to-integration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-drive-development-to-integration.md).
It starts after [Route development intent](route-development-intent.md) or
[Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md). Workflows, stages, gates, envelopes and
worktrees are explained in [Concepts](../concepts.md).

## Where you start

A spec Unit is on its `dev-<slug>` activity branch, in a task worktree or the current checkout. The walkthrough below
uses the defaults: `activity-effort` `medium`, `direct` mode, `dev-integration` policy `ask`, local route.

## 1. Ask the workflow where you are

```bash
uv run devkit workflow next --unit specs/<YYYY-MM>/<YYYYMMDD>-<slug>
```

The agent states the effort and its reason, then follows what `next` reports: the current stage, unmet checks and the
skill to run. The stage order of each workflow lives only in its definition (`devkit workflow show <id>`); see
[`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md).

## 2. Specify, build and verify

The agent writes `spec.md`, `plan.md` and `tasks.md`, implements each task within its `_Boundary:`, runs the affected
tests and commits at every stage boundary.

## 3. Review

An initial `code-reviewer` pass checks the diff against the requirements and the check results. The agent records the
findings as a review envelope, fixes them, verifies the fixes and closes the round with a reverify envelope
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md)).

How much review runs depends on the effort:

| Effort | Code review | Reconcile verification |
| --- | --- | --- |
| `low` | The author reviews, still recorded as an envelope | Self-check, recorded |
| `medium` | An initial `code-reviewer` | An independent `reconcile-reviewer`, or a recorded self-check when every affected contract is identified and no cross-component impact remains |
| `high` | Bounded rounds of fresh reviewers until a round finds nothing or only minor fixes remain | The same bounded loop |

## 4. Update the Living Spec

The agent reflects the change in `docs/` and writes `reconcile.md`; the reconcile verification is recorded as a
`reconcile-check` envelope. Then it resolves the reconcile and marks the spec completed.

## 5. Sweep feedback and report

The agent records observations about tools and assets, then the final change report with its test, build and lint
results.

## 6. Bring in the base

The agent merges the moved base into the branch, re-verifies only what the conflict resolution and docs reflection
changed, rechecks the reconcile targets and runs the cumulative check (`devkit rules check --ci --base <ref>`).

## 7. Approve

The agent reads the effective policy with `uv run devkit spec policy`
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md)),
then prepares the integration:

```bash
uv run devkit integration prepare dev-<slug> --task-kind unit --task-id <id> --unit <dir> --route local
```

It shows you the verified report and the exact merge and cleanup effects. You approve in the conversation. Only then
does it run:

```bash
uv run devkit integration integrate dev-<slug> --task-kind unit --task-id <id> --unit <dir> \
  --route local --expected-digest <request.digest>
```

The digest pins the scope you saw. It is a concurrency check, not proof of approval: the command cannot authenticate
your conversation, which is why the agent never runs it without your decision
([`CAP-INT-mcp-services`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/integration/CAP-INT-mcp-services.md)).

## 8. Integration lands

devkit builds the merge commit outside the base checkout, fast-forwards the base onto it without fetch or push,
removes the task worktree, deletes the local branch as policy selects and runs the scoped cleanup
([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
The base now holds `chore(merge): integrate dev-<slug> into <base>`. The agent passes `--given dev-integration` to
later `devkit workflow next` calls and reports the result with its authority.

## Variations

- **Session depth.** A small task has no spec, envelopes or reconcile document. The agent still tests and reviews,
  commits, and reports the change, effort, review and verification in its final response or PR body.
- **Local-orchestrated mode.** On your instruction a `development-worker` runs the turn in its own worktree. The agent
  inspects the returned range with `uv run devkit spec worker inspect`; a range it rejects becomes a problem that
  blocks the Unit.
- **Policy `auto`.** When the shared base sets `dev-integration = "auto"`, the gate passes by policy once review,
  reconcile and checks hold; the report says `authority: policy`.
- **Required pull requests.** Under `[worktree] pull_request = "required"`, the local route is refused with
  `WORKTREE_PR_POLICY`; the agent uses `--route pull-request`, which merges once required checks and reviews pass.

The optional MCP runtime is not part of this path: lifecycle operations run through the CLI, and the runtime serves
shared artifacts only
([`CAP-MCP-runtime-registration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/mcp/CAP-MCP-runtime-registration.md)).

## When it goes wrong

| What you see | What to do |
| --- | --- |
| You object to the change | Nothing is integrated. The agent returns with `devkit workflow return --unit <dir> --to review-refine --note "..."`. |
| `INTEGRATION_AUTHORITY_REQUIRED` or `INTEGRATION_REQUEST_STALE` | The digest is missing or the scope changed. Prepare again and approve the current scope. |
| `INTEGRATION_TARGET_MOVED` | The base moved after the result was built; nothing changed. Merge the base into the branch and request a new integration. |
| `WORKTREE_BLOCKED` | A Unit holds an unresolved problem or unanswered question. See [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md). |
| `INTEGRATION_RUNTIME_IN_WORKTREE` | The CLI runs from inside the worktree it would remove. Use a runtime outside it, then prepare and approve again. |
| `INTEGRATION_RECEIPT_READER_CHANGED` | The branch changes the receipt reader its own receipt depends on. Nothing changed; resolve the mismatch before retrying. |
| A cleanup step stayed incomplete after the merge | Inspect `devkit worktree status` and Git. Rerun `devkit worktree finish <branch> --merge --local-only` while the marked branch remains, or the owning command, such as `devkit spec proposal prune <slug>`. The merge is never repeated. |
| The outcome is unknown | Inspect Git, worktree and pull request state first; run only the remaining effects you can verify. |
| A retry cap is exceeded or a tool fails | The agent enters the `exception` stage with cause and evidence, never a new task to bypass the cap. |

The full list of integration codes is in `CAP-INT-mcp-services`. Areas: [Delivery](../areas/delivery.md),
[Integration](../areas/integration.md), [Worktree](../areas/worktree.md).
