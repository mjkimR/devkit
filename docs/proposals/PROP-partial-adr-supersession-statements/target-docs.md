---
id: PROP-partial-adr-supersession-statements-target
title: Target Living Spec Structure for PROP-partial-adr-supersession-statements
status: draft
proposal: PROP-partial-adr-supersession-statements
created_at: 2026-11-10
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
  - file: docs/usecases/documents/UC-find-the-right-documents.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/decisions/README.md
---

# [Blueprint] PROP-partial-adr-supersession-statements: Target Living Spec Structure for Structured partial-supersession statements for ADRs

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-partial-adr-supersession-statements is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets.

---

## 1. System Capabilities Plan (docs/capabilities/)

- `CAP-DOCS-document-model`, "Decision supersession":
  - The sentence "names it in `supersedes` and states the replaced clauses in its outcome" becomes a rule: a later
    ADR that replaces only part of an earlier one MUST carry, per such earlier ADR, one partial-supersession statement
    in its Decision Outcome, a list item or paragraph of its own that begins "Supersedes in part `ADR-<old>`:" and
    whose text runs to the next blank line, list item or heading. A statement SHOULD hold no trace, source citation
    or nested list.
  - A whole replacement gains no form of its own: a decision that replaces all in-force decisions of an earlier ADR
    MUST carry the same statement, naming every decision, while that ADR is not `superseded`. After the author sets
    `status: superseded` and `superseded_by`, the statement and its pointer MAY stay as written.
  - The pointer sentence gains: one pointer of the earlier ADR naming the superseder MUST repeat the statement's text
    (source text, code spans included, equal after runs of whitespace are collapsed); the statement is the source, and a pointer at an affected
    statement MAY carry other text beside it.
  - The rule paragraph: `RULE-decision-supersession` also MUST report a missing, stray, duplicated or empty statement
    and an earlier ADR without a pointer that repeats the statement. "excludes materials and PADRs" becomes: it
    excludes materials and checks a PADR for its statements only.
  - "neither rule interprets decision meaning" stays. The index sentence stays: a decision's `supersedes` and
    `superseded_by` add no reference-graph edge. It gains that `devkit docs supersession` reads them
    (`CAP-DOCS-document-lookup`).
  - The consolidation paragraph gains that a replacement keeps each statement and the pointer that repeats it equal.
  - The decision cited is the ADR promoted from `PADR-partial-supersession-statements`, beside `ADR-decision-ledger`.
- `CAP-DOCS-document-lookup`:
  - Summary, section 1 and section 2 name four commands: `resolve`, `refs`, `list` and `supersession`.
  - A section "`devkit docs supersession ID`" after 3.3, with these rules:
    1. ID is an ADR or a PADR, or an alias of one; another kind fails with `ARGUMENT_INVALID`.
    2. One `[SUPERSEDES: ...]` line per `supersedes` entry of the document, then one `[SUPERSEDED_BY: ...]` line per
       ADR whose `supersedes` names it, each group in ID order.
    3. `scope=whole` when the earlier ADR of the pair is `superseded` with `superseded_by` naming the later one, else
       `scope=partial`.
    4. `line` and `text` are the line and text of the later ADR's statement for the pair, `-` when it has none.
    5. `path=-` and `status=-` mark an entry no single document declares.
    6. The command has no paging and does not change `refs`: a decision's `supersedes` stays outside the reference
       graph.
  - 4.1 gains a `devkit docs supersession <ID>` line. 4.2 gains
    `[SUPERSEDES: <id> scope= path= status= line= text=]` and `[SUPERSEDED_BY: <id> scope= path= status= line= text=]`.
    4.3 gains the row `supersession`: `id`, `supersedes`, `superseded_by` (records with `id`, `path`, `status`,
    `scope`, `line`, `text`), `notices`. 4.5 gains the `ARGUMENT_INVALID` condition.
- `CAP-GOV-spec-rules`:
  - The rule table row of `RULE-decision-supersession` reads: status, metadata resolution, reciprocal partial pointers
    and partial-supersession statements agree; historical ADRs checked, materials excluded, PADRs checked for
    statements only.
  - Section 3.17 gains three rules: missing statement (at the `supersedes` field), stray, duplicated or empty
    statement (at the statement's line), and pointer text (once per pair that has a pointer naming the superseder,
    at the earlier ADR's first such pointer when targeted, else at the statement's line). Each is a non-fixable
    error. A pair whose earlier ADR is `superseded` is exempt from the first and third, and a pair without any
    pointer keeps the existing replacement-target finding.
- `CAP-DLV-proposal-planning`:
  - 4.4: the PADR's commented `supersedes` line names the statement to write in Decision Outcome.
  - 4.5 step 4: `<clause>` is the text of the promoted decision's statement for that ADR. The sentence that
    Development replaces it at `living-spec-draft` is removed. A `supersedes` entry that needs a pointer and has no
    statement in the PADR MUST be refused with `SPEC_PROPOSAL_INVALID` before the first write; a composed handoff
    fails at its handoff step under its existing failure contract. The remaining
    sentences (placement, order, no second pointer, the sentinel, no `status: superseded`) stay: a PADR that replaces
    a whole ADR gets the same pointer, and the whole supersession stays the author's edit.
  - The error table row of `SPEC_PROPOSAL_INVALID` gains the condition.

No sentinel, JSON key or code of an existing command changes; `devkit docs supersession` adds two sentinels and one
JSON shape.

---

## 2. Use Cases Plan (docs/usecases/)

- `UC-find-the-right-documents`:
  - Scope names `supersession` beside `resolve`, `refs`, `list` and `search`.
  - A new extension of step 3: the document is a decision and the agent needs what it replaced or what replaced it;
    the agent asks for the decision's supersession; the system lists each earlier and each later decision with
    `whole` or `partial` and the replaced scope; resumes at step 5 (`CAP-DOCS-document-lookup`).
  - A new scenario covering that extension: Given an ADR that is superseded in part, When the agent runs
    `devkit docs supersession <ID>`, Then it receives one `[SUPERSEDED_BY: ...]` line with `scope=partial` and the
    statement's text, and exits `0`.

No screen changes: the viewer is `PROP-viewer-decision-supersession`'s.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-2-components`: the commands of `devkit_docs.features.documents` gain `docs supersession`. No layer,
  package or feature edge changes.
- `PADR-partial-supersession-statements` becomes an ADR at handoff. It names no `supersedes`.
- `docs/decisions/README.md`: the opening paragraph and the schema comments name the statement and that the pointer
  repeats it.
- `docs/decisions/` (not listed under `targets`, because the files are found at Development time): each pair on the
  Development head at its final verification (27 at `c84a5485`, `materials/planning-evidence.md` section 4) gets its
  statement and its repeating pointer, as section 3.6 of the proposal describes. No status, `supersedes` or
  `superseded_by` value changes; the `supersedes_clause` key of `ADR-skill-local-swarm-roles` is removed.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- Docs bundle: the decision template, the `decision-writing` instruction ("Supersession"), the seeded
  `docs/decisions/README.md` and the `RULE-decision-supersession` guide state the statement, the repeating pointer
  and the added findings.
- Spec bundle: the `adr-consolidation` playbook reads statements and names `devkit docs supersession`; the
  `spec-next` post-handoff reference loses the pointer clarification.
- `.devkit/architecture.toml`: at most one `public_modules` entry, when the shared reader of statements and pointers
  is a module of its own. No `feature_dependencies` entry changes.
- `devkit sync` output for the selected `docs` and `spec` bundles follows the bundle edits.

---

## 5. System Before & After Comparison (Before & After)

| Aspect | Before | After |
| --- | --- | --- |
| Replaced scope in the later ADR | Free prose in Decision Outcome | One fixed statement per earlier ADR |
| Pointer text at handoff | The later ADR's `summary` | The statement's text |
| Post-handoff step | The Host clarifies each pointer by hand | None |
| `RULE-decision-supersession` | Pointer and `supersedes` name each other | Also: the statement exists and one pointer repeats it |
| PADRs in the rule | Excluded | Checked for statements |
| Handoff without a replaced scope | Writes the summary | Refuses before writing |
| Pointers that repeat a summary | 6 of 27 | 0 |
| Whole replacement through a PADR | A pointer holding the summary; the author sets `superseded` | The same statement, naming every decision, and its pointer; the author sets `superseded` |
| Listing a decision's replacements | `devkit docs refs --direction in`, mixed with every body reference | `devkit docs supersession <ID>` |
| Frontmatter, statuses, reference graph | `supersedes`, `accepted`, no decision edges | Unchanged |
| Viewer | No supersession display | Unchanged; `PROP-viewer-decision-supersession` |
