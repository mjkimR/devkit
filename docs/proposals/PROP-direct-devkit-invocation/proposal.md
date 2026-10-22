---
id: PROP-direct-devkit-invocation
title: Invoke the installed devkit directly on frequent paths
summary: "Has agent guidance and hooks call the project's installed devkit executable on frequent paths instead of uv run, removing a fixed per-call overhead while keeping uv run where environment synchronization is needed."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: harness/
priority: low                          # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/bundles/devkit/
    - docs/capabilities/harness/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-direct-devkit-invocation] Invoke the installed devkit directly on frequent paths

## 1. Background & Hypothesis

`uv run devkit --version` takes about 93 ms against 53-63 ms for `.venv/bin/devkit --version` (Measured on main at 4dbf9c4b (macOS, Python 3.12, this repository: about 820 tracked Python files and 850 Markdown files)): `uv run`
adds about 40 ms per call to verify and synchronize the environment. Bundle guidance and hooks name
`uv run devkit ...` throughout (about 56 mentions in bundle sources), so every frequent agent call pays it.

Hypothesis: calling the project's installed executable directly on frequent, read-mostly paths saves the fixed
overhead, while `uv run` stays where environment synchronization is the point (setup, `devkit sync` after a
dependency change).

## 2. Technical Spike Questions

- **Q1**: Which invocation is portable across consumer repositories and hosts (a `.venv/bin/devkit` path, an
  activated environment, `uv run --no-sync`), and what does each do when the environment is missing or stale?
- **Q2**: Which paths are frequent enough to matter (hooks, `get-context`, `workflow next`, `spec` lookups), and
  which must keep `uv run`?

## 3. Proposed Design & Impact

- Guidance and hook templates use the chosen direct form on the frequent paths and keep `uv run` elsewhere; a stale
  or missing environment still fails with an actionable advisory rather than running stale code.
- The consumer installation guides and smoke checks cover the chosen form. Per-call overhead is measured again.
- Lowest priority of the CLI performance drafts: the saving is fixed per call, while `PROP-rule-shared-python-ast`
  and `PROP-lint-clean-target-scoped-rules` address the multi-second commands.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr direct-devkit-invocation "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept direct-devkit-invocation --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff direct-devkit-invocation.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
