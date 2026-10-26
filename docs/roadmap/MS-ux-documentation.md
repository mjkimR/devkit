---
id: MS-ux-documentation
title: UX documentation and review in the Living Spec
summary: "Makes screens and interaction flows first-class Living Spec documents linked to use cases and capabilities, with authoring guidance and an independent use-case-driven UX review, on document kinds defined in one place."
status: planned
created_at: 2026-10-26
depends_on: []
---

# [MS-ux-documentation] UX documentation and review in the Living Spec

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification) and §1.3
(Delivery Workflow Orchestration) for products with a user interface. The Living Spec describes behavior through
capabilities and use cases (`CAP-DOCS-document-model`), but has no document for what a person sees and operates:
screens, their states, inputs and the flow between them. Interface specifications therefore end up as free-form
materials without traceability, or are squeezed into capabilities, and agents implement screens without a contract
to check against. Agent-produced layouts also tend toward generic averages, and an agent judges its own result
leniently, so a reviewable screen contract and a review performed in a separate context are both needed.

The theme starts with making document kinds data-driven, so that adding the UX kind (and later kinds) changes one
definition instead of kind-specific branches across the documents, governance and browsing code.

## Exit condition

- Document kinds are defined in one place that the document index, the spec rules and browsing read; adding a kind
  changes that definition and its templates, not kind-specific branches elsewhere.
- Screens and interaction flows are a Living Spec document kind with a deployed template, linked so that a use case
  step can name the screen it happens on and a screen names the capabilities whose state it presents; the spec rules
  report use case steps without a screen and screen interactions that serve no use case step, where the links are
  declared.
- The `spec` bundle carries UX authoring guidance that leaves the wireframe medium to the project, and an
  independent review that walks each use case's scenarios through the linked screens and scores them against a
  heuristic rubric.

## Non-goals

- **Scope Excluded**: wireframe or mock-up rendering, design tool integrations, visual styling and theming rules,
  and engine- or framework-specific UI verification; these stay project-owned.
- **Scope Excluded**: a plug-in extension point for third-party document kinds; kinds stay defined inside
  devkit-spec.

## Completion review

Decomposition: pending
Direct proposal work: pending

Confirm both with the current Backlog close candidate; record confirmed and status done together after the user's
confirmation. Missing assertions mean unconfirmed. Actual semantic scope changes reset both to pending; normal handoff does not.
