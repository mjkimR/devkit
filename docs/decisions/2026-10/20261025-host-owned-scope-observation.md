---
id: ADR-host-owned-scope-observation
title: Creation snapshots and host-owned scope observation
summary: "For parallel work scope evidence, we retain creation snapshots and use explicit host observation, to remove worker publication duties, accepting incomplete remote visibility."
supersedes: ADR-worktrees-branches-and-scope
proposal: SPEC-automatic-scope-collection
status: accepted
created_at: 2026-10-25
---

# [ADR-host-owned-scope-observation] Creation snapshots and host-owned scope observation

- **Status**: Accepted
- **Date**: 2026-10-25

---

## 1. Context & Problem Statement

CAP-COLL-work-scope-registry provides advisory overlap evidence. ADR-worktrees-branches-and-scope assigns scope
refresh to skills. Those worker calls add token, retry and ACK duties without proving freshness when the Host
schedules another task. Creation already registers initial scope, while host-visible worktrees and branch trees
contain later evidence that can be read without modifying registrations.

This decision replaces only that ADR's skill-maintained refresh decision. Its worktree policies, linked-worktree
registration eligibility, storage, ownership, branch guards and post-finish cleanup remain in force by incorporation in this decision. The `supersedes` link
records that limited replacement; Development adds the reciprocal metadata without rewriting the old decisions.

## 2. Decision Drivers

- Remove worker publication and ACK obligations.
- Make observation an explicit Host action with bounded cost.
- Preserve source attribution and report incomplete coverage.
- Keep the generic harness independent of spec observation.
- Accept local and published remote evidence without claiming distributed monitoring.

## 3. Considered Options

| Option | Benefit | Cost or risk |
| --- | --- | --- |
| Keep skill updates | Reuses existing registry operation | Workers retain maintenance duties; records can lag silently |
| Automatic `workflow next` refresh | Uses existing worker boundary calls | Optional-provider hook, worker token recovery and timing gaps remain |
| Handoff snapshots only | Smallest implementation | Cannot inspect later local declarations, dirty paths or published branch changes |
| Creation snapshots plus explicit Host observation (selected) | Host chooses when and how much evidence to collect; no worker publication | Partial visibility and bounded scanning cost must remain explicit |
| Distributed registry/watchers now | Could share snapshots between machines | Requires backend, credentials, shared identity and publication contracts outside this scope |

## 4. Decision Outcome

Choose creation snapshots plus explicit Host collection as specified in PROP-automatic-scope-collection.

- Keep automatic creation registration best effort with verbose-only failure diagnostics and unchanged primary
  results, including `--strict`. No replacement worker recovery action is required.
- Remove worker scope registration/update/ACK duties and exclude all workflow evaluation triggers.
- Add `scope collect` with `snapshot`, `refs` and default `worktrees` modes, opt-in fetch and bounded deadlines.
- Read consistently through filesystem or pinned-tree source adapters. Collection leaves registry records, owner
  tokens, revisions and journal unchanged. Fetch affects only the requested remote-tracking branch namespace.
- Preserve per-source observations, deduplicate only confirmed identities with identical effective range/declaration inputs and expose unknown attribution,
  branch-relative committed ranges, missing layers and comparison coverage. Explicit collection failures and partial
  results retain the Agent Advisory Protocol; only automatic creation failure handling is silent.
- Hide maintenance `update` in ordinary discovery while retaining direct invocation and its existing ACK contract.
- Record a cloud-backed registry repository, such as Firestore, as a future direction for cross-PC initial snapshot
  sharing. Backend implementation and cross-machine registration are excluded. PRs provide published-change
  visibility in the meantime; neither PRs nor future creation snapshots reveal later private worktree edits.

## 5. Consequences

- The Host can inspect an unregistered branch or accessible worktree without acquiring its token.
- Worker omissions no longer control whether live host-visible evidence can be collected.
- Parsing must be extracted below use cases so target documents and entrypoints use the same source as declarations.
- Snapshots can be stale, remote refs can lag and another PC's dirty/unpushed work is invisible. A complete report
  means requested observable coverage, not global independence or a single atomic repository snapshot.
- Cross-PC snapshot sharing is reconsidered when it becomes an implementation requirement; this decision chooses no
  backend and promises no cloud adapter in this delivery.

## 6. Confirmation

Development verifies AC-01–AC-08 in PROP-automatic-scope-collection with scope/delivery integration tests and source
bundle guidance checks. Tests cover no token/registry writes, pinned-ref inputs, divergent refs, malformed or absent
inputs, source/total deadlines, comparison truncation, dense-output/input size limits, fetch outcomes and strict/non-strict output. Existing
ownership, maintenance ACK and post-finish cleanup tests remain regression checks. Planning evidence does not
substitute for these runtime checks. Guidance about PRs and future cloud storage is Review only.
