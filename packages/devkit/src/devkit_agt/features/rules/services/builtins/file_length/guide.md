# [RULE-file-length] File Length Budget

## 1. Overview

Long files are hard for people to review and expensive for agents to load: an agent that needs one section pays for
the whole file. The rule warns when a file outgrows its line budget, so it is split at a meaningful boundary.

- **Phase and severity**: `hygiene`, `warning`. It runs only under `devkit rules check --phase hygiene`; ordinary
  checks, the commit gate and CI do not run it.
- **What is checked**: the targeted files whose suffix is in `extensions` (default `.md`).

## 2. Cause of Violation

- A file has more than `max_lines` lines (default 400). The violation is reported at line `max_lines + 1` with the
  message `File exceeds line length limit (<lines> > <max_lines> lines)`.
- Lines are counted as Git does: a final newline does not add a line, an empty file has none, CRLF counts like LF.

## 3. Remediation

Split the file at a meaningful boundary (a chapter, a component, a topic) and link the parts. Do not join lines to
fit the budget. When a file is long for a good reason, raise the budget for that path (section 4) instead. The rule
never rewrites files.

## 4. Configuration

```toml
[rules.settings.RULE-file-length]
extensions = [".md"]
max_lines = 300

# Research notes are long by nature.
[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"
max_lines = 800
```

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `max_lines` | positive integer | `400` | Lines allowed per file. |
| `extensions` | list of literal suffixes | `[".md"]` | Files checked (`.md`, `.py`, ...); an empty list checks none. |

Override `path` patterns are workspace-relative: a standalone `**` matches zero or more path segments, `*`, `?` and
character classes match within one segment. Later matching overrides win, and omitted keys inherit earlier values.
Unknown keys, wrong types and invalid patterns fail the run before any rule executes.

## 5. Exceptions

Prefer an exact-path override with the reason in a comment directly above it, so the exception stays visible and
reviewable. `[rules] exclude` removes files from every rule, which is rarely what a length exception needs.
