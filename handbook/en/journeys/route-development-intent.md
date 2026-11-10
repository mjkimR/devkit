---
sources:
  ADR-decision-ledger: 5f393c36778713137fbbe406a7307153d8c42df2
  CAP-DIST-sync-and-transactions: 231d34498b080f25b3ab13f0c97c6c21475eb0ee
  CAP-DLV-delivery-workflows: 3239f814148a48be87ed6befa85cae48681e4519
  CAP-DLV-project-policy: 8887a983196e8dc5bc3936327b30ef214314e07f
  CAP-DLV-spec-bundles: 4920f894d479c8c4a54379c07ed130d81356bec3
  CAP-HARN-agent-guidance: f0895c05d6f477fbc898329866f8f673bebf2a74
  CAP-WT-task-worktrees: dae7b66b4ad24ea9aa812da83433b153f00adc50
  UC-advance-an-idea: 0ce93e70e07d5a6a3d120257d9e318f680aec3e1
  UC-plan-and-hand-off-a-proposal: e2ddba8f64ed51705b1f02682e562b20f0d34e37
  UC-route-development-intent: c5ef3381db5cefc65ec9a805cd981b37df4618c6
title: Route a development request
---

# Route a development request

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `dabb86f9e659`, generated 2026-11-05. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
- [Advance an idea](advance-an-idea.md)
- [Design necessary command entry points](design-command-entrypoints.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Explore a design problem](explore-a-design-problem.md)
- [Find the latest maintenance run](find-the-latest-maintenance-run.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Improve an interface and user flow](improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Record a maintenance run](record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](research-an-idea-and-shape-a-roadmap.md)
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

Source: [`UC-route-development-intent`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-route-development-intent.md).

## Before you start

`devkit-spec` is installed and its `spec` bundle synchronized. The repository's shared development approach decides
whether this routing applies at all: `[development] approach` in `.devkit/config.toml` is `sdd` (the default when
unset) or `adaptive-dev`, and selecting bundles never changes it. The agent checks it with `uv run devkit config show`
and loads the spec constitution once per agent context (`uv run devkit get-context spec`) before any development work.

## Step by step

The common path: a `spec`-depth `feature` in `direct` mode.

1. **Intake.** The agent confirms the effective approach is SDD and enters the `spec` skill with your request. It
   runs one bounded playbook search (`devkit playbook search "<query>" --limit 3 --max-bytes 4096`). If no playbook
   names the operation you asked for, it continues silently (`ADR-decision-ledger`).
2. **Policy.** It reads the effective project policy:

   ```sh
   uv run devkit spec policy
   ```

   The output starts with `[DEVELOPMENT_APPROACH: approach=sdd source=default]` and includes lines such as
   `[GIT_POLICY: worktree=auto ...]`, `[ROUTING_POLICY: depth_escalation=auto]` and one `[GATE_POLICY: ...]` per gate
   ([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md)).
3. **Classification.** It classifies the request by `task-kind` (`feature` or `bugfix`), then `planning-depth`
   (`session`, `spec` or `proposal`, by what must be settled before implementation, not by size), then the mode and
   `activity-effort`, and states this to you
   ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-agent-guidance.md)).
4. **Branch.** It starts `dev-<slug>`, in the current checkout (`devkit worktree start dev-<slug> --no-worktree`) or in
   its own task worktree, as the Git policy allows.
5. **Spec bundle.** It creates the bundle:

   ```sh
   uv run devkit spec new <slug>
   ```

   This writes `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` with skeleton `spec.md`, `plan.md` and `tasks.md`, bound to
   `sdd-spec-feature`, and ends with `[NEXT_CMD: uv run devkit workflow next --unit <dir>]`
   ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)).
6. **Scope.** It states the scope authorized by your explicit instruction; no intent approval record is created.
7. **Next stage.** It runs `devkit workflow next --unit <dir>` and follows the stage, its unmet checks and the skill it
   names ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)).

## Other routes

| Classification | What happens |
| --- | --- |
| Approach is `adaptive-dev` | No SDD routing: the agent follows the project's adaptive development guidance and its independent document and project checks, creating no Unit and choosing no depth. See [Advance an idea](advance-an-idea.md). Units already bound to SDD keep their checks. |
| `session` depth | Intent agreed in conversation; the agent follows `sdd-session-<task-kind>` itself, writing no Unit, envelope, gate record or reconcile document. |
| `proposal` depth | `devkit spec proposal new <slug>` creates a draft `docs/proposals/PROP-<slug>/proposal.md`; continues in [Plan and hand off a proposal](plan-and-hand-off-a-proposal.md). |
| Not starting now, or too big | Kept as one or more draft proposals in Backlog, optionally in a milestone, with `decomposed_from` or `supersedes` preserving the origin. Work that would need two or more specs or a different `task-kind` is `size: XL` and is decomposed before Planning. |
| `overall-refactor` | No behavior added, several areas restructured: `sdd-overall-refactor` in `direct` mode, without a Unit, proposal or bundle. |
| Defect against a contract | `devkit spec new <slug> --workflow sdd-spec-bugfix`: only `spec.md`; the `reproduce` stage stays open until a reproduction is recorded. |
| You only ask "what next?" | `spec-next` recommends an eligible queued draft (by prerequisites, milestone, priority, size); `needs_decompose` and `XL` drafts are reported as Backlog decomposition through the `decomposer` role; approvals stay with you. |

## Authorizing the task

Your explicit instruction authorizes the stated goal and scope. The agent clarifies unresolved details before
starting dependent work; it creates no intent gate record. Later proposal acceptance, Development start and final
integration retain their independent approval policies.

## When it goes wrong

- **A playbook matches.** The agent names it in one line with the classification and waits. Confirming runs it;
  declining means it is not offered again in this conversation. Continuations and follow-ups run no search.
- **`SPEC_LIFECYCLE_INACTIVE` from `devkit spec new` or `devkit spec proposal new`.** The approach is adaptive development, so
  SDD Units cannot be created; nothing is written. Switching to SDD is your explicit decision, described in
  [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md).
- **`DEVELOPMENT_CONFIG_INVALID`.** The `[development]` table has an unknown key or value; policy-dependent commands
  refuse until you fix `.devkit/config.toml`.
- **`SPEC_CONFIG_INVALID` from `devkit spec policy`.** A `[tool.spec]` key is unknown, or a gate policy is not `ask` or
  `auto` (for example `plan-accept = "off"`). The agent stops policy-dependent work until you fix `.devkit/config.toml`.
- **`SPEC_WRONG_BRANCH`.** The checkout is not on `dev-<slug>`; nothing is written. Start or continue that branch, then
  rerun `devkit spec new`.
- **`SPEC_EXISTS`.** Another document, proposal or bundle already holds the slug (`[TARGET]` lists it). Choose another
  slug.
- **A worktree is required.** Under `worktree=required`, or under `auto` when the checkout holds unrelated changes or
  another task, the agent starts `dev-<slug>` in its own worktree
  ([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
- **A session turns out to need a contract change.** The agent raises the depth to `spec` (on its own under
  `depth_escalation=auto`, after your confirmation under `ask`), adds a spec Unit on `dev-<slug>` in the same place and
  keeps the work done so far. A depth is never lowered by itself.

## What you end up with

One workflow per task, named by its Unit or, for a session, by the conversation. Every recorded approval comes from
your instruction, your explicit answer or `auto` policy; a refused `devkit spec new` leaves the workspace unchanged.
