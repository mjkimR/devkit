---
id: PROP-integration-follow-ups
title: 'Integration follow-ups: auto dispatch, pull request cleanup and host confirmation adapters'
summary: 'Plans the integration extensions deferred by the first local integration release: policy-driven dispatch under dev-integration auto, remote pull request and squash or rebase cleanup, and confirmation adapters for hosts beyond Codex.'
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: integration/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - integration/
    - worktree/
    - delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-integration-follow-ups] Integration follow-ups: auto dispatch, pull request cleanup and host confirmation adapters

## 1. Background & Hypothesis

- **Problem**: `SPEC-hook-driven-integration-cleanup` shipped approval-bound local integration under
  `dev-integration = ask` and deferred three extensions (its Non-Goal 3), each recorded as feedback:
  - no dispatch without an interactive confirmation under `dev-integration = auto` (`FB-auto-integration-dispatch`);
  - no remote push or pull request merge, and `WORKTREE_UNMERGED` after a squash or rebase merge, because the merge
    test is commit ancestry (`FB-pr-remote-and-squash-integration`);
  - native confirmation only through Codex MCP elicitation; other hosts get `INTEGRATION_CONFIRMATION_UNAVAILABLE` and
    the CLI fallback (`FB-multi-host-integration-ergonomics`).
- **Restart condition**: the deferral waited for ask-mode integration to be used in real workflows. Several sessions
  have since completed local integrations through `integration_integrate` with `authority="mcp-elicitation"`.
- **Hypothesis**: The three extensions share the integration service, its confirmation binding and the scoped cleanup,
  so one Planning can settle their common contract and decide whether they are delivered together or split.

## 2. Technical Spike Questions

- **Q1 (Split)**: One spec or several? Which extension comes first, and which depends on another?
- **Q2 (Auto dispatch)**: Which readiness evidence must hold before an `authority="policy-auto"` integration runs
  without a prompt, and how is that authority recorded?
- **Q3 (Remote and pull request)**: How is remote push or pull request merge authority separated from local-only
  integration, and how is a squash or rebase merge verified (recorded pull request state, tree or patch equivalence)
  before the worktree and branch are removed?
- **Q4 (Host adapters)**: Which confirmation surfaces do Claude Code, Antigravity and other hosts offer that keep the
  binding to `request.id` and `(source_sha, target_sha)` and never let the agent approve itself?

## 3. Proposed Design & Impact

- Affected: `devkit.integration` and devkit-spec's integration provider, `devkit worktree finish`, `devkit.host`
  adapters, the `spec-integrate` skill, and `CAP-INT-mcp-services` with the worktree and delivery capabilities.
- Every extension keeps the existing invariants: fail closed, exact scope binding, no network operation without
  explicit authority, and no deletion of unmerged work.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr integration-follow-ups "<title>"`.
- If Planning splits the work: decompose into child drafts with `--decomposed-from PROP-integration-follow-ups`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff integration-follow-ups`.
- On rejection: `status: rejected` with the user's reason in the commit message.
