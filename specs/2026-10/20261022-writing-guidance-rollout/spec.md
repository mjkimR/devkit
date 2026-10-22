---
id: SPEC-writing-guidance-rollout
title: Roll out agent-asset-writing to bundle assets
summary: "Rewrites the remaining bundle skills, playbooks, instructions and role contracts under the agent-asset-writing guidance, verified by a content-preservation review of each changed document."
status: completed
created: 2026-10-22
related_capabilities:
  - CAP-HARN-agent-guidance
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-writing-guidance-rollout] Roll out agent-asset-writing to bundle assets

## 1. Problem Statement & Motivation

`SPEC-writing-guidance-layers` added the `agent-asset-writing` instruction and piloted it on `spec-plan`. The other
bundle skills, playbooks, instructions and role contracts still stack a condition, an action, an exception and a
cross-reference in one sentence. This spec rewrites them to the guidance. Misbehavior found in later use is corrected
then, so verification is a review of each changed document for preserved content, not a behavior comparison.

## 2. User Stories

- **US-1**: As an agent loading a devkit skill, playbook, instruction or role contract, I want directive sentences
  with the condition first, so that I act on each line without unpacking it.

## 3. Non-Goals

1. **Scope Excluded**: Behavior comparison by dry runs (the acceptance check `FB-writing-guidance-rollout` proposed).
   - **Rationale**: Decided at intent: later use corrects misbehavior; the content-preservation review guards
     against dropped constraints.
2. **Scope Excluded**: Changes to frontmatter (`name`, `description`, role `hosts`), Jinja logic, commands, codes,
   paths or IDs.
3. **Scope Excluded**: Files already written under the guidance: `spec-plan`, the `skill-authoring` playbook and the
   instructions `document-writing`, `decision-writing`, `capability-writing`, `story-writing`,
   `architecture-writing`, `agent-asset-writing`.
4. **Scope Excluded**: `guides/`, `docs/`, rule guides (`rules/*/guide.md`) and templates.
5. **Scope Excluded**: Mechanical style rules (`FB-writing-style-rules`).

## 4. Assumptions

- A file that already follows `agent-asset-writing` stays unchanged; a rewrite changes only sentences the guidance
  covers.
- Phrases asserted by tests, headings targeted by `#anchor` links and every Jinja block stay verbatim.
- Rewriting runs in parallel batches with disjoint write boundaries in this worktree; the Host checks each batch's
  diff against its boundary.

## 5. Source Feedback

- `FB-writing-guidance-rollout`: resolved by this spec, with the behavior comparison replaced by the
  content-preservation review (Non-Goal 1).

## 6. Acceptance Criteria & Behavioral Contracts

### [AC-01] Every in-scope asset follows the guidance
- **Given** the 67 in-scope Markdown files under `packages/*/src/**/bundle/{skills,playbooks,instructions,subagents}/`
- **When** a reviewer reads each changed file against `agent-asset-writing`
- **Then** no stacked multi-clause directive, hedged directive or emphatic capitals outside defined keywords remains,
  and the review envelope lists no such finding

### [AC-02] No content is lost
- **Given** the base and changed version of each file
- **When** a reviewer compares them
- **Then** every constraint, command, flag, code, path, ID, link, condition and completion criterion of the base
  version is present in the changed version, and frontmatter and Jinja blocks are byte-identical

### [AC-03] Checks pass
- **Given** the change complete
- **When** `uv run devkit sync`, `just test-affected`, `just lint-check` and `devkit rules check --ci --base <base>`
  run
- **Then** all exit `0`; every skill and playbook file stays within 12288 bytes and the `spec` and `spec-delegate`
  skills within 11776 bytes
