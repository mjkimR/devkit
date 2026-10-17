---
id: ARCH-06-runtime-view
title: Runtime View
summary: "Runtime scenarios: transactional bundle synchronization, rule evaluation and repair, and task worktree workflows."
status: active
created_at: 2026-10-17
---

# [ARCH-06-runtime-view] Runtime View

- **arc42**: §6 Runtime View
- Components: `ARCH-05-2-components`. Cross-cutting: `ARCH-08-cross-cutting`.

---

## 1. Scenario 1: Transactional Bundle Synchronization (`devkit sync`)

`devkit sync` ensures atomic deployment of bundle assets and projections into consumer repositories:

```mermaid
sequenceDiagram
    participant Dev as Agent / Engineer
    participant CLI as devkit sync
    participant Dist as devkit.distribution
    participant Journal as .devkit/transient/
    participant Target as .devkit/managed/ & Projections
    participant Receipt as .devkit/installation.json

    Dev->>CLI: devkit sync
    CLI->>Dist: execute_sync()
    Dist->>Dist: Discover installed bundles & presets
    Dist->>Journal: Open transaction journal
    loop For each selected asset
        Dist->>Target: Write/update managed files & projections
        Dist->>Journal: Record written paths & previous state
    end
    Dist->>Target: Update root AGENTS.md guidance block
    Dist->>Receipt: Commit installation receipt atomically
    Dist->>Journal: Remove transaction journal
    Dist-->>CLI: Report sync statistics & notices
    CLI-->>Dev: [SYNC: state=clean added=... updated=...]
```

If an error or process termination occurs midway, `devkit recover` reads `.devkit/transient/` to roll back modified files to their previous clean baseline.

---

## 2. Scenario 2: Governance Rule Evaluation & Autofix (`devkit rules check|fix`)

```mermaid
sequenceDiagram
    participant Dev as Developer / Hook
    participant Engine as devkit.rules
    participant Cache as Workspace Cache
    participant Scanner as Rule Scanners

    Dev->>Engine: devkit rules check [--staged]
    Engine->>Cache: Build snapshot index (Git or Working Tree)
    loop For each active rule in phase order (syntax -> hygiene -> linter -> contract)
        Engine->>Scanner: Evaluate rule against targets
        Scanner-->>Engine: Return list of Violations
    end
    alt When running under `fix`
        Engine->>Scanner: Apply deterministic repairs
        Engine->>Engine: Re-evaluate convergence
    end
    Engine-->>Dev: Print [SUMMARY: errors=N warnings=N fixed=N]
```

---

## 3. Scenario 3: Task Worktree Lifecycle (`devkit worktree start|finish`)

1. **Start**: `devkit worktree start <branch> [--unit <dir>]` checks that no uncommitted conflicts exist, checks that the branch does not already exist, and creates a linked Git worktree under `.devkit/worktrees/<slug>`.
2. **Execute**: The agent runs development tasks isolated within the allocated worktree.
3. **Finish**: `devkit worktree finish [--merge]` validates that envelopes hold no unresolved questions or problems, commits final artifacts, integrates into the base branch, and safely removes the worktree.
