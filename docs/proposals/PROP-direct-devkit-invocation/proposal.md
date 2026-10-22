---
id: PROP-direct-devkit-invocation
title: Invoke the installed devkit directly on frequent paths
summary: "Has agent guidance and hooks call the project's installed devkit executable on frequent paths instead of uv run, removing a fixed per-call overhead while keeping uv run where environment synchronization is needed."
status: rejected                     # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: harness/
priority: low                          # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/distribution/services/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/guidance/
    - packages/devkit/src/devkit_agt/bundles/harness/bundle/guidance/
    - docs/capabilities/harness/
    - docs/capabilities/distribution/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-direct-devkit-invocation] Invoke the installed devkit directly on frequent paths

## 1. Background & Hypothesis

`uv run devkit --version` took about 93 ms against 53-63 ms for `.venv/bin/devkit --version` in the draft's
measurement (main at 4dbf9c4b, macOS, Python 3.12): `uv run` verifies, and when needed synchronizes, the project
environment before each call. Agent guidance names `uv run devkit ...` on frequent paths: the managed `AGENTS.md`
block (`get-context`, `devkit run`) and the generated `devkit-workflow` entry skill (`workflow next`, `envelope`).

Hypothesis: calling the project's installed executable directly on frequent paths saves the fixed overhead, while
`uv run` stays where environment synchronization is the point (setup, `devkit sync` after a dependency change).

## 2. Technical Spike Questions

- **Q1**: Which invocation is portable across consumer repositories and hosts (a `.venv/bin/devkit` path, an
  activated environment, `uv run --no-sync`, an executable recorded at sync), and what does each do when the
  environment is missing or stale?
  - **Finding**: only `uv run devkit` runs the locked devkit from any directory and syncs it after a lock change.
    `.venv/bin/devkit` fails with exit 127 from a subdirectory or without an environment; it and
    `uv run --no-sync` silently run an older devkit after `git pull`, a branch switch or a new worktree without
    setup. No direct form can raise a devkit advisory for a missing environment, because devkit is not running. An
    activated environment depends on host shell state (this run's shell carried another project's `VIRTUAL_ENV`);
    a recorded executable is machine-specific and cannot appear in the committed `AGENTS.md` block. Windows is out
    of scope (`ARCH-03-context`).
- **Q2**: Which paths are frequent enough to matter, and which must keep `uv run`?
  - **Finding**: frequent: the `AGENTS.md` block (6 mentions) and the `devkit-workflow` entry skill (12); setup or
    rare: the `devkit` bundle instructions, installation guides, playbooks and rule remediation text. Hooks pay no
    `uv run` cost today: commit gates run the worktree's `.venv` interpreter and Codex host hooks run `devkit` from
    `PATH`.
  - **Finding**: the measured overhead is 18-23 ms over `.venv/bin/devkit` and 9-14 ms over `uv run --no-sync`,
    2-14 % of a 120-450 ms frequent command (`get-context`, `workflow next`, `spec resolve`), about 1 s across a
    50-call agent session.

Evidence: `materials/invocation-forms.md`.

## 3. Proposed Design & Impact

Recommended (`PADR-keep-uv-run-as-the-agent-facing-devkit-invocation`, pending the user's answer to `q1`): keep
`uv run devkit` as the agent-facing form on every path and change no guidance or hook. The saving does not justify
running a devkit that disagrees with the lock or failing outside the repository root in consumer repositories.
Under this outcome the proposal produces no Development change; the Host decides its close.

If the user chooses a direct form instead, Development changes only the frequent emitters:

- The managed `AGENTS.md` block lines (`guidance_block.py`, `bundles/guidance.py`, the `spec-pointer` and
  `run-pointer` guidance) and the generated `devkit-workflow` entry skill (`workflow_skill.py`) name the chosen form,
  with an instruction to run `uv sync` when the executable is missing.
- Setup and maintenance guidance (`devkit` bundle instructions, `guides/`, playbooks) and hooks stay unchanged.
- `CAP-HARN-agent-guidance` and the distribution capability that defines the entry skill state the form; generator
  tests pin the emitted text; the per-call overhead is measured again.

Acceptance outcomes (direct form only):

- The managed `AGENTS.md` block and the `devkit-workflow` entry skill name the chosen form and the `uv sync`
  recovery; no other guidance, guide or hook changes.
- Generator tests assert the emitted form; `just test-affected` and `devkit rules check` pass.
- A re-measurement of `get-context spec` and `workflow next` records the saving in the reconcile record.

### Non-Goals

- Changing Git or host hook commands; they do not use `uv run`.
- Normalizing the bare `devkit ...` mentions in bundle text.
- Windows support.

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
