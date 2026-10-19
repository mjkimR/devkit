---
id: FB-smoke-response-style-instruction-path
title: just smoke asserts the removed response-style instruction path and fails on main
scope: repo
kind: friction
category: tool-error
target: scripts/smoke.sh (response-style section)
skill: spec
agent: claude-code
origin: agent
severity: blocked
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-smoke-response-style-instruction-path] just smoke asserts the removed response-style instruction path and fails on main

## 1. Friction / Question (friction, question)

- **Context**: Collecting the `build` evidence for the final change report of `SPEC-targeted-tests`, which does not
  touch the smoke script or the response-style bundle.
- **Expectation**: `just smoke` (the consumer smoke listed in AGENTS.md Verification) passes on `main`.
- **Actual**: The response-style step reads `.devkit/managed/response-style/instructions/response-style.md`, which
  the installed bundle no longer has (it now ships `guidance/` and `skills/`), so the recipe exits 1 with
  `FileNotFoundError`. The same failure occurs on the base checkout at `main`.
- **Workaround (or Interpretation Chosen)**: Took the build evidence from `uv build --all-packages --wheel` (all
  five wheels built) and reported the smoke failure as pre-existing and unrelated.
- **Suggestion**: Point the smoke assertions at the response-style skill path the bundle now deploys (and the
  `AGENTS.md` pointer it writes), so the smoke covers the current bundle layout again.

## Diagnostic Details

- **Reproduction**: `just smoke` on `main` and on the `dev-targeted-tests` branch.
- **Expected / Actual**: Expected the smoke to pass; it stops at the response-style assertion with exit 1.
- **Versions**: `main` at 58dae19; branch head d9b43e4.
- **Conditions**: macOS, Python 3.13 for the smoke consumer project; independent of this branch's changes.
- **Workarounds Attempted**: `uv build --all-packages --wheel` succeeded for every package.
- **Related Assets**: `scripts/smoke.sh`, the response-style bundle, `SPEC-response-style-skill`.

## Evidence

```text
scripts/smoke.sh:
    path = Path(".devkit/managed/response-style/instructions/response-style.md")
    assert "Use ko as the default" in path.read_text()
just smoke (main and branch):
    FileNotFoundError: [Errno 2] No such file or directory: '.devkit/managed/response-style/instructions/response-style.md'
    error: recipe `smoke` failed ... with exit code 1
ls .devkit/managed/response-style/  ->  bundle.toml guidance skills
```

- **Disposition**: scripts/smoke.sh (commit c05b3c5): the smoke now checks the rendered response-style skill and its AGENTS.md pointer instead of the removed instruction path.
