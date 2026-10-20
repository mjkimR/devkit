---
id: PROP-worker-range-validation
title: One-command worker result inspection for orchestrated units
summary: "Bundles existing worker-result checks and reviewer diff information into one command, using the Host-supplied scope and leaving interpretation to the agent without adding an approval gate."
status: reviewing                      # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: delivery/
priority: critical                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - delivery/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-orchestrate/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-worker-range-validation] One-command worker result inspection for orchestrated units

## 1. Background & Hypothesis

- **Observed on 2026-10-19**: the first sustained local-orchestrated run (three Development units and two Planning
  units in parallel) worked, but the Host repeated the same checks by hand for every returned range: ancestry from
  the last accepted head, every changed path inside the write scope, a clean worktree, the cumulative rules check
  and `devkit workflow next`. The write scope exists only in the delegation payload, so each scope check was a
  hand-written pattern.
- **Reviewer input**: `FB-reconcile-reviewer-no-diff-list` identifies missing changed-file information in the
  read-only reviewer's payload. The same Git inspection can supply it.
- **Hypothesis**: A small command that collects existing checks and diff information saves repeated shell work. It
  provides evidence for the main agent; it does not become another approval gate or coordination system.

## 2. Planning Scope

Implement a thin wrapper in `devkit-spec` around the checks the Host already performs. Use an explicit starting
head, returned head and Host-supplied write scope. Reuse an existing delegation record when available; do not make
workers author a new mandatory committed scope record or extend the envelope schema just for this helper.

Planning settles only the CLI arguments, concise result fields and reuse of existing check APIs. Prefer existing
conventions without introducing a separate scope authority or validation lifecycle.

## 3. Proposed Design & Impact

- One invocation reports ancestry, changed paths, paths outside the supplied scope, worktree status, existing
  envelope validation, cumulative rules results and `devkit workflow next`. Include the compared heads and changed
  paths in information the agent can pass to a read-only reviewer.
- Default output carries the result and actionable findings; structured output is one JSON object. Preserve the
  stable codes and actions of existing checks and report checks that could not run distinctly from negative results.
- Scope mismatches and worktree observations are information for the main agent to assess. The command MUST NOT
  add an approval request, workflow gate, integration refusal, mandatory scope registration or override option.
  Existing rules, delegation write boundaries and approval gates retain their current meaning; the helper neither
  weakens them nor adds a new blocking prerequisite to accepting a worker result.
- The agent decides how to act on findings and runs any corrective commands. The helper does not modify files,
  merge the base, refresh environments, run `devkit sync`, retry operations or automatically enlarge write scope.
- Affected: a small `devkit spec` command, `spec-delegate` and `spec-orchestrate` guidance, reviewer payload guidance,
  and `CAP-DLV-delivery-workflows`. No new worker envelope fields are required.

**Non-Goals**: automatic scope derivation or expansion, link-repair ownership inference, base-drift detection or
merging, worktree environment refresh, new approval gates, and automatic enforcement of helper findings.

**Separate feedback**: `FB-worker-scope-misses-link-repairs` and `FB-handoff-premise-drift-unreported` remain open for
scope construction and handoff drift respectively. Neither is required for this command and neither is implemented
by this proposal.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr worker-range-validation "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff worker-range-validation`.
- On rejection: `status: rejected` with the user's reason in the commit message.
