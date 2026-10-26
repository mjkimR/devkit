---
id: ARCH-01-introduction-and-goals
title: Introduction & Goals
summary: "Mission, goals, quality requirements, and agent-first design philosophy of devkit."
status: active
created_at: 2026-10-17
---

# [ARCH-01-introduction-and-goals] Introduction and Goals

- **arc42**: §1 Introduction and Goals
- Building blocks: `ARCH-05-1-containers`, `ARCH-05-2-components`. Cross-cutting: `ARCH-08-cross-cutting`.

---

## 1. Mission

`devkit` is a developer tooling suite for engineering teams collaborating with AI coding agents (such as Codex, Claude Code, and Antigravity). It ships one CLI (`devkit`) in two Python distributions released in lockstep: `devkit-dist` (asset distribution with the shared foundation, host hooks, search and the `devkit` executable) and `devkit-agt` (the developer harness: rules, workflows, gates, worktrees, generated files, integration and compact output, mounted under the same executable), which depends on it; a repository that only deploys agent assets installs `devkit-dist` alone. Its `devkit.advisory` library is also published on its own as `devkit-advisory`, the standard-library-only runtime dependency of repositories that report advisories from their own code, and its command-line boundary as `devkit-cli`, the runtime dependency of other repositories' click tools that agents run.

Its primary mission is to provide an **agent-first developer harness** that unifies:
1. **Asset Distribution & Guidance Delivery (`devkit_dist.features.distribution`)**: packaging, versioning, selecting, and synchronizing agent guidance, instructions, playbooks, native skills, subagent roles, and bundle assets across repositories.
2. **Repository Governance & Deterministic Verification (`devkit_agt.features.rules`)**: static invariants, Markdown link integrity, and code hygiene with automated repairs and convergence rechecks.
3. **Delivery Workflow Orchestration (`devkit_agt.features.workflow`)**: multi-stage delivery procedures declared as data, tracking activity progress, envelopes, and human decisions.
4. **Commit Gates (`devkit_agt.features.gate`)**: pluggable commit-time policy enforcement through static wrappers and layered configuration.
5. **Agent Advisories (`devkit.advisory`)**: the Agent Advisory Protocol reporting structured errors, warnings, and notices with machine-actionable directives.
6. **Agent-First CLI Toolkit (`devkit_cli`, `cli-tool` bundle)**: the output contract of `devkit` commands for any click tool, with an opt-in structure guide and rules for such tools (`CAP-CLI-agent-cli-toolkit`).
7. **Compact Command Output (`devkit_agt.features.compact`)**: bounded command execution for agents with full logs saved to disk (`devkit run`).
8. **Task Worktrees (`devkit_agt.features.worktree`)**: activity branches and isolated Git worktrees for safe parallel task execution.
9. **Document Search (`devkit_dist.features.search`)**: lexical, dense, and hybrid ranking over project documents.
10. **Host & Scoped Integration (`devkit_dist.features.host`, `devkit_agt.features.integration`)**: lifecycle observation, native hooks, and MCP service endpoints.

---

## 2. Agent-First Design Philosophy

`devkit`'s primary consumer is an AI coding agent running commands through tool calls and acting deterministically on results:

- **stdout is the result**: one-line `[KIND: ...]` sentinels or a single JSON object under `--format json`. No terminal colors, emojis, progress bars, or decorative output.
- **stderr is for advisories**: Agent Advisory Protocol blocks (`[ERROR]`, `[WARN]`, `[NOTICE]`) with stable `UPPER_SNAKE` codes and explicit `[ACTION]` directives.
- **Codes over messages**: callers branch on codes and modes, never on free-form message text.
- **Bounded context**: default output carries only what affects the agent's next step.
- **Libraries never print**: output is managed strictly through `devkit_dist.adapters.cli`.

---

## 3. Quality Goals

1. **Deterministic Execution**: Given identical inputs and repository state, commands return identical exit codes and sentinels.
2. **Transactional Safety**: Synchronization operations (`devkit sync`) write atomically or roll back cleanly without leaving corrupted intermediate states.
3. **Strict Layering**: Lower foundation modules never import or depend on higher orchestrators.
4. **Platform Compatibility**: POSIX-compliant execution across macOS and Linux with zero external daemon requirements.

## Repository roadmap

The repository owns its roadmap under `docs/roadmap/`. A global MS milestone document cites the mission or quality goal it advances, states an observable exit condition and holds no work list. Only direct proposal anchors declare milestone membership; SPEC milestone metadata is ignored and handoff does not carry it. Backlog maintains explicit lifecycle decisions and spec-next recommends queued work (`ADR-roadmap-and-milestones`). External trackers and autohub integration are outside this roadmap contract.
