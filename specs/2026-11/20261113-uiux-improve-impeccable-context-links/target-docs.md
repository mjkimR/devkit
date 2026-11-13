---
id: PROP-uiux-improve-impeccable-context-links-target
title: Target contracts for tracked Impeccable context links
summary: "The capability, use case, decision and bundle text changes for the optional POSIX context-link helper, including requested mutations and read-only checks."
status: draft
proposal: SPEC-uiux-improve-impeccable-context-links
created_at: 2026-11-13
targets:
  - file: docs/decisions/2026-11/20261113-impeccable-context-links.md
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
  - file: docs/decisions/2026-11/20261110-impeccable-session-authority.md
  - file: packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/README.md
  - file: packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/references/orchestration.md
---

# [Blueprint] Tracked Impeccable context links

## Living Spec

- `CAP-DLV-uiux-improvement` rule 1 counts the script in the existing skill asset. Rule 19 permits requested links
  and exact root excludes. A helper contract covers fixed entries, preflight, no overwrites, checks, codes and exits.
- `UC-improve-an-interface-and-user-flow` adds a step-3 setup extension for an optional requested link operation and
  a read-only context check; Given/When/Then examples cover linked worktrees and replacement recovery.
- `ADR-impeccable-context-links` promotes at handoff. Its partial-supersession pointer is added to
  `ADR-impeccable-session-authority`; its remaining clauses stay unchanged.
- Architecture is unchanged: this is content under an existing skill, with no Python feature or dependency edge.

## Bundle text

- `references/orchestration.md` Project files and user requests conditionally invokes the script for the requested
  setup, shows the exact exclude lines, permits inspection with `--check` and preserves content/route authority.
- The guide documents committing the source separately, default and explicit layouts, each-worktree/clone link setup,
  independent source-side runtime ignores, quiescent setup and unsupported concurrent writers, exit states, and manual reconciliation after atomic-save replacement.
- Deployed instructions contain no authoring-repository IDs and require only their own script plus POSIX tools/Git.

## Implementation owners

- `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/` owns the new scripts
  directory; the script is not a manifest asset of its own.
- `packages/devkit-catalog/tests/integration/bundles/` owns the subprocess matrix and projection assertions.
