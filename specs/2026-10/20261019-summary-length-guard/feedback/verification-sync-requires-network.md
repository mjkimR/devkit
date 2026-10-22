---
id: FB-verification-sync-requires-network
title: Required lint and type checks resolve remote model metadata inside an initialized worktree
scope: repo
kind: friction
category: tool-error
target: scripts/module.sh run_check uv run invocations
origin: agent
severity: workaround
recurring: true
status: resolved
created_at: 2026-10-19
---

# [FB-verification-sync-requires-network] Required lint and type checks resolve remote model metadata inside an initialized worktree

## 1. Friction / Question

- **Context**: required `just lint-check devkit-spec` and `just check devkit-spec` ran in an initialized worktree during the native worker experiment.
- **Expectation**: lint and type checks should use the available environment without needing unrelated model-wheel metadata.
- **Actual**: both sandboxed commands stopped before their checks because uv tried to fetch `devkit-embed` release-wheel metadata and DNS resolution failed. Narrow escalated reruns passed lint/format and Pyright.
- **Workaround (or Interpretation Chosen)**: rerun only the required commands with command-scoped escalation. No dependency or script change was made.
- **Suggestion**: evaluate an explicitly initialized-environment verification path using `--no-sync`; retain a deliberate environment preparation step so stale environments are not silently accepted. That script change remains untested and outside this fix.

## Diagnostic Details

- **Reproduction**: run the two required commands in the initialized sibling worktree under the restricted network sandbox.
- **Expected / Actual**: expected Ruff/Pyright execution; actual uv metadata-resolution DNS failures before either check ran.
- **Versions**: repository worker input head `471b19a`; remote wheel was `devkit-embed==0.1.0`; uv version unknown.
- **Conditions**: workspace-write with restricted network, existing initialized worktree environment, `run_check` invoking `uv run --no-active` without `--no-sync`.
- **Workarounds Attempted**: elevated reruns succeeded; direct `uv run --no-sync` for workflow commands and one-file Ruff formatting also succeeded. No alternative script implementation was tested.
- **Related Assets**: `scripts/module.sh`, `just lint-check`, `just check`, uv dependency resolution.

## Evidence

```text
just lint-check devkit-spec / just check devkit-spec:
Failed to generate package metadata for devkit-embed==0.1.0
Failed to fetch the release wheel; dns error
Escalated reruns: All checks passed; 218 files already formatted;
Pyright: 0 errors, 0 warnings, 0 informations
```

- **Disposition**: `session` task `dev-feedback-resolutions`: updated `scripts/module.sh` (`run_check` and `check_test_environment`) to invoke `uv run` with `--no-sync` so initialized worktrees and sandboxed environments do not resolve remote package metadata over the network. Verified with `pytest packages/devkit/tests/test_module_script.py`.

