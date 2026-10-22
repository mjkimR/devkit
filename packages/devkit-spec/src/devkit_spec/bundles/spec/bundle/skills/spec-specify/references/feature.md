# spec-specify reference: feature specification

Fill the `spec.md` skeleton's sections at the `specify` stage, under the shared contracts of `SKILL.md` §4.

1. **Problem and story**: derive the user problem from the agreed intent, the issue and the proposal. Cite an existing
   story that already expresses it by ID (`` `US-<slug>` ``) and list it in `related_stories`.
2. **Non-goals**: what this feature will not do.
3. **Acceptance scenarios**: the happy path, boundary values, the interface's error contract (exit codes, status or
   error codes, payloads) and unauthorized cases, each confirmable by a test or a CLI run.
4. **Security, privacy and compliance**: add this section only when the change has permission boundaries, sensitive
   data or auth constraints.
5. Leave `related_capabilities` or `related_stories` as `[]` when none exist; every listed ID resolves
   (`devkit spec resolve <ID>`).
