---
id: ADR-impeccable-context-links
title: User-requested links to tracked Impeccable context
summary: "For tracked Impeccable context across worktrees, we ship a user-requested POSIX link helper with read-only inspection, to reuse one source without overwrites, accepting per-worktree setup and source-side ignore management."
proposal: SPEC-uiux-improve-impeccable-context-links
supersedes: [ADR-impeccable-session-authority]
status: accepted
created_at: 2026-11-13
---

# [ADR-impeccable-context-links] User-requested links to tracked Impeccable context

- **Status**: Accepted
- **Date**: 2026-11-13

## 1. Context & Problem Statement

Consumer-owned Impeccable context kept only at the checkout root is absent from another worktree or clone.
The existing setup list allows `.impeccable/` ignore entries but does not permit root context links/excludes.
A tracked source plus relative root links retains one copy, while atomic-save replacement can fork the content.

## 2. Decision Drivers

- Reuse tracked context inside each worktree without a devkit runtime dependency.
- Preserve every occupied root entry and consumer-owned content.
- Keep setup requested and bounded; make context inspection read-only.
- Keep upstream retention policy independent of root-link exclusions.

## 3. Considered Options

- Keep manual linking and local-only absolute-path briefing: no shipped helper, but per-worktree setup and fork
  detection remain manual. The briefing path stays available for projects that do not use the helper.
- Add a devkit CLI/configuration surface: structured runtime integration, but requires devkit in the consumer and
  expands a content-only bundle into application behavior.
- Ship one optional POSIX script inside the existing skill: uses installed Git/POSIX tools, preserves occupied
  entries and reports drift, with explicit setup in each clone/worktree and bounded platform coverage.

## 4. Decision Outcome

Choose the optional script, because it supplies reproducible requested setup and read-only drift inspection without
introducing a Python feature, installer or upstream runtime.

- On the user's request, the coordinator can run the bundled script to create absent relative root links for
  `PRODUCT.md`, `DESIGN.md` and `.impeccable`, and append only missing `/PRODUCT.md`, `/DESIGN.md`, `/.impeccable`
  lines to the resolved Git exclude file after showing the exact lines. → `CAP-DLV-uiux-improvement` rule 19 (MAY).
- The coordinator can run the script's read-only check while gathering context. Every mutating setup operation
  still follows the user's selected task route and host permissions. → `CAP-DLV-uiux-improvement` rule 19 (MAY).
- The helper preserves existing root entries and source bytes, emits stable codes/actions and uses exits 0, 1 and 2
  for clean, problems and unable to run. Mutating setup requires quiescent root entries and source; it makes no
  guarantee about noncooperating concurrent writers. → `CAP-DLV-uiux-improvement` rules 27–29 (MUST).
- Source-side ignores remain consumer-owned; linking `.impeccable` does not authorize installing ignore rules or
  writing context content. → `CAP-DLV-uiux-improvement` rules 18–19 (MUST).
- A POSIX script is shipped content inside the skill, with no devkit Python feature, new asset kind or runtime
  dependency. The restriction on adding Impeccable runtime/installer/vendor content stays in force.

Supersedes in part `ADR-impeccable-session-authority`: Decision Outcome setup clause limiting user-requested ignore additions to `.impeccable/` paths and its setup-action list, which now also permits requested root context links and exact root-link excludes through the bundled helper. Consumer content ownership, explicit request, task route, host permissions and no implicit Git authority remain in force.

## 5. Consequences

- Positive: each worktree reads its own tracked source through stable root entry points.
- Positive: check mode exposes missing, foreign, dangling, tracked and replaced entries without repair.
- Negative: links must be set up per worktree/clone, and source-side runtime ignores remain a separate consumer choice.
- Risk: an atomic-save editor can replace a link. The helper reports it; reconciliation remains user-directed.
- Risk: GNU/BusyBox utility behavior and unsupported Windows checkouts require explicit test/coverage reporting.

## 6. Confirmation

- Development subprocess integration tests under `packages/devkit-catalog/tests/integration/bundles/` cover link
  states, no overwrites, check-mode immutability, exclusion, portability cases and linked worktrees.
- Existing `test_app_uiux_improve.py` extends projection byte checks and instruction authority assertions.
- Review only: consumer selection of source-side retention and actual upstream/editor save behavior.
