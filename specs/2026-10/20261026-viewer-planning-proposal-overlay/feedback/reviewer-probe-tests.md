---
id: FB-reviewer-probe-tests
title: Let the code reviewer run probe tests in an ignored path
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/code-reviewer.md
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-reviewer-probe-tests] Let the code reviewer run probe tests in an ignored path

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The `code-reviewer` contract forbids any write, so a reviewer who suspects a reactivity or
  ordering defect in frontend code can only reason about it. In this unit the reviewer's attempt to copy the frontend
  into a temporary directory to run a probe test was refused, and two of its findings were reported as "from reading
  the code; no probe test was run".
- **Proposed Procedure**: Allow the reviewer to write throwaway probe tests under an ignored path inside the worktree
  (for example `<worktree>/scratch/`), deleted before it returns, and to run the package's test command on them. The
  contract's "leaves `git status --short` unchanged" check still holds because the path is ignored.
- **Expected Benefit**: Findings about timing, reactivity or ordering arrive with a failing probe instead of a code
  reading, so the implementer spends less time reproducing them.
- **Cost & Risk**: A probe left behind in the ignored path; a reviewer could mistake its probe for the unit's tests.
- **Attempted**: Hypothesis. Both read-only findings reproduced when the implementer wrote the tests, which suggests a
  probe would have been cheap and conclusive.

## Diagnostic Details

- **Reproduction**: Delegate `code-reviewer` on a Svelte change; the reviewer tries to run vitest on a copy outside the
  worktree and is refused.
- **Expected / Actual**: Expected an executable probe; actual: findings reasoned from the source only.
- **Versions**: devkit at this unit's branch.
- **Conditions**: Claude Code native subagent; read-only reviewer contract.
- **Workarounds Attempted**: The implementer reproduced both findings with tests.
- **Related Assets**: `code-reviewer` contract, `spec-review` skill, `review-01.yaml` of this unit.

## Evidence

```text
review-01 unverified_areas: "Findings 2 and 3 come from reading the code; no probe test was run, because copying the
frontend into the scratchpad to run vitest was denied and the worktree is read-only."
```
