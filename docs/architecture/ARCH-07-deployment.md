---
id: ARCH-07-deployment
title: Deployment View
summary: "Deployment topology: wheel builds, GitHub Releases, Git dependency sources, the test-selection graph constraints, and projected directory structures."
status: active
created_at: 2026-10-17
---

# [ARCH-07-deployment] Deployment View

- **arc42**: §7 Deployment View
- Containers: `ARCH-05-1-containers`. Context: `ARCH-03-context`.

---

## 1. Distribution Architecture

devkit packages are not hosted on PyPI. A Git tag (`vX.Y.Z`) triggers a GitHub Release with changed workspace
wheels, `SHA256SUMS`, installation commands and `release-inventory.json`. The completed inventory contains every
workspace package's actual version, original wheel URL and SHA256, plus the separately versioned model artifact.
Unchanged wheels remain at their original release location. The model and viewer npm library retain their
independent policies (`ADR-selective-package-versions`).

### 1.1 Consumer Dependency Declaration

In consumer projects managed with `uv`, devkit is declared either via release wheel URLs or directly via Git references in `pyproject.toml`:

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
# Or distribution only (no harness commands or guidance), never next to devkit-agt:
uv add --dev "devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist"
# Optional SDD extension; uv brings devkit-docs and its base dependencies from the same monorepo:
uv add --dev "devkit-spec @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-spec"
# Optional local viewer; its page is committed, so installing from Git needs no Node:
uv add --dev "devkit-viewer @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-viewer"
```

`uv.lock` pins the resolved commits. A Git requirement on `devkit-agt` brings `devkit-dist`, `devkit-core`, `devkit-cli` and
`devkit-advisory` from the same commit (their workspace sources), and the `search` extra brings the model wheel from the release
`packages/devkit-dist/pyproject.toml` pins. Root `VERSION` selects one human-authored `X.Y.Z` release version, strictly newer than the selected completed
baseline. Only distributions whose canonical shipped payload changes and the fixed point of their exact-pin
reverse dependencies MUST take it. Unchanged packages MUST retain their published versions. A bundle MUST advance
only when its own enumerated content changes. Repository tests and root documents alone do not advance wheels.
`devkit --version` reports installed `devkit-dist`, which can differ from the latest release version.

Versions follow semver: within `0.x`, a breaking schema, command or API change bumps the minor release number;
other changes bump the patch number. Internal runtime and optional requirements MUST pin each dependency's actual
selected version, including inactive markers and extras. Unversioned extra pass-throughs retain their spelling.
Development-only requirements do not propagate release membership. The supported combination is one complete
inventory; arbitrary cross-inventory mixtures gain no compatibility promise.

`just version-sync --baseline FILE` builds comparison wheels under a pinned Python/uv/hatchling recipe and writes
`scripts/releases/pending.json`. Comparisons MAY build all wheels; no speed reduction is promised. Canonicalization
MUST ignore only owning dist-info identity, its METADATA Version, registered bundle top-level versions, RECORD
and ZIP container ordering, timestamps and compression. Requirements, entry points, other metadata, code literals,
resources and executable modes remain significant. Bundle fingerprints use manifest source enumeration and its
`.DS_Store`, `__pycache__` and `*.pyc` exclusions. Unsupported wheel shapes MUST fail.

A pending plan records the verified completed baseline and digest, selected versions, canonical fingerprints,
closure reasons, original artifact provenance and exact generated field edits. Repreparation MUST logically unwind
only recorded changes whose generated after-value still matches, before comparing with the same completed
baseline. It preserves removed requirements and unrelated authored edits; ambiguous generated fields or a changed
baseline MUST fail before writes. A prepare/revert-source/prepare cycle MUST remove unnecessary generated advances.
Before generated writes, preparation MUST recheck captured metadata bytes and refuse with
`RELEASE_PREPARATION_CONFLICT` if an authored edit arrived during comparison. It preserves that edit and asks for
repreparation after editing finishes. No global lock or unrelated source-file snapshot is promised.

Existing package versions after logical unwind MUST match the supplied baseline; an older archive cannot silently
downgrade a current package. For the next release, a retained prior plan is superseded only when the supplied
completed inventory proves its origin, selected identities and exact committed plan at its source SHA. Published
generated edits become baseline inputs and MUST NOT be unwound. An unpublished mismatched plan still refuses.

The plan remains incomplete until `uv lock` and normal sync succeed. Failed preparation emits no success sentinel.

`just version-check --baseline FILE` recomputes the plan read-only. `just release-build vX.Y.Z --baseline FILE`
requires a complete plan committed in the tag, matching final payloads, a clean tagged HEAD, and `uv lock --check`.
Changed wheels use the new tag URL; reused wheels MUST retain original filenames, URLs and digests and MUST NOT be
rebuilt for publication. Missing or corrupt original artifacts MUST fail. The release workflow retains tag
verification and main ancestry. Publication retries verify every existing asset before uploading missing assets;
a mismatched existing asset MUST refuse. The completed inventory is uploaded last. Checks are exercised by
`packages/devkit/tests/integration/package/test_selective_releases.py` and release CI.

The first selective preparation requires explicit bootstrap of one historical lockstep release:

```bash
uv run python scripts/version.py --bootstrap v0.1.6 --source v0.1.6 \
  --artifacts dist/original-v0.1.6 --output scripts/releases/baseline-v0.1.6.json --repository mjkimR/devkit
just version-sync --baseline scripts/releases/baseline-v0.1.6.json
```

The artifacts directory MUST contain original published wheels and SHA256SUMS. Bootstrap verifies filename/version,
checksum, source tag and package/bundle identities and derives fingerprints from those original bytes. It MUST NOT
infer a published baseline from current metadata or rebuild historical bytes. Historical asset availability is a
first-use prerequisite; Development fixtures do not prove it. The tracked pending plan embeds the verified baseline
so the tag workflow can use the first bootstrap without requiring a historical inventory asset.

Release notes generate the complete URL closure for harness, dist-only, search, MCP, SDD, viewer, tool, advisory-only
and CLI-only variants. Consumers MUST use each selected artifact's original URL; constructing every wheel URL from
the newest tag is invalid. Git installs continue to resolve all workspace packages from one monorepo commit with
consistent actual-version pins. A tool installation names the executable owner and adds its required closure:
`uv tool install <devkit-dist requirement> --with <devkit-agt requirement>` (`ARCH-05-3-command-plugins`). The viewer's
Svelte library remains a pinned-commit npm tarball (`CAP-VIEW-repository-viewer`).

Python runtime YAML reads require PyYAML's `yaml.CSafeLoader`; package dependency metadata does not guarantee that optional binding. For uv-managed environments, install PyYAML without building it from source with `uv add --no-build-package pyyaml ...` or `uv tool install --no-build-package pyyaml ...`. A compatible binary wheel needs no system LibYAML development headers. Installation guidance then checks the active interpreter with `uv run python -c "import yaml; assert hasattr(yaml, 'CSafeLoader')"`; runtime availability is authoritative, and a missing binding raises `YAML_BINDING_UNAVAILABLE` with exit `2` at the first YAML read. This check does not guarantee support for every operating system or Python build.

Synchronization also runs `uv run --no-active devkit sync` after locking to refresh deployed bundles and
`.devkit/installation.json`. Commit the refreshed receipt with the release metadata. A sync failure stops release
preparation without a success sentinel; resolve its advisory and rerun `just version-sync`.

### 1.2 Optional Handbook Refresh

When the user requests it, release preparation refreshes the handbook (`CAP-DLV-release-handbook`) after `VERSION`
names the upcoming release and before the `just version-sync` metadata commit: the `devkit-dev/handbook` playbook
regenerates and verifies `handbook/` and commits it, writing `v<VERSION>` as the manifest tag. There is no cadence; a
release without a refresh keeps the previous handbook (`ADR-release-handbook`).

`scripts/release.sh` runs the handbook check after the tag, metadata and lock checks and before any wheel build. A
release is refreshing exactly when `handbook/manifest.json` names the tag being built: its build fails on a
verification finding or when `docs/` at the tagged commit differs from `docs/` at the manifest source commit. Every
other release runs no handbook command that writes files; the release wrapper keeps the child result off stdout.

### 1.3 Test Selection Graph

Local verification selects tests with `just test-affected` (`scripts/affected_tests.py`); nightly, manual and release
CI run the complete suite (`ADR-test-selection-and-ci`). The selector keeps these constraints:

- The selector MUST resolve helpers, applicable conftests, relative imports, initializers and re-exports
  conservatively: a static uncertainty widens to a broad owner dependency, and an unsafe or unknown change mapping or
  a parse failure selects the full suite.
- The selector MUST keep the explicit data, structural and frontend checks and every full-suite trigger
  (`scripts/affected_tests.py` `FULL_PREFIXES`, `FULL_FILES`, `FULL_NAMES`, `FRONTEND_CHECK`).
- The selector MUST NOT add an implicit package edge to every fine-grained `devkit_spec` test; opaque consumers
  (root, wildcard, CLI, bundle and source-tree consumers) MUST keep an explicit broad dependency.
- Source code MUST NOT use a deferred import to hide a real dependency from the selector.
- A change that reduces selection SHOULD be validated with same-revision before/after collection matrices and
  independent positive and negative dependency fixtures; a measured reduction never justifies omitting required
  coverage.

Checked by `packages/devkit/tests/e2e/package/test_affected_tests.py`; the deferred-import and reduction rules are
review only.

---

## 2. Consumer Workspace Layout

When installed and synchronized, devkit establishes the following layout inside a consumer repository:

```text
<consumer-workspace-root>/
├── .devkit/
│   ├── config.toml            # Project-owned configuration (presets, policies, overrides)
│   ├── installation.json      # Machine-generated installation receipt
│   ├── managed/               # Pristine read-only bundle asset copies
│   │   ├── devkit/
│   │   ├── advisory/
│   │   └── harness/           # with devkit-agt (auto-selected harness bundle)
│   ├── overrides/             # Local modifications to upstream bundle assets
│   └── transient/             # Atomic transaction journals
├── .agents/skills/            # Projected skills shared by Codex and Antigravity
├── .claude/skills/            # Projected skills for Claude Code
├── .codex/agents/             # Projected Codex subagent contracts
└── AGENTS.md                  # Root instructions with managed <!-- DEVKIT:START/END --> block
```

Task worktrees are sibling checkouts at `<parent of base>/<base name>-wt-<branch>`, outside `.devkit/`.
See `CAP-WT-task-worktrees` and `CAP-DIST-agent-projections` for the canonical path and projection contracts.

## Optional MCP deployment

Supported isolated installations are dist alone, dist plus runtime, agt without the SDK, agt with its `mcp` extra,
and spec plus runtime. Runtime-only discovery may return no services. No wheel duplicates another installed path.
`devkit mcp` uses a retained base or explicitly selected tool runtime with matching service packages and verified
import locations; linked-worktree interpreters and editable sources are refused. Registration and its absolute
paths remain ignored machine-local state. Removing a task checkout cannot remove its server runtime. Owning
configuration loss blocks new approval/resume; only the same approved call's exact terminal cleanup may finish.

The devkit-docs wheel registers `docs = "devkit_docs.bundles.docs"` in `devkit.bundles`. Its default core is
auto-selected by every installation carrying devkit-docs, including adaptive and SDD installations. Built-wheel isolation without devkit-spec is
verified by `packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py`.

The devkit-adaptive wheel registers `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"`; it deploys only after explicit
selection of `adaptive-dev:core`, `adaptive-dev:agents` or `adaptive-dev:import`. A clean adaptive-dev installation uses
devkit-adaptive alone without devkit-spec; it requires devkit-docs at an exact pin like every internal requirement. The adaptive distribution owns the entry, pointer, role contracts, managed
current-context template, the explicitly invoked import entry and the conversion playbook
(`CAP-DLV-adaptive-development`). The coordinator's
`.devkit/adaptive-dev.md` remains project-owned and is never a seeded or overwritten deployment output. Built-wheel
isolation, common policy inspection and context preservation are exercised by
`packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py`.

The devkit-catalog wheel registers `deep-research = "devkit_catalog.deep_research"`; it deploys only after explicit
`deep-research:core` selection and needs no devkit-spec under either approach. The catalog owns its entry, references
and four role contracts; retained materials under `docs/materials/` are project-owned and never a deployment output.
Built-wheel isolation under the default `sdd` approach, the transient workspace example and material preservation are
exercised by `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py`.
