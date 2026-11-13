---
id: PROP-snapshot-subdirectory-source-commit
title: Record the source commit for snapshots of subdirectory providers
summary: "Restore verified snapshot source commits for content providers below a Git repository root by making ls-tree resolve repository-relative paths. Preserve existing content verification and explicit refresh behavior."
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-13
target_area: capabilities/distribution/
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/distribution/
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - packages/devkit-dist/tests/
  excludes:
    - docs/decisions/
task_kind: bugfix                     # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-snapshot-subdirectory-source-commit] Record the source commit for snapshots of subdirectory providers

## 1. Background & Hypothesis

`devkit bundle snapshot` records `source.commit` in `snapshot.json` only when every copied input matches the
captured `HEAD` (`CAP-DIST-in-repo-bundles` rule 5, verified identity). `source_commit()` in
`packages/devkit-dist/src/devkit_dist/features/distribution/repositories/snapshots.py` runs every Git command with
the snapshot source directory as its working directory, but passes `ls-tree` a path relative to the repository root
(`path.relative_to(repository)`). Git resolves `ls-tree` paths against the working directory, so for a provider that
lives below the repository root no path matches, `ls-tree` prints nothing and the function returns `None`.

Observed while snapshotting a content-only provider at `tools/<package>` of a private game-foundation repository:
the committed, unchanged checkout produced `"commit": null` on every run (absolute and relative source paths alike),
while the copied bytes matched that commit exactly. The existing test
`test_optional_commit_matches_only_copied_committed_inputs` initializes the Git repository at the provider root, so
it never exercises a subdirectory provider. Provenance of every monorepo-hosted snapshot is therefore weaker than the
contract promises. Refresh retains its existing explicit preview/apply protocol; correcting the optional commit
changes provenance metadata and therefore its digest.

Hypothesis: resolving the paths from the repository root (`ls-tree --full-tree`, or running the lookups with the
repository root as working directory) records the verified commit for subdirectory providers without changing the
result for root providers or for sources that differ from `HEAD`.

## 2. Planning Decisions

- **Q1 resolved**: add `--full-tree` to the existing `ls-tree` invocation in `source_commit()`. The copied input paths
  are already relative to the repository root. The flag gives those paths the matching interpretation while retaining
  the existing working directory, one captured immutable commit, 10-second timeout, blob-byte checks and normalized
  executable-mode checks. Changing every lookup's working directory adds no benefit to this defect fix.
- **Q2 resolved**: adopt the existing metadata-change behavior. When an unchanged subdirectory provider first gains a
  verified commit, preview reports only `snapshot.json` modified, different current/candidate digests and
  `packaging_changed=false`. Preview writes nothing. Applying the reviewed digest pair records the commit and returns
  `BUNDLE_SNAPSHOT_UPDATED`; repeating the same refresh returns `BUNDLE_SNAPSHOT_UNCHANGED` without writing.
- No user design decision remains. Planning used a focused real-Git probe and the existing source/path tests; no Scout
  or Challenger is required at `low` effort. The evidence and exact baseline are in `materials/source-commit-probe.md`.
- Development stays `bugfix`, size `S`, effort `low`. No package, feature edge, schema, CLI field or lasting policy is
  added. No PADR or ADR is needed for restoring the existing verified-identity contract.

## 3. Proposed Design & Impact

### Implementation boundary

Change only `packages/devkit-dist/src/devkit_dist/features/distribution/repositories/snapshots.py` and the existing
snapshot integration tests under `packages/devkit-dist/tests/integration/features/distribution/`. The repository
helper keeps returning `None` on non-Git sources, failed/timed-out Git commands, missing/nonblob entries, changed
copied bytes or executable-mode mismatches. Unrelated untracked files remain outside copied-input verification.

### Acceptance criteria for Development

- **AC-01 — subdirectory identity**: Given a committed content provider at `tools/content` below a repository root,
  when creating a snapshot from either its absolute path or an equivalent unlinked relative spelling, then
  `source.commit` equals that repository's captured `HEAD` and equivalent source spellings yield identical provenance.
- **AC-02 — verified inputs**: Given that subdirectory provider, when a copied input has uncommitted byte changes or
  a normalized executable-mode mismatch, then a snapshot records `source.commit=null`. A provider rooted at its Git
  repository continues to record the verified commit. The captured-HEAD race regression continues to pass.
- **AC-03 — metadata-only refresh**: Given an unchanged committed subdirectory provider and a valid existing snapshot
  whose only older provenance difference is `source.commit=null`, when previewing refresh with the fix, then only
  `snapshot.json` is modified, current/candidate digests differ, `packaging_changed=false`, and the destination tree
  is unchanged. Applying that digest pair returns `BUNDLE_SNAPSHOT_UPDATED` and records `HEAD`; applying again returns
  `BUNDLE_SNAPSHOT_UNCHANGED` and preserves all destination file modification times.

Development first adds the subdirectory regression against the unfixed implementation and records its failure, then
adds the flag and verifies these criteria. Run the snapshot integration module, the independent dist check, repository
lint/type checks and `just test-affected` with its full fallback retained. No viewer frontend check applies.

### Living Spec impact

No canonical document wording changes are planned. `CAP-DIST-in-repo-bundles` section 8 rules 4–7 and 10 already
cover optional verified commits, immutable input comparison, deterministic preview/reviewed adoption and unchanged
metadata/content. The fix restores those guarantees without adding a contract. `target-docs.md` declares an empty
canonical target list and the reconciliation rationale; Development must re-evaluate it if its actual diff changes
that conclusion.

### Non-Goals

- No provenance schema, digest algorithm, result status/code or refresh protocol change.
- No change to source-path admission, symlink handling, Git environment handling or timeout policy.
- No snapshot repair outside the existing user-requested refresh operation.
- No architecture, package or feature dependency change.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr snapshot-subdirectory-source-commit "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept snapshot-subdirectory-source-commit --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff snapshot-subdirectory-source-commit.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
