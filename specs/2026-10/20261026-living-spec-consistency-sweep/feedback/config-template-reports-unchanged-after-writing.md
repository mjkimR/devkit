---
id: FB-config-template-reports-unchanged-after-writing
title: devkit config template reported unchanged while it added commented tables
scope: repo
kind: friction
category: tool-error
target: devkit config template
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-config-template-reports-unchanged-after-writing] devkit config template reported unchanged while it added commented tables

## 1. Friction / Question (friction, question)

- **Context**: checking the `[tool.spec] worktree` template key for a documentation finding, by running
  `uv run devkit config template` in a task worktree.
- **Expectation**: a command that writes `.devkit/config.toml` reports what it added; its JSON result names the
  change, so an agent knows a tracked file changed.
- **Actual**: the result was `{"path": ".devkit/config.toml", "state": "unchanged", "added": [], "notices": []}`,
  while `git diff` showed about 30 added comment lines (the header, the managed-scope and update-policy comments,
  `[shared]`, `[workflow.stages]`, `[[tool.spec.namespaces]]` and `[tool.spec.scope]` blocks).
- **Workaround (or Interpretation Chosen)**: restored the committed file content and read the template from
  `template()` in the source instead.
- **Suggestion**: report commented additions in `added` and a `state` other than `unchanged` whenever the file
  bytes change, or offer a read-only form (`--dry-run` or stdout) for inspecting the template.

## Diagnostic Details

- **Reproduction**: `uv run devkit config template` in a checkout whose `.devkit/config.toml` lacks those commented
  blocks; then `git diff .devkit/config.toml`.
- **Expected / Actual**: a reported change / `state: unchanged`, `added: []` with a changed file.
- **Versions**: worktree head of `dev-living-spec-consistency-sweep`.
- **Conditions**: the repository's own `.devkit/config.toml` with selected bundles and `[tool.spec]` settings.
- **Workarounds Attempted**: restoring the file from `HEAD`; it removed the additions.
- **Related Assets**: `devkit config template`, `CAP-DIST-sync-and-transactions` (Commented Template).

## Evidence

```text
{"path": ".devkit/config.toml", "state": "unchanged", "added": [], "notices": []}
git diff .devkit/config.toml: @@ -1,3 +1,17 @@ ... @@ -37,3 +51,23 @@ (commented header and tables added)
```

## Disposition

Resolved by `SPEC-handoff-modes-and-template-report` (decision 4): the mismatch does not reproduce in one invocation at base `2bbd8251`; the write and its report come from one comparison, and the repository's own `.devkit/config.toml` reports `updated` with seven added names, then `unchanged` with `added: []` on a second run, which matches the observation. A CLI regression test pins the contract (bytes changed with `updated` and every commented key and table named, then `unchanged` with the bytes kept, and `--print` agreeing with the write), and `CAP-DIST-sync-and-transactions` (Commented Template) and the distribution reference state that `state` is `unchanged` exactly when the bytes stay the same. No code change.
