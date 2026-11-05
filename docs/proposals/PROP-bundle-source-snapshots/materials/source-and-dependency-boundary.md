# Source and dependency evidence

Inspected source at Planning base `255b54b38a89035e77527a75824ff590d4e110dc`.

| Evidence | Finding and implication |
| --- | --- |
| `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/discovery.py` (`discover_bundles`, `_load`) | Entry-point names equal bundle names; duplicate entry points fail globally before selection. Whole content-provider replacement avoids a second loader or a partial-provider conflict. |
| `packages/devkit-starter/pyproject.toml`, `src/devkit_starter/bundle/bundle.toml` | Static metadata, empty runtime dependencies, one bundle, ordinary src layout; valid first supported package. |
| `packages/devkit-catalog/pyproject.toml` | Empty runtime dependencies and eight bundle entry points. Copying one while leaving the original installed creates a duplicate; preserving all provider bundles keeps selections available. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/manifest.py` (`source_files`, `safe_source`, `Bundle.constitution`) | Existing manifest validation rejects symlinks/nonregular sources and resolves declared source trees, variants and optional constitution. Use these source identities; never copy managed output. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/templates.py` (`render_template`) | Templates use scalar inputs, with no filesystem include loader. Retaining raw template bytes and declarations preserves rendering; no expanded private context should be copied. |
| `CAP-DIST-in-repo-bundles` sections 1–4 | Ordinary local content package, no second loader; editable sources need no package version bump. |
| `CAP-DIST-content-packages` sections 1–3 | Resource initializer has no side effects; project runtime requirements propagate through packaging; dependency group tooling does not. |
| `ARCH-05-2-components` sections 1.1–1.3 | Distribution owns this use case; bundle plugin code may use public foundation/rule APIs. Bundle Python is not itself runtime-package vendoring. |

No private repository was fetched or inspected. No snapshot prototype or installed-consumer test ran in Planning.
Supported Python rules are verified in Development with an in-bundle relative-helper fixture, a standard-library
import, documented devkit API imports and an intentionally missing external import. Arbitrary import semantics
cannot be proved statically; the command supports a documented inspectable subset and refuses dynamic imports.

Options: manual copy (small but no refresh safety), ordinary wrapper (chosen), second loader (duplicates ownership),
partial bundle extraction/provider precedence (changes discovery), arbitrary wheel/runtime copy (breaks bounded
private-content promise). Provider replacement is deliberately separate from source copying and normal sync.

## Challenger disposition

`envelopes/challenger-01.yaml` identified four P2 gaps. The proposal now defines the exact derived-bytecode
exclusion, editable metadata reinstall/removal steps, declarative runtime-reference preflight and a nonrecursive
payload/provenance digest. Each fix implements the suggested action; no supported asset class or chosen packaging
direction changed. Required Development fixtures now cover each failure condition.
