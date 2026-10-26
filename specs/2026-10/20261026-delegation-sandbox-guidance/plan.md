---
id: PLAN-delegation-sandbox-guidance
spec: SPEC-delegation-sandbox-guidance
---

# Technical Plan: `SPEC-delegation-sandbox-guidance` Delegation scope and sandbox guidance fixes

## 1. Constitution & Invariant Review

None. The changes add guidance inside existing contracts. The `code-reviewer` stays `x-git-actions: [read]` and its
Claude Code projection keeps `disallowedTools: [Write, Edit]`, because the probe exemption covers only an ignored path
and the shell already reaches it; `test_every_other_role_stays_read_only` keeps holding. The Codex rule of the
`development-worker` (per-operation approval, no host-setting change) is the route `worktree.md` cites, so no new
sandbox policy is introduced.

## 2. Architecture Overview & Impact

All edits are in `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`:

| AC | File | Change |
| --- | --- | --- |
| AC-01 | `skills/spec-delegate/references/payload.md` | Workers bullet: a `_Boundary:` with a selected bundle source adds the tracked files `devkit sync --check` lists to the write scope |
| AC-01, AC-02 | `subagents/development-worker.md.jinja` | Procedure: run `devkit sync` after a selected-bundle edit and commit its tracked outputs; produce a before/after baseline only as the spec names it, never by checkout, and report a base measurement it cannot take |
| AC-02 | `skills/spec/references/planning.md` | Step 5 bullet: a before/after outcome names a worker-producible baseline or states that the Host measures the base |
| AC-03 | `subagents/code-reviewer.md` | Probe tests under the ignored path the payload names, deleted before return; never the unit's tests |
| AC-03 | `skills/spec-delegate/references/payload.md` | `code-reviewer` row "Also pass": an ignored probe path inside the worktree |
| AC-04 | `skills/spec/references/worktree.md.jinja` | A "Sandboxed sessions" paragraph in §1: fixed path, `--workspace-root` semantics, shared Git directory, permitted route |
| AC-05 | the five source feedback files | `status: resolved` and a `Disposition` section |

After the bundle edit, `uv run devkit sync` refreshes the ignored `.devkit/managed/` copy and any tracked receipt it
writes; those tracked files are committed with the change.

Living Spec: `CAP-DLV-delivery-workflows` states the role table (`code-reviewer` "Writes" cell) and the worker and
approval paragraphs; reconcile updates those sentences only.

## 3. Verification & Test Plan

- New `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py` pins the phrases of
  AC-01 to AC-04 in the rendered documents (`spec_support.bundle_text.text`, `local` and `cloud`).
- AC-05: `rg -n "^status: resolved|SPEC-delegation-sandbox-guidance"` on the five feedback files shows both lines in
  each, and `uv run devkit rules check` reports no violation for them. A package test does not read `specs/`,
  because feedback files are repository history, not bundle content.
- `test_bundle_budgets.py` keeps every edited skill document under its budget.
- `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`, `just rules-check`.
