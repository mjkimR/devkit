# devkit.gate

Pluggable Git commit gates (`devkit gate` CLI), part of the `devkit` distribution. The module owns the gate system: managed hook wrappers, layered configuration, gate discovery and the stage runner. Policy lives in content wheels that ship gates as `kind = "gate"` bundle assets, so selecting a bundle and running `devkit sync` adds its gates.

Architecture and design rationale: [Commit Gate Overview](overview.md).

## Usage

```bash
uv add --dev devkit
uv run devkit gate install      # writes pre-commit, commit-msg and post-commit wrappers into <common-git-dir>/hooks
uv run devkit gate status       # hooks, gates with effective state, configuration layers, problems that fail a commit
```

Adding gates from a content wheel:

```bash
uv add --dev <content-wheel>
uv run devkit add <bundle>:<preset>   # a preset that includes the bundle's gate assets
uv run devkit sync                    # deploys the gate files and records them in the receipt
```

`devkit gate run <stage> [hook args]` is what the wrappers call; run it by hand to test a stage. Set `DEVKIT_VERBOSE=1` (or pass `-v` before the stage, `devkit gate run -v pre-commit`) to also see passed and skipped gates as `[INFO]` lines; `DEVKIT_QUIET=1` hides notices and `DEVKIT_STRICT=1` makes a warning fail a blocking stage ([Agent-First Output](../architecture/agent-output.md#6-verbosity-and-strictness)). Hooks read these from the environment, since Git passes no flags. `git commit --no-verify` skips `pre-commit` and `commit-msg` as usual. Existing executable hooks are kept: `install --force` moves them to `<hook>.pre-gate` and the wrapper runs them before the gates. The wrapper prefers the work tree's `.venv` interpreter when `devkit` is installed there; see [Hook Wrappers](overview.md#3-hook-wrappers).

Exit codes: `install`/`uninstall` exit `0` or `2`; `status` is a report and exits `1` when it lists any problem that would fail a commit (`2` only when it cannot run, outside a Git work tree); `run` on a blocking stage exits with the highest exit code among the problems it reports: `1` when gates refused the commit, `2` for a configuration, registry, load or settings problem, a gate that failed with a non-refusal error, or a stage that cannot run (outside a Git work tree); `run post-commit` always exits `0` and renders its problems as warnings (`[WARN]`), since the commit already exists. Codes and the full table: [Commit Gate Overview, CLI](overview.md#7-cli).

## Built-in gates

| Gate | Stage | Default | Behavior |
| --- | --- | --- | --- |
| `rules-staged` | `pre-commit` | on | Runs `devkit.rules`'s linter phase over the exact staged tree, as `devkit rules check --staged` does, and refuses on unresolved error violations (`GATE_RULES_VIOLATION`). Rule loading or execution errors and an invalid `[rules]` policy fail it with the rule engine's own error, unchanged. Warning- and info-severity violations pass; remaining warnings are counted in a `GATE_RULES_WARNINGS` notice. |
| `message-nonempty` | `commit-msg` | on | Refuses a message that is blank (whitespace only) above any scissors line. Messages that are empty only once comment lines are stripped are left to Git, which aborts them itself. |

Built-ins are limited to the gate system's own integrations; anything that is
policy belongs in a bundle. `rules-staged` reads `.devkit/config.toml`, the
installation receipt and the synchronized rules from the staged tree itself
(Git-ignored managed rule copies are taken from the working tree only when they
match the receipt's hash), so unstaged edits cannot change the result. With
nothing staged it is skipped; a commit that only deletes files is still evaluated. Its refusal lists each violation as
`<rule> <file>:<line> <message>` and points at `devkit rules fix` and
`devkit rules explain <rule>`. It evaluates through `run_project_rules`, the
entry point `devkit rules check --staged` uses, so both apply the same
`[rules]` policy, including `exclude`.

## Built-in git-commits bundle

Commit message policy is a bundle, not a gate: the package ships the opt-in
bundle `git-commits` (sources in `src/devkit/gate/commits/bundle/`), deployed
after `uv run devkit add git-commits`. Its preset `core` holds:

- the instruction `git-commits`: Conventional Commits types, optional scope,
  imperative subject, body and footer formatting, breaking changes and clean
  message output; listed by `devkit get-context git-commits`;
- the `guidance` fragment `commit-pointer`, which adds one line to the root
  `AGENTS.md` block: "Before drafting or creating a commit message, read
  `<path>` and follow it." The path is the managed copy, or the project override
  after `devkit override create git-commits:git-commits`.

It ships no gate: messages are not validated. Adapt the conventions (scope
names, message language, issue references) with an override of the
instruction.

## Configuration

`.devkit/config.toml` (tracked) is overridden by `<common-git-dir>/devkit.config` (untracked, per clone):

```toml
[gates.settings.rules-staged]
enabled = false                 # e.g. a repository that runs devkit rules only in CI

[gates.settings.message-nonempty]
enabled = false

[gates.settings.<gate-id>]
enabled = true
some_setting = 3
```

## Library

`devkit gate` is a thin command line over two entry points:

```python
from devkit.gate import Stage, load_gate_project, run_hook

project = load_gate_project(root)  # gates, layered configuration, every problem `gate status` reports
report = run_hook(root, Stage.COMMIT_MSG, [".git/COMMIT_EDITMSG"])  # one stage, as the hook wrapper runs it
report.ok, report.problems, report.exit_code
```

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

Declare the file in `bundle.toml`:

```toml
[[assets]]
id = "staged-file-limit"
kind = "gate"
source = "gates/staged_file_limit.py"
```
