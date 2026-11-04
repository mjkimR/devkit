---
id: FB-entrypoints-derive-boundary-annotations
title: devkit spec entrypoints derive reads a parenthetical note in a _Boundary list as part of a path
scope: repo
kind: friction
category: tool-error
target: packages/devkit-spec/src/devkit_spec/features/entrypoints/repositories/bundle.py
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-04
---

# [FB-entrypoints-derive-boundary-annotations] devkit spec entrypoints derive reads a parenthetical note in a _Boundary list as part of a path

## 1. Friction / Question (friction, question)

- **Context**: Reviewing entrypoint candidates for `SPEC-namespace-steering` after a review finding asked for a
  boundary extension to be annotated in `tasks.md`; the extended `_Boundary` entry was written as a backticked path
  followed by a parenthetical reason spanning a continuation line.
- **Expectation**: `devkit spec entrypoints derive --spec <dir>` reads the backticked paths of a `_Boundary` list
  and ignores prose around them, as `spec-tasks` lets a task explain a boundary.
- **Actual**: every `[CANDIDATES: ...]` line reported
  `missing="packages/.../test_playbook_get.py  shape,so it gains the new keys)"`: the comma-separated split kept
  the note's tail as part of the path, so the real path was neither matched nor offered.
- **Workaround (or Interpretation Chosen)**: ignored the `missing` value; the annotated path was a test file that
  never becomes an entrypoint, so nothing was lost this time.
- **Suggestion**: take only the backticked code spans of a `_Boundary` line (and its continuation lines) as paths,
  or strip text outside code spans before splitting; `spec-tasks` could also say that a `_Boundary` note belongs on
  its own line.

## Diagnostic Details

- **Reproduction**: a `tasks.md` task whose `_Boundary` lists `` `a/b.py`, ``, then a continuation line
  `` `c/d.py` (its fixture asserts the exact shape, so it gains the new keys)``; run
  `uv run devkit spec entrypoints derive --spec <dir>`.
- **Expected / Actual**: `missing` empty or naming `c/d.py` alone; actual `missing="c/d.py  shape,so it gains the new keys)"`.
- **Versions**: the devkit workspace at the Development branch of `SPEC-namespace-steering`.
- **Conditions**: any `_Boundary` entry with prose containing a comma after a backticked path.
- **Workarounds Attempted**: none beyond ignoring the value.
- **Related Assets**: `devkit spec entrypoints derive`, `spec-entrypoints`, `spec-tasks`.

## Evidence

```text
[CANDIDATES: CAP-GOV-spec-rules path=docs/capabilities/governance/CAP-GOV-spec-rules.md new=... missing="packages/devkit-dist/tests/integration/features/distribution/test_playbook_get.py  shape,so it gains the new keys)" folded=- declared=...]
```


## Disposition

Resolved by `SPEC-worker-scope-extension`. The shared boundary parser now strips balanced parenthetical prose,
including nested `ContextResult.to_dict()` calls, embedded backticks and commas, while retaining quoted and
unquoted literal boundary paths. The focused legacy-note regression in
`packages/devkit-spec/tests/unit/features/entrypoints/test_boundary_extensions.py` verifies exactly
`['a/b.py', 'c/d.py', 'plain/e.py', 'f/g.py']`; the previous probe emitted prose fragments. Independent medium Code
Review covered this change at `62e62672718159b9b46882a87a5830e67a266736`, and the post-fix affected selector
passed 2314 tests at `7137f4cc811f2084b336edaf2cd3a5c32ee3cff2`. No managed-path filtering was added.
