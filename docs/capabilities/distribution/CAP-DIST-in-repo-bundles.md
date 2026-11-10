---
id: CAP-DIST-in-repo-bundles
title: "In-Repository Bundles"
summary: "Local content packages and complete shared-provider source snapshots use ordinary discovery, explicit refresh and project overrides, with independent runtime installation."
area: distribution
status: active
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/distribution/cli/bundles.py
  - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/snapshots.py
created_at: 2026-10-17
usecases:
  - UC-snapshot-bundle-sources
---

# [CAP-DIST-in-repo-bundles] In-Repository Bundles

A repository's own assets (a rule encoding a project convention, a skill driving its release script, an on-call
playbook) must be versioned with it, never published, and still get everything devkit does for distributed assets:
planning, hash-tracked projection, receipt recording, rule discovery and Git snapshot gates. The consumer-facing
version of this document is the `in-repo-bundle` instruction of the [`devkit` guide bundle](../../development/reference/distribution.md#4-bundles-shipped-with-devkit);
the two MUST be kept in step. The bundle setup is mirrored by the `devkit` bundle's `in-repo-bundle` instruction
(shipped by `devkit-dist`); rule discovery, rule tests and Git snapshot gates by the `harness` bundle's `harness-assets`
instruction (shipped by `devkit-agt`, which runs the rules).
Rules that bind an agent, a host or a playbook step are checked by review only unless they name a check.

## 1. Decision

**A repository ships its own assets as an ordinary content package inside the repository, installed as a
development dependency of that same repository.** There is no local asset directory under `.devkit/` and no second
loader: `importlib.metadata.entry_points(group="devkit.bundles")` does not distinguish a registry wheel, a Git or
`path` dependency, or a workspace member.

A `.devkit/local/` directory was rejected. It would need a second discovery and planning path, its own receipt and
ownership rules, a second rule source for `devkit rules`, explicit support per asset kind, and it would blur the line
with `.devkit/overrides/` (overrides change upstream files; bundles add assets). The in-repository bundle costs only a
`pyproject.toml`, an entry point and a `bundle.toml`, paid once.

## 2. Layout

By convention the package SHOULD live under `tools/` and be named after the repository:

```text
my-repo/
  pyproject.toml
  .devkit/config.toml                 # selects the in-repo bundle like any other
  tools/my-repo-devkit/
    pyproject.toml
    src/my_repo_devkit/
      __init__.py                     # empty; no runtime side effects
      bundle/
        bundle.toml
        rules/no_todo/rule.py         # one plugin package per rule: rule.py, guide.md, tests/
        skills/release/SKILL.md
        playbooks/on-call.md
```

```toml
# tools/my-repo-devkit/pyproject.toml
[project]
name = "my-repo-devkit"
version = "0.1.0"
description = "Agent assets owned by my-repo"
requires-python = ">=3.12"
dependencies = []

[project.entry-points."devkit.bundles"]
my-repo = "my_repo_devkit"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/my_repo_devkit"]
```

```toml
# tools/my-repo-devkit/src/my_repo_devkit/bundle/bundle.toml
schema = 1
name = "my-repo"
version = "0.1.0"
default_preset = "all"

[[assets]]
id = "no-todo"
kind = "rule"
source = "rules/no_todo"

[[assets]]
id = "release"
kind = "skill"
source = "skills/release"

[[assets]]
id = "on-call"
kind = "playbook"
source = "playbooks/on-call.md"
```

The entry point name (`my-repo`) is the bundle name
(`CAP-DIST-content-packages`).
The manifest MUST follow the `CAP-DIST-manifest-spec` without exception; `devkit bundle validate` and
`devkit bundle plan` work on `tools/my-repo-devkit/src/my_repo_devkit/bundle` before it is installed.

## 3. Installation

In a **uv workspace**, add the package to the members and to the dev group next to the devkit requirement the
project already declares: `devkit-agt` when the project uses the harness (and always when the bundle ships rules,
gates or workflows, which only `devkit-agt` runs), otherwise `devkit-dist`. `devkit-agt` depends on `devkit-dist` at
the selected actual version, so a project SHOULD NOT declare both (`ADR-package-ownership-and-release-version`):

```toml
# pyproject.toml (repository root)
[tool.uv.workspace]
members = ["packages/*", "tools/*"]

[dependency-groups]
dev = ["devkit-agt", "my-repo-devkit"]

[tool.uv.sources]
devkit-agt = { git = "https://github.com/mjkimR/devkit.git", subdirectory = "packages/devkit" }
my-repo-devkit = { workspace = true }
```

In a **single project**, `uv add --dev --editable ./tools/my-repo-devkit` writes the same dev dependency with
`my-repo-devkit = { path = "tools/my-repo-devkit", editable = true }` as its source. A repository **without Python
code** already has a `pyproject.toml` for `devkit`; its root project needs no build system, only `[project]` with a
name, `[dependency-groups]` and `[tool.uv.sources]`.

Then:

```bash
uv sync
uv run devkit add my-repo        # records [presets] my-repo = "all" and synchronizes
```

The package MUST be declared in `[dependency-groups].dev`, never in `[project.dependencies]`: dependency groups are
not written to a built wheel, so if the repository is itself published, its consumers never receive the bundle, its
rules or its entry point (`CAP-DIST-content-packages`). To share the bundle later, publish the package or let
other repositories depend on it with a Git URL and `subdirectory`.

## 4. Editing Lifecycle

1. Edit the sources under `tools/my-repo-devkit/src/.../bundle/`.
2. Run `uv run devkit sync`. The editable install exposes the change at once and `sync` compares hashes against the
   receipt on every run, so the package version need not change.
3. Commit the source change with the updated `.devkit/installation.json`.

A project MUST NOT edit `.devkit/managed/<bundle>/`: a modified managed file stops the sync as for any bundle.
Overrides are for bundles the repository does not own. WHEN another repository consumes the bundle, the project
SHOULD bump the bundle `version`, so their receipts record which version they run.

## 5. Rules and Snapshot Gates

The bundle's rules deploy to `.devkit/managed/my-repo/rules/`, are listed under their asset's `paths`, load in
`devkit rules check` without flags and are configured in `[rules]` like any rule. They need `devkit-agt`: in an
installation with `devkit-dist` alone they are deployed with a `HARNESS_ENGINE_MISSING` warning
(`CAP-DIST-sync-and-transactions`).

Snapshot gates (`devkit rules check --staged`, `--ci`) evaluate a Git tree whose receipt pins the Git-ignored managed
copies: a materialized tree lacks them, and the gate reads such a file from the working tree only when its SHA-256
matches the `files` entry of the receipt committed to the snapshot; a staged snapshot evaluated in place checks the
same hash
(`CAP-GOV-evaluation-lifecycle`). Hence:

- After editing a rule, the developer MUST run `devkit sync` and stage the receipt with the rule source; a stale
  receipt fails the gate, whose `[FIX]` says to run `devkit sync`.
- A fresh clone MUST run `uv sync` and `uv run devkit sync --locked` before the gate can run; otherwise it reports
  the managed rule as missing, as for upstream bundles. CI SHOULD run the same: it fails (`RECEIPT_STALE`) when a
  bundle source was committed without the receipt it produces.
- The committed receipt pins exactly which rule code a gate executed.

`devkit rules` loads built-in rules, then rule assets in receipt order (bundle name order), then `--rules-dir`; a
rule with an earlier rule's ID replaces it. An in-repository bundle can shadow an upstream rule that way, but the
order between bundles is not a declared priority, so rule IDs SHOULD be prefixed with the repository name
(`RULE-myrepo-no-todo`) unless shadowing is the intent.

## 6. Project-Specific Mechanisms

| Need | Mechanism |
| --- | --- |
| Change a setting, phase or severity of a distributed rule | `[rules]` in `.devkit/config.toml` |
| Replace the content of one upstream asset file | `devkit override create` (`.devkit/overrides/<bundle>/...`) |
| Add rules, skills, playbooks, subagents, workflows or gates that belong to this repository | In-repository bundle |
| Try an unfinished rule without recording it | `devkit rules check --rules-dir <dir>`; with `--staged`/`--ci` a directory inside the repository is read from the snapshot, one outside it or untracked is refused, and the commit gate's staged-rules gate never takes it |

## 7. Open Items

- **Scaffolding**: a `bundle init <path>` subcommand writing the `pyproject.toml`, `__init__.py` and a minimal
  `bundle.toml`. Not implemented.
- **Explicit rule precedence**: a declared load order replacing bundle name ordering, if shadowing upstream rules
  becomes common. Not planned until a concrete need appears.

## 8. Bundle Source Snapshots

`ADR-bundle-source-snapshots` owns complete-provider packaging, credential-free provenance and explicit
refresh. A bundle source snapshot is generated source in an ordinary local package, conventionally under tools/.
It copies upstream resources; managed/projection output is not a source, and no second loader is introduced.

1. **Snapshot source**: WHEN creating a snapshot, distribution MUST inspect a local static content-only checkout
   with ordinary Hatch src resource mappings, inert initializers, empty project runtime dependencies and only
   devkit.bundles entry points without executing provider code or builds.
2. **Snapshot packaging**: WHEN creation succeeds, distribution MUST preserve every provider bundle, original
   bundle versions, bytes/executable modes, variants, templates, constitutions, relative helpers and named license
   files in an ordinary distinct wrapper whose editable package version is 0.0.0.
3. **Supported inputs**: IF source layout, imports or declarative runtime references exceed the documented subset,
   THEN distribution MUST refuse `BUNDLE_SNAPSHOT_UNSUPPORTED` before destination writes.
   The distribution reference names public API prefixes and consumer test-environment limits; arbitrary Python
   behavior and runtime-dependency closure are not certified.
4. **Snapshot provenance**: WHEN creating provenance, distribution MUST record schema, wrapper/source identities,
   original bundle versions, optional verified commit and canonical path/hash/normalized-mode entries without
   source paths, remote URLs, credentials or timestamps.
5. **Verified identity**: WHEN a commit is recorded, distribution MUST compare every copied input to that one
   captured immutable commit; equivalent unlinked source path spellings MUST produce identical provenance.
6. **Snapshot preview**: WHERE refresh has --check, distribution MUST report deterministic additions, modifications,
   removals, current/candidate digests and subsequent actions without writing files.
7. **Reviewed adoption**: WHEN applying refresh, distribution MUST match both --expect and --candidate against the
   current snapshot and prepared source before replacing it.
8. **Authored drift**: IF authored changes or a changed captured previous tree are detected, THEN refresh MUST
   preserve/restore that actual tree and refuse `BUNDLE_SNAPSHOT_CONFLICT` without overwriting edits.
9. **Replacement recovery**: IF staged or installed validation/write fails and restoration is possible, THEN
   distribution MUST restore the prior package and report `BUNDLE_SNAPSHOT_WRITE_FAILED`; failed restoration MUST
   preserve and identify its recovery backup.
10. **Idempotence**: WHEN metadata/content is unchanged, refresh MUST write nothing; derived __pycache__ and pyc files
    and Finder .DS_Store files MUST NOT count as authored drift. Other unexpected local files remain drift.
11. **Destination**: IF a destination is existing at creation, symlinked, outside the consumer, overlaps the source
    or protected state, or lies inside another snapshot, THEN distribution MUST refuse without content replacement.
12. **Explicit continuation**: WHEN an operation finishes, distribution MUST return applicable conditional provider
    replacement, install, metadata reinstall and removed-selected-bundle actions without executing them.

Tests: packages/devkit-dist/tests/integration/features/distribution/test_snapshots.py covers support, identity,
diffs, drift and recovery. packages/devkit-dist/tests/e2e/cli/test_snapshots.py proves wrapper/runtime wheels,
fresh-clone bootstrap without the private origin, editable metadata changes and harness-equipped rule execution.
The dist-only suite retains installation without devkit-agt.

### Interface and state

    uv run devkit bundle snapshot SOURCE --to DEST --package NAME [-w ROOT]
    uv run devkit bundle refresh DEST --source SOURCE --check [-w ROOT]
    uv run devkit bundle refresh DEST --source SOURCE --expect CURRENT --candidate REVIEWED [-w ROOT]

The commands print exactly one JSON object. Exit 0 statuses/codes are created/`BUNDLE_SNAPSHOT_CREATED`,
preview/`BUNDLE_SNAPSHOT_PREVIEW`, updated/`BUNDLE_SNAPSHOT_UPDATED` and unchanged/`BUNDLE_SNAPSHOT_UNCHANGED`.
Results carry destination, package, bundle versions, current_digest, candidate_digest, changes, packaging_changed,
removed_selected, actions and notices. `BUNDLE_SNAPSHOT_INVALID`, `BUNDLE_SNAPSHOT_UNSUPPORTED`,
`BUNDLE_SNAPSHOT_CONFLICT` and `BUNDLE_SNAPSHOT_WRITE_FAILED` use exit 2 with deterministic corrective directives.

Schema 1 snapshot.json contains package; source name/version/commit/requires_python/metadata_sha256; bundle
version/module pairs; ordered files with SHA256 and normalized modes (420 or 493); and aggregate digest. Payload
excludes snapshot.json; the aggregate hashes canonical metadata plus inventory without its own digest.
Unknown schemas, malformed records and mismatched aggregate hashes refuse. Generated sources use explicit
refresh; consumer adaptations use project overrides. Removal commands apply only to the dependency's owning group
and are skipped when the original provider is absent as a direct requirement.
