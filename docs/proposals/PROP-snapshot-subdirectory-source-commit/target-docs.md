---
id: PROP-snapshot-subdirectory-source-commit-target
title: Snapshot source commit contract impact
status: draft
proposal: PROP-snapshot-subdirectory-source-commit
created_at: 2026-11-13
targets: []
---

# [Blueprint] PROP-snapshot-subdirectory-source-commit: Contract impact

No canonical document change is planned. `CAP-DIST-in-repo-bundles` section 8 rules 4–7 and 10 already cover the
verified commit, deterministic preview, reviewed adoption and unchanged metadata/content. The implementation restores
repository-relative lookup under a subdirectory provider; it changes no schema, CLI result or user action.

The intended production diff is confined to `source_commit()` in
`packages/devkit-dist/src/devkit_dist/features/distribution/repositories/snapshots.py` and regression coverage in
`packages/devkit-dist/tests/integration/features/distribution/test_snapshots.py`. Development reconciliation will
confirm this no-contract-change conclusion against its actual diff.
