# [RULE-markdown-link] Relative Markdown Link Integrity

## 1. Overview

Every relative link in a Markdown file must point at a file or directory that exists. Moving or renaming a document
silently breaks the links to it; agents follow links to load context, so a broken one sends them to nothing.

- **Phase and severity**: `linter`, `error`. It runs in `devkit rules check`, the commit gate (`check --staged`) and
  CI (`check --ci`).
- **What is checked**: inline links and images, `[text](target)` and `![alt](target)`, in the Markdown files the run
  targets. The destination is resolved relative to the linking file, after removing a `?query` or `#fragment` and
  decoding percent-encoding and backslash escapes. A symlinked Markdown file is not checked itself: it is an alias of
  its target, which is checked and repaired at its own path.
- **What is not**: URLs with a scheme (`https:`, `mailto:`), fragment-only links (`#section`), root-relative and
  protocol-relative paths (`/x`, `//host`), reference-style links (`[text][ref]`) and autolinks; links inside fenced
  code blocks and inline code spans.
- **Snapshots**: in `--staged` and `--ci` runs the targets are the changed files plus every Markdown file whose links
  point at a path the diff deletes, so deleting a document fails the commit that breaks the links to it.

## 2. Cause of Violation

- The resolved file or directory does not exist: a typo, a moved or renamed file, or a wrong number of `../`.
- The message is `Broken relative markdown link '<target>'`, at the link's line and column.

## 3. Remediation

- **Autofix**: `devkit rules fix` rewrites a broken destination when exactly one Markdown file in the workspace has
  the destination's file name and the destination stays inside the workspace. The new path is relative to the
  linking file; the link text, title, query and fragment are kept, and a path with spaces or parentheses is written
  as `<...>`. Such violations are reported as fixable (`status=fixable`) with the candidate in the remediation.
- **By hand**: when no file or several files have that name, correct the path yourself, link a different document,
  or remove the link. A file that is not valid UTF-8 is never rewritten.

## 4. Configuration

The rule has no settings. Project policy in `.devkit/config.toml` applies as to every rule:

```toml
[rules]
exclude = ["docs/legacy/**"]            # files no rule targets

[rules.severity_overrides]
RULE-markdown-link = "warning"          # report without failing
```

## 5. Exceptions

There is no inline suppression. Exclude generated or vendored Markdown with `[rules] exclude`; files under
`.devkit/managed/` and `.devkit/overrides/` are never checked. An excluded file still counts as an existing target,
so links into it stay valid.

## 6. Example

```markdown
See [the setup guide](../development/setup.md).      <!-- checked -->
See [the site](https://example.com).                   <!-- not checked: URL -->
See [section](#install).                               <!-- not checked: fragment only -->
```
