---
name: content-snapshot
description: Read before copying a shared private content provider into this repository with `devkit bundle snapshot`, or refreshing such a copy from its source.
---

# Snapshot a shared private content provider

1. Obtain an authorized local content-package checkout.
2. Copy its complete supported provider with a distinct local package name:

       uv run devkit bundle snapshot /checkout/team-assets --to tools/team-assets-copy --package team-assets-copy

3. Follow returned conditional removal/install actions: skip direct removal when absent, use --dev only for a
   direct dev-group declaration, remove other direct requirements from their owning group, and resolve transitive origin requirements.
4. Run normal selection and sync, then commit the local package, provenance and deliberate dependency changes.

The source must use static metadata, ordinary Hatch src resources and inert initializers with no project runtime
dependencies or other entry-point groups. Self-contained bundle rules/gates/helpers may import standard-library
or documented devkit APIs and copied relative helpers. Unsupported imports, dynamic execution/import syntax and
external declarative handlers refuse before writes. Keep required devkit/harness/build tools separately installed.
The wrapper preserves every bundle of the provider because duplicate bundle names remain a discovery error.

Keep consumer adaptations in project overrides. Do not edit generated snapshot sources. The local wrapper version
stays 0.0.0; source package/bundle versions, content digests and the adoption commit identify the snapshot.

When upstream sources change, preview (no digests) and inspect the returned file changes, then apply with both
returned digests:

    uv run devkit bundle refresh tools/team-assets-copy --source /checkout/team-assets
    uv run devkit bundle refresh tools/team-assets-copy --source /checkout/team-assets --expect <current-digest> --candidate <reviewed-candidate-digest>

Apply requires both preview digests and refuses authored local changes. Unchanged sources write nothing.
Follow returned reinstall commands when packaging metadata changes and explicitly deselect removed bundles before
normal sync. Refresh changes only the snapshot directory; installation, config, overrides, receipt and Git remain
separate steps. Done when normal sync succeeds and a fresh consumer can install the local provider without fetching
its private origin, given the required runtime/build dependencies.
