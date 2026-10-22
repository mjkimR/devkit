# [RULE-code-entrypoints] Live Code Entrypoints

## 1. Overview

A capability or use case may declare `entrypoints` in its frontmatter: the files and directories where its
implementation starts. They are anchors for finding the code (`devkit spec list capability --file <path>` finds the
documents that own a path), not a complete list of the implementation and not proof that the code implements the
document. The rule keeps every declared path alive, so an agent following an entrypoint never lands on nothing.

- **Phase and severity**: `linter`, `error`.
- **What is checked**: capabilities (`CAP-`) and use cases (`UC-`) under `docs/capabilities/`, `docs/usecases/` and the
  same directories of a namespace docs root `docs/packages/<name>/`, when they declare `entrypoints`. An omitted
  field and an empty list pass.
- **Path contract**: files or directories, relative to the workspace root and written with `/`, whatever the
  document's directory; `src/a` covers `src/a/b.py`, not `src/ab`.
- **Targeting**: violations are reported in the targeted documents. `--staged` and `--ci` also check every current
  document not matched by `[rules] exclude` that declares a path the diff deletes (or a directory containing it), so
  deleting code without touching the document that declares it fails the commit gate too. Snapshot runs resolve
  paths in the snapshot's tree, where an empty directory does not exist, so an unstaged or untracked path or an
  empty directory fails only there: stage the code rather than edit the declaration.

## 2. Cause of Violation

Reported at the offending list item, or at the `entrypoints` key:

- The field is not a list: `entrypoints must be an array of path strings`.
- An item is not a string: `entrypoints must contain only path strings`.
- An item is empty or blank, absolute, or contains a backslash, a colon, a glob character (`*`, `?`, `[`, `]`), NUL
  or a line break: `invalid entrypoint '<value>': use a literal workspace-relative path`.
- An item has a `..` segment: `invalid entrypoint '<value>': parent traversal is forbidden`.
- The path is neither a file nor a directory inside the workspace, or is a symbolic link resolving outside it:
  `Dead code entrypoint: '<value>' (missing or outside workspace)`.

## 3. Remediation

Not fixable: the rule never guesses whether the code moved or the declaration is obsolete. Restore the code, point
the declaration at where the code moved, or remove an obsolete declaration.
`devkit spec entrypoints derive --spec <bundle>` proposes paths from a spec bundle's `tasks.md` boundaries.

## 4. Configuration

No settings.

## 5. Exceptions

No inline suppression. Remove a declaration rather than excuse it: an entrypoint is optional, and one that does not
exist misleads. `[rules] exclude` removes a file from every rule.

## 6. Example

```yaml
entrypoints:
  - src/example/engine.py
  - src/example/cli/
```
