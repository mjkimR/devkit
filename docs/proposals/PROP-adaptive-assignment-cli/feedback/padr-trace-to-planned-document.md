---
id: FB-padr-trace-to-planned-document
title: A PADR cannot write the required trace to a document its proposal creates
scope: repo
kind: friction
category: instruction-conflict
target: the decision-writing instruction (Decision Outcome Clauses) and RULE-document-reference
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-padr-trace-to-planned-document] A PADR cannot write the required trace to a document its proposal creates

## 1. Friction / Question (friction, question)

- **Context**: Planning of a proposal whose Development creates a capability. Two PADRs record decisions that the
  planned capability will restate.
- **Expectation**: `decision-writing` says a clause that a capability restates ends with its trace: "the backticked
  ID, the section or rule that holds it and the keyword that document uses".
- **Actual**: `devkit rules check` reports `RULE-document-reference` ("no document has the ID ...") for every
  backticked mention of the planned capability ID in the PADRs, `proposal.md` and `target-docs.md`, 14 findings in
  all. The capability does not exist until Development writes it.
- **Workaround (or Interpretation Chosen)**: The planned ID is written without backticks in the four files, with one
  sentence in the proposal telling Development to backtick it in the promoted decisions once the document exists.
- **Suggestion**: State the form in `decision-writing` and the proposal guidance for a document the proposal plans
  (for example the unquoted ID followed by "(planned)"), or let `RULE-document-reference` accept an ID that the
  proposal's `target-docs.md` lists under `targets` as a file to create.

## Diagnostic Details

- **Reproduction**: Write `` `CAP-<AREA>-<new-slug>` `` in a PADR of a `reviewing` proposal and run
  `uv run devkit rules check <PADR path>`.
- **Expected / Actual**: Expected a way to trace to the planned document; got `RULE-document-reference` errors.
- **Versions**: Worktree at `0b1b9c9e`.
- **Conditions**: Proposal Planning, before the target document exists.
- **Workarounds Attempted**: Removing the backticks clears the findings.
- **Related Assets**: `.devkit/managed/docs/instructions/decision-writing.md`,
  `.devkit/managed/docs/rules/document_reference/guide.md`.

## Evidence

```text
[VIOLATION: RULE-document-reference severity=error file=<proposal>/decisions/PADR-<slug>.md line=53 status=open
 message="no document has the ID CAP-DLV-adaptive-assignments" remediation="Create the intended document or correct
 the exact ID"]
[SUMMARY: errors=14 warnings=0 infos=0 fixed=0 rules=22]
```
