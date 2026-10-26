---
id: MAT-ux-documentation-planning-spike
title: Planning spike for UX documents, links, checks and review
summary: "Answers the Planning spike questions of PROP-ux-documentation from devkit's code and documents: what a new UX kind touches next to the kind definition table, how use case steps can name screens, which checks are cheap, where an isolated UX review fits the workflows, and when UX documents are written."
created_at: 2026-10-26
---

# [MAT-ux-documentation-planning-spike] Planning spike for UX documents, links, checks and review

Evidence for the Planning of `PROP-ux-documentation`, gathered on the head of `main` at `96df5d86` by three `scout`
runs (`envelopes/scout-01.yaml` kind machinery, `scout-02.yaml` links and glossary, `scout-03.yaml` review and
workflows). External evidence stays in `MAT-ux-documentation-practice` and `MAT-ux-object-modeling`; this material
adds only what devkit's own code and contracts decide. Paths are relative to
`packages/devkit-spec/src/devkit_spec/` unless they start with a package or `docs/`.

## 1. What a new kind touches

A document's kind follows from its ID prefix; there is no `kind:` frontmatter field, and a file whose prefix is
unknown is dropped from the index (`features/documents/models/ids.py:16-51`, `features/documents/models/parse.py:58-61`).
A UX document therefore does not exist for any rule until its prefix is registered.

| Touch point | Location | Covered by the table of `PROP-table-driven-document-kinds` as drafted | Left to this proposal |
| --- | --- | --- | --- |
| Kind enum, prefixes, ID pattern | `features/documents/models/ids.py:16-51` | Yes (derived) | Add the row |
| Kind order, `--kind` choices | `features/documents/usecases/browse.py:22`, `features/documents/cli/commands.py:184` | Yes | Row position |
| Living Spec membership and directories | `features/governance/usecases/id_convention.py:80-81,291` | Yes | Row |
| Path and stem rule, messages | `id_convention.py:192-230` | Partly ("location pattern") | Stem rule and message unless the table carries them |
| Binary fallbacks (non-CAP/UC falls to ARCH rules; area remediation) | `id_convention.py:200-230,509` | Yes (named as its target) | None |
| Relation field list and field-to-prefix typing | `features/documents/models/model.py:11-14`, `features/governance/usecases/document_reference.py:43-52` | Yes ("fields it declares and accepts") | Define the UX row's fields |
| Bidirectional pair UC `capabilities` and CAP `usecases` | `features/governance/usecases/traceability_link.py:40-92` | No (pair logic) | A UX pair or a generalized pair table |
| Summary requirement | `features/governance/usecases/document_summary.py:29` | Yes | Flag |
| Entrypoint kinds | `features/governance/usecases/code_entrypoints.py:42`, `features/entrypoints/services/paths.py:25-34` | Likely | Decide: UX documents carry no entrypoints |
| `spec_format` namespace scope | `features/governance/usecases/spec_format.py:58-59,174-175` | Not named | Confirm, else add |
| Terminal statuses | `features/documents/repositories/index.py:157-161` | Not named | None if UX uses `draft`, `active`, `deprecated` like capabilities (no terminal status, so `ADR-terminal-statuses-are-historical` needs no new decision) |
| Templates, `AGENTS.md.jinja` template list | `bundles/spec/bundle/templates/`, `bundles/spec/bundle/AGENTS.md.jinja:61` | The table names a template; the file is new | Write the template; list it |
| `docs-skeleton` seed | `bundles/spec/bundle/seed/docs/` | No | Seed `docs/ux/` |
| Target-docs blueprint | `features/proposals/usecases/scaffold.py:440-452` | No | Add a UX section |
| Writing instructions, `spec-sync`, rule guides | `bundles/spec/bundle/instructions/`, `skills/spec-sync/SKILL.md`, `bundles/spec/bundle/rules/*/guide.md` | No | Prose |
| Viewer book grouping | `packages/devkit-viewer/frontend/src/lib/api/documents.ts:268-296` | Open (its Q3: served, generated or checked copy) | A "UX" group if the table does not supply it; today `docs/ux/` falls into "Overview" |
| Viewer bracket-ID regex | `packages/devkit-viewer/frontend/src/lib/api/documents.ts:246` | Not named | Add `UX`; the regex already lists the removed `US` and omits `UC`, `MS`, `FB` (pre-existing defect) |
| `CAP-DOCS-document-model` §3.2, §3.3 tables | `docs/capabilities/documents/CAP-DOCS-document-model.md:124-146` | No (document) | Rows and fields |

Two prefixes (for example `SCR` and `FLOW`) are possible as one kind or as two kinds, but no kind shares a prefix
today and each directory maps to one kind with one stem rule (`id_convention.py:77,81,291-294`). One prefix is the
cheapest; two kinds mean two rows, two directories and two relation fields.

Constraining decisions: `ADR-roadmap-and-milestones` (a kind needs a reader: agents implementing screens and the UX
reviewer), `ADR-document-id-aliases` (aliases and prefix-typed fields on every kind), `ADR-terminal-statuses-are-historical`
and `ADR-usecases-replace-stories` (the precedent for adding a kind with a namespace directory).

## 2. Documents (Q1)

| Option | Content | Cost | Risk |
| --- | --- | --- | --- |
| A | One `UX` kind; each document is one interface element (`element: screen`, `modal` or `panel`) with purpose, content tree, states and an interactions table whose rows carry the served step and the target; the use case's numbered scenario is the task flow and the targets form the navigation map | One row; one template | No single picture of the whole flow; a reader follows exits |
| B | Two kinds, `SCR` screens and `FLOW` flows (screen list, persistent panels, transition table) | Two rows, two templates, two relation fields | The transition table repeats the screens' exits; two places to keep in step |
| C | One `UX` kind with two document shapes told apart by frontmatter | One row; each shape has its own sections and rules | A template and every reader carry two schemas |

The use case already holds what a flow document would hold for one task: its steps in order and its extensions
(`usecase-writing` instruction). A per-screen interactions table with a target column gives the transitions, so
the flow graph is derived rather than written twice. Option A is the recommendation; option B fits projects whose
navigation spans many use cases and needs one overview (a later, derived listing could serve that).

Sections of a screen document under option A (an outline for the template; the medium stays with the project):

1. **Purpose**: the primary task in one verb phrase, the facts the user needs to commit to it, and where every
   secondary item goes.
2. **Content**: prose region rules (relative: primary, secondary, beside, below) and a content tree whose nodes name
   the glossary object and representation they show, with conditions next to the nodes. Character-cell layouts are
   ruled out (`MAT-ux-object-modeling` §3).
3. **States**: lowercase state names; `populated` plus each of `empty`, `loading` and `error` that applies, and any
   other state the screen has.
4. **Interactions**: one row per trigger: `Trigger | Step | From | To | Target | Capability | Feedback`, where
   `Step` names the served use case step key (`UC-<slug> 2a`), `Target` is a UX ID, `close` or empty.
5. **Evidence** (optional): a path or link to the project's own wireframe, mock-up or screenshot, read by the
   reviewer when present.

Objects (6a, 6b, 6d): a screen names objects by glossary terms. Adding glossary columns would silently disable the
glossary Owner check, which matches only the exact five-column header (`features/governance/usecases/document_reference.py:312-358`);
a second table under its own header is ignored by that check and by search, which reads only `glossary.yaml`
(`features/documents/usecases/search.py:39,62-65`). `PROP-foundation-documents` moves the glossary to
`docs/foundation/` and excludes table-format changes, so a UX object table belongs to this proposal and lands on the
moved path.

## 3. Links (Q2)

All 13 use cases write each main-scenario step as one `N.` list item and each extension as `- **Na.**` or
`- **\*a.**`; 12 of 13 cite a capability in every step, and `UC-resolve-stale-activity-branches` step 5 is an
actor-only step with none (`scout-02`). Every link rule reads frontmatter only; body references carry line and
column but are never mapped to a step (`features/documents/models/parse.py:183-206`).

| Option | Use case side | Screen side | Cost | Fit |
| --- | --- | --- | --- | --- |
| a | Step prose cites the UX ID, like a capability today | Interactions name the step key | One step segmenter; body references, resolution and alias rewriting are reused | A screen ID names where the step happens, not how; the step stays an intent |
| b | A trailing marker per step | Same | A new micro-syntax | Closer to UI detail; reduces to (a) |
| c | A frontmatter map of step key to UX ID | Same | Dict-valued field: new parse code, keys drift on renumbering | Clean prose, fragile keys |
| d | Nothing | The screen lists `UC-<slug> 2a` | A reverse index plus the step parser for "step without a screen" | The use case stays free of screen IDs; its author cannot see the screens |

Option (a) with the step key on the screen side is the recommendation. The step segmenter must tolerate an intro
paragraph before step 1, prose inside Extensions, the escaped `\*a` key and free-form `Covers` lines. Frontmatter:
a UX document declares `usecases` and `capabilities`; a use case declares no new field, because its step citations
are its side of the link.

## 4. Checks (Q3)

| Option | Checks | Needs |
| --- | --- | --- |
| 2a | Steps without a screen in a use case that a UX document lists; interactions whose step key is empty, unknown or not citing the screen; UX `usecases` against step citations | Step segmenter, interactions table schema |
| 2b | 2a plus: targets that are not UX IDs, screens without an exit, a modal without `close`, screens unreachable from the screens cited by step 1 | `element` value, target column |
| 2c | 2b plus each extension key reaching a declared state | State names in the `To` column |

Under option A of section 2, 2b costs little over 2a because the targets are already in the interactions table.
Not every step happens on a screen (actor decisions off-screen, background system steps), so the strictness of
"step without a screen" is a decision of its own.

## 5. Review (Q4)

- `code-reviewer` is a bundle subagent asset bound to `spec-review`; a new subagent asset is a valid stage role
  without engine code (`packages/devkit/src/devkit_agt/features/workflow/repositories/project/roles.py:1-16`). A
  seventh role still changes `CAP-DLV-delivery-workflows` ("six host-neutral role contracts") and the role-contract
  tests (`packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py:15,24`).
- Envelope kinds are open: `envelope new --kind ux-review` records one with no code change. Recording UX findings
  as `review` would share the code-review round state and decide or mask the `review-refine` exit. Only `review`
  and `challenger` rounds close by `reverify` (`packages/devkit/src/devkit_agt/features/workflow/services/envelope/model.py:37-43,109-112`).
- No exit-check primitive can say "only when the unit touches UX documents": file checks stay inside the unit
  directory, an `optional` stage never becomes current, and a mandatory stage blocks every unit without a UI
  (`packages/devkit/src/devkit_agt/features/workflow/services/evaluation/primitives.py:51-136`,
  `packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py:358-384`). A conditional stage therefore
  needs a new primitive in `devkit-agt`, outside this proposal's boundaries.
- Severity is inert in the engine; P1-P3 and the recovery rules keyed on P1 are bundle procedure for `review`,
  `reconcile-check` and `challenger` (`review-loop.md` §3-§4). A UX reviewer outside that loop keeps the non-goal
  "no severity ranking" and needs its own round cap in its skill.

| Placement | Cost | Risk |
| --- | --- | --- |
| Optional delegation before code (Planning spike; after specify), `ux-review-NN` envelopes | Bundle files, the capability text, role tests | Nothing enforces it; prose and effort trigger it |
| Conditional stage | New check primitive in `devkit-agt`, shared-stage alignment | Boundary expansion; blocks non-UI units if mandatory |

## 6. Timing of UX documents

`spec-sync` writes `docs/` at `living-spec-draft`, after `review-refine` (`workflows/sdd-spec-feature.md:53-71`;
`skills/spec-sync/SKILL.md:13`). A screen contract and a review before code need the screens before
`build-verify`. Options: write UX documents in `docs/ux/` on the development branch at `specify` (the branch merges
only at integration, so the base never holds a screen without its code; the rules and the review run on them), or
draft them in `spec.md` or `target-docs.md` and move them at `spec-sync` (no rule checks them before code), or
review only after `spec-sync` (the review cannot shape the build).

A UX document written into `docs/` alone at `specify` links use case steps and possibly new use cases or
capabilities that `spec-sync` writes only later, so the rules refuse the commit or the review walks the old use case
(`challenger-01` finding 1). The early option therefore has to move the whole linked slice (screens, use case step
citations, new use cases and capabilities) or nothing.

## 7. Decomposition (Q6)

One proposal hands off to exactly one spec (`CAP-DLV-proposal-incubation` §3, line 64). The kind, its checks and the
writing instruction are one contract; the reviewer depends on the template and the step key form. Keeping one
proposal means one spec with ordered tasks (kind and template, rule, instruction, reviewer); splitting gives the
reviewer its own proposal after the kind lands.

## 8. Overlaps and order

- `PROP-table-driven-document-kinds` must be developed first: the UX row is added to its table, and Development of
  this proposal starts from the table as merged. Section 1 lists what this proposal assumes the table carries.
- `PROP-foundation-documents` moves the glossary (and `bookGroup`'s `docs/glossary.md` group) to
  `docs/foundation/`; a UX object table and the UX document glossary terms land on whichever path is current at
  Development.
- All three proposals own `packages/devkit-spec/src/devkit_spec/features/`, `packages/devkit-spec/tests/` and
  `docs/capabilities/documents/`; the table and UX proposals also own the viewer frontend.
