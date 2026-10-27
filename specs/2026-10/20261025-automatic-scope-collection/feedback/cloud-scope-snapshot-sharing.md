---
id: FB-cloud-scope-snapshot-sharing
title: Retain cloud-backed sharing of initial handoff snapshots
scope: repo
kind: change-request
category: missing-capability
target: packages/devkit-spec/src/devkit_spec/features/scope/models/registry.py
origin: user
severity: noise
recurring: false
status: dismissed
created_at: 2026-10-25
---

# [FB-cloud-scope-snapshot-sharing] Retain cloud-backed sharing of initial handoff snapshots

## 2. Suggestion / Change Request

- **Current Procedure**: SPEC-automatic-scope-collection retains initial snapshots in the local filesystem registry.
  Separate clones/machines do not automatically share that storage.
- **Proposed Procedure**: When cross-PC snapshot sharing becomes an implementation requirement, design a shared
  registry repository adapter, with Firestore as one possible backend. Settle backend selection, shared repository
  and namespace identity, credentials, ownership, publication and cross-machine registration eligibility first.
- **Expected Benefit**: A Host on another PC can read an initial handoff snapshot without a distributed watcher.
- **Cost & Risk**: Backend availability and authorization become dependencies. Creation snapshots still omit later
  private dirty/unpushed changes. This deferred work is excluded from the current runtime acceptance criteria.
- **Attempted**: Direction recorded in ADR-host-owned-scope-observation; no cloud adapter or service was implemented.

## Diagnostic Details

- **Reproduction**: Registry storage defaults to each repository's Git common directory.
- **Expected / Actual**: Shared initial snapshots are a future requirement; only linked local worktrees share defaults.
- **Versions**: SPEC-automatic-scope-collection.
- **Conditions**: Multiple PCs or isolated clones need initial task scope evidence.
- **Workarounds Attempted**: Current Host observation reads fetched refs; PR guidance covers published changes.
- **Related Assets**: CAP-COLL-work-scope-registry; ADR-host-owned-scope-observation.

## Evidence

`LocalRegistry` is the deployed registry adapter. The accepted ADR names cloud-backed initial snapshot sharing as
future direction only. Future acceptance should use separate clones against one configured adapter to verify initial
publication/read visibility, ownership and failure isolation, without claiming observation of private later changes.

## Disposition

Dismissed on the user's decision (2026-10-27). It records no observed failure, and the cloud sharing direction is
already recorded in `ADR-host-owned-scope-observation` and `CAP-COLL-work-scope-registry`. Raise it as a proposal when
cloud scope sharing is planned.
