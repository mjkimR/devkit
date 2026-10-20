---
id: PADR-separate-shared-configuration-from-local-execution-and-rendering
title: Separate shared configuration from local execution and rendering
summary: Use validated local preferences, explicit workspace execution constraints and a separate ignored render overlay while preserving shared approval policy and committed receipt verification.
proposal: PROP-local-config-execution-environment
status: draft
created_at: 2026-10-20
---

# [PADR-separate-shared-configuration-from-local-execution-and-rendering] Separate shared configuration from local execution and rendering

- **Status**: Draft
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

Current template variables change committed receipt hashes and can change tracked guidance. Ignored files do not
travel with worktrees. A local environment label must constrain execution without granting approval authority.
The evidence is in the proposal's `materials/configuration-evidence.md`; this decision is proposed, not accepted.

## 2. Decision Drivers

Personal preferences must not leak into shared files. Shared policy and snapshot verification must stay reproducible.
Worktree creation must supply its initial preferences before setup; each created checkout owns subsequent changes.
A base-anchored service must identify its configuration workspace independently of its runtime root.
The foundation belongs to devkit-dist and cannot import the harness, following `ADR-dist-foundation-ownership`.

## 3. Considered Options

| Option | Benefit | Failure or cost |
| --- | --- | --- |
| Merge every local key into existing config/receipt | Small implementation | Enables governance weakening and personal committed receipt/guidance changes |
| Copy local config before worktree setup | Simple, explicit snapshot with independent worktrees | Base edits do not propagate; raw Git worktrees need explicit provisioning |
| Runtime-only language command with no rendering | No second ledger | Existing templated skill/native projection does not reflect the preference without a new per-reply lookup contract |
| Restricted local overlay and ignored render ledger | Preserves personal rendering and shared verification | Requires explicit runtime reader routing, stale-ledger checks and restricted asset kinds |
| Live retained-base preference inheritance | No copying | Couples independent checkouts and needs missing-base and multi-source restriction rules |

## 4. Decision Outcome

Recommend restricted local overlays and an ignored render ledger, with creation-time worktree copying.
The user-directed copy semantics settle the worktree choice: copy before setup/first sync, then independent ownership. The proposal defines the exact eligibility, errors, precedence, transaction behavior and
acceptance matrix. Keep `read_project_config` shared-only; add `read_effective_config` and the independent
explicit-root execution resolver in core. Local config cannot alter governance or topology. Shared receipt bytes
remain canonical; a transient ledger permits only ignored human-readable asset bytes to differ. The local ledger
is never an authority for executable rule/workflow/gate files or snapshot policy.

New devkit worktrees receive the local file from the base caller before setup. Attach preserves an existing
worktree's choice. No live inheritance, process cloud latch or global environment override is introduced. A retained
MCP service binds a configuration workspace separately from its runtime and integration roots. Environment is a
runtime constraint, never an approval grant; MCP owns enforcement and rechecks the bound workspace.

## 5. Consequences

Distribution runtime readers must deliberately select effective rendering; engines and Git snapshots remain on the
canonical receipt. Existing ignore-file seed-only behavior changes only for the managed local-config entry. Local
preferences require ignored native destinations; refusal preserves tracked state. Existing config writers retain
shared destinations. The standalone MCP proposal consumes the resolver and owns its request context and approval
logic, without copying config parsing. Medium Development includes independent review and reconcile verification.
