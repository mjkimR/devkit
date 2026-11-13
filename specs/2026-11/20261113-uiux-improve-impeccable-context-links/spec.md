---
id: SPEC-uiux-improve-impeccable-context-links
title: Link tracked Impeccable context through a bundled POSIX script
summary: "Link tracked Impeccable context into each checkout through optional relative root symlinks, and inspect missing or replaced links without changing consumer content."
status: completed
created: 2026-11-13
related_capabilities: [CAP-DLV-uiux-improvement]
related_usecases: [UC-improve-an-interface-and-user-flow]
workflow: sdd-spec-feature
---

# [SPEC-uiux-improve-impeccable-context-links] Tracked Impeccable context links

## 1. Problem Statement & Motivation

Local-only root context disappears in another worktree or clone. A tracked source directory and excluded relative
root links preserve one content copy. A read-only check exposes replacement by atomic-save editors.
`ADR-impeccable-context-links` authorizes the bounded helper and requested setup. Planning evidence is retained at
`docs/materials/2026-11/20261113-uiux-improve-impeccable-context-links/link-evidence.md`.

## 2. User Stories

- **US-1**: As a consumer, I want each worktree to read its own tracked context without copying or overwriting files.
- **US-2**: As a coordinator, I want to inspect link drift and report manual recovery within consumer authority.

## 3. Non-Goals

**Scope Excluded**: devkit CLI/configuration/runtime additions, context content creation/editing, automatic repair,
root .gitignore changes, staging/untracking, source-side ignore installation, Windows support beyond clear refusal,
and changes to Impeccable run/question/load routing. No new feature edge, package or test tier is introduced.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Idempotent links

- **Given** present optional source entries in an ordinary repository.
- **When** link mode runs twice.
- **Then** relative links resolve to the source and the second run changes no link or exclude bytes.

### [AC-02] Preserve occupied entries

- **Given** an occupied root file, directory, foreign/dangling link or tracked root entry.
- **When** either mode runs under the quiescence precondition.
- **Then** each occupied entry is preserved with a stable state, while eligible other entries progress in link mode.

### [AC-03] Per-worktree source and common excludes

- **Given** a linked worktree with the source tracked on its branch.
- **When** the helper runs from a subdirectory.
- **Then** root links point into that worktree and the resolved common exclude file receives the exact patterns.

### [AC-04] Read-only classification

- **Given** each root/source state, including equal/different atomic-save replacement, directory replacement and a resolving foreign link ending in newline bytes.
- **When** check mode runs.
- **Then** codes/actions and exit precedence match the interface, the filesystem/index/HEAD stay unchanged, and the newline target is LINK_WRONG_TARGET.

### [AC-05] Bounded source and invocation

- **Given** spaces, arrows, leading-dash source after --, lexical parent paths, source symlink escapes, wrong input types, missing repository or disabled symlinks.
- **When** preflight runs.
- **Then** supported physical in-worktree paths are normalized, and invalid sources/invocations return exit 2 before any mutation.

### [AC-06] Exclude preservation and partial I/O failure

- **Given** exact/unrelated excludes, an unterminated last line, an existing helper lock or injected I/O failure.
- **When** link mode runs with quiescent managed entries/source.
- **Then** existing bytes and occupied directory contents survive, exact patterns are deduplicated, busy lock refuses exclude writes, and I/O failure returns exit 2 with retained partial effects.

### [AC-07] Content-only projection

- **Given** the selected bundle projects to supported hosts.
- **When** sync deploys the skill.
- **Then** the script bytes are identical in managed/shared/Claude directories and executable through sh without a new asset kind/runtime dependency.

### [AC-08] Consumer authority and recovery

- **Given** the guide, orchestration and capability contracts.
- **When** their behavior is reviewed and exercised.
- **Then** mutating setup requires a user request and shows exact excludes, check remains read-only inspection, source ignores remain consumer-owned, recovery preserves both versions, and the local-only absolute-path fallback remains available.

## 5. Interface and Design Constraints


### 3.1 Interface and preflight

Bundle source: `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/scripts/`.
The directory will be created in Development; it is part of the existing skill asset.

```sh
sh .agents/skills/app-uiux-improve/scripts/link-impeccable-context.sh [--check] [--] [<source-dir>]
```

`--check` is optional only before the source argument. `--` admits an argument beginning with `-`.
Unknown options or more than one source argument return exit 2 with `LINK_ARGUMENT_INVALID`.
All relative source paths are relative to the worktree root even when invoked from a subdirectory.

1. Resolve the root with `git rev-parse --show-toplevel`, then `cd -P`/`pwd -P`. Refuse no worktree or
   `core.symlinks=false` with exit 2. Resolve `git rev-parse --git-path info/exclude` after entering the root;
   linked worktrees share that file. Do not assume `.git` is a directory.
2. Require an existing source directory, physically inside this worktree and different from its root, using
   `cd -P`/`pwd -P` and a path-component containment check. Reject `.git`/Git metadata locations and source paths
   containing control characters with exit 2. Spaces, punctuation and ` -> ` are supported.
3. Derive a normalized relative source path from that physical location. Top-level source entries, when present,
   are regular unlinked files for `PRODUCT.md`/`DESIGN.md` and an unlinked directory for `.impeccable`.
   A source symlink, wrong type or unreadable input returns exit 2 before link/exclude mutation.
4. Manage exactly `PRODUCT.md`, `DESIGN.md` and `.impeccable`; absent source entries are optional.
   The helper neither stages files nor changes context bytes or root `.gitignore`.

### 3.2 Link and exclude operations

Mutating setup requires quiescent managed root entries and source for the command duration. The guide tells the
consumer to stop editors, context-writing sessions and other helpers before running link mode. This is a supported
use precondition, not a concurrency lock against arbitrary writers. Check mode stays read-only.

- For each present source entry, create a relative root symlink to `<normalized-source>/<entry>` only when no root
  entry exists, including dangling links. Use `ln -s` without force under the quiescence precondition. Preserve all entries occupied at invocation start.
  Concurrent noncooperating destination changes are unsupported: POSIX `ln` can treat a raced-in directory as a
  destination directory, so this helper makes no competing-creation guarantee.
- Preserve a correct existing link. Compare literal target spelling with the normalized relative target; an
  equivalent absolute or differently spelled path is a wrong target, not something silently rewritten.
- Preserve any other existing root file, directory or symlink, report its state, and continue inspecting/linking
  the other entries. A root entry tracked by Git is reported `LINK_TRACKED`; excludes do not untrack it.
- Add only missing exact lines `/PRODUCT.md`, `/DESIGN.md`, `/.impeccable` to the resolved local exclude file.
  Show those exact lines in the setup instructions before a user requests the mutating command.
  Use a final newline before appended entries when the file lacks one; preserve existing bytes and patterns.
  The directory symlink needs `/.impeccable` without a trailing slash.
- Sequential reruns add no links or lines. Link/exclude work may be partially complete when a later operation fails;
  report completed entries and stop on an I/O failure with exit 2. Never remove already created links as rollback.
  Do not claim transaction isolation from unrelated concurrent Git/configuration writers.
- Serialize helper exclude edits with an exclusively created adjacent lock, refuse an existing lock with
  `LINK_EXCLUDE_BUSY` exit 2, and remove only the lock this invocation created. Check mode creates no lock.

### 3.3 Read-only classification and result contract

`--check` creates no link, exclude line, lock or temporary file. It emits one state for each fixed root entry and
one exclude state for each of the three exact lines. Classification order is tracked root, source absent, root
absent, root nonlink, dangling root link, wrong target, correct link. Source preflight errors still return exit 2.

| Stable code | Condition | Deterministic action |
| --- | --- | --- |
| `LINK_CREATED`, `LINK_OK` | Created or literal target correct and resolves | `NONE` |
| `LINK_ABSENT` | Source and root entry both absent | `NONE` |
| `LINK_MISSING` | Source present, root absent in check mode | `RUN_LINK` |
| `LINK_STALE` | Source entry absent, root link present | `INSPECT_LINK` |
| `LINK_OCCUPIED` | Source absent, root nonlink present | `INSPECT_ROOT` |
| `LINK_REPLACED` | Source present, root regular file/directory | `MERGE_INTO_SOURCE` |
| `LINK_DANGLING` | Source present, root symlink target missing | `INSPECT_LINK` |
| `LINK_WRONG_TARGET` | Source present, existing resolving link has a different literal target | `INSPECT_LINK` |
| `LINK_TRACKED` | Git index already tracks a managed root entry | `UNTRACK_MANUALLY` |
| `EXCLUDE_ADDED`, `EXCLUDE_OK` | Exact exclude line appended or already present | `NONE` |
| `EXCLUDE_MISSING` | Exact exclude line absent in check mode | `RUN_LINK` |
| `LINK_ARGUMENT_INVALID`, `LINK_NOT_WORKTREE`, `LINK_SYMLINKS_DISABLED`, `LINK_SOURCE_INVALID`, `LINK_INSPECTION_FAILED`, `LINK_IO_FAILED`, `LINK_EXCLUDE_BUSY` | Invalid invocation, unsupported checkout, source/preflight, inspection, I/O or lock failure | `FIX_INPUT`, `USE_WORKTREE`, `ENABLE_SYMLINKS`, `FIX_SOURCE`, `INSPECT_FILES`, `CHECK_PERMISSIONS`, `RETRY_AFTER_UNLOCK` respectively |

For `LINK_REPLACED`, report `content=equal|differs|type_mismatch`; compare regular file bytes with `cmp -s` and
matching directory contents with Git's read-only `diff --no-index --exit-code --no-ext-diff --no-textconv`, with file
mode differences disabled. Discard diff stdout and capture stderr only; only diagnostic-free exits 0/1 mean equal/different; any
diagnostic or other exit is inspection failure, so unreadable nested content is not silently called different. A comparison failure returns `LINK_INSPECTION_FAILED` exit 2, not an equality claim.
Never execute a configured external diff or textconv. No modification is proposed by check output.

Stdout uses one-line sentinels with fixed entry names, stable codes and actions, for example:

```text
[CONTEXT_LINK: PRODUCT.md code=LINK_REPLACED content=differs action=MERGE_INTO_SOURCE]
[CONTEXT_EXCLUDE: PRODUCT.md code=EXCLUDE_OK action=NONE]
[CONTEXT_LINK_RESULT: mode=check code=LINK_PROBLEMS exit=1 action=INSPECT_REPORTED]
```

A terminal result is always emitted: `LINK_CLEAN`/`NONE` exit 0, `LINK_PROBLEMS`/`INSPECT_REPORTED` exit 1, or the
specific failure code/action exit 2. Exit 1 covers unresolved link states and missing excludes; successful repairs
in link mode do not count as problems. Stderr carries bounded failure details without changing the stdout schema.
No JSON mode or devkit Python dependency is introduced.

### 3.4 Delivery scope and acceptance

`target-docs.md` lists exact Living Spec, guide and source owners. Development adds one script, extends the existing
projection test and adds subprocess integration coverage under `packages/devkit-catalog/tests/integration/bundles/`.
No new Python feature, dependency edge, package or test tier is introduced.

- **AC-01**: Given present optional source entries in an ordinary repository, when link mode runs twice, relative
  links resolve to that source and the second run changes no links or exclude bytes.
- **AC-02**: Given a root file, directory, foreign/dangling link or tracked root entry, when either mode runs, the
  occupied entry is preserved and its stable state is reported; eligible other entries still progress in link mode.
- **AC-03**: Given a linked worktree and source tracked on its branch, when invoked from its subdirectory, links point
  inside that worktree and use the common exclude file; no link points into the main checkout.
- **AC-04**: Given every classification above, including atomic-save replacement with equal/different content and a
  replaced `.impeccable` directory, when `--check` runs, codes/actions and exit precedence match the contract and the
  filesystem/index/HEAD remain unchanged. A resolving foreign link whose target is the expected path plus one or
  more trailing newline bytes MUST be `LINK_WRONG_TARGET`; exact-target capture preserves those bytes without
  printing them.
- **AC-05**: Given spaces, ` -> `, leading-dash arguments after `--`, lexical `..`, source symlink escapes,
  wrong source types, no repository and disabled symlinks, when run, containment/preflight behavior matches 3.1.
- **AC-06**: Given an exclude file without final newline, existing exact patterns, unrelated patterns or a held
  helper lock, when link mode runs, existing bytes survive, exact lines are deduplicated and a held lock fails
  before exclude writes. Injected I/O failure reports exit 2 and retained partial effects without overwrite under the quiescence precondition. Tests preserve occupied
  directory contents as well as root identity, and instruction assertions require the no-concurrent-writer limitation.
- **AC-07**: Given selected bundle projection to supported hosts, when synchronized, the script is byte-identical
  under managed/shared/Claude skill directories and runs via `sh`; it introduces no runtime dependency or asset kind.
- **AC-08**: Given the guide and orchestration text, when reviewed against the PADR, mutating setup is requested and
  shows exact excludes, check mode is read-only inspection, source-side ignore ownership is explicit, replacement
  recovery preserves both versions until user direction, and the local-only absolute-path fallback remains available.

Run POSIX syntax checks and subprocess tests with `sh` and with `dash` where available. GNU and BusyBox utility
coverage is reported separately from macOS evidence, never inferred from `dash` alone. Required repository lint,
type checks and `just test-affected` with full fallback run in Development.

Non-Goals: a devkit CLI command, Python runtime feature, installer, asset kind, config key, context-file creation or
content editing, automatic replacement repair, root `.gitignore` edits, staging/untracking, source-side ignore
installation, Windows beyond an explicit unsupported result, run/question/load routing or upstream-fallback changes.

Host technical decision: setup requires quiescence rather than adding non-POSIX link flags or a Git-apply
implementation. The choice preserves the requested dependency boundary and reports its concurrency limitation.

Size `M`: the script and its tests/guide/contracts remain one feature spec. No concrete deferred implementation is
created by these exclusions. Source-side retention setup is existing consumer responsibility rather than a follow-up
feature. The unseen consumer pilot and live upstream/editor save behavior remain unverified observations.
