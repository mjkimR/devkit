---
id: FB-viewer-test-without-install
title: Viewer checks fail opaquely in a fresh task worktree
scope: repo
kind: friction
category: tool-error
target: scripts/viewer.sh
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-viewer-test-without-install] Viewer checks fail opaquely in a fresh task worktree

## 1. Friction / Question (friction, question)

- **Context**: Running the viewer checks a Development handoff names (`just viewer test`) in a newly created task
  worktree, which has no `packages/devkit-viewer/frontend/node_modules`.
- **Expectation**: The command either runs the tests or reports that the frontend dependencies are missing with a
  directive to run `just viewer install`, in the agent-facing advisory form.
- **Actual**: npm prints `sh: vitest: command not found` and the recipe exits 127; nothing names the missing install.
  A direct `npx vitest` fetched an unrelated vitest and failed to load the config.
- **Workaround (or Interpretation Chosen)**: Ran `just viewer install` (npm ci) first; the checks then passed.
  `just test-affected` does name `just viewer install` first in its `[FRONTEND_CHECK: ...]` line, but a handoff that
  lists the individual commands omits it.
- **Suggestion**: Let `scripts/viewer.sh` check for `node_modules` before `lint`, `check`, `test`, `build` and `pack`
  and fail with a stable code and an `[ACTION]` naming `just viewer install`.

## Diagnostic Details

- **Reproduction**: In a fresh worktree without frontend dependencies, run `just viewer test`.
- **Expected / Actual**: Expected a directive naming the install; observed `vitest: command not found`, exit 127.
- **Versions**: node v22.22.0, npm 10.9.4 (npm also warned the engine wants node ^22.22.2).
- **Conditions**: Task worktree created by `devkit worktree`; `node_modules` is ignored and not shared with the base
  checkout.
- **Workarounds Attempted**: `npx vitest run` (fails: fetches vitest outside the package); `just viewer install`
  (works).
- **Related Assets**: `scripts/viewer.sh`, `justfile` recipe `viewer`, `scripts/affected_tests.py` frontend check line.

## Evidence

```text
$ just viewer test
bash scripts/viewer.sh "$@"
sh: vitest: command not found
error: recipe `viewer` failed on line 74 with exit code 127
```
