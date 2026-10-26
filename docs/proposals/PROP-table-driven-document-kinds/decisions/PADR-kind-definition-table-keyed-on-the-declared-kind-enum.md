---
id: PADR-kind-definition-table-keyed-on-the-declared-kind-enum
title: Kind definition table keyed on the declared Kind enum
summary: For document kind facts scattered across devkit-spec, we keep Kind a declared enum and add one definition row per member in the documents models, read by the index and spec rules, to remove silent fallbacks while static checks see every kind, accepting that a new kind adds a member and a row.
proposal: PROP-table-driven-document-kinds
status: draft
created_at: 2026-10-26
---

# [PADR-kind-definition-table-keyed-on-the-declared-kind-enum] Kind definition table keyed on the declared Kind enum

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

The facts that make up a document kind live in about a dozen modules of devkit-spec (`MAT-kind-facts-inventory`
section 1): the prefix map, Living Spec membership and directories, the summary requirement, terminal statuses,
entrypoint-bearing kinds, heading-token kinds and the field-to-prefix map of the reference rule. Some consumers fall
back between kinds ("not a use case, so a capability"), so a new kind that misses one place is silently treated as
another. `Kind` members are also referenced statically in 51 places outside `ids.py`, and behavior that really is
kind-specific (lifecycles, unit anchors, path grammars) depends on that.

## 2. Decision Drivers

- One place to read and change each per-kind fact.
- A missing fact for a kind fails a check instead of falling back to another kind.
- Pyright keeps seeing every `Kind` member; the layer direction stays intact (models never import higher layers).
- Every current ID, path, rule code, message and output stays byte-identical.

## 3. Considered Options

- **Keep the scattered constants**: no change cost; a new kind still needs a search and fallbacks stay silent.
- **Table generates the enum** (`StrEnum("Kind", rows)`): one source in theory; Pyright loses every member, so 51
  static references fail `just check` or turn into string lookups.
- **Declared enum plus one row per member**: the enum stays the static name of a kind, the row holds its data, and a
  check requires exactly one row per member; a new kind adds a member and a row.

## 4. Decision Outcome

Chosen: **declared enum plus one row per member**, because it is the only option that keeps static checking (third
driver) while giving one place per fact and a failing check (first two drivers).

- The table lives in `features/documents/models/` beside `ids.py`, as frozen dataclass rows with no imports above
  the models layer; the governance rules, browse, search and the CLI already import the documents feature.
- A row holds the prefix, the kind, the Living Spec directory or none, whether the directory is area-scoped, whether
  `RULE-spec-format` checks its directory (globally and in namespaces), whether its first H1 carries an ID token,
  its summary requirement (always, anchor file only, never), whether it bears `entrypoints`, its terminal statuses,
  its default status at fix time, and the relation fields that accept it (`usecases` and `related_usecases` accept
  `UC`, and so on). Rows follow the enum order, which `devkit spec list` and the CLI choices use; there is no
  separate position field.
- Each relation field maps to exactly one prefix, checked for uniqueness: `depends_on` sits only on the milestone
  row, and its unit-anchor case (`PROP-`/`SPEC-`) stays code. The use case and capability link pair of
  `RULE-traceability-link` is one explicit pair declaration beside the rows, not row data.
- Consumers read the rows through one accessor called at check time, never through constants bound at import; the
  ID regexes (`ID_SOURCE`, `ID_PATTERN`) are the exception and are built from the rows at import.
- The path-keyed copies of a fact derive from the rows too: `entrypoints/services/paths.py` builds its
  entrypoint-bearing directories from them.
- `PREFIXES`, `ID_SOURCE`, `ID_PATTERN`, `kind_of` and `is_id` keep their names and signatures and derive from the
  rows.
- Consumers read these facts from the table; the fallbacks between kinds (`MAT-kind-facts-inventory` section 1)
  are replaced by explicit lookups, and a kind without a required fact raises instead of taking another kind's
  value. The values the lookups return reproduce today's messages byte for byte.
- Kind-specific behavior stays code: path and stem grammars per kind, spec bundle files, unit anchors and their
  relation rules (`depends_on`, `milestone`, provenance), spec, proposal, feedback and milestone lifecycles
  (`MAT-kind-facts-inventory` section 2). How a new Living Spec kind gets its path check is decided with the user
  (proposal Planning decisions).
- Templates stay bundle files with no table field, because no code reads them.

## 5. Consequences

- Positive: adding a kind is a member and a row plus its kind-specific behavior, and a forgotten fact fails the
  exhaustiveness check.
- Negative: the enum and the table are two declarations of the same set; the check keeps them equal.
- Risk: a fact whose current consumers disagree (for example the heading-token set excludes `PROP`, `PADR` and
  `MAT` while other sets include them) must be encoded per consumer, not unified, or a message changes.
- Follow-up: `PROP-ux-documentation` adds its kind through this table once this change lands.

## 6. Confirmation

- A unit test in `packages/devkit-spec/tests/unit/features/documents/` asserts one row per `Kind` member, in enum
  order, and that `PREFIXES` equals the current map.
- A unit test patches the accessor with a table whose use case row names another Living Spec directory and whose
  capability row accepts another relation field, and shows that `RULE-id-convention`, `RULE-traceability-link` and
  `RULE-document-reference` follow the table with no other code change. A synthetic new kind is not possible with a
  declared enum; this test shows the consumers read the table rather than constants. It asserts which files are
  checked and as which kind, not message text, because the path messages keep their literal directory names.
- A unit test asserts that each relation field maps to exactly one prefix.
- The existing devkit-spec suites and the rule tests under `bundles/spec/bundle/rules/*/tests/` pass unchanged; a
  characterization fixture workspace added before the first code change gives identical `devkit rules check` JSON
  and `devkit rules fix` diffs, and `devkit spec list`, `devkit spec search` JSON and their `--help` text are
  identical before and after (`MAT-kind-facts-inventory` section 5).
