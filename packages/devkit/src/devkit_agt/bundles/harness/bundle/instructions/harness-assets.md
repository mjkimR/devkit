---
name: harness-assets
description: Read before adding, changing or testing a rule, gate or workflow asset, including in-repository rules.
---

# Rule, gate and workflow assets

| Kind | Run by | Tested with |
| --- | --- | --- |
| `rule` | `devkit rules check`, the `rules-check` commit gate and CI | `uv run devkit rules test <RULE-id>` |
| `gate` | `devkit gate` at its Git hook stage | the bundle's own tests |
| `workflow` | `devkit workflow next` through the `devkit-workflow` entry skill | `uv run devkit workflow validate` |

- Each asset is a plugin package directory: every `.py` file except tests is a
  module, `__init__.py` is optional, and sibling modules import each other
  relatively. Import nothing else but the engine's public API and installed packages.
- Put a rule's tests in its `tests/` folder and load the rule with
  `devkit_agt.features.rules.services.testing.load_rule(__file__)`.
- Prefix rule ids with the repository name (`RULE-<repo>-<topic>`); reuse an
  upstream id only to shadow that rule.
- To try an unfinished rule without recording it, run
  `uv run devkit rules check --rules-dir <dir>`.
- An in-repository bundle with these assets depends on `devkit-agt`, not
  `devkit-dist`; the `devkit` bundle's `in-repo-bundle` instruction has the setup.
  In a fresh clone and in CI, run `uv sync` and `uv run devkit sync --locked`
  before gates can pass.

Done when the tests command of each changed asset passes.
