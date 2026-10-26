---
id: FB-workspace-root-help-resolution-order
title: Workspace-root help misstates the resolution order in distribution commands
scope: repo
kind: change-request
category: docs-mismatch
target: packages/devkit-dist/src/devkit_dist/features/distribution/cli/output.py
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-workspace-root-help-resolution-order] Workspace-root help misstates the resolution order in distribution commands

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the distribution command groups (`devkit playbook get`, `devkit playbook search` and the
  other modules importing `WORKSPACE` from `cli/output.py`) describe `-w/--workspace-root` as "the nearest directory
  with .devkit/, else the Git top level, else the current one", while `find_project_root` returns the Git top level
  first inside a work tree and walks to the nearest `.devkit/` only outside Git. The shared default
  `WORKSPACE_HELP` in `adapters/cli.py` uses a second wording for the same behavior.
- **Proposed Procedure**: keep one help text for the option, stated in the resolution order the code applies, and
  drop the distribution-specific wording.
- **Expected Benefit**: agents predict the root correctly and avoid `DEVKIT_ROOT_NESTED` and `ARGUMENT_INVALID`
  retries; one text to keep accurate.
- **Cost & Risk**: help assertions in the distribution tests change; no behavior change.
- **Attempted**: not applied: finding RR-1 of the read-only review-refactor sweep in `materials/sweep.md`, which
  stops at its decision round by design; restart on a review-refactor decision round over the CLI surface or the
  next change to `cli/output.py`.

## Evidence

```text
cli/output.py:26-28  WORKSPACE = workspace_option("Project root (default: the nearest directory with .devkit/, else the Git top level, else the current one).")
adapters/cli.py:81   WORKSPACE_HELP = "Workspace root directory [default: the devkit project containing the current directory]"
project.py:125-138   toplevel = git_toplevel(origin); if toplevel is not None: ... return toplevel; else walk parents for .devkit/
```

## Disposition

Resolved by `SPEC-living-spec-consistency-sweep`: `WORKSPACE` in
`packages/devkit-dist/src/devkit_dist/features/distribution/cli/output.py` now uses the shared default
`WORKSPACE_HELP` of `devkit_dist.adapters.cli`, so every distribution command describes `-w/--workspace-root` as
"Workspace root directory [default: the devkit project containing the current directory]", one text for the option.
Verified with `devkit sync --help` and `devkit playbook search --help`.
