---
id: PROP-automatic-scope-collection-target
title: Target Living Spec for creation snapshots and host scope collection
status: draft
proposal: PROP-automatic-scope-collection
created_at: 2026-10-25
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
  - file: docs/usecases/collaboration/UC-run-parallel-work-safely.md
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  - file: docs/decisions/2026-10/20261022-worktrees-branches-and-scope.md
---

# Target Living Spec for PROP-automatic-scope-collection

## Capability and use case changes

- CAP-COLL-work-scope-registry: retain automatic creation registration and introduce explicit Host collection.
  Define `snapshot`, `refs` and `worktrees` observation modes, independent opt-in fetch, inventory selection,
  ref-based inputs, provenance, identity/deduplication, partial coverage and bounded execution. Collection leaves
  worker records, tokens, revisions and journals unchanged. Preserve read-only query/history/compare behavior,
  explicit maintenance semantics and post-finish cleanup. Hide `update` from ordinary discovery.
- UC-run-parallel-work-safely: replace mandatory worker-update scenarios with initial evidence and explicit Host
  observation before scheduling decisions. Include unregistered branches, divergent refs, inaccessible worktrees,
  snapshot-only tasks, partial results and private changes on other machines. Overlap evidence does not grant
  writes or certify independence.
- CAP-HARN-agent-guidance: remove worker scope registration/update/ACK obligations from task writing,
  reconciliation and worker acceptance. Explain Host observation modes and recommend PRs with pushed changes
  for frequent multi-PC work. Do not add a replacement worker command or workflow trigger.

CAP-DLV-workflow-orchestration requires no collection extension or evaluation side effect. Explicit and internal
`workflow next` calls remain free of scope collection and publication.

Creation registration failures preserve primary outcomes, including `--strict`, and produce only verbose
diagnostics without worker recovery duties. Explicit Host collection reports incomplete coverage through stable
codes and notices; an operation that cannot run raises an advisory error. Explicit maintenance failures keep their
own error/ACK contract. Preserve actual snapshot publication times and report fresh observation times separately.

## Decision impact

Planning creates a PADR replacing the skill-maintained refresh decision in ADR-worktrees-branches-and-scope with
creation snapshots and explicit Host observation. Preserve linked-worktree registration eligibility, Git storage,
owner tokens and post-finish cleanup. Record cloud-backed shared registry storage (for example Firestore) as a
future direction for cross-PC handoff snapshot sharing, conditional on backend configuration, shared identity,
credentials and publication/ownership contracts. Do not add a cloud adapter or its acceptance checks in this scope.
Document silent creation failure handling and the boundary between local
worktree observation, fetched remote commits and invisible private changes. Add the resulting ADR target when it
exists; this draft does not approve a change to storage or ownership.

## Agent assets and command discovery

Change the source spec bundle and regenerate projections through ordinary sync. Do not manually edit managed or
projected files. Hide `scope update` from ordinary help and generated agent discovery while retaining direct
maintenance invocation. Inspect discovery before widening implementation ownership. No harness runtime hook is
part of this design.

## Settled Planning direction

PADR-host-owned-scope-observation replaces only the skill-refresh portion of ADR-worktrees-branches-and-scope.
Add the reciprocal `superseded_by` metadata to the prior ADR without changing its decision text.
The command is `scope collect`, defaulting to `worktrees`, with `snapshot` and `refs` alternatives. Explicit
`--fetch <remote>` is separate from observation depth. Default budgets are 30 seconds total and 5 seconds per source.
Preserve per-source observations, conservative unregistered ranges, lifecycle ambiguity and partial comparison
coverage. Development validates the output contract and runtime bounds defined in the proposal; the synthetic
Planning measurements are not end-to-end acceptance evidence.

## Before and after

Before: creation registers initial linked-worktree scope; workers must publish subsequent changes.
After: creation retains initial registration; the Host explicitly collects available evidence at the requested
observation mode. Separate clones do not automatically share registry snapshots. Remote refs and PRs expose only
published commits, and no mode observes another PC's dirty or unpushed work.
