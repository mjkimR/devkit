---
id: ARCH-05-1-containers
title: Building Block View - Containers
summary: "Container topology of devkit: workspace packages, the devkit-dist, devkit-agt, devkit-advisory and devkit-mcp wheels released in lockstep, and external content packages."
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
        PkgDist["packages/devkit-dist<br>(devkit-dist wheel, devkit executable)"]
        PkgMcp["packages/devkit-mcp<br>(optional devkit-mcp wheel)"]
        PkgDevkit["packages/devkit<br>(devkit-agt wheel)"]
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
    PkgDist -->|Same-version dependency| PkgCore
    PkgDist -->|Same-version dependency| PkgAdv
    PkgMcp -->|Same-version dependency| PkgDist
    PkgMcp -.->|MCP transport and native forms| DevTools
    PkgDevkit -.->|Optional mcp extra| PkgMcp
    PkgDevkit -->|Same-version dependency| PkgDist
    PkgDist -.->|Dev dependency (asset distribution only)| DevTools
    PkgDevkit -.->|Dev dependency (CLI harness)| DevTools
    ModelEmbed -.->|Optional search extra| PkgDist
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

Application wheels own independent regular packages: `devkit_dist`, `devkit_agt`, `devkit_spec`,
`devkit_mcp` and `devkit_viewer`. `devkit_core` owns the shared foundation. Only `devkit-advisory`
continues to ship the PEP 420 `devkit.advisory` API; it never ships `devkit/__init__.py`.
No installed file belongs to two wheels. Foundation and application distributions are released in
lockstep from one tag, pinning workspace runtime dependencies to that exact version
(`ADR-package-split-and-namespaces`, `ADR-package-split-and-namespaces`).

### 2.1 `devkit-dist` (`packages/devkit-dist`)
- **Distribution Wheel**: `devkit_dist-<version>-py3-none-any.whl`
- **CLI**: `devkit`, the sole console script: the distribution commands, `devkit shared` and `devkit host`, plus whatever installed
  packages mount through `devkit.commands` (`ARCH-05-3-command-plugins`).
- **Contents**: Project configuration and receipts (`devkit_dist.features.project`), shared CLI boundary (`devkit_dist.adapters.cli`), document search (`devkit_dist.features.search`), host hooks and project MCP registrations
  (`devkit_dist.features.host`), immutable expiring artifacts (`devkit_dist.features.shared`, importing only core/advisory), asset distribution (`devkit_dist.features.distribution`) with the `.devkit/config.toml` schema and the receipt,
  the root command line (`devkit_dist.cli`, `devkit_dist.__main__`) and the built-in bundles `devkit`, `advisory` and
  `git-commits` (`ADR-dist-foundation-ownership`).
- **Dependencies**: `click`, `jinja2`, `pyyaml`, `tomlkit`, `devkit-core` and `devkit-advisory` (locked to the same version);
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

### 2.4 `devkit-spec` (`packages/devkit-spec`)
- **Distribution Wheel**: `devkit_spec-<version>-py3-none-any.whl`
- **CLI**: `devkit spec`, mounted through `devkit.commands`.
- **Contents**: The SDD document model and commands, proposals, spec bundles, code entrypoints, scope registry,
  and the `spec` guidance bundle with its workflows, rules, templates and opt-in docs skeleton.
- **Dependencies**: `devkit-agt`, `devkit-core` and `click`; the base harness remains SDD-agnostic.
- **Contracts**: `CAP-HARN-command-mount`, `CAP-HARN-agent-guidance`.

### 2.5 `devkit-viewer` (`packages/devkit-viewer`)
- **Distribution Wheel**: `devkit_viewer-<version>-py3-none-any.whl`, carrying the committed page build.
- **CLI**: `devkit viewer serve`, mounted through `devkit.commands`: a foreground, loopback-only, read-only server
  for several local repositories.
- **Contents**: the server (`devkit_viewer`) and, under `frontend/`, one Svelte source for the page and for the
  component library whose `npm pack` tarball autohub vendors. Node is needed only to change the frontend.
- **Dependencies**: `devkit-agt`, `devkit-core` and `click`. It consumes foundation primitives,
  distribution project support and `devkit.advisory`; it has no dependency on `devkit-spec` code,
  since the page parses the documents itself.
- **Contracts**: `CAP-VIEW-repository-viewer`, `ADR-viewer`,
  `ADR-viewer`.

### 2.6 Opt-in and Example Content Packages
- **`devkit-catalog` (`packages/devkit-catalog`)**: Ships opt-in bundle assets (e.g. `host-observer`) that are installed in the environment but only deployed when explicitly selected (`devkit add <bundle>`).
- **`devkit-starter` (`packages/devkit-starter`)**: Example external content package demonstrating bundle authoring.
- Both test their bundles against the manifest reader of `devkit-dist`, their only development dependency.
- **`devkit-embed` (`models/devkit-embed`)**: Hand-built data package containing the default dense embedding model for the `search` extra of `devkit-dist` (and `devkit-agt[search]`).

### Repository development bundle

`tools/devkit-dev` owns repository-specific project structure and layering checks. It starts as a
bundle-only development package; optional `base`, `utils` or feature layers may be added when it
acquires Python behavior. Its rules are separate from the reusable harness rules shipped to consumers.

### Optional MCP runtime

`packages/devkit-mcp` ships `devkit_mcp` and mounts `devkit mcp` through `devkit.commands`. It is a
lockstep application wheel, depending on the exact dist release, `mcp>=1.30,<2` and `jsonschema`. It owns transport,
form adaptation and `devkit.host.services` discovery; integration and handoff remain domain services. Dist imports
no runtime module and keeps the executable, receipts, hooks and narrow project-registration reconciler.
`ADR-mcp-runtime-and-shared-artifacts` defines this inversion.
