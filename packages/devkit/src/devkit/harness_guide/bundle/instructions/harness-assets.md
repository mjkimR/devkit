---
name: harness-assets
description: Read before adding, changing or testing a rule, gate or workflow asset, including the rules of an in-repository bundle. Covers how the devkit-agt engines run and test these assets, how in-repository rules reach Git snapshot gates, trying an unfinished rule, and the devkit-agt development dependency they need.
---

# Rule, gate and workflow assets

The `devkit` bundle's `resource-kinds` instruction says when to author a rule,
a gate or a workflow, and its `in-repo-bundle` instruction how to ship them in
a bundle of the repository's own. This instruction covers what the engines of
`devkit-agt` do with them.

## How they run

| Kind | Run by | Tested with |
| --- | --- | --- |
| `rule` | `devkit rules check` (working tree), the `rules-check` commit gate (`--staged`) and CI (`--ci`); loaded from the receipt | `devkit rules test <RULE-id>` |
| `gate` | `devkit gate` at its Git hook stage | the bundle's own tests |
| `workflow` | `devkit workflow next`, through the generated `devkit-workflow` entry skill | `devkit workflow validate` |

Rules, gates and workflow checks are plugin package directories: every
`.py` file in one is a module (tests under `tests/` or named `test_*.py`
are never imported), `__init__.py` is optional, and modules import each
other relatively (`from .helpers import parse`). They import only their
engine's public API and installed packages; the bundle package never
imports them. A rule's tests go in its `tests/` folder, load the rule with
`devkit.rules.testing.load_rule(__file__)` and run with
`devkit rules test <RULE-id>`.

## Rules of an in-repository bundle

A repository whose own bundle ships rules depends on `devkit-agt` (not only
`devkit-dist`) in the dev group next to the bundle package; `devkit-agt`
brings `devkit-dist`, so the project declares one of them:

```toml
[dependency-groups]
dev = ["devkit-agt", "<repo>-devkit"]

[tool.uv.sources]
devkit-agt = { git = "https://github.com/mjkimR/devkit.git", subdirectory = "packages/devkit" }
"<repo>-devkit" = { workspace = true }
```

`devkit rules check --staged` and `--ci` evaluate a Git tree. The managed rule
copies are Git-ignored, so the gate reads them from the working tree only when
their SHA-256 matches the committed receipt. Therefore:

- Stage the updated receipt with every rule change; a stale receipt fails the
  gate and names `devkit sync` as the fix.
- A fresh clone runs `uv sync` and `uv run devkit sync --locked` before gates
  can pass; CI runs the same, and it fails (`RECEIPT_STALE`) when a bundle
  source was committed without its receipt.
- Prefer rule ids prefixed with the repository name
  (`RULE-<repo>-<topic>`) unless the intent is to shadow an upstream rule.

| Need | Mechanism |
| --- | --- |
| Change a setting, phase or severity of an installed rule | `[rules]` in `.devkit/config.toml` |
| Try an unfinished rule without recording it | `devkit rules check --rules-dir <dir>` (with `--staged`/`--ci` only a tracked directory inside the repository is read, from the snapshot; the commit gate never takes it) |
