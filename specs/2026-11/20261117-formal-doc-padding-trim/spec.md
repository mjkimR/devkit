---
id: SPEC-formal-doc-padding-trim
title: Trim padding from formal document guidance and documents
summary: Remove guidance and template elements that duplicate rules, frontmatter or other owners, narrow the Maintenance section to update triggers, and apply the same standard to the existing design, domain and operations documents.
status: completed
created: 2026-11-17
related_capabilities: [CAP-DOCS-documentation-ownership, CAP-DLV-proposal-lifecycle, CAP-DIST-sync-and-transactions]
related_usecases: []
workflow: sdd-spec-feature
---
# [SPEC-formal-doc-padding-trim] Trim padding from formal document guidance and documents

## 1. Problem Statement & Motivation

Handed off from proposal PROP-formal-doc-padding-trim on 2026-11-17.
- **Preserved Materials**: `docs/materials/2026-11/20261117-formal-doc-padding-trim`

### 1. Background & Hypothesis

Two read-only audits of the formal documentation, one of the authoring assets and one of the 13 existing design,
domain and operations documents (1,063 lines), found that most padding in the documents is induced by the
templates and writing instructions:

- `## Authority boundary` requires a stock disclaimer ("transfers no normative statement", "routes and owns no
  recovery") that is true of every document of the kind, and documents fill it by re-listing the owners already in
  their domain or operations table.
- `## Maintenance and next action` mixes the one fact nothing else holds (which source change makes the document
  stale) with "next read" pointers that repeat frontmatter `related_*` and the authority boundary; the broad name
  also attracts misplaced body content (`OPS-distribution-sync` keeps a `RECOVERY_BLOCKED` routing rule there, two
  DOMAIN documents keep their per-question owner lines there).
- The design, domain and operations writing instructions repeat path, ID and frontmatter steps that
  `RULE-spec-format`, `RULE-id-convention` and `RULE-code-entrypoints` already enforce, and copy about six identical
  steps across the three files that `living-spec-writing.md` and `CAP-DOCS-documentation-ownership` §3.3 state again.
- `CAP-DOCS-documentation-ownership` has two overlapping routing tables (§3.1 rules 5 and 7) plus a prose copy in
  `living-spec-writing.md`, and §4 restates the template layout, so every template edit forces a capability edit.
- Smaller items: an unused capability template §4 scaffold (0 of 59 capabilities use it), a capability Summary comment
  that asks to repeat the frontmatter `summary`, a YAML-parser install note in `document-writing.md` that the advisory
  already carries, several "the selected development approach defines …" sentences that give no action, the lead and
  datasheet rules restated in template and instruction, a domain worked example that the template calls optional and
  the instruction requires, file-path comments restating `RULE-id-convention`, and `---` separators in the use case and
  UX templates.

In the documents, about 130–150 lines (13%) are padding beyond the Maintenance sections: generic authority
boundaries, repeated "non-normative" and "example executes nothing" disclaimers, lead paragraphs ending in a "This
entry …" restatement of the summary, prose duplicating a table in the same document, a capability table re-stated in
`DESIGN-proposal-handoff`, about 20 private helper names that churn, and DESIGN-distribution-transactions, which is
almost entirely a wrapper around `DESIGN-distribution-file-directory-replacement`.

Hypothesis: removing the elements that induce padding, then applying the same standard once to the existing
documents, makes formal documents shorter to write and read without losing any fact a reader acts on.

Checked and kept: use case sections (parsed by rules), operations "Normal-state observation", the problem-first lead,
the domain relationship table, the reference template, ADR drivers and confirmation.

## 2. User Stories

- **US-1**: As an agent writing a design, domain or operations document, I want templates and writing instructions
  that ask only for facts no other owner holds, so that a new document carries no stock disclaimer or repeated
  owner list.
- **US-2**: As a reader of an existing formal document, I want its closing to name only the limits the body does not
  state and the source changes that make it stale, so that every closing line changes what I do next.
- **US-3**: As an agent routing a fact to its owner, I want one fact-type table in `CAP-DOCS-documentation-ownership`
  and `living-spec-writing`, so that I consult one table instead of two overlapping ones.
- **US-4**: As an agent reading `CAP-DLV-proposal-lifecycle` before a handoff, I want the capability to state outcomes
  and `DESIGN-proposal-handoff` to state order and passes, so that each fact has one owner.

## 3. Non-Goals

1. **Scope Excluded**: the ADR template and `decision-writing` (`decision-writing.md` line 19 stays); they belong to
   the sibling proposal on ADR body metadata.
2. **Scope Excluded**: `CAP-DLV-proposal-lifecycle` §4.1 step 4 (PADR promotion) and the
   `DESIGN-proposal-handoff` worked-example row on ADR promotion; the sibling proposal rewrites both.
3. **Scope Excluded**: other capability, use case, UX and architecture documents, except the one reference repair in
   `CAP-DIST-sync-and-transactions`.
4. **Scope Excluded**: any rule or check change; no rule checks closing sections (`ADR-formal-document-closings` §5).
5. **Scope Excluded**: completed specs, reconcile records and materials that name the folded design; they keep the
   old ID, which resolves through the successor's `aliases`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Formal templates close with the narrowed sections
- **Given** the docs bundle templates `design.md`, `domain.md` and `operations.md`
- **When** `rg -n "Maintenance and next action|transfers no normative|owns no recovery|Optional: a nonexecuted" <the three templates>` runs
- **Then** it exits `1`; each template ends with `## Update triggers`, the domain and operations templates mark
  `## Authority boundary` as omitted when nothing remains, and `domain.md` requires the worked example in the
  overview or its own section.

### [AC-02] Per-kind writing instructions keep only kind-specific steps
- **Given** `design-writing.md`, `domain-writing.md` and `operations-writing.md`
- **When** `rg -n "Supply nonempty string|first H1|Omit proposal|Omit area|Omit entrypoints|Delete every template HTML comment|settle the one reader question" <the three instructions>` runs
- **Then** it exits `1`; each instruction keeps one path line, its lead focus, its body sections, its closing per
  `ADR-formal-document-closings` and its support location, and its first step points to `living-spec-writing`.
- **And** `living-spec-writing` "Responsibility and design navigation" states the shared steps once (one reader
  question, the lead with at most one question sentence, related_* lists without reciprocity, rename/split/retire,
  and a same-kind fold that deletes the folded document and keeps its ID as an alias of the receiving one), and
  `document-writing` states the delete-template-comments step.

### [AC-03] One fact-type routing table
- **Given** `CAP-DOCS-documentation-ownership` §3.1 and `living-spec-writing`
- **When** `uv run pytest packages/devkit-spec/tests/integration/bundles/spec/test_formal_doc_checkpoints_guidance.py` runs
- **Then** it exits `0`, asserting that each holds exactly one `| Fact type | Owner |` table of 15 rows, that both
  tables are equal, and that the first row reads "Behavior, validity, safety, limit, output order or tie-break a
  consumer can observe"; `rg -c "^\| Responsibility / reader question" docs/capabilities/documents/CAP-DOCS-documentation-ownership.md` exits `1`.

### [AC-04] Shared templates and instructions lose inactive elements
- **Given** the docs bundle sources
- **When** `rg -n "selected development approach defines|File path is|YAML_BINDING_UNAVAILABLE" packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions` runs
- **Then** it reports only `templates/decision.md` and `instructions/decision-writing.md`, which Non-Goal 1 leaves
  to the sibling proposal; `templates/usecase.md` and `templates/ux.md` hold no body `---`
  separator; `templates/capability.md` keeps the `## 1. Summary` and `## 4. Interfaces & Data Contracts` headings
  without the Summary comment or the §4 scaffold; the docs and spec bundle guidance tests pass.

### [AC-05] CAP-DOCS-documentation-ownership states the new section contract
- **Given** `CAP-DOCS-documentation-ownership`
- **When** a reviewer reads §3.2, §3.3 and §4
- **Then** §3.3 rule 2 states the closings of `ADR-formal-document-closings` with that ADR cited; the §3.2 closing
  paragraph and the §3.3 "This migration transfers..." sentence are gone; §4 names the templates and writing
  instructions without restating the template layout; rule 8 cites the renumbered fact-type rule.

### [AC-06] The existing documents follow the standard
- **Given** the 12 remaining design, domain and operations documents
- **When** `rg -n "^## Maintenance and next action|non-normative|transfers no normative|settles no rule|owns no recovery|nonexecuted example|^Next read" docs/designs docs/domain docs/operations` runs
- **Then** it exits `1`; `rg -c "^## Update triggers$" docs/designs docs/domain docs/operations` counts one per
  document (12); ``rg -n "`_[A-Za-z]" docs/designs`` exits `1`; `DOMAIN-bundle-selection-and-installation` and
  `DOMAIN-delivery-relationships` carry `related_capabilities`, the former also `related_designs`; and
  `uv run devkit rules check docs/designs docs/domain docs/operations` reports no violation.

### [AC-07] DESIGN-distribution-transactions is folded into its detail
- **Given** the folded design
- **When** `uv run devkit docs resolve DESIGN-distribution-transactions` runs
- **Then** it exits `0` naming `DESIGN-distribution-file-directory-replacement`, whose `aliases` lists the old ID;
  the old bundle directory is absent; `CAP-DIST-sync-and-transactions` cites the successor;
  `specs/2026-11/20261116-design-bundle-layout/feedback/viewer-adopts-bundle-grammar.md` names the successor once; and
  the viewer `FormalReading.test.ts` reads the capability, the detail, two domains and the operations document as
  five chapters and follows capability → detail → capability.

### [AC-08] The handoff mechanism moves from the capability to the design
- **Given** `CAP-DLV-proposal-lifecycle` §4.1 step 5 and §4.3
- **When** `rg -n "preflight pass|followed back|before ordinary relocation|extract_links|relocate_links" docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md` runs
- **Then** it exits `1`; the capability keeps the outcome sentences Q8 lists (refused before its first write, a
  created directory removed when empty, each changed file replaced atomically, the merge bullets, the
  dropped-record citation condition and `unmapped`); `DESIGN-proposal-handoff` states the preflight pass, the
  rollback walk, the pass order and the link library and cites `CAP-DLV-proposal-lifecycle` §4.2 for the body
  classification instead of restating it; `FB-proposal-lifecycle-capability-holds-mechanism-detail` is `resolved`
  with a Disposition naming this spec.

### [AC-09] Verification passes
- **Given** the final Development head
- **When** `just lint-check`, `uv run devkit generated check`, `uv run devkit rules check --ci --base main`,
  `just test-affected --base main` and the viewer frontend check run
- **Then** each exits `0`, and `uv run devkit sync --check` exits `0` after the committed sync output.

## 5. Source feedback

- `FB-proposal-lifecycle-capability-holds-mechanism-detail` (direct fix, user-authorized scope extension): review
  `CAP-DLV-proposal-lifecycle` §4.1 step 5 and §4.3 against `CAP-DOCS-documentation-ownership` §3.1, move pure
  mechanism explanation into `DESIGN-proposal-handoff` and keep every observable guarantee in the capability (Q8).
  The source resolves at this unit's completion when the move lands and verification passes.

## 6. Planning decisions

Each answer is a Planning decision and binds Development; `ADR-formal-document-closings` records Q1, Q2 and the shared-step part of Q4.

- **Q1**: What does the narrowed section say? Rename `## Maintenance and next action` to `## Maintenance` (or
  `## Update triggers`) holding only the source change that makes the document stale, naming public entry points or
  codes; keep a "next read" only when frontmatter and the authority boundary lack it, or drop it?
  - **Answer**: rename it `## Update triggers` in all three kinds and keep only the source changes that make the
    document stale, named by public entry point, use case, field, code or capability section, plus a command that
    rechecks a worked example when the document has one. Drop "next read" as a section role, but keep every route
    it holds: each document ID or skill a removed sentence names stays in the body or in `related_*`. Concretely,
    the `spec-next` post-handoff check in `DESIGN-proposal-handoff` moves into its rewriting phase; the
    `devkit playbook search` pointer of `OPS-search-mode-and-model-routing` moves into its no-row fallback; the two
    DOMAIN documents without `related_*` (`DOMAIN-bundle-selection-and-installation`,
    `DOMAIN-delivery-relationships`) gain `related_capabilities` and, for the bundle chain, `related_designs`. The
    operations fallback for evidence that matches no row moves under `## Routing`, below the table, because it is
    routing; where it repeats a row (`OPS-distribution-sync` lines 45-48 against 23-25) it merges into that row.
    "Update triggers" names the one fact the section holds; "Maintenance" is broad enough to keep attracting body
    content (the `OPS-distribution-sync` `RECOVERY_BLOCKED` rule, the DOMAIN owner-per-question lines).
- **Q2**: What does `## Authority boundary` keep? Proposal: only what the evidence or document cannot conclude beyond
  its table (domain, operations) or what the design does not settle (design), with no stock disclaimer.
  - **Answer**: as proposed. Design keeps the section (it has no owner table): the rules it explains and their owners
    by full ID, even when the body cites them inline. Domain and operations keep owners neither the table nor the
    body names and what the document or evidence cannot conclude; they omit the section when nothing remains. The
    DOMAIN owner-per-question lines (`DOMAIN-delivery-relationships` 52-54, `DOMAIN-bundle-selection-and-installation`
    52-55) therefore go, since the table and body already name every owner they list. No document states that it transfers no normative
    statement or owns no recovery: `CAP-DOCS-documentation-ownership` §3.1 and §3.3 already say so for every
    document of the kind.
- **Q3**: Merge the two `CAP-DOCS-documentation-ownership` routing tables into one fact-type table and keep the
  equality test on that single table; which rows move?
  - **Answer**: one `Fact type | Owner` table of 15 rows under one rule, in both the capability and
    `living-spec-writing`, whose prose copy (lines 25-27) goes. The nine fact-type rows stay, with the first row
    widened to "Behavior, validity, safety, limit, output order or tie-break a consumer can observe", the
    internal-order row to "Local mechanism, internal processing order, algorithm, pseudocode or worked example", the
    domain row to "Concept meaning, identity, relationships and lifecycle", the ADR row to "Enduring choice,
    rationale and rejected options", the materials row to "Measurement, experiment or assumption" and the syntax row
    to "Command, flag, API, configuration key or payload field syntax". Six
    responsibility rows move in: actor goal, scenario and success contract (use case); human interface element and
    interaction (UX); system structure, interactions, deployment and architectural constraints (architecture);
    symptom and evidence routed to an existing action owner and normal-state observation (operations); executable
    recovery steps and permissions (the existing instruction, playbook, advisory or executable owner); contributor
    development activity (development guide). The responsibility row "exact command/API/config syntax or error
    mapping" is covered by the code and syntax rows. Rule 8's "rule 7" citation follows the renumbering, and the
    `| Fact type |` header stays, so the consumers that cite the table by name (`spec-plan`, `spec-review`,
    `reconcile-reviewer`, `capability-writing`) are unaffected. The test keeps the equality assertion and pins 15 rows
    and the new first row.
- **Q4**: How far do the per-kind writing instructions shrink: path line, lead focus, body sections, closing, and a
  pointer to `living-spec-writing` plus `devkit rules check` for the shared steps?
  - **Answer**: to those five items. Each keeps one path line (the agent needs it before the first check), the
    kind's lead focus, its body sections (design: topic headings and the datasheet condition with its field list;
    domain: the relationship table and the example; operations: the routing table, the no-row fallback and the
    normal-state observation), its closing per Q1/Q2, and the kind-specific support location. Steps that
    `RULE-spec-format`, `RULE-id-convention` or `RULE-code-entrypoints` enforce go (frontmatter fields, H1 shape,
    forbidden fields, entrypoint liveness, `area`). Steps shared by the three move once to
    `living-spec-writing` "Responsibility and design navigation": settle one reader question, the lead with at most one
    question sentence, related_* lists without reciprocity, rename/split/retire, and a same-kind fold that deletes
    the folded document and keeps its ID as an alias of the receiving one. Each kind's first step points to
    `living-spec-writing` unconditionally, since it now holds the shared steps. The "delete template comments" step
    moves to `document-writing`, since every template carries comments.
- **Q5**: Domain worked example: optional or required? Pick one and align template and instruction.
  - **Answer**: required, in the overview or in its own section. All four domain documents carry one (three as a
    section, `DOMAIN-bundle-selection-and-installation` inside the overview), and the example is what separates the
    confused concepts the lead names. The template drops "Optional" and "Delete the section when unused" and says
    the example may sit in the overview instead.
- **Q6**: Retire DESIGN-distribution-transactions by folding its two useful lines into
  `DESIGN-distribution-file-directory-replacement`; which inbound references need repointing (`devkit docs refs`)?
  - **Answer**: fold its problem sentence (rollback must tell prior file content from directories the change set
    created) into the successor's lead and its `ARCH-05-4-distribution-components` §3 pointer into the successor's
    authority boundary, then delete the bundle and declare the old ID in the successor's `aliases`, so historical
    specs and materials still resolve. A same-kind fold is not a rename, so Q4 states this alias use in the shared
    steps. `devkit docs refs <old ID> --direction in -n 0` lists 10 referrers besides this proposal: the current ones to repoint are `CAP-DIST-sync-and-transactions` (one body line) and the successor
    (one body line). Line 79 of the resolved feedback
    `specs/2026-11/20261116-design-bundle-layout/feedback/viewer-adopts-bundle-grammar.md` names both designs, so
    `devkit rules fix` would write the successor ID twice; Development edits that line by hand to name the successor
    once, because `RULE-document-reference` reports alias references in feedback files. Completed specs,
    reconcile records and materials stay as written. The viewer test
    `FormalReading.test.ts` reads the real files and follows the capability → design → detail links, so it moves to
    capability → detail with five chapters instead of six; the detail design and `OPS-distribution-sync` keep
    a backticked `CAP-DIST-sync-and-transactions`, so the test's links back to the capability still resolve. `ARCH-06-runtime-view` §1 was a "not prerequisite" pointer
    and is dropped.
- **Q7**: Private helper names in design documents: keep public entry points, use cases and advisory codes, describe
  private steps in words. Is any private name load-bearing for a reader (e.g. a worked example)?
  - **Answer**: none is load-bearing. The three designs name about 30 underscore-prefixed helpers (17 in
    `DESIGN-proposal-handoff`, 7 in `DESIGN-distribution-file-directory-replacement`, 6 in
    `DESIGN-workflow-stage-evaluation`); the worked examples rest on codes, sentinel lines, paths and commit IDs, and
    the three private names they mention (`_result`, `_without_own_path`, `_waiting_for`) read as well in words.
    Keep public functions and use cases that a reader searches for (`apply_changes`, `require_writable`,
    `recover_locked`, `handoff_proposal`, `HandoffUseCase`, `evaluate_definition`), fields and codes; the viewer test
    pins `apply_changes`. `## Update triggers` names the same public entry points.

- **Q8** (scope extension): Which sentences of `CAP-DLV-proposal-lifecycle` §4.1 step 5 and §4.3 are pure mechanism
  that moves to `DESIGN-proposal-handoff`, and how does that settle the reverse duplication in
  `DESIGN-proposal-handoff` lines 74-82?
  - **Answer**: one direction for both: the capability states outcomes (what is refused before writing, what rolls
    back, codes and output lines, which references change and which do not), and the design states order, passes and
    helpers and cites the capability section for every outcome instead of restating it. Applied to the text:
    - Moves to the design (the capability keeps the outcome sentence): "planned in one preflight pass over the
      `materials/` leaves and the carried files" (§4.1 step 5; the capability keeps "refused before its first
      write"); "is followed back" in the rollback paragraph (the capability keeps "a directory created inside the
      moved `materials/` is removed when empty"); the library names `extract_links` and `relocate_links` in §4.3
      (the capability keeps "each changed file is replaced atomically"); "before ordinary relocation" in the
      dropped-record bullet (the design states the pass order).
    - Stays in the capability as guarantees: the merge containment, duplicate and conflict bullets with their
      `lstat` criteria, conflict kinds, `[TARGET]`/`[DETAIL]` lines and fix; the absent-in-preflight write rule and
      the concurrency window; the code-span path rewriting, including directory-only spans staying unchanged; the
      dropped-record citation condition (bytes at HEAD equal the deleted file) and `unmapped` reporting. Evidence:
      `ADR-proposal-handoff` §4 restates the merge rules as decided clauses and its §6 Confirmation says
      "`CAP-DLV-proposal-lifecycle` states the merge rules, the residual window and the result fields; review checks
      it against the tests"; `docs/decisions/2026-11/20261110-partial-supersession-statements.md` traces into §4.1
      step 4, which this unit does not touch.
    - No test or rule cites a moved phrase: no `.py` or `.ts` file under `packages/` reads
      `CAP-DLV-proposal-lifecycle`, and the moved phrases appear only in the capability itself
      (`rg "preflight pass|followed back|before ordinary relocation|relocate_links|extract_links"` over `docs/` and
      the bundle sources). Development reruns that check per moved sentence.
    - `DESIGN-proposal-handoff` lines 74-82 shrink to the order of the body carry and a citation of
      `CAP-DLV-proposal-lifecycle` §4.2 for the classification table.
    - The feedback's expected gain is smaller than it assumed: most of §4.1 step 5 and §4.3 is observable contract
      that an ADR confirms, so the capability shortens by a few clauses, not by the merge bullets.

### Proposed Design & Impact

- Docs bundle: templates (design, domain, operations, capability, usecase, ux, milestone) and instructions (design,
  domain, operations, living-spec, document, capability, usecase, ux writing) lose the duplicated and inactive
  elements above; `## Update triggers` and the narrowed `## Authority boundary` replace the current closings.
- `CAP-DOCS-documentation-ownership`: one routing table, §4 reduced to "the docs bundle supplies templates and writing
  instructions", §3.2 closing prose cut to its rules, §3.3 updated to the new section contracts.
- The 13 existing design, domain and operations documents follow the new standard; DESIGN-distribution-transactions
  is folded into `DESIGN-distribution-file-directory-replacement` and the old ID kept as an alias there.
- Tests pinning the changed phrases (`test_formal_doc_checkpoints_guidance.py`, the viewer's `FormalReading.test.ts`)
  are updated; bundle sources change, so `devkit sync` rewrites `.devkit/installation.json`.
- `CAP-DLV-proposal-lifecycle` §4.1 step 5 and §4.3 lose the mechanism clauses Q8 lists, which
  `DESIGN-proposal-handoff` takes over; `FB-proposal-lifecycle-capability-holds-mechanism-detail` resolves.
- Out of scope: the ADR template and decision-writing (`PROP-adr-body-metadata-removal`), §4.1 step 4 of
  `CAP-DLV-proposal-lifecycle` (its PADR body-metadata rewrite belongs to that sibling), other capability and use case
  documents (one reference repair in `CAP-DIST-sync-and-transactions` aside), and any rule change.

### Lifecycle & Retirement Criteria

- Planning settles Q1–Q7 and the spec boundaries; acceptance hands off to Development and integrates locally under
  `dev-integration=auto`.
- `PROP-adr-body-metadata-removal` touches the same docs bundle; the two units are integrated sequentially, this one
  first. Their write scopes are disjoint: that unit owns `templates/decision.md`, `decision-writing.md` and the
  devkit-spec proposals feature.
- Retire when the guidance and the document cleanup land.

### Planning decisions on edits

- **Bundle edits** (B = `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`):
  - `templates/{design,domain,operations}.md`: per-kind lead comment without the question rule; `## Update
    triggers` and the narrowed `## Authority boundary` per Q1/Q2; domain example per Q5; the design datasheet
    comment points to `design-writing` instead of repeating the field list.
  - `templates/capability.md`: drop the unused §4 scaffold lines (0 of 59 capabilities use them; keep the heading),
    the Summary comment that repeats frontmatter `summary` (keep the heading), the file-path comment and the
    "selected development approach" clause. `templates/usecase.md` and `templates/ux.md`: drop the file-path
    comment and the `---` separators; keep every string the UX and use case tests pin. `templates/milestone.md`:
    drop the two "selected development approach defines" sentences.
  - `instructions/{usecase,ux}-writing.md` and `living-spec-writing.md` line 13: drop the "selected development
    approach defines" sentences that give no action. Keep `decision-writing.md` line 19 (sibling scope) and
    `living-spec-writing.md` line 14. The docs bundle's own constitution already states the neutrality, and the
    distribution test bans only SDD markers.
  - `instructions/document-writing.md`: drop the `YAML_BINDING_UNAVAILABLE` install bullet; the advisory's `fix`
    carries it (`devkit_core.base.errors.YamlBindingUnavailableError`). Add the template-comment step.
- **CAP-DOCS-documentation-ownership**: §3.1 rules 5 and 7 become one rule with the Q3 table; §3.1 rule 6 and the
  §3.3 closing lines on operations authority stay, since Q2 relies on them; §3.2 keeps rules 1-2
  and drops the closing paragraph that `architecture-writing` "Responsibility boundary" states; §3.3 rule 2 states
  the new closing; §3.3's closing "This migration transfers..." sentence goes; §4 keeps the index and Review
  sentences and drops the template layout.
- **Existing documents**: apply the audit's per-document list in `materials/` (`document-audit.md`). Remove only a
  sentence whose fact a table row, frontmatter or another sentence of the same document already states; move a
  unique distinction into its row instead of deleting it. Write the old ID DESIGN-distribution-transactions as plain text in the spec's mapping, so
  `devkit rules fix` keeps the record.
- **Test pins to keep**: `templates/design.md` keeps the phrase "later run, another process or another tool reads
  back" with "datasheet" (`test_formal_doc_checkpoints_guidance.py` 41-42) while the field list moves to
  `design-writing`; `templates/capability.md` keeps "capability-writing" and `templates/usecase.md` exactly two
  "usecase-writing" (`test_writing_guidance.py` 110, 116); new bundle text carries none of the SDD markers
  `test_distribution.py` bans; `FormalReading.test.ts` keeps its text pins (`apply_changes`, the Installation
  receipt and Milestone membership rows, `TRANSACTION_PENDING`).
- **Sibling unit**: `DESIGN-proposal-handoff` line 93 names `_accept_status`, which `PROP-adr-body-metadata-removal`
  changes; this unit words it as "sets the accepted status" without the body Status line, so the sibling needs no
  edit of the design. That sibling owns neither `docs/designs/` nor `.devkit/installation.json`; integrating this
  unit first leaves it only its own sync output.
- **Effort**: `dev_effort` stays `medium`: the change is text across one bundle, one capability, 13 documents and two
  tests, with no code path.
- **Formal documents**: the change edits the design, domain and operations documents themselves; no new formal
  document is created. DESIGN-distribution-transactions is the only identity removed.

