---
name: harness-assets
description: Read before adding, changing or testing a rule, gate or workflow asset, including in-repository rules.
---

# Rule, gate and workflow assets

## How they run

| Kind | Run by | Tested with |
| --- | --- | --- |
| `rule` | `devkit rules check` (working tree), the `rules-check` commit gate (`--staged`) and CI (`--ci`); loaded from the receipt | `devkit rules test <RULE-id>` |
| `gate` | `devkit gate` at its Git hook stage | the bundle's own tests |
| `workflow` | `devkit workflow next`, through the generated `devkit-workflow` entry skill | `devkit workflow validate` |

Rules, gates and workflow checks are plugin package directories:

- Every `.py` file is a module; tests under `tests/` or named `test_*.py` are never imported.
- `__init__.py` is optional.
- Import sibling modules relatively (`from .helpers import parse`); otherwise
  import only the engine's public API and installed packages.
- Do not import them from the bundle package.
- Put a rule's tests in its `tests/` folder and load the rule with
  `devkit_agt.features.rules.services.testing.load_rule(__file__)`.

## Rules of an in-repository bundle

If the repository's own bundle ships these assets, declare `devkit-agt` in the
dev group next to the bundle package, because `devkit-dist` deploys them but
runs none. `devkit-agt` brings `devkit-dist` at the same version, so declare
only `devkit-agt`:

```toml
[dependency-groups]
dev = ["devkit-agt", "<repo>-devkit"]

[tool.uv.sources]
devkit-agt = { git = "https://github.com/mjkimR/devkit.git", subdirectory = "packages/devkit" }
"<repo>-devkit" = { workspace = true }
```

`devkit rules check --staged` and `--ci` evaluate a Git tree and read the
Git-ignored managed rule copies only when their SHA-256 matches the committed
receipt. In a fresh clone and in CI, run `uv sync` and
`uv run devkit sync --locked` before gates can pass.

Prefix rule ids with the repository name (`RULE-<repo>-<topic>`); reuse an
upstream rule's id only to shadow that rule.

| Need | Mechanism |
| --- | --- |
| Change a setting, phase or severity of an installed rule | `[rules]` in `.devkit/config.toml` |
| Try an unfinished rule without recording it | `devkit rules check --rules-dir <dir>` (with `--staged`/`--ci` only a tracked directory inside the repository is read, from the snapshot; the commit gate never takes it) |

## Completion

- `uv run devkit rules test <RULE-id>` passes for each changed rule.
- `uv run devkit workflow validate` passes for a changed workflow.
