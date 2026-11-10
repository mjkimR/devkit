---
id: ADR-<slug>
title: Decision Title
summary: "For <context>, we <decision>, to <achieved quality>, accepting <downside>."   # required, English Y-statement (decision-writing); quote it, it may contain ": "
status: proposed          # proposed | accepted | deprecated | superseded (only when a later ADR replaces all of its decisions; decision-writing)
created_at: YYYY-MM-DD
# supersedes: [ADR-<slug>]   # optional: ADRs this one replaces, wholly or in part; write Supersedes in part `ADR-<old>`: <the replaced clauses>. in Decision Outcome
---

# [ADR-<slug>] Decision Title (e.g., Select PostgreSQL as Main RDBMS)

<!-- File path is docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md and id is ADR-<slug>. -->
<!-- Replaced only in part: stay Accepted and add one line per later ADR here: Superseded in part by `ADR-<new>`: <the replaced clauses>. -->

- **Status**: Proposed | Accepted | Deprecated | Superseded by `ADR-<slug>`
- **Date**: YYYY-MM-DD
- **Deciders**: @author, @collaborator
- **Involved Components/Capabilities**: `architecture/`, `capabilities/<area>/`

---

## 1. Context & Problem Statement
<!-- Clearly describe the technical/architectural problem, constraints (cost, timeline, performance, regulatory), and current challenges. -->

---

## 2. Decision Drivers
- Driver 1: <!-- e.g., Need for data consistency and ACID guarantees -->
- Driver 2: <!-- e.g., Team technical familiarity and productivity -->
- Driver 3: <!-- e.g., Operational infrastructure cost reduction -->

---

## 3. Considered Options

### Option 1: [Selected Alternative Name] (Selected)
- **Overview**: Brief description of the option.
- **Pros**:
  - Pro 1
  - Pro 2
- **Cons**:
  - Con 1

### Option 2: [Alternative B Name]
- **Overview**: Brief description of the option.
- **Pros**: ...
- **Cons**: ...

---

## 4. Decision Outcome

<!-- Per earlier ADR not superseded, write: Supersedes in part `ADR-<old>`: <the replaced clauses>.
The earlier ADR pointer repeats this source text, code spans included. Keep each statement a separate item or paragraph without trace, source citation, nested list or relative link. -->
We decided to adopt **[Option 1]**.

<!-- One declarative list item per clause (decision-writing). A clause that a capability or architecture document restates ends with its trace: the ID (`CAP-<AREA>-<slug>` or `ARCH-<id>`), the section or rule, and the keyword that document uses. A rationale clause carries no trace. -->
- <declarative clause>. → `CAP-<AREA>-<slug>` <section or rule> (<MUST|SHOULD|MAY>)
- [Option 1] best satisfies [Driver 1] and [Driver 2] in a balanced manner, and potential drawbacks can be mitigated through ...

---

## 5. Consequences
- **Positive**:
- **Negative / Risks**:
- **Follow-ups**:

---

## 6. Confirmation
<!-- How compliance is checked: a rule ID, a test path, a review step or the restating IDs of Decision Outcome; "Review only" when no check exists. -->
