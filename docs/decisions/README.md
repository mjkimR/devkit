# Architecture Decision Records (ADR)

A permanent ledger recording critical technical and structural decisions, as well as architectural invariants. Approved ADRs are never deleted or retroactively modified; when an update is needed, create a new ADR linked via `supersedes` and `superseded_by`.

## Directory Layout & Naming Conventions

```text
docs/decisions/
└── {YYYY-MM}/
    └── {YYYYMMDD}-{slug}.md
```

- `{YYYY-MM}`: Year-month partition when the decision was accepted. `{YYYYMMDD}`: Decision date. `{slug}`: Kebab-case semantic identifier.
- The reference identifier is `ADR-{slug}`. Reference documents in prose as `ADR-{slug}` without Markdown file paths.
- Preliminary decisions during proposal stages reside at `docs/proposals/PROP-{slug}/decisions/PADR-{slug}.md` and are graduated to this ledger upon acceptance.

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
