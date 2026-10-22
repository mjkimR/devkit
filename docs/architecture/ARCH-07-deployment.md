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
├── devkit_dist-X.Y.Z-py3-none-any.whl
├── devkit_agt-X.Y.Z-py3-none-any.whl
├── devkit_advisory-X.Y.Z-py3-none-any.whl
├── devkit_core-X.Y.Z-py3-none-any.whl
├── devkit_cli-X.Y.Z-py3-none-any.whl
├── devkit_mcp-X.Y.Z-py3-none-any.whl
├── devkit_spec-X.Y.Z-py3-none-any.whl
├── devkit_starter-X.Y.Z-py3-none-any.whl
├── devkit_catalog-X.Y.Z-py3-none-any.whl
├── devkit_viewer-X.Y.Z-py3-none-any.whl
├── devkit_dev-X.Y.Z-py3-none-any.whl
└── SHA256SUMS
```

### 1.1 Consumer Dependency Declaration

In consumer projects managed with `uv`, devkit is declared either via release wheel URLs or directly via Git references in `pyproject.toml`:

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
# Or distribution only (no harness commands or guidance), never next to devkit-agt:
uv add --dev "devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist"
# Optional SDD extension; uv uses the same monorepo for its base dependencies:
uv add --dev "devkit-spec @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-spec"
# Optional local viewer; its page is committed, so installing from Git needs no Node:
uv add --dev "devkit-viewer @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-viewer"
```

`uv.lock` pins the resolved commits. A Git requirement on `devkit-agt` brings `devkit-dist`, `devkit-core`, `devkit-cli` and
`devkit-advisory` from the same commit (their workspace sources), and the `search` extra brings the model wheel from the release
`packages/devkit-dist/pyproject.toml` pins. Every workspace distribution under `packages/` and `tools/` shares the version in root `VERSION` and is released
from its matching `vX.Y.Z` tag. `just version-sync` updates static package versions, versioned internal requirements
and `uv.lock`. Existing internal version constraints become exact matching pins; unversioned requirements retain
their spelling. The separately built devkit-embed wheel keeps its model version. `just version-check` and
`scripts/release.sh` enforce metadata consistency; release builds also check the tag and `uv lock --check`.
The version source and generated metadata policy is `ADR-single-release-version`. A tool installation names the owner of the `devkit` executable and adds the harness:
`uv tool install <devkit-dist requirement> --with <devkit-agt requirement>` (`ARCH-05-3-command-plugins`). The viewer's Svelte library is not a release asset: a host such as autohub
vendors its `npm pack` tarball from a pinned commit (`CAP-VIEW-repository-viewer`). Release-wheel installations
name every required local package wheel explicitly (a `devkit-agt` installation names the `devkit-dist`, `devkit-core`,
`devkit-cli` and `devkit-advisory` wheels too); release notes include the harness, distribution-only, SDD, viewer and tool installation
commands, and the runtime-only `devkit-advisory` and `devkit-cli` (with `devkit-advisory`) installations.

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
