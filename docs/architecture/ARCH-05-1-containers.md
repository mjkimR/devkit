---
id: ARCH-05-1-containers
title: Building Block View - Containers
summary: "Container topology of devkit: workspace packages, the devkit-dist, devkit-agt, devkit-docs, devkit-spec, devkit-advisory, devkit-cli and devkit-mcp wheels released in lockstep, and external content packages."
status: active
created_at: 2026-10-17
---

# [ARCH-05-1-containers] Building Block View: Containers

- **arc42**: §5 Building Block View - Level 1 (Containers)
- System context: `ARCH-03-context`. Components: `ARCH-05-2-components`.

---

## 1. Container Topology

devkit is structured as a Python monorepo using `uv` workspaces:

```mermaid
graph TD
    subgraph DevkitWorkspace ["devkit Monorepo (uv workspace)"]
        PkgCore["packages/devkit-core<br>(devkit_core, shared foundation)"]
        PkgCli["packages/devkit-cli<br>(devkit-cli wheel, agent-first CLI boundary)"]
        PkgDist["packages/devkit-dist<br>(devkit-dist wheel, devkit executable)"]
        PkgMcp["packages/devkit-mcp<br>(optional devkit-mcp wheel)"]
        PkgDevkit["packages/devkit<br>(devkit-agt wheel)"]
        PkgDocs["packages/devkit-docs<br>(devkit-docs wheel, document system)"]
        PkgSpec["packages/devkit-spec<br>(devkit-spec wheel)"]
        PkgAdv["packages/devkit-advisory<br>(devkit-advisory wheel)"]
        PkgCat["packages/devkit-catalog<br>(devkit-catalog wheel)"]
        PkgStart["packages/devkit-starter<br>(devkit-starter wheel)"]
        PkgViewer["packages/devkit-viewer<br>(devkit-viewer wheel, Svelte library tarball)"]
        ModelEmbed["models/devkit-embed<br>(devkit-embed wheel, manual release)"]
    end

    subgraph ConsumerApp ["Consumer Repository (e.g. app-common, autohub)"]
        Runtime["Runtime Application Code"]
        DevTools["Development Environment / Agents"]
    end

    PkgAdv -.->|Runtime dependency (std-lib only)| Runtime
    PkgCore -->|Same-version dependency| PkgAdv
    PkgCli -->|Same-version dependency| PkgAdv
    PkgCli -.->|Runtime dependency of click tools| Runtime
    PkgDist -->|Same-version dependency| PkgCli
    PkgDist -->|Same-version dependency| PkgCore
    PkgDist -->|Same-version dependency| PkgAdv
    PkgMcp -->|Same-version dependency| PkgDist
    PkgMcp -.->|MCP transport| DevTools
    PkgDevkit -.->|Optional mcp extra| PkgMcp
    PkgDevkit -->|Same-version dependency| PkgDist
    PkgDist -.->|Dev dependency (asset distribution only)| DevTools
    PkgDevkit -.->|Dev dependency (CLI harness)| DevTools
    ModelEmbed -.->|Optional search extra| PkgDist
    PkgDocs -->|Harness dependency| PkgDevkit
    PkgDocs -.->|Document commands and rules| DevTools
    PkgSpec -->|Document dependency| PkgDocs
    PkgSpec -->|Harness dependency| PkgDevkit
    PkgSpec -.->|SDD commands and agent assets| DevTools
    PkgViewer -->|Harness dependency| PkgDevkit
    PkgViewer -.->|Local read-only viewer| DevTools
    PkgViewer -.->|Vendored viewer library (autohub)| Runtime
```

---

## 2. Package Breakdown

`devkit-core` owns shared contracts in `devkit_core.base` and implementations in `devkit_core.core`.
Base never imports core. The package depends only on PyYAML and
`devkit-advisory`. It is released at the same version as dist and agt. Generic primitives no longer live
in the dist wheel; project configuration, receipts and CLI support remain there.

Application wheels own independent regular packages: `devkit_dist`, `devkit_agt`, `devkit_docs`,
`devkit_spec`, `devkit_mcp` and `devkit_viewer`. `devkit_core` owns the shared foundation and `devkit_cli` the command-line boundary. Only `devkit-advisory`
continues to ship the PEP 420 `devkit.advisory` API; it never ships `devkit/__init__.py`.
No installed file belongs to two wheels. Foundation and application distributions are released in
lockstep from one tag, pinning workspace runtime dependencies to that exact version
(`ADR-package-split-and-namespaces`).

### 2.1 `devkit-dist` (`packages/devkit-dist`)
- **Distribution Wheel**: `devkit_dist-<version>-py3-none-any.whl`
- **CLI**: `devkit`, the sole console script: the distribution commands, `devkit shared` and `devkit host`, plus whatever installed
  packages mount through `devkit.commands` (`ARCH-05-3-command-plugins`).
- **Contents**: Project configuration and receipts (`devkit_dist.features.project`), shared CLI boundary (`devkit_dist.adapters.cli`, `devkit-cli` bound to devkit), document search (`devkit_dist.features.search`), host hooks and project MCP registrations
  (`devkit_dist.features.host`), immutable expiring artifacts (`devkit_dist.features.shared`, importing only core/advisory), asset distribution (`devkit_dist.features.distribution`) with the `.devkit/config.toml` schema and the receipt,
  the root command line (`devkit_dist.cli`, `devkit_dist.__main__`) and the built-in bundles `devkit`, `advisory` and
  `git-commits` (`ADR-foundation-and-mcp-package-ownership`).
- **Dependencies**: `click`, `jinja2`, `pyyaml`, `tomlkit`, `devkit-core`, `devkit-cli` and `devkit-advisory` (locked to the same version);
  extra `search` (numpy, tokenizers, `devkit-embed`). It never depends on `devkit-agt`, and its tests also
  run in an environment without it (`just test-dist`).

### 2.2 `devkit-agt` (`packages/devkit`)
- **Distribution Wheel**: `devkit_agt-<version>-py3-none-any.whl`
- **CLI**: no console script; `devkit rules`, `devkit workflow`, `devkit gate`, `devkit worktree`, `devkit generated`,
  `devkit integration` and `devkit run` mount under the `devkit` executable through `devkit.commands`
  (`ADR-package-split-and-namespaces`).
- **Contents**: The developer harness: rules engine, delivery workflows, commit gates, task worktrees, tracked
  generated files, approval-bound integration and the compact runner, with the built-in bundles `authoring` and
  `harness` (auto-selected).
- **Dependencies**: `click`, `pyyaml`, `tomlkit`, `devkit-core`, `devkit-dist` and `devkit-advisory` (all locked to the same
  version); its `search` extra requires `devkit-dist[search]`; `mcp` requires the same-version `devkit-mcp`.

### 2.3 `devkit-advisory` (`packages/devkit-advisory`)
- **Distribution Wheel**: `devkit_advisory-<version>-py3-none-any.whl`
- **Contents**: The Agent Advisory Protocol standard library types (`AdvisoryError`, `Advisory`, `ExitCode`, `Actor`, `Level`, `Retry`).
- **Dependencies**: None (Python standard library only).
- **Role**: Published on its own so consumer libraries can raise and handle advisories without importing the devkit CLI or orchestration engines.

### 2.3.1 `devkit-cli` (`packages/devkit-cli`)
- **Distribution Wheel**: `devkit_cli-<version>-py3-none-any.whl`
- **Contents**: `devkit_cli`, the agent-first output contract of `ARCH-08-1-agent-output` for any click command:
  `Boundary`, the output helpers, `LazyGroup` and the `devkit_cli.testing` helper (`CAP-CLI-agent-cli-toolkit`).
- **Dependencies**: `click` and `devkit-advisory` (same version); nothing else is imported.
- **Role**: The runtime dependency of click tools in other repositories and the base of `devkit_dist.adapters.cli`.
  A semver contract like `devkit-advisory`, released at the same version.

### 2.4 `devkit-docs` (`packages/devkit-docs`)
- **Distribution Wheel**: `devkit_docs-<version>-py3-none-any.whl`
- **CLI**: `devkit docs` (`resolve`, `refs`, `list`, `search`), mounted through `devkit.commands`.
- **Contents**: The document system: the document model (kinds, IDs, frontmatter, references, aliases), the
  document index and its memo, namespaces (`[[tool.docs.namespaces]]`), browse and search
  (`devkit_docs.features.documents`); the implementations of the nine document rules and the entrypoint path
  contract (`devkit_docs.features.governance`); the `DOCS_` codes and the proposal layout and effort vocabulary (`devkit_docs.base`).
  It ships no bundle and knows no delivery process: the `devkit.docs.status_overlay` entry-point group lets a
  delivery package change how `devkit docs list` shows a document's status.
- **Dependencies**: `devkit-agt`, `devkit-core` and `click` (same version); its `search` extra requires
  `devkit-agt[search]`. It never imports `devkit_spec` (`ADR-document-package`).
- **Contracts**: `CAP-DOCS-document-model`.

### 2.5 `devkit-spec` (`packages/devkit-spec`)
- **Distribution Wheel**: `devkit_spec-<version>-py3-none-any.whl`
- **CLI**: `devkit spec` (`new`, `proposal`, `policy`, `entrypoints`, `scope`, `worker`), mounted through
  `devkit.commands`.
- **Contents**: Proposals, spec bundles, delivery integration, code entrypoints (derive and apply), scope registry,
  delivery policy, worker inspection, the lifecycle rules, and the `spec` guidance bundle with its workflows,
  rules, templates and opt-in docs skeleton. The bundle ships every rule asset, including the document rules,
  whose wrappers import `devkit_docs`. It registers the `spec` status overlay that shows a draft proposal under
  Planning as `reviewing`.
- **Dependencies**: `devkit-docs`, `devkit-agt`, `devkit-core` and `click` (same version); its `search` extra
  requires `devkit-docs[search]`. Its proposal acceptance and handoff run through the `devkit spec proposal` CLI,
  and the base harness remains SDD-agnostic (`ADR-document-package`).
- **Contracts**: `CAP-HARN-command-mount`, `CAP-HARN-agent-guidance`.

### 2.6 `devkit-viewer` (`packages/devkit-viewer`)
- **Distribution Wheel**: `devkit_viewer-<version>-py3-none-any.whl`, carrying the committed page build.
- **CLI**: `devkit viewer serve`, mounted through `devkit.commands`: a foreground, loopback-only, read-only server
  for several local repositories.
- **Contents**: the server (`devkit_viewer`) and, under `frontend/`, one Svelte source for the page and for the
  component library whose `npm pack` tarball autohub vendors. Node is needed only to change the frontend.
- **Dependencies**: `devkit-agt`, `devkit-core` and `click`. It consumes foundation primitives,
  distribution project support and `devkit.advisory`; it has no dependency on `devkit-docs` or `devkit-spec` code,
  since the page parses the documents itself.
- **Contracts**: `CAP-VIEW-repository-viewer`, `ADR-viewer` as superseded by
  `ADR-viewer-working-tree`.

### 2.7 Opt-in and Example Content Packages
- **`devkit-catalog` (`packages/devkit-catalog`)**: Ships opt-in bundle assets that are installed in the environment but only deployed when explicitly selected (`devkit add <bundle>`).
- **`devkit-starter` (`packages/devkit-starter`)**: Example external content package demonstrating bundle authoring.
- Both test their bundles against the manifest reader of `devkit-dist`, their only development dependency.
- **`devkit-embed` (`models/devkit-embed`)**: Hand-built data package containing the default dense embedding model for the `search` extra of `devkit-dist` (and `devkit-agt[search]`).

### Repository development bundle

`tools/devkit-dev` owns repository-specific project structure and layering checks and the release handbook
playbook (`handbook` preset; `CAP-DLV-release-handbook`), whose script lives in root `scripts/handbook.py`. It is a
bundle-only development package; optional `base`, `utils` or feature layers may be added when it
acquires Python behavior. Its rules and playbook are separate from the reusable assets shipped to consumers.

### Optional MCP runtime

`packages/devkit-mcp` ships `devkit_mcp` and mounts `devkit mcp` through `devkit.commands`. It is a
lockstep application wheel, depending on the exact dist release, `fastmcp>=4.0.3,<5`, `mcp-types>=2,<3` and
`jsonschema`. It owns transport,
form adaptation and `devkit.host.services` discovery; integration and handoff remain domain services. Dist imports
no runtime module and keeps the executable, receipts, hooks and narrow project-registration reconciler.
`ADR-mcp-runtime-and-shared-artifacts` defines this inversion.
