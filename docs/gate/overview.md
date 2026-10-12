# Commit Gate: Architecture Overview

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit.gate` (`devkit gate` CLI)  
**Related Documents**:
- [Bundle Manifest Specification](../distribution/manifest-spec.md)
- [Synchronization & Transactions](../distribution/sync-and-transactions.md)
- [Rule Engine Overview](../rules/overview.md)
- [Architecture Overview](../architecture/overview.md)

---

## 1. Overview and Objectives

`devkit.gate` runs policy at Git's commit hooks. It owns the **system**: hook wrappers, configuration layering, gate discovery and the stage runner. It deliberately owns almost no **policy**: gates that encode a team's or a person's commit rules ship in content wheels as `kind = "gate"` bundle assets, so installing a wheel, selecting its bundle and running `devkit sync` adds them, exactly as rules are added to `devkit.rules`.

### Core Principles

1. **System in the core, policy in bundles.** The core ships only the gate system's own integrations as built-ins: the rule engine's staged check (`rules-staged`) and the non-empty message check (`message-nonempty`). Identity checks, timestamp handling, message conventions and similar rules belong to the content wheels that need them.
2. **Static wrappers, runtime discovery.** The hook files never change after `devkit gate install`. Each commit discovers the gates from the installation receipt, so `devkit sync` alone changes what runs; it never writes into the hooks directory.
3. **Explicit opt-in.** Installing a wheel makes its gates available; selecting a preset that contains them deploys them; a gate may additionally ship disabled and require `enabled = true` in configuration.
4. **Fail closed where Git can still refuse.** `pre-commit` and `commit-msg` failures, configuration errors and missing or drifted gate files block the commit (refusals exit `1`, everything that kept a check from running exits `2`). `post-commit` runs after the commit exists, only reports, and always exits `0`; its problems are rendered as warnings (`[WARN]`, `CONTINUE`), never as errors, so an agent does not mistake a reported problem for a failed commit.
5. **One error format.** Gate refusals and configuration problems are Agent Advisory Protocol errors (`devkit.advisory`), so an agent reads the same `[ACTION]` contract it gets from every other devkit CLI.

---

## 2. Subsystem Layout

```text
packages/devkit/src/devkit/gate/
├── errors.py       # GateError and its subclasses, one class per code (GateRefusedError, GateConfigError, ...)
├── engine/
│   ├── models.py   # Stage, Outcome, GateResult, GateContext, Gate protocol
│   ├── base.py     # BaseGate: the abstract class deployed gate files subclass
│   ├── config.py   # Layered [gates] configuration and typed settings resolution
│   ├── registry.py # Built-ins plus receipt-deployed gate files (devkit.core receipt and plugin loader)
│   └── runner.py   # validate_gates, run_stage, and the library entry points load_gate_project and run_hook
├── hooks/
│   ├── hooks.py    # Wrapper scripts: install, uninstall, status; the one hooks-directory resolver
│   └── git.py      # Git queries on devkit.core.run_git: repo root, git dirs, config values
├── gates/          # Built-in gates (rules-staged, message-nonempty)
├── cli/            # devkit gate: install, uninstall, status, run (a thin layer over the library)
└── __main__.py     # python -m devkit.gate: the gate CLI alone, which the wrappers exec
```

### Library entry points

```python
from devkit.gate import Stage, load_gate_project, run_hook

project = load_gate_project(root)  # any directory inside the work tree; project.root is its top level
project.validation.errors          # every registry, configuration and settings problem (what `gate status` reports)

report = run_hook(root, Stage.PRE_COMMIT)            # what `devkit gate run pre-commit` runs
report = run_hook(root, Stage.COMMIT_MSG, ["MSG"])   # args are the hook arguments Git passes
report.ok, report.problems, report.exit_code         # exit_code: the highest exit code among the problems
```

`load_gate_project` collects problems instead of raising them; only a failed Git query raises (`GitError`, `GIT_FAILED`). `run_hook` loads the project and runs the stage with `run_stage`, so the CLI and a library caller cannot diverge. The steps underneath are public too: `project_registry`, `load_gates_config`, `validate_gates` and `run_stage`.

---

## 2a. Built-in Gates

| Gate | Stage | Order | Default | Behavior |
| --- | --- | --- | --- | --- |
| `rules-staged` | `pre-commit` | 100 | on | Evaluates `devkit.rules`'s linter phase over the exact Git index and refuses the commit on unresolved error violations, rule loading or execution errors, or an invalid `[rules]` policy. |
| `message-nonempty` | `commit-msg` | 900 | on | Refuses a message that is blank (whitespace only) above any scissors line. |

`rules-staged` is the hook form of `devkit rules check --staged` and calls the rule engine as a library (`git_snapshot`, then `run_project_rules`, the same entry point as the CLI), so there is no separate commit command: the index Git hands the hook is what is evaluated. The staged tree is materialized into a temporary directory that becomes the workspace root; `.devkit/config.toml`, the installation receipt and synchronized rules are read from that snapshot, and Git-ignored managed rule copies are read from the working tree only when their hash matches the snapshot's receipt. Unstaged edits, untracked files and per-clone configuration therefore cannot change the result. The gate has no settings; the project tunes rules through `[rules]` (phase and severity overrides, typed settings, `exclude`) as everywhere else.

| Outcome | Condition | Advisory |
| --- | --- | --- |
| skipped | the index changes no files | — |
| passed | no error violations | none; when warning-severity violations remain, a `GATE_RULES_WARNINGS` notice counts them and its `fix` names `devkit rules check --staged` |
| refused | error violations remain | `GATE_RULES_VIOLATION` (`GateRefusedError`, BLOCKED, exit `1`): one `[DETAIL]` per violation as `<rule> <file>:<line> <message>`, `fix` names `devkit rules fix` and `devkit rules explain <rule>`, `[TARGET]` lists the files |
| failed | `[rules]` in the staged `.devkit/config.toml` is invalid | the rule engine's `RULES_CONFIG_INVALID` (or the core `CONFIG_INVALID`), passed through |
| failed | the staged receipt is malformed, a receipt-listed rule is missing, drifted from its hash or fails to import, the policy does not apply, or a rule raised | the rule engine's `RULES_RUN_FAILED` (`ProjectRun.raise_for_problems`), one `[DETAIL]` per problem with its own code (`RULES_LOAD_FAILED`, `RULES_POLICY_INVALID`, `RULES_EXECUTION_FAILED`, ...) |
| failed | the staged tree cannot be read or materialized | the rule engine's `RULES_SNAPSHOT_FAILED`, passed through |

Errors of the rule engine are never re-wrapped: they fail the gate as they are, exit `2` (the check could not run), and read the same as from `devkit rules check --staged`. A commit that only deletes files is not skipped: the policy and the rules are still loaded and evaluated, so a broken receipt or policy fails it as well.

Disable it per project or per clone with `[gates.settings.rules-staged] enabled = false`, for example in a repository that runs `devkit rules check --ci` only in CI.

`message-nonempty` sees the message before Git's cleanup. Whether Git strips comment lines depends on how the commit was made (`git commit -m "#123 fix"` keeps the `#` line; the editor template strips it; `core.commentChar` changes the character), so the gate refuses only a message that is blank above the scissors line. A message that is empty only once comments are stripped is left to Git, which aborts such a commit itself unless `--allow-empty-message` is given.

---

## 3. Hook Wrappers

`devkit gate install` writes `pre-commit`, `commit-msg` and `post-commit` into `<common-git-dir>/hooks`, the hooks directory shared by every worktree. `install`, `status` and `uninstall` all resolve this one directory. Each wrapper:

1. runs `<hook>.pre-gate` first when it exists and is executable (a hook `install` moved aside) and, in a blocking stage, stops with its exit status when it fails;
2. picks the interpreter: `<work tree>/.venv/bin/python` when `devkit` is installed in that environment, otherwise the interpreter recorded at install time;
3. runs:

```sh
exec "$python" -P -m devkit.gate run <stage> "$@"
```

- **`-P`**: the repository is the working directory of a hook, so without `-P` a file such as `json.py` or `devkit.py` at the repository root could shadow a module the wrapper imports. `-P` keeps the current directory off `sys.path`.
- **`-m devkit.gate`**: the gate CLI alone, so a commit imports only the gate area and what it depends on.
- **Interpreter**: the work tree's `.venv` comes first, so every worktree uses its own environment even though the hooks directory is shared. The recorded fallback is `sys.executable` of the installing process, or `--python`; `install` stores it as an absolute path and refuses (`GATE_PYTHON_INVALID`) an interpreter that cannot import `devkit.gate`. Wrappers do not depend on `PATH`, so Git GUIs and agent shells behave like a terminal.
- **Missing environment**: when neither interpreter is usable, a blocking stage exits `2` (the gates could not run) with a `run 'uv sync'` hint; `post-commit` exits `0`.
- **Existing hooks**: hooks without the managed marker are never overwritten silently. An executable hook, a symbolic link (even a dangling one) or anything that is not a regular file is foreign: `install` refuses (`GATE_FOREIGN_HOOK`), and `install --force` moves it to `<hook>.pre-gate`, where the wrapper keeps running it first. A non-executable regular file, which Git ignores, is inert and is moved aside without `--force`. `uninstall` restores what was moved. An existing backup is never overwritten (`GATE_BACKUP_EXISTS`).
- **Writing**: wrappers are LF-only files with POSIX paths, written to a temporary file and renamed into place, so a symbolic link at the hook path is never written through.
- **`core.hooksPath`**: when it points anywhere other than `<common-git-dir>/hooks`, Git would not run the wrappers: `install` refuses (`GATE_HOOKS_PATH_SET`), `status` reports the setting, and `uninstall` still cleans the common hooks directory.
- **Bypass**: `git commit --no-verify` skips `pre-commit` and `commit-msg` as Git defines; the gate system adds no bypass of its own.

---

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
- **Refusing**: raise `GateRefusedError(message, *details, code=..., fix=..., target_files=...)`: message first, remediation in `fix`, and the gate's own code (default `GATE_FAILED`). It is `BLOCKED` and exits `1` (`FINDINGS`), since a refusal is the negative result of a check that ran. Any other `AdvisoryError` fails the gate as it is (most exit `2`: the check could not run); any other exception is wrapped as `UNEXPECTED_ERROR` (exit `2`). Every failed gate therefore reports an advisory.
- **Context**: `ctx.repo_root` (top level of the work tree), `ctx.git_dir` (this worktree's git dir, for `MERGE_HEAD`, rebase state and the like), `ctx.common_git_dir` (shared by every worktree), `ctx.stage`, `ctx.args` (hook arguments), `ctx.settings` (the gate's effective settings) and `ctx.message_file` for `commit-msg`.
- **Ordering**: gates in a stage run by `(order, id)`. Message transforms use `order < 100`, checks default to `100`, and the built-in `message-nonempty` runs at `900` so it sees the transformed message. A `post-commit` gate that rewrites `HEAD` must take a low order so later gates observe the final commit.
- **No short-circuit**: a failing gate does not stop later gates, so one commit attempt reports every refusal.

Gate files are loaded like rule files, with `devkit.core.plugins.load_subclasses`: every concrete `BaseGate` subclass defined in the file is instantiated without arguments. `BaseGate` is abstract, so a shared base class that leaves `run` abstract is skipped. Loading is atomic per file: if any gate of a file fails to instantiate or has invalid metadata (`id`, `stage`, `order`; `GateDefinitionError`), the file contributes no gate and the failure is reported as `GATE_LOAD_FAILED`. A gate's `settings` dataclass fields may be `int`, `float`, `str`, `bool` or `list[str]`, each optionally `| None`: the same type vocabulary and checker as rule settings (`devkit.rules.engine.settings`). Any other annotation is a defect of the gate (`GATE_DEFINITION_INVALID`, `MAINTENANCE`). A gate file may import from any package installed in the same environment, which lets a content wheel keep its logic in a library module and ship only a thin gate file.

---

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

`devkit sync` copies the selected gate files to `.devkit/managed/<bundle>/` (or uses the project override under `.devkit/overrides/<bundle>/`) and records them in `.devkit/installation.json`. At commit time the registry reads the receipt with `devkit.core.receipt` (strict: a malformed receipt or an unsafe path is an error) and loads every `.py` file of every `kind = "gate"` asset (`entrypoints` then `paths`), whatever its name. The files are found and checked with `devkit.core.verified_asset_files`, as `devkit rules` finds rule files and `devkit workflow` plugin checks: a file with a `files` entry in the receipt must match its SHA-256; a file without one (a project override) is loaded as it is.

| State | Effect at commit time |
| --- | --- |
| Wheel installed, bundle not selected | Gate absent |
| Bundle selected, synchronized | Gate loaded; runs if enabled |
| Receipt lists a gate file the disk lacks, or the file differs from its recorded hash | Blocking stages fail with `ASSET_FILE_INVALID` (the core error, passed through); fix `devkit sync`, or `devkit override create <bundle>:<asset>` to keep a deliberate edit |
| Receipt is malformed or lists a path outside the project | Blocking stages fail with `RECEIPT_INVALID` (restore the receipt from version control, then `devkit sync`) |
| Gate file fails to import, or two gates share an id | Blocking stages fail with `GATE_LOAD_FAILED` |

---

## 6. Configuration Layers

Two files contribute a `[gates]` table; the later layer wins:

| Order | File | Tracked | Purpose |
| --- | --- | --- | --- |
| 1 | `.devkit/config.toml` | Yes | Team policy shared by every clone |
| 2 | `<common-git-dir>/devkit.config` | No | Per-clone and personal overrides, shared by every worktree |

Tables are deep-merged; a scalar or array in a later layer replaces the earlier value. `devkit.config` uses the same TOML shape and currently accepts only `[gates]`.

```toml
# .devkit/config.toml
[gates.settings.staged-file-limit]
max_files = 50

# .git/devkit.config
[gates.settings.staged-file-limit]
max_files = 200

[gates.settings.rules-staged]
enabled = false

[gates.settings.message-nonempty]
enabled = false
```

- `enabled` is reserved in every gate table and overrides `enabled_by_default`.
- Other keys must match the gate's settings dataclass fields and their annotations: an integer for `int`, a number for `float` (an integer becomes a float), a string, a boolean, an array of strings for `list[str]`; no other array or value type, and never `null` (TOML has none) unless the field is `| None`. Settings are validated for every installed gate, whatever its stage and whether it is enabled; unknown keys and wrong types fail every blocking stage, and the gate itself is skipped.
- A file that cannot be read or parsed is the core `ConfigError` (`CONFIG_INVALID`), passed through unchanged; a malformed `[gates]` table or invalid settings are `GateConfigError` (`GATE_CONFIG_INVALID`), a subclass of it.
- An entry for a gate that is not installed fails blocking stages, so a typo or a forgotten `devkit sync` cannot silently disable policy.
- `devkit` passes `[gates]` through untouched, as it does `[rules]` and `[workflow]`.

---

## 7. CLI

| Command | Purpose |
| --- | --- |
| `devkit gate install [--force] [--python PATH]` | Write the managed wrappers. |
| `devkit gate uninstall` | Remove managed wrappers; restore hooks moved aside by `install`. |
| `devkit gate status [--format text\|json]` | Hooks directory and `core.hooksPath`, hook states, every gate with stage, order, effective enablement and source, configuration layers, and every problem that fails a commit (`load_gate_project`, the same `validate_gates` the stages run). |
| `devkit gate run [-q\|-v] [--strict] <stage> [hook args]` | Run one stage (`run_hook`); what the wrappers call. Options go before `<stage>`; hooks set `DEVKIT_QUIET`, `DEVKIT_VERBOSE` or `DEVKIT_STRICT` instead. |

`-w/--workspace-root` (default: the current directory) may name any existing directory inside the repository; every command, `install` and `uninstall` included, works on the work tree's top level (`devkit.core.require_git_toplevel`), as a hook does. A `-w` that is not an existing directory is `ARGUMENT_INVALID`; one outside a work tree is `GIT_FAILED` (`INPUT_ERROR`). Output follows [Agent-First Output](../architecture/agent-output.md): `install`, `uninstall` and `status` print sentinel lines on stdout (`[HOOKS: …]`, `[HOOK: …]`, `[GATE: <id> stage=<stage> …]`, `[CONFIG: sources=…]`) and their problems as advisory blocks on stderr. `run` prints nothing on stdout, so the hook stays silent when every gate passes: a refusal or failure is one advisory block per gate on stderr whose first `[DETAIL]` names the gate and stage (`gate=<id> stage=<stage>`, before the gate's own details), a configuration problem is its own advisory block, notices such as `GATE_RULES_WARNINGS` follow as `[NOTICE]` blocks, and passed and skipped gates appear only under `-v`, as `[INFO]` lines. `status --format json` prints one object with `hooks_dir`, `hooks_path`, `hooks`, `gates`, `config_sources` and `errors` (each `{code, message, exit_code, advisory}`), or `{"error": {...}}` when the status cannot be read.

Exit codes follow the devkit convention ([Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)). `status` is a report: it exits `1` when it lists any problem that would fail a commit and `2` only when it cannot run (outside a Git work tree). A blocking `run` collects several problems and exits with the highest `exit_code` among them: a refusal (`GateRefusedError`) gives `1`; a configuration, registry, load or settings problem, an error a gate raised that is not a refusal (such as a rule engine error), or an unexpected exception gives `2`.

| Command | `0` | `1` | `2` |
| --- | --- | --- | --- |
| `install`, `uninstall` | done | — | refused or failed: `GATE_HOOKS_PATH_SET`, `GATE_FOREIGN_HOOK`, `GATE_BACKUP_EXISTS`, `GATE_PYTHON_INVALID`, `GIT_FAILED`, `ARGUMENT_INVALID`, usage errors |
| `status` | no problem would fail a commit | — | a reported problem would fail a commit (registry, configuration or settings errors are all configuration or load problems), or the status cannot be read (not a Git work tree: `GIT_FAILED`; `ARGUMENT_INVALID`), usage errors |
| `run pre-commit`, `run commit-msg` | every gate passed or was skipped | gates refused the commit and nothing else went wrong | the gate setup has a problem, a gate failed with a non-refusal error, or the stage cannot run (not a Git work tree), usage errors; the wrapper exits `2` when no interpreter is found |
| `run post-commit` | always, even when the stage cannot run (the commit already exists; problems are reported only, as `[WARN]` blocks) | — | usage errors |

Any nonzero status of a blocking stage aborts the commit.

### Error codes

Every gate error derives from `GateError` (`devkit.gate.errors`), which sets `actor = DEVELOPER` and `retry = AFTER_FIX` once; there is one class per code, constructed message first with keyword fields.

| Code | Class | Mode | Exit | Meaning |
| --- | --- | --- | --- | --- |
| `GATE_FAILED` | `GateRefusedError` | `BLOCKED` | `1` | default code of a gate refusal; gates pass their own (`GATE_MESSAGE_EMPTY`, `GATE_RULES_VIOLATION`, ...) |
| `GATE_CONFIG_INVALID` | `GateConfigError` (also a `devkit.core.ConfigError`) | `INPUT_ERROR` | `2` | invalid `[gates]` table or settings, a configured gate that is not installed |
| `GATE_LOAD_FAILED` | `GateLoadError` | `MAINTENANCE` | `2` | a deployed gate file fails to import or to instantiate its gates, or two gates share an id |
| `GATE_DEFINITION_INVALID` | `GateDefinitionError` | `MAINTENANCE` | `2` | a gate declares an unusable `id`, `stage`, `order` (reported inside its file's load failure) or settings declaration, or uses `ctx.message_file` outside `commit-msg` |
| `GATE_RESULT_INVALID` | `GateResultError` | `MAINTENANCE` | `2` | a gate built a `FAILED` `GateResult` or returned something other than a `GateResult` or `None` |
| `GATE_PYTHON_INVALID` | `GatePythonError` | `INPUT_ERROR` | `2` | `install --python` names an interpreter that cannot import `devkit.gate` |
| `GATE_FOREIGN_HOOK`, `GATE_BACKUP_EXISTS`, `GATE_HOOKS_PATH_SET` | `ForeignHookError`, `HookBackupExistsError`, `HooksPathSetError` | `INTERACTION` | `2` | `install` would move or bypass hooks it does not own |
| `CONFIG_INVALID` | `devkit.core.ConfigError` | `INPUT_ERROR` | `2` | `.devkit/config.toml` or `devkit.config` cannot be read or parsed |
| `ASSET_FILE_INVALID` | `devkit.core.AssetFileError` | `MAINTENANCE` | `2` | a receipt-listed gate file is missing, unsafe or differs from its recorded hash |
| `ARGUMENT_INVALID` | `devkit.core.ArgumentError` | `INPUT_ERROR` | `2` | `-w/--workspace-root` is not an existing directory; `run commit-msg` without the message file |
| `GIT_FAILED` | `devkit.core.GitError` | `INPUT_ERROR` outside a work tree, else `MAINTENANCE` | `2` | a Git query failed |
| `RECEIPT_INVALID` | `devkit.core.ReceiptError` | `MAINTENANCE` | `2` | `.devkit/installation.json` is malformed or lists an unsafe path |
| `RULES_*` | `devkit.rules` errors | as raised | `2` | the `rules-staged` gate could not run the rule engine (passed through unchanged) |
| `GATE_RULES_WARNINGS` | `RulesWarningsNotice` | `NOTE` (level `NOTICE`) | `0` | returned, never raised: `rules-staged` passed while warning-severity violations remain in the staged tree |

