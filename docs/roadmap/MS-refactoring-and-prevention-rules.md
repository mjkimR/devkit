---
id: MS-refactoring-and-prevention-rules
title: Maintenance review and refactoring playbook
summary: "Delivers an on-demand maintenance review and refactoring playbook grounded in AI slop research, covering code, agent guidance, and CLI help while preserving behavior and reducing unnecessary complexity."
status: planned
created_at: 2026-10-18
depends_on: []
---

# [MS-refactoring-and-prevention-rules] Maintenance review and refactoring playbook

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3 (Delivery Workflow Orchestration), and §3.3 (Strict Layering) by providing a maintenance playbook for broad review and refactoring before a release, after substantial feature growth, or on user request. The playbook addresses accumulated AI slop in code and agent guidance, using repository evidence and engineering judgment beyond deterministic hygiene checks (`CAP-GOV-evaluation-lifecycle`). It can be invoked manually without a scheduler.

## Exit condition

- A review/refactoring playbook defines intake, review scope, candidate prioritization, agreed changes, verification, and completion evidence; a manual run demonstrates the path. Review findings and implemented changes are recorded separately, with deferred work linked to existing or new follow-ups without duplication.
- Research into AI slop patterns, causes, reduction methods, and refactoring techniques produces cited findings and repository-applicable review criteria. Criteria distinguish evidenced problems from stylistic preference and state limitations of automated detection.
- Code review covers redundant behavior, unnecessary abstractions, speculative compatibility paths, unused code, and boilerplate without a demonstrated purpose. Findings cite concrete locations and explain the maintenance cost; refactoring preserves agreed behavior and passes relevant verification.
- Guidance review covers skills, playbooks, AGENTS.md, and instructions for duplication, conflicts, obsolete exceptions, and excessive always-loaded context. Deletion, consolidation, and moving occasional procedures out of startup guidance preserve necessary constraints, decision criteria, and examples; token or line reduction alone is not proof of correctness.
- CLI help and its source docstrings are reviewed for accuracy against actual commands and options, useful next-step information, repetition, and unnecessary detail. Changes to help preserve the documented command contract.
- Shared implementations are introduced for demonstrated repeated behavior, with updated callers and a usable interface. Speculative commonization is excluded.
- Recurrence prevention first considers deleting, consolidating, or correcting existing code and guidance. New rules or instructions require an evidenced recurring failure and a stated benefit beyond existing coverage. Deterministic rule proposals state detectable conditions, examples, scope, and false-positive limits; adopted rules follow `CAP-GOV-rule-authoring`. No new rule proposal is required for every cleanup finding.
- Completion evidence links findings, changes, verification, and prevention decisions so reporting can distinguish completed cleanup from deferred work.

## Non-goals

- **Scope Excluded**: Scheduler implementation or trigger design, cosmetic churn without an evidenced problem, speculative commonization, behavior-changing feature work disguised as refactoring, mandatory rule growth, and automatic adoption of proposed rules.
