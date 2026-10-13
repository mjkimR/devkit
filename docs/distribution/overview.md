# Agent Asset Distribution: Overview

`devkit.distribution` packages, projects, upgrades, audits and restores agent assets (instructions, playbooks,
skills, subagents, workflows, rules, gates) for Codex, Claude Code and Antigravity as versioned Python packages.
Commands, configuration and codes are in the [reference](reference.md); its
[section 5](reference.md#5-specifications) lists the specifications.

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
│                   devkit (Python CLI: devkit)                    │
│  - Entry-point & resource discovery (`importlib.resources`)      │
│  - Manifest validation, inventory planning & preset selection    │
│  - Transaction engine, advisory locking & write-ahead journal    │
│  - Native projections (Codex, Claude Code, Antigravity)          │
│  - Context loading & playbook search                             │
│  - Local authoring validator & deterministic ZIP builder         │
└──────────────────┬───────────────────────────────┬───────────────┘
                   │                               │
       (Projects & Manages)           (Receipt read by)
                   │                               │
                   ▼                               ▼
┌────────────────────────────────────┐ ┌───────────────────────────┐
│       Consumer Project Workspace   │ │   Receipt consumers       │
│  - .devkit/installation.json       │ │  - devkit.rules: rule     │
│  - .devkit/managed/<bundle>/       │ │    assets                 │
│  - .devkit/transient/ (lock, jrnl) │ │  - devkit.workflow: defs, │
│  - Projected native agent files    │ │    checks, roles          │
│    (.agents/, .codex/, .claude/)   │ │  - devkit.gate: gates     │
└────────────────────────────────────┘ └───────────────────────────┘
```

Three `schema = 1` contracts connect the units: the bundle manifest `bundle.toml` inside each content wheel
([Manifest Specification](manifest-spec.md)), the Git-tracked project configuration `.devkit/config.toml`
([selection model](sync-and-transactions.md#2-asset-selection-model)) and the Git-tracked receipt
`.devkit/installation.json` ([receipt](sync-and-transactions.md#1-the-installation-receipt-devkitinstallationjson)).
`devkit.rules`, `devkit.workflow` and `devkit.gate` load the assets the receipt records; asset code declares its
own dependencies through wheels.

## 3. Module Layout

The code lives in `packages/devkit/src/devkit/distribution/` and imports only `devkit.core` (frontmatter grammar,
typed receipt reader, safe relative paths, project root discovery) and `devkit.advisory`. Modules import each other
by absolute path (`devkit.distribution...`), never relatively. The library surface is exported from
`devkit.distribution`: `sync_project`, `load_bundle`, `get_context`, `search_playbooks`, the override operations,
`plan_bundle`, `get_project_status`, `get_project_listing`, and their results, frozen dataclasses whose `to_dict()`
is the JSON the command prints.

- `content.py`: file content helpers shared by both sides: `Content` (bytes plus mode), `normal_mode`,
  `same_content`, the one `sha256` helper, canonical JSON (`json_content`) and the receipt `signature`.
- `bundles/`: the authoring side; no workspace knowledge, imports nothing from `installation/`.
  - `common.py`: slug, version and `x-<name>` key grammars, the reserved `all` preset, supported agent names, and
    `read_frontmatter`/`locate_frontmatter` (every failure a `BundleError`).
  - `manifest.py`: `bundle.toml` schema 1, source path rules, seeded targets, `source_files`, kind-specific
    validation at load.
  - `instructions.py`, `playbooks.py`, `workflows.py`, `subagents.py`: per-kind headers; role contract rendering.
  - `guidance.py`: the context-loading prerequisite inserted into skills. `fragments.py`: `guidance` fragments.
  - `package.py`: deterministic ZIP archives.
- `installation/`: the consumer workspace side.
  - `workspace.py`: well-known paths, path safety for reads and writes, file snapshots.
  - `transaction.py`: project lock, write-ahead journal, atomic replacement (also used to save
    `.devkit/config.toml`), recovery, `prune_empty_parents`.
  - `receipt.py`: strict receipt reading (`devkit.core.receipt` plus ownership rules) and serialization.
  - `config.py`: `.devkit/config.toml` reading, selection resolution, edits checked before a sync and saved after it.
  - `discovery.py`: installed bundles via `devkit.bundles`; built-in and auto-selected bundles.
  - `inventory.py`: the desired state (`Inventory`): managed copies, projections, rendered role contracts,
    generated entry skills, rendered fragments, seeds, override tracking.
  - `overrides.py`, `override_commands.py`: which file a deployment reads, drift tracking, `override ...` commands.
  - `sync.py`: `sync_project` (lock, a saved selection, `commit_locked`, then post-sync extensions) and recovery.
  - `guidance_block.py`: the root `AGENTS.md` block; its markers come from `devkit.core`.
  - `context.py`, `playbook_search.py`, `reading.py`: agent-facing reads under the shared lock.
  - `status.py`, `plan.py`, `results.py`: `status`, `list`, `bundle plan` and the result dataclasses.
  - `playbook_skill.py`, `workflow_skill.py`: the generated `devkit-playbook` and `devkit-workflow` entry skills.
  - `extensions.py`: the `devkit.post_sync` extension point.
- `errors.py`: the `DistributionError` hierarchy, one class per code, and the sync notice classes
  ([codes](reference.md#error-codes), [notices](reference.md#sync-output-and-notices)).
- `cli/`: the distribution commands, listed in `COMMANDS`; the root `devkit` group loads each one lazily by name. Output and exit codes
  follow [Agent-First Output](../architecture/agent-output.md) and the
  [reference conventions](reference.md#1-quick-start).
