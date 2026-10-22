---
id: ADR-single-release-version
title: Synchronize workspace releases from one version file
summary: "For a workspace released from one tag, we synchronize static package metadata from root VERSION, to make version updates one edit, accepting generated changes across package metadata and the lock."
status: accepted
created_at: 2026-10-22
---

# [ADR-single-release-version] Synchronize workspace releases from one version file

## 1. Context & Problem Statement

One GitHub release publishes every workspace wheel. Independent versions and repeated internal pins make release
preparation require edits across package metadata. Installed library contracts still require their semantic versions.

## 2. Decision Drivers

- One human-edited version value for every workspace distribution.
- Preserve standalone wheel and source distribution builds and exact internal dependency pins.
- Keep the existing Hatchling backend and avoid additional build dependencies.

## 3. Considered Options

- Keep independent static versions: no tooling change, but repeated manual edits and mixed release versions.
- Derive metadata dynamically from a root file or Git tags: fewer generated files, but shared-file availability
  and internal dependency metadata need build integration for standalone package builds.
- Synchronize static metadata from VERSION: one source and ordinary package builds, with generated tracked changes.

## 4. Decision Outcome

Use root VERSION and `just version-sync` for every workspace package, including repository tools. Synchronize
project and bundle manifest versions and versioned internal requirements, then regenerate uv.lock with uv. Keep unversioned extra
pass-throughs unchanged. Check consistency before release building. The separately built model and frontend npm
library keep their own versions. `ARCH-07-deployment` defines the deployment boundary.

Synchronization also runs `uv run --no-active devkit sync` after locking to refresh deployed bundles and
`.devkit/installation.json`. Commit the refreshed receipt with the release metadata. A sync failure stops release
preparation without a success sentinel; resolve its advisory and rerun `just version-sync`.

## 5. Consequences

Maintainers edit one version value and run one command. Package metadata and the lock still change and must be
committed together. Failed locking leaves updated metadata for inspection and retry. A public breaking change to
devkit-advisory or devkit-cli still requires a minor bump across the workspace under the compatibility contract.

## 6. Confirmation

`packages/devkit/tests/integration/package/test_version_script.py` checks synchronization, invalid input,
staleness, lock failure and release tag refusal. `test_lockstep.py` checks every workspace version against VERSION.
`scripts/release.sh` requires consistent metadata, a matching tag and a current lock before building.
