---
id: ADR-archive-terminal-milestones-in-roadmap
title: Archive terminal milestones in a flat roadmap directory
summary: "For a roadmap that separates live themes from history, we keep done and dropped milestones in one flat archive, to preserve identity and browsing while clearing the root, accepting coordinated reader and guidance updates."
proposal: SPEC-milestone-archive
supersedes:
  - ADR-roadmap-and-milestones
status: accepted
created_at: 2026-10-28
---

# [ADR-archive-terminal-milestones-in-roadmap] Archive terminal milestones in a flat roadmap directory

## 1. Context & Problem Statement

`ADR-roadmap-and-milestones` keeps global milestone identity, status, direct proposal membership and user-owned
lifecycle decisions in repository files. Root-only storage mixes four done themes with current work. The document
index already supports nested Markdown; validator, authoring and viewer path assumptions prevent a coherent archive.

## 2. Decision Drivers

- Separate current themes from history in filesystem browsing without changing identity or lifecycle meaning.
- Keep history lookup, aliases, incoming references, prerequisite readiness and existing viewer access intact.
- Retain simple Backlog file operations and concrete user authority; introduce no new runtime command or registry.
- Preserve existing contents and completion evidence when relocating old history.

## 3. Considered Options

- Keep terminal milestones at the root: no reader work, but the requested filesystem separation is not delivered.
- One flat `_archive` directory: one extra path pattern, preserves identity and existing status filters; all path-based
  consumers must agree before files move.
- Year/status subdirectories: more partitions and validation/discovery branches without a demonstrated browsing need.
- A copied index, archive status or archive command: centralizes moves but adds derived state or lifecycle machinery
  for an occasional user-owned Backlog edit.

## 4. Decision Outcome

Use the flat archive. Live milestones remain at the global roadmap root;
done/dropped files use `docs/roadmap/_archive/` with the same filename and identity. Both statuses already satisfy
milestone prerequisites, and history stays derived from status rather than directory.

This partially supersedes only the root-only milestone storage convention in `ADR-roadmap-and-milestones`.
Its identity, membership, dependency and closure authority remain unchanged. Follow the partial-supersession
precedent of `ADR-milestone-merging`; do not retire that larger decision or rewrite its unrelated outcomes.

Placement validation belongs with existing document conventions. Close/drop/reopen guidance combines existing
user decisions, applicable status/assertions/disposition and file movement in one Backlog commit. Checks report
invalid placement rather than automatically changing state. Merging historical themes and alias preservation remain.

Readers and tests land before the approved content-preserving batch. The four-file candidate manifest is review
evidence, not a runtime protocol or authority. Refresh changed candidate effects before applying them.

## 5. Consequences

- Positive: filesystem browsing, document tools and viewer history agree while old IDs and dependencies stay valid.
- Cost: docs/spec validators, agent guidance and Python/TypeScript viewer discovery need coordinated coverage.
- Risk: a root-only reader can hide history or make an edge unknown. The reader inventory and two loader-path tests
  address that concrete failure; ordinary file comparisons handle relocation collisions and content preservation.
- No package split, new archive screen, lifecycle evaluator or automatic data migration is required.

## 6. Confirmation

Development checks AC-01 through AC-08: path/status and historical targeting, lookup/alias/refs/search, membership
notice, both terminal dependency states, optimized/generic viewer loading and detail, close/drop/reopen and the exact
byte-preserving batch. Run affected Python tests plus viewer lint/check/test/build and rebuild its committed page.
Semantic transition correctness and concrete batch authority are review-only; a rule cannot certify user intent.
