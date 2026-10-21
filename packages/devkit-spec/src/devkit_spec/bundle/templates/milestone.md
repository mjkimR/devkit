---
id: MS-<slug>
title: <Milestone title>
summary: "<The goal and exit condition this milestone owns.>"
status: planned
created_at: <YYYY-MM-DD>
# depends_on: [MS-foundation] # MS-only prerequisites; omit when empty
---

# [MS-<slug>] <Milestone title>

## Goal

Cite the goal in ARCH-01-introduction-and-goals. Use a word-led slug, for example MS-release-1-0.
User and agent jointly review a multi-unit phase, release or architectural theme and decompose it into direct PROP
members. A theme may initially have one proposal while broader scope is not authored; it SHOULD NOT exist solely
as a sequencing gate. Use unit depends_on for unit ordering.

## Exit condition

State observable phase-level outcomes and capability boundaries. CLI flags, branch names, file layouts and scenario
tests belong in proposals/specs. Only direct PROP anchors declare membership through milestone; do not list work
here. Handoff does not carry milestone metadata to SPEC. Inspect downstream code/Git on demand; do not store lineage.

## Non-goals

- **Scope Excluded**: <what this milestone does not deliver>
