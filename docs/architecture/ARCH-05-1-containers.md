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
        PkgAdv["packages/devkit-advisory<br>(devkit-advisory wheel)"]
        PkgCat["packages/devkit-catalog<br>(devkit-catalog wheel)"]
        PkgStart["packages/devkit-starter<br>(devkit-starter wheel)"]
        ModelEmbed["models/devkit-embed<br>(devkit-embed wheel, manual release)"]
    end

    subgraph ConsumerApp ["Consumer Repository (e.g. app-common, autohub)"]
        Runtime["Runtime Application Code"]
        DevTools["Development Environment / Agents"]
    end

    PkgAdv -.->|Runtime dependency (std-lib only)| Runtime
    PkgDevkit -.->|Dev dependency (CLI harness)| DevTools
    ModelEmbed -.->|Optional search extra| PkgDevkit
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

### 2.3 Opt-in and Example Content Packages
- **`devkit-catalog` (`packages/devkit-catalog`)**: Ships opt-in bundle assets (e.g. `github-milestones`, `host-observer`) that are installed in the environment but only deployed when explicitly selected (`devkit add <bundle>`).
- **`devkit-starter` (`packages/devkit-starter`)**: Example external content package demonstrating bundle authoring.
- **`devkit-embed` (`models/devkit-embed`)**: Hand-built data package containing the default dense embedding model for `devkit-agt[search]`.
