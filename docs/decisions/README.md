# Architecture Decision Records (ADR)

A permanent ledger recording critical technical and structural decisions, as well as architectural invariants. A decision is never changed in place: reversing, invalidating or changing a decision takes a new ADR that names the earlier one in `supersedes`; the earlier ADR becomes `superseded` with `superseded_by` only when all of its decisions are replaced, and otherwise stays `accepted` with a "Superseded in part by" line. The documents themselves may be edited without changing any decision's meaning: wording, format, stale names and references, metadata, and consolidation of related ADRs into one that lists their IDs in `aliases` (the `adr-compaction` playbook) (`ADR-immutable-decisions-editable-records`).

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
status: accepted # proposed | accepted | superseded | rejected | deprecated; superseded only when wholly replaced
created_at: <YYYY-MM-DD>
supersedes: [] # optional: the ADRs this one replaces, wholly or in part
superseded_by: null # optional: only on a superseded ADR; one replaced in part stays accepted with a "Superseded in part by" line
---

# [ADR-<slug>] <Decision Title>

## 1. Context & Problem Statement
## 2. Decision Drivers
## 3. Considered Options
## 4. Decision Outcome & Rationale
## 5. Consequences
## 6. Confirmation
```
