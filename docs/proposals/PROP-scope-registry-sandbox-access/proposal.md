---
id: PROP-scope-registry-sandbox-access
title: Work scope registry access across sandboxed worktrees
summary: Compare Git-directory storage, shared devkit state, and MCP-mediated access for the work scope registry across sandboxed worktrees. Define permission boundaries and query behavior without assuming that relocating state removes approval requirements.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-20
target_area: collaboration/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - collaboration/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-scope-registry-sandbox-access] Work scope registry access across sandboxed worktrees

## 1. Background & Hypothesis
<!-- Describe background, current challenges, and core hypothesis to address -->

## 2. Technical Spike Questions
<!-- Define key uncertainties and technical questions to answer -->
- **Q1**:
- **Q2**:

## 3. Proposed Design & Impact
<!-- Describe expected architectural design, CLI commands, and structural impact -->

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr scope-registry-sandbox-access "<title>" --summary "<what it decides>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept scope-registry-sandbox-access --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff scope-registry-sandbox-access.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
