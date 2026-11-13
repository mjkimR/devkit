---
reconcile_id: REC-uiux-improve-impeccable-context-links
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    resolution: modified
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    resolution: modified
  - file: docs/decisions/2026-11/20261113-impeccable-context-links.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-impeccable-session-authority.md
    resolution: modified
  - file: packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/README.md
    resolution: modified
  - file: packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/SKILL.md
    resolution: modified
  - file: packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/references/orchestration.md
    resolution: modified
  - file: packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/references/context-links.md
    resolution: modified
---

# Reconciliation: `SPEC-uiux-improve-impeccable-context-links`

`CAP-DLV-uiux-improvement` rules 1, 19 and 27–30 plus section 4.1 reflect the actual script contract and consumer
authority. `UC-improve-an-interface-and-user-flow` extensions 3e/3f and scenarios27/28 cover per-worktree setup and
manual recovery. `ADR-impeccable-context-links` was promoted by handoff; its prior-ADR partial pointer remains exact,
and its traces now name actual capability clauses rather than planned amendments.

The guide describes source preparation, per-worktree/per-clone setup, common excludes, check/exit states, source-side
ignore ownership, quiescence and manual recovery. The conditional router and helper reference keep the source
bundle self-contained within its size bound; the orchestration setup list names the same requested action.
The Host explicitly admitted the router-only SKILL.md edit and new helper reference before their first commit.

All AC01–08 have helper/projection/authority tests. Initial medium code-review P2s are closed by reverify-01 and
regressions for absent-lock I/O failure and later unreadable directory content. Source lint/types pass; affected
native all-tier selection passed227 tests. BusyBox, Windows and live editor/Impeccable execution remain unverified;
these exclusions do not defer a required criterion. No new term, architecture edge, runtime dependency or policy
beyond the accepted setup ADR was introduced. No source feedback or concrete deferred implementation remains.

Entrypoint review keeps the main skill and helper as doorways for the capability and use case. Reference files,
README, tests and the broad scripts directory are not independent doorway candidates.
