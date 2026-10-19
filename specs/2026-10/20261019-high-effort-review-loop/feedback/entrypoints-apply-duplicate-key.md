---
id: FB-entrypoints-apply-duplicate-key
title: entrypoints derive --apply writes a second entrypoints key when created_at precedes the existing one
scope: repo
kind: friction
category: tool-error
target: packages/devkit-spec/src/devkit_spec/entrypoints/apply.py (devkit spec entrypoints derive --apply)
skill: spec-entrypoints
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-entrypoints-apply-duplicate-key] entrypoints derive --apply writes a second entrypoints key when created_at precedes the existing one

## 1. Friction / Question (friction, question)

- **Context**: `spec-sync` Step 2b of `SPEC-high-effort-review-loop`: applying one reviewed candidate with
  `devkit spec entrypoints derive --spec <unit> --apply --target CAP-DLV-delivery-workflows --code <review-loop.md>`.
  The capability's frontmatter order is `id`, `title`, `summary`, `area`, `status`, `created_at`, `stories`,
  `entrypoints`.
- **Expectation**: `set_entrypoints` docstring: "An existing `entrypoints` key is replaced where it stands (with every
  line of its value); without one the block goes before `created_at`".
- **Actual**: the command reported `[APPLIED: ... added=<review-loop.md>]` and wrote a new `entrypoints:` block before
  `created_at`, leaving the original `entrypoints:` block after `stories`. The frontmatter became invalid YAML
  (duplicate key): `devkit rules check docs/capabilities/delivery` then reported `RULE-spec-format` "frontmatter is
  malformed" on the capability and `RULE-document-reference` "no document has the ID CAP-DLV-delivery-workflows" in
  nine referring files.
- **Workaround (or Interpretation Chosen)**: removed the inserted block by hand and appended the path to the original
  list; `devkit rules check` passed again.
- **Suggestion**: in `set_entrypoints`, decide between "replace" and "insert before `created_at`" only after scanning
  the whole header for an existing key (or skip the `created_at` branch when `_KEY` matches any later line), and add
  a test with `entrypoints` after `created_at`. The command could also re-parse the header it wrote and refuse to
  save a malformed one.

## Evidence

- `apply.py` `set_entrypoints`: the loop checks `_KEY` and `_CREATED` line by line with one `inserted` flag; when
  `created_at:` comes first it inserts the rendered block there, sets `inserted = True`, and the later existing
  `entrypoints:` line is then copied unchanged.
- Resulting header excerpt: `status: active` / `entrypoints:` (4 entries) / `created_at: 2026-10-13` / `stories:` ... /
  `entrypoints:` (3 entries) / `---`.

- **Disposition**: packages/devkit-spec/src/devkit_spec/entrypoints/apply.py: an existing entrypoints key is replaced wherever it stands; created_at insertion only when there is none
