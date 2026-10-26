---
sources:
  CAP-DLV-delivery-workflows: 9214b7acf5c49e41a824f1466ef5db167241eb82
  CAP-DLV-proposal-incubation: 961cf0d8332f015d97ec2e7f96f4facb52b8ea85
  CAP-DLV-spec-bundles: 516cc932fee8af93baae90012e8dbe4c9b6f4725
  UC-incubate-and-hand-off-a-proposal: 672aca028fbab742fbbadf7562638352cb439e8d
title: Incubate and hand off a proposal
---

# Incubate and hand off a proposal

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `3da97383dc87`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
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
[`UC-incubate-and-hand-off-a-proposal`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md).
Proposals, PADRs, Planning and Development, and gates are explained in [Concepts](../concepts.md).

## 1. Create the draft

In Backlog, the agent creates a draft bound to the `sdd-proposal` workflow:

```bash
uv run devkit spec proposal new fast-engine --title "Fast Engine" --summary "Replaces the regex rule engine with an AST parser."
```

It records your confirmation of the draft and its proposed Planning effort as `plan-intent`
([`CAP-DLV-proposal-incubation`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-proposal-incubation.md)).

## 2. Plan

The agent starts Planning on the `plan-<slug>` branch and sets the proposal in review. As the Planning effort
requires, it asks `scout` for evidence and `challenger` for criticism, records their returns, and writes preliminary
decisions as PADRs:

```bash
uv run devkit spec proposal padr fast-engine "Use AST parser"
```

## 3. Answer the open questions

The agent puts every open question to you in one round, folds your answers into the proposal and its PADRs, and
refines the Development effort hint. Before each return to you it records fresh feedback-sweep coverage
([`CAP-DLV-delivery-workflows`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-delivery-workflows.md)).

## 4. Review and accept

After the final Planning commit, the agent reviews the proposal, PADRs and envelopes and presents its findings. You
can read the same briefing:

```bash
uv run devkit spec proposal report fast-engine
```

When you accept the direction, the agent records the acceptance and the accepted status in one step:

```bash
uv run devkit spec proposal accept fast-engine --by user --note "<your decision>"
```

With `--mode accept_and_handoff --effort <level>` the same call also starts Development; `accept_only` stops after
acceptance. The agent then integrates the Planning branch, and the workflow reports the proposal Unit complete.

## 5. Hand off

With `proposal-handoff` authority, on `dev-<slug>`:

```bash
uv run devkit spec proposal handoff fast-engine --effort medium
```

The handoff creates the spec bundle bound to `sdd-spec-<task_kind>`
([`CAP-DLV-spec-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-spec-bundles.md)),
promotes the PADRs to accepted ADRs, moves materials and open feedback, carries the `plan-intent` and `plan-accept`
records by name, rewrites references that pointed into the proposal, and removes it. Output lines name what moved:
`[PROMOTED_ADR: ...]`, `[MATERIALS: ...]`, `[CARRIED_GATE: ...]`, `[REWRITTEN: ...]`, then
`[NEXT_CMD: devkit workflow next --unit <dir>]`.

## 6. Reread and continue

A `SPEC_PROPOSAL_REFS_REWRITTEN` notice asks the agent to reread the rewritten sentences. It fixes any unresolved link
in the same change and follows the spec workflow's next stage, as in
[Drive development to integration](drive-development-to-integration.md).

## Shortcuts and other endings

- **Nothing needs Planning.** For a draft whose direction is settled, the agent checks eligibility read-only on the
  base checkout, then records a direct acceptance after your explicit decision:
  `uv run devkit spec proposal accept <slug> --by user --direct --check --note "<reason>"`, then the same without
  `--check`.
- **It is really a small task.** At pickup you can decide a queued draft without PADRs is `session` work. The agent
  deletes the draft in one base commit that keeps its open feedback, and does the work as a session.
- **It must be split.** Planning returns the proposal as a draft marked for decomposition. After the Planning branch
  is gone and `devkit spec proposal check <slug>` passes on the base, Backlog creates the child drafts.
- **You reject it.** The agent sets `status: rejected` with your reason in the commit message and merges the Planning
  branch per policy. A later `devkit rules check --phase hygiene` warns `SPEC_PROPOSAL_REJECTED_PENDING`, and its fix
  writes the rejection ADR and deletes the proposal, keeping open feedback.
- **Policy accepts.** When both the owning base and the branch set `plan-accept = "auto"`, the agent runs
  `accept --by policy`, and the report names the policy, never your consent.

## When it goes wrong

| Code | Meaning | What to do |
| --- | --- | --- |
| `SPEC_PROPOSAL_NOT_ELIGIBLE` | A direct acceptance fails a condition; each is listed. | Fix the condition or go through Planning. |
| `SPEC_PROPOSAL_GATE_NOT_OPEN` | The workflow does not open `plan-accept` (for example, a missing feedback sweep). The status is restored. | Meet the listed checks, then accept again. |
| `SPEC_PROPOSAL_IN_PLANNING` | A Backlog change touched a draft whose `plan-<slug>` exists. | Leave the draft to its Planning branch. |
| `SPEC_PROPOSAL_NOT_APPROVED` | Handoff of a proposal that is not accepted. | Ask for the decision; approval is never inferred. |
| `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` | The proposal says `accepted` without its recorded `plan-accept`. | Repair through a direct acceptance on the base, or decide on reverting the Planning merge. |
| `SPEC_PROPOSAL_WRONG_WORKTREE` | Handoff ran outside `dev-<slug>`. | Start or continue `dev-<slug>`. |
| `SPEC_PROPOSAL_HANDOFF_FAILED` | A write failed; everything was rolled back and the proposal kept. | Fix the cause and rerun. |
| `SPEC_HANDOFF_STALE` | The base, proposal or configuration changed after you saw the handoff. | Review the current state and approve again. |

A refused acceptance or handoff writes nothing. A bugfix proposal hands off to a bundle that holds only `spec.md`,
bound to `sdd-spec-bugfix`. Area: [Delivery](../areas/delivery.md).
