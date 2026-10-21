# devkit_agt.features.gate

Pluggable Git commit gates (`devkit gate` CLI, shipped by `devkit-agt`): managed hook wrappers, layered configuration, gate discovery and the stage runner. Policy lives in content wheels that ship gates as `kind = "gate"` bundle assets. Semantics: `CAP-GATE-commit-gates`.

## Usage

```bash
uv add --dev "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit gate install      # prepares dispatchers and active 20-devkit entries (sync also installs them)
                                # and a commented table per gate into <common-git-dir>/devkit.config
uv run devkit gate status       # hooks, gates with effective state, configuration layers, problems that fail a commit

uv add --dev <content-wheel>          # adding gates from a content wheel
uv run devkit add <bundle>:<preset>   # a preset that includes the bundle's gate assets (not needed when the default preset of an auto-selected bundle has them)
uv run devkit sync                    # deploys the gate packages and records their files in the receipt
```

Writing syncs install dispatchers automatically. Existing regular hooks are moved to `<hook>.legacy` with a warning and run through `<hook>.d/00-legacy`; `<hook>.d/20-devkit` is added only for stages with enabled gates. Add executable scripts beside it in filename order. Symlinks and non-regular hooks need `install --force`; `git commit --no-verify` skips `pre-commit` and `commit-msg`. See `CAP-GATE-commit-gates`.

## Commands

| Command | Purpose |
| --- | --- |
| `devkit gate install [--force] [--python PATH]` | Prepare dispatchers and active `20-devkit` entries, and append the commented table of every gate `<common-git-dir>/devkit.config` does not mention yet (`CAP-GATE-commit-gates`). |
| `devkit gate uninstall` | Remove owned devkit entries; keep dispatchers for user scripts, otherwise restore preserved hooks. |
| `devkit gate status [--format text\|json] [--strict]` | Hooks directory and `core.hooksPath`, hook states and script filenames, every gate with stage, order, effective enablement and source, configuration layers, and every problem that fails a commit (`load_gate_project`, the same `validate_gates` the stages run). Warns with `GATE_HOOK_ENTRY_MISSING` when a stage has enabled gates but no installed `20-devkit` entry, so they would not run; when `core.hooksPath` sends Git to another directory, no managed hook runs and `install` refuses, so one `GATE_HOOKS_PATH_SET` warning names every enabled gate instead, with the fix that clears the setting. Warnings leave the exit code `0`, except under `--strict`, which exits `1` on them. |
| `devkit gate run [-q\|-v] [--strict] <stage> [hook args]` | Run one stage (`run_hook`); what the wrappers call, and how to test a stage by hand. Options go before `<stage>`; hooks set `DEVKIT_QUIET`, `DEVKIT_VERBOSE` or `DEVKIT_STRICT` instead, since Git passes no flags (`ARCH-08-1-agent-output`). |

`-w/--workspace-root` (default: the current directory) may name any existing directory inside the repository; every command, `install` and `uninstall` included, works on the work tree's top level (`devkit_dist.features.project.repositories.project.require_git_toplevel`), as a hook does. A `-w` that is not an existing directory is `ARGUMENT_INVALID`; one outside a work tree is `GIT_FAILED` (`INPUT_ERROR`).

Output follows `ARCH-08-1-agent-output`. `install`, `uninstall` and `status` print sentinel lines on stdout (`[HOOKS: …]`, `[HOOK: …]`, `[GATE: <id> stage=<stage> …]`, `[CONFIG: sources=…]`, and from `install` `[CONFIG: template=<state> path=<path>]`). `status --format json` prints one object with `hooks_dir`, `hooks_path`, `hooks`, `gates`, `config_sources`, `errors` (each `{code, message, exit_code, advisory}`) and `notices` (its warnings, the same shape), or `{"error": {...}}` when the status cannot be read. `run` prints nothing on stdout, so the hook stays silent when every gate passes: a refusal or failure is one advisory block per gate on stderr whose first `[DETAIL]` is `gate=<id> stage=<stage>` (before the gate's own details), a configuration problem is its own block, and passed and skipped gates appear only under `-v`, as `[INFO]` lines. Notices such as `GATE_VERIFY_UNSTAGED` are `[NOTICE]` blocks: in `pre-commit` and `commit-msg` they come before the refusal and failure blocks, so errors are last; in `post-commit`, whose problems are `[WARN]` blocks (the commit already exists), they come after those.

## Exit codes

The devkit convention (`ARCH-08-cross-cutting`) applies. `status` is a report: it exits `1` when it lists any problem that would fail a commit, whatever the problem's own code. A blocking `run` collects several problems and exits with the highest `exit_code` among them: a refusal (`GateRefusedError`) gives `1`; a configuration, registry, load or settings problem, an error a gate raised that is not a refusal (such as a rule engine error), or an unexpected exception gives `2`. Any nonzero status of a blocking stage aborts the commit.

| Command | `0` | `1` | `2` |
| --- | --- | --- | --- |
| `install`, `uninstall` | done | — | refused or failed: `GATE_HOOKS_PATH_SET`, `GATE_FOREIGN_HOOK`, `GATE_BACKUP_EXISTS`, `GATE_PYTHON_INVALID`, `GIT_FAILED`, `ARGUMENT_INVALID`, usage errors |
| `status` | no problem would fail a commit (warnings included, without `--strict`) | a reported problem would fail a commit (registry, configuration, load or settings errors); under `--strict`, also a warning (`GATE_HOOK_ENTRY_MISSING`, `GATE_HOOKS_PATH_SET`) | the status cannot be read (not a Git work tree: `GIT_FAILED`; `ARGUMENT_INVALID`), usage errors |
| `run pre-commit`, `run commit-msg` | every gate passed or was skipped | gates refused the commit and nothing else went wrong | the gate setup has a problem, a gate failed with a non-refusal error, or the stage cannot run (not a Git work tree), usage errors; the wrapper exits `2` with `GATE_INTERPRETER_UNAVAILABLE` when no interpreter can import `devkit_agt.features.gate` |
| `run post-commit` | always, even when the stage cannot run (the commit already exists; problems are reported as `[WARN]` blocks) | — | usage errors |

## Error codes

Every gate error derives from `GateError` (`devkit_agt.features.gate.models.errors`), which sets `actor = DEVELOPER` and `retry = AFTER_FIX`; there is one class per code, constructed message first with keyword fields.

| Code | Class | Mode | Exit | Meaning |
| --- | --- | --- | --- | --- |
| `GATE_FAILED` | `GateRefusedError` | `BLOCKED` | `1` | default code of a gate refusal; gates pass their own (`GATE_MESSAGE_EMPTY`, `GATE_VERIFY_FAILED`, ...) |
| `GATE_CONFIG_INVALID` | `GateConfigError` (also a `devkit_dist.base.errors.ConfigError`) | `INPUT_ERROR` | `2` | invalid `[gates]` table or settings, a configured gate that is not installed |
| `GATE_LOAD_FAILED` | `GateLoadError` | `MAINTENANCE` | `2` | a deployed gate package fails to import or to instantiate its gates, or two gates share an id |
| `GATE_DEFINITION_INVALID` | `GateDefinitionError` | `MAINTENANCE` | `2` | a gate declares an unusable `id`, `stage`, `order` (reported inside its file's load failure) or settings declaration, or uses `ctx.message_file` outside `commit-msg` |
| `GATE_RESULT_INVALID` | `GateResultError` | `MAINTENANCE` | `2` | a gate built a `FAILED` `GateResult`, gave a `GateResult` a notice that is not an `AdvisoryError`, or returned something other than a `GateResult` or `None`; the stage's other gates still run |
| `GATE_PYTHON_INVALID` | `GatePythonError` | `INPUT_ERROR` | `2` | `install --python` names an interpreter that cannot import `devkit_agt.features.gate` |
| `GATE_INTERPRETER_UNAVAILABLE` | `GateInterpreterError` (printed by the `20-devkit` entry) | `MAINTENANCE`; `CONTINUE` (level `WARNING`) in `post-commit` | `2`; `0` in `post-commit` | at commit time the entry's interpreter is missing or cannot import `devkit_agt.features.gate`, so the stage's gates did not run; `[DETAIL] python=<path>` and the reason (`not an executable file`, or the import error's first line) |
| `GATE_RULES_FAILED` | `GateRefusedError` | `BLOCKED` | `1` | `rules-check` found unfixed error-severity violations in the staged tree; one `<RULE-id> <file>:<line>: <message>` detail per violation (and `  fix: <remediation>`), the first 20 listed, then `... and <n> more` |
| `GATE_RULES_WARNINGS` | `RulesWarningsNotice` | `CONTINUE` (level `WARNING`) | `0` | returned, never raised: `rules-check` found warning-severity violations in the staged tree, listed as in `GATE_RULES_FAILED` |
| `RULES_RUN_FAILED` | `devkit_agt.features.rules.RulesRunError` | `MAINTENANCE`, or `AUTO` | `2` | `rules-check` could not complete the run (rules that cannot load, an invalid policy, a rule that raised); each problem is a detail; `AUTO` with their fix when every problem is `AUTO` with that one fix (`devkit sync` for missing managed rule files). `RULES_CONFIG_INVALID` and `RULES_SNAPSHOT_FAILED` pass through unchanged |
| `GATE_VERIFY_FAILED` | `GateRefusedError` | `BLOCKED` | `1` | a `verify-commands` command exited nonzero; one `command: ... exit=... log=...` detail per failed command, then its summaries, failed tests or last lines and relayed `devkit` error blocks (`  > `) |
| `GATE_VERIFY_NOT_RUN` | `VerifyNotRunError` | `MAINTENANCE`, or `AUTO` | `2` | a nested `devkit` command could not run (exit `2` with its own error block, such as `RULES_LOAD_FAILED`); same details; `AUTO` with the relayed fix when every relayed error is `AUTO` with that one fix (`devkit sync` for missing managed files) |
| `GATE_VERIFY_UNSTAGED` | `VerifyUnstagedNotice` | `NOTE` (level `NOTICE`) | `0` | returned, never raised: `verify-commands` ran on a working tree with unstaged or untracked files |
| `GATE_CONFIG_TEMPLATE_SKIPPED` | `GateTemplateNotice` | `CONTINUE` (level `WARNING`) | `0` | returned, never raised: `devkit.config` is a symbolic link, not a regular file, not UTF-8 or cannot be written, the `[gates]` table of `.devkit/config.toml` cannot be read, or the refresh failed otherwise (the message names the error's code), so `install` or the post-sync refresh left it alone; the hook notices of the same run are still reported |
| `GATE_FOREIGN_HOOK`, `GATE_BACKUP_EXISTS`, `GATE_HOOKS_PATH_SET` | `ForeignHookError`, `HookBackupExistsError`, `HooksPathSetError` | `INTERACTION`; `CONTINUE` (level `WARNING`) from `status` | `2`; `0` from `status` | `install` would move or bypass hooks it does not own; `status` returns `GATE_HOOKS_PATH_SET` as a warning when `core.hooksPath` points elsewhere and gates are enabled (`[DETAIL] gates=<ids>`, the scope's fix) |
| `GATE_HOOK_LAYOUT_INVALID` | `HookLayoutError` | `MAINTENANCE` | `2` | Reserved entry collision or unsafe hook directory |
| `GATE_HOOK_PRESERVED` | `HookPreservedNotice` | `CONTINUE` | `0` | Existing hook preserved and chained; warning returned once when moved |
| `GATE_HOOK_INSTALL_SKIPPED` | `HookInstallSkippedNotice` | `CONTINUE` | `0` | Automatic installation skipped; reason code and remediation included |
| `GATE_HOOK_SCRIPT_FAILED` | `HookScriptFailedNotice` (printed by the POSIX dispatcher) | `CONTINUE` | `0` | A post-commit script failed; later scripts still run. `[DETAIL] stage=<stage> script=<path> exit=<status>` |
| `GATE_HOOK_ENTRY_MISSING` | `HookEntryMissingNotice` | `CONTINUE` (level `WARNING`) | `0` | returned by `status`, never raised: a stage has enabled gates but no managed dispatcher with a `20-devkit` entry, so they do not run (`[DETAIL] gates=<ids>`); fix `devkit gate install` or `devkit sync`. Not reported while `core.hooksPath` points elsewhere (`GATE_HOOKS_PATH_SET` instead) |
| `CONFIG_INVALID` | `devkit_dist.base.errors.ConfigError` | `INPUT_ERROR` | `2` | `.devkit/config.toml` or `devkit.config` cannot be read or parsed |
| `ASSET_FILE_INVALID` | `devkit_dist.base.errors.AssetFileError` | `MAINTENANCE`; `AUTO` when missing | `2` | a receipt-listed gate file is unsafe or differs from its recorded hash; a missing one (a fresh clone or worktree) is `AUTO` with the fix `devkit sync` |
| `ARGUMENT_INVALID` | `devkit_core.base.errors.ArgumentError` | `INPUT_ERROR` | `2` | `-w/--workspace-root` is not an existing directory; `run commit-msg` without the message file |
| `GIT_FAILED` | `devkit_core.base.errors.GitError` | `INPUT_ERROR` outside a work tree, else `MAINTENANCE` | `2` | a Git query failed |
| `RECEIPT_INVALID` | `devkit_dist.base.errors.ReceiptError` | `MAINTENANCE` | `2` | `.devkit/installation.json` is malformed or lists an unsafe path |

## Built-in gates

| Gate | Stage | Default | Behavior |
| --- | --- | --- | --- |
| `rules-check` | `pre-commit` | on, skipped when nothing is staged | Evaluates the linter phase on the staged tree as `devkit rules check --staged` does, in the hook's process, and refuses on an unfixed error-severity violation (`GATE_RULES_FAILED`); warnings pass with `GATE_RULES_WARNINGS`; a run that cannot complete is `RULES_RUN_FAILED`. |
| `verify-commands` | `pre-commit` | on, skipped while `commands` is empty | Runs `[gates.settings.verify-commands] commands` (shell lines, in order, from the work tree's top level, through `devkit_agt.features.compact`) and refuses when any fails (`GATE_VERIFY_FAILED`, or `GATE_VERIFY_NOT_RUN` when a nested `devkit` command could not run); notes a working tree that differs from the commit (`GATE_VERIFY_UNSTAGED`). |
| `message-nonempty` | `commit-msg` | on | Refuses a message that is blank (whitespace only) above any scissors line. |

Outcomes and failure codes: `CAP-GATE-commit-gates`.

## Built-in git-commits bundle

Commit message policy is a bundle, not a gate: `devkit-dist` ships the opt-in bundle `git-commits` (sources in `packages/devkit-dist/src/devkit_dist/bundles/git_commits/bundle/`, the data-only module `devkit_dist.bundles.git_commits`), deployed after `uv run devkit add git-commits`; it needs no engine, so a distribution-only installation deploys it too. Its preset `core` holds:

- the instruction `git-commits`: Conventional Commits types, optional scope, imperative subject, body and footer formatting, breaking changes and clean message output; listed by `devkit get-context git-commits`;
- the `guidance` fragment `commit-pointer`, which adds one line to the root `AGENTS.md` block: "Before drafting or creating a commit message, read `<path>` and follow it." The path is the managed copy, or the project override after `devkit override create git-commits:git-commits`.

It ships no gate: messages are not validated. Adapt the conventions (scope names, message language, issue references) with an override of the instruction.

## Configuration

`.devkit/config.toml` (tracked) is overridden by `<common-git-dir>/devkit.config` (untracked, per clone); see `CAP-GATE-commit-gates`. A key in `devkit.config` replaces the project's value as a whole (an array too): in its commented template, uncomment a table's header and only the keys you change (`CAP-GATE-commit-gates`).

```toml
[gates.settings.verify-commands]
commands = ["just lint-check", "just test"]

[gates.settings.rules-check]
enabled = false   # only to keep rules out of commits; tune rules in [rules] instead

[gates.settings.<gate-id>]
enabled = true
some_setting = 3
```

## Library

```text
packages/devkit/src/devkit_agt/features/gate/
├── errors.py       # GateError and its subclasses, one class per code
├── engine/         # models (Stage, GateResult, GateContext), BaseGate, layered config, registry, runner
├── hooks/          # dispatchers, gate scripts, installation, local template and Git queries
├── gates/          # built-in gates (rules-check, verify-commands, message-nonempty)
├── cli/            # devkit gate (a thin layer over the library)
└── __main__.py     # python -m devkit_agt.features.gate: the gate CLI alone, which the wrappers run
```

The opt-in `git-commits` bundle is not part of this module: it lives in the data-only `devkit_dist.bundles.git_commits` ([Built-in git-commits bundle](#built-in-git-commits-bundle)).

`devkit gate` is a thin command line over `load_gate_project(root)` (gates, layered configuration, every problem `gate status` reports) and `run_hook(root, stage, args)` (one stage, as the hook wrapper runs it; `report.ok`, `report.problems`, `report.exit_code`). See `CAP-GATE-commit-gates`.

## Writing a gate

```python
from dataclasses import dataclass

from devkit_agt.features.gate import BaseGate, GateContext, GateRefusedError, GateResult, Stage


@dataclass(frozen=True)
class Settings:
    max_files: int = 50


class StagedFileLimitGate(BaseGate):  # BaseGate is abstract: implement run()
    def __init__(self) -> None:
        super().__init__(
            id="staged-file-limit",
            description="Refuse commits that stage too many files.",
            stage=Stage.PRE_COMMIT,
            settings=Settings(),
        )

    def run(self, ctx: GateContext) -> GateResult:
        count = ...  # e.g. `git diff --cached --name-only` in ctx.repo_root
        if count > ctx.settings.max_files:
            raise GateRefusedError(
                f"{count} files staged (limit {ctx.settings.max_files})",
                code="GATE_STAGED_FILE_LIMIT",
                fix="Split the change into smaller commits",
            )
        return GateResult.passed()
```

Declare the file as a `kind = "gate"` asset in `bundle.toml` and add it to a preset (`CAP-GATE-commit-gates`); the `CAP-GATE-commit-gates` defines results, refusals, context and ordering.
