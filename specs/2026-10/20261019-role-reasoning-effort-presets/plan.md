---
id: PLAN-role-reasoning-effort-presets
spec: SPEC-role-reasoning-effort-presets
---

# Technical Plan: `SPEC-role-reasoning-effort-presets` Per-role reasoning effort presets

## 1. Constitution & Invariant Review

None. The change follows `ADR-role-effort-presets`. It narrows the model-selection non-goal of
`CAP-DLV-delivery-workflows` exactly as that ADR's consequences state; the ADR is the record that permits it. The
keys used are already in the host allowlists of `CAP-DIST-agent-projections`, so no projection code, schema or layer
changes.

## 2. Architecture Overview & Impact

- **Impacted Components**:
  - `packages/devkit-spec/src/devkit_spec/bundle/subagents/scout.md`, `reconcile-reviewer.md`: `effort: medium`
    under `claude-code`, `model_reasoning_effort: medium` under `codex`.
  - `packages/devkit-spec/src/devkit_spec/bundle/subagents/code-reviewer.md`, `challenger.md`: the same keys at
    `high`; the `challenger` comment "Choose a high-reasoning model at invocation time, not in the contract." becomes
    one that names the preset and leaves the model to the runtime.
  - `planning-worker.md`, `development-worker.md`: unchanged.
  - `packages/devkit-spec/tests/test_role_contracts.py`: one table `EFFORT_PRESETS` mapping each role to its
    `x-model-profile` and expected preset (`None` for the workers), and tests that assert it against every contract
    file in `subagents/`.
  - `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`: §2 model-selection non-goal, §4.6 host keys, role
    table column and the sentence on main-session runs (reconcile target).
  - `.devkit/installation.json`: refreshed by `devkit sync` because the managed contracts' hashes change.
- **New Dependencies**: None.

## 3. Component & Interface Design

### Data Contracts & Types

The test table is the single source the assertions read:

```python
EFFORT_PRESETS: dict[str, tuple[str, str | None]] = {
    "scout": ("light-medium", "medium"),
    "reconcile-reviewer": ("light-medium", "medium"),
    "code-reviewer": ("general-high", "high"),
    "challenger": ("high-reasoning", "high"),
    "planning-worker": ("general-high", None),
    "development-worker": ("general-high", None),
}
```

- Coverage: the set of `subagents/*.md` stems equals the table's keys (both directions fail: a contract without an
  entry, an entry without a contract).
- Per role, through one helper `_preset_violations(role, metadata) -> list[str]`: `x-model-profile` equals the entry's profile; `hosts.claude-code.effort` equals the preset (absent when
  `None`); `hosts.codex.model_reasoning_effort` equals the preset when the `codex` status is not `unsupported`, and
  is absent otherwise; no `antigravity` key contains `effort`; no host block carries `model`.
- Design choice (recommended option, recorded here): the existing `ROLES` tuple stays as the parametrization source
  for the other tests; the new coverage test compares the table against the files on disk, so a new contract fails
  even if `ROLES` is not updated.

## 4. Error Handling & Edge Cases

- **A worker gains a `codex` block other than `unsupported` later**: its preset is `None`, so the test then requires
  the key to be absent, matching the ADR (workers set no preset on any host).
- **A host renames its key**: the allowlist in devkit's distribution rejects unknown keys (`BUNDLE_INVALID`), so
  `devkit sync` fails before a wrong key reaches a projection.

## 5. Verification & Test Plan

- `just test devkit-spec tests/test_role_contracts.py` during development; `just test devkit-spec` once the change
  is complete (AC-01 to AC-04).
- Mutation check for AC-04, automated: the per-role assertions live in one helper that returns the violations for
  a parsed frontmatter; a test feeds it copies of real contracts with a changed profile, a changed preset, a preset
  on a worker, an Antigravity effort key and a `model` key, and asserts each yields a violation. No contract file is
  edited for the check.
- `devkit sync`, then read the projected `.claude/agents/*.md` and `.codex/agents/*.toml` frontmatter and run
  `devkit sync --check` (AC-05).
- `rg` for the challenger comment string (AC-03); read `CAP-DLV-delivery-workflows` §2 and §4.6 (AC-06).
- `just lint-check`, `just check devkit-spec`, `just rules-check`, `devkit rules check --ci --base main`.
