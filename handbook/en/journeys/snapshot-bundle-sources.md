---
sources:
  CAP-DIST-content-packages: 4f9b5893c0b732c10d59925ec4dbcc12c5146308
  CAP-DIST-in-repo-bundles: 7d71d79b481fbdf7cbc1c86d61fea924dfc924d6
  CAP-DIST-sync-and-transactions: d0837e092276ca06cecfc650bdd57053d781f79c
  CAP-DIST-workspace-ownership: 7801db0b2bf793890a591d71ed1e46ec39ba6739
  UC-snapshot-bundle-sources: c54e121b9394e47799bc2e32ed7d2dca452ecabc
title: Adopt and refresh bundle sources locally
---

# Adopt and refresh bundle sources locally

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `93e3808721b4`, generated 2026-11-13. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

A bundle source snapshot preserves a complete supported content provider in a distinct local package. It keeps original bundle versions, resource bytes, modes and license files with path-free provenance. Runtime/command providers and unsupported dynamic closure are refused before writes.

```sh
uv run devkit bundle snapshot SOURCE --to tools/local-content --package local-content
uv run devkit bundle refresh tools/local-content --source SOURCE
uv run devkit bundle refresh tools/local-content --source SOURCE --expect CURRENT --candidate REVIEWED
```

The first refresh command previews changes without writing. Review its current/candidate digests and continuation actions before passing both identities to adopt the replacement. Authored drift or stale review identities gives `BUNDLE_SNAPSHOT_CONFLICT` and preserves edits.

Replace the complete original provider dependency in its actual owning group, install the distinct editable wrapper and run ordinary sync. Skip direct removal when no direct origin requirement exists; resolve any transitive origin dependency separately. Reinstall when package metadata changes and explicitly deselect removed bundles. These actions are reported, never executed by snapshot creation or refresh.

Commit sources, provenance and deliberate bootstrap changes. Keep consumer adaptations in project overrides. A fresh clone can reproduce selected sources without private-origin access when runtime/build prerequisites are supplied.

## Sources

- [UC-snapshot-bundle-sources](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/distribution/UC-snapshot-bundle-sources.md)
- [CAP-DIST-in-repo-bundles](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md)
- [CAP-DIST-content-packages](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-content-packages.md)
- [CAP-DIST-workspace-ownership](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md)
- [CAP-DIST-sync-and-transactions](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md)
