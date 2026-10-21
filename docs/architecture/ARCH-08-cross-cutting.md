---
id: ARCH-08-cross-cutting
title: Cross-cutting Concepts
summary: "Cross-cutting architectural concepts: Agent Advisory Protocol, agent-first output, resource taxonomy, and exit code conventions."
status: active
created_at: 2026-10-17
---

# [ARCH-08-cross-cutting] Cross-Cutting Concepts

- **arc42**: §8 Cross-cutting Concepts
- Goals: `ARCH-01-introduction-and-goals`. Components: `ARCH-05-2-components`.

---

## 1. Agent Advisory Protocol

Every command in `devkit` reports errors, warnings, and notices through the structured Agent Advisory Protocol (`devkit.advisory`):

```text
[ERROR] <UPPER_SNAKE_CODE>: <clear imperative explanation>
  target: <file-or-resource-path>
  details: <additional diagnostics>
[ACTION] <Deterministic, unambiguous next step for the AI agent>
```

- **Levels**: `ERROR` (halts execution), `WARNING` (advisory warning; does not fail unless `--strict`), `NOTICE` (informational note).
- **Directives**: Every advisory MUST carry an actionable `[ACTION]` directive telling the agent what to fix or inspect next.
- **Library Contracts**: Library functions raise subclasses of `AdvisoryError` containing typed codes and retry modes (`IMMEDIATE`, `AFTER_FIX`, `AFTER_INPUT`, `NEVER`).

See `CAP-ADV-agent-advisory-protocol` for full details.

---

## 2. Agent-First Output Contract

Commands emit output strictly divided between channels:

- **stdout (Primary Result)**:
  - Text mode: Sentinels in the format `[KIND: primary_value key=value ...]`.
  - JSON mode (`--format json`): Exactly one root JSON document containing result data or `{"error": {...}}`.
- **stderr (Advisories & Diagnostics)**:
  - Agent Advisory blocks (`[ERROR]`, `[WARN]`, `[NOTICE]`).
  - Diagnostic logs (`[INFO]`) only enabled with `-v`.

See `ARCH-08-1-agent-output` for channel routing and formatting rules.

---

## 3. Resource Taxonomy

Agent assets distributed by `devkit` fall into a three-tier taxonomy:

1. **Guidance & Context Layer (Natural Language)**:
   - `host-guidance-block`: Managed block in `AGENTS.md`.
   - `package-instruction`: Markdown guidelines with read conditions.
   - `package-playbook`: Occasional operational procedures explicitly discovered via `devkit playbook search` or retrieved by exact ID via `devkit playbook get`.
   - `package-workflow`: Delivery workflow definitions.
2. **Mechanized Execution Layer**:
   - `governance-rule`: Deterministic invariant verified by `devkit rules check`.
   - `agent-skill`: Tool directory projected to `.agents/skills/`.
   - `agent-subagent`: Native persona configuration.
   - `git-commit-gate`: Commit hook policy.
   - `host-hook`: Native host lifecycle event handler.
3. **Packaging & Selection Layer**:
   - Bundle presets and project configuration (`.devkit/config.toml`).

See `ARCH-08-2-resource-taxonomy` for detailed asset schemas.

---

## 4. Exit Code Conventions

`devkit` commands adhere to the checker convention of `grep`, `diff`, and `ruff`:

| Exit Code | `ExitCode` Constant | Meaning | Examples |
| :---: | :--- | :--- | :--- |
| **`0`** | `OK` | Success; clean run | `rules check` with 0 violations; `sync` complete. |
| **`1`** | `FINDINGS` | The command ran successfully but found negative issues | Rule violations remain; `sync --check` detected drift; gate refused commit. |
| **`2`** | `ERROR` | Command could not execute | Malformed arguments; unreadable configuration; unexpected exception. |

---

## 5. Platform Constraints

`devkit` is designed exclusively for POSIX platforms (**macOS and Linux**):
- Relies on POSIX `fcntl` file locking.
- Uses POSIX permission modes and executable bits.
- Generates `/bin/sh` shell hook wrappers.
- Emits standard LF line endings across all managed outputs.
