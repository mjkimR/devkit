---
id: PROP-spec-rules-shared-document-index
title: Share one document index across a rules run
summary: "Lets the spec rules and markdown_link share one in-process document index and catalog per rules run, and keeps markdown_link to its targets, so targeted runs such as workflow lint-clean stop re-reading every document."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: documents/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/governance/
    - packages/devkit/src/devkit_agt/features/rules/services/builtins/markdown_link/
    - docs/capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-spec-rules-shared-document-index] Share one document index across a rules run

## 1. Background & Hypothesis

`devkit workflow next` on a documentation-only spec unit now takes about 0.85 s (Measured on main at df307e99 (macOS, Python 3.12, about 820 tracked Python files)). Most of what remains is the
`lint-clean` rules run over the unit's few files: the spec rules load the document index through a supplied reader
(`DocumentIndex.load` about a fifth of the profiled run, reading and hashing every document even with a warm memo),
and `markdown_link` checks the whole catalog for a handful of targets.

Hypothesis: one in-process document index and catalog per rules run, shared by every spec rule and `markdown_link`,
and target-limited link checking, cut the targeted run without changing findings.

## 2. Technical Spike Questions

- **Q1**: Do the spec rules already share one index per run, or does each load its own, and can a supplied-reader
  load reuse the persisted memo's entries for files the run did not modify?
- **Q2**: Which `markdown_link` findings depend on non-target files (link targets, anchors), and how far can a
  targeted run narrow its reads without missing a broken link in a target?

## 3. Proposed Design & Impact

- The rules run builds the document index and link catalog once and hands them to the rules that need them; findings
  stay identical for targeted and whole-workspace runs.
- `workflow next` on the same unit measured on main before and after.
- Independent of the Python-rule proposals.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr spec-rules-shared-document-index "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept spec-rules-shared-document-index --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff spec-rules-shared-document-index.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
