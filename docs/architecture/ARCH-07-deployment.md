---
id: ARCH-07-deployment
title: Deployment View
summary: "Deployment topology: wheel builds, GitHub Releases, Git dependency sources, and projected directory structures."
status: active
created_at: 2026-10-17
---

# [ARCH-07-deployment] Deployment View

- **arc42**: §7 Deployment View
- Containers: `ARCH-05-1-containers`. Context: `ARCH-03-context`.

---

## 1. Distribution Architecture

devkit packages are not hosted on PyPI. Instead, each Git tag (`vX.Y.Z`) triggers a GitHub Release publishing wheel artifacts with `SHA256SUMS`:

```text
GitHub Release Assets (vX.Y.Z):
├── devkit_agt-X.Y.Z-py3-none-any.whl
├── devkit_advisory-X.Y.Z-py3-none-any.whl
├── devkit_spec-<spec-version>-py3-none-any.whl
├── devkit_starter-<starter-version>-py3-none-any.whl
├── devkit_catalog-<catalog-version>-py3-none-any.whl
├── devkit_viewer-<viewer-version>-py3-none-any.whl
└── SHA256SUMS
```

### 1.1 Consumer Dependency Declaration

In consumer projects managed with `uv`, devkit is declared either via release wheel URLs or directly via Git references in `pyproject.toml`:

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
# Optional SDD extension; uv uses the same monorepo for its base dependencies:
uv add --dev "devkit-spec @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-spec"
# Optional local viewer; its page is committed, so installing from Git needs no Node:
uv add --dev "devkit-viewer @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-viewer"
```

`uv.lock` pins the resolved commits. Devkit-agt and devkit-advisory share a version; spec, starter, catalog and
viewer keep independent versions. The viewer's Svelte library is not a release asset: a host such as autohub
vendors its `npm pack` tarball from a pinned commit (`CAP-VIEW-repository-viewer`). Release-wheel installations name every required local package wheel explicitly; release
notes include both base and SDD installation commands.

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
│   │   └── advisory/
│   ├── overrides/             # Local modifications to upstream bundle assets
│   └── transient/             # Atomic transaction journals
├── .agents/skills/            # Projected skills shared by Codex and Antigravity
├── .claude/skills/            # Projected skills for Claude Code
├── .codex/agents/             # Projected Codex subagent contracts
└── AGENTS.md                  # Root instructions with managed <!-- DEVKIT:START/END --> block
```

Task worktrees are sibling checkouts at `<parent of base>/<base name>-wt-<branch>`, outside `.devkit/`.
See `CAP-WT-task-worktrees` and `CAP-DIST-agent-projections` for the canonical path and projection contracts.
