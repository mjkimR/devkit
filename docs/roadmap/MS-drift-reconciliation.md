---
id: MS-drift-reconciliation
title: Spec-code drift reconciliation maintenance playbook
summary: "Delivers a manually invocable playbook for evidence-based checks of Living Spec, code, and guidance consistency, with explicit decisions to update documentation, fix code, or defer findings."
status: planned
created_at: 2026-10-20
depends_on: []
---

# [MS-drift-reconciliation] Spec-code drift reconciliation maintenance playbook

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification) and §1.3 (Delivery Workflow Orchestration) by providing the maintenance playbook for Tier 2 reconciliation in `ADR-dual-source-of-truth-and-periodic-reconciliation`. The playbook checks accumulated drift between the Living Spec, implementation, and consumer-facing guidance, complementing per-work-unit reconciliation. It can be invoked manually without a scheduler.

## Exit condition

- A reconciliation playbook defines scope selection, evidence collection, mismatch assessment, user decisions, cleanup, and verification; a manual run demonstrates the path.
- Checks examine documented CLI commands, options, interfaces, terminology, and behavior against implementation and relevant guidance. Findings separate deterministic failures from suspected semantic mismatches, citing both sides and explaining the discrepancy.
- Each finding receives an explicit disposition: update documentation when the implemented behavior is intended, fix code when the documented intent remains correct, or defer with a reason and a follow-up destination. Discovery alone does not authorize choosing a new source of truth or rewriting the contract.
- Changes follow the applicable delivery and verification boundaries. Completion evidence distinguishes detected, resolved, and deferred findings and links to changes and verification, supporting later sweeps and reporting without duplicate follow-ups.
- Detection choices respect the evidence and rejected candidates recorded in `PROP-periodic-drift-reconciliation`; path changes or document age alone do not establish semantic drift. A dedicated detection command is introduced only when the existing commands and playbook procedure leave a demonstrated gap.

## Non-goals

- **Scope Excluded**: Scheduler implementation or trigger design, replacing per-work-unit reconciliation, automatically treating code as authoritative, broad structural refactoring without a drift finding, and reviving rejected detection heuristics without new evidence.
