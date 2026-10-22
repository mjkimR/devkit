---
id: PLAN-writing-guidance-rollout
spec: SPEC-writing-guidance-rollout
---

# Technical Plan: `SPEC-writing-guidance-rollout` Roll out agent-asset-writing to bundle assets

## 1. Constitution & Invariant Review

None. The change rewrites text inside the existing assets; asset kinds, presets, frontmatter and Jinja logic stay
(`ADR-layered-writing-guidance` placed the guidance; this spec applies it).

## 2. Architecture Overview & Impact

- **Impacted Components**: 67 Markdown sources in seven batches with disjoint write boundaries (tasks.md).
- **Projections**: `uv run devkit sync` refreshes `.devkit/installation.json` and the projected copies.
- **Living Spec**: none expected; capabilities describe asset contracts, which do not change. `reconcile.md` records
  the no-impact reasoning.
- **New Dependencies**: None.

## 3. Rewrite Contract (per batch)

Each batch rewriter:

1. Reads `packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md`.
2. Before editing a file, finds the tests that read it (`rg -l <file stem or skill name> packages/*/tests scripts`
   and the rule and bundle tests) and the `#anchor` links into it (`rg -n "<file name>#" packages docs guides`).
3. Rewrites only sentences the guidance covers; keeps frontmatter, Jinja blocks, asserted phrases, anchored
   headings, commands, codes, paths, IDs and links verbatim; drops no constraint.
4. Runs the tests that read its files and reports per file what changed and anything it could not rewrite safely.

## 4. Verification & Test Plan

- Host: compare each batch's changed paths with its boundary; run `uv run devkit sync`, `just test-affected`,
  `just lint-check`, `uv run devkit rules check --ci --base <base>` (AC-03).
- `code-reviewer` (medium, mandatory first pass): base-versus-changed comparison per file for AC-01 and AC-02.
