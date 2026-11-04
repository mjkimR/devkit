# [RULE-steering-documents] Steering Documents

## 1. Overview

`docs/steering/` holds project-wide background that applies to every piece of work but is neither a contract nor
evidence: the glossary, the product's purpose, a tone or style guide, a domain overview. One Markdown file covers one
topic. `devkit get-context docs` lists each file's `title` and `summary` in every agent context, and an agent reads a
body before a decision its summary covers. This rule keeps that always-loaded list short and readable.

- **Phase and severity**: `linter`, `error`.
- **What is checked**: the files under the root `docs/steering/` and under `docs/packages/<name>/steering/` of each
  namespace registered in `[[tool.docs.namespaces]]`, one directory at a time: a directory is checked when at least
  one of its files is targeted, and `max_files` counts each directory on its own. A namespace steering directory
  follows the root contract; its `glossary.md` and `glossary.yaml` are reported (see below), because the package
  glossary lives at `docs/packages/<name>/glossary.md` and search synonyms are read from `docs/steering/glossary.yaml`
  only.
- **What is not**: `README.md` is neither checked, counted nor listed. The root `glossary.yaml` (search synonyms) is
  allowed and not checked here. The steering directory of an unregistered `docs/packages/<name>/` is not checked.
  The IDs a steering file cites are checked by `RULE-document-reference`.

## 2. Cause of Violation

Each finding is reported at the file, on the line of the key concerned or line 1. A message names the directory it
concerns: `docs/steering/` below reads `docs/packages/<name>/steering/` in a namespace steering directory.

- A file in a subdirectory: `steering documents live directly in docs/steering/, not in <dir>/`.
- A file that is neither Markdown nor `glossary.yaml`: `docs/steering/ holds only Markdown files and glossary.yaml`.
  In a namespace steering directory, where `glossary.yaml` is not allowed either: `docs/packages/<name>/steering/
  holds only Markdown files`.
- `glossary.md` in a namespace steering directory, at line 1: `the package glossary lives at
  docs/packages/<name>/glossary.md, not in docs/packages/<name>/steering/`. Move it there; it does not count toward
  `max_files`.
- `glossary.yaml` in a namespace steering directory, at line 1: `docs/packages/<name>/steering/ holds only Markdown
  files`. Remove it; search synonyms are read from `docs/steering/glossary.yaml` only, and it does not count toward
  `max_files`.
- A file that is not UTF-8: `steering document must be UTF-8`. `devkit get-context` would list it with null values.
- Frontmatter that does not parse: `steering document frontmatter is invalid: <detail>`.
- Frontmatter that closes after the first 4096 bytes, all `devkit get-context` reads of a file: `frontmatter ends at
  byte <n>; get-context reads only the first 4096 bytes`.
- An `id` key: `steering documents carry no id`. A document with an ID belongs to its kind's directory.
- A missing or empty `title`: `steering document has no title`.
- A missing or empty `summary`: `steering document has no summary`.
- A summary with a letter outside the Latin script: `summary must be English; it contains <letters>`.
- A summary longer than `max_summary_length`: `summary has <n> characters (<max> at most)`.
- A body (the text after the frontmatter) larger than `max_body_bytes`: `body has <n> bytes; at most <max> are
  allowed`, at the first body line.
- More than `max_files` Markdown files in one directory: `docs/steering/ has <n> Markdown files; at most <max> are
  allowed`, on each file beyond the limit in sorted order. It is reported whenever any file of that directory is
  targeted, so the commit that adds a file is refused even when the new file sorts first.

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
