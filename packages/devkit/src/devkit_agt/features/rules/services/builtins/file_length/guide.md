# [RULE-file-length] File Byte Budget

## 1. Overview

This hygiene warning signals how much file content an agent loads, independently of line wrapping. It does not
prove topic cohesion or authorize deleting retained contracts.

- **Phase and severity**: `hygiene`, `warning`. Only `devkit rules check --phase hygiene` runs it by default;
  ordinary checks, the commit gate and CI do not run this rule.
- **Targets**: files with configured suffixes (default `.md`), subject to normal targets and exclusions.

## 2. Cause of Violation

The rule counts raw file bytes through `ctx.cache.read_bytes`, so a snapshot run uses its evaluated snapshot.
The default is 49152 bytes (48 KiB). Exactly the selected budget passes; a larger file reports a file-level
finding at line 1 with `File exceeds byte budget (<actual> > <limit> bytes)`.

Markdown normally uses UTF-8, but the count is raw bytes rather than characters or reencoded decoded text. CRLF
counts two bytes; a final newline counts its bytes. Empty content is zero. No newline normalization or tokenizer
is applied.

## 3. Remediation

Split at a meaningful topic boundary and link the parts. Preserve guarantees, decisions and outcomes. If a file
is cohesive at its measured size, configure an exact-path budget with its reason. The rule never rewrites files.

## 4. Configuration

```toml
[rules.settings.RULE-file-length]
extensions = [".md"]
max_bytes = 49152
consolidated_max_bytes = 65536 # Optional; omitted keeps ordinary budgets.

# Capabilities retain complete interface and failure contracts.
[[rules.settings.RULE-file-length.overrides]]
path = "docs/capabilities/**"
max_bytes = 65536
```

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `max_bytes` | positive integer | `49152` | Raw bytes allowed per file. |
| `consolidated_max_bytes` | positive integer or omitted | omitted (`None`) | Alternative budget for qualifying Markdown records. |
| `extensions` | list of literal suffixes | `[".md"]` | Checked suffixes. An empty list checks none. |

Path overrides are workspace-relative patterns. Standalone `**` matches zero or more segments; `*`, `?` and
character classes match within one segment. Later matching overrides win; omitted keys inherit earlier values.
Boolean, string, zero and negative budgets, invalid extensions and unknown keys fail before execution with
`RULES_SETTINGS_INVALID` and exit 2.

### Consolidated records

When `consolidated_max_bytes` exists, targeted Markdown above its ordinary budget qualifies only with a nonempty
string `id`, a list containing only nonempty string aliases, and either:

- an `ADR-` ID with at least two distinct aliases;
- an `FB-consolidated-<area>-<status>` ID with at least one alias. Area is a lowercase alphanumeric slug with
  optional hyphenated namespace segments. Status is `resolved`, `promoted`, `dismissed` or `forwarded`.

Duplicates count once. Empty/whitespace-only aliases, malformed values, missing/malformed headers, PADRs and other
IDs keep the ordinary budget. ADR aliases are a heuristic: repeated renames can qualify without consolidation.
The rule neither proves consolidation provenance nor changes grouping authority.

A qualifying file uses `max(max_bytes, consolidated_max_bytes)` after path overrides. A higher ordinary override
stays higher. A path may replace either setting; omit the optional key to disable it (TOML has no null).
An eligible over-budget record reports the same numeric byte message at line 1 and advises reviewing its group by
topic while preserving every retained decision or outcome. Header lookup occurs only when the optional budget can
apply to over-budget Markdown.

### Migration from line settings

Replace `max_lines` with an intentionally chosen `max_bytes`, and `consolidated_max_lines` with
`consolidated_max_bytes`, including overrides. There is no line-to-byte conversion or second metric mode.
Old keys are unknown settings and fail with `RULES_SETTINGS_INVALID`. The rule ID and Python class/module names
remain stable; `FileLengthRule` takes `max_bytes`.

## 5. Exceptions

Prefer an exact-path override with a reason comment. A size warning calls for review, not mechanical deletion.
`[rules] exclude` removes files from every rule and is rarely the right size exception.
