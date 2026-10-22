---
id: PROP-frontmatter-syntax-governance
title: YAML frontmatter syntax governance and autofix for libyaml fast path
summary: Enforce standard YAML frontmatter formatting via a governance rule (RULE-frontmatter-syntax) with autofix for BOM and tabs, ensuring documents satisfy the libyaml fast path while preserving the runtime Python fallback.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/capabilities/governance/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-frontmatter-syntax-governance] YAML frontmatter syntax governance and autofix for libyaml fast path

## 1. Background & Hypothesis

The frontmatter parser optimization in `devkit-core` (`commit 2e1744ac`, `commit bffd0222`) introduced a guarded libyaml fast path (`_FastStrictLoader`) delivering a 3.55x parsing speedup across Markdown files. To resolve scanner discrepancies where libyaml accepts inputs that the Python scanner rejects (such as tabs, ambiguous question marks, hashes, and U+FEFF byte-order marks), `frontmatter.py` routes headers containing `\t?#\ufeff` to the strict Python `SafeLoader`.

While retaining the Python `SafeLoader` as a runtime fallback ensures resilience and superior error diagnostics, authoring practices across the repository are unguided:
- Documents containing non-standard formatting (e.g. BOM headers, indentation tabs, unquoted scalar values containing `?` or `#`) silently fall back to the slower Python loader without notifying authors or agents.
- Forcing a hard runtime refusal or guessing quote boundaries at load time creates unacceptable runtime risk and syntax corruption.

**Hypothesis**: By introducing a deterministic project governance rule (`RULE-frontmatter-syntax`) with automated repair (`just rules-fix`) for mechanical formatting (BOM removal, indentation tab-to-space expansion) and actionable diagnostic directives (`[ACTION]`) for unquoted scalars, repository documents will consistently satisfy libyaml fast-path requirements at commit time while preserving the runtime Python fallback as a zero-risk safety net.

## 2. Technical Spike Questions

- **Q1 (Autofix boundaries)**: Which syntax issues can be deterministically auto-repaired without an AST parser?
  - *Answer*: Stripping leading `\ufeff` (BOM) and normalizing leading indentation tabs (`\t` -> two spaces) are completely safe text-level operations. Unquoted scalar values containing `?` or `#` require semantic understanding of intended values and must emit an actionable linter error directing the author or agent to add quotes (`"..."`), avoiding regex-based quote guessing.
- **Q2 (Rule placement & phase)**: Where should the governance rule reside and what phase should it target?
  - *Answer*: Reside under `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/frontmatter_syntax/` (or `packages/devkit/src/devkit_agt/features/rules/services/builtins/`), running in the `linter` phase with `error` severity so it participates in `devkit rules check` and the pre-commit gate (`--staged`).
- **Q3 (Runtime independence)**: Does this rule require changes to `devkit_core.core.frontmatter`?
  - *Answer*: No. `frontmatter.py` keeps its dual-loader architecture and `_PYTHON_SYNTAX` guard untouched. The governance rule operates upstream during editing, commit gates, and CI checks.

## 3. Proposed Design & Impact

- **Governance Rule (`RULE-frontmatter-syntax`)**:
  - Scans Markdown frontmatter blocks across `docs/`, `specs/`, and bundle guides.
  - Emits violations when encountering:
    1. Byte-order marks (`\ufeff`) in document headers (autofixable).
    2. Tab characters (`\t`) in indentation (autofixable).
    3. Unquoted plain scalar strings containing characters that trigger Python fallback (`?`, `#`) when quotes would allow unambiguous fast-path classification.
    4. General YAML parsing errors (duplicate keys, unclosed mappings).
- **Autofix Integration (`rules-fix`)**:
  - Invoking `devkit rules fix` or `just rules-fix` automatically cleans BOMs and normalizes tabs across modified files without user intervention.
- **Diagnostic Directives**:
  - For non-autofixable violations (e.g., unquoted `title: Why devkit?`), output a deterministic Agent Advisory Protocol block:
    ```text
    [ERROR] RULE-frontmatter-syntax: unquoted scalar contains '?' at line 3, col 8
    [ACTION] Wrap the scalar in quotes: title: "Why devkit?"
    ```
- **Impact**:
  - Guarantees that virtually 100% of committed repository documentation remains on the 3.55x faster libyaml parsing path.
  - Zero risk of document corruption from speculative regex quote rewriting.
  - Zero breakage for external or unmanaged documents due to the intact runtime Python fallback.

## 4. Lifecycle & Retirement Criteria

- Acceptance criteria:
  - `RULE-frontmatter-syntax` is implemented with unit and rule tests under its rule directory.
  - `just rules-check` passes cleanly across all existing repository documentation.
  - `just rules-fix` successfully auto-repairs synthetic test fixtures with BOMs and tabs.
  - Commit gate catches invalid frontmatter syntax on staged files.
