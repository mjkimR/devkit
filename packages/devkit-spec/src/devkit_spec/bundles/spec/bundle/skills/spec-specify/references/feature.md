# spec-specify reference: feature specification

Fill the `spec.md` skeleton's sections at the `specify` stage, under the shared contracts of `SKILL.md` §4.

1. **Problem and user stories**: derive the user problem from the agreed intent, the issue and the proposal, and
   state the intent as user stories. Cite each existing use case whose goal the feature changes by ID
   (`` `UC-<slug>` ``) and list it in `related_usecases`; `spec-sync` later folds the delivered behavior into it.
2. **Non-goals**: what this feature will not do.
3. **Acceptance scenarios**: the happy path, boundary values, the interface's error contract (exit codes, status or
   error codes, payloads) and unauthorized cases, each confirmable by a test or a CLI run.
4. **Screens**: when the feature changes what a person sees, draft its screens in a `Screens` section (`SKILL.md` §4)
   and the use case step citations they need; the optional UX review runs before `spec-plan`.
5. **Security, privacy and compliance**: add this section only when the change has permission boundaries, sensitive
   data or auth constraints.
6. Leave `related_capabilities` or `related_usecases` as `[]` when none exist; every listed ID resolves
   (`devkit docs resolve <ID>`).
