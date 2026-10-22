---
id: PLAN-document-id-aliases-and-compaction
spec: SPEC-document-id-aliases-and-compaction
---

# Technical Plan: `SPEC-document-id-aliases-and-compaction` Document and Playbook ID Aliases

## 1. Constitution & Invariant Review

None. The design is accepted in `ADR-document-id-aliases` and `ADR-playbook-aliases-as-identifiers`; the playbook
change refines `ADR-external-playbook-execution` without reversing it. The playbook asset format change is a breaking
change made in place, as the repository's compatibility policy allows. No file under `docs/decisions/` changes.

### Planned Boundaries:
- `packages/devkit-spec/` (source, bundle instructions, rule guide and tests)
- `docs/capabilities/documents/`, `docs/capabilities/governance/`
- `packages/devkit-dist/src/devkit_dist/features/distribution/`, `packages/devkit-dist/tests/`
- `packages/devkit-dist/src/devkit_dist/features/search/services/index.py` (docstring wording only)
- `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`
- `docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md`, `docs/development/reference/distribution.md`
- `docs/capabilities/search/CAP-SRCH-document-search.md`, `docs/architecture/ARCH-08-2-resource-taxonomy.md`
- the bundled playbooks of devkit-agt `authoring`, devkit-catalog `maintenance` and devkit-starter
- `.devkit/installation.json` and projections through `devkit sync`

### Excluded Boundaries:
- `docs/decisions/`
- `packages/devkit/src/devkit_agt/features/`
- `packages/devkit-viewer/`

## 2. Architecture Overview & Impact

- **Impacted Components**:
  - `devkit_spec.features.documents.models` (`ids`, `model`, `parse`): the legacy ID predicate moves into `ids`;
    `Document` gains `aliases` and `alias_issues`; the parser validates the field.
  - `devkit_spec.features.documents.repositories.index.DocumentIndex`: `by_alias`, the canonical mapping, collision
    listing; `resolve()`, `incoming()` and `outgoing()` go through the mapping.
  - `devkit_spec.features.documents.services.dependencies`: `target_problem` and `cycle_members` canonicalise.
  - `devkit_spec.features.documents.usecases` (`browse`, `search`) and `cli.commands`: `resolve` reports the alias,
    `refs` groups by canonical ID, `search` pins an exact alias.
  - `devkit_spec.features.governance.usecases`: `document_reference` (alias shape and collision identity checks,
    fixable alias references, decision-record exemption, glossary report, canonical `_handed_off`, cycle graph),
    `traceability_link` (canonical target and reverse-link comparison), `hygiene` (milestone membership),
    `id_convention` (imports the shared legacy predicate).
  - `devkit_spec.features.proposals`: `handoff` (alias carriage, ADR alias translation, `_check_targets` clash
    refusal, `_check_dependency_projection` alias map), `services/rewrite` (alias mapping, ambiguity), `scaffold`
    (`check_spec_conflict`, PADR duplicate check), `specs` (slug taken), `roadmap` (milestone value).
  - `devkit_spec.features.entrypoints.usecases.derive`: `--target` resolves through `resolve()`, unchanged code.
  - `devkit_dist.features.distribution`: `services/bundles/playbooks.py` (slug aliases),
    `services/bundles/manifest.py` (bundle-level uniqueness), `usecases/playbook_search.py` (name and description
    only), `usecases/playbook_get.py` (alias path), `models/results.py` (`alias` field), `models/errors.py`
    (`PLAYBOOK_ALIAS_AMBIGUOUS`), `services/installation/playbook_skill.py` (skill text).
  - Bundled playbooks drop keyword aliases; Living Spec documents and instructions follow.
- **New Dependencies**: None.

## 3. Component & Interface Design

```python
# devkit_spec.features.documents.models.ids
def legacy_references(text: str) -> list[re.Match[str]]: ...   # moved from RULE-id-convention
def is_legacy_id(value: str) -> bool: ...                     # bool(legacy_references(value))

# devkit_spec.features.documents.models.model
@dataclass(slots=True)
class Document:
    ...
    aliases: tuple[str, ...] = ()          # validated items, in order
    alias_issues: list[Issue] = ...        # identity issues, reported over every document

# devkit_spec.features.documents.repositories.index
class DocumentIndex:
    by_alias: dict[str, list[Document]]
    def canonical(self, written: str) -> tuple[Document, str | None] | None: ...
        # (document, alias used or None); None when no document or several
    def canonical_id(self, written: str) -> str: ...            # canonical ID, else ``written``
    def lookup(self, written: str) -> tuple[Document, str | None]: ...
        # raises UnresolvedIdError / DuplicateIdError
    def resolve(self, written: str) -> Document: ...            # lookup()[0]
    def alias_collisions(self) -> list[tuple[str, list[Document]]]: ...
    def declares(self, document_id: str) -> list[Document]: ... # by_id plus by_alias holders
```

- **Precedence**: `canonical(written)` returns the declared document when `by_id` has exactly one; when `by_id` has
  several it returns `None`; otherwise the alias resolves only when exactly one document declares it.
- **Rule**: an alias reference is a fixable error in a current, non-material, non-decision document (kinds `ADR` and
  `PADR` are decision records); the fix maps it to `canonical_id`. Shape issues and collisions are reported in the
  identity loop next to the duplicate-ID check, on every targeted document.
- **Handoff**: `spec_files` writes `aliases` from the proposal's validated aliases with `SPEC-`; `_plan_decisions`
  replaces each PADR alias item in its frontmatter span with `ADR-` before the PADR-to-ADR promotion. `rewrite_ids`
  maps each carried alias to the new canonical ID. `_check_targets` collects the graduating IDs and translated
  aliases and refuses duplicates among them and any equal to an existing ID or alias.
- **Playbooks**: `PlaybookHeader.aliases` must match `SLUG`; `_check_playbook_aliases(bundle)` runs in `_load`.
  `GetPlaybook` tries the exact asset first; on a miss it reads every effective playbook header of the bundle and
  serves the single declarer, raising `PlaybookAliasAmbiguousError` for several. `PlaybookResult.alias` is
  `str | None`.

## 5. Error Handling & Edge Cases

- **Malformed aliases**: bad items are dropped from the index and reported; the document stays indexed.
- **Collisions**: never resolved through the alias; the rule reports every document involved; fix leaves the
  reference.
- **Handoff clash**: refused before any write with `SPEC_PROPOSAL_TARGET_EXISTS`.
- **Playbook alias ambiguity at retrieval**: `PLAYBOOK_ALIAS_AMBIGUOUS` (exit 2) naming the declaring playbooks; an
  invalid effective header on the alias path is `BUNDLE_INVALID` as on the exact path.

## 6. Verification & Test Plan

- Unit: `packages/devkit-spec/tests/unit/features/documents/` (parsing and shape on every kind, index mapping,
  precedence, collisions).
- Rule tests: `bundle/rules/document_reference/tests/test_rule.py` (alias fix, historical and decision-record
  exemption, self-mention, relation typing, materials, ADR alias, glossary, cycle, late handed-off reference).
- Governance integration: traceability through an alias, hygiene milestone membership with an `MS` alias.
- Handoff and scaffolding integration tests; CLI tests for `resolve`, `refs`, `search`, entrypoints `--target`.
- devkit-dist integration tests for manifest validation, search, `playbook get` (exact, alias, shadowing,
  ambiguous, override collision).
- Commands: `just lint devkit-spec`, `just lint devkit-dist`, `just check devkit-spec`, `just check devkit-dist`,
  `just test-affected`, `just rules-check`, `uv run devkit sync` then `uv run devkit status`.
