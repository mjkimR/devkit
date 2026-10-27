---
id: CAP-DLV-review-refactor
title: Review and Refactoring Pass
summary: "An invoked or confirmed maintenance playbook reviews user-selected code, guidance or CLI surfaces one batch per surface and applies only agreed consolidations and reductions as evidenced direct-mode refactors in parallel isolated checkouts, routing contract removals as separate work items."
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
  recorded evidence; application of agreed behavior-preserving changes as direct-mode refactors, in parallel
  isolated checkouts where their write scopes are disjoint.
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
   behavior. IF a proposed consolidation joins implementations that do not behave identically, THEN its finding MUST
   list each difference with the behavior the consolidation keeps in the decision round, and the user's decision MUST
   cover each difference.
3. **Preservation evidence**: each consolidation or removal MUST record static and dynamic reachability searches
   with their results and the relevant verification before and after; a characterization test MUST be added only
   when a merged caller is exercised by no test; a guidance change MUST record a retained-constraint map
   (`ADR-require-reachability-evidence-and-layered-placement`).
   - **Differential comparison**: WHERE a change consolidates or replaces a parser, scanner, matcher, file listing,
     serialized format or other function whose inputs can be enumerated or generated, its evidence MUST include a
     comparison of the old and new code on the same inputs (the repository's own corpus plus edge cases of the input
     domain) with the input count and the result. Each difference MUST be an approved behavior change or be fixed.
   - **Old code side by side**: the old code MUST run from an extracted copy or a separate checkout and MUST NOT be
     restored by stashing, because the stash is shared by every worktree of a repository.
   - **Removal sweep**: WHEN a removal is applied, the playbook's agent MUST recheck the branches, parameters, types,
     errors and helpers that only the removed path reached, remove those that became unreachable within the agreed
     change, and record each one it keeps or defers.
4. **Helper placement**: a consolidated helper MUST live at the lowest common owner under the declared layering; a
   new cross-package or foundation module, or a repository without declared layering, MUST be a decision in the
   round.
5. **Route**: a batch's behavior-preserving work item MUST follow the repository's cross-area refactor workflow
   (`sdd-overall-refactor` with `spec`) unless every edited source file lies in one feature or module, which follows
   the feature workflow at its own depth; the route and edited paths MUST be stated in the decision round
   (`ADR-apply-review-refactor-changes-in-parallel-checkouts`, refining `ADR-overall-refactor-workflow`).
6. **Direct mode**: WHERE the work item follows the cross-area refactor route, the playbook's agent MUST apply it on
   its own branch, without a Unit or workers, within the batch's write scope
   (`ADR-apply-review-refactor-changes-in-parallel-checkouts`).
   - **Parallel application**: WHERE the host supports subagents, agreed changes with disjoint write scopes SHOULD run
     as concurrent edit tasks, each in its own isolated checkout created at the work item branch's current commit and
     prepared with the repository's documented setup (for example dependency installation and managed-asset
     synchronization) before its subagent starts.
   - **Sequential fallback**: IF two changes' write scopes overlap or one change builds on another, THEN the playbook's
     agent MUST run them one after another on the previous checkpoint.
   - **Editing subagents**: an editing subagent MUST edit only its assigned scope and MUST leave its result
     uncommitted; each diff MUST be checked against the agreed change and its scope, and a rejected edit MUST be
     reverted hunk by hunk.
   - **No governance relaxation**: the playbook's agent MUST NOT and an editing subagent MUST NOT add an exception, an
     ignore entry, a rule setting or a bypass of the repository's checks to make a change pass; IF a subagent's change
     fails a layering, rule or configuration check, THEN it MUST report the failure, and the playbook's agent MUST
     resolve the placement or return the change to the decision round.
   - **Unrelated changes**: IF the working tree holds changes that do not belong to the run, THEN the playbook's agent
     MUST stop for the user to commit, stash or exclude them and MUST NOT discard them.
7. **Commits and verification**: the playbook's agent MUST move each edit task's result onto the work item branch one
   at a time, verify it there and commit it alone through the repository's commit checks, so each commit holds one
   change with its own evidence; each change MUST be verified before and after on the previous checkpoint, and the
   final head MUST pass the repository's full verification on a clean tree.
8. **Review, report and integration**: the work item's diff MUST be reviewed by a fresh reviewer or a recorded
   self-review. The fresh reviewer's brief MUST give each change's preservation claim and ask for the inputs or states
   under which behavior differs, each with a reproduction, plus the list of what the reviewer checked and found sound.
   The work item's report MUST name every breaking change, and the work item MUST integrate only after the report
   through the repository's integration path and its own approval.
9. **Contract removals**: an approved removal of a command, option, public interface or compatibility path MUST be its
   own work item through the normal development workflow with the contract and documentation updated, unless the
   declared compatibility policy states no external consumer exists, in which case it MUST name the inputs no longer
   accepted (`ADR-apply-approved-contract-removals-as-separate-work-items`).

## 5. Report Interface

The report is an ordinary local Markdown file under the owning unit's materials or the repository's materials
location. It records intake, coverage per batch (reviewed, excluded, gaps, dropped candidates), findings and changes
as separate records (each change with its evidence, commit, delta and no-longer-accepted inputs), approved behavior
changes in their own section, separate from the inputs no longer accepted, decisions with provenance, follow-ups,
counts and the outcome. A report written before its work item integrates has its outcome updated with the
integration state when the work item integrates or stops. Seeded exercises label decisions simulated and change only
the fixture. Completion applies to a batch with no pending decision; a batch never claims the whole repository.
