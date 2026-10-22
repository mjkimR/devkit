---
id: PLAN-single-release-version
spec: SPEC-single-release-version
---

# Technical Plan: `SPEC-single-release-version`

## 1. Constitution & Invariant Review

`ARCH-07-deployment` changes from six shared versions to all workspace distributions.
Record `ADR-single-release-version` for the durable version policy. Public library APIs are unchanged.
Base main is a1bed56189f11cdd7e00a0335d17ff2c2b49f624; this direct intake has no prerequisite edges.

## 2. Architecture Overview & Impact

Root VERSION is the human-edited source. Static pyproject metadata and uv.lock remain committed build inputs.
A standard-library Python script discovers members from the root workspace patterns, updates project versions
and versioned internal requirements while retaining formatting, then calls uv lock.
Existing unversioned dependency entries retain their spelling; existing internal ranges become exact pins.
The release script checks synchronization and the tag before touching its output directory.
No build backend plugin or runtime dependency is added. Python 3.12 is already required by this repository.

## 3. Component & Interface Design

`just version-sync` calls `python3 scripts/version.py`; `just version-check` passes `--check`.
Success emits one VERSION sentinel. Staleness exits 1; invalid input or lock failure exits 2 with an error advisory.
A failed lock leaves synchronized metadata for inspection; fix the lock failure and rerun synchronization.
Checking is read-only and checks metadata only; uv lock --check verifies the lock separately.

## 6. Verification & Test Plan

Extend package integration checks for workspace-wide versions, input validation, idempotence, pin updates,
read-only checks and lock failure propagation. Run just lint-check, just check and just test-affected.
Build the release locally and inspect every workspace wheel version and internal dependency requirement.
