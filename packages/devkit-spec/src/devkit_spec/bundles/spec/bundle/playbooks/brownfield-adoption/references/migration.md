# Legacy migration

Read this when work touches an area with content under `docs/materials/_legacy/`, or when the user asks to migrate
legacy content up front.

## Destinations

| Legacy content | Destination |
| :--- | :--- |
| Behavior the system provides, its scope and invariants | Capability `docs/capabilities/<area>/CAP-<AREA>-<slug>.md` |
| A user goal with acceptance scenarios | Story `docs/stories/<area>/US-<slug>.md` |
| Context, containers, components, runtime, deployment, cross-cutting concepts | arc42 chapter `docs/architecture/ARCH-<NN>-<slug>.md` |
| A decision with its rationale | `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md`, dated by the original decision |
| Setup, build, release and contribution guides | `docs/development/` |
| Terms | `docs/glossary.md` |
| Agent working rules | `AGENTS.md` outside the markers when every task needs it; otherwise an instruction, playbook or rule (`spec-rule` skill) in the in-repository bundle |
| An in-progress feature spec (for example spec-kit `specs/NNN-*/`) | A new spec through the `spec` skill when that work resumes |
| Research, meeting notes, superseded plans, completed specs | Stay in `_legacy/` |

Start from `.devkit/managed/spec/templates/<kind>.md`.

## Procedure

1. Migrate inside ordinary work, typically in the `spec-sync` skill.
2. Write the current state, citing IDs, without legacy change logs; fill a starter chapter instead of keeping a second
   architecture description.
3. Delete the legacy copy once superseded; keep it when it holds history the Living Spec does not carry.
4. Report a legacy instruction that conflicts with the spec constitution to the user; do not pick precedence yourself.
5. Delete a `.devkit/config.toml` deferral when `uv run devkit rules check --phase hygiene` reports
   `RULES_PROMOTION_READY` for it.
