---
id: FB-selection-edits-rewrite-crlf-line-endings
title: Selection edits rewrite CRLF line endings of .devkit/config.toml
scope: repo
kind: friction
category: tool-error
target: packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py (_document, prepare_config_update)
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-selection-edits-rewrite-crlf-line-endings] Selection edits rewrite CRLF line endings of .devkit/config.toml

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-approval-mode-and-crlf-template` made `devkit config template` keep a CRLF file's line endings;
  its Non-Goal 2 left the selection edits out of scope.
- **Expectation**: `CAP-DIST-sync-and-transactions` (Commented Template, **Selection edits**) places a new `agents`
  or `[presets]` entry in the file; nothing says the other lines change.
- **Actual**: `_document` reads the file with `read_text("utf-8")`, which translates CRLF to LF, and
  `prepare_config_update` writes `tomlkit.dumps` of it, so every line of a CRLF file ends in LF after one selection
  edit.
- **Workaround (or Interpretation Chosen)**: none; recorded for a later unit.
- **Suggestion**: parse the untranslated text (`read_bytes().decode("utf-8")`) as `_template` now does, so tomlkit
  keeps the existing line endings, and convert the added entry's LF to CRLF in a file whose every line ending is CRLF,
  with a regression test.

## Evidence

```text
before: b'schema = 1\r\n\r\n[presets]\r\nspec = "core"\r\n'
update_config(root, agents=["claude"])
after:  b'schema = 1\nagents = ["claude"]\n\n[presets]\nspec = "core"\n'
```
