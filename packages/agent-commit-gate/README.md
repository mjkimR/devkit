# agent-commit-gate

Pluggable Git commit gates (`commit-gate` CLI). The package owns the gate system: managed hook wrappers, layered configuration, gate discovery and the stage runner. Policy lives in content wheels that ship gates as `kind = "gate"` bundle assets, so selecting a bundle and running `devkit sync` adds its gates.

Architecture and design rationale: [Commit Gate Overview](../../docs/commit-gate/overview.md).

## Usage

```bash
uv add --dev agent-commit-gate
uv run commit-gate install      # writes pre-commit, commit-msg and post-commit wrappers
uv run commit-gate status       # hooks, gates with effective state, configuration layers
```

Adding gates from a content wheel:

```bash
uv add --dev <content-wheel>
uv run devkit add <bundle>:<preset>   # a preset that includes the bundle's gate assets
uv run devkit sync                    # deploys the gate files and records them in the receipt
```

`commit-gate run <stage> [hook args]` is what the wrappers call; run it by hand to test a stage. Set `DEVKIT_GATES_VERBOSE=1` (or pass `-v`) to also see passed and skipped gates. `git commit --no-verify` skips `pre-commit` and `commit-msg` as usual.

## Built-in gates

| Gate | Stage | Default | Behavior |
| --- | --- | --- | --- |
| `rules-staged` | `pre-commit` | on | Runs `agent-rule-engine`'s linter phase over the exact staged tree, as `agent-rules check --staged` does, and refuses on unresolved error violations, rule loading or execution errors, or an invalid `[rules]` policy. Warnings pass. |
| `message-nonempty` | `commit-msg` | on | Refuses a message that is empty once comment lines are removed. |

Built-ins are limited to the gate system's own integrations; anything that is
policy belongs in a bundle. `rules-staged` reads `.devkit/config.toml`, the
installation receipt and the synchronized rules from the staged tree itself
(Git-ignored managed rule copies are taken from the working tree only when they
match the receipt's hash), so unstaged edits cannot change the result. With
nothing staged it is skipped. Its refusal lists each violation as
`<rule> <file>:<line> <message>` and points at `agent-rules fix` and
`agent-rules explain <rule>`; when the rule engine is not importable from the
hook's interpreter the gate fails closed (`GATE_RULES_UNAVAILABLE`, fix: `uv sync`).

## Configuration

`.devkit/config.toml` (tracked) is overridden by `<common-git-dir>/devkit.config` (untracked, per clone):

```toml
[gates.settings.rules-staged]
enabled = false                 # e.g. a repository that runs agent-rules only in CI

[gates.settings.message-nonempty]
enabled = false

[gates.settings.<gate-id>]
enabled = true
some_setting = 3
```

## Writing a gate

```python
from dataclasses import dataclass

from agent_commit_gate import BaseGate, GateContext, GateError, GateResult, Stage


@dataclass(frozen=True)
class Settings:
    max_files: int = 50


class StagedFileLimitGate(BaseGate):
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
            raise GateError.blocked(f"{count} files staged (limit {ctx.settings.max_files})")
        return GateResult.passed()
```

Declare the file in `bundle.toml`:

```toml
[[assets]]
id = "staged-file-limit"
kind = "gate"
source = "gates/staged_file_limit.py"
```
