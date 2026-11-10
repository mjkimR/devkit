---
id: PADR-partial-supersession-statements
title: Fixed partial-supersession statement in the superseding ADR
summary: "For partial ADR replacement, we state the replaced clauses once as a fixed Decision Outcome sentence per earlier ADR and repeat that text in the earlier ADR's pointer, to keep both readable and checkable without post-handoff rewrites, accepting two copies a rule keeps equal."
proposal: PROP-partial-adr-supersession-statements
# supersedes: [ADR-<slug>]   # an ADR this decision replaces, wholly or in part; name the replaced clauses in Decision Outcome
status: draft
created_at: 2026-11-10
---

# [PADR-partial-supersession-statements] Fixed partial-supersession statement in the superseding ADR

- **Status**: Draft
- **Date**: 2026-11-10
- **Involved Components/Capabilities**: `docs/decisions/`, `capabilities/documents/`, `capabilities/governance/`,
  `capabilities/delivery/`, the `adr-consolidation` playbook

---

## 1. Context & Problem Statement

A later ADR that replaces part of an earlier one names it in `supersedes`, and the earlier ADR stays `accepted` with
a "Superseded in part by `ADR-<new>`" pointer (`ADR-decision-ledger`, `CAP-DOCS-document-model`). Which clauses were
replaced has no fixed form:

- The later ADR states the replaced scope in free prose. The 26 existing pairs use at least five wordings, so no tool
  can read it.
- `devkit spec proposal handoff` therefore fills the pointer with the later ADR's `summary`, which states the new
  decision. A person has to rewrite it; six pointers still repeat a summary, and the rewrite has been applied to the
  wrong file.
- `RULE-decision-supersession` checks that the pointer and `supersedes` name each other. It cannot check what the
  pointer says.
- The `adr-consolidation` playbook reads the replaced scope from the earlier ADR's pointer, so it depends on the
  rewritten text.

`SPEC-partial-adr-supersession` excluded a structured field to bound its scope; it kept "the status and a body line".
`materials/planning-evidence.md` in the proposal holds the inventory and the option comparison.

## 2. Decision Drivers

- The replaced scope is written once, by the author of the later decision.
- The earlier ADR says what was replaced without opening the later one.
- A rule and the handoff read the scope with the reader they already have.
- IDs in the text stay under `RULE-document-reference` and alias rewrites.
- Agents write the text without YAML quoting of long prose.
- The 26 existing pairs migrate by wording edits only.

## 3. Considered Options

### Option 1: A fixed sentence per earlier ADR in Decision Outcome (Selected)

- **Overview**: the later ADR carries one list item or paragraph per earlier ADR: "Supersedes in part `ADR-<old>`:
  <the replaced clauses>." The earlier ADR's pointer repeats the same text.
- **Pros**: mirrors the pointer, so one reader serves both; the text stays Markdown under the reference rules; all 26
  pairs already state the scope in Decision Outcome; no new frontmatter field or status.
- **Cons**: the scope exists in two files, and a rule has to keep the copies equal; a tool has to read the body.

### Option 2: A frontmatter map from each earlier ADR to its replaced clauses

- **Overview**: `supersedes` gains a companion key holding one string per earlier ADR.
- **Pros**: readable from frontmatter alone; no body convention.
- **Cons**: 60 to 400 characters of prose with backticks, quotes and colons inside YAML strings; IDs in the string are
  outside reference checks and alias rewrites; Decision Outcome either repeats the scope or loses it; it adds the
  structured field `SPEC-partial-adr-supersession` excluded.

### Option 3: A fixed subsection of Decision Outcome with one list item per earlier ADR

- **Overview**: a heading such as "Replaced clauses" holds the items.
- **Pros**: the items are easy to find.
- **Cons**: a heading no existing ADR has, heading detection in the reader and a larger migration, for the same
  information as Option 1.

### Option 4: Keep free prose and clarify the pointer after handoff

- **Overview**: the current state, with the Host rewriting each pointer.
- **Pros**: no change.
- **Cons**: the rewrite depends on guidance that has failed repeatedly, and no rule can check it.

## 4. Decision Outcome

We adopt **Option 1**.

- A decision that replaces part of an ADR states the replaced scope in a partial-supersession statement: a list item
  or paragraph of its Decision Outcome that begins "Supersedes in part `ADR-<old>`:" and runs to the end of that item
  or paragraph. It writes one statement per earlier ADR its `supersedes` names that is not `superseded`. →
  `CAP-DOCS-document-model` Decision supersession (MUST)
- The earlier ADR's pointer "Superseded in part by `ADR-<new>`:" repeats the statement's text. The statement is the
  source: a repair changes the statement and copies it to the pointer. Further pointers at the affected statements
  keep their own text. → `CAP-DOCS-document-model` Decision supersession (MUST)
- `devkit spec proposal handoff` writes the pointer from the promoted decision's statement and refuses, before any
  write, a `supersedes` entry that needs a pointer and has no statement. Nobody rewrites the pointer after handoff. →
  `CAP-DLV-proposal-planning` 4.5 step 4 (MUST)
- `RULE-decision-supersession` reports a missing, duplicated, stray or empty statement in an ADR or a PADR, and an
  earlier ADR without a pointer that repeats the statement. The rule stays report-only: it compares text and never
  interprets which clauses a statement covers. → `CAP-GOV-spec-rules` 3.17 (MUST)
- A PADR is checked for its statements because its author knows the replaced scope; its pointer does not exist before
  handoff and is not checked.
- The frontmatter stays as it is: `supersedes` lists the earlier ADRs, an ADR replaced in part stays `accepted`, and
  the document index adds no edge for a decision's `supersedes`.
- Option 1 satisfies the single-source, readable-earlier-ADR and existing-reader drivers. Option 2 fails the reference
  and YAML drivers, Option 3 adds structure without information, and Option 4 keeps the failure.

## 5. Consequences

- **Positive**: the pointer is correct at the handoff commit; consolidation and the `devkit docs supersession` command
  read the replaced scope from the statements; a summary cannot reach a pointer unnoticed.
- **Negative / Risks**:
  - The replaced scope exists in two files. The rule reports a difference at the commit gate, and the repair is a
    manual copy.
  - A repository that adopts this rule version with partly superseding ADRs gets errors until each has its statement
    and matching pointer; the rule guide states the repair.
  - A decision meant to replace a whole ADR through a PADR still passes through the partial form: its statement names
    every decision, handoff writes the pointer, and the author's edit then sets `status: superseded` and
    `superseded_by`.
- **Follow-ups**:
  - A fixer that copies the statement into the pointer, when manual copies are missed or become frequent.
  - The frontmatter form of Option 2, when a consumer has to read the replaced scope without reading the body.

## 6. Confirmation

- `RULE-decision-supersession` and its tests in
  `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/decision_supersession/tests/test_rule.py`.
- Handoff tests for the derived pointer and the refusal in `packages/devkit-spec/tests/`.
- `uv run devkit rules check` exits `0` on the migrated ledger.
- Review of the diff for whether a statement names the right clauses.
