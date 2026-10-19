---
id: FB-just-test-package-relative-path
title: just test refuses a package-relative test file path
scope: repo
kind: friction
category: tool-error
target: scripts/module.sh (just test <module> [area|path...])
skill: none
agent: claude-code
origin: agent
severity: noise
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-just-test-package-relative-path] just test refuses a package-relative test file path

## 1. Friction / Question (friction, question)

- **Context**: running one test file of `devkit-spec` during build-verify, as the repository guide's verification
  table suggests (`just test <module> [area|path...]`).
- **Expectation**: a path under the named module, such as `tests/test_role_contracts.py`, selects that file.
- **Actual**: the selector is accepted only as a path that exists from the repository root or as a directory name
  under `<module>/tests/` or `<module>/src/*/`; the package-relative file path fails with exit 2 and the error lists
  only the areas, not that a path must be repository-relative.
- **Workaround (or Interpretation Chosen)**: passed the repository-relative path
  `packages/devkit-spec/tests/test_role_contracts.py`, which ran 40 tests.
- **Suggestion**: also resolve a selector against `<module>/` (and `<module>/tests/`) before failing, or say in the
  error line that a path is taken from the repository root. Assessment: one wasted call per agent that tries the
  natural form; the fix is a few lines in `select_area` and needs no interface change.

## Diagnostic Details

- **Reproduction**: `just test devkit-spec tests/test_role_contracts.py` from the repository root.
- **Expected / Actual**: expected the one file to run; actual is the "Unknown area" error with exit 2.
- **Versions**: devkit 0.1.1, unit branch dev-role-reasoning-effort-presets.
- **Conditions**: macOS, `just` recipe `test` calling `scripts/module.sh test`.
- **Workarounds Attempted**: repository-relative path; it worked.
- **Related Assets**: `scripts/module.sh` (area selection), `justfile` recipe `test`, `AGENTS.md` verification table.

## Evidence

```text
$ just test devkit-spec tests/test_role_contracts.py
Unknown area for devkit-spec: tests/test_role_contracts.py
Available areas: documents entrypoints proposals scope
error: recipe `test` failed on line 26 with exit code 2

scripts/module.sh: if [ -e "${selector%%::*}" ]; then selected+=("$selector") ...
                   for dir in "$base/tests/$selector" "$base"/src/*/"$selector"; do [ -d "$dir" ] ...
```

- **Disposition**: scripts/module.sh: a selector is also resolved from the module directory, and the unknown-area error says where paths are taken from
