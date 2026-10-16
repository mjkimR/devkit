# [RULE-skill-document-size] Skill Document Size Budget

## 1. Overview

A skill or playbook is loaded whole when it runs; an oversized one spends context on content most runs never need
and buries the steps that matter. The rule warns when a skill or playbook Markdown file outgrows its budget.

- **Phase and severity**: `hygiene`, `warning`; runs under `devkit rules check --phase hygiene` only. Shipped by the
  opt-in `authoring` bundle (preset `skill-authoring`).
- **What is checked**: the targeted files with a suffix in `extensions` (default `.md`) matching `paths`: project
  skills (`.agents/skills/**`, `.claude/skills/**`) and bundle sources (`**/bundle/skills/**`,
  `**/bundle/playbooks/**`). Files the installation receipt owns (agent projections of bundle skills) are skipped:
  fix the bundle source instead. Symbolic links are skipped, so each original is reported once.

## 2. Cause of Violation

- A file is larger than `max_bytes` UTF-8 bytes (default 12288): `File has <n> bytes; effective max_bytes is <max>`.
  The default is 12 KiB. The whole file counts, including YAML frontmatter, comments and whitespace; each
  supporting Markdown file is measured separately, not summed with `SKILL.md`.

## 3. Remediation

Follow Step 2 of the `skill-authoring` playbook (`uv run devkit playbook search "restructure a large skill"`):

1. Split content needed only in some situations into focused `references/` files, stating when each is read.
2. Keep `SKILL.md` a thin router with always-required constraints; remove repeated explanation.
3. Aim for each resulting file to use about 75-80% of its effective `max_bytes`, leaving room for later edits.
   This is restructuring guidance, not an additional limit: files between that range and the limit do not warn.
4. Review supporting files the same way. Do not merely trim the document to just below the warning threshold.

Never hide an always-required safety or boundary constraint in a rarely read file, and do not shrink a file by
joining lines or splitting one inseparable procedure into arbitrary fragments: size is a signal for review, not a
goal. The rule never rewrites files.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `max_bytes` | positive integer | `12288` | Bytes allowed per file. |
| `extensions` | list of literal suffixes | `[".md"]` | Files measured. |
| `paths` | list of patterns | the four skill and playbook locations above | Where skills live. |

```toml
[rules.settings.RULE-skill-document-size]
paths = [".agents/skills/**", "tools/agents/**"]

# Read as one procedure; split deferred.
[[rules.settings.RULE-skill-document-size.overrides]]
path = ".agents/skills/release/SKILL.md"
max_bytes = 16384
```

Patterns are workspace-relative; a standalone `**` matches zero or more path segments.

## 5. Exceptions

Record a justified exception as an exact-path override with the reason in a comment directly above it; update or
remove it when the file moves or shrinks.
