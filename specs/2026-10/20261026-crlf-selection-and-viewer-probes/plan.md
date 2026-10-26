---
id: PLAN-crlf-selection-and-viewer-probes
spec: SPEC-crlf-selection-and-viewer-probes
---

# Technical Plan: `SPEC-crlf-selection-and-viewer-probes` CRLF-preserving selection edits and viewer probe test runs

## 1. Constitution & Invariant Review

None. `CAP-DIST-sync-and-transactions` already states the line-ending rule for the template (Append-only); the
Selection edits paragraph gains the same rule. No `MUST` of `docs/architecture/` changes, and no ADR is needed.

## 2. Architecture Overview & Impact

- **Selection edits** (`packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py`):
  `_document` parses the untranslated text (`_read_untranslated`: `read_bytes().decode("utf-8")`), so tomlkit keeps
  the existing line endings. The rule `_template` applied inline becomes `_match_line_endings(before, text)`: bare-LF
  endings turn into CRLF when the file has a newline and every one follows a CR. `prepare_config_update` applies it to
  the rendered text of an existing file; a created file stays LF. `_template` calls the same helper (AC-01, AC-02).
- **Probe action** (`scripts/viewer.sh probe <dir> [args]`): checks that `<dir>` is an existing absolute directory
  (else exit `2`), writes `<dir>/.viewer-probe.vitest.config.mts` with a trap that removes it, and runs
  `npx --no-install vitest run --config <it> [args]` from the frontend. The config imports the package's
  `vite.config.ts`, sets `root` to the frontend, `test.dir` to `<dir>`, `test.include` to `**/*.test.ts`, and
  `resolve.dedupe` to the dependencies, devDependencies and peerDependencies of `package.json`, so Vite resolves a
  bare import from the probe to the package (AC-03, AC-04). The `just viewer` recipe already passes arguments through.
- **Guidance**: the `code-reviewer` contract's probe sentence and `docs/development/reference/viewer.md` name
  `just viewer probe`; `uv run devkit sync` refreshes the projections and `.devkit/installation.json` (AC-05).

## 3. Error Handling & Edge Cases

- A file without a newline (`schema = 1`) is LF: nothing to convert. A mixed file gets LF lines.
- A decode failure raises inside `_document`'s existing `ConfigError` handler (`CONFIG_INVALID`); `read_config` runs
  first and already refuses an unreadable or invalid file.
- A probe directory containing spaces is passed to the config through the environment
  (`VIEWER_PROBE_ROOT`, `VIEWER_PROBE_DIR`), never interpolated into source.

## 4. Verification & Test Plan

- Red first: the AC-01 and AC-02 tests in `test_config_template.py` failed before the fix (CRLF and mixed: the edit
  wrote every line ending as LF), and pass after it.
- `just test devkit-dist packages/devkit-dist/tests/integration/features/distribution/test_config_template.py`.
- `just viewer probe <worktree>/scratch/probe-check-01` (one failing test: exit `1`) and `.../probe-check-02`
  (passing: exit `0`); `bash scripts/viewer.sh probe scratch/probe-check-02` and a missing path exit `2`;
  `just viewer test` unchanged.
- `just lint-check devkit-dist`, `just check devkit-dist`, `just test-affected`, `just test-dist`,
  `uv run devkit sync --check`, `uv run devkit rules check --ci --base f076ddbc`.
