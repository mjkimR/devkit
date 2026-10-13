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

- A file is larger than `max_bytes` UTF-8 bytes (default 8192): `File has <n> bytes; effective max_bytes is <max>`.
  Bytes track token cost for English and Korean better than lines or characters.

## 3. Remediation

Follow Step 2 of the `skill-authoring` playbook (`uv run devkit playbook search "restructure a large skill"`):

1. Compress repeated explanation.
2. Move content needed only in some situations to `references/`, stating when each reference is read.
3. Keep `SKILL.md` a thin router to those references.
4. Review the supporting files the same way.

Never hide an always-required safety or boundary constraint in a rarely read file, and do not shrink a file by
joining lines: size is a signal for review, not a goal. The rule never rewrites files.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `max_bytes` | positive integer | `8192` | Bytes allowed per file. |
| `extensions` | list of literal suffixes | `[".md"]` | Files measured. |
| `paths` | list of patterns | the four skill and playbook locations above | Where skills live. |

```toml
[rules.settings.RULE-skill-document-size]
paths = [".agents/skills/**", "tools/agents/**"]

# Read as one procedure; split deferred.
[[rules.settings.RULE-skill-document-size.overrides]]
path = ".agents/skills/release/SKILL.md"
max_bytes = 12288
```

Patterns are workspace-relative; a standalone `**` matches zero or more path segments.

## 5. Exceptions

Record a justified exception as an exact-path override with the reason in a comment directly above it; update or
remove it when the file moves or shrinks.
