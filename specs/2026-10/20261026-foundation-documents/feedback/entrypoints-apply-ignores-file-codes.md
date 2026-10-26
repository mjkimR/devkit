---
id: FB-entrypoints-apply-ignores-file-codes
title: Entrypoints apply silently writes nothing for a file code
scope: repo
kind: friction
category: other
target: devkit spec entrypoints derive --apply
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-entrypoints-apply-ignores-file-codes] Entrypoints apply silently writes nothing for a file code

Category: a CLI result that hides a refused input.

## 1. Friction / Question (friction, question)

- **Context**: In `spec-sync` step 4 of a spec bundle whose `_Boundary` paths are directories, I applied two doorway
  files to one capability with `devkit spec entrypoints derive --spec <dir> --apply --target <CAP-ID> --code
  <file> --code <file>`.
- **Expectation**: The `spec-entrypoints` skill says to keep 1-3 doorway files per document (`usecase.py`,
  `service.py`), so a file under a candidate directory should be accepted or refused with a code.
- **Actual**: The command printed `[SUMMARY: pairs=0 new=0 declared=0 skipped=8 applied=0]` and exit `0`; it wrote
  nothing and named no reason. Only directory candidates are applied.
- **Workaround (or Interpretation Chosen)**: I added the two files to the capability's `entrypoints` frontmatter by
  hand and checked them with `devkit rules check` (`RULE-code-entrypoints`).
- **Suggestion**: Accept a `--code` file that lies under a candidate path, or report each unmatched `--code` with a
  stable code and an `[ACTION]`, so the result never reads as a success that applied nothing.
