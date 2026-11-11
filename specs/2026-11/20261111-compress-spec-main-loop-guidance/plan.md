---
id: PLAN-compress-spec-main-loop-guidance
spec: SPEC-compress-spec-main-loop-guidance
---

# Technical Plan: `SPEC-compress-spec-main-loop-guidance` Compress the spec guidance of the main development loop

## 1. Architecture Overview & Impact
- Target Area: capabilities/delivery/ (agent guidance only; the delivery contract does not change).
- Sources: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`; projections follow through `devkit sync`.

## 2. Component Breakdown & Interface Contracts

Three parallel review-and-edit groups in isolated checkouts, each applying the second-pass brief (Policy 1 with
the one-line-essence rule for late refusals, Policy 2 with one-level references):
- **A, entry and constitution**: `AGENTS.md.jinja`, `skills/spec/SKILL.md.jinja`, `references/{envelope,
  worker-records,completion.md.jinja}`.
- **B, workflow and stage skills**: `workflows/sdd-spec-feature.md`, `skills/spec-{specify,plan,tasks,review,
  sync}/SKILL.md`.
- **C, delegation and integration**: `subagents/development-worker.md.jinja`, `skills/spec-{delegate,
  integrate}/SKILL.md*`, `skills/spec-orchestrate/SKILL.md.jinja`, `skills/spec-orchestrate/references/
  isolated-execution.md`.

The Host compares each returned file set, verifies every Policy 1 claim against the cited code path, and commits
one document per commit (with any receiving reference and the tests that follow it), then one `devkit sync`
commit.

### Planned Boundaries:
- `capabilities/delivery/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`, its pinned guidance tests and the projections
  `devkit sync` writes.

### Excluded Boundaries:
- `docs/decisions/`
- Code, CLI messages and package versions.

## 3. Verification & Test Plan
- `uv run devkit rules check --ci --base <base>`
- `just test-affected --base <base>`
- `uv run devkit sync --check`
- Per-document byte report and Policy 1 evidence in the final change report.
