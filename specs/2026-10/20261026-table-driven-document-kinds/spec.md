---
id: SPEC-table-driven-document-kinds
title: Table-driven document kind definitions
summary: Moves each document kind's prefix, Living Spec membership, directory, relation fields and other per-kind facts into one definition table that the index, the spec rules and browsing read, so a missing fact for a new kind fails instead of falling back, without changing current behavior.
status: completed
created: 2026-10-26
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-GOV-spec-rules
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-table-driven-document-kinds] Table-driven document kind definitions

## 1. Problem Statement & Motivation

Handed off from proposal PROP-table-driven-document-kinds on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-table-driven-document-kinds`
- Target Docs Blueprint: `PROP-table-driven-document-kinds-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

A document's kind follows from its ID prefix (`CAP-DOCS-document-model` section 3.2). The facts that make up a kind
are not kept together:

- `features/documents/models/ids.py` defines the closed `Kind` enum and the `PREFIXES` map that builds the ID
  pattern.
- `features/governance/usecases/id_convention.py` repeats which kinds form the Living Spec (`_LIVING_SPEC`), which
  directory holds which kind (`_LIVING_DIRECTORIES`), and the path and ID rule of each kind in its own branch. Some
  branches assume a fixed set, for example choosing `usecases` when a kind is a use case and `capabilities`
  otherwise.
- The relation fields and the kind each accepts (`usecases` takes `UC`, `capabilities` takes `CAP`, `milestone`
  takes `MS`) live in the reference rule; summary, entrypoint, scope, hygiene, roadmap and browsing code test kinds
  in further places.

Adding a kind therefore means finding every such place by search. A missed branch does not fail: a fallback such as
"not a use case, so a capability" silently gives the new kind the wrong directory or rule. The UX document kind of
`MS-ux-documentation` is the first kind this would affect, and it would not be the last.

Hypothesis: one definition row per kind (prefix, kind name, Living Spec directory and membership, the relation
fields it accepts, summary requirement and the other per-kind facts of `MAT-kind-facts-inventory`) can be read by
the index, the spec rules and browsing. Adding a kind then means a `Kind` member, its row, its path-grammar branch
and its template, and an exhaustiveness check fails when any of them is missing instead of letting the kind fall
back to another kind's rule. Path grammars and the lifecycle behavior that really is kind-specific (spec
lifecycle, proposal handoff, feedback lifecycle, milestone hygiene) stay in code. The change is a refactor: every
current output stays identical.

## 2. User Stories

- **US-1**: As an agent adding a document kind, I want every per-kind fact in one definition row so that a fact I
  forget fails a check instead of silently borrowing another kind's directory, rule or message.
- **US-2**: As a maintainer, I want the index, the spec rules, entrypoints and browsing to read the same row so that
  the facts cannot drift apart.

## 3. Non-Goals

1. **Scope Excluded**: no new kind (the UX kind is `SPEC-ux-documentation`), no change to the closed set of kinds,
   no plug-in or configuration extension point, no location grammar as row data, and no change to any ID, path,
   rule code, message, remediation or CLI output.
2. **Scope Excluded**: no viewer change; the front-end link-prefix drift is `FB-viewer-link-prefixes-drift`
   (resolved by a separate bugfix).
3. **Scope Excluded**: kind-specific lifecycle behavior stays code: path and stem grammars, spec bundle files, unit
   anchors and their relation rules, and the spec, proposal, feedback and milestone lifecycles, including the
   milestone status vocabulary and `created_at` check of `RULE-spec-format`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] One definition row per kind

- **Given** the documents models
- **When** the kind table is loaded or validated
- **Then** it holds exactly one row per `Kind` member in enum order, each prefix and each relation field appears in
  exactly one row, and a table with a missing, extra, reordered or duplicate row, a duplicated prefix or relation
  field, or an anchor-only summary without an anchor file raises `KindTableError` naming the defect.

### [AC-02] Derived ID grammar unchanged

- **Given** the table
- **When** `PREFIXES`, `ID_SOURCE`, `ID_PATTERN`, `TERMINAL_STATUSES`, `kind_of` and `is_id` are read
- **Then** they keep their names and signatures and equal today's values: the same prefix-to-kind map in the same
  order, the same pattern source and the same terminal statuses.

### [AC-03] Consumers follow the table at check time

- **Given** a table injected through the accessor that changes one fact (a summary requirement, an
  entrypoint-bearing kind, a relation-field prefix, a default status or a terminal status)
- **When** `RULE-document-summary`, `RULE-code-entrypoints`, `RULE-document-reference`, `RULE-spec-format` or the
  index evaluates a workspace
- **Then** the result changes as the injected row says, without re-importing any module.

### [AC-04] A missing fact fails instead of falling back

- **Given** a table whose Living Spec row has no path-grammar branch in `RULE-id-convention`, or an identifier
  target kind with no path remediation
- **When** `RULE-id-convention` checks a document of that kind
- **Then** it raises `KindTableError` naming the kind, instead of checking the document under the architecture
  grammar or giving it the dated-partition remediation.

### [AC-05] Characterization outputs are identical

- **Given** the characterization fixture workspace (one violation per rule branch per kind, a registered namespace,
  terminal documents) and this repository
- **When** `devkit rules check --format json` and `devkit rules fix` run on the fixture, and
  `devkit spec list --all-namespaces -n 0 --format json`, `devkit spec search "document kind" --format json` and the
  `--help` text of `devkit spec list`, `devkit spec search`, `devkit rules` and `devkit rules check` run, before the
  first code change and at the final head
- **Then** every captured output and the fix diff are byte-identical (`diff -r` empty), and the existing test suites
  pass with no existing assertion changed.

### [AC-06] The parse memo follows the table

- **Given** the document index parse memo
- **When** the kind table module changes
- **Then** the parser fingerprint changes with it, because the module lies in `features/documents/models/`, which the
  fingerprint covers.

## 5. Assumptions

- The handed-off premises hold on the current base: the fallbacks the proposal names are at
  `id_convention.py:200-222` (grammar), `:476-490` (path remediation; the milestone remediation fix of
  `SPEC-link-prefixes-and-milestone-remediation` already landed and is kept byte-for-byte), `:514` (area
  directory) and `spec_format.py:316-322` (default status); the entrypoint-bearing path copy is
  `entrypoints/services/paths.py:25`.
- The table error is a `ValueError` subclass in the documents models (`KindTableError`): a defect in the code's own
  declarations, raised to the developer, never a user-facing advisory, so it adds no advisory code.
- The heading-token kinds keep today's set (`SPEC PLAN TASKS REC ADR FB CAP UC ARCH MS`); the regular-expression
  alternation follows the enum order instead, which matches the same tokens because no prefix followed by `-` is a
  prefix of another.

## 6. Source feedback

- `FB-milestone-path-remediation-dated` (resolved before this unit; its remediation text is kept).
- `FB-viewer-link-prefixes-drift` (out of scope; resolved by a separate bugfix).

## 7. Carried Proposal Notes


Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Which per-kind facts are data that belongs in the table, and which are behavior that stays kind-specific
  code? List every current kind test (`Kind.` and `kind_of` uses across devkit-spec) and classify each.
- **Q2**: Where does the table live so that models, services and the governance rules read it without breaking the
  layer direction (models never import higher layers)?
- **Q3**: How does the viewer obtain the same definitions: served by the Python side, generated into the front end,
  or kept as a checked copy? Which choice keeps the committed front-end build in step?
- **Q4**: How is "no behavior change" shown: the existing test suites unchanged, plus identical `devkit rules check`,
  `devkit spec list` and search output on this repository before and after?

#### Spike findings

Evidence is in `MAT-kind-facts-inventory` and historical Git `cfc82a4cb3d651c38c61b6a4da880be9ebfbe2fd:docs/proposals/PROP-table-driven-document-kinds/envelopes/scout-01.yaml`.

- **Q1**: table data is the prefix and order, Living Spec membership and directory, area scoping,
  `RULE-spec-format` scope, heading-token kinds, the summary requirement, entrypoint-bearing kinds, terminal
  statuses and the relation fields each kind accepts. Path and stem grammars, spec bundle files, unit anchors and
  their relation rules, and the spec, proposal, feedback and milestone lifecycles stay code. Fallbacks between
  kinds sit at `id_convention.py:200-222`, `:476-485` and `:509` and `spec_format.py:316-322`, and the
  entrypoint-bearing set has a second, path-keyed copy in `entrypoints/services/paths.py:25`
  (historical Git `cfc82a4cb3d651c38c61b6a4da880be9ebfbe2fd:docs/proposals/PROP-table-driven-document-kinds/envelopes/challenger-01.yaml` findings 1 and 2).
- **Q2**: the table lives in `features/documents/models/` beside `ids.py`. `Kind` stays a declared enum, because 51
  static `Kind.<MEMBER>` references would lose their type under a generated enum
  (`ADR-kind-definition-table-keyed-on-the-declared-kind-enum`).
- **Q3**: the viewer's kind knowledge is front-end constants, and it neither depends on devkit-spec nor receives a
  kind in any payload; autohub hosts supply their own data source, so only a definition inside the front-end
  bundle reaches every host. The front-end link pattern has already drifted (`US` instead of `UC`, no `FB` or
  `MS`). The viewer stays out of this proposal (Planning decisions).
- **Q4**: `devkit spec list`, `devkit spec search` and `devkit rules check` JSON output is byte-stable between runs,
  but this repository has no rule violations and many rule tests match message fragments, so message parity needs a
  characterization fixture workspace captured before the first code change.

### 3. Proposed Design & Impact

- A kind definition table in `features/documents/models/`, one frozen row per declared `Kind` member, replaces the
  scattered constants; `PREFIXES`, `ID_SOURCE`, `kind_of` and `is_id` derive from it and keep their signatures
  (`ADR-kind-definition-table-keyed-on-the-declared-kind-enum`).
- The index, `RULE-id-convention`, `RULE-spec-format`, `RULE-document-summary`, `RULE-code-entrypoints`,
  `RULE-document-reference`, `RULE-traceability-link`, the entrypoint paths, browse and search read their per-kind
  facts through one check-time accessor; the fallbacks at `id_convention.py:200-222`, `:476-485`, `:509` and
  `spec_format.py:316-322` become explicit lookups that return today's values, and a missing fact fails instead
  of borrowing another kind's.
- Unit tests check one row per member in enum order, one prefix per relation field, and a patched accessor to show
  the rules follow the table.
- Every Living Spec row must have a path-grammar branch in `RULE-id-convention`; a row without one raises, so an
  unknown Living Spec kind is no longer checked as an architecture document.
- `CAP-DOCS-document-model` section 3.2 states that the table is the single definition of kinds; its table of
  prefixes and locations stays as the documented contract (`target-docs.md`).
- The milestone path remediation keeps its current text, which wrongly names a dated partition; it is fixed in a
  separate bugfix (`FB-milestone-path-remediation-dated`).
- Baseline: before the first code change, the development worker adds a characterization fixture workspace with
  one violation per rule branch per kind and captures, at its starting head, its `devkit rules check --format json`
  output and `devkit rules fix` diff, plus `devkit spec list --all-namespaces -n 0 --format json`,
  `devkit spec search "document kind" --format json` and the `--help` text of both on this repository. All are
  identical after the change, and the existing suites pass unchanged.
- Size: `M` and `dev_effort: medium`: the change stays inside devkit-spec and its Living Spec.
- Non-goals: no new kind (the UX kind is `SPEC-ux-documentation`), no plug-in or configuration extension point, no
  change to the closed set of kinds, no change to IDs, paths, rule codes or messages, no location grammar as row
  data, and no viewer change.

#### Relation to parallel proposals

- `SPEC-ux-documentation` depends on this proposal and is developed after it (user decision). Both own the
  devkit-spec features and `CAP-DOCS-document-model`; it adds its kind as a member, a row, a path-grammar branch
  and templates, and adds its own viewer support, so this change must land first and it rebases on it.
- `SPEC-foundation-documents` adds an ID-free group, not a kind, so it adds no row. It overlaps on
  `RULE-id-convention`, `RULE-document-summary` (keyed by kind, while foundation documents carry a summary without
  an ID), `RULE-spec-format` (path-based scope, its Q2), the `docs/glossary.md` owner input of
  `RULE-document-reference` and `CAP-DOCS-document-model` section 3. Neither needs the other, and the one that lands
  second rebases. The viewer's `bookGroup` hard-codes `docs/glossary.md`; this proposal keeps that rule unchanged,
  and the glossary move should carry its viewer update (that proposal's Planning owns it, not this one).

#### Planning decisions

- The table keys on the declared `Kind` enum (`ADR-kind-definition-table-keyed-on-the-declared-kind-enum`).
- The table has no template field: no code reads templates, which stay bundle files.
- The proposal's "synthetic kind row" test becomes an injected-table test, because a declared enum admits no extra
  member at test time.
- Rows follow the enum order with no position field; each relation field maps to one prefix, `depends_on` stays on
  the milestone row with its unit case in code, and the traceability pair is one explicit declaration
  (historical Git `cfc82a4cb3d651c38c61b6a4da880be9ebfbe2fd:docs/proposals/PROP-table-driven-document-kinds/envelopes/challenger-01.yaml` findings 8 and 10).
- Path grammars stay code; a new kind needs a member, a row, a grammar branch and a template, and the
  exhaustiveness check replaces the silent architecture fall-through; the hypothesis is reworded to match (user,
  q1; challenger finding 6).
- The viewer is out of scope: the link-prefix drift is fixed by a separate bugfix from
  `FB-viewer-link-prefixes-drift`, and `SPEC-ux-documentation` adds its own viewer support (user, q2).
- The wrong milestone path remediation is kept byte-for-byte and fixed by a separate bugfix from
  `FB-milestone-path-remediation-dated` (user, q3; challenger finding 7).

### 4. Lifecycle & Retirement Criteria

- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-table-driven-document-kinds`; the proposal is deleted there and its decisions become ADRs.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.

