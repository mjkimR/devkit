---
sources:
  ADR-spec-intake-playbook-discovery: 16bc21ff4c9228e34f7634d89dd64da91c60b50a
  CAP-DLV-delivery-workflows: e1366a8cbed7bace6c51651085abc7d50b588768
  CAP-DLV-project-policy: 7cec046a7324de8f46048c80dea6a4286bf809ef
  CAP-DLV-spec-bundles: 516cc932fee8af93baae90012e8dbe4c9b6f4725
  CAP-HARN-agent-guidance: dbab285c20602e97d78db8768dc21e0a5613b379
  CAP-WT-task-worktrees: a885013edf5dd548ffad4e9140c4b32b01b16ce2
  UC-incubate-and-hand-off-a-proposal: cad9b1da4379376d6512d16b06787ea1eed9a43e
  UC-route-development-intent: 50d6278b292da8b936bc1bd6587bde501f490ee6
title: Route a development request
---

# Route a development request

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `c94b6a08710e`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
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

This is where almost every piece of work starts. You tell your agent what you want (`/spec <intent>` or any
development request), and it puts the request on exactly one delivery workflow, with your intent agreed. Small work
that needs nothing settled stays light, contract changes get a spec bundle, open directions get a proposal, and every
approval you own is asked at the right moment instead of being assumed.

Workflows, stages, gates and the three classification axes are explained in [Concepts](../concepts.md) and the
[delivery area](../areas/delivery.md).

Source: [`UC-route-development-intent`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-route-development-intent.md).

## Before you start

`devkit-spec` is installed and its `spec` bundle synchronized. The agent loads the spec constitution once per agent
context (`uv run devkit get-context spec`) before any development work.

## Step by step

The common path: a `spec`-depth `feature` in `direct` mode.

1. **Intake.** The agent enters the `spec` skill with your request and runs one bounded playbook search
   (`devkit playbook search "<query>" --limit 3 --max-bytes 4096`). If no playbook names the operation you asked for,
   it continues silently (`ADR-spec-intake-playbook-discovery`).
2. **Policy.** It reads the effective project policy:

   ```sh
   uv run devkit spec policy
   ```

   The output includes lines such as `[GIT_POLICY: worktree=auto ...]`, `[ROUTING_POLICY: depth_escalation=auto]` and
   one `[GATE_POLICY: ...]` per gate
   ([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md)).
3. **Classification.** It classifies the request by `task-kind` (`feature` or `bugfix`), then `planning-depth`
   (`session`, `spec` or `proposal`, by what must be settled before implementation, not by size), then the mode and
   `activity-effort`, and states this to you
   ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md)).
4. **Branch.** It starts `dev-<slug>`, in the current checkout (`devkit worktree start dev-<slug> --no-worktree`) or in
   its own task worktree, as the Git policy allows.
5. **Spec bundle.** It creates the bundle:

   ```sh
   uv run devkit spec new <slug>
   ```

   This writes `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` with skeleton `spec.md`, `plan.md` and `tasks.md`, bound to
   `sdd-spec-feature`, and ends with `[NEXT_CMD: devkit workflow next --unit <dir>]`
   ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)).
6. **Intent.** It records `plan-intent` from your explicit instruction.
7. **Next stage.** It runs `devkit workflow next --unit <dir>` and follows the stage, its unmet checks and the skill it
   names ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)).

## Other routes

| Classification | What happens |
| --- | --- |
| `session` depth | Intent agreed in conversation; the agent follows `sdd-session-<task-kind>` itself, writing no Unit, envelope, gate record or reconcile document. |
| `proposal` depth | `devkit spec proposal new <slug>` creates a draft `docs/proposals/PROP-<slug>/proposal.md`; continues in [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md). |
| Not starting now, or too big | Kept as one or more draft proposals in Backlog, optionally in a milestone, with `decomposed_from` or `supersedes` preserving the origin. |
| `overall-refactor` | No behavior added, several areas restructured: `sdd-overall-refactor` in `direct` mode, without a Unit, proposal or bundle. |
| Defect against a contract | `devkit spec new <slug> --workflow sdd-spec-bugfix`: only `spec.md`; the `reproduce` stage stays open until a reproduction is recorded. |
| You only ask "what next?" | `spec-next` recommends an eligible queued draft (by prerequisites, milestone, priority, size); approvals stay with you. |

## Approving the intent

Under `plan-intent` policy `ask` (the default), when goal, scope, verification, kind or depth are still open,
`devkit workflow next` prints `[WAITING: human gate:plan-intent]`. The agent asks you, and records your answer only
after you reply:

```sh
uv run devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user
uv run devkit workflow answer --unit <dir> --request gate:plan-intent --action decline --by user --note "<reason>"
```

Under `auto` the gate passes by policy, and the agent reports it as policy, never as your consent. A decline ends the
task.

## When it goes wrong

- **A playbook matches.** The agent names it in one line with the classification and waits. Confirming runs it;
  declining means it is not offered again in this conversation. Continuations and follow-ups run no search.
- **`SPEC_CONFIG_INVALID` from `devkit spec policy`.** A `[tool.spec]` key is unknown, or a gate policy is not `ask` or
  `auto` (for example `plan-intent = "off"`). The agent stops policy-dependent work until you fix `.devkit/config.toml`.
- **`SPEC_WRONG_BRANCH`.** The checkout is not on `dev-<slug>`; nothing is written. Start or continue that branch, then
  rerun `devkit spec new`.
- **`SPEC_EXISTS`.** Another document, proposal or bundle already holds the slug (`[TARGET]` lists it). Choose another
  slug.
- **A worktree is required.** Under `worktree=required`, or under `auto` when the checkout holds unrelated changes or
  another task, the agent starts `dev-<slug>` in its own worktree
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
- **A session turns out to need a contract change.** The agent raises the depth to `spec` (on its own under
  `depth_escalation=auto`, after your confirmation under `ask`), adds a spec Unit on `dev-<slug>` in the same place and
  keeps the work done so far. A depth is never lowered by itself.

## What you end up with

One workflow per task, named by its Unit or, for a session, by the conversation. Every recorded approval comes from
your instruction, your explicit answer or `auto` policy; a refused `devkit spec new` leaves the workspace unchanged.
