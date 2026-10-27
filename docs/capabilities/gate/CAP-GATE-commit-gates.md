---
id: CAP-GATE-commit-gates
title: "Commit Gates"
summary: "Pluggable commit hooks, shell wrappers, layered policies, and snapshot verification."
area: gate
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/gate/usecases/hooks/hooks.py
  - packages/devkit/src/devkit_agt/features/gate/usecases/hooks/local_config.py
created_at: 2026-10-17
usecases:
  - UC-keep-the-living-spec-consistent
---

# [CAP-GATE-commit-gates] Commit Gate: Architecture Overview

**Package**: `devkit_agt.features.gate` (`devkit gate` CLI). Commands, exit codes and error codes: [Gate Reference](../../development/reference/gate.md).
**Related**: `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions`, `CAP-GOV-rules-engine`.

## 1. Overview and Objectives

`devkit_agt.features.gate` runs policy at Git's commit hooks. It owns the **system**: hook wrappers, configuration layering, gate discovery and the stage runner. It owns almost no **policy**: gates that encode a team's or a person's commit rules ship in content wheels as `kind = "gate"` bundle assets, so installing a wheel, selecting its bundle and running `devkit sync` adds them, exactly as rules are added to `devkit_agt.features.rules`.

1. **System in the core, policy in bundles.** The only built-ins are the gate system's own integrations: the rule engine's commit-time check (`rules-check`, policy-free: the rules it evaluates ship in bundles and are tuned in `[rules]`), the runner of the project's own verification commands (`verify-commands`, policy-free: the project supplies the commands) and the non-empty message check (`message-nonempty`). Identity checks, timestamp handling, message conventions and similar rules belong to the content wheels that need them.
2. **Shared dispatchers, runtime discovery.** Writing syncs install POSIX dispatchers and a separate `20-devkit` script for each stage with enabled gates. Each commit discovers gates from the installation receipt; sync also appends the commented tables of new gates to `devkit.config` ([Settings Template](#6a-settings-template)).
3. **Deployed with their preset.** Installing a wheel makes its gates available; a preset that contains them deploys them once it is selected, by `devkit add` or, for a bundle that declares `auto_select`, by default; a gate may additionally ship disabled and require `enabled = true` in configuration.
4. **Fail closed where Git can still refuse.** In `pre-commit` and `commit-msg`, refusals, configuration errors and missing or drifted gate files block the commit. `post-commit` runs after the commit exists, only reports, and always exits `0`; its problems are rendered as warnings (`[WARN]`, `CONTINUE`), never as errors, so an agent does not mistake a reported problem for a failed commit.
5. **One error format.** Gate refusals and configuration problems are Agent Advisory Protocol errors (`devkit.advisory`).

## 2. Library

```python
from devkit_agt.features.gate import Stage, load_gate_project, run_hook

project = load_gate_project(root)  # any directory inside the work tree; project.root is its top level
project.validation.errors          # every registry, configuration and settings problem (what `gate status` reports)

report = run_hook(root, Stage.PRE_COMMIT)            # what `devkit gate run pre-commit` runs
report = run_hook(root, Stage.COMMIT_MSG, ["MSG"])   # args are the hook arguments Git passes
report.ok, report.problems, report.exit_code         # exit_code: the highest exit code among the problems
```

`load_gate_project` collects problems instead of raising them; only a failed Git query raises (`GitError`, `GIT_FAILED`). `run_hook` loads the project and runs the stage with `run_stage`, so the CLI (a thin layer over these two) and a library caller cannot diverge. The steps underneath are public too: `project_registry`, `load_gates_config`, `validate_gates` and `run_stage`. `python -m devkit_agt.features.gate` is the gate CLI alone, which the wrappers exec.

## 2a. Built-in Gates

| Gate | Stage | Order | Default | Behavior |
| --- | --- | --- | --- | --- |
| `rules-check` | `pre-commit` | 100 | on (skipped when nothing is staged) | Checks the staged tree against the project's rules, as `devkit rules check --staged` does, and refuses the commit on an error-severity violation. |
| `verify-commands` | `pre-commit` | 200 | on (skipped while `commands` is empty) | Runs the project's verification commands and refuses the commit when any fails. |
| `message-nonempty` | `commit-msg` | 900 | on | Refuses a message that is blank (whitespace only) above any scissors line. |

`rules-check` runs the rule engine on what is committed, in the hook's own process, so every project that installs the hooks checks its rules at commit time without configuring a command:

- It takes the snapshot `devkit rules check --staged` takes (`CAP-GOV-evaluation-lifecycle`): the index of the commit being made (`git commit -a` and `git commit <paths>` included), with its `.devkit/config.toml`, receipt and tracked rules, and evaluates the linter phase on the files the commit changes. When the working tree holds exactly what is staged (the usual case: everything changed is committed) it evaluates in place, so its cost follows the commit, not the repository; partial staging or an untracked file under `.devkit/` materializes the tree first. Unstaged edits and per-clone configuration cannot change the result; untracked files outside `.devkit/` are visible in place. A commit that stages nothing is skipped.
- Unfixed error-severity violations refuse the commit with `GATE_RULES_FAILED` (`INPUT_ERROR`, exit `1`: correct the staged change and commit again): per violation a `[DETAIL]` `<RULE-id> <file>:<line>: <message>` and, when the rule gives one, `  fix: <remediation>`, the first 20 listed and the rest counted. Warning-severity violations pass with one `GATE_RULES_WARNINGS` warning listing them the same way.
- A run that could not complete (rules that cannot load, an invalid `[rules]` policy, a rule that raised) did not judge the commit: it is `RULES_RUN_FAILED` (exit `2`) with each problem as a detail, `AUTO` with their fix when every problem is `AUTO` with the same one (managed rule files missing in a fresh worktree or clone: `devkit sync`), else `MAINTENANCE`. An invalid `[rules]` table is `RULES_CONFIG_INVALID`.
- While the rules run, the hook's `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE` and `GIT_PREFIX` are removed from the process environment and the index is passed as `DEVKIT_GIT_INDEX_FILE`, as `verify-commands` does for its commands; the environment is restored afterwards.
- Tune the rules, not the gate: severities, phases (a rule parked in `hygiene` is not evaluated at commit time), settings and `exclude` in `[rules]`. A repository that keeps rules out of its commits sets `enabled = false` in `[gates.settings.rules-check]`, or a clone does so in `devkit.config`.

`verify-commands` runs the repository's own checks (formatter, linter, type checker, fast tests) as the final verification before a commit:

```toml
# .devkit/config.toml: the team's commands; a clone overrides them in .git/devkit.config
[gates.settings.verify-commands]
commands = ["just lint-check", "just check"]
```

Hooks run with Git's environment, where the project's `.venv/bin` is usually not on `PATH`: call project tools through `uv run` or a recipe runner (`just`), never as bare `devkit`, `pytest` or `ruff`.

- Each command line runs with `sh -c` from the top level of the work tree, in order, through `devkit_agt.features.compact.run_command`: the full output goes to a log file and the refusal carries only the compact view. Every command runs, so one attempt reports every failure.
- A failure is `GATE_VERIFY_FAILED` (`INPUT_ERROR`, exit `1`: fix what failed and commit again) naming the failed commands, with per command a `[DETAIL]` `command: <line>  exit=<n>  log=<path>`, then its recognized summaries, its failed tests, its last 10 output lines (summaries left out) and the error blocks of nested `devkit` commands (`  > ` lines). `RUN_SLOW_COMMAND` notices of the runs are returned as they are.
- A nested `devkit` command that could not do its job (exit `2` with an error block of its own: rules that cannot load, a worktree or checkout that needs `devkit sync`) did not judge the commit, so the gate raises `GATE_VERIFY_NOT_RUN` (exit `2`) with the same details instead of the `GATE_VERIFY_FAILED` refusal. It is `AUTO` with the relayed fix when every relayed error is `AUTO` with the same one (managed files missing: `devkit sync`, then commit again), else `MAINTENANCE`.
- The commands see the working tree, not the index. When tracked files have unstaged changes or untracked files exist, the gate adds a `GATE_VERIFY_UNSTAGED` notice (in a refusal, a final `note:` detail) listing up to 10 of them, and does not refuse for it. A check that must match the commit exactly evaluates the index itself, as `rules-check` and `devkit rules check --staged` do: it reads `.devkit/config.toml`, the receipt and the synchronized rules from the staged tree (in place when the working tree holds exactly that tree, else from a materialized copy), and so cannot depend on unstaged edits or per-clone configuration (`CAP-GOV-evaluation-lifecycle`).
- The hook's `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE` and `GIT_PREFIX` are removed from the commands' environment, so a test suite that runs Git in its own repositories is not pointed at this commit's index. The index is passed as `DEVKIT_GIT_INDEX_FILE` instead; devkit's staged snapshot uses it for this repository only (`devkit_core.core.git.commit_index`), so `devkit rules check --staged` evaluates exactly what `git commit -a` or `git commit <paths>` commits, a temporary index.
- `devkit gate status` shows the gate's setup: `commands=<n>`, or `commands=0 (skipped: no commands configured)` while
  the list is empty (`setup` in its JSON gate row).
- Keep the list to what is quick enough for every commit; slower suites belong in CI. Interrupting a command (Ctrl-C, `SIGTERM`, `SIGHUP`) stops it, skips the remaining commands and gates, and aborts the commit: `devkit gate run` exits `128 + N` (`130` for Ctrl-C), as `devkit run` does.

`message-nonempty` sees the message before Git's cleanup. Whether Git strips comment lines depends on how the commit was made (`git commit -m "#123 fix"` keeps the `#` line; the editor template strips it; `core.commentChar` changes the character), so the gate refuses only a message that is blank above the scissors line, with `GATE_MESSAGE_EMPTY` (`INPUT_ERROR`, exit `1`: write a subject line and commit again). A message that is empty only once comments are stripped is left to Git, which aborts such a commit itself unless `--allow-empty-message` is given.

## 3. Hook Wrappers

`devkit sync` and `devkit gate install` prepare `pre-commit`, `commit-msg` and `post-commit` dispatchers in
`<common-git-dir>/hooks`, shared by every worktree. `install`, `status` and `uninstall` resolve this directory.
Each dispatcher runs executable regular files (including links to regular files) directly under `<hook>.d/`
in bytewise filename order. It finds that directory beside itself by its stage's name, not by its own filename, so a
dispatcher another tool renamed still runs its entries. Hidden files, non-executable files and directories are ignored; no recursion or
shell sourcing occurs. Scripts may use any interpreter through their shebang. Git's arguments, working directory,
environment and stdin are inherited. Only these three commit stages are supported; adding stages with stdin
payloads such as `pre-push` requires a replay contract so every child receives the full input.

```text
<common-git-dir>/hooks/
├── pre-commit                  # managed POSIX dispatcher
├── pre-commit.devkit-preserved # preserved existing hook, when present
└── pre-commit.d/
    ├── 00-legacy               # managed adapter invoking ../pre-commit.devkit-preserved
    ├── 10-pre-commit           # the pre-commit framework's hook, when one was installed
    ├── 15-custom-check         # optional user script before devkit
    ├── 20-devkit               # managed gate entry, when the stage has enabled gates
    └── 30-custom-check         # optional user script after devkit
```

- **Order and failure**: `pre-commit` and `commit-msg` stop at the first failed script and preserve its exit code.
  `post-commit` reports each failed script as `GATE_HOOK_SCRIPT_FAILED` on stderr, continues with the remaining
  scripts and exits `0`; the commit already exists.
- **Empty stages**: sync and install always prepare dispatchers and `.d` directories, but add `20-devkit` only
  for stages with at least one enabled gate. Registry or configuration errors install the entry for all stages
  so commit-time validation reports the problem. Enabled gates that skip at runtime still count: for example,
  `verify-commands` stays enabled even without commands. With defaults, `pre-commit` and `commit-msg` have
  entries and `post-commit` does not. An existing managed entry is retained even if this worktree has no enabled
  gates, since another worktree shares it. Run sync after enabling a gate in a stage that has no entry yet;
  until then `devkit gate status` warns with `GATE_HOOK_ENTRY_MISSING` naming the stage and its gates.
- **Gate entry**: `20-devkit` selects the worktree's `.venv/bin/python` when devkit is installed there,
  otherwise the absolute fallback recorded by install (`sys.executable` or `--python`), then runs
  `python -m devkit_agt.features.gate run <stage>` through a small `<python> -P -c` bootstrap in the same process.
  `-P` prevents repository modules from shadowing imports. The fallback must import `devkit_agt.features.gate` at
  install time (`GATE_PYTHON_INVALID`); it does not depend on `PATH`. When at commit time the interpreter
  is missing or cannot import `devkit_agt.features.gate` (removed, or a broken or incompatible devkit), the entry prints
  `GATE_INTERPRETER_UNAVAILABLE` with `[DETAIL] python=<path>` and the reason, never a traceback, and exits
  `2` in a blocking stage (an `[ERROR]`: the gates could not run, not a refusal) and `0` in `post-commit`
  (a `[WARN]`).
- **Existing hooks**: regular files are automatically renamed to `<hook>.devkit-preserved`, retaining their
  executable mode, and chained through `00-legacy`. `GATE_HOOK_PRESERVED` is returned as a warning only when a hook
  moves. Keeping the preserved hook beside the original reduces directory-relative breakage, but scripts depending on
  their original filename still need review. Non-executable hooks stay inactive. Symlinks and non-regular hooks
  require explicit `install --force` (`GATE_FOREIGN_HOOK`); automatic sync skips installation instead.
  An existing preserved hook is never overwritten (`GATE_BACKUP_EXISTS`). `00-legacy` and `20-devkit` are reserved;
  foreign files there, or symlinked script directories, are refused (`GATE_HOOK_LAYOUT_INVALID`).
- **The pre-commit framework**: devkit never preserves a hook as `<hook>.legacy`, the name `pre-commit install`
  moves a foreign hook to and its hook runs first (with `PRE_COMMIT_RUNNING_LEGACY=1`, refusing to run inside it).
  Either install order works:
  - devkit after pre-commit: a hook containing `# File generated by pre-commit` becomes the `10-pre-commit` entry,
    where it finds no `<hook>.legacy` of its own; a hook it was chaining from `<hook>.legacy` becomes the preserved
    hook. A `10-pre-commit` that is not a pre-commit script is refused (`GATE_HOOK_LAYOUT_INVALID`).
  - pre-commit after devkit: pre-commit moves the dispatcher to `<hook>.legacy` and runs it first; the dispatcher
    still runs its entries and, run that way, skips entries written by pre-commit, which then runs its hooks once.
    `devkit gate status` reports no missing entry for this layout. The next install or sync moves pre-commit's
    hook to `10-pre-commit`, removes the dispatcher at `<hook>.legacy` and writes the dispatcher at the hook path.
  - A `<hook>.legacy` an earlier devkit preserved is moved to `<hook>.devkit-preserved` (or, when it is a
    pre-commit script, to `10-pre-commit`) by the next install or sync, also when the dispatcher was deleted
    by hand while devkit's `00-legacy` still chains it.
  - `00-legacy` exists exactly while a hook is preserved: install rewrites it to run `<hook>.devkit-preserved`
    (an earlier adapter ran `<hook>.legacy`, which pre-commit may later fill with the dispatcher, a loop) and
    removes it when no hook is preserved.
- **Writing**: mutations, and the settings template refresh in `devkit.config`, are serialized by a clone-wide
  `devkit-hooks.lock` (an exclusive `devkit_core.core.locks.file_lock`, waited for without a bound). Scripts are LF-only
  executable files, replaced atomically without writing through symlinks. Identical scripts are left untouched.
  All stages are checked for conflicts before writing. If dispatcher replacement fails after a hook moves,
  the original hook is restored. A dry run (`post_sync_preview`) takes no lock and writes nothing, the lock file
  included.
- **Automatic installation**: the `devkit.post_sync` extension `gate-hooks` runs after writing syncs, including
  `--locked`; it does not run on `--dry-run` or `--check`, or install outside a Git worktree. When it changed the
  hooks it returns one line, `gate hooks: <stage>: <change>; ...` (each move, then `<stage>: installed` per stage
  whose files changed); hooks already in place report nothing. `post_sync_preview` reports the same changes as
  `gate hooks would change: ...` without writing, or the `GATE_HOOK_INSTALL_SKIPPED` warning a sync would report. Unsafe layouts,
  custom `core.hooksPath` and installation failures produce `GATE_HOOK_INSTALL_SKIPPED` warnings with the
  reason code and remediation. Automatic sync retains each existing fallback that is executable and can import
  `devkit_agt.features.gate`, validated under the clone-wide lock, so a linked worktree does not replace a valid shared fallback
  with its own disposable interpreter. Missing or invalid fallbacks of active entries use the validated sync
  interpreter. Explicit `devkit gate install` replaces active fallbacks with `sys.executable` or its `--python`
  argument. The sync succeeds unless warnings trigger `--strict`.
- **Removal**: uninstall removes owned `20-devkit` entries. If user entries remain, it keeps the dispatcher,
  `00-legacy` and the preserved hook. Otherwise it removes the dispatcher and managed adapter and restores the
  hooks it chained: a `10-pre-commit` entry becomes the hook again, with the preserved hook as its `<hook>.legacy`
  (pre-commit's migration mode); without one, `<hook>.devkit-preserved` becomes the hook. When that `<hook>.legacy`
  already exists, the preserved hook stays where it is and uninstall prints that nothing runs it. When
  `pre-commit install` moved the dispatcher to `<hook>.legacy`, uninstall works on that layout: pre-commit's hook
  stays, the dispatcher (and an older pre-commit copy in `10-pre-commit`) is removed and the preserved hook becomes
  `<hook>.legacy`. It never deletes user entries, including non-executable files or directories.
- **`core.hooksPath`**: a value pointing elsewhere is left unchanged. Explicit install refuses
  (`GATE_HOOKS_PATH_SET`), sync reports a skipped-install warning, and status reports the setting with a
  `GATE_HOOKS_PATH_SET` warning naming the enabled gates that do not run. Uninstall
  still cleans the common hooks directory. Remediation depends on scope: unset a local or worktree value in
  that scope, override global/system values for this clone, or remove command-scope options/environment.
- **Bypass**: `git commit --no-verify` skips `pre-commit` and `commit-msg` as Git defines.

## 4. Gate Contract

```python
class Gate(Protocol):
    id: str
    description: str
    stage: Stage                # pre-commit | commit-msg | post-commit
    order: int                  # lower runs first within the stage
    enabled_by_default: bool
    settings: Any               # dataclass instance with defaults, or None

    def run(self, ctx: GateContext) -> GateResult | None: ...
```

- **Passing and skipping**: return `GateResult.passed(note)` or `GateResult.skipped(reason)`; `None` means passed. `GateResult.passed(note, notices=[...])` also returns warnings and notices (`AdvisoryError` at level `WARNING` or `NOTICE`; an `ERROR` is lowered to `WARNING`), which `devkit gate run` prints without blocking the commit, unless `DEVKIT_STRICT=1` and one is a warning. A notice that is not an `AdvisoryError` fails the gate with `GATE_RESULT_INVALID`. Each outcome is logged and shows as an `[INFO]` line under `-v`. A `GateResult` cannot carry `FAILED` (constructing one raises `GateResultError`, `GATE_RESULT_INVALID`, `MAINTENANCE`), and any other return value fails the gate with the same code.
- **Refusing**: raise `GateRefusedError(message, *details, code=..., fix=..., target_files=...)`: message first, remediation in `fix`, and the gate's own code (default `GATE_FAILED`). It is `BLOCKED` and exits `1` (`FINDINGS`): the negative result of a check that ran, a policy the committer must not work around. When correcting the commit is the remedy (a failed check of its content), raise its subclass `GateFindingsError` instead: `INPUT_ERROR`, also exit `1`, as the built-in gates do.
- **Status**: `setup(settings)` returns what `devkit gate status` shows after the gate's row for its effective settings (default `None`: nothing), such as `verify-commands`' command count. Any other `AdvisoryError` fails the gate as it is (most exit `2`: the check could not run); any other exception, and `SystemExit` from a gate that calls `sys.exit()`, is wrapped as `UNEXPECTED_ERROR` (exit `2`), and the stage's later gates still run. Every failed gate therefore reports an advisory. `KeyboardInterrupt` is not caught: it aborts the run, and a blocking stage exits nonzero. Neither is `devkit_agt.features.compact.CommandInterrupted`, though it is a `SystemExit`: a gate whose `run_command` is interrupted aborts the run the same way, exiting `128 + N` for signal `N`.
- **Context**: `ctx.repo_root` (top level of the work tree), `ctx.git_dir` (this worktree's git dir, for `MERGE_HEAD`, rebase state and the like), `ctx.common_git_dir` (shared by every worktree), `ctx.stage`, `ctx.args` (hook arguments), `ctx.settings` (the gate's effective settings) and `ctx.message_file` for `commit-msg`.
- **Ordering**: gates in a stage run by `(order, id)`. Message transforms use `order < 100`, checks default to `100`, and the built-in `message-nonempty` runs at `900` so it sees the transformed message. A `post-commit` gate that rewrites `HEAD` must take a low order so later gates observe the final commit.
- **No short-circuit**: a failing gate does not stop later gates, so one commit attempt reports every refusal.

A gate is written as a **plugin package**, a directory like a rule package (`CAP-GOV-rule-authoring`): every `.py` file in it is a module of one package (files under `tests/`, `test_*.py` and `*_test.py` excepted, so tests live beside the code), `__init__.py` is optional, and modules import each other relatively (`from .limits import max_files`). For example:

```text
gates/
  staged_file_limit/
    gate.py              # class StagedFileLimitGate(BaseGate)
    limits.py            # helpers, imported as `from .limits import ...`
    tests/test_limits.py # never imported by devkit
```

Gate packages are loaded like rule packages, with `devkit_core.core.plugins.load_subclasses`: every module of the package is imported and every concrete `BaseGate` subclass defined in one of them is instantiated without arguments, in module then definition order. `BaseGate` is abstract, so a shared base class that leaves `run` abstract is skipped. Loading is atomic per package: if any module fails to import, or any gate of the package fails to instantiate or has invalid metadata (`id`, `stage`, `order`; `GateDefinitionError`), the package contributes no gate and the failure is reported as `GATE_LOAD_FAILED` naming the package. A gate's `settings` dataclass fields may be `int`, `float`, `str`, `bool` or `list[str]`, each optionally `| None`: the type vocabulary and checker of rule settings (`devkit_agt.features.rules.models.settings`). Any other annotation is a defect of the gate (`GATE_DEFINITION_INVALID`, `MAINTENANCE`). A gate package may import from any package installed in the same environment, so a content wheel can keep its logic in a library module and ship only a thin gate package.

## 5. Distribution

A bundle declares a gate as an asset:

```toml
[[assets]]
id = "staged-file-limit"
kind = "gate"
source = "gates/staged_file_limit"     # a plugin package directory; a file is BUNDLE_INVALID

[presets.commit]
assets = ["staged-file-limit"]
```

`devkit sync` copies the selected gate packages to `.devkit/managed/<bundle>/` (a project override under `.devkit/overrides/<bundle>/` replaces the managed copy of each file it overrides) and records their files in `.devkit/installation.json`. At commit time the registry reads the receipt with `devkit_dist.features.project.repositories.receipt` (strict: a malformed receipt or an unsafe path is an error) and loads every `kind = "gate"` asset as one package whose modules are its listed `.py` files, whatever their names (test files excepted). Packages are found and their files checked with `devkit_dist.features.project.repositories.receipt.verified_asset_packages`, as for rule packages: a file with a `files` entry in the receipt must match its SHA-256; only a project override under `.devkit/overrides/` may lack one and is then loaded as it is; any other file without one is refused, and a package with a refused file is not loaded.

| State | Effect at commit time |
| --- | --- |
| Wheel installed, bundle not selected | Gate absent |
| Bundle selected, synchronized | Gate loaded; runs if enabled |
| Receipt lists a gate file the disk lacks, or the file differs from its recorded hash | Blocking stages fail with `ASSET_FILE_INVALID` (the core error, passed through); fix `devkit sync`, or `devkit override create <bundle>:<asset>` to keep a deliberate edit |
| Receipt is malformed or lists a path outside the project | Blocking stages fail with `RECEIPT_INVALID` (restore the receipt from version control, then `devkit sync`) |
| Gate package fails to import, or two gates share an id | Blocking stages fail with `GATE_LOAD_FAILED` |

## 6. Configuration Layers

Two files contribute a `[gates]` table; the later layer wins:

| Order | File | Tracked | Purpose |
| --- | --- | --- | --- |
| 1 | `.devkit/config.toml` | Yes | Team policy shared by every clone |
| 2 | `<common-git-dir>/devkit.config` | No | Per-clone and personal overrides, shared by every worktree |

Tables are deep-merged; a scalar or array in a later layer replaces the earlier value. `devkit.config` uses the same TOML shape and accepts only `[gates]`.

```toml
# .devkit/config.toml
[gates.settings.staged-file-limit]
max_files = 50

# .git/devkit.config
[gates.settings.staged-file-limit]
max_files = 200

[gates.settings.message-nonempty]
enabled = false
```

- `enabled` is reserved in every gate table and overrides `enabled_by_default`.
- Other keys must match the gate's settings dataclass fields and their annotations: an integer for `int`, a number for `float` (an integer becomes a float), a string, a boolean, an array of strings for `list[str]`; no other array or value type, and never `null` (TOML has none) unless the field is `| None`. Settings are validated for every installed gate, whatever its stage and whether it is enabled; unknown keys and wrong types fail every blocking stage, and the gate itself is skipped.
- A file that cannot be read or parsed is the core `ConfigError` (`CONFIG_INVALID`), passed through unchanged; a malformed `[gates]` table or invalid settings are `GateConfigError` (`GATE_CONFIG_INVALID`), a subclass of it.
- An entry for a gate that is not installed fails blocking stages, so a typo or a forgotten `devkit sync` cannot silently disable policy.
- `devkit` passes `[gates]` through untouched, as it does `[rules]` and `[workflow]`.

The tracked `.devkit/config.toml` template (`devkit config template`) lists the built-in gates' commented
`[gates.settings.<id>]` tables at their defaults, from `config_tables` in
`devkit_agt.features.gate.usecases.hooks.local_config` (the `devkit.config_tables` entry point `gates`); bundle gates
appear in the clone-local template below.

## 6a. Settings Template

`devkit gate install` makes `<common-git-dir>/devkit.config` list every installed gate as a commented table, so a
per-clone setting is changed by uncommenting lines in place: the table header and only the keys that change. An
uncommented key replaces the `.devkit/config.toml` value as a whole (an array too); a key left commented keeps it.

```toml
## pre-commit gate, on by default: Refuses a commit that stages too many files.
# [gates.settings.staged-file-limit]
#   enabled = true
#   max_files = 50  # integer; Most files one commit may stage

## pre-commit gate, on by default: Run the project's verification commands (format, lint, type check, tests) before a commit.
# [gates.settings.verify-commands]
#   enabled = true
##   commands: set in .devkit/config.toml; adding commands = <value> here replaces it  # array of strings; Shell commands run in order from the repository root; empty skips the gate
```

- **Layout**: prose is commented twice (`##`), the table header and keys once (`#`), with the keys indented under
  their header. Uncommenting a whole table in an editor (which removes one `#`) leaves the prose a comment and yields
  valid TOML. A key uncommented without its header belongs to whatever table precedes it, so the header is
  uncommented with the keys; the file's own header says so.
- **Content**: per gate (in stage and order), its stage, default state and description, its header, `enabled` at its
  default, then each settings field at its default with its type and the field's `metadata["help"]` when the gate
  declares one (`field(default=50, metadata={"help": "..."})`). A field whose default is `None` shows a placeholder
  of its type and `unset by default`; TOML has no null, so uncomment it only with a value. Gates that fail to load
  are left out (`devkit gate status` reports them).
- **Project keys**: a key (`enabled` included) that `.devkit/config.toml` sets for the gate when its table is written
  is not offered at its default, since uncommenting it would replace the team's value (an empty `commands` skips
  `verify-commands`, and every commit would pass unverified). It is a `##` line naming it as set by
  `.devkit/config.toml`, without the value, so uncommenting the whole table keeps the project's value and nothing
  copied goes stale. A key the project starts setting after its table was written still shows its default, since no
  line is rewritten; uncommenting only the keys that change, as the file's header says, keeps it in effect. A
  `.devkit/config.toml` whose `[gates]` cannot be read skips the refresh (below).
- **Append-only**: a missing file is created with a header and every table. An existing file only gets the tables of
  gates whose `[gates.settings.<id>]` header it does not mention yet, commented or not; no existing line is changed
  or removed, so uncommented values stay where the developer put them. A table of a gate that is later removed
  stays; once uncommented, it fails blocking stages like any entry for a gate that is not installed.
- **Refresh**: `install` (safe to re-run) prints `[CONFIG: template=<created|updated|unchanged|skipped> path=<path>]`.
  After every writing sync, the `devkit.post_sync` extension `gate-hooks` installs hooks and refreshes the template in Git worktrees, so a gate that `devkit add` or an upgrade brings in appears without another `install`. The
  hook imports the receipt's gate packages to read their settings, as every commit already does, and reports nothing
  unless it skips.
- **Skipped**: a `devkit.config` that is a symbolic link, not a regular file or not UTF-8 is never written; nor is
  one whose tables would need a `.devkit/config.toml` with a `[gates]` table that cannot be read or parsed. `install`
  and the hook report `GATE_CONFIG_TEMPLATE_SKIPPED` (`GateTemplateNotice`, a warning) and succeed. A file that
  cannot be written, or any other failure of the refresh, is reported the same way, so the hook notices of the same
  run (`GATE_HOOK_PRESERVED`) are never lost to it; a settings default TOML cannot represent is left out of its table.
