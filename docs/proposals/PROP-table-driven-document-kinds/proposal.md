---
id: PROP-table-driven-document-kinds
title: Table-driven document kind definitions
summary: "Moves each document kind's prefix, location, Living Spec membership and relation fields into one definition table that the index, the spec rules and browsing read, so a new kind is added in one place without changing current behavior."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-26
target_area: documents/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-ux-documentation
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/
    - packages/devkit-spec/tests/
    - packages/devkit-viewer/src/devkit_viewer/features/browse/
    - packages/devkit-viewer/frontend/src/lib/
    - packages/devkit-viewer/src/devkit_viewer/static/
    - packages/devkit-viewer/tests/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/capabilities/viewer/
    - docs/architecture/
    - .devkit/managed/spec/
    - .devkit/installation.json
  excludes:
    - New document kinds
    - A plug-in or configuration extension point for document kinds
    - Changes to document IDs, paths, rule codes or messages
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-table-driven-document-kinds] Table-driven document kind definitions

## 1. Background & Hypothesis

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
  in further places, and the viewer front end keeps its own knowledge of the Living Spec directories.

Adding a kind therefore means finding every such place by search. A missed branch does not fail: a fallback such as
"not a use case, so a capability" silently gives the new kind the wrong directory or rule. The UX document kind of
`MS-ux-documentation` is the first kind this would affect, and it would not be the last.

Hypothesis: one definition table per kind (prefix, kind name, location pattern, Living Spec directory, Living Spec
membership, the relation fields it declares and accepts, summary requirement, template) can be read by the index,
the spec rules, browsing and the viewer. Adding a kind then means adding a row and its template, while the
lifecycle behavior that really is kind-specific (spec lifecycle, proposal handoff, feedback lifecycle, milestone
hygiene) stays in code. The change is a refactor: every current output stays identical.

## 2. Technical Spike Questions

- **Q1**: Which per-kind facts are data that belongs in the table, and which are behavior that stays kind-specific
  code? List every current kind test (`Kind.` and `kind_of` uses across devkit-spec) and classify each.
- **Q2**: Where does the table live so that models, services and the governance rules read it without breaking the
  layer direction (models never import higher layers)?
- **Q3**: How does the viewer obtain the same definitions: served by the Python side, generated into the front end,
  or kept as a checked copy? Which choice keeps the committed front-end build in step?
- **Q4**: How is "no behavior change" shown: the existing test suites unchanged, plus identical `devkit rules check`,
  `devkit spec list` and search output on this repository before and after?

### Spike findings

Evidence is in `MAT-kind-facts-inventory` and `envelopes/scout-01.yaml`.

- **Q1**: table data is the prefix and order, Living Spec membership and directory, area scoping,
  `RULE-spec-format` scope, heading-token kinds, the summary requirement, entrypoint-bearing kinds, terminal
  statuses and the relation fields each kind accepts. Path and stem grammars, spec bundle files, unit anchors and
  their relation rules, and the spec, proposal, feedback and milestone lifecycles stay code. Fallbacks between
  kinds sit at `id_convention.py:200-222`, `:476-485` and `:509` and `spec_format.py:316-322`, and the
  entrypoint-bearing set has a second, path-keyed copy in `entrypoints/services/paths.py:25`
  (`envelopes/challenger-01.yaml` findings 1 and 2).
- **Q2**: the table lives in `features/documents/models/` beside `ids.py`. `Kind` stays a declared enum, because 51
  static `Kind.<MEMBER>` references would lose their type under a generated enum
  (`PADR-kind-definition-table-keyed-on-the-declared-kind-enum`).
- **Q3**: the viewer's kind knowledge is front-end constants, and it neither depends on devkit-spec nor receives a
  kind in any payload; autohub hosts supply their own data source, so only a definition inside the front-end
  bundle reaches every host. The front-end link pattern has already drifted (`US` instead of `UC`, no `FB` or
  `MS`). The source of the viewer's copy is a user question.
- **Q4**: `devkit spec list`, `devkit spec search` and `devkit rules check` JSON output is byte-stable between runs,
  but this repository has no rule violations and many rule tests match message fragments, so message parity needs a
  characterization fixture workspace captured before the first code change.

## 3. Proposed Design & Impact

- A kind definition table in `features/documents/models/`, one frozen row per declared `Kind` member, replaces the
  scattered constants; `PREFIXES`, `ID_SOURCE`, `kind_of` and `is_id` derive from it and keep their signatures
  (`PADR-kind-definition-table-keyed-on-the-declared-kind-enum`).
- The index, `RULE-id-convention`, `RULE-spec-format`, `RULE-document-summary`, `RULE-code-entrypoints`,
  `RULE-document-reference`, `RULE-traceability-link`, the entrypoint paths, browse and search read their per-kind
  facts through one check-time accessor; the fallbacks at `id_convention.py:200-222`, `:476-485`, `:509` and
  `spec_format.py:316-322` become explicit lookups that return today's values, and a missing fact fails instead
  of borrowing another kind's.
- Unit tests check one row per member in enum order, one prefix per relation field, and a patched accessor to show
  the rules follow the table.
- `CAP-DOCS-document-model` section 3.2 states that the table is the single definition of kinds; its table of
  prefixes and locations stays as the documented contract (`target-docs.md`).
- The viewer's prefix and Living Spec directory knowledge follows the choice of Planning question q2.
- Baseline: before the first code change, the development worker adds a characterization fixture workspace with
  one violation per rule branch per kind and captures, at its starting head, its `devkit rules check --format json`
  output and `devkit rules fix` diff, plus `devkit spec list --all-namespaces -n 0 --format json`,
  `devkit spec search "document kind" --format json` and the `--help` text of both on this repository. All are
  identical after the change, and the existing suites pass unchanged.
- Size: `M` and `dev_effort: medium` hold unless q2 chooses a generated viewer copy, which adds a generator, an
  artifact entry, an affected-tests mapping and `CAP-GEN-tracked-artifacts` reconciliation and makes it `L`.
- Non-goals: no new kind (the UX kind is `PROP-ux-documentation`), no plug-in or configuration extension point, no
  change to the closed set of kinds, no change to IDs, paths, rule codes or messages.

### Relation to parallel proposals

- `PROP-ux-documentation` depends on this proposal and is developed after it (user decision). Both own the
  devkit-spec features, the viewer front end and `CAP-DOCS-document-model`; it adds its kind as a member and a row
  of this table, so this change must land first and it rebases on it.
- `PROP-foundation-documents` adds an ID-free group, not a kind, so it adds no row. It overlaps on
  `RULE-id-convention`, `RULE-document-summary` (keyed by kind, while foundation documents carry a summary without
  an ID), `RULE-spec-format` (path-based scope, its Q2), the `docs/glossary.md` owner input of
  `RULE-document-reference` and `CAP-DOCS-document-model` section 3. Neither needs the other, and the one that lands
  second rebases. The viewer's `bookGroup` hard-codes `docs/glossary.md`; this proposal keeps that rule unchanged,
  and the glossary move should carry its viewer update (that proposal's Planning owns it, not this one).

### Planning decisions

- The table keys on the declared `Kind` enum (`PADR-kind-definition-table-keyed-on-the-declared-kind-enum`).
- The table has no template field: no code reads templates, which stay bundle files.
- The proposal's "synthetic kind row" test becomes an injected-table test, because a declared enum admits no extra
  member at test time.
- Rows follow the enum order with no position field; each relation field maps to one prefix, `depends_on` stays on
  the milestone row with its unit case in code, and the traceability pair is one explicit declaration
  (`envelopes/challenger-01.yaml` findings 8 and 10).
- Open for the user: the path check of a new Living Spec kind and so the scope of the hypothesis (q1, challenger
  finding 6), whether and how the viewer follows the table, including the drifted link pattern (q2), and whether
  the wrong milestone path remediation is kept (q3, challenger finding 7).

## 4. Lifecycle & Retirement Criteria

- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-table-driven-document-kinds`; the proposal is deleted there and its decisions become ADRs.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
