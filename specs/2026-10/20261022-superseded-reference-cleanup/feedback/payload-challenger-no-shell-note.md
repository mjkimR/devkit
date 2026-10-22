---
id: FB-payload-challenger-no-shell-note
title: The spec-delegate payload reference still says the challenger has no shell
scope: repo
kind: friction
category: docs-mismatch
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md
skill: spec-delegate
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-payload-challenger-no-shell-note] The spec-delegate payload reference still says the challenger has no shell

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-superseded-reference-cleanup` gave `reconcile-reviewer` read-only shell access following the
  `challenger` precedent (`FB-challenger-round-diff-without-shell`) and checked whether the `spec-delegate` payload
  reference states a role's missing shell.
- **Expectation**: The payload reference describes the roles' current tool sets, so a caller does not over-supply
  inputs a role can read itself.
- **Actual**: The `challenger` row passes the documents "as paths (it has no shell)", but the `challenger` contract has
  `Bash` on claude-code (Write and Edit disallowed), `sandbox_mode: read-only` on codex and `run_command` on
  antigravity.
- **Workaround (or Interpretation Chosen)**: Left unchanged: the unit's write scope allowed that file only for a
  sentence saying the reconcile reviewer has no shell, and the row concerns the challenger.
- **Suggestion**: Drop "(it has no shell)" from the `challenger` row, or replace it with what the caller still passes
  (the documents as paths, the round's `diff_scope`).

## Diagnostic Details

- **Reproduction**: Read the `challenger` row of `skills/spec-delegate/references/payload.md` and the `hosts` block of
  `subagents/challenger.md` in the `spec` bundle.
- **Expected / Actual**: No shell claim / "(it has no shell)" beside a contract that grants a read-only shell.
- **Versions**: devkit worktree at the base of `SPEC-superseded-reference-cleanup` (8801eb6a).
- **Conditions**: Every host; the text is caller guidance, not a projection.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `spec-delegate` skill, `challenger` role contract, `FB-challenger-round-diff-without-shell`.

## Evidence

```text
skills/spec-delegate/references/payload.md:17
| `challenger` | Proposal or spec, AC, non-goals, ADRs and capabilities as paths (it has no shell); ... |
subagents/challenger.md hosts.claude-code: tools: [Read, Grep, Glob, Bash], disallowedTools: [Write, Edit]
```
