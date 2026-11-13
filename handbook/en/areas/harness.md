---
sources:
  ARCH-08-1-agent-output: 4921a21fa00c4cd4413b7a01236cc833944a458a
  CAP-DIST-sync-and-transactions: d0837e092276ca06cecfc650bdd57053d781f79c
  CAP-DLV-adaptive-development: 3461a3435f94eea4228dd966c2dc8e8b3aa80362
  CAP-DLV-delivery-workflows: 747eec234d403705ebf34d9a03424bd87afb9ce4
  CAP-DLV-sdd-baseline-adoption: acd7cadb9c726ae861f26364cd831d3d1afa1c4c
  CAP-GOV-spec-rules: 903255aa74c723fbf1e382808a1b7bfbcd9c68b2
  CAP-HARN-agent-guidance: dff559b3349a28515857465630025e54b334b414
  CAP-HARN-command-design: 55dfa957b84301d7a9897676145bec7e2486e71f
  CAP-HARN-command-mount: 9963e0253b7b23f53d30d2185998241d83cecd95
  CAP-HARN-isolated-execution: 7b36ba1e9522527ede0d5a91189ee2ec1efcf6ff
  UC-adopt-in-an-existing-repository: 018001c6e9a67168a045c00dd6d3938b05cbecad
  UC-adopt-sdd-from-adaptive-development: 1eb8461c21c7c3e6fa131c4efb88d7f7e07095f6
  UC-advance-an-idea: ccd7fa7758787dfc9e96321082bc99904eaadb2f
  UC-handle-delivery-problems-and-exceptions: 95b05bae6cd1c9cfa3f4ca276b34e14bc73df3a7
  UC-resolve-stale-activity-branches: b19fb4071f1680f2fa080aab2b6f4b7a7d22741c
  UC-route-development-intent: e3be291799759fd445b4dc4b6ddfe3c77c0addee
title: Harness
---

# Harness

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `a6e769c5721d`, generated 2026-11-13. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](../journeys/adopt-sdd-from-adaptive-development.md)
- [Advance an idea](../journeys/advance-an-idea.md)
- [Assess a selected test suite](../journeys/assess-test-management.md)
- [Design necessary command entry points](../journeys/design-command-entrypoints.md)
- [Discover and refine an idea](../journeys/discover-and-refine-an-idea.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Execute an isolated command](../journeys/execute-an-isolated-command.md)
- [Explore a design problem](../journeys/explore-a-design-problem.md)
- [Find the latest maintenance run](../journeys/find-the-latest-maintenance-run.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Import selected third-party agent assets](../journeys/import-third-party-agent-assets.md)
- [Improve an interface and user flow](../journeys/improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](../journeys/plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Read decision supersession](../journeys/read-decision-supersession.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Record a maintenance run](../journeys/record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](../journeys/research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Adopt and refresh bundle sources locally](../journeys/snapshot-bundle-sources.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

The harness is the part of devkit-spec your agent reads and runs: the `spec` bundle tells every session how
spec-driven delivery (SDD) works and which procedure each stage follows, and the `devkit spec` command group gives it
the commands those procedures call. It builds on devkit-docs, which owns the shared document side: the writing
instructions, templates and document rules in the `docs` bundle and the `devkit docs` lookup commands. You install
neither bundle separately: both are auto-selected on `devkit sync`, and `devkit spec` and `devkit docs` mount into
the one `devkit` executable. For the model behind it (Living Spec, Units, workflow stages), read
[Concepts](../concepts.md) first.

## What lands in your repository

`devkit sync` copies each bundle under `.devkit/managed/` (`spec/` and `docs/`), projects the skills and role
contracts into each agent host's native directories (`.claude/`, `.agents/`, `.codex/`) and adds short pointers to
the root `AGENTS.md` block. The `spec` pointer tells every session to check the project's development approach with
`uv run devkit config show` first; under SDD it then runs `uv run devkit get-context spec` once, starts with
`/spec <intent>` and orients with `/spec-next`.

| Preset | How it is selected | What it brings |
| --- | --- | --- |
| `spec:core` | automatically | lifecycle guidance, the `AGENTS.md` pointer, the five lifecycle rules, the proposal template, skills, workflows, role contracts, playbooks |
| `docs:core` | automatically | the shared writing instructions, document templates and the ten document rules |
| `docs:docs-skeleton` | `devkit add docs:docs-skeleton` | a seeded `docs/` tree, written once where absent |

Opt out with `[presets] spec = false` in `.devkit/config.toml`. Never edit managed or projected files: change
them through `devkit override create` or your project's own bundle.

## SDD or adaptive development

`[development] approach` in `.devkit/config.toml` is the project's shared choice: `sdd` (the default when it is
absent) or `adaptive-dev`. Installing or selecting bundles never changes it. Under adaptive development the `spec` guidance
steps aside: ordinary work follows the project's adaptive development guidance and its independent checks, without implicit
Units, envelopes or classification, while documents already bound to an SDD workflow keep their checks. The opt-in
`adaptive-dev` bundle of `devkit-adaptive` supplies that guidance and its `/adaptive-dev` entry; see
[Advance an idea](../journeys/advance-an-idea.md). Moving a retained adaptive development product to SDD is the
`sdd-baseline` playbook, described in [Adopt SDD from adaptive development](../journeys/adopt-sdd-from-adaptive-development.md).

## Start a piece of work

1. The agent confirms the approach is SDD and loads the constitution with `devkit get-context spec`: where the
   Living Spec lives, how work is classified, the approval boundaries and the completion checks. Before document
   work it also loads `devkit get-context docs`, which carries the writing instructions and the titles and summaries
   of the project's steering documents.
2. You state the intent with `/spec <intent>`. On a new task intake the `spec` skill first runs one
   `devkit playbook search` and offers a playbook only when it names the exact operation you asked for; nothing runs
   until you confirm.
3. The skill reads `devkit spec policy` and proposes a classification for you to confirm: `task-kind` (feature,
   bugfix, overall-refactor), `planning-depth` (`session`, `spec` or `proposal`, chosen by what must be settled before
   implementation, not by size) and per activity a mode and `activity-effort`.
4. It drives the matching workflow `sdd-<planning-depth>[-<task-kind>]` (`CAP-DLV-delivery-workflows`). Unit
   depths write `spec.md`, `plan.md` and `tasks.md` before production code; a `session` task writes no Unit.

The agent can raise the depth on its own judgment but never lowers it on its own, and Development never returns to
Planning: a wrong direction is closed and restarted under a new slug. A request too large for one spec (`size: XL`)
stays a draft until it is split. The full walk-through is
[Route development intent](../journeys/route-development-intent.md); when a stage fails or needs an exception, see
[Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md).

## The skills

| Skill | Use it to |
| --- | --- |
| `spec` | route any development intent: classify, Backlog, inline Planning, drive the workflow |
| `spec-next` | orient: what is under way, or which queued draft to pick up next |
| `spec-specify`, `spec-plan`, `spec-tasks` | write `spec.md`, `plan.md` and `tasks.md` |
| `spec-review` | verify the diff, criteria and checks before declaring work done |
| `spec-ux-review` | review drafted screens against their use cases before code (run by the `ux-reviewer`) |
| `spec-sync` | reconcile the change into the Living Spec and resolve `reconcile.md` |
| `spec-integrate` | merge the base, re-verify, get your approval and integrate |
| `spec-delegate`, `spec-orchestrate` | hand work to reviewers or one-shot workers in their own worktrees |
| `spec-review-proposal` | review a committed proposal and its PADRs before acceptance |
| `spec-rule` | author a project rule ([Governance rules](governance.md)) |
| `spec-feedback` | record observations about tools and assets, or sweep them |
| `spec-entrypoints` | derive capability and use case entrypoints from spec bundles |

Skills load only the instructions and references of the current phase, and each reference says when to read it.
Ten role contracts are deployed for delegation: `challenger`, `scout`, `code-reviewer`, `reconcile-reviewer` and
`ux-reviewer` for checks, `triage` and `decomposer` for Backlog (grouping open feedback, splitting a draft), and
`planning-worker`, `development-worker` and `git-operator`. Each runs `devkit get-context spec` itself. Which model a role runs on is
distribution's setting, not the harness's ([Distribution](distribution.md)).

## Write documents the way the rules expect

New documents start from `.devkit/managed/docs/templates/<kind>.md` (capability, use case, UX document, decision,
milestone); the proposal template stays under `.devkit/managed/spec/templates/`. Before writing, the agent reads the
`docs` instruction for that kind:

| Instruction | Read before |
| --- | --- |
| `document-writing` | any document: the sentence-level baseline |
| `living-spec-writing` | editing `docs/` or `specs/`: current-state writing, IDs, summaries, glossary |
| `contract-authoring` | specs, acceptance criteria, policies, rules, workflows |
| `capability-writing`, `usecase-writing`, `ux-writing`, `architecture-writing`, `decision-writing` | each document kind |

The bundles' rules check what these instructions describe; see the document and lifecycle rules in
[Governance rules](governance.md).

## Adopt it in a repository that already has docs

devkit never seeds an existing `docs/` tree on its own. The `brownfield-adoption` playbook installs, takes a
baseline, contains legacy Markdown under `docs/materials/_legacy/` and records any deferral you decide; see
[Adopt in an existing repository](../journeys/adopt-in-an-existing-repository.md). A project that grew under
adaptive development uses `sdd-baseline` instead. Two more playbooks ship with the bundle: `feedback-hygiene` (triage open
feedback in one batch) and `adr-compaction` (consolidate related ADRs without changing a decision).

## Policies the guidance follows

- **Feedback**: `spec-feedback` follows `FEEDBACK_POLICY` from `devkit spec policy`: whether observations are
  captured automatically or only on request, whether upstream tools count, and how detailed records are.
- **Verification**: planning, review and integration follow your repository's own verification policy, such as
  affected-test selection with a full-suite fallback.
- **Integration**: after checks, review and reconcile, the agent asks you in conversation and only then runs
  `devkit integration integrate`; approval is never inferred.
- **Backlog and milestones**: requests not starting now become draft proposals, optionally grouped under milestone
  themes that bind no design choice; `spec-next` filters drafts by their direct prerequisites on one local base
  snapshot before ranking them. Closing, dropping or reopening a milestone is your decision, and the same commit
  moves a done or dropped milestone to `docs/roadmap/_archive/`.
- **Parallel work**: before scheduling parallel work the Host observes what other worktrees are doing with
  `devkit spec scope collect`; workers carry no registration duty.
- **Stale branches**: leftover `plan-*` and `dev-*` branches are handled as in
  [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md).
- **No session hijacking**: an agent never stops your session or active work without your direction.

## The `devkit spec` and `devkit docs` commands

Neither group has an executable of its own; devkit's root group imports each through its `devkit.commands` entry
point only when it runs. `devkit spec --version` and `devkit docs --version` print the package versions
(`devkit --version` reports devkit itself).

| Commands | For |
| --- | --- |
| `devkit docs resolve`, `refs`, `list`, `search` | finding documents |
| `devkit spec new`, `devkit spec proposal new`, `accept`, `handoff` | creating spec bundles and planning proposals |
| `devkit spec policy` | reading project policy |
| `devkit spec entrypoints` | deriving code entrypoints |
| `devkit spec scope collect`, `compare`, `register`, `query`, `release` | observing and comparing work scopes |
| `devkit spec worker inspect` | inspecting a worker's committed result |

Every subcommand takes `-w/--workspace-root`, `--format text|json`, `-q`, `-v` and `--strict`, prints sentinels
or one JSON object as `ARCH-08-1-agent-output` describes, and raises `SPEC_`- or `DOCS_`-prefixed advisories
([Advisories](advisory.md)). Listings page with `--limit` and `--offset`; when more items follow, a
`[NEXT_CMD: ...]` line gives the exact command for the next page. Exit `0` is success with or without notices, `1` a
warning under `--strict`, `2` a command that could not run or refused.

## Lifecycle executor and command design

Ten SDD roles include git-operator, a reusable executor for exact current Host-authorized lifecycle jobs.
The Host keeps decisions, scheduling and result acceptance. Git Operator uses lean; scout uses compact;
other role settings inherit unless overridden. Resource levels never change activity-effort or write authority.

`command-design` is an opt-in catalog instruction for necessary justfile, CLI and MCP entry points.
It identifies operation/caller, reuses suitable paths and checks additions from their documented execution context.
See [Design necessary command entry points](../journeys/design-command-entrypoints.md).

## Sources

- [CAP-HARN-agent-guidance](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-agent-guidance.md):
  the bundle's presets, constitution, skills, role contracts, playbooks, templates and policies.
- [CAP-HARN-command-mount](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/harness/CAP-HARN-command-mount.md):
  how `devkit spec` and `devkit docs` mount and the conventions their subcommands share.
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md):
  the workflows and role contracts the skills drive.
- [CAP-GOV-spec-rules](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/governance/CAP-GOV-spec-rules.md):
  the rules the bundles deploy.
- [CAP-DLV-adaptive-development](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-adaptive-development.md)
  and [CAP-DLV-sdd-baseline-adoption](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md):
  the adaptive development approach and the move to SDD.

## Commands at a fixed commit

[Isolated execution](../journeys/execute-an-isolated-command.md) uses `devkit exec` to prepare a detached checkout and retain command evidence outside it. Launch success is pending; collect the result before claiming verification. Cancellation, observation and cleanup have separate outcomes.

## Working with this release

The coordinator delegates useful separable research, implementation and verification while retaining integration and final validation. Child scope and commit authority stay within the parent assignment; there is no fixed nesting-depth rule. Concurrent writers use separate worktrees or run serially.

Close UX review findings at `build-verify`, including findings already fixed in drafts; this is a closure record rather than another independent review round. A closing reconcile check covers the whole reflection, identifies the earlier check and marks each finding resolved or waived with a reason. Required contract mismatches cannot be waived.
