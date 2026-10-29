---
generated: true
---
# Glossary

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated page -->
The terms of devkit as its documents use them, from the Living Spec glossary.

### 1. Distribution and Packaging

| Term | Definition | Owner |
| :--- | :--- | :--- |
| **devkit bundle** | devkit's unit of distributable agent assets, declared in `bundle.toml`. Bundles ship instructions, playbooks, rules, workflows, subagents, gates, and guidance fragments. | `CAP-DIST-manifest-spec` |
| **Subagent model level** | Distribution-owned preset (minimal, compact, standard, deep or maximal) selecting native model family and supported effort for a common role contract, with inherit as the default; excludes delivery activity-effort and runtime model routing. | `CAP-DIST-agent-projections` |
| **Preset** | A named asset selection of a bundle (e.g. `core`, `default`). | `CAP-DIST-manifest-spec` |
| **Managed files** | Pristine synchronized copies under `.devkit/managed/<bundle>/`; never edited by hand. | `CAP-DIST-workspace-ownership` |
| **Projections** | Native agent files projected into `.agents/skills/`, `.claude/skills/`, `.codex/skills/`, etc. | `CAP-DIST-agent-projections` |
| **Receipt** | `.devkit/installation.json`: records every deployed file, checksum, and origin bundle in one transaction. | `CAP-DIST-sync-and-transactions` |
| **Project override** | Local adaptation of an upstream asset placed under `.devkit/overrides/`, tracked against an upstream baseline. | `CAP-DIST-workspace-ownership` |
| **Alias** | A previous or alternate identifier of a document (`aliases` in its frontmatter) or of a playbook (a previous asset ID in its header's `aliases`). It resolves to the canonical document or playbook and counts as a declaration; it is identity, not a reference. | `CAP-DOCS-document-model` |

### 2. Governance and Verification

| Term | Definition | Owner |
| :--- | :--- | :--- |
| **Governance rule** | A deterministic invariant evaluated by `devkit rules check` with optional automatic repair (`devkit rules fix`). | `CAP-GOV-rules-engine` |
| **Per-file rule facts** | Immutable rule-owned syntax extracted from one logical Python path; persistent reuse is keyed by cached source bytes, explicit extraction context and executing-source fingerprint. Excludes shared AST objects and cross-file judgments. | `CAP-GOV-rule-authoring` |
| **Rule phase** | Execution category of a rule: `syntax`, `hygiene`, `linter`, `contract`. | `CAP-GOV-rules-engine` |
| **Snapshot run** | Rule execution against an exact Git snapshot: staged tree (`devkit rules check --staged`) or base commit comparison (`--ci --base <ref>`). | `CAP-GOV-rules-engine` |
| **Steering document** | An ID-free Markdown file directly in `docs/steering/`, one per project-wide background topic (the glossary, product, style), with only `title` and `summary` frontmatter; `devkit get-context docs` lists every one in each agent context and an agent reads its body when a decision concerns its summary. Excludes contracts (capabilities, use cases, architecture, decisions) and evidence (materials). | `ADR-steering-documents-directory` |
| **UX document** | A Living Spec document (`UX-<slug>`, kind `ux`) describing one interface element a person sees and operates, a screen, modal or panel, by purpose, content tree, states and interactions; use case steps cite it and each interaction names the step it serves. Excludes visual style and the wireframe medium. | `ADR-ux-screen-documents` |
| **UX object register** | The steering file `docs/steering/ux-objects.md` listing each object's representations and calls to action per role, for the objects the use cases with UX documents touch; created with a project's first UX document, never seeded. | `ADR-ux-screen-documents` |

### 3. Delivery Workflows and Tasks

| Term | Definition | Owner |
| :--- | :--- | :--- |
| **Development approach** | Shared project choice of SDD or incubation, independent of installed packages and selected assets; excludes clone-local execution environment and publication authority. | `CAP-DIST-sync-and-transactions` |
| **Incubation current context** | Mutable current product facts used to resume incubation: goal, retained choices versus assumptions, run/check evidence, uncertainty and next useful action; excludes SDD Units/envelopes, transcripts and immutable experiment history. | `CAP-DLV-idea-incubation` |
| **Work scope observation** | Invocation-local evidence from one snapshot, pinned branch tree or accessible worktree, with task attribution, provenance and missing layers; excludes a persistent registry revision or write authority. | `CAP-COLL-work-scope-registry` |
| **Workflow** | A multi-stage delivery procedure declared as data (`kind = "workflow"`): ordered stages with entry/exit checks, approval gates, and returns. | `CAP-DLV-workflow-orchestration` |
| **Unit** | A directory driven by a workflow, tracked by its anchor file (e.g. `spec.md` or `proposal.md`). | `CAP-DLV-workflow-orchestration` |
| **Stage** | A discrete step in a workflow (`intent`, `specify`, `build-verify`, `handoff`); evaluates whether checks are met. | `CAP-DLV-workflow-definitions` |
| **Segment** | The execution span during which a Unit is bound to a single workflow definition; reset upon workflow handoff. | `CAP-DLV-workflow-orchestration` |
| **Gate** | A workflow stage that pauses for an explicit human or automated decision. | `CAP-DLV-workflow-definitions` |
| **Envelope** | A structured YAML file recording the findings, questions, problems, or resolution of a workflow stage. | `CAP-DLV-workflow-envelopes` |
| **Shared artifact** | Immutable expiring report content shared by exact generation reference; excludes scope coordination and approval authority. | `CAP-COLL-shared-artifacts` |
| **Task worktree** | An isolated Git worktree created on an activity branch (`plan-<slug>`, `dev-<slug>`) for parallel task execution. | `CAP-WT-task-worktrees` |
| **Source feedback** | Explicit FB IDs whose observations and received scope an authorized task addresses; recorded in the proposal/spec body or session agreement. Excludes unrelated observations captured during the task. | `ADR-feedback-lifecycle` |
| **Direct acceptance** | The user's `plan-accept` of an eligible draft given on sight in Backlog and recorded on the base checkout, without a Planning branch or run. Excludes any `activity-effort`, Planning `worker` envelope or acceptance without the user. | `ADR-proposal-acceptance` |
| **Session reclassification** | Deleting a queued draft without PADRs on the user's explicit decision at pickup, preserving its open feedback, to do the work as a `session` task under a new slug; the one lowering of depth besides a proposal's handoff. Excludes proposals in review or accepted and spec Units. | `ADR-delivery-classification` |
| **Feedback promotion** | Closing feedback by routing an observation to identified follow-up work, which owns subsequent tracking. Excludes any claim that the observation has been fixed or verified. | `ADR-feedback-lifecycle` |
| **Feedback resolution** | Closing an explicitly linked open observation through a direct verified fix without promotion, in a session or spec task. Excludes promoted sources, handoff alone, partial fixes and any claim of integration. | `ADR-feedback-lifecycle` |

### 4. Gates, Host and Integration

| Term | Definition | Owner |
| :--- | :--- | :--- |
| **Host** | The main agent of the user's local session: it drives Backlog, inline Planning, worktree preparation, worker delegation and local integration, and carries the user's conversational decisions to Host-authorized CLI operations. Excludes delegated workers and subagent roles, and the agent host product (Codex, Claude Code, Antigravity) that `--host` and host hooks name. | `ARCH-04-1-ecosystem-boundaries` |
| **Commit gate** | Git hook wrapper installed by `devkit gate install` enforcing policy prior to commit. | `CAP-GATE-commit-gates` |
| **Compact output** | Bounded command execution for AI agents (`devkit run`), capturing full logs to disk while streaming bounded summaries to stdout. | `CAP-CMP-bounded-execution` |
| **Agent advisory** | Structured error, warning, or notice adhering to the Agent Advisory Protocol (`[ERROR]`, `[WARN]`, `[NOTICE]`) with machine-actionable directives. | `CAP-ADV-agent-advisory-protocol` |
| **Host hook** | Mechanized execution resource registering an installed service at a native host event (`kind = "hook"`). | `CAP-HOST-lifecycle-observation` |
| **Scoped CLI integration** | The Host-authorized `devkit integration prepare` and `integrate` commands that land committed work through the local or pull-request route after revalidating policy, readiness, source identity and cleanup scope; no MCP tool performs integration. | `CAP-INT-mcp-services` |
<!-- /handbook:generated -->
