---
id: PROP-uiux-improve-impeccable-context-links
title: Link tracked Impeccable context through a bundled POSIX script
summary: The app-uiux-improve bundle ships a POSIX sh script that links a project's tracked Impeccable context (PRODUCT.md, DESIGN.md, .impeccable/) into the repository root as git-excluded relative symlinks and checks them, so the context survives worktrees and clones without a second copy.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-13
target_area: capabilities/delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/delivery/
    - usecases/delivery/
    - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/
    - packages/devkit-catalog/tests/
  excludes:
    - packages/devkit-dist/
    - packages/devkit-catalog/src/devkit_catalog/design_explore/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-uiux-improve-impeccable-context-links] Link tracked Impeccable context through a bundled POSIX script

## 1. Background & Hypothesis

Impeccable reads `PRODUCT.md`, `DESIGN.md` and an optional `.impeccable/` directory from the project root.
`CAP-DLV-uiux-improvement` and `references/orchestration.md` ("Project files and user requests") treat these files as
consumer-owned and point to upstream's "Project files and git" guidance. The bundle says nothing about where a
consumer keeps them when it does not want them tracked at the root.

Observed problem (`MAT-uiux-improve-pilot`, finding A5): the consumer kept `PRODUCT.md` and `DESIGN.md` local-only
through `.git/info/exclude`. An SDD worktree did not contain them, so the pilot fell back to an in-place branch and
passed main-checkout absolute paths read-only. `SPEC-uiux-improve-bundle-hygiene` AC-06 made that fallback the
instruction. Untracked root files are also lost on a fresh clone.

Consumer pilot on 2026-11-13 (a SvelteKit/FastAPI consumer repository, commits `dc7ffb4` and `644e821`, merged to
its `main` as `e1a50a8`):

- The tracked source moved to `docs/materials/impeccable/` (`PRODUCT.md` plus a `README.md`; `DESIGN.md` is
  deliberately absent because a steering document owns the visual style).
- devkit docs rules treat `docs/materials/` as free-form, so a non-devkit-format file passes lint there.
- On that `main`, the root `PRODUCT.md` is a relative symlink to `docs/materials/impeccable/PRODUCT.md`, made by hand with
  `ln -s docs/materials/impeccable/PRODUCT.md PRODUCT.md`.
- `/PRODUCT.md` and `/DESIGN.md` stay in `.git/info/exclude`. That file lives in the Git common directory, so every
  linked worktree shares the entries, while each worktree still needs its own link.
- The pilot README names "a link script in devkit's `app-uiux-improve` bundle" as the intended replacement for the
  manual step.

Two failure modes remain manual: forgetting the link in a new worktree or clone, and a tool that saves through
temp-file-and-rename. The second replaces the symlink with a regular file, so later edits fork the content silently
while the tracked source looks unchanged. Whether Impeccable or a common editor saves this way is not verified.

Hypothesis: a POSIX `sh` script shipped inside the skill directory removes the manual step and detects the fork. It
needs no devkit runtime, so the bundle stays content-only and independently installable. A devkit CLI command is out
of scope by intent: `devkit-catalog` declares no runtime dependencies and `app-uiux-improve` has no Python feature.

### Related specs and boundary

- `SPEC-uiux-improve-ooux-impeccable` (completed) owns context-file ownership and the user-requested setup list. That
  list allows ignore entries confined to `.impeccable/` paths after showing the exact lines. This proposal adds one
  user-requested action: link the tracked source and add root `.git/info/exclude` entries. It keeps the ownership
  rule and the explicit-direction rule for `PRODUCT.md` and `DESIGN.md` content.
- `SPEC-uiux-improve-bundle-hygiene` (completed) AC-06 passes local-only context as absolute read-only paths. That
  stays the fallback for an unlinked project; a linked worktree makes the root files readable in place.
- `SPEC-uiux-improve-run-model`, `SPEC-uiux-improve-impeccable-routing` and `SPEC-uiux-upstream-fallbacks` (all
  completed) govern route choice, question and load routing and upstream limits. They exclude context-file changes,
  and this proposal leaves them unchanged.
- None of these specs defines where tracked Impeccable context lives or how it reaches the root.

## 2. Planning Decisions

Planning applies `medium` effort; Development remains `medium`. Evidence is in `materials/link-evidence.md`.
No product screen changes are proposed, so there is no Screens draft or UX review.

| Question | Decision | Rejected alternative and consequence |
| --- | --- | --- |
| Q1: authority | `PADR-impeccable-context-links` narrowly extends requested setup to links and exact root excludes; read-only `--check` is inspection the coordinator may run while gathering context. | Treating link creation as an automatic preflight would exceed consumer authority. No Python/runtime package is added. |
| Q2: source | One optional argument, relative to the current worktree root; default `docs/materials/impeccable`. | No Git/devkit configuration key: another state source is unnecessary. A project with another layout passes the argument. |
| Q3: projection | The script stays inside the existing skill asset; document `sh <deployed-skill>/scripts/link-impeccable-context.sh`. | No new asset kind or distribution change; `sh` avoids a dependency on executable-bit preservation. Existing subtree loading includes non-Markdown files. |
| Q4: inspection | Use POSIX `test -L`, then capture `LC_ALL=C QUOTING_STYLE=literal ls -dn ./<fixed-entry>` with an appended non-newline sentinel, remove the sentinel and exactly one output record newline, then remove the exact ` ./<fixed-entry> -> ` prefix and compare the complete target string. | No `readlink`, `realpath`, `test -ef`, field splitting or generic filename parser. GNU's quoting override is harmless to other implementations; clear color-forcing variables. macOS and `dash` probes pass with spaces and ` -> ` in the source path. GNU utility target-capture probes also pass; BusyBox remains Development coverage. |
| Q5: directory | Link `.impeccable` as one directory when present. Source-side upstream retention/ignore rules remain the consumer's responsibility; root-link exclusion does not ignore files reachable through the tracked source path. | Linking selected children would split shared/runtime layout and require upstream-specific inventory maintenance. The helper neither creates source content nor installs source-side ignores. |

These are proposed technical choices within the feature request, pending Host/user plan acceptance.
The PADR supersedes only the existing setup list's restriction on root link/exclude actions; content ownership,
explicit request, task route, host permissions and no implicit Git authority remain unchanged.

## 3. Proposed Design & Impact

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
matching directory contents with Git's read-only `diff --no-index --quiet --no-ext-diff --no-textconv`, with file
mode differences disabled. Capture diagnostic output: only empty-output exits 0/1 mean equal/different; any
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

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr uiux-improve-impeccable-context-links "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept uiux-improve-impeccable-context-links --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff uiux-improve-impeccable-context-links.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
