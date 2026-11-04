# [RULE-file-length] File Length Budget

## 1. Overview

Long files are hard for people to review and expensive for agents to load: an agent that needs one section pays for
the whole file. The rule warns when a file outgrows its line budget, so its topic breadth can be reviewed.

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
consolidated_max_lines = 600 # Optional; omit to retain ordinary limits.

# Research notes are long by nature.
[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"
max_lines = 800
```

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `max_lines` | positive integer | `400` | Lines allowed per file. |
| `consolidated_max_lines` | positive integer or omitted | omitted (`None`) | Alternative budget for qualifying Markdown records. |
| `extensions` | list of literal suffixes | `[".md"]` | Files checked (`.md`, `.py`, ...); an empty list checks none. |

Override `path` patterns are workspace-relative: a standalone `**` matches zero or more path segments, `*`, `?` and
character classes match within one segment. Later matching overrides win, and omitted keys inherit earlier values.
Unknown keys, wrong types and invalid patterns fail the run before any rule executes.

### Consolidated records

When `consolidated_max_lines` is set, a targeted Markdown file above its ordinary budget qualifies if its header
has a nonempty string `id`, a list containing only nonempty string aliases, and either:

- an `ADR-` ID with at least two distinct aliases;
- an `FB-consolidated-<area>-<status>` ID with at least one alias. Area is a lowercase alphanumeric slug, including
  hyphenated namespace-qualified areas. Status is `resolved`, `promoted`, `dismissed` or `forwarded`.

Duplicates count once. Empty or whitespace-only aliases, malformed alias values, absent or malformed frontmatter,
PADRs and other IDs keep the ordinary budget. ADR aliases are a heuristic: an ADR renamed twice can qualify without
having been consolidated. The rule does not validate document identity or prove consolidation provenance.

The selected budget is `max(max_lines, consolidated_max_lines)` after path overrides; a 900-line ordinary override
stays 900 with a consolidated budget of 600. A path override may replace either setting. Omission disables the
alternative budget; TOML has no null literal. Boolean, string, zero and negative values fail with
`RULES_SETTINGS_INVALID` and exit 2.

An eligible record above the selected budget warns at selected budget plus one, with the same numeric message.
Review its consolidation group by topic while preserving every retained decision or outcome. Never discard content
to meet a budget. Feedback grouping changes require a separate authorized decision. The rule never splits records.

## 5. Exceptions

Prefer an exact-path override with the reason in a comment directly above it, so the exception stays visible and
reviewable. `[rules] exclude` removes files from every rule, which is rarely what a length exception needs.
