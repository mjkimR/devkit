# Commit Gate: Architecture Overview

**Package**: `devkit.gate` (`devkit gate` CLI). Commands, exit codes and error codes: [Gate Reference](reference.md).  
**Related**: [Bundle Manifest Specification](../distribution/manifest-spec.md), [Synchronization & Transactions](../distribution/sync-and-transactions.md), [Rule Engine Overview](../rules/overview.md).

## 1. Overview and Objectives

`devkit.gate` runs policy at Git's commit hooks. It owns the **system**: hook wrappers, configuration layering, gate discovery and the stage runner. It owns almost no **policy**: gates that encode a team's or a person's commit rules ship in content wheels as `kind = "gate"` bundle assets, so installing a wheel, selecting its bundle and running `devkit sync` adds them, exactly as rules are added to `devkit.rules`.

1. **System in the core, policy in bundles.** The only built-ins are the gate system's own integrations: the runner of the project's own verification commands (`verify-commands`, policy-free: the project supplies the commands) and the non-empty message check (`message-nonempty`). The rule engine runs at commit time as one of those commands (`uv run devkit rules check --staged`). Identity checks, timestamp handling, message conventions and similar rules belong to the content wheels that need them.
2. **Static wrappers, runtime discovery.** The hook files never change after `devkit gate install`. Each commit discovers the gates from the installation receipt, so `devkit sync` alone changes what runs; it never writes into the hooks directory. It only appends the commented tables of new gates to `devkit.config` ([Settings Template](#6a-settings-template)).
3. **Deployed with their preset.** Installing a wheel makes its gates available; a preset that contains them deploys them once it is selected, by `devkit add` or, for a bundle that declares `auto_select`, by default; a gate may additionally ship disabled and require `enabled = true` in configuration.
4. **Fail closed where Git can still refuse.** In `pre-commit` and `commit-msg`, refusals, configuration errors and missing or drifted gate files block the commit. `post-commit` runs after the commit exists, only reports, and always exits `0`; its problems are rendered as warnings (`[WARN]`, `CONTINUE`), never as errors, so an agent does not mistake a reported problem for a failed commit.
5. **One error format.** Gate refusals and configuration problems are Agent Advisory Protocol errors (`devkit.advisory`).

## 2. Library

```python
from devkit.gate import Stage, load_gate_project, run_hook

project = load_gate_project(root)  # any directory inside the work tree; project.root is its top level
project.validation.errors          # every registry, configuration and settings problem (what `gate status` reports)

report = run_hook(root, Stage.PRE_COMMIT)            # what `devkit gate run pre-commit` runs
report = run_hook(root, Stage.COMMIT_MSG, ["MSG"])   # args are the hook arguments Git passes
report.ok, report.problems, report.exit_code         # exit_code: the highest exit code among the problems
```

`load_gate_project` collects problems instead of raising them; only a failed Git query raises (`GitError`, `GIT_FAILED`). `run_hook` loads the project and runs the stage with `run_stage`, so the CLI (a thin layer over these two) and a library caller cannot diverge. The steps underneath are public too: `project_registry`, `load_gates_config`, `validate_gates` and `run_stage`. `python -m devkit.gate` is the gate CLI alone, which the wrappers exec.

## 2a. Built-in Gates

| Gate | Stage | Order | Default | Behavior |
| --- | --- | --- | --- | --- |
| `verify-commands` | `pre-commit` | 200 | on (skipped while `commands` is empty) | Runs the project's verification commands and refuses the commit when any fails. |
| `message-nonempty` | `commit-msg` | 900 | on | Refuses a message that is blank (whitespace only) above any scissors line. |

`verify-commands` runs the repository's own checks (formatter, linter, type checker, fast tests) as the final verification before a commit:

```toml
# .devkit/config.toml: the team's commands; a clone overrides them in .git/devkit.config
[gates.settings.verify-commands]
commands = ["just lint-check", "just check", "uv run devkit rules check --staged"]
```

Hooks run with Git's environment, where the project's `.venv/bin` is usually not on `PATH`: call project tools through `uv run` or a recipe runner (`just`), never as bare `devkit`, `pytest` or `ruff`.

- Each command line runs with `sh -c` from the top level of the work tree, in order, through `devkit.compact.run_command`: the full output goes to a log file and the refusal carries only the compact view. Every command runs, so one attempt reports every failure.
- A failure is `GATE_VERIFY_FAILED` (`BLOCKED`, exit `1`) naming the failed commands, with per command a `[DETAIL]` `command: <line>  exit=<n>  log=<path>`, then its recognized summaries, its failed tests, its last 10 output lines (summaries left out) and the error blocks of nested `devkit` commands (`  > ` lines). `RUN_SLOW_COMMAND` notices of the runs are returned as they are.
- A nested `devkit` command that could not do its job (exit `2` with an error block of its own: rules that cannot load, a worktree or checkout that needs `devkit sync`) did not judge the commit, so the gate raises `GATE_VERIFY_NOT_RUN` (exit `2`) with the same details instead of the `BLOCKED` refusal. It is `AUTO` with the relayed fix when every relayed error is `AUTO` with the same one (managed files missing: `devkit sync`, then commit again), else `MAINTENANCE`.
- The commands see the working tree, not the index. When tracked files have unstaged changes or untracked files exist, the gate adds a `GATE_VERIFY_UNSTAGED` notice (in a refusal, a final `note:` detail) listing up to 10 of them, and does not refuse for it. A check that must match the commit exactly evaluates the index itself, as `devkit rules check --staged` does: it materializes the staged tree, reads `.devkit/config.toml`, the receipt and the synchronized rules from it, and so cannot depend on unstaged edits, untracked files or per-clone configuration ([Evaluation Lifecycle](../rules/evaluation-lifecycle.md#6-git-snapshot-gates)).
- The hook's `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE` and `GIT_PREFIX` are removed from the commands' environment, so a test suite that runs Git in its own repositories is not pointed at this commit's index. The index is passed as `DEVKIT_GIT_INDEX_FILE` instead; devkit's staged snapshot uses it for this repository only (`devkit.core.git.commit_index`), so `devkit rules check --staged` evaluates exactly what `git commit -a` or `git commit <paths>` commits, a temporary index.
- Keep the list to what is quick enough for every commit; slower suites belong in CI. Interrupting a command (Ctrl-C) aborts the commit.

`message-nonempty` sees the message before Git's cleanup. Whether Git strips comment lines depends on how the commit was made (`git commit -m "#123 fix"` keeps the `#` line; the editor template strips it; `core.commentChar` changes the character), so the gate refuses only a message that is blank above the scissors line. A message that is empty only once comments are stripped is left to Git, which aborts such a commit itself unless `--allow-empty-message` is given.

## 3. Hook Wrappers

`devkit gate install` writes `pre-commit`, `commit-msg` and `post-commit` into `<common-git-dir>/hooks`, the hooks directory shared by every worktree; `install`, `status` and `uninstall` all resolve this one directory. Each wrapper:

1. runs `<hook>.pre-gate` first when it is an executable file (a hook `install` moved aside) and, in a blocking stage, stops with its exit status when it fails;
2. picks the interpreter: `<work tree>/.venv/bin/python` when `devkit` is installed in that environment, otherwise the interpreter recorded at install time;
3. runs `exec "$python" -P -m devkit.gate run <stage> "$@"`.

- **`-P`**: keeps the current directory (the repository, for a hook) off `sys.path`, so a `json.py` or `devkit.py` at the repository root cannot shadow a module the wrapper imports. `-m devkit.gate` imports only the gate area and what it depends on.
- **Interpreter**: the work tree's `.venv` comes first, so every worktree uses its own environment even though the hooks directory is shared. The recorded fallback is `sys.executable` of the installing process, or `--python`; `install` stores it as an absolute path and refuses (`GATE_PYTHON_INVALID`) an interpreter that cannot import `devkit.gate`. Wrappers do not depend on `PATH`, so Git GUIs and agent shells behave like a terminal.
- **Missing environment**: when neither interpreter is usable, a blocking stage exits `2` with a `run 'uv sync'` hint; `post-commit` exits `0`.
- **Existing hooks**: hooks without the managed marker are never overwritten silently. An executable hook, a symbolic link (even a dangling one) or anything that is not a regular file is foreign: `install` refuses (`GATE_FOREIGN_HOOK`), and `install --force` moves it to `<hook>.pre-gate`, where the wrapper keeps running it first. A non-executable regular file, which Git ignores, is inert and is moved aside without `--force`. `uninstall` restores what was moved. An existing backup is never overwritten (`GATE_BACKUP_EXISTS`).
- **Writing**: wrappers are LF-only files with POSIX paths, written to a temporary file and renamed into place, so a symbolic link at the hook path is never written through.
- **`core.hooksPath`**: when its effective value (any configuration scope) points anywhere other than `<common-git-dir>/hooks`, Git would not run the wrappers: `install` refuses (`GATE_HOOKS_PATH_SET`), `status` reports the setting, and `uninstall` still cleans the common hooks directory. The `[FIX]` depends on the scope that sets it (`git config --show-scope`): a `local` value is unset (`git config --unset core.hooksPath`), a `worktree` value is unset with `--worktree`, a `global` or `system` value is overridden for this repository only (`git config core.hooksPath <common-git-dir>/hooks`, which `install` accepts), and a `command` value (`git -c` or `GIT_CONFIG_*` variables) is removed from the environment.
- **Bypass**: `git commit --no-verify` skips `pre-commit` and `commit-msg` as Git defines; the gate system adds no bypass of its own.

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

- **Passing and skipping**: return `GateResult.passed(note)` or `GateResult.skipped(reason)`; `None` means passed. `GateResult.passed(note, notices=[...])` also returns warnings and notices (`AdvisoryError` at level `WARNING` or `NOTICE`; an `ERROR` is lowered to `WARNING`), which `devkit gate run` prints without blocking the commit, unless `DEVKIT_STRICT=1` and one is a warning. Each outcome is logged and shows as an `[INFO]` line under `-v`. A `GateResult` cannot carry `FAILED` (constructing one raises `GateResultError`, `GATE_RESULT_INVALID`, `MAINTENANCE`), and any other return value fails the gate with the same code.
- **Refusing**: raise `GateRefusedError(message, *details, code=..., fix=..., target_files=...)`: message first, remediation in `fix`, and the gate's own code (default `GATE_FAILED`). It is `BLOCKED` and exits `1` (`FINDINGS`): the negative result of a check that ran. Any other `AdvisoryError` fails the gate as it is (most exit `2`: the check could not run); any other exception, and `SystemExit` from a gate that calls `sys.exit()`, is wrapped as `UNEXPECTED_ERROR` (exit `2`), and the stage's later gates still run. Every failed gate therefore reports an advisory. `KeyboardInterrupt` is not caught: it aborts the run, and a blocking stage exits nonzero.
- **Context**: `ctx.repo_root` (top level of the work tree), `ctx.git_dir` (this worktree's git dir, for `MERGE_HEAD`, rebase state and the like), `ctx.common_git_dir` (shared by every worktree), `ctx.stage`, `ctx.args` (hook arguments), `ctx.settings` (the gate's effective settings) and `ctx.message_file` for `commit-msg`.
- **Ordering**: gates in a stage run by `(order, id)`. Message transforms use `order < 100`, checks default to `100`, and the built-in `message-nonempty` runs at `900` so it sees the transformed message. A `post-commit` gate that rewrites `HEAD` must take a low order so later gates observe the final commit.
- **No short-circuit**: a failing gate does not stop later gates, so one commit attempt reports every refusal.

Gate files are loaded like rule files, with `devkit.core.plugins.load_subclasses`: every concrete `BaseGate` subclass defined in the file is instantiated without arguments. `BaseGate` is abstract, so a shared base class that leaves `run` abstract is skipped. Loading is atomic per file: if any gate of a file fails to instantiate or has invalid metadata (`id`, `stage`, `order`; `GateDefinitionError`), the file contributes no gate and the failure is reported as `GATE_LOAD_FAILED`. A gate's `settings` dataclass fields may be `int`, `float`, `str`, `bool` or `list[str]`, each optionally `| None`: the type vocabulary and checker of rule settings (`devkit.rules.engine.settings`). Any other annotation is a defect of the gate (`GATE_DEFINITION_INVALID`, `MAINTENANCE`). A gate file may import from any package installed in the same environment, so a content wheel can keep its logic in a library module and ship only a thin gate file.

## 5. Distribution

A bundle declares a gate as an asset:

```toml
[[assets]]
id = "staged-file-limit"
kind = "gate"
source = "gates/staged_file_limit.py"

[presets.commit]
assets = ["staged-file-limit"]
```

`devkit sync` copies the selected gate files to `.devkit/managed/<bundle>/` (or uses the project override under `.devkit/overrides/<bundle>/`) and records them in `.devkit/installation.json`. At commit time the registry reads the receipt with `devkit.core.receipt` (strict: a malformed receipt or an unsafe path is an error) and loads every `.py` file of every `kind = "gate"` asset (`entrypoints` then `paths`), whatever its name. Files are found and checked with `devkit.core.verified_asset_files`, as for rule files and workflow plugin checks: a file with a `files` entry in the receipt must match its SHA-256; only a project override under `.devkit/overrides/` may lack one and is then loaded as it is; any other file without one is refused.

| State | Effect at commit time |
| --- | --- |
| Wheel installed, bundle not selected | Gate absent |
| Bundle selected, synchronized | Gate loaded; runs if enabled |
| Receipt lists a gate file the disk lacks, or the file differs from its recorded hash | Blocking stages fail with `ASSET_FILE_INVALID` (the core error, passed through); fix `devkit sync`, or `devkit override create <bundle>:<asset>` to keep a deliberate edit |
| Receipt is malformed or lists a path outside the project | Blocking stages fail with `RECEIPT_INVALID` (restore the receipt from version control, then `devkit sync`) |
| Gate file fails to import, or two gates share an id | Blocking stages fail with `GATE_LOAD_FAILED` |

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

## 6a. Settings Template

`devkit gate install` makes `<common-git-dir>/devkit.config` list every installed gate as a commented table, so a
per-clone setting is changed by uncommenting lines in place:

```toml
## pre-commit gate, on by default: Refuses a commit that stages too many files.
# [gates.settings.staged-file-limit]
#   enabled = true
#   max_files = 50  # integer; Most files one commit may stage
```

- **Layout**: prose is commented twice (`##`), the table header and keys once (`#`), with the keys indented under
  their header. Uncommenting a whole table in an editor (which removes one `#`) leaves the prose a comment and yields
  valid TOML. A key uncommented without its header belongs to whatever table precedes it, so the header is
  uncommented with its keys; the file's own header says so.
- **Content**: per gate (in stage and order), its stage, default state and description, its header, `enabled` at its
  default, then each settings field at its default with its type and the field's `metadata["help"]` when the gate
  declares one (`field(default=50, metadata={"help": "..."})`). A field whose default is `None` shows a placeholder
  of its type and `unset by default`; TOML has no null, so uncomment it only with a value. Gates that fail to load
  are left out (`devkit gate status` reports them).
- **Append-only**: a missing file is created with a header and every table. An existing file only gets the tables of
  gates whose `[gates.settings.<id>]` header it does not mention yet, commented or not; no existing line is changed
  or removed, so uncommented values stay where the developer put them. A table of a gate that is later removed
  stays; once uncommented, it fails blocking stages like any entry for a gate that is not installed.
- **Refresh**: `install` (safe to re-run) prints `[CONFIG: template=<created|updated|unchanged|skipped> path=<path>]`.
  After every writing sync, the `devkit.post_sync` hook `gate-config-template` does the same for a repository whose
  wrappers are installed, so a gate that `devkit add` or an upgrade brings in appears without another `install`. The
  hook imports the receipt's gate files to read their settings, as every commit already does, and reports nothing
  unless it skips.
- **Skipped**: a `devkit.config` that is a symbolic link, not a regular file or not UTF-8 is never written; `install`
  and the hook report `GATE_CONFIG_TEMPLATE_SKIPPED` (`GateTemplateNotice`, a warning) and succeed.
