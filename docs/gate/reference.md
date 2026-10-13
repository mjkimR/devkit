# devkit.gate

Pluggable Git commit gates (`devkit gate` CLI): managed hook wrappers, layered configuration, gate discovery and the stage runner. Policy lives in content wheels that ship gates as `kind = "gate"` bundle assets. Semantics: [Commit Gate Overview](overview.md).

## Usage

```bash
uv add --dev devkit
uv run devkit gate install      # writes pre-commit, commit-msg and post-commit wrappers into <common-git-dir>/hooks
                                # and a commented table per gate into <common-git-dir>/devkit.config
uv run devkit gate status       # hooks, gates with effective state, configuration layers, problems that fail a commit

uv add --dev <content-wheel>          # adding gates from a content wheel
uv run devkit add <bundle>:<preset>   # a preset that includes the bundle's gate assets (not needed when the default preset of an auto-selected bundle has them)
uv run devkit sync                    # deploys the gate packages and records their files in the receipt
```

Existing executable hooks are kept: `install --force` moves them to `<hook>.pre-gate` and the wrapper runs them before the gates; `git commit --no-verify` skips `pre-commit` and `commit-msg`. See [Hook Wrappers](overview.md#3-hook-wrappers).

## Commands

| Command | Purpose |
| --- | --- |
| `devkit gate install [--force] [--python PATH]` | Write the managed wrappers, and append the commented table of every gate `<common-git-dir>/devkit.config` does not mention yet ([Settings Template](overview.md#6a-settings-template)). |
| `devkit gate uninstall` | Remove managed wrappers; restore hooks moved aside by `install`. |
| `devkit gate status [--format text\|json]` | Hooks directory and `core.hooksPath`, hook states, every gate with stage, order, effective enablement and source, configuration layers, and every problem that fails a commit (`load_gate_project`, the same `validate_gates` the stages run). |
| `devkit gate run [-q\|-v] [--strict] <stage> [hook args]` | Run one stage (`run_hook`); what the wrappers call, and how to test a stage by hand. Options go before `<stage>`; hooks set `DEVKIT_QUIET`, `DEVKIT_VERBOSE` or `DEVKIT_STRICT` instead, since Git passes no flags ([Agent-First Output](../architecture/agent-output.md#6-verbosity-and-strictness)). |

`-w/--workspace-root` (default: the current directory) may name any existing directory inside the repository; every command, `install` and `uninstall` included, works on the work tree's top level (`devkit.core.require_git_toplevel`), as a hook does. A `-w` that is not an existing directory is `ARGUMENT_INVALID`; one outside a work tree is `GIT_FAILED` (`INPUT_ERROR`).

Output follows [Agent-First Output](../architecture/agent-output.md). `install`, `uninstall` and `status` print sentinel lines on stdout (`[HOOKS: …]`, `[HOOK: …]`, `[GATE: <id> stage=<stage> …]`, `[CONFIG: sources=…]`, and from `install` `[CONFIG: template=<state> path=<path>]`). `status --format json` prints one object with `hooks_dir`, `hooks_path`, `hooks`, `gates`, `config_sources` and `errors` (each `{code, message, exit_code, advisory}`), or `{"error": {...}}` when the status cannot be read. `run` prints nothing on stdout, so the hook stays silent when every gate passes: a refusal or failure is one advisory block per gate on stderr whose first `[DETAIL]` is `gate=<id> stage=<stage>` (before the gate's own details), a configuration problem is its own block, and passed and skipped gates appear only under `-v`, as `[INFO]` lines. Notices such as `GATE_VERIFY_UNSTAGED` are `[NOTICE]` blocks: in `pre-commit` and `commit-msg` they come before the refusal and failure blocks, so errors are last; in `post-commit`, whose problems are `[WARN]` blocks (the commit already exists), they come after those.

## Exit codes

The devkit convention ([Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)) applies. `status` is a report: it exits `1` when it lists any problem that would fail a commit, whatever the problem's own code. A blocking `run` collects several problems and exits with the highest `exit_code` among them: a refusal (`GateRefusedError`) gives `1`; a configuration, registry, load or settings problem, an error a gate raised that is not a refusal (such as a rule engine error), or an unexpected exception gives `2`. Any nonzero status of a blocking stage aborts the commit.

| Command | `0` | `1` | `2` |
| --- | --- | --- | --- |
| `install`, `uninstall` | done | — | refused or failed: `GATE_HOOKS_PATH_SET`, `GATE_FOREIGN_HOOK`, `GATE_BACKUP_EXISTS`, `GATE_PYTHON_INVALID`, `GIT_FAILED`, `ARGUMENT_INVALID`, usage errors |
| `status` | no problem would fail a commit | a reported problem would fail a commit (registry, configuration, load or settings errors) | the status cannot be read (not a Git work tree: `GIT_FAILED`; `ARGUMENT_INVALID`), usage errors |
| `run pre-commit`, `run commit-msg` | every gate passed or was skipped | gates refused the commit and nothing else went wrong | the gate setup has a problem, a gate failed with a non-refusal error, or the stage cannot run (not a Git work tree), usage errors; the wrapper exits `2` when no interpreter is found |
| `run post-commit` | always, even when the stage cannot run (the commit already exists; problems are reported as `[WARN]` blocks) | — | usage errors |

## Error codes

Every gate error derives from `GateError` (`devkit.gate.errors`), which sets `actor = DEVELOPER` and `retry = AFTER_FIX`; there is one class per code, constructed message first with keyword fields.

| Code | Class | Mode | Exit | Meaning |
| --- | --- | --- | --- | --- |
| `GATE_FAILED` | `GateRefusedError` | `BLOCKED` | `1` | default code of a gate refusal; gates pass their own (`GATE_MESSAGE_EMPTY`, `GATE_VERIFY_FAILED`, ...) |
| `GATE_CONFIG_INVALID` | `GateConfigError` (also a `devkit.core.ConfigError`) | `INPUT_ERROR` | `2` | invalid `[gates]` table or settings, a configured gate that is not installed |
| `GATE_LOAD_FAILED` | `GateLoadError` | `MAINTENANCE` | `2` | a deployed gate package fails to import or to instantiate its gates, or two gates share an id |
| `GATE_DEFINITION_INVALID` | `GateDefinitionError` | `MAINTENANCE` | `2` | a gate declares an unusable `id`, `stage`, `order` (reported inside its file's load failure) or settings declaration, or uses `ctx.message_file` outside `commit-msg` |
| `GATE_RESULT_INVALID` | `GateResultError` | `MAINTENANCE` | `2` | a gate built a `FAILED` `GateResult` or returned something other than a `GateResult` or `None` |
| `GATE_PYTHON_INVALID` | `GatePythonError` | `INPUT_ERROR` | `2` | `install --python` names an interpreter that cannot import `devkit.gate` |
| `GATE_VERIFY_FAILED` | `GateRefusedError` | `BLOCKED` | `1` | a `verify-commands` command exited nonzero; one `command: ... exit=... log=...` detail per failed command, then its summaries, failed tests or last lines and relayed `devkit` error blocks (`  > `) |
| `GATE_VERIFY_NOT_RUN` | `VerifyNotRunError` | `MAINTENANCE`, or `AUTO` | `2` | a nested `devkit` command could not run (exit `2` with its own error block, such as `RULES_LOAD_FAILED`); same details; `AUTO` with the relayed fix when every relayed error is `AUTO` with that one fix (`devkit sync` for missing managed files) |
| `GATE_VERIFY_UNSTAGED` | `VerifyUnstagedNotice` | `NOTE` (level `NOTICE`) | `0` | returned, never raised: `verify-commands` ran on a working tree with unstaged or untracked files |
| `GATE_CONFIG_TEMPLATE_SKIPPED` | `GateTemplateNotice` | `CONTINUE` (level `WARNING`) | `0` | returned, never raised: `devkit.config` is a symbolic link, not a regular file or not UTF-8, or the `[gates]` table of `.devkit/config.toml` cannot be read, so `install` or the post-sync refresh left it alone |
| `GATE_FOREIGN_HOOK`, `GATE_BACKUP_EXISTS`, `GATE_HOOKS_PATH_SET` | `ForeignHookError`, `HookBackupExistsError`, `HooksPathSetError` | `INTERACTION` | `2` | `install` would move or bypass hooks it does not own |
| `CONFIG_INVALID` | `devkit.core.ConfigError` | `INPUT_ERROR` | `2` | `.devkit/config.toml` or `devkit.config` cannot be read or parsed |
| `ASSET_FILE_INVALID` | `devkit.core.AssetFileError` | `MAINTENANCE`; `AUTO` when missing | `2` | a receipt-listed gate file is unsafe or differs from its recorded hash; a missing one (a fresh clone or worktree) is `AUTO` with the fix `devkit sync` |
| `ARGUMENT_INVALID` | `devkit.core.ArgumentError` | `INPUT_ERROR` | `2` | `-w/--workspace-root` is not an existing directory; `run commit-msg` without the message file |
| `GIT_FAILED` | `devkit.core.GitError` | `INPUT_ERROR` outside a work tree, else `MAINTENANCE` | `2` | a Git query failed |
| `RECEIPT_INVALID` | `devkit.core.ReceiptError` | `MAINTENANCE` | `2` | `.devkit/installation.json` is malformed or lists an unsafe path |

## Built-in gates

| Gate | Stage | Default | Behavior |
| --- | --- | --- | --- |
| `verify-commands` | `pre-commit` | on, skipped while `commands` is empty | Runs `[gates.settings.verify-commands] commands` (shell lines, in order, from the work tree's top level, through `devkit.compact`) and refuses when any fails (`GATE_VERIFY_FAILED`, or `GATE_VERIFY_NOT_RUN` when a nested `devkit` command could not run); notes a working tree that differs from the commit (`GATE_VERIFY_UNSTAGED`). |
| `message-nonempty` | `commit-msg` | on | Refuses a message that is blank (whitespace only) above any scissors line. |

Outcomes and failure codes: [Built-in Gates](overview.md#2a-built-in-gates).

## Built-in git-commits bundle

Commit message policy is a bundle, not a gate: the package ships the opt-in bundle `git-commits` (sources in `src/devkit/gate/commits/bundle/`), deployed after `uv run devkit add git-commits`. Its preset `core` holds:

- the instruction `git-commits`: Conventional Commits types, optional scope, imperative subject, body and footer formatting, breaking changes and clean message output; listed by `devkit get-context git-commits`;
- the `guidance` fragment `commit-pointer`, which adds one line to the root `AGENTS.md` block: "Before drafting or creating a commit message, read `<path>` and follow it." The path is the managed copy, or the project override after `devkit override create git-commits:git-commits`.

It ships no gate: messages are not validated. Adapt the conventions (scope names, message language, issue references) with an override of the instruction.

## Configuration

`.devkit/config.toml` (tracked) is overridden by `<common-git-dir>/devkit.config` (untracked, per clone); see [Configuration Layers](overview.md#6-configuration-layers). A key in `devkit.config` replaces the project's value as a whole (an array too): in its commented template, uncomment a table's header and only the keys you change ([Settings Template](overview.md#6a-settings-template)).

```toml
[gates.settings.verify-commands]
commands = ["just lint-check", "uv run devkit rules check --staged"]

[gates.settings.<gate-id>]
enabled = true
some_setting = 3
```

## Library

```text
packages/devkit/src/devkit/gate/
├── errors.py       # GateError and its subclasses, one class per code
├── engine/         # models (Stage, GateResult, GateContext), BaseGate, layered config, registry, runner
├── hooks/          # wrapper scripts (install, uninstall, status) and Git queries
├── gates/          # built-in gates (verify-commands, message-nonempty)
├── commits/        # the git-commits guide bundle
├── cli/            # devkit gate (a thin layer over the library)
└── __main__.py     # python -m devkit.gate: the gate CLI alone, which the wrappers exec
```

`devkit gate` is a thin command line over `load_gate_project(root)` (gates, layered configuration, every problem `gate status` reports) and `run_hook(root, stage, args)` (one stage, as the hook wrapper runs it; `report.ok`, `report.problems`, `report.exit_code`). See [Library](overview.md#2-library).

## Writing a gate

```python
from dataclasses import dataclass

from devkit.gate import BaseGate, GateContext, GateRefusedError, GateResult, Stage


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

Declare the file as a `kind = "gate"` asset in `bundle.toml` and add it to a preset ([Distribution](overview.md#5-distribution)); the [Gate Contract](overview.md#4-gate-contract) defines results, refusals, context and ordering.
