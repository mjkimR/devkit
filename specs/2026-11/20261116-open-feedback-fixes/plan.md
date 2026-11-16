---
id: PLAN-open-feedback-fixes
spec: SPEC-open-feedback-fixes
---

# Technical Plan: Fixes for four open feedback items

## 1. Constitution & Invariant Review

No architecture `MUST` changes; no ADR is needed. `CAP-DIST-sync-and-transactions` stays the owner of the journal
algorithm, `CAP-DOCS-document-lookup` already states workspace-relative output, and `CAP-DLV-proposal-lifecycle`
gains one clause naming the excluded proposal path. No feature edge, layer or test tier changes.

## 2. Architecture Overview & Impact

- **Runtime view**: move the journal step out of the per-asset loop to before it ("Write journal: pending changes &
  previous state"), leaving the loop with only the file writes. Design, domain and operations impact: none; the
  runtime view is architecture context and the capability keeps the algorithm.
- **Scout**: add `WebSearch` to the Claude Code `tools`; `devkit sync` refreshes the projected agent and the
  installation receipt.
- **Handoff**: in `handoff_proposal`, build a copy of the proposal frontmatter whose `boundaries.owns` omits the
  proposal's own path and pass it to `_scope_notes` and `spec_files`. The original `meta` keeps serving validation,
  namespace, summary and effort reads.
- **Resolve help**: the click docstring becomes "Print the workspace-relative path of each document ID."

### Choice: exact match on the proposal path

The proposal path is `proposal_rel`'s directory for a bundle (`docs/proposals/PROP-<slug>`) or the file itself.
An entry equal to it, or to the directory with a trailing `/`, is dropped; `PROP-<slug>-other/` shares the prefix
and must stay, so no prefix match. When `owns` empties, the existing `target_area` fallback applies.

## 3. Component & Interface Design

```python
# handoff.py
def _without_own_path(meta: dict[str, Any], proposal_rel: str, is_bundle: bool) -> dict[str, Any]: ...
```

## 6. Verification & Test Plan

- AC-01: read-through of the edited diagram against `apply_changes`.
- AC-02: `test_support_roles_shell_access` asserts `WebSearch` and `WebFetch` and no `Write`/`Edit`.
- AC-03, AC-04: `test_carries_the_proposal_body` adds the own directory and a prefix sibling to `owns`.
- AC-05: a `CliRunner` `--help` test in `test_cli_documents.py`.
- Checks: `devkit rules check --ci --base main`, `just lint-check`, `just check`, `just test-affected --base
  a627466bb`.
