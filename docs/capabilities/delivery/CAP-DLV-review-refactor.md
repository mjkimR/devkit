---
id: CAP-DLV-review-refactor
title: Review and Refactoring Pass
summary: "An explicitly invoked or confirmed maintenance playbook reviews user-selected code, guidance or CLI surfaces one batch per surface and applies only user-agreed consolidations and reductions as evidenced direct-mode refactors, routing contract removals as separate work items."
area: delivery
status: active
usecases:
  - UC-review-and-refactor-accumulated-slop
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/SKILL.md
---

# [CAP-DLV-review-refactor] Review and Refactoring Pass

## 1. Summary

The opt-in `maintenance` catalog bundle supplies the independent `review-refactor` playbook
(`CAP-DIST-content-packages`), a directory-form asset whose `SKILL.md` holds intake, review, decisions and completion,
`references/criteria.md` the review questions and evidence and `references/applying.md` the application procedure.
Explicit invocation through `devkit-playbook`, exact `devkit playbook get maintenance/review-refactor` or the user's
confirmation of a `spec` intake offer loads it on demand (`CAP-DIST-context-and-playbooks`). Consolidation and
reduction are its primary outcomes. It targets maintenance cost in code that agrees with its contract; a contract
mismatch belongs to `CAP-DLV-drift-reconciliation`.

## 2. Scope & Boundary

- **In scope**: review of code, agent guidance and CLI commands in user-selected roots; consolidation of duplicated
  behavior, folding of repeated technical helpers and removal of unneeded code, guidance, options and commands with
  recorded evidence; application of agreed behavior-preserving changes as direct-mode refactors.
- **Out of scope**: a scheduler or trigger (external runners, `ADR-external-playbook-execution`), a history store
  (`PROP-maintenance-history`), contract drift (`CAP-DLV-drift-reconciliation`), rule adoption
  (`CAP-GOV-rule-authoring`), detector tools as dependencies, cosmetic churn and behavior-changing feature work.

## 3. Run Contract

1. **Entry**: the playbook MUST run only when the user invoked or confirmed it; IF an invocation or an external
   runner names it without a decision round, THEN the run MUST stop at the decision round with nothing applied.
2. **Intake**: the playbook MUST record the run ID, repository identity, HEAD, dirty paths, prior reports and the
   report destination, and MUST clarify missing surfaces or roots before inspecting.
3. **Surface batches**: the playbook MUST split the run into one batch per selected surface, each with one decision
   round (`ADR-bound-review-refactor-runs-by-surface-batch`).
4. **Cross-surface findings**: a finding spanning surfaces MUST cite both sides and belong to the batch where its
   change lands; IF that surface is not selected, THEN it MUST be deferred with a follow-up unless the user adds the
   surface, which adds its own batch and decision round and is recorded in the report.
5. **Following edits**: tests of the changed code and non-code text naming it MUST stay with their change on any
   surface; they MUST NOT edit receipt-owned files, which go to the source bundle, an upstream follow-up or
   `devkit override`.
6. **Subagent review**: WHERE the host supports subagents, a subagent result MUST be validated at the cited location
   before it enters the decision round or a change record, and its verification or negative-reachability commands
   MUST be re-run before recording; a root MUST count as covered only when the result lists what was read.
   Subagents MUST NOT ask the user, approve a change or write the run's records.
7. **Findings**: each finding MUST cite a location, the review question and a named maintenance cost; a candidate
   without a named cost MUST be dropped and counted in the coverage. Tool output MUST be treated as candidates, and the
   playbook MUST install nothing without asking.
8. **Dispositions**: each finding MUST receive one of consolidate, reduce or remove with behavior preserved;
   contract change; defer (destination and restart condition); keep (reason). Unanswered findings MUST stay pending.
   The decision-round approval MUST supply the routed work item's intent and MUST NOT supply its integration
   approval.

## 4. Change Contract

1. **Reduction grounds**: a reduction MUST rest on one recorded ground: derivable, duplicated with a named canonical
   copy, enforced mechanically elsewhere, or shown unnecessary by a recorded check (verification and reachability
   for code, a representative-task run with and without the text for guidance). Line or token delta MUST be
   reported and MUST NOT justify a change.
2. **Shared implementations**: a shared implementation MUST have at least two current callers with the same
   behavior.
3. **Preservation evidence**: each consolidation or removal MUST record static and dynamic reachability searches
   with their results and the relevant verification before and after; a characterization test MUST be added only
   when a merged caller is exercised by no test; a guidance change MUST record a retained-constraint map
   (`ADR-require-reachability-evidence-and-layered-placement`).
4. **Helper placement**: a consolidated helper MUST live at the lowest common owner under the declared layering; a
   new cross-package or foundation module, or a repository without declared layering, MUST be a decision in the
   round.
5. **Route**: a batch's behavior-preserving work item MUST follow the repository's cross-area refactor workflow
   (`sdd-overall-refactor` with `spec`) unless every edited source file lies in one feature or module, which follows
   the feature workflow at its own depth; the route and edited paths MUST be stated in the decision round
   (`ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`, refining `ADR-overall-refactor-workflow`).
6. **Direct mode**: the playbook's agent MUST apply the work item on its own branch, without a Unit or workers,
   within the batch's write scope; editing subagents MUST work in disjoint assigned scopes, never commit, and have
   each diff checked, a rejected edit reverted hunk by hunk.
7. **Commits and verification**: each change MUST be verified before and after on the previous checkpoint and
   committed alone; the final head MUST pass the repository's full verification on a clean tree.
8. **Review, report and integration**: the work item's diff MUST be reviewed by a fresh reviewer or a recorded
   self-review; its report MUST name every breaking change; it MUST integrate only after the report through the
   repository's integration path and its own approval.
9. **Contract removals**: an approved removal of a command, option, public interface or compatibility path MUST be its
   own work item through the normal development workflow with the contract and documentation updated, unless the
   declared compatibility policy states no external consumer exists, in which case it MUST name the inputs no longer
   accepted (`ADR-apply-approved-contract-removals-as-separate-work-items`).

## 5. Report Interface

The report is an ordinary local Markdown file under the owning unit's materials or the repository's materials
location. It records intake, coverage per batch (reviewed, excluded, gaps, dropped candidates), findings and changes
as separate records (each change with its evidence, commit, delta and no-longer-accepted inputs), decisions with
provenance, follow-ups, counts and the outcome. Seeded exercises label decisions simulated and change only the
fixture. Completion applies to a batch with no pending decision; a batch never claims the whole repository.
