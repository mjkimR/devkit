---
id: ARCH-05-4-distribution-components
title: Building Block View - Distribution Components
summary: "Agent asset distribution components, shared and local configuration, canonical and personal runtime views, and transaction boundaries."
status: active
created_at: 2026-10-17
---

# [ARCH-05-4-distribution-components] Building Block View: Distribution Components

`devkit_dist.features.distribution` packages, projects, upgrades, audits and restores agent assets (instructions, playbooks,
skills, subagents, workflows, rules, gates, hooks) for Codex, Claude Code and Antigravity as versioned Python packages.
Commands, configuration and codes are in the [reference](../development/reference/distribution.md); its
[section 5](../development/reference/distribution.md#5-specifications) lists the specifications.

## 1. Principles

1. **Native config fidelity**: native subagent definitions and tool configurations are copied verbatim, never
   converted between hosts. An agent without a native variant gets no projection and the sync reports it
   (`unprojected`); a role contract must name every agent, so a missing host fails validation. Nothing is silently
   stripped or degraded.
2. **Standard Python packaging**: content ships as wheels installed with `uv` as dev dependencies and discovered
   through `importlib.metadata`; versions are pinned by `uv.lock`. There is no custom resolver, downloader or cache.
3. **Deterministic, side-effect-free ingestion**: reproducible manifests, normalized modes (`0644`/`0755`), strict
   relative path containment, and no execution of bundle code during a sync.
4. **Explicit ownership**: managed assets, overrides, seeded files and foreign files are kept apart; an unmanaged
   collision or a modified deployed file halts the sync before any write.
5. **Transactional integrity**: every installation, upgrade and removal is planned and conflict-checked up front,
   then executed under a project lock with a write-ahead journal, atomic replacement and recovery.

## 2. Architecture Units

```text
┌──────────────────────────────────────────────────────────────────┐
│                   Python Content Wheels (uv)                     │
│  - Installed via `uv add --dev <content-wheel>`                  │
│  - Entry point group: `devkit.bundles`                           │
│  - Resource module containing `bundle/bundle.toml` & assets      │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ (importlib discovery)
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              devkit-dist (Python CLI: devkit)                    │
│  - Entry-point & resource discovery (`importlib.resources`)      │
│  - Manifest validation, inventory planning & preset selection    │
│  - Transaction engine, advisory locking & write-ahead journal    │
│  - Native projections (Codex, Claude Code, Antigravity)          │
│  - Context loading & playbook search/get                             │
│  - Local authoring validator & deterministic ZIP builder         │
└──────────────────┬───────────────────────────────┬───────────────┘
                   │                               │
       (Projects & Manages)           (Receipt read by)
                   │                               │
                   ▼                               ▼
┌────────────────────────────────────┐ ┌───────────────────────────┐
│       Consumer Project Workspace   │ │   Receipt consumers       │
│  - .devkit/installation.json       │ │  - devkit_agt.features.rules: rule     │
│  - .devkit/managed/<bundle>/       │ │    assets                 │
│  - .devkit/transient/ (lock, jrnl) │ │  - devkit_agt.features.workflow: defs, │
│  - Projected native agent files    │ │    checks, roles          │
│    (.agents/, .codex/, .claude/)   │ │  - devkit_agt.features.gate: gates     │
└────────────────────────────────────┘ └───────────────────────────┘
```

Three `schema = 1` contracts connect the units: the bundle manifest `bundle.toml` inside each content wheel
(`CAP-DIST-manifest-spec`), the Git-tracked project configuration `.devkit/config.toml`
(`CAP-DIST-sync-and-transactions`) and the Git-tracked receipt
`.devkit/installation.json` (`CAP-DIST-sync-and-transactions`).
`devkit_agt.features.rules`, `devkit_agt.features.workflow` and `devkit_agt.features.gate` load the assets the receipt records; asset code declares its
own dependencies through wheels.

## 3. Module Layout

The distribution feature lives in `packages/devkit-dist/src/devkit_dist/features/distribution/`.
It uses shared primitives from `devkit_core.core`, project configuration and receipts from
`devkit_dist.features.project`, `devkit.advisory`, document search and native host contracts.
The dist wheel never depends on `devkit-agt`. Feature imports use absolute paths.

- `cli/` adapts distribution commands to use cases and formats their results. The root executable
  discovers the commands lazily (`ARCH-05-3-command-plugins`).
- `usecases/` owns sync and recovery, context and playbook reads, overrides, project listing/status
  and bundle planning. `sync_selection` and `add_selection` own persistence and replacement/union
  policy. Public operations also own installed-bundle discovery and cleanup. CLI adapters provide
  parsed inputs and format results; they do not compose configuration-save callbacks.
- `services/bundles/` owns manifest and header validation, role rendering, guidance fragments,
  configurable template rendering and deterministic package creation. It has no installation workspace dependency.
- `services/installation/` owns workspace path safety and snapshots, transaction journaling and
  recovery, configuration selection, bundle discovery, inventory, native projections, guidance blocks
  and generated entry skills. Receipt handling applies distribution ownership rules to the typed reader
  from the project feature.
- `models/` owns content values, bundle and installation contracts, results, notices and error types.
  Results expose `to_dict()` for the JSON command result.

The distribution feature exports operations such as `sync_project`, `load_bundle`, `get_context`,
`get_playbook`, `search_playbooks`, override operations, `plan_bundle`, `get_project_status` and
`get_project_listing`. CLI adapters expose these operations through use cases; internal services do not
import transport code.

Built-in data bundles live under `devkit_dist.bundles`: `devkit`, `advisory` and `git_commits`.
The harness and authoring bundles belong to `devkit_agt.bundles`. Bundle names presented to consumers
remain `devkit`, `advisory`, `git-commits`, `harness` and `authoring`. Output and exit codes follow
`ARCH-08-1-agent-output` and the [reference conventions](../development/reference/distribution.md#1-quick-start).

## Configurable content rendering

The `services/bundles/templates.py` module owns scalar variable declarations, template destination naming and restricted
Jinja rendering. Its Jinja imports are local to rendering so CLI discovery, ordinary bundle loading and non-template
sync do not load the engine. The installation config reader owns `[bundles.<name>.variables]`; inventory resolves
those values against declarations and renders selected instruction, guidance, document and skill `.md.jinja` sources,
including raw project overrides, into final managed `.md` files before transaction planning and receipt hashing.
Skill projections use the rendered filenames and contents before native invocation settings are inserted.
This does not execute bundle Python code or alter the verbatim contract of native host configurations.


## Shared configuration and personal runtime views

The project feature repository `local_config.py` owns restricted local validation, recursive merge, source provenance and explicit-workspace
execution resolution, independent of distribution asset planning and harness engines. Governance keeps `read_project_config` and canonical
receipt loading. Distribution `local_render.py` compares effective and canonical inventory, checks ignored/untracked
output eligibility, captures configuration inputs and validates transient render evidence. `sync.py` journals local
configuration and ledger writes alongside output and shared selection edits. Runtime context/status receive a
validated receipt view; that view never becomes engine or snapshot authority. Worktree lifecycle captures and copies
local preferences before setup on creation only. See `CAP-DIST-sync-and-transactions` and `CAP-WT-task-worktrees`.

## Local MCP registration

Ordinary sync asks the optional launch provider for a retained executable/executor and explicit owning workspace,
then reconciles eligible project host entries separately from portable receipts. The host layer owns the exact-entry
ledger, collision inspection and recoverable registration journal. It never imports `devkit_mcp` by module name.
The fixed lock order is common Git exclusion lock followed by checkout project lock. Dry-run/check compute the same
plan without registration writes; locked sync validates only and directs changed local registrations to ordinary
sync. Fresh absent registrations are initialized separately after locked asset restoration. Trusted native
lifecycle children carry only an owning-workspace refusal constraint, checked after locks and before transaction
writes; approval authority remains in the Host invocation. Tracked or visible foreign destinations remain untouched. See `CAP-MCP-runtime-registration`.
