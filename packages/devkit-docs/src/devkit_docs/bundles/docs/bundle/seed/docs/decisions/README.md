# Architecture Decision Records (ADR)

Record important choices and their reasons. The selected development approach defines how decisions are revised and retained.

Do not manually maintain catalog tables of individual ADRs in this README. Catalog discovery is performed dynamically by parsing frontmatter metadata.

## Directory Layout & Naming Conventions

```text
docs/decisions/
└── {YYYY-MM}/
    └── {YYYYMMDD}-{slug}.md
```

- `{YYYY-MM}`: Year-month partition when the decision was accepted. `{YYYYMMDD}`: Decision date. `{slug}`: Kebab-case semantic identifier.
- The reference identifier is `ADR-{slug}`. The date prefix is metadata for ordering, not part of the identifier; reference documents in prose as `ADR-{slug}` without Markdown file paths. Number-based or date-based references are rejected by `RULE-id-convention`.

## Frontmatter Schema

```markdown
---
id: ADR-<slug>
title: <Decision Title>
summary: "For <context>, we <decision>, to <achieved quality>, accepting <downside>." # required, English Y-statement
status: accepted # proposed | accepted | superseded | rejected | deprecated
created_at: <YYYY-MM-DD>
supersedes: [] # optional
superseded_by: null # optional
---

# [ADR-<slug>] <Decision Title>

## 1. Context & Problem Statement
## 2. Decision Drivers
## 3. Considered Options
## 4. Decision Outcome & Rationale
## 5. Consequences
## 6. Confirmation
```
