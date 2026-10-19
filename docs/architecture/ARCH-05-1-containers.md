---
id: ARCH-05-1-containers
title: Building Block View - Containers
summary: "Container topology of devkit: workspace packages, distribution wheels, and external content packages."
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
    PkgDevkit -.->|Dev dependency (CLI harness)| DevTools
    ModelEmbed -.->|Optional search extra| PkgDevkit
    PkgSpec -->|Harness dependency| PkgDevkit
    PkgSpec -.->|SDD commands and agent assets| DevTools
    PkgViewer -->|Harness dependency| PkgDevkit
    PkgViewer -.->|Local read-only viewer| DevTools
    PkgViewer -.->|Vendored viewer library (autohub)| Runtime
```

---

## 2. Package Breakdown

### 2.1 `devkit-agt` (`packages/devkit`)
- **Distribution Wheel**: `devkit_agt-<version>-py3-none-any.whl`
- **CLI**: `devkit`
- **Contents**: The full developer tooling suite: asset distribution, rules engine, delivery workflows, commit gates, task worktrees, compact runner, host hooks, and MCP services.
- **Dependencies**: `click`, `pyyaml`, `tomlkit`, and `devkit-advisory` (locked to the same version).

### 2.2 `devkit-advisory` (`packages/devkit-advisory`)
- **Distribution Wheel**: `devkit_advisory-<version>-py3-none-any.whl`
- **Contents**: The Agent Advisory Protocol standard library types (`AdvisoryError`, `Advisory`, `ExitCode`, `Actor`, `Level`, `Retry`).
- **Dependencies**: None (Python standard library only).
- **Role**: Published on its own so consumer libraries can raise and handle advisories without importing the devkit CLI or orchestration engines.

### 2.3 `devkit-spec` (`packages/devkit-spec`)
- **Distribution Wheel**: `devkit_spec-<version>-py3-none-any.whl`
- **CLI**: `devkit spec`, mounted through `devkit.commands`.
- **Contents**: The SDD document model and commands, proposals, spec bundles, code entrypoints, scope registry,
  and the `spec` guidance bundle with its workflows, rules, templates and opt-in docs skeleton.
- **Dependencies**: `devkit-agt` and `click`; the base harness remains SDD-agnostic.
- **Contracts**: `CAP-HARN-command-mount`, `CAP-HARN-agent-guidance`.

### 2.4 `devkit-viewer` (`packages/devkit-viewer`)
- **Distribution Wheel**: `devkit_viewer-<version>-py3-none-any.whl`, carrying the committed page build.
- **CLI**: `devkit viewer serve`, mounted through `devkit.commands`: a foreground, loopback-only, read-only server
  for several local repositories.
- **Contents**: the server (`devkit_viewer`) and, under `frontend/`, one Svelte source for the page and for the
  component library whose `npm pack` tarball autohub vendors. Node is needed only to change the frontend.
- **Dependencies**: `devkit-agt` (its shared core) and `click`; no `devkit-spec` code, since the page parses the
  documents itself.
- **Contracts**: `CAP-VIEW-repository-viewer`, `ADR-viewer-distribution-and-frontend-build`,
  `ADR-read-only-local-server-over-git-refs`.

### 2.5 Opt-in and Example Content Packages
- **`devkit-catalog` (`packages/devkit-catalog`)**: Ships opt-in bundle assets (e.g. `host-observer`) that are installed in the environment but only deployed when explicitly selected (`devkit add <bundle>`).
- **`devkit-starter` (`packages/devkit-starter`)**: Example external content package demonstrating bundle authoring.
- **`devkit-embed` (`models/devkit-embed`)**: Hand-built data package containing the default dense embedding model for `devkit-agt[search]`.
