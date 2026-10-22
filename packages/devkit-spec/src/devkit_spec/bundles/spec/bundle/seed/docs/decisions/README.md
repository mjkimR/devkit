# Architecture Decision Records (ADR)

A permanent ledger recording critical technical and structural decisions, as well as architectural invariants. Approved ADRs are never deleted or retroactively modified; when an update is needed, create a new ADR linked via `supersedes` and `superseded_by`. The only exception is compaction (the `adr-compaction` playbook): related approved ADRs are replaced by one ADR that lists their IDs in `aliases`, without changing any decision.

Do not manually maintain catalog tables of individual ADRs in this README. Catalog discovery is performed dynamically by parsing frontmatter metadata.

## Directory Layout & Naming Conventions

```text
docs/decisions/
└── {YYYY-MM}/
    └── {YYYYMMDD}-{slug}.md
```

- `{YYYY-MM}`: Year-month partition when the decision was accepted. `{YYYYMMDD}`: Decision date. `{slug}`: Kebab-case semantic identifier.
- The reference identifier is `ADR-{slug}`. The date prefix is metadata for ordering, not part of the identifier; reference documents in prose as `ADR-{slug}` without Markdown file paths. Number-based or date-based references are rejected by `RULE-id-convention`.
- Preliminary decisions during proposal stages reside at `docs/proposals/PROP-{slug}/decisions/PADR-{slug}.md` and are graduated to this ledger upon acceptance via `devkit spec proposal handoff`.

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
