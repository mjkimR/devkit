# [RULE-file-length] File length warning

Files longer than the effective `max_lines` receive a warning with their actual
line count and limit. Split the file at a meaningful boundary, or change the
limit for that path. The rule never rewrites files.

This is a hygiene rule: it runs under `devkit rules check --phase hygiene` only.

Configure it in `.devkit/config.toml`:

```toml
[rules.settings.RULE-file-length]
extensions = [".md"]
max_lines = 300

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"
max_lines = 800

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/summary.md"
max_lines = 150
```

Without configuration the rule checks `.md` files at 400 lines. `max_lines`
must be a positive integer; `extensions` must be literal dot-prefixed strings,
and an empty array selects no files. Override paths are workspace-relative: a
standalone `**` matches zero or more path segments, while `*`, `?` and
character classes match within one segment. Later matching overrides win and
omitted keys inherit earlier values. Unknown keys, wrong types and invalid
patterns fail the run before any rule executes.

A final newline does not add a line; an empty file has zero lines.
