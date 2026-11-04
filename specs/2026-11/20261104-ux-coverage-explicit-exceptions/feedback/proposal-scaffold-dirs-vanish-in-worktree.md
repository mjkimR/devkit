---
id: FB-proposal-scaffold-dirs-vanish-in-worktree
title: Proposal scaffold's empty decisions and materials directories do not exist in the Planning worktree
scope: repo
kind: friction
category: tool-error
target: devkit spec proposal new
origin: agent
severity: workaround
recurring: false
status: promoted
created_at: 2026-11-04
---

# [FB-proposal-scaffold-dirs-vanish-in-worktree] Proposal scaffold's empty decisions and materials directories do not exist in the Planning worktree

## 1. Friction / Question (friction, question)

- **Context**: Planning of a draft proposal on its `plan-<slug>` worktree; writing the first comparison file to the
  proposal's `materials/` directory as the planning reference asks.
- **Expectation**: the proposal bundle created by `devkit spec proposal new` has `decisions/` and `materials/`, as
  the base checkout shows.
- **Actual**: both directories are empty in the scaffold, Git tracks no empty directory, so the worktree created by
  `devkit worktree start plan-<slug>` has neither; the write to `materials/<file>.md` failed with "no such file or
  directory". `devkit spec proposal padr` creates `decisions/` itself, so only `materials/` bites.
- **Workaround (or Interpretation Chosen)**: `mkdir -p` before writing.
- **Suggestion**: either stop creating the empty directories in the scaffold (the `padr` command and the Scout's
  materials write create them on demand) or seed each with a tracked placeholder; and let the planning reference say
  that `materials/` may need creating. The first option keeps the bundle honest about what it holds.

## Diagnostic Details

- **Reproduction**: `devkit spec proposal new <slug>` on the base, commit, `devkit worktree start plan-<slug>`,
  then write to `<worktree>/docs/proposals/PROP-<slug>/materials/x.md`.
- **Expected / Actual**: expected the directory to exist; the shell reported no such file or directory.
- **Versions**: the repository at the base commit of this Planning (main, 2026-11-04).
- **Conditions**: any proposal whose Planning starts in a fresh worktree before a PADR or material was committed.
- **Workarounds Attempted**: `mkdir -p` succeeded.
- **Related Assets**: `devkit spec proposal new`, `devkit worktree start`, the spec skill's `references/planning.md`.

## Evidence

```text
$ ls -la docs/proposals/PROP-<slug>        # base checkout, right after the scaffold commit
drwxr-xr-x  decisions
drwxr-xr-x  materials
-rw-r--r--  proposal.md
$ cat > <worktree>/docs/proposals/PROP-<slug>/materials/notation-comparison.md
no such file or directory: <worktree>/docs/proposals/PROP-<slug>/materials/notation-comparison.md
```

- **Disposition**: `PROP-proposal-scaffold-and-handoff-pointers`: the scaffold creates no empty directories; the planning reference names on-demand creation.
