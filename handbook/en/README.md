---
sources:
  ARCH-01-introduction-and-goals: 9057d8c207781509028fb8f0335905634db97a9c
  ARCH-03-context: da101a47ee997b3705720a96951abc661301ea62
  ARCH-05-1-containers: cb3b0e165eb94c1f1bff13af613ae3864be8a451
  CAP-DIST-content-packages: 71d426703b854a24bdce4cd0c44b130ed8a106dc
  CAP-DIST-sync-and-transactions: 2759dc504dc98f758acf3b168122c97f35bd1dd6
  CAP-DLV-idea-incubation: c1ff3be1b056ec9d5746689d189c17fdde8bee89
  CAP-DLV-incubation-sdd-baseline: 8899fda9b8975eb5cf9848c226df2ee8f43abc14
  CAP-DLV-release-handbook: ef9a59be9a4712194710b04969671a12582c28d7
title: devkit handbook
---

# devkit handbook

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `022b9f03bbd2`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

devkit is a developer toolkit for repositories where AI coding agents (Codex, Claude Code, Antigravity) do much of
the work. It gives every agent in a repository the same guidance, the same deterministic checks and the same
delivery procedure, and it answers in a form an agent can act on without guessing.

This handbook is written for you, the developer who sets devkit up and works with it day to day. It is a release
snapshot of the Living Spec under `docs/`, reorganized by what you want to do rather than by contract. Each page
links to the documents it draws on; when a page and the Living Spec disagree, the Living Spec is right
(`CAP-DLV-release-handbook`).

## What devkit gives you

devkit is one command, `devkit`, shipped as Python wheels released together at one version
([`ARCH-05-1-containers`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-05-1-containers.md)):

- **Distribution** (`devkit-dist`): packages agent assets into bundles, deploys the ones your project selects with
  `devkit sync`, projects skills and subagents into each agent's native directories, and loads guidance on demand.
  A repository that only wants shared agent assets installs this alone.
- **Harness** (`devkit-agt`): repository rules (`devkit rules`), data-driven delivery workflows (`devkit workflow`),
  commit gates (`devkit gate`), task worktrees (`devkit worktree`), tracked generated files, approval-bound
  integration (`devkit integration`) and bounded command output (`devkit run`).
- **Documents** (`devkit-docs`): the document model of the Living Spec, the `devkit docs` commands that resolve,
  list, search and follow references between documents, the document rules, and the auto-selected `docs` bundle of
  shared formats and writing guidance. It knows no delivery process.
- **Spec-driven delivery** (`devkit-spec`): proposals and spec bundles (`devkit spec`), delivery policy, worker
  inspection, the `spec` bundle of skills, workflows and role contracts, and the lifecycle rules that keep the
  documents consistent. It builds on `devkit-docs`.
- **Libraries for other repositories**: `devkit-advisory` (the `devkit.advisory` advisory protocol, standard
  library only) and `devkit-cli` (the agent-first output contract for any click tool).
- **Optional extras**: `devkit-mcp` (MCP transport), `devkit-viewer` (a local read-only page over your
  repositories), `devkit-catalog` (opt-in bundles such as `incubation`, `maintenance` and `response-style`) and the
  `search` extra for dense and hybrid document search.

The goals behind these pieces, deterministic results, transactional sync, strict layering and POSIX-only
operation, are set out in
[`ARCH-01-introduction-and-goals`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-01-introduction-and-goals.md).

## The overall model

devkit sits between three parties
([`ARCH-03-context`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/architecture/ARCH-03-context.md)):

- **You** configure project policy in `.devkit/config.toml`, confirm what the agent proposes and make the
  decisions devkit reserves for a person, such as approving an integration.
- **The agent** runs `devkit` commands, reads the one-line `[KIND: ...]` results on stdout and the advisories on
  stderr, and follows the guidance of the project's development approach: under SDD, the stage the workflow engine
  reports.
- **Git and your workspace** hold everything durable: deployed assets and their receipt, the Living Spec, work
  units, envelopes, hooks and worktrees. devkit runs no daemon and calls no LLM itself.

### Two development approaches

Every project makes one shared choice of **development approach**, `sdd` (the default) or `incubation`, recorded
as `[development] approach` in `.devkit/config.toml`. `uv run devkit config show` reports the effective value and
where it comes from. Installing a package or selecting a bundle never changes it; only an explicit edit you agree to
does ([`CAP-DIST-sync-and-transactions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md)).

- **SDD** (spec-driven development) is the full delivery procedure. `devkit sync` deploys guidance; the agent reads
  it with `devkit get-context <bundle>`; a development request is classified and bound to one workflow; the agent
  follows `devkit workflow next` stage by stage, recording reviews and questions as envelopes; rules and commit
  gates keep the repository consistent; and finished work lands on the base branch through `devkit integration`
  once you approve it.
- **Incubation** is for an idea whose product is still taking shape. The opt-in `incubation` bundle's `/incubate`
  entry advances the next useful product action (a question, a bounded experiment, an implementation, a usage
  check) and keeps only the current facts needed to resume in `.devkit/incubation.md`, with no spec bundles,
  envelopes or approvals per change. Document checks and your project's own checks still apply
  ([`CAP-DLV-idea-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-idea-incubation.md)).
  A small app can stay in incubation for good; when you want later changes to go through SDD, the `sdd-baseline`
  playbook verifies what you keep and switches the approach only on your decision
  ([`CAP-DLV-incubation-sdd-baseline`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-incubation-sdd-baseline.md)).

[Concepts](concepts.md) explains each of these pieces and how they connect.

## Where to start

1. Read [Concepts](concepts.md) for the vocabulary used everywhere else.
2. Install devkit. You can give your agent the installation guide and let it propose a plan, or install the release
   wheels yourself and run `uv run devkit sync`
   ([`CAP-DIST-content-packages`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-content-packages.md)
   describes which wheels bring which bundles).
3. Pick your starting point:
   - a repository that already has code and documents: [Adopt in an existing repository](journeys/adopt-in-an-existing-repository.md);
   - a new idea you want to explore before committing to specs: [Incubate an idea](journeys/incubate-an-idea.md),
     and later, if you want, [Adopt SDD from incubation](journeys/adopt-sdd-from-incubation.md);
   - otherwise, the SDD journeys below, starting with [Route development intent](journeys/route-development-intent.md).

## Journeys

Getting oriented:
- [Adopt in an existing repository](journeys/adopt-in-an-existing-repository.md)
- [Find the right documents](journeys/find-the-right-documents.md)

Exploring an idea:
- [Incubate an idea](journeys/incubate-an-idea.md)
- [Adopt SDD from incubation](journeys/adopt-sdd-from-incubation.md)

Delivering work:
- [Route development intent](journeys/route-development-intent.md)
- [Incubate and hand off a proposal](journeys/incubate-and-hand-off-a-proposal.md)
- [Drive development to integration](journeys/drive-development-to-integration.md)
- [Handle delivery problems and exceptions](journeys/handle-delivery-problems-and-exceptions.md)
- [Run parallel work safely](journeys/run-parallel-work-safely.md)
- [Resolve stale activity branches](journeys/resolve-stale-activity-branches.md)

Keeping the Living Spec healthy:
- [Keep the Living Spec consistent](journeys/keep-the-living-spec-consistent.md)
- [Reconcile Living Spec drift](journeys/reconcile-living-spec-drift.md)
- [Review and refactor accumulated slop](journeys/review-and-refactor-accumulated-slop.md)
- [Speed up selected slow operations](journeys/speed-up-selected-slow-operations.md)

Reporting progress:
- [Inspect weekly repository progress](journeys/inspect-weekly-repository-progress.md)
- [Publish a weekly report](journeys/publish-a-weekly-report.md)

## Areas

| Area | What it covers |
| --- | --- |
| [advisory](areas/advisory.md) | Structured errors, warnings and notices with codes and directives |
| [cli](areas/cli.md) | The agent-first output contract for click tools |
| [collaboration](areas/collaboration.md) | Shared report artifacts and the work scope registry |
| [compact](areas/compact.md) | Bounded command output with full logs on disk |
| [delivery](areas/delivery.md) | Development approaches, incubation, workflows, proposals, spec bundles, envelopes, policy and maintenance playbooks |
| [distribution](areas/distribution.md) | Bundles, sync, receipts, projections, context and playbooks |
| [documents](areas/documents.md) | The document model, lookup, search and namespaces |
| [gate](areas/gate.md) | Commit hooks and layered gate policy |
| [generated](areas/generated.md) | Tracked machine-generated files |
| [governance](areas/governance.md) | The rules engine, rule authoring and spec rules |
| [harness](areas/harness.md) | The `devkit spec` command mount and agent guidance |
| [host](areas/host.md) | Host lifecycle hooks and project MCP registration |
| [integration](areas/integration.md) | Preparing and integrating committed work |
| [mcp](areas/mcp.md) | The optional MCP runtime |
| [search](areas/search.md) | Lexical, dense and hybrid ranking |
| [traceability](areas/traceability.md) | Code entrypoints of capabilities and use cases |
| [viewer](areas/viewer.md) | The local read-only repository viewer |
| [worktree](areas/worktree.md) | Activity branches and task worktrees |

## Reference pages

[Decisions](decisions.md) lists the accepted architecture decisions, [Changes](changes.md) what is new in this
snapshot, and the [Glossary](glossary.md) the ubiquitous terms of devkit.
