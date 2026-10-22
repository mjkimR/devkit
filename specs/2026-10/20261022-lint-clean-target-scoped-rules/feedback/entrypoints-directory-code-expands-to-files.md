---
id: FB-entrypoints-directory-code-expands-to-files
title: Entrypoints apply cannot write the directory entry the skill recommends
scope: repo
kind: friction
category: docs-mismatch
target: spec-entrypoints skill, devkit spec entrypoints derive --apply --code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-entrypoints-directory-code-expands-to-files] Entrypoints apply cannot write the directory entry the skill recommends

## 1. Friction / Question (friction, question)

- **Context**: Choosing entrypoints for `CAP-GOV-rules-engine`, which describes the whole rules feature package, while
  running the `living-spec-draft` stage of a spec unit.
- **Expectation**: The `spec-entrypoints` skill says to "choose a directory (trailing `/`) only when the document owns
  the whole package". So `--apply --target CAP-GOV-rules-engine --code <package>/` should write the directory as one
  entrypoint.
- **Actual**: `--code` is a filter ("Keep only candidates equal to or under this path"). The apply wrote all ten
  changed files under the directory as separate entrypoints, not the directory.
- **Workaround (or Interpretation Chosen)**: Edited the capability's frontmatter by hand down to two doorway files.
- **Suggestion**: Either let `--apply` write a directory `--code` value as one entrypoint when it ends in `/`, or change
  the skill to say how a directory entrypoint is written (or that it cannot be written through `derive`).

## Diagnostic Details

- **Reproduction**: `devkit spec entrypoints derive --spec <unit> --apply --target CAP-GOV-rules-engine --code packages/devkit/src/devkit_agt/features/rules/`
- **Expected / Actual**: expected one `entrypoints` entry, the directory; actual ten file entries.
- **Versions**: devkit workspace at the unit's head (dev-lint-clean-target-scoped-rules).
- **Conditions**: the directory held ten changed candidate files.
- **Workarounds Attempted**: manual frontmatter edit, then `devkit rules check` passed.
- **Related Assets**: `spec-entrypoints` skill step 2, `devkit spec entrypoints derive --help`.

## Evidence

```text
[APPLIED: CAP-GOV-rules-engine path=docs/capabilities/governance/CAP-GOV-rules-engine.md added=packages/devkit/src/devkit_agt/features/rules/__init__.py,...cli/output.py,...models/contracts.py,... (10 files)]
--code TEXT  Keep only candidates equal to or under this path
```
