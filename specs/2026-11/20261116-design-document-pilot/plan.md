---
id: PLAN-design-document-pilot
spec: SPEC-design-document-pilot
---

# Technical Plan: `SPEC-design-document-pilot`

## 1. Constitution & Invariant Review

No invariant change or ADR is required. Retain `CAP-DIST-sync-and-transactions`, `CAP-DIST-content-packages`,
`CAP-DIST-manifest-spec`, `CAP-DIST-agent-projections` and `CAP-DIST-workspace-ownership` as contract owners.
`ARCH-05-2-components`, `ARCH-05-4-distribution-components` and `ARCH-06-runtime-view` keep structure/runtime ownership.
The glossary keeps terminology. `PROP-design-document-pilot-target` defines unchanged Living Spec targets.

## 2. Architecture Overview & Impact

Only the unit directory and dated pilot materials change. No package, feature, layer, test tier or feature edge is added.
Use ordinary Markdown and full existing document IDs rather than inventing a role kind. This preserves independently
readable entry/detail examples while representation remains an evidence-based foundation decision.

AC-01: domain-entry.md, design-entry.md, replacement-detail.md, operations-entry.md and statement-ledger.md.
AC-02: independent bounded trials plus existing lexical lookup, resolve/refs and relative-link checks in evidence.md.
AC-03: counterfactual maintenance table in evidence.md.
AC-04: three independent recommendation dimensions per role in evidence.md.

Source claims are checked against transaction.py symbols `_ordered`, `missing_directories`, `require_writable`,
`apply_changes` and `recover_locked`. The detail explains the mechanism; the entry only orients and leads there.
Operations classifies symptoms and links existing owners without making a parallel procedure.

## 6. Verification & Test Plan

Before edits run `uv run devkit sync --check`. Run workflow next, rules for affected documents and unit,
`uv run devkit rules check --ci --base main`, envelope validation and `git diff --check`.
Run `just test-affected --base 8f89c95d01e6f1e28ac94f48d92104ce9cb53ffc`, retaining its full-mode fallback.
There is no production or frontend change, so lint, type and frontend checks have no applicable changed inputs.

An independent reader receives only each protocol's starting question and entry/contract. It records all opened
sources and usability observations. A nested code reviewer repeats the trials and audits source ownership.
A nested reconcile reviewer checks the unchanged contract classification and retained evidence. Roles read absolute
paths in this worktree; prompt boundaries and returned read reports substitute for native isolation enforcement.
No recovery runs. Normal-state conclusions are documented-state analysis, distinct from this worktree's actual
read-only sync readiness check. No timing benchmark is relevant.
