---
id: FB-smoke-integration-stale-task-kind
title: Consumer smoke calls removed integration task-kind option
scope: repo
kind: friction
category: tool-error
target: tests/e2e/smoke_integration.py
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-smoke-integration-stale-task-kind] Consumer smoke calls removed integration task-kind option

## 1. Friction

- **Context**: Verifying `SPEC-adaptive-package-extraction` with `just smoke` after the package move.
- **Expectation**: The installed consumer integration probe uses the supported integration CLI.
- **Actual**: The probe passes `--task-kind` to `integration prepare`, which rejects the option; smoke exits 1 after successful package registration and worktree checks.
- **Workaround**: AC-06 explicitly permits an unchanged baseline smoke failure outside the planned edit lines. The Host reproduced this failure with the baseline runtime and smoke code, after correcting only the earlier stale catalog-set assertion in a disposable script.
- **Suggestion**: Update the consumer integration probe to the current CLI and verify the complete smoke sequence. This file is outside the extraction scope.

## Diagnostic Details

- **Reproduction**: `just smoke` in the extraction worktree, then the Host baseline disposable-script probe.
- **Expected / Actual**: Consumer integration succeeds / argument parsing rejects `--task-kind`.
- **Versions**: Source bundle and wheels 0.1.6; implementation `7e81bc8d`, historical baseline `9ab4f8e`; Host probe observed base `b46086c`.
- **Conditions**: Local macOS wheel consumers; the baseline advanced only in four proposal/feedback documents. Runtime, smoke and package source paths in the probe are unchanged from `9ab4f8e`.
- **Workarounds Attempted**: Baseline probe changed only the disposable script working directory and catalog expected set from the stale five names to the actual eight; repository source remained unchanged. It reproduced the same option error.
- **Related Assets**: `tests/e2e/smoke.sh`, `tests/e2e/smoke_integration.py`, `SPEC-adaptive-package-extraction` AC-06.

## Evidence

```text
smoke_integration.py:127: assert result.returncode == 0
Usage: python -m devkit_dist integration prepare [OPTIONS] BRANCH
Error: No such option '--task-kind'.
```
