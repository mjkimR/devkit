# Glossary

The ubiquitous terms of devkit as its documents, commands and bundles use them. Each row gives the `Term`, its
`Definition`, the `Owner` (the capability or decision that defines the term's contract), the rejected synonyms to
`Avoid` and the matching `Code identifiers` (fields, types and paths). Search synonyms for these terms live in
[glossary.yaml](glossary.yaml).

## 1. Distribution and Packaging

| Term | Definition | Owner | Avoid | Code identifiers |
| :--- | :--- | :--- | :--- | :--- |
| **devkit bundle** | devkit's unit of distributable agent assets, declared in `bundle.toml`. Bundles ship instructions, playbooks, rules, workflows, subagents, gates, and guidance fragments. | `CAP-DIST-manifest-spec` |  | `bundle.toml` |
| **Preset** | A named asset selection of a bundle (e.g. `core`, `default`). | `CAP-DIST-manifest-spec` |  |  |
| **Managed files** | Pristine synchronized copies under `.devkit/managed/<bundle>/`; never edited by hand. | `CAP-DIST-workspace-ownership` |  | `.devkit/managed/<bundle>/` |
| **Projections** | Native agent files projected into `.agents/skills/`, `.claude/skills/`, `.codex/skills/`, etc. | `CAP-DIST-agent-projections` |  | `.agents/skills/`, `.claude/skills/`, `.codex/skills/` |
| **Receipt** | `.devkit/installation.json`: records every deployed file, checksum, and origin bundle in one transaction. | `CAP-DIST-sync-and-transactions` |  | `.devkit/installation.json` |
| **Project override** | Local adaptation of an upstream asset placed under `.devkit/overrides/`, tracked against an upstream baseline. | `CAP-DIST-workspace-ownership` |  | `.devkit/overrides/` |
| **Alias** | A previous or alternate identifier of a document (`aliases` in its frontmatter) or of a playbook (a previous asset ID in its header's `aliases`). It resolves to the canonical document or playbook and counts as a declaration; it is identity, not a reference. | `CAP-DOCS-document-model` | search keyword | `aliases`, `DocumentIndex.canonical` |

## 2. Governance and Verification

| Term | Definition | Owner | Avoid | Code identifiers |
| :--- | :--- | :--- | :--- | :--- |
| **Governance rule** | A deterministic invariant evaluated by `devkit rules check` with optional automatic repair (`devkit rules fix`). | `CAP-GOV-rules-engine` |  |  |
| **Per-file rule facts** | Immutable rule-owned syntax extracted from one logical Python path; persistent reuse is keyed by cached source bytes, explicit extraction context and executing-source fingerprint. Excludes shared AST objects and cross-file judgments. | `CAP-GOV-rule-authoring` |  | `FileFactsDescriptor`, `WorkspaceCache.get_file_facts` |
| **Rule phase** | Execution category of a rule: `syntax`, `hygiene`, `linter`, `contract`. | `CAP-GOV-rules-engine` |  |  |
| **Snapshot run** | Rule execution against an exact Git snapshot: staged tree (`devkit rules check --staged`) or base commit comparison (`--ci --base <ref>`). | `CAP-GOV-rules-engine` |  |  |

## 3. Delivery Workflows and Tasks

| Term | Definition | Owner | Avoid | Code identifiers |
| :--- | :--- | :--- | :--- | :--- |
| **Workflow** | A multi-stage delivery procedure declared as data (`kind = "workflow"`): ordered stages with entry/exit checks, approval gates, and returns. | `CAP-DLV-workflow-orchestration` |  | `kind = "workflow"` |
| **Unit** | A directory driven by a workflow, tracked by its anchor file (e.g. `spec.md` or `proposal.md`). | `CAP-DLV-workflow-orchestration` |  |  |
| **Stage** | A discrete step in a workflow (`intent`, `specify`, `build-verify`, `handoff`); evaluates whether checks are met. | `CAP-DLV-workflow-definitions` |  |  |
| **Segment** | The execution span during which a Unit is bound to a single workflow definition; reset upon workflow handoff. | `CAP-DLV-workflow-orchestration` |  |  |
| **Gate** | A workflow stage that pauses for an explicit human or automated decision. | `CAP-DLV-workflow-definitions` |  |  |
| **Envelope** | A structured YAML file recording the findings, questions, problems, or resolution of a workflow stage. | `CAP-DLV-workflow-envelopes` |  |  |
| **Shared artifact** | Immutable expiring report content shared by exact generation reference; excludes scope coordination and approval authority. | `CAP-COLL-shared-artifacts` | shared state, coordination record | `devkit_dist.features.shared`, `Artifact` |
| **Task worktree** | An isolated Git worktree created on an activity branch (`plan-<slug>`, `dev-<slug>`) for parallel task execution. | `CAP-WT-task-worktrees` |  |  |
| **Source feedback** | Explicit FB IDs whose observations and received scope an authorized task addresses; recorded in the proposal/spec body or session agreement. Excludes unrelated observations captured during the task. | `ADR-feedback-lifecycle` |  | `Source feedback`, `FB-<name>` |
| **Direct acceptance** | The user's `plan-accept` of an eligible draft given on sight in Backlog and recorded on the base checkout, without a Planning branch or run. Excludes any `activity-effort`, Planning `worker` envelope or acceptance without the user. | `ADR-proposal-acceptance` | skipping Planning by effort | `devkit spec proposal accept --direct`, `form=direct\|repair` |
| **Session reclassification** | Deleting a queued draft without PADRs on the user's explicit decision at pickup, preserving its open feedback, to do the work as a `session` task under a new slug; the one lowering of depth besides a proposal's handoff. Excludes proposals in review or accepted and spec Units. | `ADR-delivery-classification` |  | `depth proposal -> session` commit message |
| **Feedback promotion** | Closing feedback by routing an observation to identified follow-up work, which owns subsequent tracking. Excludes any claim that the observation has been fixed or verified. | `ADR-feedback-lifecycle` |  | feedback `status: promoted`, `Disposition` |
| **Feedback resolution** | Closing an explicitly linked open observation through a direct verified fix without promotion, in a session or spec task. Excludes promoted sources, handoff alone, partial fixes and any claim of integration. | `ADR-feedback-lifecycle` |  | feedback `status: resolved`, `Disposition` |

## 4. Gates, Host and Integration

| Term | Definition | Owner | Avoid | Code identifiers |
| :--- | :--- | :--- | :--- | :--- |
| **Commit gate** | Git hook wrapper installed by `devkit gate install` enforcing policy prior to commit. | `CAP-GATE-commit-gates` |  |  |
| **Compact output** | Bounded command execution for AI agents (`devkit run`), capturing full logs to disk while streaming bounded summaries to stdout. | `CAP-CMP-bounded-execution` |  |  |
| **Agent advisory** | Structured error, warning, or notice adhering to the Agent Advisory Protocol (`[ERROR]`, `[WARN]`, `[NOTICE]`) with machine-actionable directives. | `CAP-ADV-agent-advisory-protocol` |  |  |
| **Host hook** | Mechanized execution resource registering an installed service at a native host event (`kind = "hook"`). | `CAP-HOST-lifecycle-observation` |  | `kind = "hook"` |
| **Integration MCP** | Scoped Model Context Protocol server exposing devkit integration services to coding agents. | `CAP-INT-mcp-services` |  |  |
