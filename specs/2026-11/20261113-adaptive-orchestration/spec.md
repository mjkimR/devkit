---
id: SPEC-adaptive-orchestration
title: Coordinator-led adaptive delegation without fixed nesting limits
summary: "Make adaptive-dev actively delegate useful work and remove fixed nesting and child-budget requirements from guidance and assignment recording."
status: in-progress
created: 2026-11-13
related_capabilities: [CAP-DLV-adaptive-development, CAP-DLV-adaptive-assignments]
related_usecases: [UC-advance-an-idea]
workflow: sdd-spec-feature
---

# [SPEC-adaptive-orchestration] Coordinator-led adaptive delegation without fixed nesting limits

## 1. Problem Statement & Motivation

The adaptive entry describes how to delegate conditionally but does not directly request useful delegation.
Main agents can interpret it as requiring another user request. Nested roles and assignment recording also impose
a fixed depth and an extra child budget that are unrelated to the task's authority boundaries.

## 2. User Stories

- US-1: The main agent coordinates work and actively delegates separable research, implementation and verification.
- US-2: Nested delegation is not constrained by a fixed depth or prompt-level child budget.
- US-3: Descendants still cannot widen write scopes or commit authority, and parents await their children.

## 3. Non-Goals

- Scope Excluded: changing host configuration, adding replacement host-limit advice, changing role permission
  boundaries, publishing a release, or updating downstream dependency pins.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Active coordinator-led delegation
- Given adaptive-dev is applied to an authorized task.
- When separable research, implementation or verification is useful.
- Then the entry explicitly directs delegation while the main agent retains decomposition, integration and validation.

### [AC-02] Remove extra depth and budget rules
- Given adaptive entry references and reusable swarm roles.
- When their instructions are loaded.
- Then fixed child levels, required depth/budget payload fields and leaf delegation bans are absent, without replacement host-configuration advice.

### [AC-03] Record deeper assignments
- Given a valid nested assignment chain with narrowed write/commit authority.
- When another descendant is recorded.
- Then no fixed-depth error or ancestor-scope overlap blocks it; sibling and unrelated overlap still fail.

### [AC-04] Preserve authority and completion
- Given nested assignments.
- When a child widens its immediate parent's write/commit grant, or a parent completes with open children.
- Then existing authority and outstanding-child refusals remain effective.

## 5. Decision

`ADR-coordinator-led-adaptive-delegation` partially supersedes the earlier fixed nesting/budget decision.
