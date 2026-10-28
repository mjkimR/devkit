---
id: PROP-document-bundle-split
title: Install the document system without SDD
summary: Splits the spec bundle's distribution so a repository can install document formats, instructions, templates and rules without the SDD lifecycle assets.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-28
target_area: delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-idea-incubation
boundaries:
  owns:
    - delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-document-layer-package
workflow: sdd-proposal
---

# [PROP-document-bundle-split] Install the document system without SDD

## 1. Background & Hypothesis

The spec bundle's `core` preset installs document assets (writing instructions, templates, document rules)
together with lifecycle assets (lifecycle rules, `/spec` skills, workflows, subagents, the spec pointer). A
repository cannot keep devkit documents without SDD guidance. See `docs/materials/2026-10/20261028-document-layer-split/coupling-survey.md`.

Hypothesis: a document-only installation, with the lifecycle as a separate selection, lets idea incubation and
other processes reuse the document formats without SDD entry guidance.

Prerequisite: the document layer is first decoupled from the lifecycle and moved into its own package by an
overall refactor, which has no unit to depend on. Start Planning once that refactor has landed.

## 2. Technical Spike Questions

- **Q1**: Two bundles or one bundle with two presets; the `auto_select` default; the owner of `docs-skeleton`, `context_documents` and the steering pointer.
- **Q2**: How asset text that cites document commands (about 53 citations) and lifecycle commands (about 75) is rewritten so a document-only install never points at SDD.

## 3. Proposed Design & Impact

- Redistribute instructions, templates, rules and guidance between the document and lifecycle selections.
- Rewrite the constitution, the spec pointer and asset citations for a document-only installation.
- Update `CAP-DLV-spec-bundles`, `CAP-DLV-delivery-workflows`, `CAP-DLV-proposal-incubation` and the `guides/`
  installation guides; smoke-test a document-only install in a consumer repository.

## 4. Lifecycle & Retirement Criteria

- Retire with acceptance and handoff, or reject if idea incubation no longer needs a document layer without SDD.
