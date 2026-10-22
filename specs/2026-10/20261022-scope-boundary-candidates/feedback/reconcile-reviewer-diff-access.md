---
id: FB-reconcile-reviewer-diff-access
title: Reconcile reviewer cannot read the diff it must compare
scope: repo
kind: friction
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/reconcile-reviewer.md
skill: spec-sync
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-reconcile-reviewer-diff-access] Reconcile reviewer cannot read the diff it must compare

## 1. Friction / Question (friction, question)

- **Context**: A development-worker delegated the medium-effort reconcile check of a spec unit to `reconcile-reviewer`.
- **Expectation**: The role contract asks it to "compare the diff in `diff_scope` with the docs changes and
  `reconcile.md`" and to report the verification as stale when the head moved.
- **Actual**: On claude-code the role has only Read, Grep and Glob, so it can neither run `git diff` for the range
  nor confirm the head; it reported both as unverified.
- **Workaround (or Interpretation Chosen)**: The worker exported `git diff <base> <head> -- docs/ <package src>` to an
  ignored `tmp/` path inside the worktree and named it in the prompt; the reviewer read the patch and the current
  files.
- **Suggestion**: Either state in the role contract and `spec-delegate` that the caller passes the range's diff as a
  file in the worktree (and the head it was taken at), or give the role a read-only Git command on hosts that allow
  one.

## Diagnostic Details

- **Reproduction**: Delegate `reconcile-reviewer` with only `diff_scope: base -> head` and no diff file.
- **Expected / Actual**: The reviewer compares the range's diff / it can read only current files and must infer the
  diff.
- **Versions**: devkit worktree at 01cfbda5 and later.
- **Conditions**: claude-code host, `reconcile-reviewer` frontmatter `tools: [Read, Grep, Glob]`.
- **Workarounds Attempted**: Diff exported to an ignored worktree path; the check completed with head staleness
  unverified.
- **Related Assets**: `.devkit/managed/spec/subagents/reconcile-reviewer.md`, the `spec-delegate` skill.

## Evidence

```text
reconcile-reviewer return, unverified_areas: "I could not check that HEAD is still b61af7b7 (no shell), so
staleness is unconfirmed." and "I did not run the tests or the rules check."
```

## Disposition

- **Disposition (resolved)**: `SPEC-superseded-reference-cleanup` gives the `reconcile-reviewer` the `challenger` host settings
  (claude-code `Bash` with `Write` and `Edit` disallowed, codex `sandbox_mode: read-only`, antigravity `run_command`
  under the sandbox policy), keeps `x-git-actions: [read]`, and directs it to run `git diff <base> <head>` for
  `diff_scope` and compare `git rev-parse HEAD` with the `diff_scope` head. Verified by the new assertions in
  `test_support_roles_shell_access`, `just test-affected` (mode=full, 4664 passed), the regenerated projections and
  `devkit sync --check`.
