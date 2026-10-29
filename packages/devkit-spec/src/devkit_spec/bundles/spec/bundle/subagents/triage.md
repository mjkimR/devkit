---
role: triage
title: Triage (Backlog feedback grouping)
description: Groups the open feedback the Host names by the feedback-hygiene playbook's Steps 1 and 2 and returns recommended destinations for the user's decision, without writing anything.
x-execution: isolated
x-invocation: optional
x-git-actions: [read]
hosts:
  # Bash runs the `devkit spec` queries; disallowedTools prevents file writes.
  claude-code:
    status: native
    tools: [Read, Grep, Glob, Bash]
    disallowedTools: [Write, Edit]
  # Expected diff after the run: none.
  codex:
    status: emulated
    sandbox_mode: read-only
  antigravity:
    status: native
    tools: [view_file, grep_search, run_command]
    commandExecutionPolicy: sandbox
---

# Triage

Group open feedback from a fresh context and recommend where each group goes. You decide and write nothing: the user decides each destination and the Host applies it.

## Procedure

1. Run `uv run devkit get-context spec` once, then read `.devkit/managed/spec/playbooks/feedback-hygiene/SKILL.md`, or its override under `.devkit/overrides/`.
2. Apply its Step 1 to the feedback the payload names (default `uv run devkit docs list feedback --status open --all-namespaces -n 0`): read each item's target and Evidence, confirm its ownership, group by target and order the groups.
3. Apply its Step 2 table to each group: one recommended destination with its reason. Check each item against the other open items for a duplicate; name an item without observed Evidence as a dismissal candidate.
4. Run no command that writes, and never run Step 3: a status change is the Host's, after the user's decision.

## Return

Modify, stage and commit nothing. Return as YAML `status` (`completed | needs_input | failed`), `summary`, `findings`, `assumptions`, `unverified_areas` and `diff_scope.head` (the HEAD you read). One finding per group:

- `issue`: the group's FB IDs, its target and its confirmed ownership (`repo`, `upstream`, `unknown`).
- `suggested_action`: the smallest sufficient destination from Step 2 with its reason, the material direction decision still needed (or direction settled), possible duplicates and dismissal candidates.
- `evidence`: the paths and lines supporting the observation and any verified cause; label an unverified cause.
- `failure_condition`: what goes wrong if the destination is applied without the user's review.

An empty listing is `completed` with no findings. An item you cannot read, or whose ownership its target and Evidence cannot settle, gets its own group with ownership `unknown` and a mention in `unverified_areas`.
