# Commit Gate: Architecture Overview

**Status**: Architecture Specification & Reference Implementation  
**Package**: `agent-commit-gate` (`commit-gate` CLI)  
**Related Documents**:
- [Bundle Manifest Specification](../distribution/manifest-spec.md)
- [Synchronization & Transactions](../distribution/sync-and-transactions.md)
- [Rule Engine Overview](../rule-engine/overview.md)
- [Architecture Overview](../architecture/overview.md)

---

## 1. Overview and Objectives

`agent-commit-gate` runs policy at Git's commit hooks. It owns the **system**: hook wrappers, configuration layering, gate discovery and the stage runner. It deliberately owns almost no **policy**: gates that encode a team's or a person's commit rules ship in content wheels as `kind = "gate"` bundle assets, so installing a wheel, selecting its bundle and running `devkit sync` adds them, exactly as rules are added to `agent-rule-engine`.

### Core Principles

1. **System in the core, policy in bundles.** The core ships only trivial built-in gates. Identity checks, timestamp handling, message conventions and similar rules belong to the content wheels that need them.
2. **Static wrappers, runtime discovery.** The hook files never change after `commit-gate install`. Each commit discovers the gates from the installation receipt, so `devkit sync` alone changes what runs; it never writes into the hooks directory.
3. **Explicit opt-in.** Installing a wheel makes its gates available; selecting a preset that contains them deploys them; a gate may additionally ship disabled and require `enabled = true` in configuration.
4. **Fail closed where Git can still refuse.** `pre-commit` and `commit-msg` failures, configuration errors and missing gate files block the commit. `post-commit` runs after the commit exists and only reports.
5. **One error format.** Gate refusals and configuration problems are Agent Advisory Protocol errors (`agent-advisory`), so an agent reads the same `[ACTION]` contract it gets from every other devkit CLI.

---

## 2. Subsystem Layout

```text
packages/agent-commit-gate/src/agent_commit_gate/
├── models.py      # Stage, Outcome, GateResult, GateContext, Gate protocol, GateError, GateConfigError
├── base.py        # BaseGate: the class deployed gate files subclass
├── config.py      # Layered [gates] configuration and typed settings resolution
├── registry.py    # Built-ins plus receipt-deployed gate files
├── runner.py      # run_stage: ordering, enablement, settings, outcome collection
├── hooks.py       # Wrapper scripts: install, uninstall, status
├── git.py         # repo root, common git dir, hooks dir
├── gates/         # Built-in gates (message-nonempty)
└── cli/           # commit-gate: install, uninstall, status, run
```

---

## 3. Hook Wrappers

`commit-gate install` writes `pre-commit`, `commit-msg` and `post-commit` into the repository's hooks directory (`git rev-parse --git-path hooks`, shared by every worktree). Each wrapper records the interpreter that installed it and runs:

```sh
exec "$python" -m agent_commit_gate run <stage> "$@"
```

- **Interpreter**: `sys.executable` of the installing process, normally the project's `.venv/bin/python`. `--python` overrides it. Wrappers do not depend on `PATH`, so Git GUIs and agent shells behave like a terminal.
- **Missing environment**: a blocking stage exits `1` with a `run 'uv sync'` hint; `post-commit` exits `0`.
- **Existing hooks**: hooks without the managed marker are never overwritten silently. `install` refuses (`GATE_FOREIGN_HOOK`); `install --force` moves them to `<hook>.pre-gate` and `uninstall` restores them.
- **`core.hooksPath`**: when set, another tool owns hook placement and `install` refuses (`GATE_HOOKS_PATH_SET`).
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

- **Passing and skipping**: return `GateResult.passed(note)` or `GateResult.skipped(reason)`; `None` means passed.
- **Refusing**: raise an `AdvisoryError`, normally `GateError.blocked(...)`. Any other exception is wrapped as `UNEXPECTED_ERROR` and also fails the gate.
- **Context**: `ctx.repo_root`, `ctx.git_dir` (common git dir), `ctx.stage`, `ctx.args` (hook arguments), `ctx.settings` (the gate's effective settings) and `ctx.message_file` for `commit-msg`.
- **Ordering**: gates in a stage run by `(order, id)`. Message transforms use `order < 100`, checks default to `100`, and the built-in `message-nonempty` runs at `900` so it sees the transformed message. A `post-commit` gate that rewrites `HEAD` must take a low order so later gates observe the final commit.
- **No short-circuit**: a failing gate does not stop later gates, so one commit attempt reports every refusal.

Gate files are loaded like rule files: every concrete `BaseGate` subclass defined in the file is instantiated without arguments. A gate file may import from any package installed in the same environment, which lets a content wheel keep its logic in a library module and ship only a thin gate file.

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

`devkit sync` copies the selected gate files to `.devkit/managed/<bundle>/` (or uses the project override under `.devkit/overrides/<bundle>/`) and records them in `.devkit/installation.json`. At commit time the registry loads every `.py` path of every `kind = "gate"` asset in the receipt.

| State | Effect at commit time |
| --- | --- |
| Wheel installed, bundle not selected | Gate absent |
| Bundle selected, synchronized | Gate loaded; runs if enabled |
| Receipt lists a gate file the disk lacks | Blocking stages fail with `fix: devkit sync` |
| Gate file fails to import, or two gates share an id | Blocking stages fail |

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

[gates.settings.message-nonempty]
enabled = false
```

- `enabled` is reserved in every gate table and overrides `enabled_by_default`.
- Other keys must match the gate's settings dataclass fields; unknown keys and wrong types fail the stage before the gate runs.
- An entry for a gate that is not installed fails blocking stages, so a typo or a forgotten `devkit sync` cannot silently disable policy.
- `devkit-distribution` passes `[gates]` through untouched, as it does `[rules]` and `[workflow]`.

---

## 7. CLI

| Command | Purpose |
| --- | --- |
| `commit-gate install [--force] [--python PATH]` | Write the managed wrappers. |
| `commit-gate uninstall` | Remove managed wrappers; restore hooks moved aside by `--force`. |
| `commit-gate status [--format text\|json]` | Hook states, every gate with stage, order, effective enablement and source, configuration layers, load errors. |
| `commit-gate run <stage> [hook args] [-v]` | Run one stage; what the wrappers call. `DEVKIT_GATES_VERBOSE=1` equals `-v`. |

Output uses sentinel lines (`[HOOK: …]`, `[GATE: <id> stage=<stage> outcome=<outcome>]`, `[CONFIG: sources=…]`) followed by advisory blocks for failures.
