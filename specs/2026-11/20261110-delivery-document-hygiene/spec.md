---
id: SPEC-delivery-document-hygiene
title: Split delivery contracts by responsibility and trim reference duplication
summary: "Separate delivery role and proposal lifecycle contracts into focused capabilities while preserving every existing guarantee, and trim duplicate distribution reference text without changing behavior."
status: in-progress
created: 2026-11-10
related_capabilities: [CAP-DLV-delivery-workflows, CAP-DLV-proposal-planning]
related_usecases: [UC-drive-development-to-integration, UC-plan-and-hand-off-a-proposal]
workflow: sdd-spec-feature
---

# [SPEC-delivery-document-hygiene] Split delivery contracts by responsibility and trim reference duplication

## 1. Problem Statement & Motivation

The workflow and proposal capabilities combine core policy with independently useful role and lifecycle
interfaces. Their 783 and 784 lines exceed the 600-line capability budget. Agents loading one contract pay
for the others. The distribution quick reference repeats the canonical configuration example and exceeds
its 400-line budget. The Development use case repeats Scenario 32's number.

## 2. User Stories

- **US-1**: As an agent, I want delivery contract ownership split by responsibility so I can load the needed
  contract without losing its exceptions or failure behavior.
- **US-2**: As a reader, I want a concise distribution reference that retains commands and unique diagnostics.

## 3. Non-Goals

- **Scope Excluded**: runtime, agent-asset, policy, dependency or feature-edge changes.
- **Scope Excluded**: rewriting completed specs, materials, aliases or decision outcomes.
- **Scope Excluded**: compressing the sync capability or consolidated ADR solely to meet a line budget.
- **Scope Excluded**: deleting acceptance scenarios or joining lines to hide length.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Cohesive delivery contract partition
- **Given** the two delivery capabilities at the starting head,
- **When** roles/worker inspection and lifecycle interfaces are separated,
- **Then** the two original IDs remain useful entry points and two focused capabilities own the moved text,
  with all four files at most 600 lines and a section relocation map demonstrating preserved contracts.

### [AC-02] Current references and traceability
- **Given** current links and ADR restatement traces to relocated sections,
- **When** their owners change,
- **Then** current references name the correct capability and section, CAP/use-case backlinks remain symmetric,
  and document rules report no violation; completed specs and historical materials remain unchanged.

### [AC-03] Concise distribution reference
- **Given** canonical configuration contracts and the 433-line quick reference,
- **When** duplicate explanations are replaced with canonical references,
- **Then** the reference is shorter than 433 lines, retains practical command/selection examples and its unique
  diagnostic tables, justifies any remaining budget warning, and changes no command, error code or remediation contract.

### [AC-04] Scenario numbering and bounded verification
- **Given** two Scenario 32 headings in `UC-drive-development-to-integration`,
- **When** the duplicate is renumbered,
- **Then** every acceptance scenario and its meaning remain, and cumulative rules, affected tests, sync and
  whitespace checks pass with an explicit E2E selection result and documented retained hygiene warnings.

## 5. Assumptions

- This is content-preserving editorial work; partition rationale belongs in the plan, not a new policy ADR.
- Codex boundaries are emulated through absolute worktree commands, per-operation permissions and scope audits.
