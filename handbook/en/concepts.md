---
sources:
  ADR-delivery-classification: 54062bf6f8923b415cde2b503111a6c682325dee
  ARCH-08-1-agent-output: 86a790e9a7ff89af5e69e19a19746d3e0cde4f85
  ARCH-08-2-resource-taxonomy: bc6fb555940924532404e5d99a71e74cf0cd16cc
  ARCH-08-cross-cutting: 3bf334671a435d6d6956b2a8be623aafadd34924
  CAP-ADV-agent-advisory-protocol: 572af49f008a71f993b3b82c2d457b7610529192
  CAP-COLL-work-scope-registry: 648447161142a20d42839609f502b027f5c7d403
  CAP-DIST-agent-projections: d3811102c439ab16edeb87f4c7b0de4868ae1d4f
  CAP-DIST-context-and-playbooks: f8b3284cb8b92384bac15fd49128ed43e012bb5c
  CAP-DIST-manifest-spec: c36062832b0a088f0cdfba7bea04c6eceb3ae0d4
  CAP-DIST-sync-and-transactions: 231d34498b080f25b3ab13f0c97c6c21475eb0ee
  CAP-DIST-workspace-ownership: d23d1e146e4a38ea8021b4ed5f52c39e529a80cd
  CAP-DLV-adaptive-development: 120b77c7814f67b082a728d0fdbec0108b852b00
  CAP-DLV-deep-research: 08c383e1a9a76e3e47679db645eeb7a751126b8e
  CAP-DLV-delivery-workflows: 3239f814148a48be87ed6befa85cae48681e4519
  CAP-DLV-design-exploration: 4fad9083aa058047d39e6956ff63b76f8232bd10
  CAP-DLV-human-interaction: 7926c28e1951896774e56bd201fbd5e3a474a673
  CAP-DLV-project-policy: 8887a983196e8dc5bc3936327b30ef214314e07f
  CAP-DLV-proposal-planning: 65becdbbd5615d0f69c7fae14d1a0c91d91204d1
  CAP-DLV-spec-bundles: 4920f894d479c8c4a54379c07ed130d81356bec3
  CAP-DLV-uiux-improvement: 5b4b328d5933e2bcd67b719eff3c78a10e2386f4
  CAP-DLV-workflow-envelopes: d9930340d63dab836aa1938f2e6cd2a8c4a23230
  CAP-DLV-workflow-orchestration: a84a1b608390b8b2c825c2be5d8ff5a8f101e828
  CAP-DOCS-document-model: 016e923f03d861ba71b8fe6a4a88fed61a07ff6a
  CAP-GATE-commit-gates: 2249929f68870aff9395cca7f2e149da88728c6b
  CAP-GOV-rules-engine: 114f633a9af2f4a675d6ce0cc37291384ce1b5b7
  CAP-HARN-agent-guidance: f0895c05d6f477fbc898329866f8f673bebf2a74
  CAP-INT-mcp-services: 6978ff46427e1a1091c65b488ca9c76734b4a4c0
  CAP-WT-task-worktrees: dae7b66b4ad24ea9aa812da83433b153f00adc50
title: Concepts
---

# Concepts

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `dabb86f9e659`, generated 2026-11-05. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](README.md)
- [Adopt devkit in an existing repository](journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](journeys/adopt-sdd-from-adaptive-development.md)
- [Advance an idea](journeys/advance-an-idea.md)
- [Design necessary command entry points](journeys/design-command-entrypoints.md)
- [Drive development to integration](journeys/drive-development-to-integration.md)
- [Explore a design problem](journeys/explore-a-design-problem.md)
- [Find the latest maintenance run](journeys/find-the-latest-maintenance-run.md)
- [Find the right documents](journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](journeys/handle-delivery-problems-and-exceptions.md)
- [Improve an interface and user flow](journeys/improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](journeys/keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](journeys/plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](journeys/reconcile-living-spec-drift.md)
- [Record a maintenance run](journeys/record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](journeys/research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](journeys/route-development-intent.md)
- [Run parallel work safely](journeys/run-parallel-work-safely.md)
- [Speed up selected slow operations](journeys/speed-up-selected-slow-operations.md)
- [Advisories](areas/advisory.md)
- [Agent-first CLI toolkit](areas/cli.md)
- [Collaboration](areas/collaboration.md)
- [Compact command output](areas/compact.md)
- [Delivery](areas/delivery.md)
- [Distribution](areas/distribution.md)
- [Documents](areas/documents.md)
- [Commit gates](areas/gate.md)
- [Generated Files](areas/generated.md)
- [Governance rules](areas/governance.md)
- [Harness](areas/harness.md)
- [Host](areas/host.md)
- [Integration](areas/integration.md)
- [MCP](areas/mcp.md)
- [Search](areas/search.md)
- [Traceability](areas/traceability.md)
- [Viewer](areas/viewer.md)
- [Worktree](areas/worktree.md)
- [Decisions](decisions.md)
- [Changes](changes.md)
- [Glossary](glossary.md)
<!-- /handbook:generated -->

This page introduces the ideas the rest of the handbook relies on, in the order you meet them: first how guidance
reaches an agent, then how work is organized and checked, then how it lands. Each section links to the contract
that defines the concept; the [Glossary](glossary.md) gives short definitions.

## Bundles: the unit of distribution

A **bundle** is a named set of agent assets declared in a `bundle.toml`: instructions, playbooks, rules, workflows,
skills, subagent roles, commit gates, host hooks and guidance fragments. A bundle ships inside a Python wheel (a
content package) or lives in your own repository. A **preset** is a named selection of a bundle's assets, such as
`core` or `default`
([`CAP-DIST-manifest-spec`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-manifest-spec.md)).

Installing a wheel only makes its bundles available. Your project chooses what is deployed in
`.devkit/config.toml`: some bundles select themselves once their package is installed (`devkit`, `advisory`,
`harness`, and `docs` and `spec` with their packages), others you add with
`devkit add <bundle>` and drop with `devkit remove <bundle>`. `devkit list` shows what is installed and selected.

The assets fall into three layers
([`ARCH-08-2-resource-taxonomy`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/architecture/ARCH-08-2-resource-taxonomy.md)):
natural-language guidance (the `AGENTS.md` block, instructions, playbooks, workflows), mechanized execution
(rules, skills, subagents, commit gates, host hooks), and the packaging layer of bundles, presets and project
configuration.

## Sync, the receipt and what you may edit

`devkit sync` deploys the selected bundles in one transaction: it either writes everything or rolls back
([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md)).
It produces three kinds of output:

- **Managed files** under `.devkit/managed/<bundle>/`: pristine copies you never edit by hand.
- **Projections**: native copies of skills and subagent roles in each agent's own directories, such as
  `.agents/skills/`, `.claude/skills/` and `.codex/skills/`
  ([`CAP-DIST-agent-projections`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-agent-projections.md)).
- **The receipt**, `.devkit/installation.json`: the committed record of every deployed file, its checksum and its
  bundle. `devkit sync --check` and `devkit status` compare the workspace against it.

To adapt an upstream asset, you do not edit the managed copy or the projection; you create a **project override**
with `devkit override`, which lives under `.devkit/overrides/` and is tracked against the upstream version it was
based on, so upstream changes show up as drift
([`CAP-DIST-workspace-ownership`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md)).

## Guidance on demand

Text in startup files costs tokens on every turn, so devkit loads guidance in stages
([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md)):

- The managed block in the root `AGENTS.md` holds only orientation.
- `devkit get-context <bundle>` returns a bundle's constitution, the headers of its instructions, each with the
  condition under which the agent reads its body, and the titles and summaries of the project documents in a
  directory the bundle declares (the `docs` bundle lists root and applicable namespace steering documents).
- **Playbooks** are occasional procedures that stay on disk. The agent finds them with `devkit playbook search`
  and retrieves one exactly with `devkit playbook get <bundle>/<id>`, and runs one only when you invoke or confirm
  it.
- **Skills** are the entry points an agent host invokes, such as `/spec`, `/spec-next` and `/adaptive-dev`;
  **subagents** are role contracts (a code reviewer, a reconcile reviewer, a worker) projected for each host. Most
  roles inherit the session's model; a project can pick a model level per role in the `[subagents]` table
  ([`CAP-DIST-agent-projections`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-agent-projections.md)).

## The Living Spec

The **Living Spec** is the durable description of the system under `docs/`. It is the source of truth: code,
guidance and this handbook follow it. Each document has an ID in its frontmatter
([`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/documents/CAP-DOCS-document-model.md)):

| Kind | ID | Describes |
| --- | --- | --- |
| Architecture | `ARCH-...` | System structure, runtime flows, cross-cutting concepts |
| Capability | `CAP-<AREA>-<slug>` | The contract of one behavior, grouped by area |
| Use case | `UC-<slug>` | How an actor reaches a goal across capabilities |
| Decision | `ADR-<slug>` | Why a structural choice was made |
| Proposal | `PROP-<slug>` | An idea being shaped before it becomes a spec |
| Milestone | `MS-<slug>` | A roadmap theme with an exit condition |

Capabilities and use cases cross-reference each other in their frontmatter. Work in progress lives apart from this, under `specs/`: a spec describes a change,
and when it completes, its effect is written back into `docs/` (**reconcile**). The `devkit-docs` package owns
the document model; `devkit docs resolve`, `devkit docs refs`, `devkit docs list` and `devkit docs search` find
documents by ID, reference, kind or meaning.

## Development approach: SDD or adaptive development

A project works in one of two **development approaches**, a shared choice in `.devkit/config.toml`:

```toml
[development]
approach = "adaptive-dev"   # absent means "sdd"
```

`uv run devkit config show` reports the effective approach and its source; `uv run devkit spec policy` repeats it
on its first line. Installing packages, selecting bundles or invoking a skill never switches it, and a checkout-local
configuration cannot override it
([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md)).

- **SDD** is everything the rest of this page describes: classification, Units, workflows, gates, envelopes and
  reconcile.
- **Adaptive development** suits a product that is still being discovered. The opt-in `adaptive-dev` bundle (`devkit add adaptive-dev`, no `devkit-spec` needed) supplies `/adaptive-dev`, which advances one useful product action at a time and
  keeps the **adaptive-dev current context** in `.devkit/adaptive-dev.md`: the current goal, the choices you made versus
  assumptions, how to run and check the product, what was actually observed, and the next action. It creates no
  spec bundles, envelopes or approvals per change; SDD lifecycle commands such as `devkit spec new` refuse with
  `SPEC_LIFECYCLE_INACTIVE` while adaptive development is active
  ([`CAP-DLV-adaptive-development`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-adaptive-development.md)).

Document checks and your project's own checks apply in both approaches, and SDD records that already exist keep
their checks. Moving from adaptive-dev to SDD is a deliberate step through the `sdd-baseline` playbook, described in
[Delivery](areas/delivery.md#adaptive-development).

## Classifying work

Under SDD, every development request is classified on three axes before work starts
([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-agent-guidance.md),
[`ADR-delivery-classification`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-delivery-classification.md)):

- **`task-kind`**: `feature`, `bugfix` or `overall-refactor`.
- **`planning-depth`**: what has to be settled before implementation, not how big the change is.
  - `session`: nothing needs settling; the work is done directly, without a work unit.
  - `spec`: a contract changes, so a spec bundle records requirements, plan and tasks first.
  - `proposal`: the direction itself is open, so a proposal is shaped and accepted before a spec exists.
- **`activity-effort`**: `low`, `medium` or `high`, setting how thorough review and verification are.

The agent proposes the classification; you confirm it. The combination names exactly one workflow,
`sdd-<planning-depth>[-<task-kind>]` (for example `sdd-spec-feature`), and the depth only rises during the work,
except through a proposal's handoff or a reclassification you decide.

Work moves through three **activities**. **Backlog** holds requests that do not start now, as draft proposals, and
ranks what to pick up next. **Planning** shapes a proposal on a `plan-<slug>` branch. **Development** implements on
a `dev-<slug>` branch. Each activity runs in a mode: `direct` by default, or `local-orchestrated` when you ask the
agent to delegate to workers in their own worktrees.

## Units, specs and proposals

A **Unit** is a directory a workflow drives, recognized by its anchor file
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md)).
There are two kinds:

- A **spec bundle**, `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`, anchored by `spec.md`, with `plan.md` and `tasks.md`
  beside it. `devkit spec new` creates one and binds it to its workflow
  ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)).
- A **proposal bundle** under `docs/proposals/PROP-<slug>/`, anchored by `proposal.md`, bound to `sdd-proposal`.
  It collects materials and preliminary decisions (PADRs). Once accepted, `devkit spec proposal handoff` turns it
  into a spec bundle, carrying its body, decisions and materials along
  ([`CAP-DLV-proposal-planning`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-proposal-planning.md)).

A `session` task has no Unit: no spec, envelope or reconcile record, only the commits.

## Workflows, stages and gates

A **workflow** is a delivery procedure declared as data: a Markdown file whose frontmatter lists ordered **stages**,
each with entry and exit checks
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md)).
The agent does not work out the stage itself. It runs `devkit workflow next --unit <dir>`, which evaluates the
checks against the Unit's files and prints the first unmet stage, what is missing and which skill to follow.
`devkit workflow show <id>` prints a whole definition. Because the Unit stores only its workflow ID, a changed
definition applies to work already under way.

A **gate** is a stage that waits for a decision; the `spec` workflows use three ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)):

- `plan-intent`: you agree on what the work is.
- `plan-accept`: you accept a proposal's direction.
- `dev-integration`: you approve landing the finished work.

Each gate is `ask` (wait for a person) or `auto` (delegated by project policy); a delegation is reported as policy,
never as your consent. A separate `exception` stage handles work that cannot continue as agreed. You see
the effective settings with `devkit spec policy`
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md)),
and decisions are recorded with `devkit workflow answer`
([`CAP-DLV-human-interaction`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-human-interaction.md)).

## Envelopes

An **envelope** is a small YAML file in `<unit>/envelopes/<kind>-<NN>.yaml` that records what a stage or a
delegated role produced: a review's findings, a reconcile check, a final change report, a worker's run
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md)).
Envelopes are never overwritten: each new one takes the next number, and workflow checks read the latest.

A `worker` envelope can carry **questions** for you, gathered into one round, or a **problem** that stopped the run.
They are closed by separate envelopes: an `answer` records your decisions, a `resolution` records how the problem
was fixed. A question is answered and a problem is resolved; neither is assumed. You write envelopes through
`devkit workflow envelope`.

## Rules and commit gates

A **governance rule** is a deterministic invariant checked by parsing, not by asking an agent to remember it
([`CAP-GOV-rules-engine`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/governance/CAP-GOV-rules-engine.md)).
`devkit rules check` reports violations with stable rule IDs; `devkit rules fix` applies safe repairs in one pass
followed by one recheck. The engine knows nothing about specs or use cases: those rules arrive in bundles, such as
the spec rules of `devkit-spec`. You can check the working tree, the staged tree (`--staged`) or a comparison with a
base commit (`--ci --base <ref>`).

A **commit gate** runs policy at Git's commit hooks
([`CAP-GATE-commit-gates`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/gate/CAP-GATE-commit-gates.md)).
`devkit gate install` installs the wrappers; the gates themselves, such as `rules-check` and `verify-commands`,
come from bundles. Before the commit exists a gate can refuse it; after the commit it only warns.

## Advisories and the output contract

devkit's first reader is an agent, so every command answers the same way
([`ARCH-08-cross-cutting`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/architecture/ARCH-08-cross-cutting.md),
[`ARCH-08-1-agent-output`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/architecture/ARCH-08-1-agent-output.md)):

- **stdout is the result**: one-line `[KIND: ...]` sentinels, or one JSON object under `--format json`.
- **stderr carries advisories**: `[ERROR]`, `[WARN]` and `[NOTICE]` blocks, each with a stable `UPPER_SNAKE` code
  and an `[ACTION]` line naming the next step
  ([`CAP-ADV-agent-advisory-protocol`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md)).
- **Exit codes**: `0` success, `1` a negative result (violations, drift, a refused commit), `2` the command could not
  run. Warnings and notices do not change the exit code unless you pass `--strict`.

Branch on codes and sentinels, never on message text. `devkit run <command>` applies the same idea to long tool
output: the full log goes to disk and a bounded summary to stdout.

## Worktrees and parallel work

An **activity branch** is named `plan-<slug>` or `dev-<slug>`. A **task worktree** is a separate checkout of that
branch at a fixed path next to your repository, `<parent>/<repo>-wt-<branch>`, so several tasks can run at once
without touching each other's files
([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
`devkit worktree start <branch>` creates one, `devkit worktree status` lists them, and `devkit worktree finish`,
run from the base checkout, integrates a branch and removes its worktree. Project policy decides whether worktrees are used only when needed or always.

When tasks run in parallel, `devkit spec scope` compares the documents and code paths they declare, using observations of declarations and Git changes across worktrees. An overlap informs scheduling and integration order; it never blocks a write
([`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md)).

## The Host and integration

The **Host** is the main agent session you talk to. It owns decisions, scheduling and result acceptance.
In local-orchestrated mode, a reusable **git-operator** executes exact currently authorized lifecycle jobs;
it makes no product decision and grants no approval.

The Host checks branch content through the source runtime, then uses
`uv run devkit integration prepare <branch> --route local` to bind Git revisions, policy and cleanup scope.
Under `ask`, you approve those effects before
`uv run devkit integration integrate <branch> --route local --expected-digest <digest>`.
Shared-base `auto` authorizes the local route by policy.
The digest detects changed scope and authenticates no conversational approval.

Integration checks Git effects, not content readiness. Both SDD and adaptive development use the same branch-only
commands, without task labels, claims or provider selection. Confirmed landing returns `landed_sha` and
`verification=pending`. The Host then synchronizes the landed runtime, regenerates stale tracked artifacts and
runs final project checks in fresh processes. Delivery finishes only when those checks pass.
See [Integration](areas/integration.md) for routes and recovery.

## How it fits together

A typical spec-depth change runs like this:

1. `devkit sync` has deployed the `spec` bundle; the agent loads it with `devkit get-context spec`.
2. You state an intent with `/spec <intent>`. The agent reads `devkit spec policy`, proposes a classification and,
   once you confirm, creates a `dev-<slug>` branch and a spec bundle and records `plan-intent`.
3. The agent follows `devkit workflow next`: spec, plan, tasks, implementation, review envelopes, the Living Spec
   reconcile, and a final change report.
4. Rules and commit gates check every commit along the way.
5. The agent prepares integration, presents the result, and on your approval integrates and cleans up.

Under adaptive development the loop is shorter: you run `/adaptive-dev` with an idea or ask to resume; the agent reads
`.devkit/adaptive-dev.md`, picks the next useful action, does it, reports what was actually run and observed, and
updates the current context.

The [journeys](README.md#journeys) walk through each path; the [areas](README.md#areas) cover each capability group.

## Explicit catalog entries and context

`adaptive-dev` replaces the former incubation identifiers: use `/adaptive-dev`, the `adaptive-dev` bundle and
`.devkit/adaptive-dev.md`. The old bundle/approach values are rejected and the old context is not a fallback.
Research material is cited by its `MAT-<slug>` ID instead of copied into current context.

`deep-research`, `design-explore` and `uiux-improve` are opt-in user-only entries. Their skill-local roles are loaded
only for an assignment; selecting a bundle grants no implementation or publication authority.
Research keeps one indexed material; exploration returns directions in conversation unless a destination is requested;
UI/UX improvement implements requested changes through the consumer workflow and reports actual usage checks.

`proposal-handoff` is the fourth approval boundary: it decides whether accepted Planning starts Development,
including worktree/setup effects. It is separate from accepting the direction and landing Development.
