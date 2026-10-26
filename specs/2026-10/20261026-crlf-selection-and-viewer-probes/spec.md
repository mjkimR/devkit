---
id: SPEC-crlf-selection-and-viewer-probes
title: CRLF-preserving selection edits and viewer probe test runs
summary: 'Resolves two feedback items: selection edits to .devkit/config.toml keep a file''s existing line endings, and the viewer tooling runs a reviewer''s frontend probes outside src/.'
status: planned
created: 2026-10-26
related_capabilities:
  - CAP-DIST-sync-and-transactions
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-crlf-selection-and-viewer-probes] CRLF-preserving selection edits and viewer probe test runs

## 1. Problem Statement & Motivation

Two open feedback items need the change the user agreed (`materials/decisions.md`):

- A selection edit (`prepare_config_update`, run by `devkit add` and the other selection commands) reads
  `.devkit/config.toml` with newline translation and writes LF, so one edit of a CRLF file rewrites every line ending.
  `devkit config template` already keeps them (`SPEC-approval-mode-and-crlf-template`), and
  `CAP-DIST-sync-and-transactions` (Selection edits) describes only where the new entry goes. This is a defect: the
  edit changes lines it does not own.
- A `code-reviewer` writing executable probes for a viewer frontend change under `<worktree>/scratch/review-NN/` is
  told to run the package's test command on them, but `just viewer test` collects only `src/**/*.test.ts`, so the
  reviewer has to write a vitest config of its own.

## 2. User Stories

- **US-1**: As a developer with a CRLF `.devkit/config.toml`, I want `devkit add` and the other selection commands to
  add only their entry, so that the diff shows the selection change and nothing else.
- **US-2**: As a `code-reviewer` probing a viewer frontend change, I want one command that runs my probe directory
  with the package's resolution, so that I write no config of my own.

## 3. Non-Goals

1. **Scope Excluded**: support for a lone-CR file, which is not valid TOML and stays refused with `CONFIG_INVALID`.
2. **Scope Excluded**: a change to where a selection entry goes or which template parts a created file gets.
3. **Scope Excluded**: a change to the include of `just viewer test`, the vitest config files or the CI viewer job;
   probes are run only on request.
4. **Scope Excluded**: a handbook refresh for this work.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A selection edit of a CRLF file keeps CRLF and adds CRLF lines
- **Given** `.devkit/config.toml` holding `schema = 1\r\n\r\n[presets]\r\nspec = "core"\r\n`
- **When** `update_config(<root>, agents=["codex"], presets={"team": ["all"]}, opt_out=["devkit"])` runs
- **Then** every original line appears in order with its `\r\n`, the count of `\n` equals the count of `\r\n`, the
  file contains `agents = ["codex"]\r\n`, and `[presets]` parses to `spec = "core"`, `team = "all"`, `devkit = false`

### [AC-02] A selection edit of an LF or mixed file keeps its bytes and adds LF lines
- **Given** `.devkit/config.toml` holding the LF text `schema = 1\n\n[presets]\nspec = "core"\n`, or the mixed text
  `schema = 1\n\r\n[presets]\r\nspec = "core"\n`
- **When** `update_config(<root>, agents=["codex"], presets={"team": ["all"]})` runs
- **Then** every original line appears in order with its own ending, the count of `\r\n` is unchanged, and
  `[presets]` parses to `spec = "core"`, `team = "all"`

### [AC-03] The viewer probe action runs a directory's tests with the package's resolution
- **Given** an absolute directory outside `packages/devkit-viewer/frontend/src/` holding a `*.test.ts` file that
  imports `vitest`, `@testing-library/svelte`, `yaml` and a component by relative path
- **When** `just viewer probe <dir>` runs
- **Then** vitest collects that file, its imports resolve, the command exits `0` when every test passes and `1` when
  one fails, and the directory holds no generated config afterwards

### [AC-04] The probe action refuses a relative or missing directory
- **Given** a relative path or an absolute path that does not exist
- **When** `bash scripts/viewer.sh probe <path>` runs
- **Then** it prints `error: probe directory must be an existing absolute path: <path>` on stderr and exits `2`

### [AC-05] The reviewer contract and the viewer reference name the probe command
- **Given** the `code-reviewer` role contract and `docs/development/reference/viewer.md`
- **When** a reviewer reads the probe sentence or the Frontend section
- **Then** both name `just viewer probe` for a viewer frontend probe outside `src/`

## 5. Assumptions

1. The edit reuses the line-ending rule `_template` applies (one helper, `_match_line_endings`), as the agreement asks.
2. vitest 5 has no include flag, so the probe action writes a temporary config into the probe directory that extends
   the package's `vite.config.ts` and removes it on exit; no tracked config file changes. The probe directory is the
   path a reviewer may write, so the action needs no other write access.
3. "The package's normal resolution" means a bare import from a probe resolves to the package's dependencies, as from
   `src/`; the temporary config lists every dependency the package declares in `resolve.dedupe`.

## 6. Source feedback

- `FB-selection-edits-rewrite-crlf-line-endings`: AC-01, AC-02.
- `FB-viewer-review-probes-outside-vitest-include`: AC-03, AC-04, AC-05.
