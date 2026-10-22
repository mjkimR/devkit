---
id: PROP-review-refactor
title: Maintenance review and refactoring playbook
summary: "Adds a review-refactor playbook to the maintenance bundle that reviews code, agent guidance and CLI commands for accumulated AI slop and refactors with evidence while preserving agreed behavior."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-maintenance-operations
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/maintenance/
    - docs/capabilities/delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-review-refactor] Maintenance review and refactoring playbook

## 1. Background & Hypothesis

Accumulated AI slop in code and agent guidance (redundant behavior, unnecessary abstractions, speculative
compatibility paths, duplicated or conflicting instructions, excessive always-loaded context) is not caught by
deterministic hygiene checks (`CAP-GOV-evaluation-lifecycle`). A maintenance playbook for a broad review and
refactoring pass, run before a release, after substantial feature growth or on request, removes it with repository
evidence and engineering judgment. It is the third playbook of the opt-in `maintenance` bundle in `devkit-catalog`,
beside `drift-reconciliation` and `weekly-report`, and it is invoked manually or by an external runner; it needs no
scheduler. This draft carries the scope its own milestone held before the
maintenance milestones merged into `MS-maintenance-operations`.

## 2. Technical Spike Questions

- **Q1**: Which cited findings on AI slop patterns, causes and refactoring techniques yield repository-applicable
  review criteria, and where do automated detection limits lie?
- **Q2**: How does the playbook bound a review pass (intake, scope, candidate prioritization) so one run stays
  reviewable?

## 3. Proposed Design & Impact

- `review-refactor` is a playbook asset of `maintenance`, with its preset selections (`upkeep`, `all`), package
  validation and bundle recommendation documentation verified. Selecting or invoking it does not require the other
  maintenance playbooks.
- The playbook defines intake, review scope, candidate prioritization, agreed changes, verification and completion
  evidence; a manual run demonstrates the path. Findings and implemented changes are recorded separately, with
  deferred work linked to existing or new follow-ups without duplication.
- Review criteria come from cited research and distinguish evidenced problems from stylistic preference.
- Code review covers redundant behavior, unnecessary abstractions, speculative compatibility paths, unused code and
  boilerplate without a demonstrated purpose; findings cite locations and the maintenance cost, and refactoring
  preserves agreed behavior and passes relevant verification.
- Guidance review covers skills, playbooks, AGENTS.md and instructions for duplication, conflicts, obsolete
  exceptions and excessive always-loaded context, preserving necessary constraints, decision criteria and examples;
  token or line reduction alone is not proof of correctness.
- CLI review inventories commands and subcommands for overlapping purposes, fragmented operations and inconsistent
  grouping, and reviews help and its source docstrings for accuracy and useful next steps. Contract-changing
  removals, renames or consolidations become separately scoped follow-ups, never behavior-preserving refactoring.
- Shared implementations are introduced only for demonstrated repeated behavior.
- Recurrence prevention first considers deleting, consolidating or correcting existing code and guidance. A new rule
  needs an evidenced recurring failure and a stated benefit, and follows `CAP-GOV-rule-authoring`.
- Non-goals: scheduler or trigger design, cosmetic churn without an evidenced problem, speculative commonization,
  behavior-changing feature work presented as refactoring, mandatory rule growth and automatic rule adoption.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr review-refactor "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- On acceptance (plan-accept): devkit spec proposal accept review-refactor --by user, then the Planning branch is merged.
  Development starts with devkit spec proposal handoff review-refactor.
- On rejection: change only status: rejected, with the user's reason in the commit message.
-->
