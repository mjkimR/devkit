---
sources:
  ARCH-08-1-agent-output: 30466db492161e034b6d5c1e076d0e9f5432f514
  CAP-DLV-delivery-workflows: e1366a8cbed7bace6c51651085abc7d50b588768
  CAP-GOV-spec-rules: d995eca73f4dea46ac7a5836f25cdfa4bf158b6e
  CAP-HARN-agent-guidance: dbab285c20602e97d78db8768dc21e0a5613b379
  CAP-HARN-command-mount: e0a433da6ecfc088b4ba2199dae7b843b73e47f0
  UC-adopt-in-an-existing-repository: bc34f546639b3305ac410f895f7ab66b72c41a0b
  UC-handle-delivery-problems-and-exceptions: 3bd25e04ea70fadeefdc4a324a9780da89013610
  UC-resolve-stale-activity-branches: b19fb4071f1680f2fa080aab2b6f4b7a7d22741c
  UC-route-development-intent: 50d6278b292da8b936bc1bd6587bde501f490ee6
title: Harness
---

# Harness

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `c94b6a08710e`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
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
spec-driven delivery works and which procedure each stage follows, and the `devkit spec` command group gives it the
commands those procedures call. You install neither separately: the `spec` bundle is auto-selected on `devkit sync`,
and `devkit spec` mounts into the one `devkit` executable. For the model behind it (Living Spec, Units, workflow
stages), read [Concepts](../concepts.md) first.

## What lands in your repository

`devkit sync` copies the bundle to `.devkit/managed/spec/`, projects its skills and role contracts into each agent
host's native directories (`.claude/`, `.agents/`, `.codex/`) and adds exactly one line to the root `AGENTS.md`
block. That line tells every session to run `uv run devkit get-context spec` once before development work, to start
with `/spec <intent>` and to orient with `/spec-next`.

| Preset | How it is selected | What it brings |
| --- | --- | --- |
| `core` | automatically | instructions, the `AGENTS.md` pointer, the eleven rules, templates, skills, workflows, role contracts, playbooks |
| `docs-skeleton` | `devkit add spec:docs-skeleton` | a seeded `docs/` tree, written once where absent |

Opt out with `[presets] spec = false` in `.devkit/config.toml`. Never edit managed or projected files: change
them through `devkit override create` or your project's own bundle.

## Start a piece of work

1. The agent loads the constitution with `devkit get-context spec`: where the Living Spec lives, how work is
   classified, the approval boundaries and the completion checks.
2. You state the intent with `/spec <intent>`. On a new task intake the `spec` skill first runs one
   `devkit playbook search` and offers a playbook only when it names the exact operation you asked for; nothing runs
   until you confirm.
3. The skill reads `devkit spec policy` and proposes a classification for you to confirm: `task-kind` (feature,
   bugfix, refactor), `planning-depth` (`session`, `spec` or `proposal`, chosen by what must be settled before
   implementation, not by size) and per activity a mode and `activity-effort`.
4. It drives the matching workflow `sdd-<planning-depth>[-<task-kind>]` (`CAP-DLV-delivery-workflows`). Unit
   depths write `spec.md`, `plan.md` and `tasks.md` before production code; a `session` task writes no Unit.

The agent can raise the depth on its own judgment but never lowers it on its own, and Development never returns to
Planning: a wrong direction is closed and restarted under a new slug. The full walk-through is
[Route development intent](../journeys/route-development-intent.md); when a stage fails or needs an exception, see
[Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md).

## The skills

| Skill | Use it to |
| --- | --- |
| `spec` | route any development intent: classify, Backlog, inline Planning, drive the workflow |
| `spec-next` | orient: what is under way, or which queued draft to pick up next |
| `spec-specify`, `spec-plan`, `spec-tasks` | write `spec.md`, `plan.md` and `tasks.md` |
| `spec-review` | verify the diff, criteria and checks before declaring work done |
| `spec-sync` | reconcile the change into the Living Spec and resolve `reconcile.md` |
| `spec-integrate` | merge the base, re-verify, get your approval and integrate |
| `spec-delegate`, `spec-orchestrate` | hand work to reviewers or one-shot workers in their own worktrees |
| `spec-review-proposal` | review a committed proposal and its PADRs before acceptance |
| `spec-rule` | author a project rule ([Governance rules](governance.md)) |
| `spec-feedback` | record observations about tools and assets, or sweep them |
| `spec-entrypoints` | derive capability and use case entrypoints from spec bundles |

Skills load only the instructions and references of the current phase, and each reference says when to read it.
Six role contracts (`challenger`, `scout`, `code-reviewer`, `reconcile-reviewer`, `planning-worker`,
`development-worker`) are deployed for delegation.

## Write documents the way the rules expect

New documents start from `.devkit/managed/spec/templates/<kind>.md` (capability, use case, decision, proposal,
milestone). Before writing, the agent reads the instruction for that kind:

| Instruction | Read before |
| --- | --- |
| `document-writing` | any document: the sentence-level baseline |
| `living-spec-writing` | editing `docs/` or `specs/`: current-state writing, IDs, summaries, glossary |
| `contract-authoring` | specs, acceptance criteria, policies, rules, workflows |
| `capability-writing`, `usecase-writing`, `architecture-writing`, `decision-writing` | each document kind |

The bundle's rules check what these instructions describe; see the spec rules in [Governance rules](governance.md).

## Adopt it in a repository that already has docs

devkit never seeds an existing `docs/` tree on its own. The `brownfield-adoption` playbook installs, takes a
baseline, contains legacy Markdown under `docs/materials/_legacy/` and records any deferral you decide; see
[Adopt in an existing repository](../journeys/adopt-in-an-existing-repository.md). Two more playbooks ship with the
bundle: `feedback-hygiene` (triage open feedback in one batch) and `adr-compaction` (consolidate related ADRs without
changing a decision).

## Policies the guidance follows

- **Feedback**: `spec-feedback` follows `FEEDBACK_POLICY` from `devkit spec policy`: whether observations are
  captured automatically or only on request, whether upstream tools count, and how detailed records are.
- **Verification**: planning, review and integration follow your repository's own verification policy, such as
  affected-test selection with a full-suite fallback.
- **Integration**: after checks, review and reconcile, the agent asks you in conversation and only then runs
  `devkit integration integrate`; approval is never inferred.
- **Backlog and milestones**: requests not starting now become draft proposals, optionally grouped under milestone
  themes; `spec-next` filters drafts by their direct prerequisites on one local base snapshot before ranking them.
- **Stale branches**: leftover `plan-*` and `dev-*` branches are handled as in
  [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md).
- **No session hijacking**: an agent never stops your session or active work without your direction.

## The `devkit spec` commands

`devkit spec` has no executable of its own; devkit's root group imports it through the `devkit.commands` entry point
only when it runs. `devkit spec --version` prints the package version (`devkit --version` reports devkit itself).

| Commands | For |
| --- | --- |
| `devkit spec resolve`, `refs`, `list`, `search` | finding documents |
| `devkit spec new`, `devkit spec proposal new`, `accept`, `handoff` | creating spec bundles and incubating proposals |
| `devkit spec policy` | reading project policy |
| `devkit spec entrypoints` | deriving code entrypoints |
| `devkit spec scope register`, `query`, `update`, `release` | the shared work scope registry |

Every subcommand takes `-w/--workspace-root`, `--format text|json`, `-q`, `-v` and `--strict`, prints sentinels
or one JSON object as `ARCH-08-1-agent-output` describes, and raises `SPEC_`-prefixed advisories
([Advisories](advisory.md)). Listings page with `--limit` and `--offset`; when more items follow, a
`[NEXT_CMD: ...]` line gives the exact command for the next page. Exit `0` is success with or without notices, `1` a
warning under `--strict`, `2` a command that could not run or refused.

## Sources

- [CAP-HARN-agent-guidance](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-agent-guidance.md):
  the bundle's presets, constitution, instructions, skills, playbooks, templates and policies.
- [CAP-HARN-command-mount](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/harness/CAP-HARN-command-mount.md):
  how `devkit spec` mounts and the conventions its subcommands share.
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md):
  the workflows and role contracts the skills drive.
- [CAP-GOV-spec-rules](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/governance/CAP-GOV-spec-rules.md):
  the rules the bundle deploys.
