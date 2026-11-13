---
id: PROP-uiux-improve-impeccable-context-links
title: Link tracked Impeccable context through a bundled POSIX script
summary: The app-uiux-improve bundle ships a POSIX sh script that links a project's tracked Impeccable context (PRODUCT.md, DESIGN.md, .impeccable/) into the repository root as git-excluded relative symlinks and checks them, so the context survives worktrees and clones without a second copy.
status: draft                         # draft | reviewing | accepted | rejected
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

Consumer pilot on 2026-11-13 (a SvelteKit/FastAPI consumer repository, commits `dc7ffb4` and `644e821` on its
`impeccable-context` branch):

- The tracked source moved to `docs/materials/impeccable/` (`PRODUCT.md` plus a `README.md`; `DESIGN.md` is
  deliberately absent because a steering document owns the visual style).
- devkit docs rules treat `docs/materials/` as free-form, so a non-devkit-format file passes lint there.
- The root `PRODUCT.md` is a relative symlink to `docs/materials/impeccable/PRODUCT.md`, created by hand with
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

## 2. Technical Spike Questions

- **Q1 (authority)**: `ADR-impeccable-session-authority` lists the constraint "Add no runtime, installer or vendored
  upstream text to devkit" and limits setup to user-requested actions. Does a consumer-side link script fall under
  that constraint? Does running it need a new ADR that supersedes the setup clause in part? Can the coordinator run
  the read-only check mode on its own initiative, for example before briefing a session, or only on the user's
  request?
- **Q2 (default source)**: should the default source be the fixed `docs/materials/impeccable`, a Git config key read
  with `git config` (for example `impeccable.source`), or a devkit configuration value? A devkit value contradicts the
  POSIX-sh-and-git dependency limit, because `sh` cannot read `.devkit/config.toml` without devkit. `docs/materials/`
  is free-form only in devkit docs consumers, so a consumer without devkit docs needs the argument.
- **Q3 (projection)**: does sync project a non-Markdown file under `skills/app-uiux-improve/scripts/` unchanged to
  every host directory (`.claude/skills/`, `.agents/skills/`) and `.devkit/managed/`? `Content` records the file mode
  and `normal_mode` keeps `0o755` when any execute bit is set, but no bundle ships a script today. Should the
  documented invocation be `sh <path>`, so that it never depends on the execute bit?
- **Q4 (portable link inspection)**: `readlink` and `test -ef` are absent from POSIX.1-2017. Which inspection
  identifies a link's target on macOS, GNU and BusyBox `sh`? Candidates are `ls -ld` parsing and
  `find <path> -prune -type l`.
- **Q5 (`.impeccable/` output)**: with `.impeccable/` linked as a directory, session output (critique snapshots,
  screenshots, `review/`) lands in the tracked source directory. Does upstream's `.impeccable/.gitignore` placement
  keep it untracked there? Or should the script link only the shared files (`config.json`, `design.json`,
  `surfaces/`)?

## 3. Proposed Design & Impact

Script: `skills/app-uiux-improve/scripts/link-impeccable-context.sh` in the bundle source. It is deployed with the
skill and is not a separate asset kind (Q3).

```sh
sh .claude/skills/app-uiux-improve/scripts/link-impeccable-context.sh [--check] [<source-dir>]
```

Behavior to specify in Planning:

1. Root: `git rev-parse --show-toplevel`, so a linked worktree links into its own root. Exclude file:
   `git rev-parse --git-path info/exclude`, which resolves to the common directory. Outside a Git work tree, exit 2.
2. Source: the argument, or the Q2 default, relative to the root. Refuse a source outside the work tree or missing,
   exit 2.
3. Link mode: for each of `PRODUCT.md`, `DESIGN.md` and `.impeccable` present in the source, create a relative
   symlink at the root whose target is the repository-relative source path (`docs/materials/impeccable/PRODUCT.md`).
   - A correct existing link is left as is, so a rerun changes nothing.
   - A root regular file, directory or link to another target is never overwritten. The script reports it and
     continues with the other entries.
   - Add only missing exclude lines: `/PRODUCT.md`, `/DESIGN.md`, `/.impeccable`. Git treats a symlink to a
     directory as a file, so a trailing-slash pattern such as `/.impeccable/` would not match the link.
4. Check mode (`--check`): read-only. Report each entry as one of:
   - missing: source present, no root entry;
   - dangling: root link whose target is absent;
   - wrong target;
   - replaced: a regular file or directory where a link is expected, with whether its content still equals the
     source;
   - stale: root link with no source entry;
   - missing exclude line.
   Exit 0 when clean, 1 when any problem is found, 2 when the check could not run.
5. Output follows the agent-first conventions in spirit: one stdout line per entry with a stable `UPPER_SNAKE` code
   and a deterministic action, for example `LINK_REPLACED PRODUCT.md content=differs action=merge-into-source`.
   Planning fixes the code set.
6. Dependencies: POSIX `sh`, POSIX utilities and `git` only. No Bash features, no `readlink -f`, no `realpath`
   (Q4).

Bundle text impact:

- `references/orchestration.md` "Project files and user requests" names the script as a user-requested convenience
  (Q1).
- The human guide `bundle/README.md` documents the tracked-source layout, first run, per-worktree and per-clone runs,
  and recovery of a replaced link.
- `CAP-DLV-uiux-improvement` rule 1 counts the deployed script; a business rule states the link and check guarantees
  with tests. `UC-improve-an-interface-and-user-flow` gains a setup extension if Planning finds one warranted.

Tests (`packages/devkit-catalog/tests/`): run the script with `sh` against temporary Git repositories and cover:

- first link and idempotent rerun;
- an occupied root;
- a linked worktree created with `git worktree add` sharing the exclude file;
- exclude deduplication;
- each check-mode state, with replacement simulated by write-to-temp-and-`mv`;
- a directory link for `.impeccable`.

Projection assertions extend `test_app_uiux_improve.py`. Run the script under `dash` when available.

Non-Goals:

- A devkit CLI command, Python code or a new asset kind in `devkit-dist`.
- Automatic repair of a replaced link: report it and leave the content decision to the user.
- Moving, creating or editing `PRODUCT.md`, `DESIGN.md` or `.impeccable/` content.
- Tracking the root links, or editing the root `.gitignore`.
- Windows or `core.symlinks=false` checkouts beyond a clear exit-2 report.
- Changes to the run model, question and load routing, or upstream-fallback guidance.

Size `M`: one shell script with integration tests, one reference section, the guide and capability updates in one
feature spec, plus a possible ADR (Q1).

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
