---
id: SPEC-small-helper-consolidations
title: Consolidate the remaining duplicated runtime helpers
summary: 'Consolidates three deferred duplicates without changing behavior or projected bytes: a public devkit-cli UTF-8 output helper, subagent projection quoting through the shared frontmatter scalar, and shared Git tracked/ignored probes in devkit-core.'
status: in-progress
created: 2026-11-11
related_capabilities: [CAP-CLI-agent-cli-toolkit, CAP-DIST-agent-projections]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-small-helper-consolidations] Consolidate the remaining duplicated runtime helpers

## 1. Problem Statement & Motivation

Handed off from proposal PROP-small-helper-consolidations on 2026-11-11.
- **Preserved Materials**: `docs/materials/2026-11/20261111-small-helper-consolidations`

Three small duplicates were deferred by the code pass (`docs/materials/2026-11/20261111-review-refactor-code-pass/report.md`):

- X-13: `_utf8_output` is copied from devkit-cli (`devkit_cli.boundary`) into devkit-dist
  (`devkit_dist.features.host.cli`, the hidden `devkit host hook` command, which bypasses `@boundary` because its
  stdout follows the host's native protocol).
- DS-09: subagent projection hand-rolls YAML quoting (`_yaml_quote`, `_yaml_scalar`, `_yaml_value` in
  `devkit_dist.features.distribution.services.bundles.subagents`) beside the shared
  `devkit_core.core.frontmatter.scalar`.
- DS-10: devkit-dist asks Git whether paths are tracked or ignored in four places (host registrations, shared
  storage, the local render check and projection Git notices), plus a tracked-only check in sync.

Each duplicate gets one owner that keeps every caller's options, so no behavior, contract or projected byte of a
shipped role contract changes. Evidence: `docs/materials/2026-11/20261111-small-helper-consolidations/planning-evidence.md`.

## 2. User Stories

- **US-1**: As a devkit maintainer, I want each of these helpers to have one owner, so that a fix to UTF-8 output,
  YAML quoting or a Git path probe lands once and every caller gets it.
- **US-2**: As a consumer of shipped subagent projections, I want the projected files to stay byte-identical, so
  that the consolidation causes no sync churn or host-visible change.

## 3. Non-Goals

1. **Scope Excluded**: the Codex TOML quoter (`_toml_string`, `_toml_multiline`, `_toml_value`) stays as it is.
2. **Scope Excluded**: shared storage's `ls-files --others --exclude-standard` query (a different question) and every
   caller's own ignore mode, deadline and failure mapping stay with the caller.
3. **Scope Excluded**: no new package dependency, feature edge (`.devkit/architecture.toml`) or ADR; no change to
   `CAP-DIST-agent-projections` or to devkit-agt and devkit-mcp.
4. **Scope Excluded**: no own minor version bump of devkit-cli; the added public name ships with the shared release
   version (`CAP-CLI-agent-cli-toolkit` rule 10).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] devkit_cli exports one UTF-8 output helper
- **Given** `devkit_cli` and `devkit_dist.adapters.cli`
- **When** a test runs `devkit_cli.utf8_output()` with stdout and stderr as ASCII `io.TextIOWrapper` streams, then
  once more with a closed stream
- **Then** both open streams report `encoding == "utf-8"` and `errors == "backslashreplace"`, the closed stream
  raises nothing, `"utf8_output"` is in the pinned `devkit_cli.__all__`, `devkit_dist.adapters.cli.utf8_output is
  devkit_cli.utf8_output`, and `rg -n "def _utf8_output" packages/devkit-cli/src packages/devkit-dist/src` prints
  nothing

### [AC-02] The boundary and the hook keep locale-independent output
- **Given** `LC_ALL=C` and `PYTHONIOENCODING=ascii`
- **When** a `Boundary` command and the hidden `devkit host hook` command write non-ASCII text
- **Then** the existing tests `test_output_is_utf8_whatever_the_locale` (devkit-cli and devkit-dist) and
  `test_hook_output_is_utf8_whatever_the_locale` pass unchanged with exit `0` and UTF-8 stdout bytes

### [AC-03] frontmatter.scalar gains quoting options with an unchanged default
- **Given** `devkit_core.core.frontmatter.scalar(value, *, quote="'", always_quote=False)`
- **When** it is called without options on every value of the existing parametrized scalar test
- **Then** it returns the same strings as before (`off` → `'off'`, `plain title` → `plain title`); with
  `quote='"'` it returns `"off"` for `off` and `Read` for `Read`; with `always_quote=True` it returns a quoted
  scalar for a plain-safe value (`Read` → `'Read'`, or `"Read"` with `quote='"'`); every result is one line and
  reads back as the same string as a mapping value and as a list item; any other `quote` value raises `ValueError`

### [AC-04] Subagent projections render through the shared scalar with identical shipped bytes
- **Given** every shipped role contract (15 source contracts plus the 2 templated ones in their installed rendered
  form under `.devkit/managed/*/subagents/`, 26 files) rendered for `claude-code`, `codex` and `antigravity`
- **When** the projections are rendered after the change
- **Then** each of the 78 renderings has the same SHA-256 as before the change, `uv run devkit sync --check` exits
  `0`, the hand-rolled double quoter `_yaml_quote` no longer exists in `subagents.py`, and every quoted value is
  rendered by `frontmatter.scalar`

### [AC-05] Projection quoting keeps today's bytes for the edge values
- **Given** a role contract whose description holds a line break, a tab, a double quote, a backslash and the control
  character U+0001, and whose `claude-code` block sets the string setting `off` and a tool list with a plain item
  and the items `a,b`, `a<TAB>b`, `Bash(ls)` and `1e3`
- **When** the `claude-code` projection is rendered
- **Then** the header holds `name: reviewer`, a double-quoted description whose bytes equal the hand-rolled
  quoter's (`\n`, `\t`, `\"`, `\\`, `\x01` escapes), the setting as `"off"`, the plain list item unquoted and the
  other four items double-quoted as today, and `yaml.safe_load` of the header returns the original values

### [AC-06] Shared Git tracked and ignored probes
- **Given** `devkit_core.core.git.tracked_paths(cwd, paths, *, deadline=None) -> set[str]` and
  `ignored_paths(cwd, paths, *, no_index=False, deadline=None) -> set[str]`
- **When** they run in a repository with a tracked file, a directory holding tracked files, a tracked file that an
  ignore rule matches, an untracked ignored file, and tracked files named `a*b`, `axb` and `:x`
- **Then** `tracked_paths` returns the tracked file, the directory, `a*b` and `:x`, and nothing for `a?b` or `x`
  (literal pathspecs: no glob match and no `:` magic);
  `ignored_paths` returns the untracked ignored file and, only with `no_index=True`, the tracked ignored file; no
  match (Git exit `1`) is the empty set; an empty `paths` returns the empty set without running Git; outside a
  repository both raise `GitError` with `returncode == 128`

### [AC-07] The five devkit-dist probe sites use the shared helpers with their own policies
- **Given** host registrations (`_tracked`, `_ignored`, `_Eligibility`), shared storage (`_eligible`,
  `_initialize`), `local_render.require_ignored`, `projection_git_notices` and the locked-sync tracked check
- **When** their existing tests run
- **Then** they pass, unchanged except that the two tests which patch a module's own Git runner to observe or fail a
  probe (`test_non_git_and_failed_query`, `test_planning_asks_git_once_for_all_destinations_with_per_path_answers`)
  patch the same runner in `devkit_core.core.git`, keeping their assertions: registrations still answer not ignored on any Git failure, shared storage still
  raises `ExclusionError` when `.devkit/.shared/` is not ignored, `require_ignored` still raises any `GitError`
  other than exit `1`, and `projection_git_notices` still skips exit `128` "not a git repository" and turns other
  failures into `PROJECTION_GIT_CHECK_FAILED`; no `"ls-files", "--"` or `"check-ignore"` call remains in those
  modules apart from shared storage's `--others --exclude-standard` query

## 5. Assumptions

1. **Control-character escapes**: PyYAML's double style writes seven C0 controls with short escapes (`\0`, `\a`,
   `\b`, `\v`, `\f`, `\r`, `\e`) where the hand-rolled quoter wrote `\x00`, `\x07`, `\x08`, `\x0B`, `\x0C`,
   `\x0D`, `\x1B`. Both forms load as the same string and no shipped description holds one, so the shipped-bytes
   contract holds; the planning evidence listed only NEL, LS, PS and non-printable characters as differences.
2. **Plain gate kept**: `scalar`'s read-back check covers block context and YAML 1.1 only, so letting it decide
   would write values such as `a<TAB>b` or `a?b` plain in a flow list (an unparsable header), `1e3` plain (a number
   to a YAML 1.2 host) and `Bash(ls)` plain (new bytes for project-owned contracts). Projection therefore keeps its
   identifier-only plain gate (`_YAML_PLAIN`, `_YAML_RESERVED`) for `name`, string settings and list items and lets
   `scalar(..., quote='"', always_quote=not plain)` write every value, so no input changes bytes apart from
   assumption 1. This narrows the proposal's removal list (`_yaml_scalar` stays as the gate); the goal of one quoting
   owner and unchanged behavior holds.
3. **Literal pathspecs**: `tracked_paths` passes each path with the `:(literal)` magic. `check-ignore` reads its
   input as path names; all current inputs are fixed devkit paths without glob characters, so no current result
   changes.

## 6. Source feedback

None: the work comes from the deferred items X-13, DS-09 and DS-10 of the code pass report, not from FB records.
