---
id: UC-snapshot-bundle-sources
title: Adopt and refresh bundle sources locally
summary: "A maintainer adopts a complete supported content provider as committed local sources and explicitly refreshes it without recurring private-origin authentication."
area: distribution
primary_actor: Maintainer
supporting_actors: []
status: active
capabilities:
  - CAP-DIST-in-repo-bundles
  - CAP-DIST-content-packages
  - CAP-DIST-workspace-ownership
  - CAP-DIST-sync-and-transactions
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/distribution/cli/bundles.py
  - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/snapshots.py
---

# [UC-snapshot-bundle-sources] Adopt and refresh bundle sources locally

## 1. Goal

- **Goal**: Reproduce selected private content from committed local sources and adopt upstream updates deliberately.
- **Scope**: Distribution source snapshots and existing content installation/sync.
- **Trigger**: A maintainer wants a reusable local copy or an explicit upstream refresh.
- **Preconditions**: Authorized local source access and required devkit/build dependencies are available.

## 2. Main Success Scenario

1. The maintainer identifies the provider, distinct wrapper identity and consumer destination (`CAP-DIST-in-repo-bundles`).
2. Distribution inspects and creates the complete local package with provenance (`CAP-DIST-in-repo-bundles`).
3. The maintainer reviews the complete replacement set and continuation (`CAP-DIST-content-packages`).
4. The maintainer performs the applicable package and selection changes (`CAP-DIST-content-packages`).
5. The maintainer runs normal sync to deploy selected sources (`CAP-DIST-sync-and-transactions`).
6. The maintainer commits sources, provenance and deliberate bootstrap changes (`CAP-DIST-workspace-ownership`).

## 3. Extensions

- **1a.** Destination is protected, overlapping, outside the consumer or symlinked: distribution refuses with
  `BUNDLE_SNAPSHOT_INVALID` or `BUNDLE_SNAPSHOT_CONFLICT`; the use case ends without content replacement.
- **2a.** Source layout/imports/declarative handlers need unsupported runtime closure:
  distribution refuses `BUNDLE_SNAPSHOT_UNSUPPORTED` before writes; the use case ends with the named requirement.
- **2b.** An intact snapshot exists and refresh is requested: distribution previews without writes, then adopts
  only the maintainer's reviewed/current identities; resumes at step 3.
- **2c.** Authored drift, stale review identities or edits during preparation/staging are detected:
  distribution preserves the actual tree and refuses `BUNDLE_SNAPSHOT_CONFLICT`; the use case ends.
- **2d.** Source/provenance/schema is invalid: distribution refuses `BUNDLE_SNAPSHOT_INVALID`; the use case ends.
- **2e.** Replacement validation/write fails: distribution restores the prior package when possible and reports
  `BUNDLE_SNAPSHOT_WRITE_FAILED` with any remaining recovery evidence; the use case ends.
- **4a.** A requirement retains the original provider: discovery refuses `BUNDLE_PACKAGE_INVALID`;
  the maintainer resolves the owning dependency group or transitive requirement; resumes at step 4.
- **4b.** Refresh changes entry points or removes a selected bundle: the maintainer reinstalls package metadata and
  explicitly deselects the removed bundle; resumes at step 5.
- **4c.** No direct origin-provider requirement exists: the maintainer skips direct removal and resolves any
  transitive origin requirement separately; resumes at step 5.
- **5a.** A project override exists: ordinary sync preserves the adaptation and reports upstream drift; resumes at step 6.

## 4. Postconditions

- **Success guarantee**: The local provider reproduces selected sources without private-origin access given required
  runtime/build prerequisites, with reviewable identity and a deliberate adoption commit.
- **Minimal guarantee**: Snapshot operations preserve authored changes and leave config, receipt, overrides and Git
  unchanged; reported failure preserves actual state or identifies recovery evidence.

## 5. Acceptance Criteria (Given / When / Then)

Rules: snapshot source/packaging/provenance, verified identity, preview, reviewed adoption, authored drift,
replacement recovery, idempotence, destination and explicit continuation (`CAP-DIST-in-repo-bundles`);
provider replacement/reinstall (`CAP-DIST-content-packages`); override preservation (`CAP-DIST-workspace-ownership`).

### Scenario 1: Adopt complete supported sources
- **Covers**: main success scenario
- **Given**: a supported multi-bundle checkout with self-contained rule helpers and named license files.
- **When**: a local package is adopted.
- **Then**: original bundle versions, bytes, modes, variants and templates survive with matching path-free provenance.

### Scenario 2: Reject an unsafe destination
- **Covers**: 1a
- **Given**: an out-of-root/protected destination or a symlink.
- **When**: creation is requested.
- **Then**: the operation refuses before replacing content.

### Scenario 3: Reject unsupported source closure
- **Covers**: 2a
- **Given**: a runtime dependency, external handler or syntactically dynamic import.
- **When**: preflight inspects it.
- **Then**: it names the unsupported requirement without executing source or writing a partial package.

### Scenario 4: Preview and adopt a refresh
- **Covers**: 2b
- **Given**: intact generated sources and changed upstream files or modes.
- **When**: the maintainer previews and applies the reported identities.
- **Then**: preview is read-only, adoption is coherent and unchanged inputs write nothing despite bytecode.

### Scenario 5: Preserve edits and reject stale review
- **Covers**: 2c
- **Given**: local drift, a mismatched candidate or an edit during preparation/staging.
- **When**: refresh reaches adoption.
- **Then**: the actual authored tree remains intact and the conflict is reported.

### Scenario 6: Reject invalid provenance
- **Covers**: 2d
- **Given**: an unknown schema or mismatched aggregate.
- **When**: refresh reads provenance.
- **Then**: it refuses rather than replacing the package.

### Scenario 7: Restore failed replacement
- **Covers**: 2e
- **Given**: an injected staged/installed validation or write failure.
- **When**: replacement fails.
- **Then**: the old package is restored; failed restoration preserves and names its recovery backup.

### Scenario 8: Keep provider uniqueness
- **Covers**: 4a
- **Given**: original provider and wrapper are both installed.
- **When**: discovery runs.
- **Then**: existing duplicate refusal remains without precedence or partial shadowing.

### Scenario 9: Refresh installed metadata
- **Covers**: 4b
- **Given**: upstream adds a bundle and removes a selected one.
- **When**: the update is adopted.
- **Then**: reinstall and explicit deselection expose the addition without silent selection edits.

### Scenario 10: Skip inapplicable direct removal
- **Covers**: 4c
- **Given**: the original provider is not a direct consumer requirement.
- **When**: continuation actions are reviewed.
- **Then**: direct removal is skipped; any transitive origin requirement is resolved separately.

### Scenario 11: Preserve an override
- **Covers**: 5a
- **Given**: an override and changed upstream content.
- **When**: refresh is followed by ordinary sync.
- **Then**: the adaptation survives and upstream drift stays visible.

### Scenario 12: Bootstrap a fresh consumer
- **Covers**: main success scenario
- **Given**: a fresh clone and no private-origin access.
- **When**: runtime/build prerequisites are supplied and normal installation/sync run.
- **Then**: selected bundles deploy and a separately harness-equipped consumer executes the copied relative-helper rule.

### Scenario 13: Keep source identity truthful and path independent
- **Covers**: 2b
- **Given**: equivalent unlinked path spellings or source HEAD advancing during inspection.
- **When**: provenance is prepared.
- **Then**: spelling alone leaves identity unchanged; a recorded commit contains every copied input, otherwise it is unknown.
