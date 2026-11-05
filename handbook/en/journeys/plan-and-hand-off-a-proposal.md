---
sources:
  CAP-DLV-delivery-workflows: 3239f814148a48be87ed6befa85cae48681e4519
  CAP-DLV-proposal-planning: 65becdbbd5615d0f69c7fae14d1a0c91d91204d1
  CAP-DLV-spec-bundles: 4920f894d479c8c4a54379c07ed130d81356bec3
  UC-plan-and-hand-off-a-proposal: e2ddba8f64ed51705b1f02682e562b20f0d34e37
title: Plan and hand off a proposal
---

# Plan and hand off a proposal

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `dabb86f9e659`, generated 2026-11-05. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
- [Advance an idea](advance-an-idea.md)
- [Design necessary command entry points](design-command-entrypoints.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Explore a design problem](explore-a-design-problem.md)
- [Find the latest maintenance run](find-the-latest-maintenance-run.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Improve an interface and user flow](improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
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

Some requests arrive with their direction still open: a new feature with several possible shapes, a spike, an
architectural change. They take `proposal` depth. The agent shapes the idea in a proposal, gathers evidence, asks you
the open questions, and you accept a direction on that evidence. Then the proposal hands off to a spec bundle that
carries everything forward, so Development starts from a consistent Living Spec.

The use case is
[`UC-plan-and-hand-off-a-proposal`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md).
Proposals, PADRs, Planning and Development, and gates are explained in [Concepts](../concepts.md).

Proposals belong to spec-driven development (SDD). While the repository's development approach is adaptive development,
creating, accepting or handing off a proposal is refused with `SPEC_LIFECYCLE_INACTIVE` before anything changes;
reading existing proposals still works. Adaptive development work follows [Advance an idea](advance-an-idea.md) instead.

## 1. Create the draft

In Backlog, the agent creates a draft bound to the `sdd-proposal` workflow:

```bash
uv run devkit spec proposal new fast-engine --title "Fast Engine" --summary "Replaces the regex rule engine with an AST parser."
```

It records your confirmation of the draft and its proposed Planning effort as `plan-intent`
([`CAP-DLV-proposal-planning`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-proposal-planning.md)).
A `--milestone` may name a planned, active, done or dropped milestone; a done or dropped one only adds the
`SPEC_PROPOSAL_MILESTONE_INACTIVE` notice so you can review the membership.

The draft's `size` decides whether it can be planned at all. `S`, `M` and `L` (or no size) are plannable. `XL` means
the work would produce two or more specs, or mixes deliverables of different kinds (a bugfix with a new feature). An
`XL` draft stays valid in Backlog, but `devkit workflow next` shows the `intent-proposal` size check unmet
(`detail="size=XL"`) and no `plan-intent` request opens. The agent reads that as "decompose first" and never edits
the size to get past it. On your decision it splits the draft (`devkit spec proposal new <child> --decomposed-from
PROP-<parent>`, keeping the parent's milestone) or promotes it to a milestone holding the children, optionally asking the
read-only `decomposer` role for a proposed split
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)).

## 2. Plan

The agent starts Planning on the `plan-<slug>` branch and sets the proposal in review. As the Planning effort
requires, it asks `scout` for evidence and `challenger` for criticism, records their returns, and writes preliminary
decisions as PADRs:

```bash
uv run devkit spec proposal padr fast-engine "Use AST parser"
```

When the proposal changes what a person sees, its `target-docs.md` holds drafted screens, and the agent can ask the
read-only `ux-reviewer` to walk the linked use cases through them before any code. Its findings carry no severity;
you decide the open ones at acceptance.

## 3. Answer the open questions

The agent puts every open question to you in one round, folds your answers into the proposal and its PADRs, and
refines the Development effort hint. Before each return to you it records fresh feedback-sweep coverage.

## 4. Review and accept

After the final Planning commit, the Host reviews the proposal, PADRs and envelopes and presents the briefing.
`uv run devkit spec proposal report <slug>` reads it without a shared-artifact publication requirement.
From the retained base checkout, after your direction decision:

```bash
uv run devkit spec proposal accept <slug> --by user --mode accept_only
```

This records acceptance and integrates Planning. A conflict-free moved base can land without a merge into
`plan-<slug>`; a changed proposal scope or Git conflict requires review and repair first.
`accept_and_handoff --effort <level>` additionally needs handoff authority, but returns after the Planning merge
with final verification pending and handoff unstarted. The Host synchronizes and checks the landed runtime before
invoking handoff in a fresh process with the retained authorized scope and effort.

## 5. Hand off

With `proposal-handoff` authority, from the retained base checkout (under `ask`, only after you approve the effects
and Development effort the Host presents; under `auto`, with the `dev_effort` hint):

```bash
uv run devkit spec proposal handoff fast-engine --effort medium
```

The command creates or validates `dev-<slug>` and its worktree, runs setup and sync, and hands off there. The
handoff creates the spec bundle bound to `sdd-spec-<task_kind>`
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)),
promotes the PADRs to accepted ADRs, moves materials and open feedback, carries the `plan-intent` and `plan-accept`
records by name, rewrites references that pointed into the proposal, and removes it. Output lines name what moved:
`[PROMOTED_ADR: ...]`, `[MATERIALS: ...]`, `[CARRIED_GATE: ...]`, `[REWRITTEN: ...]`, then
`[NEXT_CMD: uv run devkit workflow next --unit <dir>]`.

## 6. Reread and continue

A `SPEC_PROPOSAL_REFS_REWRITTEN` notice asks the agent to reread the rewritten sentences. It fixes any unresolved link
in the same change and follows the spec workflow's next stage, as in
[Drive development to integration](drive-development-to-integration.md).

## Shortcuts and other endings

- **Nothing needs Planning.** For a draft whose direction is settled, the agent checks eligibility read-only on the
  base checkout, then records a direct acceptance after your explicit decision:
  `uv run devkit spec proposal accept <slug> --by user --direct --check --note "<reason>"`, then the same without
  `--check`. The check answers `eligible=no` and exits `1` while a condition is still pending, such as an unrecorded
  `plan-intent`. An `XL` draft is never eligible.
- **It is really a small task.** At pickup you can decide a queued draft without PADRs is `session` work. The agent
  deletes the draft in one base commit that keeps its open feedback, and does the work as a session.
- **It must be split.** Planning returns the proposal as a draft marked for decomposition. After the Planning branch
  is gone and `devkit spec proposal check <slug>` passes on the base, Backlog creates the child drafts as in step 1.
- **You reject it.** The agent sets `status: rejected` with your reason in the commit message and merges the Planning
  branch per policy. A later `devkit rules check --phase hygiene` warns `SPEC_PROPOSAL_REJECTED_PENDING`, and its fix
  writes the rejection ADR and deletes the proposal, keeping open feedback.
- **Policy accepts.** When both the owning base and the branch set `plan-accept = "auto"`, the agent runs
  `accept --by policy`, and the report names the policy, never your consent. Under any other policy, `--by policy`
  is refused with `SPEC_PROPOSAL_POLICY_NOT_AUTO`.

## When it goes wrong

| Code | Meaning | What to do |
| --- | --- | --- |
| `SPEC_LIFECYCLE_INACTIVE` | The development approach is adaptive development, so proposal creation, acceptance and handoff are off. | Inspect `uv run devkit config show`; switching to SDD is your explicit choice ([Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)). |
| `SPEC_PROPOSAL_NOT_ELIGIBLE` | A direct acceptance fails a condition (for example `size: XL` or a missing `plan-intent`); each is listed with the commands that resolve it. | Fix the condition or go through Planning. |
| `SPEC_PROPOSAL_GATE_NOT_OPEN` | The workflow does not open `plan-accept` (for example, a missing feedback sweep). The status is restored. | Meet the listed checks, then accept again. |
| `SPEC_PROPOSAL_APPROVAL_NOT_READY` | The composed acceptance found Planning unfinished: unmet checks, open questions, holds, or no `plan-<slug>`. | Finish Planning there, then rerun. |
| `SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED` | The commit gate refused the acceptance commit; both acceptance writes were withdrawn. | Run `uv run devkit rules check` on `plan-<slug>`, fix and commit, then rerun. |
| `SPEC_PROPOSAL_IN_PLANNING` | A Backlog change touched a draft whose `plan-<slug>` exists. | Leave the draft to its Planning branch. |
| `SPEC_PROPOSAL_NOT_APPROVED` | Handoff of a proposal that is not accepted. | Ask for the decision; approval is never inferred. |
| `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` | The proposal says `accepted` without its recorded `plan-accept`. | Repair through a direct acceptance on the base, or decide on reverting the Planning merge. |
| `SPEC_HANDOFF_NOT_READY` | The composed handoff found the proposal not accepted, needing decomposition, or without completed Planning. | Resolve the named condition and rerun from the retained base checkout. |
| `SPEC_HANDOFF_BASE_DIRTY` | The retained base checkout has uncommitted changes (listed). | Decide what happens to them, then rerun. |
| `SPEC_HANDOFF_WORKTREE_CONFLICT` | A `dev-<slug>` worktree exists that devkit did not create for this accepted base, or it holds changes or another commit. It is never reused or removed. | Inspect and resolve that worktree yourself. |
| `SPEC_PROPOSAL_WRONG_WORKTREE` | Handoff ran outside `dev-<slug>`, or a composed command ran off the retained base checkout. | Run where `[TARGET]` and `[FIX]` say. |
| `SPEC_PROPOSAL_HANDOFF_FAILED` | A write failed; rollback is attempted and may be incomplete. | Inspect reported rollback results and retained paths before repairing or retrying. |
| `SPEC_HANDOFF_STALE` | The base, accepted plan or policy changed since the check, before any effect (exit `2`); or the new worktree no longer holds the reviewed base commit and is kept with `status=needs_recovery` (exit `1`). | Review the current state and approve again; inspect a kept worktree. |

A preflight refusal writes nothing. Failures after effects can retain a worktree or writes; inspect the reported state before recovery. A bugfix proposal hands off to a bundle that holds only `spec.md`,
bound to `sdd-spec-bugfix`. Area: [Delivery](../areas/delivery.md).

## Handoff commit and recovery

Composed handoff commits its transaction once as a clean direct child of the reviewed base and reports `commit`.
When the commit gate refuses it, `SPEC_HANDOFF_COMMIT_REFUSED` leaves writes staged in `dev-<slug>` with
`status=needs_recovery`. Fix the cause and commit there; do not rerun handoff against its dirty worktree.
A post-commit dirty or changed-history result likewise needs in-place inspection.

In local orchestration, git-operator reports `checks.worker_input` with the observed `head` and `dirty_paths`.
The Host compares these with Git before starting a worker on that clean head or its own later link-fix descendant.
The handoff's rewritten references are reread and repaired in a later commit, preserving the transaction SHA.
