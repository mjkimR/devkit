---
id: PROP-snapshot-subdirectory-source-commit
title: Record the source commit for snapshots of subdirectory providers
summary: devkit bundle snapshot records a null source commit whenever the content provider lives in a subdirectory of its Git repository, because ls-tree runs from that subdirectory with repository-root paths. Resolve paths from the repository root so verified commits are recorded.
status: reviewing                     # draft | reviewing | accepted | rejected
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
contract promises; refresh is unaffected.

Hypothesis: resolving the paths from the repository root (`ls-tree --full-tree`, or running the lookups with the
repository root as working directory) records the verified commit for subdirectory providers without changing the
result for root providers or for sources that differ from `HEAD`.

## 2. Technical Spike Questions

- **Q1**: `--full-tree` versus running the Git lookups from the repository root: which keeps `run_git`'s symlink and
  timeout handling unchanged?
- **Q2**: Do refresh previews and digests stay identical when an existing snapshot's recorded commit changes from
  `null` to a commit on the next refresh, or does that count as a provenance change to report?

## 3. Proposed Design & Impact

- Fix the `ls-tree` path resolution in `source_commit()`.
- Add a regression test with the provider in a subdirectory of its repository: a committed, unchanged source records
  `HEAD`, and an uncommitted change still records `null`.
- No capability text change is expected: the fix restores `CAP-DIST-in-repo-bundles` rule 5 as written.

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
