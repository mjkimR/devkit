---
id: PLAN-ux-documentation
spec: SPEC-ux-documentation
---

# Technical Plan: `SPEC-ux-documentation` UX documents, authoring guidance and use-case-driven review

## 1. Constitution & Invariant Review

- `ADR-kind-definition-table-keyed-on-the-declared-kind-enum`: the kind is one `Kind` member and one table row; the
  path and stem grammar stays kind-specific code in `RULE-id-convention` (`_LIVING_GRAMMARS`), which raises
  `KindTableError` for a Living Spec row without one.
- `ADR-delivery-classification`: the UX review is an optional delegation, not a stage; no workflow schema changes.
- `ADR-terminal-statuses-are-historical`: UX statuses have no terminal value, so the row declares none.
- `ADR-steering-documents-directory`: `docs/steering/ux-objects.md` is one steering file under the existing caps,
  created by the author on first use; nothing seeds it.
- `CAP-DLV-delivery-workflows` states six role contracts; it changes to seven (`ADR-ux-review-before-code`).
- No architecture `MUST` changes.

## 2. Architecture Overview & Impact

- Target Area: `packages/devkit-spec/src/devkit_spec/` (kind row, rules, blueprint, bundle content),
  `packages/devkit-viewer/frontend/src/lib/api/documents.ts`, `docs/`.

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/features/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`
- `packages/devkit-spec/tests/`
- `packages/devkit-viewer/src/devkit_viewer/features/browse/`
- `packages/devkit-viewer/frontend/src/lib/`
- `packages/devkit-viewer/src/devkit_viewer/static/`
- `packages/devkit-viewer/tests/`
- `docs/capabilities/documents/`
- `docs/capabilities/governance/`
- `docs/capabilities/delivery/`
- `docs/capabilities/viewer/`
- `docs/usecases/`
- `docs/architecture/`
- `docs/steering/glossary.md`
- `guides/`
- `.devkit/installation.json`
- `AGENTS.md`

`docs/steering/glossary.md` replaces the proposal's `docs/glossary.md`, which `SPEC-foundation-documents` moved
(the agreed boundary under `RULE-proposal-boundaries`' prerequisite-path procedure).

### Excluded Boundaries:
- `Wireframe or mock-up rendering and design tool integrations`
- `Visual styling, theming and design tokens`
- `Engine- or framework-specific UI verification`
- `Usability testing with real users`
- `Workflow engine changes in packages/devkit/ (check primitives, closable envelope kinds)`
- `Use cases or UX documents for devkit's own viewer`
- `.devkit/managed/` (written only by `devkit sync`)
- `handbook/`

### Components

- **Kind row** (`features/documents/models/kinds.py`): `Kind.UX = "ux"` after `USECASE`, row `UX`, `ux`,
  `living_spec`, `area_scoped`, `EVERY_ROOT`, heading token, `ALWAYS` summary, no entrypoints, no terminal statuses,
  `draft`, no relation fields. The ID grammar, index, `spec list ux`, search, `RULE-spec-format`,
  `RULE-document-summary` and namespace roots follow from the row.
- **`RULE-id-convention`** (`features/governance/usecases/id_convention.py`): `_UX_STEM` and a `_ux` grammar in
  `_LIVING_GRAMMARS` (`UX document must be stored at {root}/ux/{area}/UX-{slug}.md`, `file name must be UX-{slug} with
  a kebab-case slug that is not a sequence number`); the reference remediation names `UX-{slug}`.
- **UX model service** (new `features/governance/services/ux.py`): the use case step segmenter, the UX document
  reader (element, Interactions table rows with their lines, Content citations) and the per-use-case flow graph,
  shared by both rules.
- **`RULE-ux-links`** (new `features/governance/usecases/ux_links.py`, bundle folder `rules/ux_links/` with `rule.py`,
  `guide.md`, `tests/test_rule.py`; asset `ux-links`).
- **`RULE-ux-coverage`** (new `features/governance/usecases/ux_coverage.py`, bundle folder `rules/ux_coverage/`;
  asset `ux-coverage`, warning).
- **Blueprint** (`features/proposals/usecases/scaffold.py` `_target_docs`): a `### Screens (docs/ux/)` drafts
  subsection under section 2.
- **Bundle content**: `templates/ux.md`; `seed/docs/ux/README.md` and the `docs/README.md` row; `AGENTS.md.jinja`
  template list; `instructions/ux-writing.md` (asset `ux-writing`); `usecase-writing` step citation;
  `subagents/ux-reviewer.md` and `skills/spec-ux-review/SKILL.md` (assets `ux-reviewer`, `spec-ux-review`);
  `spec-specify` (SKILL, `feature.md`, `bugfix.md`), `spec-sync`, `spec/references/effort.md.jinja`,
  `spec/references/planning.md`, `workflows/sdd-proposal.md`, `spec-delegate` role list where roles are enumerated;
  `bundle.toml` assets and the `core` preset.
- **Viewer** (`frontend/src/lib/api/documents.ts`): `UX` in the bracket-ID pattern, `['ux', 'UX']` in `bookGroup`
  and `UX` after `Use Cases` in `bookGroups`; test in `HandbookMode.test.ts`; `just viewer build` output.
- **Living Spec**: the five capabilities of `related_capabilities`, `docs/steering/glossary.md` (two terms).

## 3. Component & Interface Design

```python
# devkit_spec.features.governance.services.ux
ELEMENTS = ("screen", "modal", "panel")
COLUMNS = ("Trigger", "Step", "From", "To", "Target", "Capability", "Feedback")
EXIT_WORDS = ("close", "back", "end")

@dataclass(frozen=True)
class Step:            # one main-scenario step or extension bullet of a use case
    key: str           # "1", "2a", "*a"
    line: int          # its first line
    end: int           # its last line
    extension: bool
    resumes: str | None  # the step key an extension resumes at; None when it ends the use case
    screens: tuple[str, ...]  # canonical UX IDs cited on its lines

@dataclass(frozen=True)
class Interaction:
    line: int
    steps: tuple[tuple[str, str], ...]  # (canonical UC ID, step key)
    step_cell: str
    target: str        # "", a canonical UX ID, "close", "back", "end", or the raw invalid value
    valid_step: bool

def use_case_steps(index: DocumentIndex, document: Document, text: str) -> list[Step]: ...
def read_ux(index: DocumentIndex, document: Document, text: str) -> UxDocument: ...  # element, problems, rows, content
```

`RULE-ux-links` messages (each on the UX document, or on the use case when only it is reported):

| Finding | Message |
| --- | --- |
| element | `element is missing; set screen, modal or panel` / `element "<v>" is not screen, modal or panel` |
| section | `no Interactions section` / `Interactions has no table with the columns Trigger, Step, From, To, Target, Capability, Feedback` |
| step cell | `Step cell "<v>" is not `UC-<slug>` <key>` |
| unlisted use case | `Step names <UC>, which usecases does not list` |
| unknown key | `Step names <UC> <key>, which is not a step of <UC>` |
| not citing | `Step names <UC> <key>, which does not cite <UX>` |
| unused entry | `usecases lists <UC>, but no Step cell names it` |
| reverse link | `<UC> step <key> cites <UX>, whose usecases does not list <UC>` |
| target | `Target "<v>" is not a UX document, close, back or end` |
| modal | `modal has no close or back interaction` |
| exit | `screen has no exit in <UC>` |
| reachability | `<UX> is not reachable from an entry of <UC>` |

`RULE-ux-coverage` messages: `<UC> step <key> cites no UX document` and `interaction has no Step`.

## 4. Error Handling & Edge Cases

- A UX document or use case whose text cannot be read is skipped (the index already reports it).
- An unresolved UC or UX ID in a field or cell is `RULE-document-reference`'s; `RULE-ux-links` skips the use case
  and reports a Target only when it is not a well-formed UX ID or no UX document declares it.
- Materials, completed bundles and documents outside the Living Spec directories are never read as UX documents or
  use cases (`is_material`, `index.is_historical`).
- The step parser ignores fenced code and HTML comments by using the index's body references, which already exclude
  them, and reads step boundaries from raw lines outside fences.

## 5. Verification & Test Plan

- Kind row: `packages/devkit-spec/tests/unit/features/documents/test_kinds.py` (AC-01).
- `RULE-id-convention`: its bundle tests (AC-02).
- Index, list, search, format and summary: a new `packages/devkit-spec/tests/integration/features/documents/test_ux_kind.py`
  (AC-03).
- `RULE-ux-links` and `RULE-ux-coverage`: `rules/ux_links/tests/test_rule.py` and `rules/ux_coverage/tests/test_rule.py`
  (AC-04 to AC-10), plus a test that every use case under this repository's `docs/usecases/` parses (AC-08).
- Bundle content: a new `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py` (AC-11, AC-12,
  AC-14) and `test_role_contracts.py` (AC-13); the blueprint test (AC-14).
- Viewer: `just viewer test`, `just viewer check`, `just viewer lint`, `just viewer build` (AC-03).
- Repository: `just lint`, `just check`, `just test-affected`, `uv run devkit rules check`, `uv run devkit sync
  --check` (AC-15).
- Baseline: the spec names no measured outcome; the before state is base `02615579`, where `UX-` is not an ID prefix.
