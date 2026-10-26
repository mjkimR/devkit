# [RULE-steering-documents] Steering Documents

## 1. Overview

`docs/steering/` holds project-wide background that applies to every piece of work but is neither a contract nor
evidence: the glossary, the product's purpose, a tone or style guide, a domain overview. One Markdown file covers one
topic. `devkit get-context spec` lists each file's `title` and `summary` in every agent context, and an agent reads a
body before a decision its summary covers. This rule keeps that always-loaded list short and readable.

- **Phase and severity**: `linter`, `error`.
- **What is checked**: the files under the root `docs/steering/`, when at least one of them is targeted. There is no
  namespace copy of the directory; package glossaries stay at `docs/packages/<name>/glossary.md`.
- **What is not**: `README.md` is neither checked, counted nor listed. `glossary.yaml` (search synonyms) is allowed
  and not checked here. The IDs a steering file cites are checked by `RULE-document-reference`.

## 2. Cause of Violation

Each finding is reported at the file, on the line of the key concerned or line 1:

- A file in a subdirectory: `steering documents live directly in docs/steering/, not in <dir>/`.
- A file that is neither Markdown nor `glossary.yaml`: `docs/steering/ holds only Markdown files and glossary.yaml`.
- Frontmatter that does not parse: `steering document frontmatter is invalid: <detail>`.
- An `id` key: `steering documents carry no id`. A document with an ID belongs to its kind's directory.
- A missing or empty `title`: `steering document has no title`.
- A missing or empty `summary`: `steering document has no summary`.
- A summary with a letter outside the Latin script: `summary must be English; it contains <letters>`.
- A summary longer than `max_summary_length`: `summary has <n> characters (<max> at most)`.
- A body (the text after the frontmatter) larger than `max_body_bytes`: `body has <n> bytes; at most <max> are
  allowed`, at the first body line.
- More than `max_files` Markdown files: `docs/steering/ has <n> Markdown files; at most <max> are allowed`, on each
  file beyond the limit in sorted order. It is reported whenever any steering file is targeted, so the commit that
  adds a file is refused even when the new file sorts first.

## 3. Remediation

Not fixable: background is written, never generated. Remove `id:`; write `title:` and a one-sentence English
`summary:` that says when an agent reads the file; split or merge topics to stay within the caps, or raise a setting
when the project needs more.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `max_files` | positive integer | `10` | Markdown files allowed, `README.md` not counted. |
| `max_body_bytes` | positive integer | `24576` | UTF-8 bytes allowed in each file's body, the glossary included. |
| `max_summary_length` | positive integer | `300` | Characters allowed in a summary. |

```toml
[rules.settings.RULE-steering-documents]
max_files = 10
max_body_bytes = 24576
max_summary_length = 300
```

## 5. Exceptions

No inline suppression.

## 6. Example

```markdown
---
title: Product
summary: Read before naming a feature or writing user-facing text; states who the product serves and its principles.
---

# Product
```
