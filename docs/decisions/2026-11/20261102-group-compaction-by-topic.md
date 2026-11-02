---
id: ADR-group-compaction-by-topic
title: Group ADR compaction by topic instead of supersession closure
summary: "For ADR compaction, we group members by topic and let a partial supersession cross groups, keeping a wholly superseded ADR with its superseder, to keep each replacement one coherent decision area, accepting that a superseding statement may live in a different replacement than its target."
status: accepted
created_at: 2026-11-02
supersedes: [ADR-decision-ledger]
---

# [ADR-group-compaction-by-topic] Group ADR compaction by topic instead of supersession closure

- **Status**: Accepted
- **Date**: 2026-11-02
- **Deciders**: user, agent
- **Involved Components/Capabilities**: `CAP-DOCS-document-model`, the `adr-compaction` playbook

---

## 1. Context & Problem Statement

`ADR-decision-ledger` (Compaction) closes every compaction group under supersession. A few bridging supersessions can
therefore chain unrelated topics together. In the integration ADRs, one ADR that retires two clauses and one that
replaces three lifecycle rules joined 13 ADRs into a single component. Compacted as one replacement, it would hold
about 100 clauses and 30 aliases across five topics: a mega-ADR that nobody looks up as one decision.

The closure exists so that a replacement states only clauses in effect. A partial supersession does not need closure
for that: the target's replacement can leave out the replaced clauses, and the superseding statement lives in its own
replacement.

---

## 2. Decision Drivers

- Each replacement is one decision area a reader looks up.
- A replacement still states only the clauses in effect.
- No reference breaks, and no decision changes.
- `RULE-decision-supersession` keeps checking the metadata that remains.

---

## 3. Considered Options

### Option 1: Topic groups; partial supersession may cross groups (Selected)
- **Overview**: Group by topic. A wholly superseded ADR joins its superseder's group. A partial supersession may
  cross groups.
- **Pros**: Coherent replacements; a bridging ADR no longer drags unrelated topics together.
- **Cons**: A reader follows a superseding statement into another replacement.

### Option 2: Keep the closure; split the replacement into sections
- **Overview**: One replacement per closure, sectioned by topic.
- **Pros**: No rule change.
- **Cons**: Mega-ADRs whenever a few supersessions bridge topics.

### Option 3: Keep the closure; leave such components uncompacted
- **Overview**: Compact only closures that form one topic.
- **Pros**: No rule change.
- **Cons**: The most fragmented part of the ledger stays fragmented.

---

## 4. Decision Outcome

We adopt **Option 1**. It keeps each replacement one decision area while every replacement still states only clauses
in effect. This replaces the clause "A group is closed under supersession" of `ADR-decision-ledger`; its other
compaction clauses stay in force.

- A compaction group is formed by topic and holds two or more members. → `CAP-DOCS-document-model` §Decision supersession (MUST)
- A wholly superseded ADR joins the group of its superseder. → `CAP-DOCS-document-model` §Decision supersession (MUST)
- When a partially superseding member and its target land in different groups, the target's replacement leaves out
  the replaced clauses. The superseding replacement states what it replaced, and it cites the target's replacement
  ID. → `CAP-DOCS-document-model` §Decision supersession (MUST)
- An ADR kept outside the run whose `supersedes` names a compacted member names the member's replacement instead. That
  replacement carries the matching "Superseded in part by" line. → `CAP-DOCS-document-model` §Decision supersession (MUST)
- A compacted member that partially supersedes an ADR kept outside the run passes that entry on: its replacement lists
  the kept ADR in `supersedes`, the one exception to a replacement having none, and the kept ADR's pointer names the
  replacement. → `CAP-DOCS-document-model` §Decision supersession (MUST)

---

## 5. Consequences

- **Positive**: Bridging supersessions no longer force mega-ADRs; the integration ADRs can be compacted by topic.
- **Negative / Risks**: The fidelity review must check cross-group supersession explicitly: replaced clauses left out
  of one replacement and stated in another.
- **Follow-ups**: The `adr-compaction` playbook follows this rule.

---

## 6. Confirmation

- `RULE-decision-supersession` checks the remaining `supersedes` metadata and pointer lines.
- The playbook's fidelity review checks the replaced clauses. Otherwise review only.
