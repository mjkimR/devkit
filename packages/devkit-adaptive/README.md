# devkit-adaptive

Adaptive development guidance and the `devkit adaptive assignment` commands. Installing `devkit-adaptive` brings
`devkit-docs`, the document system and harness, without devkit-spec. Select `uv run devkit add adaptive-dev` for the
product iteration guidance; command use needs neither bundle selection nor a development approach.

## Modules

- `cli`: mounts the adaptive group through `devkit.commands`.
- `features/assignment/cli`: six command adapters and sentinel/JSON formatting.
- `features/assignment/usecases`: typed create, return, verify, close, list and show entry points; `listing` is the public read interface.
- `features/assignment/services`: lifecycle, authority and verification policy.
- `features/assignment/repositories`: Git reads, governing document resolution and shared Git ledger persistence.
- `features/assignment/models`: assignment values, event fold and literal prefix predicates.
- `base/errors`: stable adaptive advisories.
- `bundles/adaptive_dev`: opt-in guidance, reusable agents and import conversion assets.

## Usage

```sh
uv run devkit adaptive assignment new --owner builder --goal "Implement editor" --write src/editor --commit --check tests
uv run devkit adaptive assignment list
uv run devkit adaptive assignment return a1 --status completed --check tests=pass
uv run devkit adaptive assignment verify a1
uv run devkit adaptive assignment close a1 --outcome integrated
```

The delegating agent records events; an assignee does not run these commands for itself. The ledger is untracked
under the shared Git directory, and the context Markdown only names outstanding IDs. Check commands are recorded,
never executed. The distribution is not a bundle snapshot source (`BUNDLE_SNAPSHOT_UNSUPPORTED`).

See `CAP-DLV-adaptive-assignments`, `CAP-DLV-adaptive-development` and `UC-advance-an-idea` for the contracts.
