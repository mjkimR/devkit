---
id: PLAN-table-driven-document-kinds
spec: SPEC-table-driven-document-kinds
---

# Technical Plan: `SPEC-table-driven-document-kinds` Table-driven document kind definitions

## 1. Constitution & Invariant Review

None. The design follows `ADR-kind-definition-table-keyed-on-the-declared-kind-enum`: the table sits in the
documents models (models import nothing above them), `Kind` stays a declared enum, and no `MUST` of
`docs/architecture/` or of `CAP-DOCS-document-model` and `CAP-GOV-spec-rules` changes.

## 2. Architecture Overview & Impact

- Target Area: `packages/devkit-spec/src/devkit_spec/features/documents/models/`
- Target Docs Blueprint: `PROP-table-driven-document-kinds-target` (Living Spec targets for this plan and reconcile.md)

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/features/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/`
- `packages/devkit-spec/tests/`
- `docs/capabilities/documents/`
- `docs/capabilities/governance/`
- `docs/architecture/`
- `.devkit/installation.json`

### Excluded Boundaries:
- `New document kinds`
- `A plug-in or configuration extension point for document kinds`
- `Changes to document IDs, paths, rule codes or messages`
- `The viewer (link-prefix drift is FB-viewer-link-prefixes-drift; UX viewer support is SPEC-ux-documentation)`
- `.devkit/managed/` (written only by `devkit sync`, and ignored by Git)

### Components

- `documents/models/kinds.py` (new): `Kind` moves here from `ids.py` (which re-exports it, so every import keeps
  working), beside `KindDefinition`, `Summary`, `FormatScope`, the row table, `validate`, the accessors
  `definitions()` / `definition(kind)` and the derived helpers below. No new dependency.
- `documents/models/ids.py`: `PREFIXES` and `ID_SOURCE` derive from the rows at import (the ADR's exception).
- `documents/repositories/index.py`: `is_terminal` reads the row's `terminal_statuses`; `TERMINAL_STATUSES` stays
  exported, derived from the rows.
- `governance/usecases/id_convention.py`: Living Spec directories and membership, the heading-token prefixes, the
  area remediation directory and the path remediations come from the rows or one explicit per-kind map; the
  capability, use case and architecture grammars become one function each in a `_LIVING_GRAMMARS` map, and a Living
  Spec row without one raises.
- `governance/usecases/spec_format.py`: the checked directories derive from each row's `format_scope` and
  `directory`; the fix-time default status is the row's `default_status`.
- `governance/usecases/document_summary.py`: `required` reads the row's `summary` and `anchor`.
- `governance/usecases/code_entrypoints.py` and `entrypoints/services/paths.py`: the entrypoint-bearing kinds and
  directories come from the rows' `entrypoints` flag.
- `governance/usecases/document_reference.py`: the field-to-prefix map comes from the rows' `relation_fields`.
- `governance/usecases/traceability_link.py`: its directories come from the use case and capability rows; the pair
  (fields and labels) stays its one explicit declaration.
- Kept as kind-specific code: the grammar bodies and their messages, spec bundle files, unit anchors, `depends_on`
  on units, the lifecycles, the milestone status vocabulary of `RULE-spec-format`, browse ordering by
  `enumerate(Kind)` (the rows follow the enum order) and the CLI kind choices.

## 3. Component & Interface Design

```python
class Summary(StrEnum):  # RULE-document-summary requirement
    ALWAYS = "always"; ANCHOR = "anchor"; NEVER = "never"

class FormatScope(StrEnum):  # where RULE-spec-format checks the kind's directory
    NONE = "none"; GLOBAL = "global"; EVERY_ROOT = "every-root"

@dataclass(frozen=True, slots=True)
class KindDefinition:  # every field required: a new row states every fact
    kind: Kind
    prefix: str
    directory: str           # its directory under a docs root ("capabilities"), "" when none
    living_spec: bool        # a Living Spec document: ID is the file stem, checked in every docs root
    area_scoped: bool        # <directory>/<area>/ with an area: field
    format_scope: FormatScope
    heading_token: bool      # RULE-id-convention reads a heading [ID] token of this prefix
    summary: Summary
    anchor: str              # the anchor file of an ANCHOR summary, "" otherwise
    entrypoints: bool        # may declare entrypoints
    terminal_statuses: frozenset[str]
    default_status: str      # RULE-spec-format fix-time status
    relation_fields: tuple[str, ...]  # frontmatter fields that take this kind's ID

class KindTableError(ValueError): ...

def validate(table: Sequence[KindDefinition]) -> tuple[KindDefinition, ...]  # raises KindTableError
def definitions() -> tuple[KindDefinition, ...]   # the current table, read at check time
def definition(kind: Kind) -> KindDefinition      # raises KindTableError for a kind without a row
```

The module validates its own table at import, so a member without a row fails every import. Tests inject a table
by patching the module-level table (through `validate`), which the accessors read on each call.

## 4. Error Handling & Edge Cases

- A Living Spec row without a grammar, or an identifier target kind without a path remediation, raises
  `KindTableError` naming the kind at check time: the defect is in code, and the rule error is the visible failure.
- The heading-token regular expression is built from the rows on each check; at the real table it covers today's
  set. The alternation follows the enum order and matches the same tokens.
- `TERMINAL_STATUSES` and `PREFIXES` are import-time snapshots for library callers; the rules and `is_terminal` read
  the accessor.

## 5. Storage & State Management

The parse memo fingerprint covers `devkit_spec.features.documents.models.*` by package walk, so `kinds.py` joins it
with no change (`AC-06`); a table edit discards the memo.

## 6. Verification & Test Plan

- Characterization (`AC-05`): `scratch/char/capture.sh before` ran at the starting head `6a19ff5f` before any code
  change (a second run, `before2`, was byte-identical); `capture.sh after` runs at the final head and
  `diff -r -x ws scratch/char/before scratch/char/after` must be empty.
- Unit tests in `packages/devkit-spec/tests/unit/features/documents/test_kinds.py` (`AC-01`, `AC-02`, `AC-06`) and
  rule tests with an injected table (`AC-03`, `AC-04`).
- `just lint devkit-spec`, `just lint-check devkit-spec`, `just check devkit-spec`, `just test-affected`,
  `uv run devkit rules check --ci --base 6a19ff5f`, `uv run devkit sync --check`.
