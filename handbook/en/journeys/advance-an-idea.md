---
sources:
  CAP-DIST-sync-and-transactions: 231d34498b080f25b3ab13f0c97c6c21475eb0ee
  CAP-DLV-adaptive-development: 120b77c7814f67b082a728d0fdbec0108b852b00
  CAP-HARN-agent-guidance: f0895c05d6f477fbc898329866f8f673bebf2a74
  UC-advance-an-idea: 0ce93e70e07d5a6a3d120257d9e318f680aec3e1
title: Advance an idea
---

# Advance an idea

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `dabb86f9e659`, generated 2026-11-05. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
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

Not every idea starts with a settled contract. When you are still finding out what a product should be, spec-driven
development (SDD) asks for more records than the work can use. Adaptive development is the lighter alternative: your agent
advances the next useful product action (a question, a bounded experiment, a representative implementation, a usage
check), verifies what it actually ran, and keeps a short file of current facts so the next session can pick up
where this one stopped. There are no per-change Units, approvals or envelopes, and a small app can stay in
adaptive development for good.

Source: [`UC-advance-an-idea`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-advance-an-idea.md),
contract [`CAP-DLV-adaptive-development`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-adaptive-development.md),
entry skill [`adaptive-dev`](https://github.com/mjkimR/devkit/blob/v0.1.6/packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md).
This is unrelated to proposal Planning in SDD, which is
[Plan and hand off a proposal](plan-and-hand-off-a-proposal.md).

## Before you start

- Install `devkit-docs` and `devkit-catalog`, then select the opt-in bundle: `uv run devkit add adaptive-dev`
  (preset `core`). `devkit-spec` is not required. The bundle deploys `/adaptive-dev`, its guidance pointer, three
  optional support roles and a current-context template; selecting it seeds no product files.
- Set the shared development approach in `.devkit/config.toml`:

  ```toml
  [development]
  approach = "adaptive-dev"
  ```

  The default is `sdd`. Selecting the bundle never changes the approach; only this setting does
  ([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md)).
- The repository's ordinary environment (build, test and run commands) is available.

## Step by step

1. **Invoke.** Run `/adaptive-dev` with the action you want, or ask the agent to resume the idea. It loads
   `uv run devkit get-context adaptive-dev` once per agent context, and `get-context docs` before document work.
2. **Check the approach.** The agent runs `uv run devkit config show` and reads
   `configuration.development.approach`. Product work only starts under `adaptive-dev`.
3. **Recover current facts.** It reads `.devkit/adaptive-dev.md` if present, the run instructions and the
   implementation: the current goal, users, constraints, the choices you made, the assumptions and the last observed
   evidence. It does not try to reconstruct discarded history.
4. **Pick the next action.** From what is still undecided or unproven, it chooses one useful step. If that step needs
   a product decision you have not made, it asks only that question, with its recommendation.
5. **Do it.** It performs the bounded action inside the agreed goal. Research and experiments separate observations
   from assumptions, and an experiment names its write boundary and stop condition. Retained code, tests and
   documents can be rebuilt freely while the goal holds.
6. **Verify.** It exercises the representative flow and runs the applicable project checks, reporting what actually
   ran on which source. A skipped, unavailable or inconclusive check stays unverified.
7. **Leave context.** It updates `.devkit/adaptive-dev.md` and reports the outcome, limitations and next action.

## Optional support roles

The agent may delegate a separable question; no iteration needs every role. Each gets one goal, explicit boundaries,
the source identity and the expected output, and the agent checks the actual return (and diff) before using it.

| Role | Returns | Boundary |
| --- | --- | --- |
| `product-clarifier` | Candidate users and problems, alternatives, missing questions; never an invented decision | Read-only |
| `product-researcher` | Evidence for one decision, or a bounded experiment with its paths, commands and limits | Read-only by default; writes only an assigned prototype; no commits |
| `usage-reviewer` | Expected versus observed usage of a representative flow, with failure conditions | Read-only product source; assigned test data only; no commits |

## The current-context file

`.devkit/adaptive-dev.md` is ordinary project-owned Markdown that the agent keeps current: goal, users, constraints and
flow; your decisions apart from implementation choices and assumptions; run and check commands with the evidence they
produced on which source; open limitations and questions; and the next useful action. It has no ID, status or schema,
superseded experiments are removed rather than logged, and sync never overwrites it. Roles return evidence and never
edit it. A later session rechecks what it relies on instead of trusting a stale entry.

## When it goes wrong

- **The approach is `sdd`.** The agent stops product work, leaves files and context unchanged, and names the setting
  to change. It never switches the approach on its own.
- **`DEVELOPMENT_CONFIG_INVALID`.** The `[development]` table is malformed; `devkit config show` exits `2`. The agent
  reports the error and does no product work until you fix it.
- **Context is missing or stale.** The agent rebuilds current facts from the implementation, run instructions and
  your answers, without asking for a full backlog or history.
- **The goal or a constraint changes.** Dependent work waits for your direction.
- **A role fails or leaves its scope.** The agent reports the actual partial state and does not count that return as
  evidence, without discarding anyone else's work.
- **Intended behavior fails.** The agent repairs it within the goal and reruns the affected checks.
- **Evidence is missing.** The check is reported unverified and the gap goes into the next action; nothing is claimed
  as passed.
- **You ask to adopt SDD.** The agent explains that spec assets can be prepared while adaptive development stays active, and
  points you to the separate baseline procedure: [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md). This
  journey never activates SDD.

## What you end up with

An observed outcome for the action, the current facts and instructions needed to resume it, and explicit limitations
and next step. No approach switch, invented product decision or skipped-as-passed check is ever claimed, and
unrelated edits and existing SDD history stay as they were. Area: [Delivery](../areas/delivery.md).
