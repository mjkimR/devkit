---
sources:
  ADR-spec-intake-playbook-discovery: 16bc21ff4c9228e34f7634d89dd64da91c60b50a
  CAP-DIST-sync-and-transactions: 2759dc504dc98f758acf3b168122c97f35bd1dd6
  CAP-DLV-delivery-workflows: 936dff28b6c106fdcc568a677db096421e174f9c
  CAP-DLV-project-policy: 2af5b2fde75faecfa8260244a614fa796525de03
  CAP-DLV-spec-bundles: b743cb4567d0a510097b1dc902a9a066f962c6cc
  CAP-HARN-agent-guidance: 3e6c66d7ea068a580cc1ee82308708d407dab6bd
  CAP-WT-task-worktrees: 2ea80d46ab9cf19504182e73b6f2bcc301e8f7db
  UC-incubate-an-idea: ba73c68267ca32979313705291d52f89febb5985
  UC-incubate-and-hand-off-a-proposal: 725298a4a0f09bb0316fe05459aad3097bcc2a4e
  UC-route-development-intent: b3ee3ac9c76d14a4b97f0645eef8954f339330d5
title: Route a development request
---

# Route a development request

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
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](incubate-an-idea.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
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

This is where almost every piece of work starts in a repository that uses spec-driven development (SDD). You tell
your agent what you want (`/spec <intent>` or any development request), and it puts the request on exactly one
delivery workflow, with your intent agreed. Small work that needs nothing settled stays light, contract changes get a
spec bundle, open directions get a proposal, and every approval you own is asked at the right moment instead of being
assumed.

Workflows, stages, gates and the three classification axes are explained in [Concepts](../concepts.md) and the
[delivery area](../areas/delivery.md).

Source: [`UC-route-development-intent`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-route-development-intent.md).

## Before you start

`devkit-spec` is installed and its `spec` bundle synchronized. The repository's shared development approach decides
whether this routing applies at all: `[development] approach` in `.devkit/config.toml` is `sdd` (the default when
unset) or `incubation`, and selecting bundles never changes it. The agent checks it with `uv run devkit config show`
and loads the spec constitution once per agent context (`uv run devkit get-context spec`) before any development work.

## Step by step

The common path: a `spec`-depth `feature` in `direct` mode.

1. **Intake.** The agent confirms the effective approach is SDD and enters the `spec` skill with your request. It
   runs one bounded playbook search (`devkit playbook search "<query>" --limit 3 --max-bytes 4096`). If no playbook
   names the operation you asked for, it continues silently (`ADR-spec-intake-playbook-discovery`).
2. **Policy.** It reads the effective project policy:

   ```sh
   uv run devkit spec policy
   ```

   The output starts with `[DEVELOPMENT_APPROACH: approach=sdd source=default]` and includes lines such as
   `[GIT_POLICY: worktree=auto ...]`, `[ROUTING_POLICY: depth_escalation=auto]` and one `[GATE_POLICY: ...]` per gate
   ([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md)).
3. **Classification.** It classifies the request by `task-kind` (`feature` or `bugfix`), then `planning-depth`
   (`session`, `spec` or `proposal`, by what must be settled before implementation, not by size), then the mode and
   `activity-effort`, and states this to you
   ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md)).
4. **Branch.** It starts `dev-<slug>`, in the current checkout (`devkit worktree start dev-<slug> --no-worktree`) or in
   its own task worktree, as the Git policy allows.
5. **Spec bundle.** It creates the bundle:

   ```sh
   uv run devkit spec new <slug>
   ```

   This writes `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` with skeleton `spec.md`, `plan.md` and `tasks.md`, bound to
   `sdd-spec-feature`, and ends with `[NEXT_CMD: uv run devkit workflow next --unit <dir>]`
   ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)).
6. **Intent.** It records `plan-intent` from your explicit instruction.
7. **Next stage.** It runs `devkit workflow next --unit <dir>` and follows the stage, its unmet checks and the skill it
   names ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)).

## Other routes

| Classification | What happens |
| --- | --- |
| Approach is `incubation` | No SDD routing: the agent follows the project's incubation guidance and its independent document and project checks, creating no Unit and choosing no depth. See [Incubate an idea](incubate-an-idea.md). Units already bound to SDD keep their checks. |
| `session` depth | Intent agreed in conversation; the agent follows `sdd-session-<task-kind>` itself, writing no Unit, envelope, gate record or reconcile document. |
| `proposal` depth | `devkit spec proposal new <slug>` creates a draft `docs/proposals/PROP-<slug>/proposal.md`; continues in [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md). |
| Not starting now, or too big | Kept as one or more draft proposals in Backlog, optionally in a milestone, with `decomposed_from` or `supersedes` preserving the origin. Work that would need two or more specs or a different `task-kind` is `size: XL` and is decomposed before `plan-intent`. |
| `overall-refactor` | No behavior added, several areas restructured: `sdd-overall-refactor` in `direct` mode, without a Unit, proposal or bundle. |
| Defect against a contract | `devkit spec new <slug> --workflow sdd-spec-bugfix`: only `spec.md`; the `reproduce` stage stays open until a reproduction is recorded. |
| You only ask "what next?" | `spec-next` recommends an eligible queued draft (by prerequisites, milestone, priority, size); `needs_decompose` and `XL` drafts are reported as Backlog decomposition through the `decomposer` role; approvals stay with you. |

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
- **`SPEC_LIFECYCLE_INACTIVE` from `devkit spec new` or `devkit spec proposal new`.** The approach is incubation, so
  SDD Units cannot be created; nothing is written. Switching to SDD is your explicit decision, described in
  [Adopt SDD from incubation](adopt-sdd-from-incubation.md).
- **`DEVELOPMENT_CONFIG_INVALID`.** The `[development]` table has an unknown key or value; policy-dependent commands
  refuse until you fix `.devkit/config.toml`.
- **`SPEC_CONFIG_INVALID` from `devkit spec policy`.** A `[tool.spec]` key is unknown, or a gate policy is not `ask` or
  `auto` (for example `plan-intent = "off"`). The agent stops policy-dependent work until you fix `.devkit/config.toml`.
- **`SPEC_WRONG_BRANCH`.** The checkout is not on `dev-<slug>`; nothing is written. Start or continue that branch, then
  rerun `devkit spec new`.
- **`SPEC_EXISTS`.** Another document, proposal or bundle already holds the slug (`[TARGET]` lists it). Choose another
  slug.
- **A worktree is required.** Under `worktree=required`, or under `auto` when the checkout holds unrelated changes or
  another task, the agent starts `dev-<slug>` in its own worktree
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
- **A session turns out to need a contract change.** The agent raises the depth to `spec` (on its own under
  `depth_escalation=auto`, after your confirmation under `ask`), adds a spec Unit on `dev-<slug>` in the same place and
  keeps the work done so far. A depth is never lowered by itself.

## What you end up with

One workflow per task, named by its Unit or, for a session, by the conversation. Every recorded approval comes from
your instruction, your explicit answer or `auto` policy; a refused `devkit spec new` leaves the workspace unchanged.
