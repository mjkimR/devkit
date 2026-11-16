# Legacy migration

Read this when work touches an area with content under `docs/materials/_legacy/`, or when the user asks to migrate
legacy content up front.

## Destinations

| Legacy content | Destination |
| :--- | :--- |
| Behavior the system provides, its scope and invariants | Capability `docs/capabilities/<area>/CAP-<AREA>-<slug>.md` |
| An actor's goal with its flow, failure paths or acceptance scenarios | Use case `docs/usecases/<area>/UC-<slug>.md` |
| Context, containers, components, runtime, deployment, cross-cutting concepts | arc42 chapter `docs/architecture/ARCH-<NN>-<slug>.md` |
| A decision with its rationale | `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md`, dated by the original decision |
| Conceptual meanings, identities, relationships and lifecycles | Formal DOMAIN `docs/domain/<area>/DOMAIN-<slug>.md` |
| Implementation mechanisms, independently maintained examples and datasheets | Formal DESIGN bundle `docs/designs/<area>/DESIGN-<slug>/design.md` |
| Operational symptoms, evidence, normal-state observation and existing action-owner routes | Formal OPS `docs/operations/OPS-<slug>.md` |
| Setup, build, release and contribution guides | `docs/development/` |
| Terms | `docs/steering/glossary.md` |
| Project-wide background (product purpose, tone or style guide, domain overview) | A steering document `docs/steering/<topic>.md` with `title` and `summary` frontmatter |
| Agent working rules | `AGENTS.md` outside the markers when every task needs it; otherwise an instruction, playbook or rule (`spec-rule` skill) in the in-repository bundle |
| An in-progress feature spec (for example spec-kit `specs/NNN-*/`) | A new spec through the `spec` skill when that work resumes |
| Research, meeting notes, superseded plans, completed specs | Stay in `_legacy/` |

Start from `.devkit/managed/docs/templates/<kind>.md`.

## Procedure

1. Migrate inside ordinary work, typically in the `spec-sync` skill.
2. Write the current state, citing IDs, without legacy change logs; fill a starter chapter instead of a second
   architecture description.
3. Delete the legacy copy once superseded; keep it when it holds history the Living Spec does not carry.
4. Report a legacy instruction that conflicts with the spec constitution to the user instead of choosing precedence.
5. Delete a `.devkit/config.toml` deferral when `uv run devkit rules check --phase hygiene` reports
   `RULES_PROMOTION_READY` for it.

For formal roles, read the core writing instruction and use its template, ID/path/alias and artifact policy.
Preserve one owner per statement. Give independent detail a peer ID; assign parent-owned support to one canonical
parent: beside `design.md` in a DESIGN bundle, or in a DOMAIN/OPS `<ID>/artifacts/` directory. Repair current
ingress, ordinary support/source links and applicable DESIGN anchors during rename, area and root moves, splits,
reclassification and retirement. Preserve historical evidence with source provenance;
never reconstruct an experiment's decisions or transfer recovery authority while reorganizing documents.
