---
id: SPEC-feedback-quick-fixes
title: Feedback Quick Fixes
summary: 'Resolves four small open feedback items: a visible warning for unsupported presentation languages, accepting the agt module name, naming nested-role skill paths in worker payloads, and clarifying that a condition-free spike completion is not Planning evidence.'
status: completed
created: 2026-10-22
namespace: global
related_capabilities:
  - CAP-DIST-sync-and-transactions
  - CAP-DIST-workspace-ownership
  - CAP-INT-mcp-services
  - CAP-DLV-proposal-incubation
  - CAP-DLV-delivery-workflows
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-quick-fixes] Feedback Quick Fixes

## 1. Problem Statement & Motivation

Four small open feedback items each cost an agent a wasted run or a silent wrong result:

- An unsupported `[presentation] language` value (for example `korean`) is accepted by configuration validation
  and silently resolves to `en`; `devkit sync` succeeds and renders English into every projection without any
  code or directive (`FB-presentation-language-silent-fallback`).
- `just lint agt` and `just check agt` refuse the natural short name of `devkit-agt`, and the refusal lists only
  full names, so a delegated verification payload cannot learn the accepted short names before running
  (`FB-module-name-discovery-before-checks`).
- A nested role started by a worker loaded its startup skill (`response-style`) from the base checkout, outside
  the assigned worktree, because the payload named only the worktree, not its skill and instruction paths
  (`FB-nested-role-skill-read-scope`).
- `devkit workflow next` lists the condition-free `spike` stage under `[DONE]` on a fresh draft, which a Planning
  worker can misread as evidence that the review already ran (`FB-planning-stage-skips-unrecorded-spike`).

## 2. User Stories

- **US-1**: As an agent configuring a workspace, I want the English fallback for an unsupported presentation
  language reported as a warning with a stable code and the accepted values, so that I learn of it and fix the value
  instead of shipping English projections unknowingly.
- **US-2**: As a delegated verifier, I want `agt` accepted and the short names listed in the refusal, so that one
  failed call is enough to correct a module name.
- **US-3**: As a Host delegating to a worker, I want the payload guidance to name the worktree's skill and
  instruction paths for nested roles, so that no nested role reads operational instructions from the base checkout.
- **US-4**: As a Planning executor, I want the guide to say that a condition-free `spike` completion is not Planning
  evidence, so that I run the review the Planning effort requires.

## 3. Non-Goals

1. **Scope Excluded**: Language aliases (`korean`, `english`) or locale inference for `[presentation] language`.
   - **Rationale**: A visible warning naming the accepted values is enough.
2. **Scope Excluded**: Changing the `sdd-proposal` workflow definition or the `devkit workflow next` evaluation of
   `spike`.
   - **Rationale**: An engine change needs separate review because low-effort Planning has no challenger.
   - **When to Reconsider**: When the wording-only clarification proves insufficient in a recorded Planning run.
3. **Scope Excluded**: Refusing unsupported presentation languages, or editing ADRs.
   - **Rationale**: `ADR-shared-language-preference-with-bounded-approval-content` decides the English fallback; the
     user decision for this unit keeps it and only makes it visible.
4. **Scope Excluded**: Any other open feedback item, refactor, or change under
   `packages/devkit-spec/src/devkit_spec/features/`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Unsupported presentation language falls back to English visibly
- **Given** a workspace whose shared `.devkit/config.toml` or local `.devkit/config.local.toml` sets
  `[presentation] language` to a string other than exactly `auto`, `en` or `ko` (for example `korean`, `KO`, `ja`
  or the empty string)
- **When** `devkit sync`, `devkit status` or `devkit config show --effective` runs
- **Then** the value resolves to `en` with `fallback=true` as the ADR decides, and the result carries, under
  `notices`, one `PRESENTATION_LANGUAGE_UNSUPPORTED` advisory at level `WARNING` per configuration file whose value
  fell back; it names the file and the value, its `[FIX]` names the accepted values `auto`, `en` and `ko` and the file
  to edit, it is printed on stderr in text mode, and it changes no exit code (`0`) except under `--strict` (`1`)

### [AC-02] Supported presentation languages resolve unchanged
- **Given** `[presentation] language` set to `auto`, `en` or `ko`, or absent
- **When** `resolve_language(root)` runs
- **Then** `resolved` equals the requested value (`auto` when absent) and `fallback` is `false`

### [AC-03] Module short names include agt and are discoverable
- **Given** the workspace module scripts
- **When** `just lint agt` or `just check agt` runs, or an unknown module name is passed
- **Then** `agt` resolves to `devkit-agt`, and the unknown-module refusal (exit 1) prints a line starting
  `Module short names:` that lists every short name with its full name, from the same table `resolve_module` uses

### [AC-04] Nested-role payloads name the worktree's skill and instruction paths
- **Given** the `spec-delegate` payload reference and the `development-worker` and `planning-worker` contracts
- **When** a Host or worker builds a nested-role payload for an assigned worktree
- **Then** the text requires naming the assigned worktree's absolute startup skill and instruction paths
  (for example its `response-style` skill) and states that a read from another checkout is reported as a boundary
  exception

### [AC-05] Condition-free spike completion is not Planning evidence
- **Given** the `spec` skill's Planning reference and the `spec-next` workflow-signals reference
- **When** `devkit workflow next` lists `spike` under `[DONE]` for a proposal
- **Then** both texts state that this completion is not Planning evidence and that the support-role envelopes
  recorded at `spike` are; no workflow definition or engine code changes

## 5. Source feedback

The unit resolves exactly these open direct-fix sources:

- `FB-presentation-language-silent-fallback` (AC-01, AC-02)
- `FB-module-name-discovery-before-checks` (AC-03)
- `FB-nested-role-skill-read-scope` (AC-04)
- `FB-planning-stage-skips-unrecorded-spike` (AC-05)

## 6. Assumptions

1. The warning has its own code, `PRESENTATION_LANGUAGE_UNSUPPORTED`, not `CONFIG_INVALID`: it is a returned
   `WARNING` of a successful command, never a refusal, and agents branch on codes.
2. Values are matched exactly; `KO` and the empty string fall back and warn like any other unsupported string.
3. `ADR-shared-language-preference-with-bounded-approval-content` decides an English fallback for unsupported strings.
   The user decision recorded with the return to build-verify (`decisions/02-return-build-verify.yaml`) keeps that
   behavior and requires only that it be visible, so this unit conforms to the ADR and no superseding ADR is needed.
   The earlier `CONFIG_INVALID` refusal is withdrawn.
4. Both the effective value (personal rendering) and the shared-only value (canonical tracked output) are checked;
   a file whose value fell back is reported once. The `fallback` field of the resolved language is set again.
