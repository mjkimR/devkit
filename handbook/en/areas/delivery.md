---
sources:
  CAP-DLV-cli-and-output: 0324155e16a2233cbc1ad5268d2f103f3f1477c1
  CAP-DLV-delivery-workflows: e1366a8cbed7bace6c51651085abc7d50b588768
  CAP-DLV-drift-reconciliation: 25e499e1a6d18c0d65be1855cfe8bd3925f2d1c6
  CAP-DLV-human-interaction: bbe6a95de1da4aae4da340a8a8f0dfd8e8e6a035
  CAP-DLV-project-policy: 7cec046a7324de8f46048c80dea6a4286bf809ef
  CAP-DLV-proposal-incubation: 9f9d06e5a526179f9d39e52890ee4e66277d95c6
  CAP-DLV-release-handbook: 98941d4b7793e2ac6a7fc50b92c337ede376e3ce
  CAP-DLV-review-refactor: 4c9e10968504b3edfdd77c6698275db599416bfd
  CAP-DLV-spec-bundles: 516cc932fee8af93baae90012e8dbe4c9b6f4725
  CAP-DLV-weekly-report: 0499a11d003f2b19a0ead794315b96ab8a09c22f
  CAP-DLV-workflow-definitions: 370fe402a7a71118569b2cf67521cd9756a7d3b7
  CAP-DLV-workflow-envelopes: ac166b8217314babc0f4e8ab346a6a9041f85fef
  CAP-DLV-workflow-orchestration: ee2cc0dbbb5824610041b822e5cdb58c301d57a4
  UC-drive-development-to-integration: bc214c7d80b401cf5b2ba5027c9144673d104393
  UC-handle-delivery-problems-and-exceptions: 3bd25e04ea70fadeefdc4a324a9780da89013610
  UC-incubate-and-hand-off-a-proposal: cad9b1da4379376d6512d16b06787ea1eed9a43e
  UC-publish-a-weekly-report: 9e5de0abff784fa43c00851d8b03cf8b59d60129
  UC-reconcile-living-spec-drift: 972538db7ca3eccccada61d606ed7a176a4effe0
  UC-review-and-refactor-accumulated-slop: 99e3929f75bacf6df151e9a3cc803b8c46bc5867
  UC-route-development-intent: 50d6278b292da8b936bc1bd6587bde501f490ee6
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

Delivery is how a piece of work travels from "I want this" to a merged change with an updated Living Spec. devkit
keeps the procedure as data: workflow definitions declare the stages, checks and gates, and a CLI tells you (or your
agent) where a unit of work stands and what comes next. This page walks through the model in the order you meet
it. For the vocabulary, see [Concepts](../concepts.md).

## The delivery model

Every task gets a `task-kind` (`feature`, `bugfix` or `overall-refactor`) and a `planning-depth` before work starts:

| Depth | When | What it leaves behind |
| --- | --- | --- |
| `session` | A small change with no lasting design or contract change | Nothing on disk: the result is reported in the conversation or PR body |
| `spec` | The change needs a written requirement, plan and Living Spec reflection | A spec bundle under `specs/` |
| `proposal` | The direction itself must be decided first | A proposal under `docs/proposals/`, later handed off to a spec |

Each combination maps to exactly one workflow: `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-feature`,
`sdd-spec-bugfix`, `sdd-proposal` and `sdd-overall-refactor`. There are no conditional stages: if the work turns out
bigger, the depth is raised (a new Unit) rather than a stage switched on. The catalog and the reasoning are in
[`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md).
Classification is the journey [Route development intent](../journeys/route-development-intent.md) (`UC-route-development-intent`).

A separate dial, `activity-effort` (`low`, `medium`, `high`), sets how thorough review and verification are for one
activity. It never removes a gate or a required check: at `low` the author self-reviews, at `medium` a
`code-reviewer` and a `reconcile-reviewer` check the work once, and at `high` both run in bounded review rounds.

## The engine underneath

The generic engine lives in `devkit workflow`
([`CAP-DLV-workflow-orchestration`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md)).
A **work unit** is a directory with an anchor file (`spec.md`, `proposal.md`) whose frontmatter records the bound
workflow. `devkit workflow next --unit <dir>` evaluates each stage's exit checks in order and reports the first
unmet stage, so agents never re-derive it from prose; a changed definition applies to in-flight work at once.

Definitions are Markdown files with a YAML frontmatter of `stages[]`; their schema, check primitives (`file-exists`,
`frontmatter`, `envelope-check-pass`, ...) and binding rules are in
[`CAP-DLV-workflow-definitions`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-definitions.md).
The commands, exit codes and the `[STAGE]`, `[WAITING]`, `[REQUEST]`, `[DELEGATE]` sentinels you see from `next`
are in [`CAP-DLV-cli-and-output`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-cli-and-output.md).

## Proposals: deciding the direction

A proposal incubates an idea whose direction is not settled
([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md)).
It is a bundle `docs/proposals/PROP-<slug>/` with `proposal.md`, optional preliminary decisions (PADRs), materials,
feedback and an optional `target-docs.md` blueprint of the intended Living Spec changes. Its lifecycle:

1. **Backlog**: `uv run devkit spec proposal new <slug>` scaffolds a `draft`. Before you edit, split or delete a draft
   by hand, run `uv run devkit spec proposal check <slug>`; it refuses while Planning is running on `plan-<slug>`.
2. **Planning** runs on the `plan-<slug>` branch: questions, evidence (`scout`) and criticism (`challenger`) as the
   Planning effort asks, folded into the proposal and its PADRs.
3. **Acceptance** (`plan-accept`): `uv run devkit spec proposal accept <slug> --by user` records `status: accepted`
   and the gate in one step. A small, eligible draft can skip Planning with `--direct --note "<reason>"` on the base
   checkout; run it with `--check` first to see every eligibility condition at once.
4. **Handoff**: `uv run devkit spec proposal handoff <slug>` on the `dev-<slug>` branch creates the spec bundle,
   carries the body, promotes PADRs to ADRs, moves materials and open feedback, rewrites links and removes the
   proposal. A failed write rolls back and keeps the proposal so you can rerun. This plain form is the Host-run step
   after the `proposal-handoff` decision and reads no policy itself; from the base checkout,
   `uv run devkit spec proposal handoff <slug> --effort <level>` reads the policy, prepares `dev-<slug>` and hands off
   there.

A rejected proposal only changes status; a later hygiene pass records a rejection ADR and deletes it. List active
proposals with `uv run devkit spec list proposal`. The full journey is
[Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md) (`UC-incubate-and-hand-off-a-proposal`).

## Specs and Units

A spec bundle is the Unit of `spec`-depth work and of every handed-off proposal
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)):
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
`collect-feedback` sweeps observations about the repository's own tools into feedback files. Every workflow also
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
([`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md)).
The same command reports the Git policy (`[tool.spec] worktree` `auto` or `required`, `[worktree] pull_request`),
routing (`depth_escalation`) and feedback capture settings.

Request kinds (`approve`, `choose`), decision records and how `devkit workflow return` voids later approvals are
in [`CAP-DLV-human-interaction`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-human-interaction.md).

## Envelopes and records

An envelope is a YAML file `<unit>/envelopes/<kind>-NN.yaml` that records what a stage or role returned: review
findings with `P1`/`P2`/`P3` severity, `reverify` closing a review round, `red`/`green` bugfix evidence,
`feedback` sweeps, `final-report` test/build/lint results, `reconcile-check`, and a `worker` record per run. Files
are never overwritten; the highest number is current
([`CAP-DLV-workflow-envelopes`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md)).

Envelopes also **hold** a unit: a `worker` envelope's `problem` that no `resolution` names blocks it, and a
question without an `answer` envelope makes it wait. While held, no gate passes, no handoff happens and
`devkit worktree finish --merge` refuses with `WORKTREE_BLOCKED`; `uv run devkit workflow envelope check --unit <dir>`
shows the hold. Only whoever actually fixed the problem writes the `resolution`.

## Orchestration and integration

In `direct` mode your main agent session (the Host) runs every stage itself. In `local-orchestrated` mode, invoked
per activity, the Host hands one turn to a one-shot worker in that activity's worktree: a `planning-worker` takes a
draft proposal on `plan-<slug>` toward `plan-accept`, and a `development-worker` runs a spec Unit on `dev-<slug>`
up to the final change report, committing at every stage boundary. Workers are the only roles that commit; they
never push, merge, rebase or amend. Read-only roles (`code-reviewer`, `reconcile-reviewer`, `challenger`, `scout`)
return findings that the caller records as envelopes.

When a worker returns, the Host runs `uv run devkit spec worker inspect`, which derives unit, base, head and scope
from committed records and reports ancestry, outside-scope paths, cleanliness, holds, cumulative rules and the next
stage; it never repairs or widens scope. Role contracts, reasoning-effort presets and per-host support (Claude
Code native, Codex emulated) are in section 4.6 of `CAP-DLV-delivery-workflows`.

At `integrate`, the work is merged with the base, conflicts are resolved within the approved intent, and only what
that changed is re-verified. The `spec` readiness provider checks the committed head in an isolated snapshot: stage
completion, no hold, `spec.md` completed, `reconcile.md` resolved and cumulative CI rules clean. Under
`pull_request = "required"` every task goes through a pull request; otherwise a local merge via
`devkit worktree finish --merge` is allowed.

## Maintenance playbooks

Three opt-in playbooks in the `maintenance` catalog bundle run only when you invoke them (through `devkit-playbook`,
their exact ID, or by confirming an offer from `/spec`). None adds a stage or a scheduler.

- **Drift reconciliation** reviews a bounded batch of Living Spec, code and guidance for accumulated drift, records
  each mismatch with evidence, and applies only the corrections you decide
  ([`CAP-DLV-drift-reconciliation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md);
  journey [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md), `UC-reconcile-living-spec-drift`).
- **Weekly report** builds an immutable, revision-bound report of delivered work, repository health and prioritized
  actions; publishing it is a separate, explicitly authorized step
  ([`CAP-DLV-weekly-report`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-weekly-report.md);
  journey [Publish a weekly report](../journeys/publish-a-weekly-report.md), `UC-publish-a-weekly-report`).
- **Review and refactor** reviews the code, guidance or CLI surfaces you select, one batch and one decision round per
  surface, and applies only the consolidations and reductions you agree to as evidenced, behavior-preserving
  refactors (`sdd-overall-refactor` in direct mode); an approved contract removal becomes its own work item
  ([`CAP-DLV-review-refactor`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-review-refactor.md);
  journey [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md),
  `UC-review-and-refactor-accumulated-slop`).

The handbook you are reading is itself a delivery artifact: a derived snapshot of the Living Spec refreshed on
request during release preparation with the repository-only `devkit-dev/handbook` playbook and `just handbook`
commands ([`CAP-DLV-release-handbook`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-release-handbook.md)).
Where it and `docs/` disagree, `docs/` wins.
