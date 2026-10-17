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
├── devkit_starter-X.Y.Z-py3-none-any.whl
├── devkit_catalog-X.Y.Z-py3-none-any.whl
└── SHA256SUMS
```

### 1.1 Consumer Dependency Declaration

In consumer projects managed with `uv`, devkit is declared either via release wheel URLs or directly via Git references in `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "devkit-agt",
    "devkit-advisory",
]

[tool.uv.sources]
devkit-agt = { git = "https://github.com/mjkimR/devkit", subdirectory = "packages/devkit", rev = "<commit-sha>" }
devkit-advisory = { git = "https://github.com/mjkimR/devkit", subdirectory = "packages/devkit-advisory", rev = "<commit-sha>" }
```

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
│   ├── transient/             # Atomic transaction journals
│   └── worktrees/             # Active task worktrees
├── .agents/skills/            # Projected native skills for Antigravity & generic agents
├── .claude/skills/            # Projected skills for Claude Code
├── .codex/skills/             # Projected skills for Codex
└── AGENTS.md                  # Root instructions with managed <!-- DEVKIT:START/END --> block
```
