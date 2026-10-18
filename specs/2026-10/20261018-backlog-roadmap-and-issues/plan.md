---
id: PLAN-backlog-roadmap-and-issues
spec: SPEC-backlog-roadmap-and-issues
---

# Technical Plan: Repository roadmap and Backlog

## 1. Constitution & Invariant Review

Conforms to `ADR-roadmap-in-repository` and `ADR-milestone-documents`. No new dependency, external tracker or lower-to-higher devkit import is needed. Libraries return advisories and never print.

## 2. Architecture Overview & Impact

Extend devkit-spec's document model, existing rules and proposal/spec scaffolding. Reuse the existing hygiene entry point for milestone warnings, keeping its rejected-proposal behavior. Guidance owns lifecycle transitions, branch checks and recommendation ordering; the CLI remains an unsorted document query.

## 3. Component & Interface Design

- documents ids/parse/index: MS kind, kind-scoped milestone/depends_on relations, decomposition and supersede provenance, historical milestones.
- rules: global roadmap ID placement, milestone format/summary and dependency cycles checked against the complete index.
- proposals scaffold/specs and CLI: validate MS references and draft decomposition sources before writes; preserve all provenance through handoff.
- hygiene/errors: done/dropped unsettled-member advisories via the existing extension; no network or new entry point.
- bundle instructions/templates/seed: repository-only Backlog procedure, deterministic recommendation and review reminder.

## 4. Error Handling & Edge Cases

Reject invalid authoring arguments before filesystem writes. Duplicate milestone IDs fail validation. Empty dependency lists are valid; wrong types, wrong-kind fields, missing IDs and cycles are rule errors. Historical references remain readable. Hygiene considers anchor files, not target blueprints or a handed-off proposal twice. Existing Git branch protections remain active for decomposition.

## 5. Verification & Test Plan

Cover document parsing/history, targeted cycles, CLI validation and handoff provenance, rule autofix and hygiene settled-member cases. Run devkit-spec lint, Pyright, package and bundled rule tests, layering, governance, packaging/consumer smoke where the environment permits. Review source guidance against AC-06 to AC-08 and reconcile all current contracts before integration.
