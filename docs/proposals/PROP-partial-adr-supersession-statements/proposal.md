---
id: PROP-partial-adr-supersession-statements
title: Structured partial-supersession statements for ADRs
summary: "Record each partial replacement once, as a fixed statement in the superseding ADR, let handoff copy it into the earlier ADR's pointer, let a rule keep both equal and let a devkit docs command list a decision's replacements, so earlier ADRs stay readable without manual pointer clarification."
status: reviewing
created_at: 2026-11-10
target_area: capabilities/documents/
priority: medium
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/decision_supersession/
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/decision_supersession.py
    - packages/devkit-docs/src/devkit_docs/features/documents/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/decisions/README.md
    - packages/devkit-docs/tests/
    - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py
    - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-consolidation/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/post-handoff.md
    - packages/devkit-spec/tests/
    - .devkit/architecture.toml
    - docs/capabilities/documents/CAP-DOCS-document-model.md
    - docs/capabilities/documents/CAP-DOCS-document-lookup.md
    - docs/capabilities/governance/CAP-GOV-spec-rules.md
    - docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    - docs/usecases/documents/UC-find-the-right-documents.md
    - docs/architecture/ARCH-05-2-components.md
    - docs/decisions/
    - docs/proposals/
  excludes:
    - packages/devkit/src/devkit_agt/features/rules/
    - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-partial-adr-supersession-statements] Structured partial-supersession statements for ADRs

## 1. Background & Hypothesis

A decision is never changed in place: a new ADR names the earlier one in `supersedes`. When only part of the earlier
ADR is replaced, the earlier ADR stays `accepted` with a "Superseded in part by `ADR-<new>`" line
(`SPEC-partial-adr-supersession`). Partial replacement is the common path: 18 of the 65 ADRs carry such a line, in 26
pairs, and none is wholly superseded.

Which clauses were replaced has no defined home:

- `devkit spec proposal handoff` fills the pointer with the new ADR's `summary`, which states the new decision, not
  the replaced clauses. Someone must rewrite it after handoff. Guidance gave that step to the Host
  (`FB-handoff-pointer-carries-summary-not-clauses`), the handoff docstrings still give it to Development
  (`FB-handoff-pointer-owner-docstring-mismatch`), and a summary pointer has already reached Development
  (`FB-partial-supersession-pointer-still-summary`, recurring). Six existing pointers still copy a summary.
- The superseding ADRs already describe their replaced scope, in free-form sentences ("This replaces <target> …",
  "Replaces in <target>: …") that no tool can extract.
- `adr-consolidation` reads the replaced scope from the earlier ADR's pointer, so consolidation depends on the
  manually clarified text.
- No command shows a decision's partial replacements; `devkit docs refs --direction in` mixes them with every other
  incoming reference.

A `spec`-depth attempt to flag summary-copy pointers with `RULE-decision-supersession` stopped on rule-engine
severity and the six existing copies; the user redirected the work to the ADR model
([attempt findings](materials/supersession-pointer-attempt.md)).

### Hypothesis

Partial supersession becomes reliable when the replaced scope is written once and everything else derives from it:

1. **Single source**: the superseding ADR carries one fixed statement per earlier ADR, written at PADR time by the
   author who knows the scope.
2. **Derived pointer**: handoff copies that statement into the earlier ADR's pointer instead of the summary, so the
   earlier ADR stays readable on its own and nobody rewrites the pointer after handoff.
3. **Checked consistency**: a rule checks that each partial superseder has a statement for each `supersedes` target
   that stays accepted, and that the earlier ADR's pointer repeats it.
4. **Queryable state**: a `devkit docs` command lists a decision's replacements from the statements.
5. **Deferred consolidation**: both ADRs stay as they are, linked, until a hygiene pass consolidates them;
   `adr-consolidation` reads the replaced scope from the statements.

## 2. Technical Spike Questions

Planning answered the six questions from repository evidence. `materials/planning-evidence.md` holds the inventory
and the option tables, `envelopes/scout-01.yaml` the command and viewer evidence. Where an envelope differs from this
document, this document holds.

- **Q1 Statement form**: a fixed sentence in Decision Outcome, one per earlier ADR: "Supersedes in part `ADR-<old>`:
  <the replaced clauses>." No frontmatter field is added. `SPEC-partial-adr-supersession` excluded a structured field
  to bound its scope and named no defect of one; the fixed sentence keeps what that spec kept (the status and a body
  line). Recorded in `PADR-partial-supersession-statements`.
- **Q2 Pointer derivation**: handoff copies the statement's text verbatim. The statement is the source: a later repair
  edits the statement and copies it to the pointer, and the rule reports a difference at the commit gate. No fixer is
  added.
- **Q3 Rule checks and severity**: every added check is an error of `RULE-decision-supersession`. `main` stays clean
  because the 26 pairs migrate in the same change. The handoff commit stays clean because handoff writes the pointer
  from the statement and refuses a missing statement before it writes.
- **Q4 Migration**: every pair on the Development head gets a statement and a pointer that repeats it (26 at
  `b3e4753d`); the six summary-copy pointers are replaced in the same change. Pointers at affected statements stay as
  they are. A pair whose existing sources name different clauses is never settled by the migration itself (3.6).
- **Q5 Command and viewer**: a sibling subcommand, `devkit docs supersession <ID>`, because `refs` is defined on the
  reference graph and a decision's `supersedes` is outside it. The viewer leaves this proposal:
  `PROP-viewer-decision-supersession` is its follow-up draft.
- **Q6 Owner**: no post-handoff clarification remains. The handoff docstrings, `CAP-DLV-proposal-planning` and the
  post-handoff reference state that the pointer repeats the statement and name no later rewrite.

## 3. Proposed Design & Impact

### 3.1 The statement and the pointer

- **Statement**: a list item or paragraph in the superseding ADR's Decision Outcome that begins
  "Supersedes in part `ADR-<old>`:". One statement per `supersedes` entry whose ADR is not `superseded`.
- **Pointer**: a list item or paragraph in the earlier ADR that begins "Superseded in part by `ADR-<new>`:". One
  pointer of the pair repeats the statement's text; handoff writes it below the heading.
- **Text**: what follows the colon, up to the next blank line, list item or heading. It is taken from the source
  lines, code spans and links included.
- **Locating**: a statement or pointer is found on visible lines only: code fences, comments, indented code and
  struck-out text are masked, as for the pointer today. The reader does not check which section holds a statement.
- **Equality**: two texts are equal when their source text matches after runs of whitespace are collapsed, so a
  re-wrapped paragraph stays equal and a difference inside a code span does not.
- A statement is an item or paragraph of its own. It carries no trace (`→ ...`), no source citation and no nested
  list, because the pointer repeats everything it holds; `decision-writing` already leaves the trace off a clause no
  document restates. It cites documents by full ID and holds no relative link, because the same text is read from a
  file in another directory.
- A pointer at an affected statement ("Superseded in part by `ADR-<new>`: the next item.") stays valid beside the
  repeating pointer and keeps its own text.
- The frontmatter is unchanged: `supersedes` lists the earlier ADRs, and the earlier ADR stays `accepted`.

Example pair:

```markdown
<!-- ADR-example-new, Decision Outcome -->
- Supersedes in part `ADR-example-old`: the retry policy clause; its timeout clauses remain.

<!-- ADR-example-old, below the heading -->
Superseded in part by `ADR-example-new`: the retry policy clause; its timeout clauses remain.
```

### 3.2 `RULE-decision-supersession`

The existing checks stay. The rule adds, as errors without a fixer:

1. **Missing statement**: an ADR or a PADR whose `supersedes` names an ADR that resolves and is not `superseded` has
   no statement naming it (by ID or alias). Reported at the `supersedes` field.
2. **Stray, duplicated or empty statement**: a statement names an ADR the document's `supersedes` does not list, a
   second statement names the same ADR, or a statement has no text. Reported at the statement's line.
3. **Pointer text**: an ADR's statement names an ADR that is not `superseded`, that ADR has at least one pointer
   naming the superseder, and none of them repeats the statement's text. Reported once per pair: at the earlier ADR's
   first pointer naming the superseder when the run targets that file, else at the statement's line. A run that
   targets only the earlier ADR finds the statement through the superseder each pointer names. An earlier ADR without
   any pointer naming the superseder stays the existing finding at `supersedes`, unchanged.

- A PADR is checked for 1 and 2 only: its pointer does not exist before handoff.
- A pair whose earlier ADR is `superseded` is not checked for 1 and 3; its statement and pointers may stay.
- The rule compares text. It does not interpret which clauses a statement covers.
- One reader of statements and pointers lives in `devkit_docs.features.documents` and serves the rule, the command
  and handoff. `devkit_docs.features.governance` and `devkit_spec.features.proposals` already depend on that feature,
  so no feature edge is added; `.devkit/architecture.toml` changes only by a `public_modules` entry when the reader is
  a module of its own.

### 3.3 Handoff and the PADR scaffold

- For each `supersedes` entry of a promoted PADR that resolves to one ADR whose status is not `superseded` and that
  has no visible pointer naming the promoted ADR, handoff writes "Superseded in part by `ADR-<new>`: <statement
  text>" as one paragraph below the earlier ADR's first heading. Placement, order, the `[SUPERSEDED_IN_PART: ...]`
  line and the JSON `pointers` are unchanged.
- When such an entry has no statement in the PADR, handoff refuses with `SPEC_PROPOSAL_INVALID` before its first
  write. The error names the PADR and the earlier ADR, and its fix is the statement to add.
- A composed handoff (`devkit spec proposal handoff --effort`) fails at its handoff step under its existing failure
  contract: the proposal and the worktree it created are kept. The repair adds the statement to the PADR on the base
  and reruns. The rule's PADR check makes this a backstop: the statement is normally demanded when the PADR is
  committed.
- The summary, title and slug fallbacks are removed.
- The scaffold's commented `supersedes` line names the statement form. Handoff keeps dropping the unchanged commented
  line, in the wording before and after this change.
- The handoff module docstring and the pointer helper's docstring state that the pointer repeats the statement.

### 3.4 `devkit docs supersession <ID>`

- ID is an ADR or a PADR, or an alias of one. Any other kind fails with `ARGUMENT_INVALID` (exit `2`).
- One `[SUPERSEDES: ...]` line per `supersedes` entry and one `[SUPERSEDED_BY: ...]` line per ADR that names ID in
  its `supersedes`, each in ID order:
  `[SUPERSEDES: <id> scope=<whole|partial> path=<path> status=<status> line=<n> text=<text>]`.
- `scope` is `whole` when the earlier ADR of the pair is `superseded` with `superseded_by` naming the later one, else
  `partial`. `line` and `text` are the statement's line and text in the later ADR, `-` when it has none.
- `--format json` prints one object with `id`, `supersedes`, `superseded_by` (records with `id`, `path`, `status`,
  `scope`, `line`, `text`) and `notices`. The command takes the common options of `CAP-DOCS-document-lookup` 3.1 and
  no paging.
- The command reads the files as the rule does. The document index and `devkit docs refs` are unchanged.

### 3.5 Guidance and playbook

- The decision template, the `decision-writing` instruction, the seeded `docs/decisions/README.md` and this
  repository's `docs/decisions/README.md` state the statement form and that the pointer repeats it.
- The rule guide lists the added findings, their repair and the example pair.
- `adr-consolidation`: Step 1 lists crossing pairs with `devkit docs supersession`; Step 2 treats the clauses a
  statement names as not in effect in the earlier ADR's replacement and carries a statement over as an item of its
  own without the source citation other Section 4 items end with; Step 3 keeps each statement and its pointer equal
  when a member's replacement takes over either side.
- The `spec-next` post-handoff reference loses its pointer clarification step and the mention of pointer
  clarifications in its opening paragraph.

### 3.6 Ledger migration

- Every pair on the Development head at its final verification gets one statement in the later ADR and one pointer
  below the earlier ADR's heading that repeats it. `materials/planning-evidence.md` section 4 lists the 26 pairs at
  `b3e4753d`; the base has since gained at least one more over `ADR-adaptive-development-and-research`
  (`materials/planning-evidence.md` section 4).
- The statement restates the later ADR's own description of the replaced scope in the fixed form:
  - several items about one earlier ADR are joined into one statement;
  - an item that names several earlier ADRs, or mixes a clause with the replaced scope, is split: the clause keeps
    its trace or source citation, and each statement becomes an item of its own.
- The migration settles no scope. A pair is flagged when its existing sources (the later ADR's Decision Outcome, the
  earlier ADR's pointer below the heading, and any other copy) name different clauses. A summary-copy pointer names
  no clauses and is no source. A flagged pair takes the scope the user decided; without that decision Development
  asks, and writes no statement for the pair by its own choice.
- One pair is flagged at `b3e4753d`: `ADR-skill-local-swarm-roles` over `ADR-adaptive-development-and-research`. Its
  Decision Outcome names "the role-set clauses"; its frontmatter key `supersedes_clause` and the earlier ADR's pointer
  name "role-set and role-authority clauses". Its scope is an open question of this Planning.
- The frontmatter key `supersedes_clause` of `ADR-skill-local-swarm-roles`, the only one in the ledger, is removed:
  the statement replaces it.
- The six summary-copy pointers and the pointer written with "for" take the statement's text.
- Pointers at affected statements are not edited.
- An open PADR on that head that names `supersedes` gets its statement as a restatement of its own Decision Outcome
  and no other edit, so the rule passes on `main`. None exists on the base at `f0434e6e`.
- `reconcile.md` holds one row per pair: the earlier sentences of the later ADR, the earlier pointer, the new
  statement, and whether the pair was flagged.

## Non-Goals

- **Scope Excluded**: the Living Spec viewer. `PROP-viewer-decision-supersession` owns it.
- **Scope Excluded**: the rules engine's severity model (`packages/devkit/src/devkit_agt/features/rules/`).
- **Scope Excluded**: a frontmatter field for the replaced scope, a new decision status, and reference-graph edges for
  a decision's `supersedes` in the document index or in `devkit docs refs`.
- **Scope Excluded**: a fixer for `RULE-decision-supersession`. When to Reconsider: when manual copies of a repaired
  statement are missed.
- **Scope Excluded**: changing any decision's meaning; migration edits wording and structure only.
- **Scope Excluded**: consolidating ADRs, and setting `status: superseded` or `superseded_by` in handoff.
- **Scope Excluded**: a setting that turns the added checks off, or a migration aid for other repositories beyond the
  rule guide's repair text. A repository defers the checks with the existing severity override for
  `RULE-decision-supersession`.
- **Scope Excluded**: refusing a missing statement at acceptance preparation; the rule's PADR check and the handoff
  refusal cover it.

## Acceptance Criteria

### [AC-01] The decision format states the statement

- **Given** the decision template, the `decision-writing` instruction, the seeded and the repository
  `docs/decisions/README.md` and a PADR written by `devkit spec proposal padr`,
- **When** a writer reads how to record a partial replacement,
- **Then** each names the sentence "Supersedes in part `ADR-<old>`: <the replaced clauses>." in Decision Outcome and
  states that the earlier ADR's pointer repeats its text; the PADR's commented `supersedes` line names the sentence;
  a guidance test asserts the template, the instruction and the scaffold.

### [AC-02] A missing statement is reported

- **Given** an ADR, and separately a PADR, whose `supersedes` names an accepted ADR and whose body has no statement
  naming it,
- **When** `devkit rules check` targets the document,
- **Then** `RULE-decision-supersession` reports one non-fixable error at the `supersedes` field naming the earlier ADR;
  it reports none when the statement exists, when it names the earlier ADR by an alias, or when the earlier ADR is
  `superseded`.

### [AC-03] A stray, duplicated or empty statement is reported

- **Given** an ADR whose statement names an ADR absent from its `supersedes`, an ADR with two statements naming the
  same ADR, and an ADR whose statement has no text after the colon,
- **When** `devkit rules check` targets each,
- **Then** `RULE-decision-supersession` reports one error at the statement's line in each case, and a statement
  inside a code fence, a comment or struck-out text is not read.
- **And** a statement followed in the same list by another item ends before that item.

### [AC-04] The pointer repeats the statement

- **Given** a pair whose earlier ADR is accepted and carries at least one pointer naming the superseder,
- **When** none of those pointers repeats the statement's text, including when the texts differ only inside a code
  span,
- **Then** `RULE-decision-supersession` reports one error for the pair, whether the run targets both files, only the
  earlier ADR or only the superseder;
- **And** it reports none when the texts differ only in whitespace or line wrapping, when the earlier ADR carries
  further pointers with other text beside the repeating one, or for a PADR;
- **And** when the earlier ADR carries no pointer naming the superseder, the rule reports the existing finding at
  `supersedes` and no pointer-text error.

### [AC-05] Handoff derives the pointer

- **Given** an accepted proposal whose PADR names an accepted ADR in `supersedes` and carries its statement, whose
  text holds a code span,
- **When** `devkit spec proposal handoff` runs,
- **Then** the earlier ADR gains one paragraph below its heading whose text equals the statement's source text, code
  span included, the result reports it as today (`[SUPERSEDED_IN_PART: ...]`, JSON `pointers`), and
  `devkit rules check` on the files the handoff wrote reports nothing from `RULE-decision-supersession`;
- **And** when the statement cites the proposal by its ID, the statement and the pointer are still equal after the
  handoff's reference rewrite;
- **And Given** the same PADR without the statement, **Then** the plain `devkit spec proposal handoff` fails with
  `SPEC_PROPOSAL_INVALID`, names the PADR and the earlier ADR, and writes nothing.

### [AC-06] The ledger follows the convention

- **Given** the Development head at its final verification,
- **When** `uv run devkit rules check` runs on the whole repository,
- **Then** it exits `0`, and every pair has one statement and one pointer below the earlier ADR's heading that
  repeats it; no pointer equals its superseder's `summary`, and no ADR carries `supersedes_clause`;
- **And** before it edits `docs/decisions/`, the Development worker runs the changed rule from its working tree and
  records that it reports at least one error for each pair present on that head;
- **And** in the ADR files under `docs/decisions/`, the diff against the Development base changes only statements,
  pointers below a heading, the sentences the statements were reworded from and the removed `supersedes_clause` key;
- **And** `reconcile.md` holds one row per pair with the earlier sentences, the earlier pointer and the new
  statement, and names every flagged pair with the decision its scope follows.

### [AC-07] `devkit docs supersession` lists both directions

- **Given** a fixture ledger with an ADR that supersedes one ADR in part and is itself superseded in part by another,
- **When** `devkit docs supersession <ID>` runs for it,
- **Then** it prints one `[SUPERSEDES: ...]` and one `[SUPERSEDED_BY: ...]` line with `scope=partial`, each
  statement's line and text, and exits `0`; `--format json` prints one object with the same records;
- **And** an alias argument names its document, a capability ID fails with `ARGUMENT_INVALID` and exit `2`, and an
  unknown ID fails with `DOCS_ID_UNRESOLVED` and exit `2`.

### [AC-08] Consolidation and post-handoff guidance follow the statements

- **Given** the `adr-consolidation` playbook, the `spec-next` post-handoff reference and `handoff.py`,
- **When** each is read,
- **Then** the playbook reads the replaced scope from the statements and names `devkit docs supersession`, the
  post-handoff reference names no pointer clarification, and no docstring in `handoff.py` says that Development or
  the Host rewrites the pointer; guidance tests assert the playbook and the reference.

### [AC-09] The Living Spec states the contract

- **Given** `target-docs.md`,
- **When** Development completes,
- **Then** `CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`, `CAP-GOV-spec-rules`, `CAP-DLV-proposal-planning`,
  `UC-find-the-right-documents` and `ARCH-05-2-components` state the behavior of AC-01 to AC-08, and
  `uv run devkit rules check` reports no violation.

## Planning decisions

| Subject | Decision | By |
| --- | --- | --- |
| Statement form (Q1) | A fixed Decision Outcome sentence per earlier ADR; no frontmatter field. Recorded in `PADR-partial-supersession-statements` | planning |
| Wording | "Supersedes in part `ADR-<old>`:" mirrors the pointer's "Superseded in part by" and the `supersedes` field, so one search finds both sides | planning |
| Pointer text (Q2) | The statement's text verbatim; equality after collapsing whitespace | planning |
| Consistency after handoff (Q2) | The rule reports a difference; the repair is a manual copy from the statement. No fixer | planning |
| Severity (Q3) | Every added check is an error of `RULE-decision-supersession`; the ledger migrates in the same change | evidence |
| PADR coverage (Q3) | The rule checks a PADR's statements, so a missing one is found when the PADR is committed, not at handoff | planning |
| Missing statement at handoff (Q3) | Refused before the first write with `SPEC_PROPOSAL_INVALID`; no summary fallback | planning |
| Migration (Q4) | All pairs in this change, the six summary copies included; text restated from the later ADR's own description | planning |
| Pairs whose sources differ | The migration settles no scope: a flagged pair follows the user's decision. The one known pair is an open question | planning |
| `supersedes_clause` | Removed from `ADR-skill-local-swarm-roles`: a frontmatter copy of the scope is the form `PADR-partial-supersession-statements` rejects | planning |
| Statement content | An item or paragraph of its own, without trace, source citation, nested list or relative link; text taken from the source lines | planning |
| Open PADRs of other units | `docs/proposals/` is owned only for the statement of an open PADR that names `supersedes` on the Development head; none exists on the base at `f0434e6e` | planning |
| Command (Q5) | `devkit docs supersession <ID>`, a sibling of `refs`; the index and `refs` are unchanged | planning |
| Viewer (Q5) | Out of this proposal: another package, capability and verification chain. `PROP-viewer-decision-supersession` is the follow-up draft | planning |
| Post-handoff clarification (Q6) | None remains; the step and the docstring sentences are removed | planning |
| Other repositories | No new setting: a repository that adopts the rule version repairs its pairs from the rule guide, or defers with the existing severity override for the rule | planning |
| Whole replacement through a PADR | Open question of this Planning. Drafted here as the recommended option: the PADR carries a statement naming every decision, handoff writes the pointer, the author then sets `superseded`, and the "in part" sentence stays in the ledger | planning |
| Supersession by this decision | `PADR-partial-supersession-statements` names no `supersedes`: it fixes the form of what `ADR-decision-ledger` already requires and leaves each of its clauses in force | planning |
| Size | `L`, one spec: the rule, the migration and the handoff change cannot land apart, and the command shares their reader | planning |
| `dev_effort` | Stays `medium`: the change is reversible in Git and releases nothing; the migration is checked by the rule and by review of a wording-only diff | planning |

## 4. Lifecycle & Retirement Criteria

On acceptance, handoff promotes `PADR-partial-supersession-statements` and starts Development. The handoff of this
proposal writes no pointer, because its PADR supersedes no ADR.

## 5. Source feedback

- `FB-partial-supersession-pointer-still-summary` (recurring): a summary pointer reached Development despite the
  guidance-only post-handoff clarification. Received in full: the derived pointer and the pointer-text check.
- `FB-handoff-pointer-owner-docstring-mismatch`: the handoff docstrings and the post-handoff reference name different
  owners for the pointer clarification. Received in full: both lose the clarification (Q6).
