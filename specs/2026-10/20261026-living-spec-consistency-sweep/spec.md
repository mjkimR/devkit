---
id: SPEC-living-spec-consistency-sweep
title: Living Spec consistency sweep
summary: Resolves contradictions, stale names and duplicate citations that the first handbook refresh found across capabilities, use cases, architecture and the glossary, aligning each with shipped behavior.
status: in-progress
created: 2026-10-26
related_capabilities:
  - CAP-DLV-workflow-orchestration
  - CAP-DLV-project-policy
  - CAP-DLV-delivery-workflows
  - CAP-DLV-proposal-incubation
  - CAP-INT-mcp-services
  - CAP-MCP-runtime-registration
  - CAP-HOST-lifecycle-observation
  - CAP-VIEW-repository-viewer
  - CAP-WT-task-worktrees
  - CAP-DOCS-document-lookup
  - CAP-GEN-tracked-artifacts
  - CAP-DIST-sync-and-transactions
  - CAP-DIST-content-packages
  - CAP-ADV-agent-advisory-protocol
  - CAP-GOV-rules-engine
related_usecases:
  - UC-incubate-and-hand-off-a-proposal
workflow: sdd-spec-feature
---

# [SPEC-living-spec-consistency-sweep] Living Spec consistency sweep

## 1. Problem Statement & Motivation

The writers of the v0.1.4 handbook read the Living Spec and found 22 places where documents contradict each other or
the shipped code (`materials/findings.md`). An agent that follows one side of a contradiction acts on behavior that
does not exist: it expects a policy value that is refused, an MCP tool that is not registered, a CLI subcommand that
is not there, or an error code that is never raised. Each item is settled by what ships: the code, the CLI help and
behavior, the workflow definitions (`devkit workflow show <id>`) and the accepted ADRs. Superseded ADRs are history.

## 2. User Stories

- **US-1**: As an agent reading a capability, use case, architecture document or the glossary, I want each statement
  to match shipped behavior, so that I act on what the CLI and code do. `UC-incubate-and-hand-off-a-proposal` is the
  one use case whose text changes.
- **US-2**: As an agent reading CLI help, I want the help text of `devkit worktree`, `devkit spec list` and the
  distribution commands' `-w/--workspace-root` to state what the command does.
- **US-3**: As an agent classifying a review-refactor work item, I want the `spec` bundle's classification criteria
  to name that case.

## 3. Non-Goals

1. **Scope Excluded**: changing behavior to match a document. Only documentation-like code changes: CLI help and
   docstring text, and the `spec` bundle's classification guidance.
2. **Scope Excluded**: editing ADRs under `docs/decisions/`; the citing documents change instead.
3. **Scope Excluded**: restructuring documents beyond what an item needs; item 15 may reorder its two paragraphs.
4. **Scope Excluded**: deciding a behavior defect or a design question an item reveals; it is recorded as feedback in
   this Unit's `feedback/`.
5. **Scope Excluded**: unhiding `devkit rules phases` and `devkit rules test`. They were hidden in the same change
   that hid the workflow authoring commands, which `CAP-DLV-cli-and-output` documents as deliberate, so the
   documents state the hiding instead.
6. **Scope Excluded**: the handbook (`handbook/`), which a later refresh regenerates from the Living Spec.

## 4. Acceptance Criteria & Behavioral Contracts

Each criterion covers one item group of `materials/findings.md` and is verified by reading the named documents at the
final head, and for help-text items by running the CLI.

### [AC-01] Delivery documents match the shipped gates, stages and lifecycle CLI (items 1-6)
- **Given** the shipped workflow definitions (`devkit workflow show sdd-spec-feature` and `sdd-proposal`), the spec
  policy reader (`check_approvals`) and `devkit spec proposal accept|handoff --help`
- **When** a reader reads `CAP-DLV-workflow-orchestration`, `CAP-DLV-project-policy`, `CAP-DLV-delivery-workflows`,
  `CAP-DLV-proposal-incubation`, `UC-incubate-and-hand-off-a-proposal` and `CAP-INT-mcp-services`
- **Then** the documents state that the workflow engine accepts `ask`, `auto` or `off`, while the spec definitions and
  `devkit spec policy` accept only `ask` or `auto` for `plan-intent`, `plan-accept`, `proposal-handoff` and
  `dev-integration`, with `WORKFLOW_GATE_POLICY` from workflow commands for a definition gate and
  `SPEC_CONFIG_INVALID` from spec commands
- **And** `proposal-handoff` is described as a policy boundary of `devkit spec proposal accept|handoff` that no
  workflow stage declares
- **And** `accept` without `--mode` never commits, merges or hands off, and with `--mode` composes those effects
- **And** no document says that acceptance publishes a shared artifact report or that a native MCP handoff form exists
- **And** no capability names specrig as a current component, and the stage names listed match shipped stage IDs

### [AC-02] Integration, MCP, host and viewer documents match the registered tools and hosts (items 7-11)
- **Given** `packages/devkit-dist/src/devkit_dist/features/shared/mcp.py`, `registrations.py` and
  `devkit mcp setup --help`
- **When** a reader reads `CAP-INT-mcp-services`, `CAP-MCP-runtime-registration`, `CAP-HOST-lifecycle-observation`,
  `docs/development/reference/host.md` and `CAP-VIEW-repository-viewer`
- **Then** no document calls the superseded `ADR-local-and-pull-request-integration` authoritative
- **And** the shared artifact MCP tools are `shared_put` (bounded write), `shared_get` and `shared_list` (read-only)
- **And** project MCP registration names Codex, Claude Code and Antigravity, and the `devkit mcp setup` reference
  lists `--host codex|claude|antigravity`
- **And** `CAP-HOST-lifecycle-observation` numbers its sections consecutively
- **And** the viewer's approval boundary names no unregistered MCP tools

### [AC-03] Worktree, document, generated and distribution contracts match the CLI (items 12-16)
- **Given** `devkit worktree --help`, `devkit spec list --help`, `devkit generated list --help` and
  `devkit sync --help`
- **When** a reader reads `CAP-WT-task-worktrees`, the `devkit worktree` CLI module docstring,
  `CAP-DOCS-document-lookup`, `CAP-GEN-tracked-artifacts`, `CAP-DIST-sync-and-transactions` and
  `CAP-MCP-runtime-registration`
- **Then** the stale-branch report is `devkit worktree status --stale` everywhere, with no `stale` subcommand
- **And** `milestone` is a `KIND` of `devkit spec list` in the capability and in `devkit spec list --help`
- **And** `CAP-GEN-tracked-artifacts` documents `devkit generated list` with its output line
- **And** `CAP-DIST-sync-and-transactions` introduces the receipt before its `host_hooks` field, and states locked
  synchronization before its host-hook exception
- **And** `devkit sync --registrations-only` has its command contract in `CAP-MCP-runtime-registration` and a pointer
  from `CAP-DIST-sync-and-transactions`

### [AC-04] Governance and advisory documents match the rules CLI (items 17-18)
- **Given** the error `devkit rules check` raises for `[rules.phase_overrides] RULE-x = "linter"`, and
  `devkit rules --help`
- **When** a reader reads `CAP-ADV-agent-advisory-protocol`, `CAP-GOV-rules-engine` and
  `docs/development/reference/rules.md`
- **Then** the advisory example is that error as the CLI prints it, naming `rules.phase_overrides` and `hygiene`
- **And** the documents state that `phases` and `test` are callable but hidden from `devkit rules --help`

### [AC-05] Citations and the glossary are consistent (items 19-20)
- **Given** the duplicate citations in `ARCH-01-introduction-and-goals`, `ARCH-05-1-containers`,
  `CAP-VIEW-repository-viewer`, `CAP-DIST-content-packages` and `CAP-DLV-project-policy`
- **When** a reader reads those passages and `docs/glossary.md`
- **Then** no passage cites the same ID twice in a row or as "refined by" itself, and `ADR-viewer` is paired with
  `ADR-viewer-working-tree`, which supersedes it
- **And** the glossary defines **Host** with its owner and what it excludes

### [AC-06] The two source feedback items are fixed and resolved (items 21-22)
- **Given** `FB-workspace-root-help-resolution-order` and `FB-classification-maintenance-playbook-case`
- **When** a reader runs `devkit sync --help` and `devkit playbook search --help`, and reads the `spec` skill's
  `references/classification.md`
- **Then** every distribution command describes `-w/--workspace-root` with the shared default text
  ("the devkit project containing the current directory"), not the reversed resolution order
- **And** the classification criteria name the review-refactor work item case: `overall-refactor` when its edited
  source files span more than one feature or module, otherwise `feature` at its own depth
- **And** both feedback files have `status: resolved` and a `Disposition` section

## 5. Assumptions

- Item 1: the generic engine's `ask`/`auto`/`off` in `CAP-DLV-workflow-orchestration` §3 is correct for the engine;
  the contradiction is in the spec-level documents, which change.
- Item 6: the glossary `Stage` entry lists `intent`, `specify`, `build-verify` and `handoff`, all shipped stage IDs
  (`handoff` is a stage of `sdd-proposal`), so the glossary stays; only `CAP-DLV-workflow-orchestration` changes.
- Item 16: `CAP-MCP-runtime-registration` and `CAP-WT-task-worktrees` already describe `--registrations-only`;
  only its command contract and a pointer from the sync capability are missing.
- Item 19: each duplicate came from consolidating several ADRs into one that keeps the old IDs as aliases, so the
  duplicate is dropped; only `ADR-viewer` has a distinct second ID to restore.
- Item 5: the same stale name in `CAP-WT-task-worktrees` §7 is fixed with item 5, as the same finding in a second
  capability.
- Item 3: the same native-MCP acceptance and handoff claim in `CAP-HARN-agent-guidance`, `ARCH-05-1-containers`
  (devkit-spec's dependencies, which have no `devkit-mcp`) and `ARCH-05-2-components` is fixed with item 3, because
  it contradicts the same Host-authorized CLI contract.
- Item 19: two more duplicate citations of the same origin (`CAP-HARN-agent-guidance`, `CAP-DLV-delivery-workflows`)
  are dropped with item 19.
- Item 12: the package docstring of `devkit_agt.features.worktree` (`__init__.py`) carries the same `stale`
  subcommand as `cli.py` and is fixed with it.

## 6. Source feedback

- `FB-workspace-root-help-resolution-order` (`specs/2026-10/20261026-review-refactor/feedback/`): item 21.
- `FB-classification-maintenance-playbook-case` (`specs/2026-10/20261026-review-refactor/feedback/`): item 22.
