---
sources:
  ADR-delivery-classification: b9c9711e7d9070d27a6db699ad186d81518cf409
  ARCH-08-1-agent-output: 6b76bd19787465ed1e7ec7aee1904077cc75042c
  ARCH-08-2-resource-taxonomy: 63719695df440fdec009db0952ef2cd87d90aeea
  ARCH-08-cross-cutting: 3bf334671a435d6d6956b2a8be623aafadd34924
  CAP-ADV-agent-advisory-protocol: 572af49f008a71f993b3b82c2d457b7610529192
  CAP-COLL-work-scope-registry: 23990ff536e67c96f25dff1857c08cbd0c4c8838
  CAP-DIST-agent-projections: a80245135911b3cc82c894d3d4bac7acd895cab4
  CAP-DIST-context-and-playbooks: 73e324739a17d8af4b885dce3d6cdf2593762fc0
  CAP-DIST-manifest-spec: 44c8ec1792cd306367a6cb09a3e7ef580ee7c2c9
  CAP-DIST-sync-and-transactions: 2759dc504dc98f758acf3b168122c97f35bd1dd6
  CAP-DIST-workspace-ownership: 11ecf337d2748f5d3f69272dfaf004bd8c83d9ba
  CAP-DLV-delivery-workflows: 936dff28b6c106fdcc568a677db096421e174f9c
  CAP-DLV-human-interaction: 8e7d688916e7c8dea4d0f26e562191a4a6c423cc
  CAP-DLV-idea-incubation: c1ff3be1b056ec9d5746689d189c17fdde8bee89
  CAP-DLV-project-policy: 2af5b2fde75faecfa8260244a614fa796525de03
  CAP-DLV-proposal-incubation: d1a2660dea8664dd37171ac723f4d54305ae72be
  CAP-DLV-spec-bundles: b743cb4567d0a510097b1dc902a9a066f962c6cc
  CAP-DLV-workflow-envelopes: ba3e36ff09f879615ad60389b433b58cdf4097ee
  CAP-DLV-workflow-orchestration: 7617520b7cd6028e8eda909cf6b3171822ad02c1
  CAP-DOCS-document-model: 89280a2bb6003fe052fa7ee3ed50e368270bf9c6
  CAP-GATE-commit-gates: 2249929f68870aff9395cca7f2e149da88728c6b
  CAP-GOV-rules-engine: fc9db7b9335944c5ef2c6554f65533f2149e07c6
  CAP-HARN-agent-guidance: 3e6c66d7ea068a580cc1ee82308708d407dab6bd
  CAP-INT-mcp-services: ee8088a63e89abb3519c1744c540c41e95352ea2
  CAP-WT-task-worktrees: 2ea80d46ab9cf19504182e73b6f2bcc301e8f7db
title: Concepts
---

# Concepts

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](README.md)
- [Adopt devkit in an existing repository](journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](journeys/adopt-sdd-from-incubation.md)
- [Drive development to integration](journeys/drive-development-to-integration.md)
- [Find the right documents](journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](journeys/incubate-an-idea.md)
- [Incubate and hand off a proposal](journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](journeys/reconcile-living-spec-drift.md)
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
([`CAP-DIST-manifest-spec`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-manifest-spec.md)).

Installing a wheel only makes its bundles available. Your project chooses what is deployed in
`.devkit/config.toml`: some bundles select themselves once their package is installed (`devkit`, `advisory`,
`harness`, and `docs` and `spec` with their packages), others you add with
`devkit add <bundle>` and drop with `devkit remove <bundle>`. `devkit list` shows what is installed and selected.

The assets fall into three layers
([`ARCH-08-2-resource-taxonomy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-2-resource-taxonomy.md)):
natural-language guidance (the `AGENTS.md` block, instructions, playbooks, workflows), mechanized execution
(rules, skills, subagents, commit gates, host hooks), and the packaging layer of bundles, presets and project
configuration.

## Sync, the receipt and what you may edit

`devkit sync` deploys the selected bundles in one transaction: it either writes everything or rolls back
([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md)).
It produces three kinds of output:

- **Managed files** under `.devkit/managed/<bundle>/`: pristine copies you never edit by hand.
- **Projections**: native copies of skills and subagent roles in each agent's own directories, such as
  `.agents/skills/`, `.claude/skills/` and `.codex/skills/`
  ([`CAP-DIST-agent-projections`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-agent-projections.md)).
- **The receipt**, `.devkit/installation.json`: the committed record of every deployed file, its checksum and its
  bundle. `devkit sync --check` and `devkit status` compare the workspace against it.

To adapt an upstream asset, you do not edit the managed copy or the projection; you create a **project override**
with `devkit override`, which lives under `.devkit/overrides/` and is tracked against the upstream version it was
based on, so upstream changes show up as drift
([`CAP-DIST-workspace-ownership`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md)).

## Guidance on demand

Text in startup files costs tokens on every turn, so devkit loads guidance in stages
([`CAP-DIST-context-and-playbooks`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md)):

- The managed block in the root `AGENTS.md` holds only orientation.
- `devkit get-context <bundle>` returns a bundle's constitution, the headers of its instructions, each with the
  condition under which the agent reads its body, and the titles and summaries of the project documents in a
  directory the bundle declares (the `spec` bundle lists the steering documents under `docs/steering/`).
- **Playbooks** are occasional procedures that stay on disk. The agent finds them with `devkit playbook search`
  and retrieves one exactly with `devkit playbook get <bundle>/<id>`, and runs one only when you invoke or confirm
  it.
- **Skills** are the entry points an agent host invokes, such as `/spec`, `/spec-next` and `/incubate`;
  **subagents** are role contracts (a code reviewer, a reconcile reviewer, a worker) projected for each host. Most
  roles inherit the session's model; a project can pick a model level per role in the `[subagents]` table
  ([`CAP-DIST-agent-projections`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-agent-projections.md)).

## The Living Spec

The **Living Spec** is the durable description of the system under `docs/`. It is the source of truth: code,
guidance and this handbook follow it. Each document has an ID in its frontmatter
([`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-model.md)):

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

## Development approach: SDD or incubation

A project works in one of two **development approaches**, a shared choice in `.devkit/config.toml`:

```toml
[development]
approach = "incubation"   # absent means "sdd"
```

`uv run devkit config show` reports the effective approach and its source; `uv run devkit spec policy` repeats it
on its first line. Installing packages, selecting bundles or invoking a skill never switches it, and a checkout-local
configuration cannot override it
([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md)).

- **SDD** is everything the rest of this page describes: classification, Units, workflows, gates, envelopes and
  reconcile.
- **Incubation** suits a product that is still being discovered. The opt-in `incubation` bundle (`devkit add
  incubation`, no `devkit-spec` needed) supplies `/incubate`, which advances one useful product action at a time and
  keeps the **incubation current context** in `.devkit/incubation.md`: the current goal, the choices you made versus
  assumptions, how to run and check the product, what was actually observed, and the next action. It creates no
  spec bundles, envelopes or approvals per change; SDD lifecycle commands such as `devkit spec new` refuse with
  `SPEC_LIFECYCLE_INACTIVE` while incubation is active
  ([`CAP-DLV-idea-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-idea-incubation.md)).

Document checks and your project's own checks apply in both approaches, and SDD records that already exist keep
their checks. Moving from incubation to SDD is a deliberate step through the `sdd-baseline` playbook, described in
[Delivery](areas/delivery.md#incubation).

## Classifying work

Under SDD, every development request is classified on three axes before work starts
([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md),
[`ADR-delivery-classification`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/decisions/2026-10/20261022-delivery-classification.md)):

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
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md)).
There are two kinds:

- A **spec bundle**, `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`, anchored by `spec.md`, with `plan.md` and `tasks.md`
  beside it. `devkit spec new` creates one and binds it to its workflow
  ([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)).
- A **proposal bundle** under `docs/proposals/PROP-<slug>/`, anchored by `proposal.md`, bound to `sdd-proposal`.
  It collects materials and preliminary decisions (PADRs). Once accepted, `devkit spec proposal handoff` turns it
  into a spec bundle, carrying its body, decisions and materials along
  ([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md)).

A `session` task has no Unit: no spec, envelope or reconcile record, only the commits.

## Workflows, stages and gates

A **workflow** is a delivery procedure declared as data: a Markdown file whose frontmatter lists ordered **stages**,
each with entry and exit checks
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md)).
The agent does not work out the stage itself. It runs `devkit workflow next --unit <dir>`, which evaluates the
checks against the Unit's files and prints the first unmet stage, what is missing and which skill to follow.
`devkit workflow show <id>` prints a whole definition. Because the Unit stores only its workflow ID, a changed
definition applies to work already under way.

A **gate** is a stage that waits for a decision; the `spec` workflows use three ([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)):

- `plan-intent`: you agree on what the work is.
- `plan-accept`: you accept a proposal's direction.
- `dev-integration`: you approve landing the finished work.

Each gate is `ask` (wait for a person) or `auto` (delegated by project policy); a delegation is reported as policy,
never as your consent. A separate `exception` stage handles work that cannot continue as agreed. You see
the effective settings with `devkit spec policy`
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md)),
and decisions are recorded with `devkit workflow answer`
([`CAP-DLV-human-interaction`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-human-interaction.md)).

## Envelopes

An **envelope** is a small YAML file in `<unit>/envelopes/<kind>-<NN>.yaml` that records what a stage or a
delegated role produced: a review's findings, a reconcile check, a final change report, a worker's run
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md)).
Envelopes are never overwritten: each new one takes the next number, and workflow checks read the latest.

A `worker` envelope can carry **questions** for you, gathered into one round, or a **problem** that stopped the run.
They are closed by separate envelopes: an `answer` records your decisions, a `resolution` records how the problem
was fixed. A question is answered and a problem is resolved; neither is assumed. You write envelopes through
`devkit workflow envelope`.

## Rules and commit gates

A **governance rule** is a deterministic invariant checked by parsing, not by asking an agent to remember it
([`CAP-GOV-rules-engine`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-rules-engine.md)).
`devkit rules check` reports violations with stable rule IDs; `devkit rules fix` applies safe repairs in one pass
followed by one recheck. The engine knows nothing about specs or use cases: those rules arrive in bundles, such as
the spec rules of `devkit-spec`. You can check the working tree, the staged tree (`--staged`) or a comparison with a
base commit (`--ci --base <ref>`).

A **commit gate** runs policy at Git's commit hooks
([`CAP-GATE-commit-gates`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/gate/CAP-GATE-commit-gates.md)).
`devkit gate install` installs the wrappers; the gates themselves, such as `rules-check` and `verify-commands`,
come from bundles. Before the commit exists a gate can refuse it; after the commit it only warns.

## Advisories and the output contract

devkit's first reader is an agent, so every command answers the same way
([`ARCH-08-cross-cutting`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-cross-cutting.md),
[`ARCH-08-1-agent-output`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-08-1-agent-output.md)):

- **stdout is the result**: one-line `[KIND: ...]` sentinels, or one JSON object under `--format json`.
- **stderr carries advisories**: `[ERROR]`, `[WARN]` and `[NOTICE]` blocks, each with a stable `UPPER_SNAKE` code
  and an `[ACTION]` line naming the next step
  ([`CAP-ADV-agent-advisory-protocol`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md)).
- **Exit codes**: `0` success, `1` a negative result (violations, drift, a refused commit), `2` the command could not
  run. Warnings and notices do not change the exit code unless you pass `--strict`.

Branch on codes and sentinels, never on message text. `devkit run <command>` applies the same idea to long tool
output: the full log goes to disk and a bounded summary to stdout.

## Worktrees and parallel work

An **activity branch** is named `plan-<slug>` or `dev-<slug>`. A **task worktree** is a separate checkout of that
branch at a fixed path next to your repository, `<parent>/<repo>-wt-<branch>`, so several tasks can run at once
without touching each other's files
([`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
`devkit worktree start <branch>` creates one, `devkit worktree status` lists them, and `devkit worktree finish`,
run from the base checkout, integrates a branch and removes its worktree. Project policy decides whether worktrees are used only when needed or always.

When tasks run in parallel, `devkit spec scope` compares the documents and code paths they declare, in a registry
shared by all worktrees. An overlap informs scheduling and integration order; it never blocks a write
([`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md)).

## The Host and integration

The **Host** is the agent session you talk to. It routes your request, delegates to workers when you ask, and is
the one that carries your approval to the CLI. Integration happens in two steps
([`CAP-INT-mcp-services`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/integration/CAP-INT-mcp-services.md)):

1. `devkit integration prepare <branch> ...` validates the committed work, the policy, the readiness checks and the
   exact cleanup it would do, and returns a digest. It changes nothing.
2. After you approve what was presented, `devkit integration integrate <branch> ... --expected-digest <digest>`
   repeats every check and lands the work, either by a local fast-forward or as a pull request. If anything changed
   since the preparation, it refuses.

The digest only proves nothing moved in between; your approval is what the Host carries. Under incubation the same
two steps integrate a `session` change, with readiness based on the review, test and lint results you report and
the repository's rules rather than on a spec bundle.

## How it fits together

A typical spec-depth change runs like this:

1. `devkit sync` has deployed the `spec` bundle; the agent loads it with `devkit get-context spec`.
2. You state an intent with `/spec <intent>`. The agent reads `devkit spec policy`, proposes a classification and,
   once you confirm, creates a `dev-<slug>` branch and a spec bundle and records `plan-intent`.
3. The agent follows `devkit workflow next`: spec, plan, tasks, implementation, review envelopes, the Living Spec
   reconcile, and a final change report.
4. Rules and commit gates check every commit along the way.
5. The agent prepares integration, presents the result, and on your approval integrates and cleans up.

Under incubation the loop is shorter: you run `/incubate` with an idea or ask to resume; the agent reads
`.devkit/incubation.md`, picks the next useful action, does it, reports what was actually run and observed, and
updates the current context.

The [journeys](README.md#journeys) walk through each path; the [areas](README.md#areas) cover each capability group.
