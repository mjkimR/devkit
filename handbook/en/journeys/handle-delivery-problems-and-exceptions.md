---
sources:
  CAP-DLV-delivery-workflows: 936dff28b6c106fdcc568a677db096421e174f9c
  CAP-DLV-workflow-envelopes: ba3e36ff09f879615ad60389b433b58cdf4097ee
  CAP-HARN-agent-guidance: 3e6c66d7ea068a580cc1ee82308708d407dab6bd
  CAP-WT-task-worktrees: 2ea80d46ab9cf19504182e73b6f2bcc301e8f7db
  UC-handle-delivery-problems-and-exceptions: 3bd25e04ea70fadeefdc4a324a9780da89013610
title: Handle delivery problems and exceptions
---

# Handle delivery problems and exceptions

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](adopt-sdd-from-incubation.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Incubate an idea](incubate-an-idea.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
- [Speed up selected slow operations](speed-up-selected-slow-operations.md)
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

Work meets obstacles. Most are not problems: a choice between two valid options, or an improvement that can wait. A
problem, in devkit's sense, is an obstacle that cannot be solved without changing the agreed goal, scope or contract.
This journey shows how the agent tells them apart, how a problem holds the work so nothing broken lands, and how the
work recovers or closes cleanly.

The use case is
[`UC-handle-delivery-problems-and-exceptions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md).
Envelopes, Units and the `exception` stage are explained in [Concepts](../concepts.md).

## 1. Is it a problem?

The executor, a worker or the agent itself, checks the obstacle against the agreement
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)):

| The obstacle is | The executor |
| --- | --- |
| A choice inside the agreed intent | Takes the recommended option and records the reason in `plan.md`, an envelope's assumptions or the final report. Work continues. |
| An improvement that does not block the work | Records it as feedback or a follow-up draft proposal. Work continues. |
| A problem in a `session` task | Reports it in the conversation, writes no record and does not integrate. |
| A problem in a Unit | Records it, as below. |

## 2. Record the problem

The executor writes the run's `worker` envelope with the cause, what it tried and the recovery it recommends:

```bash
uv run devkit workflow envelope worker --unit <dir> --stage <stage> --effort <effort> \
  --problem "<cause>" --tried "<attempt>" --recovery "<recommended recovery>"
```

It commits the unfinished work together with the envelope and ends the run without integrating
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md)).

## 3. The Unit is held

While the problem has no resolution:

- no gate from the problem's stage on passes, whatever policy or `--given` says;
- the handoff is refused;
- `devkit worktree finish --merge` refuses the branch with `WORKTREE_BLOCKED`.

You can see the hold:

```bash
uv run devkit workflow envelope check --unit <dir>
```

It prints a `[BLOCKED: ...]` line per open problem and `[PENDING_QUESTION: ...]` per unanswered question.

## 4. Fix the cause and resolve

The agent decides a recovery inside the approved scope: it fixes the root cause itself, or reverts. It commits the
fix together with a `resolution` envelope that names the problem's `worker` envelope:

```bash
uv run devkit workflow envelope resolution --unit <dir> --resolves worker-NN.yaml --summary "<what fixed it>"
```

A resolution is written by whoever actually fixed the cause, in the same commit as the fix. When the agent hands the
recovery to a new worker, that worker writes it.

## 5. Continue

`devkit workflow envelope check` reports no `[BLOCKED]` line, and the workflow continues from the stage where the
Unit stood. Gates passed before the problem stay passed.

## When the recovery does not work

- **The fix did not solve the cause.** No resolution is written; the problem stays open and the Unit stays held. The
  agent tries another remedy or reports a blocker.
- **The recovery needs a different agreement.** If the goal, scope or contract has to change, or the direction is not
  viable, you decide the close: a depth escalation to a new draft, a supersede or an abandon. The close is committed
  to the base as Backlog work. The agent closes any pull request and remote branch and drops the unmerged branch:

  ```bash
  uv run devkit worktree finish dev-<slug> --discard
  ```

  The result says `merged=no discarded=yes`. It never removes a worktree with uncommitted changes (`WORKTREE_DIRTY`)
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md),
  [`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md)).
- **The record itself cannot be written.** If the host denies the envelope or the emergency commit, the worker
  returns `failed` with the cause, the commands it tried, the actual last commit, the dirty paths and the missing
  records, never an invented result. The agent treats that return as blocked and runs the recovery itself.

## The exception stage

Some failures the agent cannot handle alone: a retry cap exceeded, a tool or execution failure, a semantic conflict
that stays unresolved. The workflow then enters `exception` with the cause and evidence. The stage stays current
until you have handled the cause (`exception-handled`), then returns to the stage that raised it. No new task is
opened to get around the cap.

## Codes you may meet

| Code | Meaning | What to do |
| --- | --- | --- |
| `WORKTREE_BLOCKED` | The merge was refused; one detail per open problem or question. | Resolve or answer, then rerun. |
| `ENVELOPE_REFERENCE_INVALID` | The resolution names a `worker` envelope that carries no problem. | Name the envelope that holds the problem; the refusal lists each `worker` envelope that carries one. |
| `HANDOFF_HELD` | A held Unit cannot be handed off. | Resolve the hold first. |
| `WORKTREE_DIRTY` | The worktree has uncommitted or untracked changes. | Commit or move them out, then discard again. |

Whatever happens, an unresolved problem keeps the base clean: the failed range, the open findings and the attempted
remedies stay in Git, and nothing is deleted without your decision. Areas: [Delivery](../areas/delivery.md),
[Worktree](../areas/worktree.md).
