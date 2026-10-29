---
sources:
  ARCH-08-1-agent-output: 6b76bd19787465ed1e7ec7aee1904077cc75042c
  CAP-DIST-sync-and-transactions: 2759dc504dc98f758acf3b168122c97f35bd1dd6
  CAP-DLV-delivery-workflows: 936dff28b6c106fdcc568a677db096421e174f9c
  CAP-DLV-idea-incubation: c1ff3be1b056ec9d5746689d189c17fdde8bee89
  CAP-DLV-incubation-sdd-baseline: 8899fda9b8975eb5cf9848c226df2ee8f43abc14
  CAP-GOV-spec-rules: d6966cab23d742d0782429acf8acaba4bcbca90d
  CAP-HARN-agent-guidance: 3e6c66d7ea068a580cc1ee82308708d407dab6bd
  CAP-HARN-command-mount: ca46e4fab66858d2ee2a89c4a8cd676ad6b0a717
  UC-adopt-in-an-existing-repository: 37265d4dcac0d34967bb003908a49d0df4a036a8
  UC-adopt-sdd-from-incubation: 84cab126d6e7b0c498c33f38a07531ed16c0c6d3
  UC-handle-delivery-problems-and-exceptions: 3bd25e04ea70fadeefdc4a324a9780da89013610
  UC-incubate-an-idea: ba73c68267ca32979313705291d52f89febb5985
  UC-resolve-stale-activity-branches: b19fb4071f1680f2fa080aab2b6f4b7a7d22741c
  UC-route-development-intent: b3ee3ac9c76d14a4b97f0645eef8954f339330d5
title: Harness
---

# Harness

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `022b9f03bbd2`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](../journeys/adopt-sdd-from-incubation.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](../journeys/incubate-an-idea.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
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
| `docs:core` | automatically | the shared writing instructions, document templates and the nine document rules |
| `docs:docs-skeleton` | `devkit add docs:docs-skeleton` | a seeded `docs/` tree, written once where absent |

Opt out with `[presets] spec = false` in `.devkit/config.toml`. Never edit managed or projected files: change
them through `devkit override create` or your project's own bundle.

## SDD or incubation

`[development] approach` in `.devkit/config.toml` is the project's shared choice: `sdd` (the default when it is
absent) or `incubation`. Installing or selecting bundles never changes it. Under incubation the `spec` guidance
steps aside: ordinary work follows the project's incubation guidance and its independent checks, without implicit
Units, envelopes or classification, while documents already bound to an SDD workflow keep their checks. The opt-in
`incubation` bundle of `devkit-catalog` supplies that guidance and its `/incubate` entry; see
[Incubate an idea](../journeys/incubate-an-idea.md). Moving a retained incubation product to SDD is the
`sdd-baseline` playbook, described in [Adopt SDD from incubation](../journeys/adopt-sdd-from-incubation.md).

## Start a piece of work

1. The agent confirms the approach is SDD and loads the constitution with `devkit get-context spec`: where the
   Living Spec lives, how work is classified, the approval boundaries and the completion checks. Before document
   work it also loads `devkit get-context docs`, which carries the writing instructions and the titles and summaries
   of the project's steering documents.
2. You state the intent with `/spec <intent>`. On a new task intake the `spec` skill first runs one
   `devkit playbook search` and offers a playbook only when it names the exact operation you asked for; nothing runs
   until you confirm.
3. The skill reads `devkit spec policy` and proposes a classification for you to confirm: `task-kind` (feature,
   bugfix, refactor), `planning-depth` (`session`, `spec` or `proposal`, chosen by what must be settled before
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
Nine role contracts are deployed for delegation: `challenger`, `scout`, `code-reviewer`, `reconcile-reviewer` and
`ux-reviewer` for checks, `triage` and `decomposer` for Backlog (grouping open feedback, splitting a draft), and
`planning-worker` and `development-worker`. Each runs `devkit get-context spec` itself. Which model a role runs on is
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
incubation uses `sdd-baseline` instead. Two more playbooks ship with the bundle: `feedback-hygiene` (triage open
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
  `devkit spec scope collect --mode worktrees`; workers carry no registration duty.
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
| `devkit spec new`, `devkit spec proposal new`, `accept`, `handoff` | creating spec bundles and incubating proposals |
| `devkit spec policy` | reading project policy |
| `devkit spec entrypoints` | deriving code entrypoints |
| `devkit spec scope collect`, `compare`, `register`, `query`, `release` | observing and comparing work scopes |
| `devkit spec worker inspect` | inspecting a worker's committed result |

Every subcommand takes `-w/--workspace-root`, `--format text|json`, `-q`, `-v` and `--strict`, prints sentinels
or one JSON object as `ARCH-08-1-agent-output` describes, and raises `SPEC_`- or `DOCS_`-prefixed advisories
([Advisories](advisory.md)). Listings page with `--limit` and `--offset`; when more items follow, a
`[NEXT_CMD: ...]` line gives the exact command for the next page. Exit `0` is success with or without notices, `1` a
warning under `--strict`, `2` a command that could not run or refused.

## Sources

- [CAP-HARN-agent-guidance](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md):
  the bundle's presets, constitution, skills, role contracts, playbooks, templates and policies.
- [CAP-HARN-command-mount](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-command-mount.md):
  how `devkit spec` and `devkit docs` mount and the conventions their subcommands share.
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md):
  the workflows and role contracts the skills drive.
- [CAP-GOV-spec-rules](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-spec-rules.md):
  the rules the bundles deploy.
- [CAP-DLV-idea-incubation](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-idea-incubation.md)
  and [CAP-DLV-incubation-sdd-baseline](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-incubation-sdd-baseline.md):
  the incubation approach and the move to SDD.
