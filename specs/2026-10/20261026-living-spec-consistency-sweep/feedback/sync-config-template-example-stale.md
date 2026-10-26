---
id: FB-sync-config-template-example-stale
title: The commented config template example shows a boolean tool.spec worktree
scope: repo
kind: change-request
category: docs-mismatch
target: CAP-DIST-sync-and-transactions (Commented Template)
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-sync-config-template-example-stale] The commented config template example shows a boolean tool.spec worktree

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the "Commented Template" example of `CAP-DIST-sync-and-transactions` shows
  `# worktree = true  # boolean; route 2 and above (formal specs, proposals) run in a task worktree` under
  `[tool.spec]`. devkit-spec's template key is `worktree` with `"auto" | "required"` (default `"auto"`), and a
  boolean is `SPEC_CONFIG_INVALID` (`CAP-DLV-project-policy` rule 5).
- **Proposed Procedure**: regenerate the example from the current `devkit config template` output.
- **Expected Benefit**: an agent copying the example does not write a refused value.
- **Cost & Risk**: one example block; no behavior.
- **Attempted**: not edited: outside the 22 findings of `SPEC-living-spec-consistency-sweep`.

## Diagnostic Details

- **Reproduction**: compare the example with `template()` in
  `packages/devkit-spec/src/devkit_spec/features/policy/services/config.py`.
- **Expected / Actual**: `worktree = "auto"  # "auto" | "required"` / `worktree = true  # boolean`.
- **Versions**: worktree head of `dev-living-spec-consistency-sweep`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-DIST-sync-and-transactions`, `CAP-DLV-project-policy`.

## Evidence

```text
CAP-DIST-sync-and-transactions: #   worktree = true  # boolean; route 2 and above (formal specs, proposals) run in a task worktree
config.py template(): TemplateKey("worktree", defaults.worktree, ..., kind='"auto" | "required"')
```

## Disposition

Resolved by `SPEC-feedback-guidance-and-scope` (item 8): the `CAP-DIST-sync-and-transactions` template example shows `worktree = "auto"  # "auto" | "required"; ...` as `devkit config template` prints it. Verified against `devkit config template --print` and `policy/services/config.py`.
