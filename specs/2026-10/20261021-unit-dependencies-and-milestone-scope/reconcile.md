---
reconcile_id: REC-unit-dependencies-and-milestone-scope
status: resolved
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/architecture/ARCH-01-introduction-and-goals.md
    resolution: modified
  - file: packages/devkit-spec/README.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/decisions/2026-10/20261018-milestone-documents.md
    resolution: modified
  - file: docs/decisions/2026-10/20261021-separate-unit-prerequisites-from-milestone-themes.md
    resolution: modified
  - file: docs/roadmap/README.md
    resolution: modified
---

# Reconciliation: `SPEC-unit-dependencies-and-milestone-scope`

## Contract reflection

- `CAP-DOCS-document-model` defines optional typed direct anchor dependencies, terminal completed SPECs and ignored SPEC milestone metadata.
- `CAP-GOV-spec-rules` defines exact unique anchor validation, separate cycle graphs, changed-path reporting, live same-slug repair and PROP-only hygiene.
- `CAP-DLV-proposal-incubation` defines outgoing dependency carry, incoming relocation and projected graph validation before writes, with no milestone carry or fulfillment inference.
- `CAP-DLV-spec-bundles` removes direct-spec milestone CLI/API input and permits frontmatter dependency authoring without new flags.
- `CAP-HARN-agent-guidance` defines base-bound scheduling, blocked reasons, order overrides, lifecycle edge disposition and coarse user-agent milestone planning. Source guidance and templates carry the same contract in local and cloud rendering.
- `ADR-separate-unit-prerequisites-from-milestone-themes` and the disposition on `ADR-milestone-documents` delimit the superseded decisions; unchanged milestone transition/readiness authority remains.
- The roadmap README describes coarse themes and direct PROP membership. No other existing roadmap document changes.

## Scope and retained work

Host handoff moved Planning evidence and promoted the ADR before this worker began. Host incorporated cloud template renames and relocated direct references in the independent milestone-completion proposal. Earlier core/docs commits were Host-audited before checkpoint 738a23287298bc1ef38fda631d4e24b1f7e74990; the independent code review examined the full feature against main, including those commits. The final worker range begins at that checkpoint as requested by the Host.

No explicitly linked open direct-fix source feedback requires resolution. The bounded viewer scope correction is approved and implemented; independent code review and reconciliation verification pass.
`SPEC-deterministic-milestone-completion` remains independent; this feature assumes none of its closure or lineage design. Existing roadmap consolidation is outside scope and no bulk cleanup is performed.

## Entrypoint review

Existing precise entrypoints already cover documents/, rules/, hygiene.py, proposals/, spec creation CLI/API, source skills/templates and seed guidance. Broad package and test directory candidates are rejected: the affected capabilities do not each own all devkit_spec code or tests. No entrypoint expansion is needed.


## Independent verification follow-up

The Host authorized narrow documentation extensions for the architecture roadmap sentence and package README.
They now state direct PROP membership and no SPEC carry; the README no longer advertises the removed creation
option. The approved viewer correction removes SPEC member selection/loading and same-slug precedence, retaining PROP
branch overrides and milestone history/readiness. Independent verification confirms all eleven targets; the Host also verified the committed generated viewer assets.
