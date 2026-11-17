---
id: PROP-adr-body-metadata-removal
title: Remove the ADR body metadata block and trim the ADR template
summary: Drop the Status/Date/Deciders/Involved block from the ADR template, the proposal scaffold and the handoff acceptance rewrite, since the frontmatter already owns status, date and supersession, and shorten the option and separator scaffolding to what decision-writing asks for.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-17
target_area: documents/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/tests/integration/features/proposals/
  excludes:
    - handbook/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-adr-body-metadata-removal] Remove the ADR body metadata block and trim the ADR template

## 1. Background & Hypothesis

The ADR template (`templates/decision.md`) puts a metadata list under the H1: `- **Status**`, `- **Date**`,
`- **Deciders**` and `- **Involved Components/Capabilities**`.

- Status and Date repeat the frontmatter `status` and `created_at`; the superseded form ("Superseded by" plus an ADR ID)
  repeats `superseded_by`. In the 71 ADRs that carry the block, both values agree with the frontmatter.
- Deciders appears in 27 of 95 ADRs and Involved Components in 45; nothing reads either.
- No rule enforces the block, but code keeps the copy alive: the proposal scaffold (`scaffold.py`) writes it for PADRs,
  and handoff acceptance (`_accept_status` in `handoff.py`) rewrites the body Status line in step with the frontmatter.
  Tests pin both (`test_proposal_handoff.py`, `test_proposal_scaffold.py`).

The same template scaffolds per-option Overview/Pros/Cons although `decision-writing.md` asks for one or two lines per
option with its main trade-off, and separates every section with `---`.

Hypothesis: the frontmatter is the single owner of status, date and supersession; removing the body copy removes a
synchronization path in code and a field authors fill by rote.

Kept: the "Superseded in part by" body lines (they name replaced clauses, which the frontmatter cannot), Decision
Drivers, Confirmation and the outcome-trace comments (test-enforced).

## 2. Technical Spike Questions

- **Q1**: Existing ADRs: remove the block from all 71 in one mechanical pass, or leave them and only stop writing it?
  Leaving them means no code keeps them in step after `_accept_status` loses its body pass.
- **Q2**: Does any reader (viewer, `devkit docs` index, search snippet, handbook generation, supersession tooling) parse
  the body Status line? Confirm nothing does before removing the rewrite.
- **Q3**: Where do "Superseded in part by" lines sit once the block is gone (directly under the H1)?
- **Q4**: Option scaffolding: `- **<Option>**: <trade-off against drivers>` lines, with the selected option marked;
  drop the `---` separators.

## 3. Proposed Design & Impact

- Docs bundle: the decision template loses the block, the per-option sub-bullets and the separators;
  `decision-writing.md` is aligned.
- Spec package: the PADR scaffold stops writing the block; handoff acceptance updates only the frontmatter status;
  their tests change accordingly.
- Depending on Q1, a mechanical edit of existing ADR bodies (wording repair, no decision change, allowed without a
  superseding ADR).
- Living Spec: the capability that describes PADR scaffolding and acceptance (`CAP-DLV-proposal-lifecycle` or its
  owner) if it mentions the body status.

## 4. Lifecycle & Retirement Criteria

- Planning settles Q1–Q4; acceptance hands off to Development and integrates locally under `dev-integration=auto`.
- Integrated after `SPEC-formal-doc-padding-trim`, which touches the same docs bundle.
- Retire when the template, scaffold and handoff changes land.
