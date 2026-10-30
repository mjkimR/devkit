---
id: FB-layering-choice-without-architecture-scope
title: A delegated layering choice lacked the architecture declaration in the write scope
scope: repo
kind: friction
category: other
target: spec-orchestrate skill (development-worker dispatch write scope)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-layering-choice-without-architecture-scope] A delegated layering choice lacked the architecture declaration in the write scope

Dispatch write-scope gap.

## 1. Friction / Question (friction, question)

- **Context**: A Development worker was asked to decide in `plan.md` whether a feature reads another feature's
  registry directly or through an injected predicate, per `ARCH-05-2-components`.
- **Expectation**: Every design the payload left open could be built inside the write scope.
- **Actual**: Any composition needed a new feature edge, which `RULE-architecture` checks against
  `.devkit/architecture.toml`; the payload's write scope excluded `.devkit/`, so the commit gate refused the code and the
  worker stopped with a problem until the Host extended the scope by one line.
- **Workaround (or Interpretation Chosen)**: Emergency commit, problem recorded, Host extended the write scope, worker
  resumed.
- **Suggestion**: When a dispatch delegates a cross-feature design choice, name `.devkit/architecture.toml` (limited to
  `feature_dependencies` entries) in the write scope, or state that a new feature edge is out of scope.

- **Disposition (resolved)**: `SPEC-generated-conflicts-follow-ups` adds a Workers rule to the `spec-delegate`
  payload reference: a payload delegating a cross-feature design choice names the architecture declaration in the
  write scope, limited to its feature edge entries, or states that a new feature edge is out of scope. The shipped
  rule names no repository path (bundle self-containment); the root `AGENTS.md` names devkit's `feature_dependencies`
  entries of `.devkit/architecture.toml`. Verified by
  `packages/devkit-spec/tests/integration/bundles/spec/test_architecture_scope_guidance.py` (AC-05).
