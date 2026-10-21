---
id: PROP-worker-shared-state-mcp
title: Shared state and workspace across worktrees and cloud agents
summary: "Define a shared state and artifact workspace across worktrees and cloud agents, backed by a base-checkout .devkit/.shared local adapter and pluggable server adapters over dual MCP and CLI surfaces."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-20
target_area: capabilities/collaboration/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-autonomous-backlog-and-orchestration
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/scope/
    - docs/capabilities/collaboration/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---


# [PROP-worker-shared-state-mcp] Shared state and workspace across worktrees and cloud agents

## 1. Background & Hypothesis

`SPEC-scope-registry-sandbox-access` retains Git storage and separates side-effect-free query/history access from
mutations. Register, update, release and recovery still need shared registry and per-worktree token writes.
`CAP-COLL-work-scope-registry` coordinates several workers against that state. At the same time, multi-unit
`local-orchestrated` and `cloud-pr` workflows need a shared, untracked space to exchange ephemeral cross-worktree
artifacts—specifically proposal review reports (`PROP-proposal-review-and-approval`)—without dirtying Git working
trees or committing localized temporary documents into the public English repository.

The hypothesis is that a shared workspace and coordination layer with a pluggable storage adapter—exposed through both
MCP tools and equivalent CLI commands—can serve bounded coordination records and TTL-governed shared artifacts across
local linked worktrees and unattended cloud agents:

- **Default local adapter (`.devkit/.shared/`)**: resolves to the retained base checkout's `.devkit/.shared/`
  directory from any linked worktree (via common-Git-directory discovery), automatically excluded from Git tracking so
  base-checkout cleanliness checks (`git status --porcelain`) remain clean while IDE `file://` links and local viewers
  can open shared artifacts directly.
- **Pluggable server adapter (e.g., Firestore)**: selectable via environment variables or local execution
  configuration for Cloud Agent environments where no shared local filesystem exists.
- **Dual MCP and CLI surface (trade-off to evaluate in Planning)**:
  - **Local multi-worktree (`local-orchestrated`) via MCP**: in linked worktrees, host shell sandboxes block writes
    outside the active worktree (`<base-checkout>/.devkit/.shared/`, sibling worktrees, `.git/`, and external sockets,
    as observed in `MAT-codex-native-worker-evidence`). When the project MCP server is trusted and connected
    (`CAP-MCP-runtime-registration`), routing shared-workspace calls through MCP delegates writes to the retained base
    process without per-command OS sandbox escalations or custom daemon lifecycle management
    (`ARCH-01-introduction-and-goals` §3.4).
  - **Cloud Agent (`cloud-pr`) and unapproved/disconnected sessions via CLI**: unlike skills (`SKILL.md`), MCP servers
    require initial host server trust and tool permission, and cloud runtimes either do not launch local `stdio` MCP
    transports or run under `CAP-MCP-runtime-registration`'s `cloud` read-only restriction. Exposing the exact same
    `SharedWorkspaceAdapter` operations through `devkit` CLI commands lets Cloud Agents and non-MCP sessions read and
    write shared artifacts immediately without interactive server trust.

## 2. Technical Spike Questions

- **Q1 — Shared workspace contract and concrete consumers:** Define the exact boundary between authoritative
  coordination state (`CAP-COLL-work-scope-registry`) and ephemeral shared artifacts (`PROP-proposal-review-and-approval`
  review reports). What bounded operations (`put`, `get`, `list`, `delete`/sweep by namespace, kind and slug)
  satisfy both without exposing unrestricted arbitrary filesystem access?
- **Q2 — Adapter architecture and configuration:** How should the storage adapter interface separate the local
  filesystem backend (`<base-checkout>/.devkit/.shared/`) from remote/server backends (such as Firestore), and how do
  environment variables or `.devkit/config.local.toml` (`SPEC-local-config-execution-environment`) select and configure
  the active adapter across both CLI and MCP entry points?
- **Q3 — MCP vs. CLI routing, trust friction and cloud execution:** Compare when agents should call MCP vs. CLI:
  - In local linked worktrees, does MCP delegation eliminate enough sandbox friction to justify tool-permission setup,
    or when is direct CLI preferable?
  - If MCP tools are used for non-interactive shared-workspace writes, how should `devkit.core.mcp` classify them so
    they are not conflated with human form-elicitation tools (`interactive`) that `CAP-MCP-runtime-registration` blocks
    in `cloud` mode?
  - How do CLI and MCP callers share lock discipline and deterministic fallback against the same underlying store?
- **Q4 — Discovery and Git cleanliness:** How does a linked worktree, CLI command or MCP server resolve the base
  checkout's `.devkit/.shared/` deterministically without trusting arbitrary caller paths, and how is `.devkit/.shared/`
  excluded (via `.gitignore` or clone-local `info/exclude`) so base-checkout preflight checks in integration and
  handoff never fail on shared artifacts?
- **Q5 — TTL retention, revision metadata and lifecycle:** Ephemeral artifacts such as proposal review reports need
  bounded retention (default 7-day TTL) and source-commit (`source_sha`) metadata. When should lazy TTL expiration
  sweeps run (on write/list operations and `devkit rules check -p hygiene`), and how are expired artifacts cleaned up
  safely without affecting authoritative scope-registry records?
- **Q6 — Authority, ownership and concurrency:** Which caller may read, write, overwrite or release each record or
  artifact? Define atomic writes, lock discipline across concurrent CLI/MCP processes, retry/idempotency and behavior
  on denied authorization or forged repository/worktree identities.

## 3. Proposed Design & Impact

Planning should define a unified adapter, CLI and optional MCP service contract that covers:

1. **Pluggable storage backend (`SharedWorkspaceAdapter`)**:
   - `local` (default): stores namespaced records and artifacts under `<base-checkout>/.devkit/.shared/`, resolving
     the base checkout from any linked worktree and returning resolved local paths/URIs so host agents and local UIs
     can link directly to generated artifacts.
   - `server` (extensible, e.g., Firestore): selected via environment variable or local config for remote/cloud worker
     execution, exposing the same logical artifact URI/key and metadata contract.
2. **Dual CLI + MCP access boundary**:
   - Core library owns all adapter, locking and TTL logic.
   - MCP tools provide sandbox-delegated access for connected local multi-worktree sessions; CLI commands provide
     zero-trust-setup execution for Cloud Agents (`cloud-pr`), scripts and sessions without MCP connected.
3. **Bounded artifact lifecycle with TTL**:
   - Artifacts carry structured metadata (`kind`, `slug` or `unit`, `source_sha`, `created_at`, `expires_at` defaulting
     to 7 days).
   - Lazy sweep removes expired artifacts automatically during workspace operations or hygiene checks; expired or
     missing artifacts can be regenerated on demand.
4. **Isolation from Git working-tree state**:
   - `.devkit/.shared/` is ignored by Git so creating or updating shared reports from a worker worktree never dirties
     the base checkout or blocks `integration_integrate` / `spec_handoff`.

Expected impact starts in `CAP-COLL-work-scope-registry` and `CAP-MCP-runtime-registration`. Planning must identify the
exact package owner, adapter protocol, CLI/MCP parity, environment variable names and code boundaries before
Development.

Acceptance evidence for a selected design should include:

- Workers in separate linked worktrees write and read shared artifacts through the selected MCP or CLI surface,
  resolving to the same `<base-checkout>/.devkit/.shared/` store while an unrelated repository remains isolated.
- Unattended / Cloud Agent execution can read and write shared workspace artifacts through the CLI surface (and configured
  server adapter) without requiring interactive MCP server trust or form capability.
- Writing shared artifacts leaves `git status --porcelain --untracked-files=normal` clean in both the base checkout
  and linked worktrees.
- Artifacts older than the configured TTL (default 7 days) are swept deterministically without touching active
  coordination records, and stale `source_sha` metadata is detectable by consumers.
- Adapter selection via environment variable / config cleanly switches or validates backend configuration and reports
  actionable advisory codes on misconfiguration.
- Concurrent update/release and retry after a lost response preserve ownership and revision semantics.

Non-goals: unrestricted arbitrary file access outside the shared namespace, changing host-wide sandbox settings,
universal approval guarantees, or replacing Git worktrees.

## 4. Lifecycle & Retirement Criteria

This draft records the shared workspace and coordination foundation for Planning; `PROP-proposal-review-and-approval`
is its primary artifact consumer. Medium Planning should evaluate the MCP vs. CLI trade-offs across local and cloud
hosts and finalize the adapter protocol, tool/CLI schemas, `.devkit/.shared/` exclusion rule and TTL sweep mechanics
before handoff.
