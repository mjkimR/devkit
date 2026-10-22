---
id: PROP-adr-compaction
title: ADR Compaction
summary: Defines a governed ADR compaction procedure that consolidates related decision records into replacement ADRs carrying the retired IDs as aliases, as an explicit exception to the append-only ledger, and ships it as a playbook.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/decisions/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - packages/devkit-spec/
  excludes:
    - packages/devkit-viewer/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-adr-compaction] ADR Compaction

## 1. Background & Hypothesis

`docs/decisions/` is an append-only ledger: an approved ADR is never edited or deleted, and a change of direction is a
new ADR linked by `supersedes`/`superseded_by`. Fast development has produced many fine-grained ADRs, and related
decisions are spread across several records and supersession chains, so readers (agents first) spend context
reassembling the current decision.

`ADR-document-id-aliases` now lets any ID-bearing document carry `aliases`, resolved through one canonical mapping
and rewritten to the canonical ID by `devkit rules fix`. That makes consolidation possible without breaking
references.

**Core hypothesis:** compaction does not reverse decisions; it reorganizes them. It can therefore be an explicit,
governed exception to the append-only rule: related ADRs are merged into a replacement ADR that lists the retired
IDs in `aliases`, the retired files are deleted (replacement, not loss), the order of the decisions is made clear,
and rejected or superseded decisions are summarized inside the replacement ADR.

## 2. Technical Spike Questions

- **Q1 (policy)**: How is the append-only rule amended so that compaction is allowed but a decision cannot be
  silently changed? What distinguishes a compaction (no decision change) from a new decision, and who approves it?
- **Q2 (procedure)**: How are ADRs grouped (similar decisions, supersession chains), ordered, and how are rejected
  or superseded decisions summarized in the replacement ADR? What must the replacement ADR keep (status, dates,
  history section) and what checks prove nothing was lost (alias coverage, references, rules)?
- **Q3 (playbook)**: The procedure ships as a playbook. Which bundle owns it (devkit-spec `spec` bundle,
  devkit-catalog `maintenance`, or another) and how is it invoked?
- **Q4 (delivery depth)**: Does a compaction run write a spec (spec-depth unit with spec/plan/tasks/reconcile) or run
  at `session` depth? What evidence does each run leave?

## 3. Proposed Design & Impact

To be settled in Planning. Expected impact: an ADR (or amendment) on the append-only rule and the five places that
state it (decisions README and its seed copy, the spec-sync skill, the living-spec-writing instruction,
`CAP-DOCS-document-model`); the decision template if the replacement ADR needs a history section; a compaction
playbook; possibly a rule check for compaction integrity. Running a real compaction of the existing ledger is not
part of this proposal unless Planning decides otherwise.

## 4. Lifecycle & Retirement Criteria

Accepted when Q1–Q4 are decided; Development delivers the policy change, the playbook and its checks.
