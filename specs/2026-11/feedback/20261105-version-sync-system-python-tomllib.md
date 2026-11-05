---
id: FB-version-sync-system-python-tomllib
title: Version recipes use a system Python without tomllib
scope: repo
kind: friction
category: tool-error
target: justfile version-sync and version-check
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-05
---

# [FB-version-sync-system-python-tomllib] Version recipes use a system Python without tomllib

## 1. Friction / Question

- **Context**: Preparing the 0.1.6 package metadata and release handbook.
- **Expectation**: The documented `just version-sync` recipe runs the repository's version synchronizer.
- **Actual**: The recipe invokes `python3 scripts/version.py`. The system interpreter cannot import `tomllib`,
  so execution stops before metadata synchronization, even though the uv project environment is usable.
- **Workaround**: `uv run --no-active python scripts/version.py` executes the same script successfully through
  the project interpreter. Its `--check` invocation verifies all twelve workspace distributions.
- **Suggestion**: Run both version recipes through the project interpreter, consistently with the handbook recipe.
  Keep the script's version validation and metadata/lock/receipt synchronization unchanged.

## Diagnostic Details

- **Reproduction**: Run `just version-sync` in the observed environment; the import fails before `main` executes.
- **Expected / Actual**: Expected synchronized release metadata; observed exit 1 from the recipe and a
  `ModuleNotFoundError` for `tomllib`.
- **Versions**: Repository source `dabb86f9e6595939cbcb428f9038a6df40fdd5fc`; release metadata 0.1.5 transitioning
  to 0.1.6. The exact system Python version was not recorded.
- **Conditions**: POSIX development environment where `python3` on PATH differs from the uv project interpreter.
- **Workarounds Attempted**: Project-interpreter execution passed after package-index access was available;
  `uv run --no-active python scripts/version.py --check` returned `packages=12`.
- **Related Assets**: `justfile`, `scripts/version.py`; `just handbook` already uses `uv run --no-active python`.

## Evidence

```text
$ just version-sync
python3 scripts/version.py
ModuleNotFoundError: No module named 'tomllib'

$ uv run --no-active python scripts/version.py
[VERSION: 0.1.6 state=synced packages=12]

$ uv run --no-active python scripts/version.py --check
[VERSION: 0.1.6 state=checked packages=12]
```

## Disposition

- **Disposition**: The selective-package-releases change already updated both `justfile` recipes to use
  `uv run --no-active python scripts/version.py`. This session verified that implementation and closed the stale
  feedback without another version change.
- **Verification**: Actual `just version-sync` and `just version-check` invocations both reached the release CLI's
  `RELEASE_BASELINE_REQUIRED` validation (exit 2), with no `tomllib` import failure. A completed release baseline is
  now required by the selective-release workflow; no baseline was imported and no release metadata was changed.
  The four existing release-boundary tests passed in the combined 31-test run.
