---
id: PROP-automatic-scope-collection-target
title: Target Living Spec for automatic work scope collection
status: draft
proposal: PROP-automatic-scope-collection
created_at: 2026-10-25
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
  - file: docs/usecases/collaboration/UC-run-parallel-work-safely.md
  - file: docs/capabilities/delivery/CAP-DLV-workflow-orchestration.md
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
---

# Target Living Spec for PROP-automatic-scope-collection

## Capability and use case changes

- CAP-COLL-work-scope-registry: define the three automatic triggers, local observation and publication,
  unchanged-snapshot behavior, ownership, bounded failure notices and the hidden maintenance command.
  Preserve side-effect-free queries and the limitation on visibility between isolated registries.
- UC-run-parallel-work-safely: replace manual-update scenarios with creation and workflow-boundary collection.
  Include timing gaps, cloud standalone identity, ownership mismatch and publication failure scenarios.
- CAP-DLV-workflow-orchestration: document the explicit `next` operation's optional observation extension,
  separate collection outcome and budget, and the absence of observation side effects in internal evaluation.
- CAP-HARN-agent-guidance: remove explicit scope refresh duties from task writing, reconciliation and worker
  acceptance; describe automatic collection at existing CLI boundaries.

## Decision impact

Planning will create a PADR replacing the skill-maintained refresh decision in
ADR-worktrees-branches-and-scope and recording the observation side effect of explicit `next`. Its
linked-worktree-only participation decision also needs replacement if standalone registration is selected. Add the exact resulting ADR
target when that decision exists; this draft does not pre-approve a change to its storage or ownership contract.

## Agent assets and command discovery

Change the source spec bundle and regenerate projections through ordinary sync. Keep managed and projected files
outside manual edits. Hide `scope update` from normal help and generated agent discovery while retaining explicit
maintenance invocation. Confirm discovery behavior before widening implementation boundaries.

## Before and after

Before: linked-worktree creation registers initial scope; agents explicitly publish later changes.
After: creation registers initial scope and explicit `workflow next` refreshes the current task automatically.
Standalone cloud participation remains an acceptance-blocking design question until Q2 is demonstrated.
