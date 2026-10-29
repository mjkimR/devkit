---
sources:
  CAP-DLV-cli-and-output: c4938daef997d6a15c536fe496279442cf5ce5a5
  CAP-DLV-delivery-workflows: eaee3ce05a4ecaacbab0789f7f12e5585c0b647c
  CAP-DLV-drift-reconciliation: 25e499e1a6d18c0d65be1855cfe8bd3925f2d1c6
  CAP-DLV-human-interaction: 8e7d688916e7c8dea4d0f26e562191a4a6c423cc
  CAP-DLV-idea-incubation: c1ff3be1b056ec9d5746689d189c17fdde8bee89
  CAP-DLV-incubation-sdd-baseline: 8899fda9b8975eb5cf9848c226df2ee8f43abc14
  CAP-DLV-performance-pass: b37939e6d8e45835bae34bf596322b6bdc5d74b3
  CAP-DLV-project-policy: 2af5b2fde75faecfa8260244a614fa796525de03
  CAP-DLV-proposal-incubation: 6a15a36e8d3fc2402928cfaa44b31689cc9ed168
  CAP-DLV-release-handbook: ef9a59be9a4712194710b04969671a12582c28d7
  CAP-DLV-review-refactor: a8eac89c524a4351fd3e5044fb3972beee3014c3
  CAP-DLV-spec-bundles: b743cb4567d0a510097b1dc902a9a066f962c6cc
  CAP-DLV-weekly-report: 0499a11d003f2b19a0ead794315b96ab8a09c22f
  CAP-DLV-workflow-definitions: 3e9e99925c9eb336af9bab4dd7d06d0468d70851
  CAP-DLV-workflow-envelopes: ba3e36ff09f879615ad60389b433b58cdf4097ee
  CAP-DLV-workflow-orchestration: 7617520b7cd6028e8eda909cf6b3171822ad02c1
  CAP-INT-mcp-services: ee8088a63e89abb3519c1744c540c41e95352ea2
  UC-drive-development-to-integration: ede0ca1f9647c2e9e1a520d97818d09fa7bcb5e4
  UC-handle-delivery-problems-and-exceptions: 3bd25e04ea70fadeefdc4a324a9780da89013610
  UC-incubate-and-hand-off-a-proposal: 725298a4a0f09bb0316fe05459aad3097bcc2a4e
  UC-publish-a-weekly-report: 9e5de0abff784fa43c00851d8b03cf8b59d60129
  UC-reconcile-living-spec-drift: 972538db7ca3eccccada61d606ed7a176a4effe0
  UC-review-and-refactor-accumulated-slop: acbb724a9d06093b139e8d8c22682ae7d7f408b2
  UC-route-development-intent: b3ee3ac9c76d14a4b97f0645eef8954f339330d5
title: Delivery
---

# Delivery

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
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
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
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

Delivery is how a piece of work travels from "I want this" to a merged change. devkit offers two development
approaches for it: spec-driven development (SDD), where the procedure is kept as data (workflow definitions declare
the stages, checks and gates, and a CLI tells you or your agent where a unit of work stands and what comes next), and
incubation, a lighter loop for a product that is still being discovered. This page starts with the choice, walks
through SDD in the order you meet it, then covers incubation, the move from incubation to SDD and the maintenance
playbooks. For the vocabulary, see [Concepts](../concepts.md).

## Choosing an approach

The approach is one shared project setting, `[development] approach = "sdd" | "incubation"` in
`.devkit/config.toml`, `sdd` when absent. `uv run devkit config show` reports it and its source, and
`uv run devkit spec policy` starts with a `[DEVELOPMENT_APPROACH: approach=... source=...]` line
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md)).
Installing `devkit-spec` or selecting the `incubation` bundle changes nothing here: the agent reads the setting
before it routes work, and it never switches the approach on its own.

| | SDD | Incubation |
| --- | --- | --- |
| Suits | Work whose requirements and contracts deserve a written record | An idea whose product is still taking shape |
| Entry | `/spec <intent>` | `/incubate` |
| Leaves behind | Spec bundles or proposals, envelopes, decision records and a reconciled Living Spec | `.devkit/incubation.md` (current facts only), the code and any current documents you keep |
| Approvals | Gates (`plan-intent`, `plan-accept`, `dev-integration`) | Your direction when the goal or constraints change; integration approval as usual |

While the approach is incubation, the SDD lifecycle commands (`devkit spec new`, `devkit spec proposal new`,
`accept` and `handoff`) refuse before changing anything with `SPEC_LIFECYCLE_INACTIVE`. Generic workflows, policy,
scope and worker inspection and document lookup stay usable, and SDD records that already exist keep their checks
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)).
The sections up to [Orchestration and integration](#orchestration-and-integration) describe SDD;
[Incubation](#incubation) describes the other approach.

## The delivery model

Under SDD, every task gets a `task-kind` (`feature`, `bugfix` or `overall-refactor`) and a `planning-depth` before work starts:

| Depth | When | What it leaves behind |
| --- | --- | --- |
| `session` | A small change with no lasting design or contract change | Nothing on disk: the result is reported in the conversation or PR body |
| `spec` | The change needs a written requirement, plan and Living Spec reflection | A spec bundle under `specs/` |
| `proposal` | The direction itself must be decided first | A proposal under `docs/proposals/`, later handed off to a spec |

Each combination maps to exactly one workflow: `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-feature`,
`sdd-spec-bugfix`, `sdd-proposal` and `sdd-overall-refactor`. There are no conditional stages: if the work turns out
bigger, the depth is raised (a new Unit) rather than a stage switched on. The catalog and the reasoning are in
[`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md).
Classification is the journey [Route development intent](../journeys/route-development-intent.md) (`UC-route-development-intent`).

A separate dial, `activity-effort` (`low`, `medium`, `high`), sets how thorough review and verification are for one
activity. It never removes a gate or a required check: at `low` the author self-reviews, at `medium` a
`code-reviewer` and a `reconcile-reviewer` check the work once, and at `high` both run in bounded review rounds.

## The engine underneath

The generic engine lives in `devkit workflow`
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md)).
A **work unit** is a directory with an anchor file (`spec.md`, `proposal.md`) whose frontmatter records the bound
workflow. `devkit workflow next --unit <dir>` evaluates each stage's exit checks in order and reports the first
unmet stage, so agents never re-derive it from prose; a changed definition applies to in-flight work at once.

Definitions are Markdown files with a YAML frontmatter of `stages[]`; their schema, check primitives (`file-exists`,
`frontmatter`, `envelope-check-pass`, ...) and binding rules are in
[`CAP-DLV-workflow-definitions`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-definitions.md).
The commands, exit codes and the `[STAGE]`, `[WAITING]`, `[REQUEST]`, `[DELEGATE]` sentinels you see from `next`
are in [`CAP-DLV-cli-and-output`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-cli-and-output.md).

## Proposals: deciding the direction

A proposal incubates an idea whose direction is not settled
([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md)).
It is a bundle `docs/proposals/PROP-<slug>/` with `proposal.md`, optional preliminary decisions (PADRs), materials,
feedback and an optional `target-docs.md` blueprint of the intended Living Spec changes. Its lifecycle:

1. **Backlog**: `uv run devkit spec proposal new <slug>` scaffolds a `draft`. Before you edit, split or delete a draft
   by hand, run `uv run devkit spec proposal check <slug>`; it refuses while Planning is running on `plan-<slug>`.
   A rough draft may carry `size: XL` (work that would need two or more specs or a different `task_kind`), but it
   is split (`new --decomposed-from`) or promoted to a milestone before Planning: until then its `plan-intent` is
   never asked, and nobody edits the size to get past it. The read-only `decomposer` role can propose the split for
   your decision.
2. **Planning** runs on the `plan-<slug>` branch: questions, evidence (`scout`) and criticism (`challenger`) as the
   Planning effort asks, folded into the proposal and its PADRs.
3. **Acceptance** (`plan-accept`): `uv run devkit spec proposal accept <slug> --by user` records `status: accepted`
   and the gate in one step. A small, eligible draft can skip Planning with `--direct --note "<reason>"` on the base
   checkout; run it with `--check` first to see every eligibility condition at once. From the base checkout,
   `uv run devkit spec proposal accept <slug> --mode accept_only|accept_and_handoff --by user` composes acceptance,
   integration of `plan-<slug>` and, with `--effort`, the handoff below, once you have approved those effects.
4. **Handoff**: `uv run devkit spec proposal handoff <slug>` on the `dev-<slug>` branch creates the spec bundle,
   carries the body, promotes PADRs to ADRs, moves materials and open feedback, rewrites links and removes the
   proposal. A failed write rolls back and keeps the proposal so you can rerun. This plain form is the Host-run step
   after the `proposal-handoff` decision and reads no policy itself; from the base checkout,
   `uv run devkit spec proposal handoff <slug> --effort <level>` reads the policy, prepares `dev-<slug>` and hands off
   there.

A rejected proposal only changes status; a later hygiene pass records a rejection ADR and deletes it. List active
proposals with `uv run devkit docs list proposal`; a draft under Planning shows as `reviewing`. The full journey is
[Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md) (`UC-incubate-and-hand-off-a-proposal`).

## Specs and Units

A spec bundle is the Unit of `spec`-depth work and of every handed-off proposal
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)):
`specs/<YYYY-MM>/<YYYYMMDD>-<slug>/` with `spec.md` (the anchor), `plan.md`, `tasks.md`, `reconcile.md`, and the
`envelopes/` and `decisions/` records. You create one directly with:

```bash
uv run devkit worktree start dev-login-flow --no-worktree   # specs live on their dev- branch
uv run devkit spec new login-flow --summary "Defines how users sign in with email and password."
uv run devkit spec new crash-on-save --workflow sdd-spec-bugfix   # spec.md only; plan and tasks come later
```

Each file starts with a `<!-- devkit:skeleton -->` marker; the stage stays open until the `spec-specify`,
`spec-plan` and `spec-tasks` skills write the real content and remove it. A proposal and a spec never share a slug.

## Workflow stages

`devkit workflow show <id>` is the authoritative order. In outline:

- **Session** (`sdd-session-*`): intent, (reproduce), execute and verify, report, approval, commit, merge; no records.
- **Spec feature**: `intent`, `specify`, `build-verify`, `review-refine`, `living-spec-draft`, `collect-feedback`,
  `final-change-report`, `integration-approval`, `integrate`, `merge`.
- **Spec bugfix**: replaces `specify` and `build-verify` with `characterize`, `plan-tasks`, `reproduce` (a `red`
  envelope proving the defect) and `fix-verify` (a `green` envelope proving the fix and preserved behavior).
- **Proposal**: `intent-proposal`, `spike`, `collect-feedback`, `direction-handoff`, `handoff`.

Two stages deserve attention. `living-spec-draft` is where the implementer reflects the change into `docs/`
(the `spec-sync` skill) and resolves `reconcile.md`; it must finish before integration is approved.
`collect-feedback` sweeps observations about the repository's own tools into feedback files.

When a change alters what a person sees, its screens are drafted under `docs/ux/` before code, and an optional,
read-only `ux-reviewer` can walk the linked use cases through the drafts and score each screen (at most two rounds,
recorded as `ux-review` envelopes during Planning or before the plan). It is a delegation, never a stage or a gate;
the implementer later marks each finding `resolved` or `waived`. Every workflow also
has an out-of-band `exception` stage for a retry cap, a tool failure or an unresolved semantic conflict; see
[Handle delivery problems](../journeys/handle-delivery-problems-and-exceptions.md)
(`UC-handle-delivery-problems-and-exceptions`). Driving a spec through these stages is the journey
[Drive development to integration](../journeys/drive-development-to-integration.md)
(`UC-drive-development-to-integration`).

## Gates and approvals

Gates are where a person (or explicit policy) decides. There are four:

| Gate | Decides | How you answer |
| --- | --- | --- |
| `plan-intent` | Goal, scope, verification, kind and depth of a task | `devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user` |
| `plan-accept` | A proposal's direction | `devkit spec proposal accept <slug> --by user` |
| `proposal-handoff` | Starting Development from an accepted proposal | the Host presents effects, then runs `devkit spec proposal handoff <slug> --effort <level>` (or `accept --mode accept_and_handoff`); no workflow stage checks it |
| `dev-integration` | Landing one integration unit (one pull request) | `--given dev-integration` on later `next` runs, or PR ready state |

There is deliberately no gate inside Development: choices within the agreed intent are the executor's, and only a
problem that would change the agreed goal, scope or contract stops the work.

Each gate is `ask` (default) or `auto` in `[workflow.approvals]`; `auto` is reported as policy, never as user
consent, and never skips checks. Stages can be switched off in `[workflow.stages]`. Read the effective policy, as
agents must, with `uv run devkit spec policy`
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md)).
The same command reports the Git policy (`[tool.spec] worktree` `auto` or `required`, `[worktree] pull_request`),
routing (`depth_escalation`) and feedback capture settings.

Request kinds (`approve`, `choose`), decision records and how `devkit workflow return` voids later approvals are
in [`CAP-DLV-human-interaction`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-human-interaction.md).

## Envelopes and records

An envelope is a YAML file `<unit>/envelopes/<kind>-NN.yaml` that records what a stage or role returned: review
findings with `P1`/`P2`/`P3` severity, `reverify` closing a review round, `red`/`green` bugfix evidence,
`feedback` sweeps, `final-report` test/build/lint results, `reconcile-check`, and a `worker` record per run. Files
are never overwritten; the highest number is current
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md)).

Envelopes also **hold** a unit: a `worker` envelope's `problem` that no `resolution` names blocks it, and a
question without an `answer` envelope makes it wait. While held, no gate passes, no handoff happens and
`devkit worktree finish --merge` refuses with `WORKTREE_BLOCKED`; `uv run devkit workflow envelope check --unit <dir>`
shows the hold. Only whoever actually fixed the problem writes the `resolution`.

## Orchestration and integration

In `direct` mode your main agent session (the Host) runs every stage itself. In `local-orchestrated` mode, invoked
per activity, the Host hands one turn to a one-shot worker in that activity's worktree: a `planning-worker` takes a
draft proposal on `plan-<slug>` toward `plan-accept`, and a `development-worker` runs a spec Unit on `dev-<slug>`
up to the final change report, committing at every stage boundary. Workers are the only roles that commit; they
never push, merge, rebase or amend. Read-only roles (`code-reviewer`, `reconcile-reviewer`, `challenger`, `scout`,
`ux-reviewer`) return findings that the caller records as envelopes; in Backlog, `triage` groups open feedback and
`decomposer` proposes a draft's split, both returning a message you decide on.

When a worker returns, the Host runs `uv run devkit spec worker inspect`, which derives unit, base, head and scope
from committed records and reports ancestry, outside-scope paths, cleanliness, holds, cumulative rules (against a
rules base you can set with `--rules-base`) and the next stage; it never repairs or widens scope, and a failed check
is an error for the Host to decide on. Role contracts and per-host support (Claude Code native, Codex emulated) are
in section 4.6 of `CAP-DLV-delivery-workflows`. Roles carry no reasoning-effort preset: they inherit the
session's model, except `scout`, which defaults to a compact model level, and the project can set levels per role
in `[subagents]`.

At `integrate`, the work is merged with the base, conflicts are resolved within the approved intent, and only what
that changed is re-verified. The `spec` readiness provider checks the committed head in an isolated snapshot: stage
completion, no hold, `spec.md` completed, `reconcile.md` resolved and cumulative CI rules clean. Under
`pull_request = "required"` every task goes through a pull request; otherwise a local merge via
`devkit worktree finish --merge` is allowed.

## Incubation

Incubation is delivered by the opt-in `incubation` catalog bundle: install `devkit-docs` and `devkit-catalog`, then
`uv run devkit add incubation`; `devkit-spec` is not needed. Selecting the bundle deploys `/incubate`, three
optional support roles and a template, and changes no approach: `/incubate` reads the effective approach first and,
if it is not `incubation`, stops and shows the configuration change instead of doing product work
([`CAP-DLV-idea-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-idea-incubation.md)).

Each session advances the next useful product action rather than a fixed sequence:

- **Clarify** only the missing product decision, reusing answers you already gave; no complete backlog or
  architecture is required first.
- **Research or experiment** within a stated write boundary and stop condition, keeping observations, assumptions
  and limits apart.
- **Implement** a representative flow, with instructions to run and check it.
- **Verify** by actually running it; a skipped or unavailable check is reported as unverified, not as a pass.

The optional roles, `product-clarifier`, `incubation-researcher` and `usage-reviewer`, are delegated only when a
separable question warrants it; they return evidence and never edit the current context or commit. While the goal
and constraints hold, the agent may rework code, tests and documents freely, with no Units, approvals or envelopes;
when the goal or constraints change, it asks for your direction first.

The **incubation current context**, `.devkit/incubation.md`, is the one record that persists between sessions. It is
project-owned Markdown holding current facts only: the goal, users and constraints, the choices you made versus the
agent's assumptions, run and check commands with what they actually showed, open questions and the next useful
action. Superseded experiments are removed rather than logged, `devkit sync` never overwrites the file, and a later
session rechecks what changed instead of trusting stale entries. The journey is
[Incubate an idea](../journeys/incubate-an-idea.md) (`UC-incubate-an-idea`).

Integration works as for an SDD `session` task: `devkit integration prepare` and `integrate` with your approval. The
project readiness provider binds the review, test and lint results the agent reports, runs the repository's rules
on the result and refuses a change that touches a retained SDD Unit until that Unit's own validation has run
([`CAP-INT-mcp-services`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/integration/CAP-INT-mcp-services.md)).

### Adopting SDD from incubation

Nothing moves a project to SDD automatically: not its size, its age or the number of experiments. When you ask for
it, the agent runs the `spec/sdd-baseline` playbook (`uv run devkit playbook get spec/sdd-baseline`), which comes
with the `spec` bundle
([`CAP-DLV-incubation-sdd-baseline`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-incubation-sdd-baseline.md)):

1. The approach stays `incubation` throughout preparation, even after `devkit-spec` is installed and its bundle
   selected, so you can keep developing in incubation while the baseline is incomplete.
2. You choose what the product retains. Each retained behavior, structure, choice and verification method is mapped
   to implementation, current documents and actual evidence and marked `verified`, `gap` or `excluded` (with a
   reason; an exclusion never counts as coverage).
3. Missing current-state documents are written as they are now, with known reasons and no invented history.
4. A report under `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/` records the source, scope, evidence, gaps and
   the exact activation effects.
5. Only when no gap remains does the agent present those effects (the `[development]` change and any integration
   provider change) for your explicit decision; changed sources are revalidated first.
6. After activation it checks `uv run devkit sync`, `uv run devkit config show`, `uv run devkit spec policy` and
   `uv run devkit sync --check`; from then on new work follows the ordinary SDD route. The baseline creates no
   historical spec bundle or envelope, and a partial failure is reported as such, with no claimed rollback.

The journey is [Adopt SDD from incubation](../journeys/adopt-sdd-from-incubation.md) (`UC-adopt-sdd-from-incubation`).

## Maintenance playbooks

Four opt-in playbooks in the `maintenance` catalog bundle run only when you invoke them (through `devkit-playbook`,
their exact ID, or by confirming an offer from `/spec`). None adds a stage or a scheduler.

- **Drift reconciliation** reviews a bounded batch of Living Spec, code and guidance for accumulated drift, records
  each mismatch with evidence, and applies only the corrections you decide
  ([`CAP-DLV-drift-reconciliation`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md);
  journey [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md), `UC-reconcile-living-spec-drift`).
- **Weekly report** builds an immutable, revision-bound report of delivered work, repository health and prioritized
  actions; publishing it is a separate, explicitly authorized step
  ([`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-weekly-report.md);
  journey [Publish a weekly report](../journeys/publish-a-weekly-report.md), `UC-publish-a-weekly-report`).
- **Review and refactor** reviews the code, guidance or CLI surfaces you select, one batch and one decision round per
  surface, and applies only the consolidations and reductions you agree to as evidenced, behavior-preserving
  refactors (`sdd-overall-refactor` in direct mode). Changes with disjoint write scopes can run in parallel isolated
  checkouts, each committed alone; a replaced parser or similar function is compared old against new on the same
  inputs, and no change may relax the repository's checks to pass. An approved contract removal becomes its own
  work item
  ([`CAP-DLV-review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-review-refactor.md);
  journey [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md),
  `UC-review-and-refactor-accumulated-slop`).
- **Performance pass** (`maintenance:performance`, which also deploys `review-refactor`) measures the operations you
  select, each as an exact command with a metric (wall time, subprocess count or peak memory). Timings are
  unprofiled and interleaved in one session, with a warm-up, at least five repetitions and a noise floor below which
  a difference counts as no change; profiling only attributes cost. Candidates are decided in one round: a change
  counts as behavior-preserving only if outputs, exit codes, written files and error behavior stay identical, and
  anything else (new caching between runs, parallelism, changed defaults) is a separate contract-change work item.
  Agreed changes form one work item on the repository's feature workflow, applied through `review-refactor`'s
  application and evidence sections, with old and new measured per change and a final measurement against the
  starting revision. A `survey` run stops at the decision round with nothing applied
  ([`CAP-DLV-performance-pass`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-performance-pass.md);
  journey [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md),
  `UC-speed-up-selected-slow-operations`).

The handbook you are reading is itself a delivery artifact: a derived snapshot of the Living Spec refreshed on
request during release preparation with the repository-only `devkit-dev/handbook` playbook and `just handbook`
commands ([`CAP-DLV-release-handbook`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-release-handbook.md)).
Where it and `docs/` disagree, `docs/` wins.
