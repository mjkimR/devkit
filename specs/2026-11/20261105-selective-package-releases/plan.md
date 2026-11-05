---
id: PLAN-selective-package-releases
spec: SPEC-selective-package-releases
---

# Technical Plan: `SPEC-selective-package-releases`

## 1. Constitution & Invariant Review

`ADR-selective-package-versions` replaces version equality only. Package ownership, layering, CLI version source,
workspace sources and model/npm policies remain. `ARCH-05-2-components` permits repository tooling and its existing
package integration test mirror. No new application feature or dependency edge is introduced.

## 2. Architecture Overview & Impact

Split repository release tooling into Python modules under scripts/releases; version.py and release.sh stay entry
adapters. Use packaging requirement parsing from the existing development environment; commands run through uv.
Use the existing distribution manifest loader and content enumeration for bundle fingerprints. Build isolated
package source snapshots under ignored build storage; never change the candidate worktree to compare wheels.
Pin the recipe's Python, uv and hatchling versions. No real release baseline is manufactured during Development.

## 3. Component & Interface Design

`just version-sync --baseline FILE` prepares; `just version-check --baseline FILE` recomputes read-only.
`just release-build vX.Y.Z --baseline FILE` verifies the complete committed plan and emits assets.
`uv run python scripts/version.py --bootstrap TAG --source REF --artifacts DIR --output FILE --repository OWNER/REPO`
imports original historical wheels plus SHA256SUMS, using read-only git show for source identities.
`uv run python scripts/releases/cli.py publish TAG` validates local and existing remote assets and resumes uploads.
No command grants tag or publication authorization. The workflow retains tag trigger and main ancestry.
Success is one VERSION, RELEASE or RELEASE_BOOTSTRAP sentinel; failure is a stable RELEASE_* advisory with
INPUT_ERROR action and exit 2 (read-only staleness exit 1). Build and publish verify checksums before reuse.

## 4. Storage & State Management

Schema 1 completed inventory: release, source_sha, recipe, packages keyed by normalized name, extras keyed by
name, and digest over canonical JSON excluding digest. Each package has path, version, fingerprint,
bundles, requires, artifact {filename,url,sha256}. Plan adds baseline digest/path identity, changed/reused
sets, closure reasons, generated field edits {path,field,before,after} and state incomplete/complete.
Track scripts/releases/pending.json only when explicitly preparing a real release. Baseline remains a completed
inventory input, never a pending plan. Store exact semantic field edits, not whole-file replacements; a removed
requirement stays removed. Mismatched generated values or changed baseline refuse before writes.
Persist incomplete before locking; set complete only after lock and sync succeed. Recompute final wheels against
the plan before build. Build reuses original artifacts after hashing and ships only changed wheels plus model.

## 5. Error Handling & Edge Cases

Validate schema, digest, normalized names, filename/version identities, source identity, exact pins and recipe.
Reject duplicate/unsupported wheel shapes. Canonicalize only owning dist-info path, METADATA Version,
registered bundle top-level version and RECORD; preserve everything else and executable modes.
Repreparation logically unwinds still-matching edits in copied metadata before comparisons; preserve unrelated
changes and removed requirements. A changed baseline or mismatched generated field refuses. An incomplete plan
can be repaired by rerunning preparation. Retry publication hashes remote bytes; upload only missing assets,
with inventory last. Never overwrite. Newly added packages enter closure; removed packages leave the inventory.

## 6. Verification & Test Plan

Integration tests in the existing package test mirror cover canonicalization, closure, bundle exclusions,
repreparation, bootstrap source/checksum validation, corruption, incomplete lock/sync and partial uploads.
Local original-wheel fixtures measure old lockstep count versus selective count in one process. Clean consumer
fixtures install wheels and Git sources outside the workspace, including optional extras and tool installs.
Run lint/types/rules and just test-affected --base 0e17cd72d96d5111e39731291241472d7cd3f87b with its full fallback.
Independent HIGH code and reconcile reviews follow the review loop. Real historical availability and publication
remain first-use checks, not experimentally validated claims.
