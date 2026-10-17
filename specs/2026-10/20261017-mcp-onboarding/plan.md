---
id: PLAN-mcp-onboarding
spec: SPEC-mcp-onboarding
---

# Technical Plan: `SPEC-mcp-onboarding` MCP onboarding

## 1. Constitution & Invariant Review

No ADR conflicts. Host uses core/advisory only; no dependency on distribution, worktree or integration is added.
`CAP-HOST-lifecycle-observation` and `CAP-INT-mcp-services` retain host ownership of trust and permission settings.
Explicit user-invoked setup extends the existing read-only config command without altering sync transactions.

## 2. Components and Interfaces

Add host/mcp/onboarding.py with bounded captured subprocess calls to Codex list/add/get. Read the named user
entry from CODEX_HOME/config.toml (default ~/.codex/config.toml) with tomllib, without editing it. Codex list/get
provide effective configuration, which can include project layers. Inspect workspace/ancestor .codex/config.toml
layers and refuse any devkit entry before setup mutation, even if identical; --replace only manages the user entry.
Report user state and effective_state separately. Effective/user state disagreement also refuses setup. Use list to distinguish
missing entries from CLI/configuration failures; inspect only the named entry and never return foreign settings
or credential values. Setup preflights the running SDK/server and rejects linked-worktree workspace or interpreter
paths, including symlink spellings, before invoking add. Reuse configuration() for exact command/args.

Expose setup/status with --host codex, -w and --format; setup additionally accepts --replace. Registration matching
requires exact stdio command/args, enabled state, empty env/env_vars/cwd and absent tool restrictions. Other settings
are preserved on a matching entry. A replaced entry uses Codex add once, followed by inspection. No remove/add gap.
Report action registered/replaced/unchanged for setup and state missing/matching/different for status, with
connection, UI, trust and execution permissions unknown. Distinct advisories cover CLI failure, conflict and
unsafe runtime. Configuration generation remains read-only and available without the optional SDK.

Installation routes link a shared optional MCP guide. The host capability, integration capability and quick
reference describe registration versus connection and unsupported automatic sync registration.

## 3. Failure Modes

All host subprocesses use argument arrays, a fixed timeout and captured output. Failures discard potentially
sensitive stderr/stdout and raise an advisory; writes are never retried automatically. Status does not import
service factories or start servers. Setup checks SDK/server imports before mutation. Simultaneous external Codex
configuration writers remain outside devkit's transaction scope; post-write verification detects disagreement.

## 4. Verification

Tests cover first setup, unchanged execution, conflict and replacement, missing/different/matching status,
disabled/extra settings, absent SDK, malformed CLI output, timeout/process failure, worktree paths, and text/JSON
boundaries. A real Codex CLI check uses an isolated temporary CODEX_HOME, leaving actual user settings untouched.
Run just lint-check devkit, just check devkit, relevant host/integration/layering tests, rules check and packaging smoke.
