---
sources:
  CAP-DLV-adaptive-development: 120b77c7814f67b082a728d0fdbec0108b852b00
  CAP-DLV-cli-and-output: 172b26ced058b74e1e73cbf864296df07af9c2a6
  CAP-DLV-deep-research: 08c383e1a9a76e3e47679db645eeb7a751126b8e
  CAP-DLV-delivery-workflows: 3239f814148a48be87ed6befa85cae48681e4519
  CAP-DLV-design-exploration: 4fad9083aa058047d39e6956ff63b76f8232bd10
  CAP-DLV-drift-reconciliation: 4666e8d6bab265e18b275ce59b5f7d32b904a6d7
  CAP-DLV-human-interaction: 7926c28e1951896774e56bd201fbd5e3a474a673
  CAP-DLV-maintenance-history: ada7d8b89abb17dd3b396263b9b4aac18b2752e5
  CAP-DLV-performance-pass: 77480522e4c42e9bd7b529e4968a9a901db640b8
  CAP-DLV-project-policy: 8887a983196e8dc5bc3936327b30ef214314e07f
  CAP-DLV-proposal-planning: 65becdbbd5615d0f69c7fae14d1a0c91d91204d1
  CAP-DLV-release-handbook: 9d4b4799c61ab2d689d741f3df61323b9cd6689a
  CAP-DLV-review-refactor: 80b523a1ee09e2cff326ff4114c3c83c5461a666
  CAP-DLV-sdd-baseline-adoption: bb6fc66abb97dd0113a4864be4a8dbeca761c704
  CAP-DLV-spec-bundles: 4920f894d479c8c4a54379c07ed130d81356bec3
  CAP-DLV-uiux-improvement: 5b4b328d5933e2bcd67b719eff3c78a10e2386f4
  CAP-DLV-weekly-report: ad32dcc4519c5757150443dcb6079f919578d2a4
  CAP-DLV-workflow-definitions: e2258d0a57c60d8b5ce18f32edcde3748b85afeb
  CAP-DLV-workflow-envelopes: d9930340d63dab836aa1938f2e6cd2a8c4a23230
  CAP-DLV-workflow-orchestration: a84a1b608390b8b2c825c2be5d8ff5a8f101e828
  CAP-INT-mcp-services: 6978ff46427e1a1091c65b488ca9c76734b4a4c0
  UC-drive-development-to-integration: 9eeb5fda80dba7727d7680c91f2989a521c3fd69
  UC-handle-delivery-problems-and-exceptions: e75045b25be4756f7975373e437320013d5c1995
  UC-plan-and-hand-off-a-proposal: e2ddba8f64ed51705b1f02682e562b20f0d34e37
  UC-publish-a-weekly-report: 9e5de0abff784fa43c00851d8b03cf8b59d60129
  UC-reconcile-living-spec-drift: 972538db7ca3eccccada61d606ed7a176a4effe0
  UC-review-and-refactor-accumulated-slop: acbb724a9d06093b139e8d8c22682ae7d7f408b2
  UC-route-development-intent: c5ef3381db5cefc65ec9a805cd981b37df4618c6
title: Delivery
---

# Delivery

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `dabb86f9e659`, generated 2026-11-05. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](../journeys/adopt-sdd-from-adaptive-development.md)
- [Advance an idea](../journeys/advance-an-idea.md)
- [Design necessary command entry points](../journeys/design-command-entrypoints.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Explore a design problem](../journeys/explore-a-design-problem.md)
- [Find the latest maintenance run](../journeys/find-the-latest-maintenance-run.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Improve an interface and user flow](../journeys/improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](../journeys/plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Record a maintenance run](../journeys/record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](../journeys/research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
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

Choose a development approach before selecting a delivery procedure. A project shares
`[development] approach = "sdd"` (the default) or `"adaptive-dev"` in `.devkit/config.toml`.
`uv run devkit config show` reports the effective value and its source. Installing a package or selecting a bundle
never changes it. [Concepts](../concepts.md) explains the vocabulary.

## SDD: classify the work

SDD classifies work by `task-kind` (feature, bugfix, overall-refactor), `planning-depth` (session, spec, proposal)
and `activity-effort` (low, medium, high). Depth describes what needs settling before implementation:

- **Session:** no open direction or contract question; no Unit, envelope or reconcile document.
- **Spec:** a clear direction with a contract to write before code.
- **Proposal:** the direction itself needs Planning and acceptance before Development.

A bugfix reproduces a defect against an agreed contract and records Red then Green evidence.
Overall-refactor is a project-wide structural change with no new behavior and no Unit; a local refactor follows
the feature route. Medium effort requires an initial independent code review. High effort uses bounded review
rounds; low permits self-review. Effort never removes a required check or gate.

At each new intake, `/spec` searches once for a playbook matching the requested operation and scope.
A matching candidate is offered before edits and runs only on your confirmation. Follow-ups within the same task
and explicit entries skip discovery. A topic match alone does not select a playbook.

## Plan a proposal

Backlog creates `docs/proposals/PROP-<slug>/proposal.md`, bound to `sdd-proposal`, and records the agreed intent.
`size: XL` means more than one deliverable/spec or mixed task kinds and is decomposed before Planning.
Run `uv run devkit spec proposal check <slug>` before changing a draft; an existing `plan-<slug>` owns it.

Planning runs on `plan-<slug>` with the proposal, PADRs, evidence and `target-docs.md` blueprint.
The agent gathers your questions in one round and presents the final committed proposal and review briefing.
`uv run devkit spec proposal report <slug>` reads that briefing without shared-artifact publication.

From the retained base checkout, composed acceptance integrates the reviewed Planning result:

```bash
uv run devkit spec proposal accept <slug> --by user --mode accept_only
```

`accept_and_handoff` also requires handoff authority and a selected `--effort`; after Planning lands it yields with
verification pending and handoff unstarted. The Host synchronizes and checks the landed runtime, then invokes
handoff in a fresh process with unchanged authorized scope and effort.
A conflict-free moved base needs no merge into Planning; a changed proposal scope needs review again.

```bash
uv run devkit spec proposal handoff <slug> --effort medium
```

The composed handoff prepares `dev-<slug>` and commits its transaction once as a clean child of the reviewed base.
It turns the proposal into a spec, promotes PADRs, preserves materials and feedback, carries approvals by name and
rewrites references. A refused handoff commit leaves writes staged in that worktree for repair and commit;
rerunning the handoff is not the recovery. An eligible settled draft can use direct acceptance on the base after
an explicit decision. See [Plan and hand off a proposal](../journeys/plan-and-hand-off-a-proposal.md).

## Develop a spec

`uv run devkit spec new <slug>` creates a bundle on `dev-<slug>` under `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`.
`spec.md`, `plan.md` and `tasks.md` precede production code. For a defect, use `--workflow sdd-spec-bugfix`.
`uv run devkit workflow next --unit <dir>` reports the authoritative stage and unmet checks;
`uv run devkit workflow show <id>` shows its full definition.

The feature path covers specification, build/verification, review, Living Spec reflection, feedback and a final report
before integration. The bugfix path adds characterization and Red/Green evidence.
Screens are drafted in the proposal or spec before code; optional `ux-reviewer` findings are recorded there.
The retained screens and use-case citations enter `docs/ux/` during reconciliation.

`reconcile.md` maps the change to durable contracts in `docs/`. Every effort records a reconcile check.
At medium, a self-check can replace an independent reconcile reviewer only when every affected contract and its
agreement with the diff is unambiguous and no cross-component interpretation remains. High requires independence.

## Decisions and records

| Boundary | Decision |
| --- | --- |
| `plan-intent` | Goal and scope; an explicit task instruction supplies it. |
| `plan-accept` | Proposal direction. |
| `proposal-handoff` | Start Development and its setup/worktree effects. |
| `dev-integration` | Land the verified change and perform scoped cleanup. |

Each boundary is `ask` or `auto`; delegation is reported as policy, never as user consent.
`uv run devkit spec policy` reports approvals, stage switches and Git/feedback policy.
Within the agreement, the executor makes implementation choices. A change to goal, scope or constraints needs your decision.

Unit envelopes record reviews, rechecks, feedback, final reports, questions and problems without overwriting history.
An unanswered question or unresolved problem holds the workflow. Only the actor who fixed a problem records its resolution.
For one fully authored envelope as the sole pending file, `uv run devkit workflow envelope commit --unit <dir>
--file envelopes/<name>.yaml` keeps normal hooks; source changes and multi-record transactions use ordinary combined commits.
Session tasks report in conversation or the PR body and create none of these records.

## Orchestration and integration

In direct mode the Host performs the work. Local-orchestrated work uses one-shot Planning or Development workers
in their worktrees. Read-only support roles return evidence; workers commit only on their activity branches.
A reusable `git-operator` executes exact currently authorized lifecycle jobs. The Host retains scheduling,
semantic choices and result acceptance. Scout defaults to compact; git-operator uses lean, with medium effort where supported.
These resource levels do not change delivery effort or authority.

Scope observations distinguish current writes from future Planning scope. Current overlap serializes running work;
future-only overlap orders handoff/integration without serializing Planning. Partial coverage never proves independence.
`uv run devkit spec worker inspect` audits the returned turn and cumulative rules against the intended base.

The Host checks content using the source runtime, then prepares and executes the explicit branch integration.
After landing, it synchronizes dependencies and assets, regenerates stale tracked artifacts and runs final checks
in fresh processes. A confirmed Git merge remains `verification=pending` until those checks pass.
See [Integration](integration.md) and [Drive development to integration](../journeys/drive-development-to-integration.md).

## Adaptive development

Install docs/catalog and select `uv run devkit add adaptive-dev`. `/adaptive-dev` advances useful clarification,
bounded experiments, representative implementation and real usage checks without per-change SDD records.
It checks that the shared approach is `adaptive-dev` before product work. Optional roles are product-clarifier,
product-researcher and usage-reviewer. The coordinator keeps mutable current facts in `.devkit/adaptive-dev.md`:
goals, retained choices versus assumptions, checks, unknowns and the next action. A product can keep this approach indefinitely.

The former incubation approach, bundle and entry are not accepted, and the old context file is not a fallback.
On your request, `spec/sdd-baseline` maps the retained product to code, current documents and actual evidence.
Preparation keeps `adaptive-dev`; only readiness and your exact-effects decision activate SDD. No retrospective
Unit or integration-provider edit is needed. See [Advance an idea](../journeys/advance-an-idea.md) and
[Adopt SDD from adaptive development](../journeys/adopt-sdd-from-adaptive-development.md).

## Optional catalog entries

- `deep-research` supplies a user-invoked, approach-neutral investigation, retained as one `MAT-<slug>` material.
  It grants no implementation, commit or publication authority.
- `design-explore` explores mechanisms for architecture, models or workflows and returns directions in conversation
  unless you request a destination. It grants no implementation authority.
- `uiux-improve` improves an interface or user flow and carries requested implementation through the consumer's
  workflow. A review-only request returns findings without edits.

These entries use optional skill-local perspectives without a fixed cast or scoring requirement.
Their selection starts no work and changes no approach. Each runs only when you explicitly invoke it.

## Maintenance and release preparation

The opt-in maintenance bundle offers drift reconciliation, weekly reporting, review-refactor and a performance pass.
They run only on invocation or confirmation; corrections, publication and integration keep their own authority.
Weekly reports preserve immutable report bytes and a separate local publication record.
Review-refactor and performance work compare old/new behavior and keep contract changes as separate work.

Maintenance history is a separate opt-in companion: installing its commands or invoking a maintenance playbook
starts no history run and triggers no recurring offer. Requested capture freezes evidence; authorized publication
uses a dedicated history branch, and later integration changes append amendments.
See [Record a maintenance run](../journeys/record-a-maintenance-run.md) and
[Find the latest maintenance run](../journeys/find-the-latest-maintenance-run.md).

The release handbook is derived from the Living Spec and refreshed on request with `devkit-dev/handbook`.
It is never a reconciliation target; `docs/` prevails when the two disagree.

## Sources

- [CAP-DLV-cli-and-output](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-cli-and-output.md)
- [CAP-DLV-delivery-workflows](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)
- [CAP-DLV-drift-reconciliation](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md)
- [CAP-DLV-human-interaction](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-human-interaction.md)
- [CAP-DLV-adaptive-development](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-adaptive-development.md)
- [CAP-DLV-sdd-baseline-adoption](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md)
- [CAP-DLV-performance-pass](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-performance-pass.md)
- [CAP-DLV-project-policy](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md)
- [CAP-DLV-proposal-planning](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-proposal-planning.md)
- [CAP-DLV-release-handbook](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-release-handbook.md)
- [CAP-DLV-review-refactor](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-review-refactor.md)
- [CAP-DLV-spec-bundles](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)
- [CAP-DLV-weekly-report](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-weekly-report.md)
- [CAP-DLV-workflow-definitions](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-definitions.md)
- [CAP-DLV-workflow-envelopes](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md)
- [CAP-DLV-workflow-orchestration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md)
- [CAP-INT-mcp-services](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/integration/CAP-INT-mcp-services.md)
- [UC-drive-development-to-integration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-drive-development-to-integration.md)
- [UC-handle-delivery-problems-and-exceptions](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md)
- [UC-plan-and-hand-off-a-proposal](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md)
- [UC-publish-a-weekly-report](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-publish-a-weekly-report.md)
- [UC-reconcile-living-spec-drift](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-reconcile-living-spec-drift.md)
- [UC-review-and-refactor-accumulated-slop](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md)
- [UC-route-development-intent](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-route-development-intent.md)
- [CAP-DLV-deep-research](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-deep-research.md)
- [CAP-DLV-design-exploration](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-design-exploration.md)
- [CAP-DLV-uiux-improvement](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-uiux-improvement.md)
- [CAP-DLV-maintenance-history](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-maintenance-history.md)
