---
id: PROP-exact-playbook-get
title: Exact playbook retrieval for external runners
summary: Add exact bundle/playbook retrieval with effective overrides, source identity and context requirements while defining external ownership of scheduling and execution.
status: reviewing                         # draft | reviewing | accepted | rejected
created_at: 2026-10-21
target_area: capabilities/distribution/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-scheduled-jobs
boundaries:
  owns:
    - packages/devkit-dist/src/devkit/distribution/
    - packages/devkit-dist/tests/
    - docs/capabilities/distribution/
    - docs/architecture/
    - docs/decisions/
    - docs/development/reference/
    - guides/
  excludes:
    - packages/devkit-catalog/
    - packages/devkit/src/devkit/integration/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-exact-playbook-get] Exact playbook retrieval for external runners

## 1. Background & Hypothesis

`MS-scheduled-jobs` requires an exact-ID entrypoint for a caller that already knows which synchronized playbook
to run. Search and candidate selection are unnecessary in that case. `CAP-DIST-context-and-playbooks` remains
the consumption contract; an explicit retrieval operation can provide instructions without executing them or
introducing scheduling into devkit.

## 2. Technical Spike Questions

- Which existing playbook resolver, manifest identity and effective override logic should the exact lookup reuse?
- What result fields and CLI output carry the complete procedure body, canonical source identity and required
  bundle context without duplicating always-loaded instructions?
- Which deterministic codes distinguish malformed identity, unknown bundle/asset, unselected or unsynchronized
  assets and invalid effective content? Which existing semantics should remain unchanged?
- How should an ADR and consumption guidance distinguish retrieval, caller execution and externally scheduled
  explicit invocation while retaining workflow gates and prohibiting unsolicited discovery?

## 3. Proposed Design & Impact

Add `devkit playbook get <bundle>/<playbook>` to the existing distribution-owned command surface. Planning
should settle the exact input grammar and return/error contract, with no fuzzy search or fallback selection.
The command reads synchronized effective content, respects overrides and returns body, source identity and
context-loading requirements. It performs no playbook execution, publication, schedule registration or lazy sync.

An ADR should assign scheduling and execution to external callers, limiting devkit to retrieval and the task
contract. Reflect that boundary in affected architecture, capabilities, quick references and consumption guidance.
No provider-specific integration or live recurring schedule is needed.

Candidate acceptance evidence:

- Given an installed and synchronized selected playbook ID, exact retrieval returns the expected effective body,
  source identity and context requirements without invoking the procedure or searching candidates.
- Given an effective override, the returned content and identity match it; invalid or missing inputs use stable
  codes and actionable directives, with text/JSON and exit-code behavior covered by tests.
- Given an unrelated or unselected asset, lookup does not silently choose another procedure or mutate installation.
- An external caller can follow the documented retrieval contract while execution remains subject to the same
  authorization boundaries; the accepted ADR and guidance state scheduler ownership consistently.

Non-goals: scheduler, daemon, job registry, schedule configuration, dispatch/retry/overlap logic, playbook execution
inside `get`, maintenance asset authoring, durable execution history and unattended approval bypasses.

## 4. Lifecycle & Retirement Criteria

Feature / proposal depth. Planning effort is medium because resolver semantics and the responsibility ADR need
independent challenge; recommended Development effort is medium. The API can be designed and tested independently
of new maintenance assets using existing playbook fixtures. Acceptance and Development start remain separate
user decisions. No milestone status transition is included.
