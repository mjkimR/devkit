---
id: PROP-selective-package-releases
title: Selective package releases under a shared release version
summary: "Keep unchanged package versions stable while assigning one shared release version to changed packages and required dependency updates."
status: reviewing
created_at: 2026-11-05
target_area: docs/capabilities/distribution/
priority: high
size: L
planning_effort: high
dev_effort: high
boundaries:
  owns:
    - scripts/
    - .github/workflows/release.yml
    - VERSION
    - pyproject.toml
    - uv.lock
    - packages/
    - tools/
    - docs/architecture/
    - docs/capabilities/distribution/
    - docs/decisions/
    - docs/development/reference/
    - guides/
    - README.md
    - justfile
    - .devkit/installation.json
  excludes:
    - models/
    - handbook/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-selective-package-releases] Selective package releases under a shared release version

## 1. Background & Hypothesis

`scripts/version.py` writes root `VERSION` into every workspace package, bundle manifest and versioned internal
requirement. `scripts/release.sh` builds every workspace wheel and generates installation commands using one release
URL. `ARCH-07-deployment` and `ADR-package-ownership-and-release-version` define this lockstep policy.

An independently consumed library such as `devkit-advisory` receives version changes even when its distributed
content is unchanged. The hypothesis is that a shared release number can preserve simple release coordination
while unchanged packages retain their last published versions.

Illustrative outcome: release `0.1.7` contains changed `devkit-dist` and `devkit-agt` at `0.1.7`, while unchanged
`devkit-advisory` remains at `0.1.6`. When advisory changes in a later release, it takes that release's number.

## 2. Technical Spike Questions

- **Q1 — Change identity:** Which shipped files, dependency metadata, generated assets and build inputs determine
  a package change? How are first releases, test-only changes and shared build changes classified without making
  generated version edits trigger every package again?
- **Q2 — Dependency propagation:** Can per-package exact pins provide an installable release set with bounded
  propagation? Compare that baseline with compatible ranges, including the externally consumed advisory contract.
- **Q3 — Artifact reuse:** Should release notes reference original wheel URLs, or should unchanged wheel bytes be
  attached again? How is their original version and checksum preserved without rebuilding a published identity?
- **Q4 — Compatibility:** How do Git/workspace installation, optional extras, bundle manifest versions and the lock
  file behave when package versions differ? Which mixed-version combinations are supported?
- **Q5 — Migration:** What release inventory and validation replace the all-packages-equal check? How are historical
  artifacts bootstrapped and a failed preparation resumed without publishing conflicting contents?

## 3. Proposed Design & Impact

Recommended starting direction, subject to Planning:

1. Keep one release number in `VERSION`. Assign it to changed packages and packages whose dependency metadata must
   change; keep all other package versions stable.
2. Compare relevant package inputs with their last released identities. Count required dependency changes as
   package changes and calculate their transitive effect before editing metadata.
3. Start with exact pins to each dependency's actual package version. Do not replace every internal pin with the
   release number. Adopt ranges only if Planning establishes their compatibility and verification contract.
4. Record each release's package versions, wheel locations and hashes in a machine-readable inventory. Reuse the
   original bytes for unchanged published wheels and generate installation instructions from that inventory.
5. Revise version synchronization, release building, metadata checks and consumer installation coverage together.
   Keep the separately versioned model and frontend library outside this policy change.

The package metadata scope covers workspace versions and dependency pins, not unrelated application behavior.
No new cross-feature dependency is proposed. Planning must prepare a successor decision for the release-version
clauses of `ADR-package-ownership-and-release-version` while preserving unrelated package ownership decisions.
`ARCH-07-deployment`, distribution references and installation guides need corresponding updates.

**Scope excluded:** package-by-package independent version selection, a new package registry, automated publishing
without release authorization, and unrelated library API changes. Handbook regeneration remains its own operation.

## 4. Lifecycle & Retirement Criteria

This is a queued draft; recommended design choices are not accepted policy. Planning and Development effort are
`high` because published package metadata and external consumers are affected. The estimated size is `L` for one
coherent release-contract change. It has no prerequisite proposal.

Planning is ready for acceptance when change detection, dependency propagation, artifact reuse, migration and
compatibility are settled, with a candidate release inventory and successor decision.

Candidate Development acceptance checks:

- **AC1:** Given a change only to one independent package's shipped content, release preparation advances that
  package to the release number and leaves unrelated packages unchanged.
- **AC2:** Given a dependency update that changes an exact pin, all required dependent metadata changes are included
  and the resulting release installs in a clean environment without the source workspace masking resolution.
- **AC3:** Given unchanged content or a repeated preparation, published package identities keep identical artifact
  hashes; documentation/test-only changes follow the explicitly chosen change-detection policy.
- **AC4:** Given the release inventory, generated wheel and Git installation paths resolve the intended package
  versions; advisory-only installation retains its independent compatibility checks.

Acceptance and handoff use the proposal lifecycle after direction approval. If selective releases do not reduce
consumer churn enough to justify the release machinery, retain lockstep releases and reject the draft with that
reason through the existing lifecycle.
