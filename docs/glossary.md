# Glossary

The ubiquitous terms of devkit as its documents, commands and bundles use them. Where a capability or decision defines a
term's contract, the last column names it. Search synonyms for these terms live in [glossary.yaml](glossary.yaml).

## 1. Distribution and Packaging

| Term | Definition | Defined in |
| :--- | :--- | :--- |
| **devkit bundle** | devkit's unit of distributable agent assets, declared in `bundle.toml`. Bundles ship instructions, playbooks, rules, workflows, subagents, gates, and guidance fragments. | `CAP-DIST-manifest-spec` |
| **Preset** | A named asset selection of a bundle (e.g. `core`, `default`). | `CAP-DIST-manifest-spec` |
| **Managed files** | Pristine synchronized copies under `.devkit/managed/<bundle>/`; never edited by hand. | `CAP-DIST-workspace-ownership` |
| **Projections** | Native agent files projected into `.agents/skills/`, `.claude/skills/`, `.codex/skills/`, etc. | `CAP-DIST-agent-projections` |
| **Receipt** | `.devkit/installation.json`: records every deployed file, checksum, and origin bundle in one transaction. | `CAP-DIST-sync-and-transactions` |
| **Project override** | Local adaptation of an upstream asset placed under `.devkit/overrides/`, tracked against an upstream baseline. | `CAP-DIST-workspace-ownership` |

## 2. Governance and Verification

| Term | Definition | Defined in |
| :--- | :--- | :--- |
| **Governance rule** | A deterministic invariant evaluated by `devkit rules check` with optional automatic repair (`devkit rules fix`). | `CAP-GOV-rules-engine` |
| **Rule phase** | Execution category of a rule: `syntax`, `hygiene`, `linter`, `contract`. | `CAP-GOV-rules-engine` |
| **Snapshot run** | Rule execution against an exact Git snapshot: staged tree (`devkit rules check --staged`) or base commit comparison (`--ci --base <ref>`). | `CAP-GOV-rules-engine` |

## 3. Delivery Workflows and Tasks

| Term | Definition | Defined in |
| :--- | :--- | :--- |
| **Workflow** | A multi-stage delivery procedure declared as data (`kind = "workflow"`): ordered stages with entry/exit checks, approval gates, and returns. | `CAP-DLV-workflow-orchestration` |
| **Unit** | A directory driven by a workflow, tracked by its anchor file (e.g. `spec.md` or `proposal.md`). | `CAP-DLV-workflow-orchestration` |
| **Stage** | A discrete step in a workflow (`intent`, `specify`, `build-verify`, `handoff`); evaluates whether checks are met. | `CAP-DLV-workflow-definitions` |
| **Gate** | A workflow stage that pauses for an explicit human or automated decision. | `CAP-DLV-workflow-definitions` |
| **Envelope** | A structured YAML file recording the findings, questions, problems, or resolution of a workflow stage. | `CAP-DLV-workflow-envelopes` |
| **Task worktree** | An isolated Git worktree created on an activity branch (`plan-<slug>`, `dev-<slug>`) for parallel task execution. | `CAP-WT-task-worktrees` |

## 4. Gates, Host and Integration

| Term | Definition | Defined in |
| :--- | :--- | :--- |
| **Commit gate** | Git hook wrapper installed by `devkit gate install` enforcing policy prior to commit. | `CAP-GATE-commit-gates` |
| **Compact output** | Bounded command execution for AI agents (`devkit run`), capturing full logs to disk while streaming bounded summaries to stdout. | `CAP-CMP-bounded-execution` |
| **Agent advisory** | Structured error, warning, or notice adhering to the Agent Advisory Protocol (`[ERROR]`, `[WARN]`, `[NOTICE]`) with machine-actionable directives. | `CAP-ADV-protocol` |
| **Host hook** | Mechanized execution resource registering an installed service at a native host event (`kind = "hook"`). | `CAP-HOST-lifecycle` |
| **Integration MCP** | Scoped Model Context Protocol server exposing devkit integration services to coding agents. | `CAP-INT-mcp-services` |
