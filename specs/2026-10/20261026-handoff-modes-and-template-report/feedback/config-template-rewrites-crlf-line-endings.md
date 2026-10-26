---
id: FB-config-template-rewrites-crlf-line-endings
title: devkit config template rewrites CRLF line endings when it adds a part
scope: repo
kind: friction
category: tool-error
target: packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py (_template, _write)
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-config-template-rewrites-crlf-line-endings] devkit config template rewrites CRLF line endings when it adds a part

## 1. Friction / Question (friction, question)

- **Context**: the code review of `SPEC-handoff-modes-and-template-report` (review-01, finding 1) probing
  `devkit config template` for byte changes its result does not report.
- **Expectation**: "no line is changed or removed" (`CAP-DIST-sync-and-transactions`, Commented Template): existing
  lines keep their bytes, line endings included.
- **Actual**: `_template` reads the file with `read_text("utf-8")`, which translates CRLF and lone CR to LF, and
  `_write` writes LF. A CRLF file that lacks a template part gets every existing line rewritten to LF, while `added`
  names only the template parts. A CRLF file with nothing missing is reported `unchanged` and left untouched.
- **Workaround (or Interpretation Chosen)**: none; outside the agreed scope of that unit, so recorded here.
- **Suggestion**: read without newline translation (`read_bytes().decode("utf-8")` or `open(newline="")`) and write
  the added lines in the file's own line ending, with a regression test on a CRLF file.

## Diagnostic Details

- **Reproduction**: write `schema = 1\r\n\r\n[presets]\r\nspec = "core"\r\n` to `.devkit/config.toml`, run
  `uv run devkit config template -w <dir>`, then `od -c .devkit/config.toml`.
- **Expected / Actual**: original lines end in `\r\n` / they end in `\n`.
- **Versions**: `dev-handoff-modes-and-template-report` at `3a4c3c7f`.
- **Conditions**: a CRLF or CR config file missing at least one template part.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-DIST-sync-and-transactions`, `FB-config-template-reports-unchanged-after-writing`.

## Disposition

Resolved by `SPEC-approval-mode-and-crlf-template`: `_template` reads the file without newline translation, so the rendered text keeps every existing byte, and converts the added lines to CRLF when every line ending of the file is CRLF; a mixed or LF file gets LF lines. `CAP-DIST-sync-and-transactions` (Commented Template) states the line-ending rule. Verified by the CRLF, LF and mixed regression tests in `test_config_template.py` (CRLF and mixed red on the base). The selection edits keep the same defect, recorded as `FB-selection-edits-rewrite-crlf-line-endings`.
