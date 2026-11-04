---
reconcile_id: REC-ux-writing-non-page-surfaces
status: pending
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
---

# Reconciliation: `SPEC-ux-writing-non-page-surfaces`

## Contract comparison

`CAP-HARN-agent-guidance` 4.3 catalogs the docs bundle's writing instructions by what each one defines; its
`ux-writing` row now names the criteria for surfaces beyond pages and forms (element choice, continuous input in prose
with `global:` rows, modes as states, transitions, task-less surfaces, mismatch recorded as feedback) beside the
items it listed before, citing this spec. The row's one-owner rule holds: the step citation criterion for long-running
activities and system judgements is written once, in `usecase-writing`, and `ux-writing`'s `Steps` bullet points to
it; the `description` of both instructions starts with `Read before` and stays within 300 characters (290 and 200),
which `test_writing_guidance.py` checks.

The guidance changes no contract the rules enforce. `CAP-GOV-spec-rules` 3.15 and 3.16 are unchanged: the section
maps surfaces onto the existing `element` kinds, the seven columns and the two classifications
(`ADR-explicit-ux-coverage-exception-notation`), and the behavior it relies on is already the rules' behavior,
now pinned by one test per rule (a task-less `screen` and `panel` with a header-only table, and a `modal` whose
`close` row is a global control, reported by neither rule). `ADR-ux-screens` keeps its element kinds, sections and
table; the `ux` template changes one comment line (one row per trigger that serves a step or is a global control)
and keeps every section and the lines `test_ux_guidance.py` pins. The `.devkit/managed/docs/` copies are regenerated
by `devkit sync` and `.devkit/installation.json` is its receipt.

No use case cites either instruction (`docs/usecases/` mentions them only in its README), no steering document
changes (the glossary's `UX document` row stays accurate: the surface criteria name no new term) and no architecture
document is affected. The repository's own `docs/ux/README.md` and the seeded `docs/ux/README.md` keep their
authoring principles unchanged (Non-Goal 3): the instruction is the owner of the criteria and the README points to
it.

## Deferred work and source feedback

The spec has no source feedback. The guidance's `Mismatch` criterion is the handoff for any surface the criteria
cannot describe: the agent records the document and the mismatch as feedback, which is the evidence a later rule
change (a relaxed `element` kind, a path-scoped opt-out) needs; `PROP-ux-rules-path-exclusion` was rejected on that
basis and nothing of its scope is deferred here.

## Verification and retained work

`just test-affected` 2169 passed at build; `just test devkit-spec tests/integration/bundles/spec/test_ux_guidance.py`
7 passed and the two UX rule test folders 38 passed after the review fixes; `uv run devkit rules check --phase hygiene`
on both instructions and the template 0 warnings; `uv run devkit rules check --ci --base 22aaef0d` errors=0
warnings=0 (reviewer run on the build head); `just lint devkit-docs devkit-spec` and `just check devkit-spec` pass.
Code review round 1 (`review-01`, native `code-reviewer`) found one P2 (the task-less bullet promised no report
while `RULE-ux-coverage` warns on an empty Step cell) and one P3 (two defaults for `populated`); both wording fixes
are applied, pinned by new assertions and the task-less modal rule test, and closed in `reverify-01`.

## Entrypoints

`devkit spec entrypoints derive` is run on this record; candidates are bundle instructions, a template and tests,
which are content and receipt support, not where reading of `CAP-HARN-agent-guidance` starts. Entrypoints stay
unchanged.
